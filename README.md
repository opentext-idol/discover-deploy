# IDOL Discover

The following installation steps complement the full Discover Administration Guide, available from the [IDOL documentation site](https://www.microfocus.com/documentation/idol/), under "IDOL Government Solutions".

## Basic deployment

To deploy Discover to a Docker system, use the `deploy.py` tool, which requires Docker Compose.
Required software versions:
- Python 3, version 3.6 or later
- Docker, version 20.10.22 or later
- Docker Compose, version 2.14.1 or later

Log in with your own password to gain access to the OpenText IDOL containers on Docker Hub:

```
docker login -u microfocusidolreadonly
```

> To obtain your password (API key) contact OpenText support.

Configure the location of your IDOL License Server in `config/base.env`, and grant the `admin` role
in your License Server configuration to the host you will deploy the `analysis` component to.

Add TLS certificates in `config/https/` (see the `Encryption` section).

Run the `deploy.py` tool using Python.  (Much like when running `docker`, you
may have to run it as a different user with sufficient permissions to manage Docker containers.)

```
python3 deploy.py auth entity filestore analysis audit dataset-locations api ui
```

With the default configuration, the Discover UI will be available at `https://localhost:8090` once the
system has started.

After the system has started, log in with a user that has the `admin` role. The Discover UI will then perform a one off initialization. 

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

- `config/https/api/tls.key`: Private key for the API.
- `config/https/api/tls.crt`: Server certificate for the API.
- `config/https/auth/tls.key`: Private key for the authentication server.
- `config/https/auth/tls.crt`: Server certificate for the authentication server.
- `config/https/ui/nginx.key`: Private key for the UI.
- `config/https/ui/nginx.crt`: Server certificate for the UI.

## Entities database schema

The entities database can be customized by modifying the file `data/entity/custom.yaml`.  The schema can only be
customized once, before deploying the system.  Customizations are saved permanently in the `entity-data` volume.

## Further examples

To use HTTP instead of HTTPS, for testing purposes only, run:

```
python3 deploy.py --disable-encryption auth entity filestore analysis audit dataset-locations api ui
```

> note: changes to the encryption state of a deployed system require manual deletion of the realm in Keycloak before running `deploy.py` with the new state.

To resume a stopped Discover system, or to apply changes made to configuration files, or to change which
components are deployed: run the normal command to deploy.

To stop and remove deployed Discover services, run the Python `deploy.py` tool with no arguments:

```
python3 deploy.py
```

You can deploy components on different hosts, or deploy some components separately using a
compatible implementation (read the `deploy.py` tool help text for a list of components).  For
example, to use an existing object storage server and deploy the audit database on a separate host,
configure hosts and ports in the files in `config/`, and then run on separate hosts:

```
python3 deploy.py audit
python3 deploy.py auth entity analysis api ui
```

## System information

By default, the following ports are forwarded ('public' ports listen on all interfaces (0.0.0.0),
while others listen on 127.0.0.1 only):

| **Component**     | **Port** | **Public** | **Purpose**                                                                |
|-------------------|----------|------------|----------------------------------------------------------------------------|
| auth              | 8000     | no         | PostgreSQL database storing authentication server configuration            |
| auth              | 8010     | yes        | Keycloak authentication server (API and admin UI)                          |
| entity            | 8021     | no         | ACI port of IDOL Content database backend for the Gremlin database         |
| entity            | 8022     | no         | Index port of IDOL Content database backend for the Gremlin database       |
| entity            | 8023     | no         | CQL port of Cassandra-compatible database backend for the Gremlin database |
| filestore         | 8030     | no         | S3-compatible object storage                                               |
| analysis          | 8040     | no         | NiFi server for media analysis (API and admin UI)                          |
| audit             | 8050     | no         | PostgreSQL database storing audit logs                                     |
| dataset-locations | 8100     | no         | ACI port of IDOL Content database backend for the locations database       |
| api               | 8060     | yes        | System HTTP API                                                            |
| ui                | 8090     | yes        | Discover UI                                                                |

Docker volumes are created with the prefix `opentext-idol-discover_`, which can be changed using the
`COMPOSE_PROJECT_NAME` setting.  The following volumes are created:

| **Component**     | **Volume name**                | **Purpose**                         |
|-------------------|--------------------------------|-------------------------------------|
| auth              | auth-db-data                   | Authentication server configuration |
| entity            | entity-storagedb-data          | Application data                    |
| entity            | entity-indexdb-data            | Search index for application data   |
| entity            | entity-indexdb-license-data    | Cache for license information       |
| filestore         | filestore-service-data         | Uploaded and generated files        |
| audit             | audit-db-data                  | Audit logs                          |
| dataset-locations | dataset-locations-license-data | Cache for license information       |
| -                 | entity-data                    | Schema for application data         |

All containers connect to a Docker network called `opentext-idol-discover_main`.  The
`opentext-idol-discover` prefix can be changed using the `COMPOSE_PROJECT_NAME` setting.
