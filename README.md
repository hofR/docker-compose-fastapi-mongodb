# Example: Docker Compose (python + fastapi + mongodb)

This example shows how to set up the infrastructure for a FastAPI REST Service with the NoSQL Database MongoDB.

## Create the project

To set up the infrastructure, we create a folder `docker-fastapi-mongodb` which will include the Dockerfile as well as 
a directory `app`, which stores the FastAPI application:

```
docker-fastapi-mongodb/
├── Dockerfile
└── app/
```

In the `app` directory, we create another `app` directory as well as an `pyproject.toml` file.

```
docker-fastapi-mongodb/
├── Dockerfile
└── app/
    ├── app/
    └──pyproject.toml
```

The `pyproject.toml` files specifies the needed dependencies of the project and integrates with `Poetry`, 
a dependency and packaging management tool for Python:

```
[tool.poetry]
name = "app"
version = "0.1.0"
description = ""
authors = ["Your Name <you@example.com>"]

[tool.poetry.dependencies]
python = "^3.6"
uvicorn = "^0.11.3"
fastapi = "^0.54.1"
pydantic = "^1.4"
gunicorn = "^20.0.4"
motor = "^2.3.0"

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

```

NOTE: `Poetry ` offers a CLI which allows performing several actions including:
* setup a new project with `poetry new app`
* initialise an existing project with `poetry init`
* add new dependencies with `poetry add <dependency>`
* install all listed dependencies with `poetry install`

Including the second `app` folder, the complete project structure looks like this:

```
docker-fastapi-mongodb/
├── Dockerfile
└── app/
    ├── app/
        ├── api/
        ├── core/
        ├── crud/
        ├── db/
        ├── schema/
        └──main.py
    └── pyproject.toml
```

* **main.py** specifies the entrypoint of the FastAPI app.
* **api** defines the REST routes of the application
* **crud** defines database operations
* **db** includes code to set up the database
* **schema** defines Data Transfer Objects 

Finally, we write a **Dockerfile** that uses the `tiangolo/uvicorn-gunicorn-fastapi:python3.7` base image:
```
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.7
WORKDIR /app/
# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false
# Copy poetry.lock* in case it doesn't exist in the repo
COPY ./app/pyproject.toml ./app/poetry.lock* /app/
RUN poetry install --no-root --no-dev
COPY ./app /app

```
Within this `Dockerfile`, the following steps will be performed:
* Build an image starting with the `tiangolo/uvicorn-gunicorn-fastapi:python3.7` image.
    * This image uses `guvicorn` or `unicorn` to serve the application.
* Set the working directory to `/app/`.
* Install `Poetry` for dependency management.
* Copy the `pyproject.toml` and it's lockfile to the working directory.
* Install all dependencies managed by poetry.
* Copy the directory `./app` in the project to the workdir `/app/` in the image.

It's important to copy the app code after installing the dependencies, 
that way you can take advantage of Docker's cache. 
That way it won't have to install everything from scratch every time you update your application files, 
only when you add new dependencies.

## Create a Compose File
Because we want to use the FastAPI image together with MongoDB, we use the following `docker-compose.yml` file,
stored in the top-level of the project:
```
/
├── docker-compose.yml
├── docker-fastapi-mongodb
└── README.md
```
This Compose file defines two services: `web` and `mongodb`:
```
version: "3.9"
services:
  web:
    build:
      context: ./docker-fastapi-mongodb
    ports:
      - "8888:80"
    volumes:
      - ./docker-fastapi-mongodb/app:/app
    depends_on:
      - mongodb
    env_file:
      - .env

  mongodb:
    image: mongo:latest
    env_file:
      - .env
    ports:
      - 27017:27017
```
The `web` service uses an image that’s built from the `Dockerfile`. 
It then binds the container port 80 to the host port 8888 and `depends_on` the `mongodb` service.
 
The `mongodb` service uses the latest official docker image for `MongoDB`
  
Note that we have mount the host's directory `./docker-fastapi-mongodb/app` to the in container directory `/app`
by using the `volumes` keyword.
This allows us to **modify the code on the fly**, without having to rebuild the image. Related to this,
the `web` service uses `/start-reload.sh` as command override. This enables live reloading of the FastAPI server
and should only be used for development.

The `env_file` key sets the environment variables specified in the `.env` for both services: 
```
PROJECT_NAME=docker-fastapi-mongodb

MONGODB_URL=mongodb://mongodb:27017/
MONGODB_DATABASE=docker-fastapi-mongodb
MONGODB_COLLECTION=items
```
Within this `.env` file, variables for the connection url, database and collection of MongoDB are set, 
and are then used by the FastAPI application. Moreover, the file defines the project name of the API.

## Run the Service
We start the application by running `# docker-compose up` from the `compose-fastapi` directory 
which contains the `docker-compose.yml`.
After the services have started, it should be possible to visit `http://localhost:8888/docs` to see the SwaggerUI of the
API.
The item endpoint is accessible at `http://localhost:8888/api/v1/items`

Now we can use curl to perform CRUD Operations:

**POST**
```
$ curl -i  -H 'Content-Type: application/json' -X POST http://localhost:8888/api/v1/items --data-binary @- <<EOF
{
  "name": "Item 1",
  "description": "First Item",
  "price": 9.99
}
EOF
```
```
HTTP/1.1 201 Created
date: Sun, 24 Jan 2021 11:03:51 GMT
server: uvicorn
content-length: 101
content-type: application/json

{"name":"Item 1","description":"First Item","price":9.99,"id":"f4a44b89-cd76-4005-9f49-d7a19373ba4a"}
```

**GET**
```
$ curl -i  -H 'Content-Type: application/json' -X GET http://localhost:8888/api/v1/items/f4a44b89-cd76-4005-9f49-d7a19373ba4a
```
```
HTTP/1.1 200 OK
date: Sun, 24 Jan 2021 11:04:44 GMT
server: uvicorn
content-length: 101
content-type: application/json

{"name":"Item 1","description":"First Item","price":9.99,"id":"f4a44b89-cd76-4005-9f49-d7a19373ba4a"}
```
**PUT**
```
$ curl -i  -H 'Content-Type: application/json' -X PUT http://localhost:8888/api/v1/items/f4a44b89-cd76-4005-9f49-d7a19373ba4a --data-binary @- <<EOF
{
  "name": "Item 2",
  "description": "First Item",
  "price": 9.99
}
EOF
```
```
HTTP/1.1 200 OK
date: Sun, 24 Jan 2021 11:05:53 GMT
server: uvicorn
content-length: 101
content-type: application/json

{"name":"Item 2","description":"First Item","price":9.99,"id":"f4a44b89-cd76-4005-9f49-d7a19373ba4a"}
```
**DELETE**
```
$ curl -i  -H 'Content-Type: application/json' -X DELETE http://localhost:8888/api/v1/items/f4a44b89-cd76-4005-9f49-d7a19373ba4a
```
```
HTTP/1.1 204 No Content
date: Sun, 24 Jan 2021 11:06:39 GMT
server: uvicorn
```

Using the `docker` command, we can analyse the installed images and running containers:

```
# docker image ls 

REPOSITORY                          TAG                 IMAGE ID            CREATED             SIZE
compose-fastapi_web                 latest              5d9f3620b3b2        23 seconds ago      1.12GB
mongo                               latest              ca8e14b1fda6        3 days ago          493MB
```

```
# docker container ls

CONTAINER ID        IMAGE                 COMMAND                  CREATED             STATUS              PORTS                      NAMES
8e5070310fa6        compose-fastapi_web   "/start.sh"              5 seconds ago       Up 3 seconds        0.0.0.0:8888->80/tcp       compose-fastapi_web_1
594ee8ee2c72        mongo:latest          "docker-entrypoint.s…"   6 seconds ago       Up 5 seconds        0.0.0.0:27017->27017/tcp   compose-fastapi_mongodb_1
```

## FastAPI Application

The file `main.py` is the entrypoint of the application:

```
app = FastAPI(
    title=settings.PROJECT_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()


app.include_router(api_router, prefix=settings.API_V1_STR)
```

We create the app by instantiating  the `FastAPI` object .
With `app.include_router(api_router, prefix=settings.API_V1_STR)` we tell the app to include endpoints.
Moreover, there are two event hooks: `startup` and `shutdown`, in which we create and close the connection to MongoDB.
```
async def connect_to_mongo():
    db.client = AsyncIOMotorClient(
        settings.MONGODB_URL  
     )

async def close_mongo_connection():
    db.client.close()
```
The FastAPI app defines endpoints in the folder `api/api_v1/endpoints/`. Below is an example for the GET-Endpoint to 
retrieve an Item:
```
@router.get("/{item_id}", response_model=Item,  status_code=status.HTTP_200_OK)
async def get_item(item_id: str,  db: AsyncIOMotorClient = Depends(get_database)):
    item = await crud_item.read_item(item_id, db)

    if item is None:
        return Response(status_code=HTTP_404_NOT_FOUND)
    else:
        return item
```
The values of the configuration of the application in `core/config.py` are automatically detected from the set environment
variables by using the `pydantic` package:

```
class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str
    MONGODB_URL: str
    MONGODB_DATABASE: str
    MONGODB_COLLECTION: str

    class Config:
        case_sensitive = True


settings = Settings()
```

## References
* [Get started with Docker Compose](https://docs.docker.com/compose/gettingstarted/)
* [MongoDB](https://www.mongodb.com/de)
* [FastAPI](https://fastapi.tiangolo.com/)
* [FastAPI Docker Image](https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker)
* [Poetry](https://python-poetry.org/)