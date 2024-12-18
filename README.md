# Iot Backend

### Para realizar deploy

````bash
git clone url_do_git
docker-compose up -d
````

### Para atualizar o código fonte

````bash
git pull
````

### Para entrar dentro do container e executar comandos

````bash
docker-compose exec web /bin/bash
# Então realize os comandos necessarios, por exemplo.
python manage.py makemigrations
python manage.py migrate
````

### Caso o queria forcar a recriação do container

````bash
docker-compose down
docker-compose up -d --force-recreate
````

### Exemplo arquivo .env ###

```dotenv
ENVIRONMENT=development
SECRET_KEY="@-2!=wpagnmz02=kxy!h(w-ot^b1mg-zg3n3q=9#pbqq2oe7^o"
DEBUG=True

POSTGRES_DB=iot
POSTGRES_PASSWORD=123
POSTGRES_USER=iot
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

```
