#
# Copyright 2021-2024 Open Text.
#
# Licensed under the MIT License (the "License"); you may not use this file
# except in compliance with the License.
#
# The only warranties for products and services of Open Text and its affiliates
# and licensors ("Open Text") are as may be set forth in the express warranty
# statements accompanying such products and services. Nothing herein should be
# construed as constituting an additional warranty. Open Text shall not be
# liable for technical or editorial errors or omissions contained herein. The
# information contained herein is subject to change without notice.
#

import argparse
import glob
import os
import shutil
import subprocess
import sys
import textwrap

BASE_PATH = os.path.dirname(os.path.abspath(sys.argv[0]))
OUTPUT_WIDTH = min(100, shutil.get_terminal_size()[0])


class ProgramError(Exception):
    pass


def wrap(text):
    return textwrap.fill(text, OUTPUT_WIDTH)


DESCRIPTION = '''
Deploy IDOL Discover.

''' + wrap('''\
This program deploys components of the Discover system, or resumes a stopped system, or reconfigures an
existing system.  Before running, check and update the configuration in `config/base.env`.
''') + '''

''' + wrap('''\
By default, nothing is deployed; for a working system, all components are required, but you may
deploy them on different hosts.  For each component you deploy using this program, check and update
its individual configuration file - for example, to configure the 'auth' component, you can edit
`config/auth.env`.
''') + '''

''' + wrap('''\
The components that can only be deployed using this script are:
''') + '''

- entity: storage for application data
- analysis: media analysis system
- analysis-live: live media analysis system
- dataset-locations: database of global locations
- api: user-facing web server
- ui: user-facing web server

''' + wrap('''\
The components that may be deployed using this script, or may be deployed manually using suitable
replacements, are:
''') + '''

- auth: user-facing web server - Keycloak authentication server
- filestore: storage for files - Amazon S3-compatible object storage
- audit: storage for audit logs - PostgreSQL database server
'''


def parse_args():
    p = argparse.ArgumentParser(description=DESCRIPTION,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('component', nargs='*', metavar='COMPONENT', help='components to deploy')
    p.add_argument('--docker-host', metavar='HOST',
                   help='Docker host to run containers on (default: use Docker running locally)')
    p.add_argument('--init', action='store_const', const=True, default=False, help='deprecated option')
    p.add_argument('--disable-encryption', action='store_const', const=True, default=False,
                   help='configure user-facing servers to accept HTTP connections (by default, '
                        'user-facing servers accept HTTPS connections)')
    p.add_argument('--extra-components-path', action='append', metavar='DIR',
                   help='directory containing custom component definitions')
    p.add_argument('--config-file', metavar='FILE',
                   help='path to a configuration file with values that override all other '
                        'configuration files')
    p.add_argument('--skip-pull', action='store_const', const=True, default=False,
                   help='skip pulling Docker images; allows running against a custom set of images')
    p.add_argument('--skip-deploy', action='store_const', const=True, default=False,
                   help='don\'t start Docker containers')
    return p.parse_args()


def run_process(args):
    try:
        subprocess.check_call(args)
    except subprocess.CalledProcessError as e:
        raise ProgramError(e)


def get_component_paths(options):
    component_paths = {}
    extra_paths = [] if options.extra_components_path is None else options.extra_components_path
    components_paths = [os.path.join(BASE_PATH, 'docker-compose')] + extra_paths
    for components_path in components_paths:
        glob_path = os.path.join(glob.escape(components_path), 'docker-compose.*.yml')
        for path in glob.iglob(glob_path):
            name = os.path.basename(path)
            name = name[name.find('.') + 1:name.rfind('.')]
            component_paths[name] = path
    return component_paths


def validate_components(components, component_paths):
    for component in components:
        if component == 'base' or component not in component_paths:
            raise ProgramError(f'invalid component: {component}',
                               f'known components: {", ".join(component_paths.keys())}')


def get_env_paths(components):
    for component in components:
        for source in ('config-fixed', 'config'):
            path = os.path.join(BASE_PATH, source, f'{component}.env')
            if os.path.exists(path):
                yield path


def build_env_file(env_paths):
    target_path = os.path.join(BASE_PATH, '.env')
    with open(target_path, 'w') as target_f:
        for source_path in env_paths:
            with open(source_path) as source_f:
                target_f.write(f'\n\n# source: {source_path}\n\n')
                target_f.write(source_f.read())
    return target_path


def get_compose_paths(components, component_paths):
    for component in components:
        if component in component_paths:
            yield component_paths[component]


def get_compose_args(components, component_paths, options,
                     command, detach=False, remove=False, log_level='info'):
    # base should be first
    compose_components = ['base'] + list(components)
    compose_args = ['docker', '--log-level', log_level]
    if options.docker_host is not None:
        compose_args.extend(['--host', options.docker_host])
    compose_args.append('compose')
    env_paths = (list(get_env_paths(compose_components)) +
                 ([] if options.config_file is None else [options.config_file]))
    compose_args.extend(['--env-file', build_env_file(env_paths)])
    for compose_path in get_compose_paths(compose_components, component_paths):
        compose_args.extend(['--file', compose_path])
    compose_args.extend(command)
    if detach:
        compose_args.append('--detach')
    if remove:
        compose_args.append('--remove-orphans')
    return compose_args


def run_compose(components, component_paths, options, skip_deploy, detach, remove, log_level='info'):
    command = ['up', f'--pull={"never" if options.skip_pull else "always"}', '--build']
    if skip_deploy:
        command.append('--no-start')
    run_process(get_compose_args(components, component_paths, options, command, detach, remove, log_level=log_level))


def deploy(components, component_paths, options):
    components = list(components)
    if options.disable_encryption:
        # should be last
        components.append('unencrypted')

    # - don't remove if --skip-deploy, so that data containers persist afterwards
    # - we want to restart if already running, to ensure that data volume changes are picked up; to avoid starting
    #   twice, this line will only create containers
    run_compose(components, component_paths, options, skip_deploy=True, detach=False, remove=not options.skip_deploy)
    if not options.skip_deploy:
        run_process(get_compose_args(components, component_paths, options, ['restart']))


def main():
    program_args = parse_args()
    component_paths = get_component_paths(program_args)

    if program_args.component:
        run_compose(['data-entity', 'data-security'], component_paths, program_args,
                    skip_deploy=program_args.skip_deploy, detach=False, remove=False, log_level='error')
        components = program_args.component
        validate_components(components, component_paths)
        deploy(components, component_paths, program_args)

    # If no components were listed to be started, perform docker compose down
    else:
        run_process(get_compose_args(component_paths.keys(), component_paths, program_args,
                                     ['down'], remove=True, log_level='error'))


try:
    main()
except ProgramError as e:
    print('error:', '\n'.join(map(str, e.args)), file=sys.stderr)
    sys.exit(1)
