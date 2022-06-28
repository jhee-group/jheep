# JHEEP: JHEE Platform

JHEEP (JHEE Platform) is a main infraware of AI/MLOps in a business scale.

### Ports
- Front: 8000
- CNS API: 8001

## How to use

### Docker image build
```sh
$ jc back build
$ jc worker build
```

### Prepare database

Run env
```sh
$ jc up
```

Use psql to create database. The default database name is `jheep`.
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

Test if backend api works: http://localhost:8001/v1/docs
