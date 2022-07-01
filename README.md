# JHEEP: JHEE Platform

JHEEP (JHEE Platform) is a main infraware of AI/MLOps in a business scale.

### Ports
- Front: 8800
- API server: 8801
- Jupyterlab server: 8899

## How to use

### Prerequisites

You need a properly setup of
  - `docker` with `docker compose v2`
  - `direnv`

Please do after clone
```
direnv allow
```
to accept the dir settings.

### Docker image build
```sh
$ jc build
```

### Prepare database

Run env
```sh
$ jc up
```

Use psql to create database. The default database name is `jheep_db`.
```sh
$ jc db createdb
```

Migrate initial database schema
```sh
$ jc back migrate
```

### Re-run env
```sh
$ jc down
$ jc up
```

Test if backend api works: http://localhost:8801/v1/docs
