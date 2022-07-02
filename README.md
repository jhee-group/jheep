# JHEEP: JHEE Platform

JHEEP (JHEE Platform) is targeting a business-scale AI/MLOps platform.

### Ports
- Front: 8800
- API server: 8801
- Jupyterlab server: 8899

## How to use

### Prerequisites

You need a properly setup of
  - `docker`
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

# Acknowledgement

The base structure of this project has been inspired by the project [Fief](https://github.com/fief-dev/fief.git).\
Many thanks to the author and the contributers.
