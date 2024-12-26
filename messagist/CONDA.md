# Conda
## Criar o environment
Depois de clonar o repositório é preciso criar o conda environment:
```sh
cd messagist
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

cd /contract
mkdir target
cd ..
./proto.sh

server:
python server.py -p 5001 -d

client:
python client.py -d

keyserver:
python keyserver.py -p 5002 -d


CONNECT TO DB LOCALLY
psql -h localhost -U postgres -d test
