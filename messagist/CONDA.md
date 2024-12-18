# Conda
## Criar o environment
Depois de clonar o repositório é preciso criar o conda environment:
```sh
cd messagistpy
conda env create --file environment.yml
```

## Ativar o environment
Antes de se poder correr o projeto é preciso ativar o environment:
```sh
cd messagistpy
conda activate messagist
```

## Adicionar uma dependencia
Adicionar a dependencia ao environment.yml:
```
name: messagist
channels:
  - defaults
dependencies:
  - python=3.12
  (...)
  - nova-dependencia
```

Atualizar o ambiente:
```sh
conda env update --file environment.yml
```
