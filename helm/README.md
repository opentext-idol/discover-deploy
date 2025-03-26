# IDOL Discover

The following installation steps complement the full Discover Administration Guide, available from the [IDOL documentation site](https://www.microfocus.com/documentation/idol/), under "IDOL Government Solutions".

## Basic deployment

This directory contains tools to deploy IDOL Discover on Kubernetes, using Helm.  The _discover_ directory contains a
Helm Chart for this purpose.

_Kubernetes_ is a system for automating deployment, scaling, and management of containerized applications.

_Helm_ is a package manager for Kubernetes.

A Helm _Chart_ defines and aids installation of a Kubernetes application.

## Prerequisites

You will need to install:
* [The `kubectl` command-line tool](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
* [The `helm` command-line tool](https://helm.sh/)

## Configuration

You can configure Discover by modifying the YAML file `discover/values.user.yaml`.  It is recommended to review all
settings before deploying, especially passwords and maximum volume sizes.  Read below to learn about the required values
that you must fill in.

### Docker Hub login

The `secret.base64dockerconfigjson` setting is a base64-encoded JSON Docker configuration file including credentials.

> To obtain your password (API key) contact OpenText support.

If you have the `docker` command-line tool installed, you can run:

```
docker login -u microfocusidolreadonly
kubectl create secret docker-registry docker-secret --dry-run=client -o yaml \
    --from-file=.dockerconfigjson=/path/to/.docker/config.json
```

Otherwise, run:

```
kubectl create secret docker-registry docker-secret --dry-run=client -o yaml \
    --docker-username=microfocusidolreadonly --docker-password=<token>
```

Copy the `.dockerconfigjson` value from the output into the `secret.base64dockerconfig.json` setting.

### License Server

Fill in the `license.ip` setting to point to an IDOL License Server.  Grant the `admin` role in your License Server
configuration to the hosts that will run Kubernetes components.

## Deployment

Install the application with your updated configuration using Helm:

```
helm dependency update discover
helm install --values discover/values.user.yaml discover ./discover/
```

After the system has started:
* With the default configuration, access the Discover UI at `http://your-kubernetes-server/discover/`.
* Log in with the admin user (see `auth.createAdminUsername` in `discover/values.user.yaml`). The Discover UI will then
  perform a one-off initialization.

## Entities database schema

The entities database can be customized by modifying the file `discover/entity-schema.yaml`.  The schema can only be
customized once, before deploying the system.  Customizations are saved permanently in the `entity-data` volume.

## Custom Docker images

Some components have customizable Docker images.  You can view information about these components in the `README.md`
files in the `custom` directory (for example, `custom/data-security/custom/README.md`).  To use custom Docker images:

1. Deploy a Docker Registry to serve your custom Docker images.
2. In `discover/values.user.yaml`, set the `docker.customRegistry.root` to the address of your Docker Registry, as seen
   from inside your Kubernetes cluster.
3. In `discover/values.user.yaml`, set `customImage` to `true` for each Docker image you want to customize.
4. In `custom/build.env`, set `CUSTOM_DOCKER_REGISTRY` to the address of your Docker Registry, as seen from this
   machine.
5. Follow the instructions in each `README.md` file in the `custom` directory for each Docker image you want to
   customize.
6. In the `custom` directory, for each Docker image you want to customize, run the following commands, replacing the
   `--file` option with the appropriate path:
 
   ```
   docker compose --env-file build.env --file data-security/docker-compose.data-security.yml build
   docker compose --env-file build.env --file data-security/docker-compose.data-security.yml push
   ```

7. Deploy the application as normal.

## System information

By default, the following HTTP paths serve requests on port 80 and 443 (HTTPS):

| **Path**   | **Purpose**                    |
|------------|--------------------------------|
| /auth/     | Keycloak authentication server |
| /api/      | System HTTP API                |
| /discover/ | Discover UI                    |

In addition, by default, the following ports are used for admin access:

| **Port** | **Purpose**                                         |
|----------|-----------------------------------------------------|
| 30020    | Keycloak authentication server Admin Console (HTTP) |

The following persistent volume claims are created:

| **Name**               | **Default size** | **Purpose**                         |
|------------------------|------------------|-------------------------------------|
| auth-db-data           | 1GiB             | Authentication server configuration |
| entity-storage-db-data | 5GiB             | Application data                    |
| entity-index-db-data   | 5GiB             | Search index for application data   |
| filestore-data         | 1TiB             | Uploaded and generated files        |
| audit-db-data          | 1GiB             | Audit logs                          |
| system-entity-data     | 100MiB           | Schema for application data         |
| system-security-data   | 100MiB           | Security-related data               |
