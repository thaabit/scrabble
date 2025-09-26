# Scrabble - the game

## Documentation

## Endpoints

### Hello (GET /)
Basic call to show the server is up
#### Response
    $ curl 127.0.0.1:6000/ | jq
    { "success": 1 }


## Running Instances

| Deployment            | Public Base URL                                 |
|-----------------------|-------------------------------------------------|
| Production            |   |

# Running
The easiest way is to use [docker-compose](https://docs.docker.com/compose/install/).
You will need [Docker](https://docs.docker.com/engine/install/)

Once you have those installed, you can get the api and database up and running with two commands:
    docker compose build
    docker compose up

The api should be available at http://localhost:6000/

    $ curl http://localhost:6000/ | jq
    {
    "success": 1
    }

#### Some useful docker commands
    # attach to the api container
    docker exec -it scrabble-api /bin/bash

    # freeze requirements.txt
    docker exec -it scrabble-api pip freeze > /api/requirements.txt

    # attach to the database
    docker exec -it scrabble-db mariadb -ualpha -palpha scrabble

    # dump database
    docker exec -it scrabble-db mariadb-dump -uroot -pasdf scrabble -r docker-entrypoint-initdb.d/dump.sql

    # reset volumes in order to reinitialized the db
    docker-compose down -v

    # run unit tests after building app
    docker exec -it scrabble-api pytest

# Deploying
In order to deploy to live, simply make a pull request.  Once merged to master, the deployment will happen automatically in OpenShift.
The `openshift_setup` script is useful for importing the project into OpenShift. If you needed to recreate the project from
scratch in OpenShift, you would simply need to run all these commands below, provided the prod.env files have all necessary ENV vars.
