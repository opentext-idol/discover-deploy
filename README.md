# Law Enforcement Media Application (LEMA)

## Basic deployment

To deploy LEMA to a Docker system, use the `deploy.py` tool, which requires Docker Compose.
Required software versions:
- Python 3, version 3.6 or later
- Docker, version 1.13.0 or later
- Docker Compose, version 1.10.0 or later

Log in to gain access to the Micro Focus IDOL containers on Docker Hub:

```
docker login -u microfocusidolreadonly
```

Run the `deploy.py` tool using Python.  Much like when running `docker` or `docker-compose`, you may
have to run it as a different user with sufficient permissions to manage Docker containers.

To immediately deploy all components on the same Docker host, configure the location of your License
Server in `config/base.env`, add TLS certificates in `config/https/` (see the `Encryption` section),
and run:

```
python3 deploy.py --init auth entity filestore analysis audit api ui
```

With the default configuration, the LEMA UI will be available at `https://localhost:8070` once the
system has started.

To show options and other usage information, run:

```
python3 deploy.py --help
```

## Configuration

All configuration files are in the `config` directory.  `base.env` contains settings relevant to
multiple components, and, for example, `api.env` contains settings relevant only to the `api`
component.  Lines starting with `#` are ignored, and these are used to explain the meaning of each
of the settings.

## Encryption

By default, the user-facing servers (authentication server, API, and UI) only accept encrypted 
connections.  For this to work, you must obtain TLS certificates and copy them into the `config` 
directory.  The required files are:

- `config/https/api/keystore.jks`: Java Keystore containing private key and server certificate for 
  the API.  Extra configuration is required in `config/api.env`.
- `config/https/auth/tls.key`: Private key for the authentication server.
- `config/https/auth/tls.crt`: Server certificate for the authentication server.

## Further examples

To use HTTP instead of HTTPS, for testing purposes only, run:

```
python3 deploy.py --disable-encryption --init auth entity filestore analysis audit api ui
```

To resume a stopped LEMA system, or to apply changes made to configuration files, or to change which
components are deployed: run the normal command to deploy, but without the `--init` argument:

```
python3 deploy.py auth entity filestore analysis audit api ui
```

You can deploy components on different hosts, or deploy some components separately using a
compatible implementation (read the `deploy.py` tool help text for a list of components).  For
example, to use an existing object storage server and deploy the audit database on a separate host,
configure hosts and ports in the files in `config/`, and then run on separate hosts (note that
`--init` need only be run once):

```
python3 deploy.py audit
python3 deploy.py --init auth entity analysis api ui
```

## System information

By default, the following ports are forwarded ('public' ports listen on all interfaces (0.0.0.0),
while others listen on 127.0.0.1 only):

| **Component** | **Port** | **Public** | **Purpose** |
|---------------|----------|---------------|-------------|
| auth | 8000 | no | PostgreSQL database storing authentication server configuration |
| auth | 8010 | yes | Keycloak authentication server (API and admin UI) |
| entity | 8020 | no | Gremlin database storing application data |
| filestore | 8030 | no | S3-compatible object storage |
| analysis | 8040 | no | NiFi server for media analysis (API and admin UI) |
| audit | 8050 | no | PostgreSQL database storing audit logs |
| api | 8060 | yes | System HTTP API |
| ui | 8070 | yes | LEMA UI |

Docker volumes are created with the prefix `micro-focus-idol-lema_`, which can be changed using the
`COMPOSE_PROJECT_NAME` setting.  The following volumes are created:

| **Component** | **Volume name** | **Purpose** |
|---------------|-----------------|-------------|
| auth | auth-db-data | Authentication server configuration |
| entity | entity-service-data | Application data |
| filestore | filestore-service-data | Uploaded and generated files |
| audit | audit-db-data | Audit logs |

All containers connect to a Docker network called `micro-focus-idol-lema_main`.  The
`micro-focus-idol-lema` prefix can be changed using the `COMPOSE_PROJECT_NAME` setting.
