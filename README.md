## Litestar API Example

A simple example of how to start your development with Litestar!



DIRECTORY STRUCTURE
-------------------

```

migrations/ -> your db migrations and rules to make them
nginx/ -> reverse-proxy configurations
src/
    api/
        ...
        framework level. There is your versions/endpoints/middlewares/use-cases and so on
    common/ -> сommon folder containing shared resources and utilities that might be used across the project
    core/ -> a heart of your project, there is like servers/settings
    database/ -> database layer, here is your storage and rules to work with it
    interfaces/ -> project interfaces
    services/ -> your business-logic
    __main__.py -> entry point
    defaults.py -> here is what you want to make before app starting
tests/
    ... your tests
```
## Download
```
git clone git@github.com:hpphpro/litestar_api_example.git
```
## ENV_FILE
First of all rename your `.env.example` to `.env`
```

DB_DRIVER=postgresql+asyncpg  # your db driver
DB_HOST=postgres # your host. If it running localy, set to localhost/127.0.0.1. If it running in a container, set a service/container_name
DB_PORT=5432 # your port
DB_USER=litestar # db user, you may want to override it
DB_NAME=litestar # your db name, you may want to override it
DB_PASSWORD=litestar # Better use a nice password.


SERVER_HOST=0.0.0.0 # your server host
SERVER_PORT=8080 # your server port. If you override it, do the same in a docker-compose as well
SERVER_CORS=1 # 1 - enable cors, 0 - disable
SERVER_CORS_ORIGINS=["http://localhost", "http://localhost:8080", "http://127.0.0.1", "http://127.0.0.1:8080"] # your origins. May be also https://my-example-frontend.com
SERVER_CORS_METHODS=["OPTIONS", "DELETE", "POST", "GET", "PATCH"] # add PUT if you add it in your application
SERVER_CORS_HEADERS=["Authorization", "Accept", "Content-Type", "If-Modified-Since", "Cache-Control"] # your CORS headers, you may want to extends or remove smth
SERVER_LOG_LEVEL=INFO # your logger level
SERVER_DEBUG=1 # should litestar throw an exception to the terminal and request answer or not
SERVER_TYPE=uvicorn # your server. uvicorn, gunicorn or granian may be used
SERVER_TITLE=Litestar # remove this if you want to disable swagger
SERVER_WORKERS=1 # set up workers for your server (only affect gunicorn/granian)

REDIS_HOST=redis # same as DB_HOST.

CIPHER_ALGORITHM=RS256 # your algorithm. If you setting up HS256, then secret_key and private_key should be the same.
# here is b64 .pem secret and public keys. You should override it by yourself
# if you using RSA, then:
# for private -> openssl genpkey -algorithm RSA -pkeyopt rsa_keygen_bits:2048 -out private.pem && cat private.pem | base64
# for public -> openssl rsa -in private.pem -pubout -out public.pem && cat public.pem | base64
# store it in b64 IS IMPORTANT. It wont work other way, T_T
# this key is 4098 bits.
CIPHER_SECRET_KEY=...
CIPHER_PUBLIC_KEY=...
CIPHER_ACCESS_TOKEN_EXPIRE_SECONDS=1800 # your access token expire. 1800 seconds that's equal to 30 min.
CIPHER_REFRESH_TOKEN_EXPIRE_SECONDS=604800 # a week, for refresh one.

```
# Installation
```
pip install -r requirements.txt
```
`Create db and tables. By default db is postgres.`

__Project already include initial migration. If you want to create your own or add a new one:__
```
alembic revision --autogenerate -m 'initial' && alembic upgrade head
```
## TESTS
To run tests, use following command:
```
docker-compose -f docker-compose.ci.yml up --build
```
Or set your local MOCK_DB settings to .env and run:
```
pytest tests
```
`For UNIX`:

__local__:
```
make run_test_local
```
__docker__:
```
make run_test_docker
```

`Start app:`


for Windows:
```
python -m src.defaults && python -m src
```
for Unix:
```
python3 -m src.defaults && python3 -m src
```
And thats it!
# Docker.
## Unix:
```
make docker_build
```
```
make docker_up
```
## Windows:
```
docker-compose -f docker-compose.prod.yml up -d --build
```

