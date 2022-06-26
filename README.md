# JHEE Central Nervious System

JHEE CNS (Central Nervious System) is a main backbone of the AI/MLOps in a business scale.

### Ports
- Front: 8000
- CNS API: 8001

## How to use

### Docker image build
```sh
$ jc build
```

### Execute images
```sh
$ jc up
```

## Initial API database setting
```sh
$ jc migrate
```
Test if backend api works: http://localhost:8001/v1/docs
