
[![CircleCI](https://circleci.com/gh/dgroh/mangia.club.svg?style=shield&circle-token=10082966a4c30b9470239b535563789cc0b2a54c)](https://circleci.com/gh/dgroh/mangia.club)

# Mangia Club

This is the repository of the API of the **Mangia Club App**

## Getting Started

### Prerequisites

* [Python 3](https://docs.python.org/3/)
* [Git](https://git-scm.com/)
* [Docker](https://www.docker.com/) (required to run MongoDB and Redis)

### Running the application in developer mode

First clone the repository:

```
$ git clone https://github.com/dgroh/mangia.club.git
```

Open a command line from the root folder of the project and create a [python virtual environment](https://docs.python.org/3/library/venv.html).

From the root folder of the project inside the activated virtual environment create the following environment variables:

On Windows

```bash
set FLASK_APP=run.py
set FLASK_ENV=development
```

On Linux/Mac

```bash
set FLASK_APP=run.py
set FLASK_ENV=development
```

Also from the command line, install the project requirements:

```bash
$ pip install -r requirements.txt
```

### Starting MongoDB and Redis instances

The app uses [MongoDB](https://docs.mongodb.com/) as default database and [Redis](https://redis.io/) for caching.
To run them with the application run:

```
$ docker run --rm --name mangia-club-mongo -d -it -p 27017:27017 mongo:latest
$ docker run --rm --name mangia-club-redis -d -it -p 6379:6379 redis:latest
```

To use the Mongo-Cli to access the MongoDB instance of the application, run:

```
$ docker exec -it mangia-club-mongo mongo
```

To use the Redis-Cli to access the Redis instance of the application, run:

```
$ docker exec -it mangia-club-redis redis-cli
```

--------

To start the API runs:

```bash
$ flask run
```

This will start the API on http://localhost:5000

--------

To test the API you can use [Postman](https://www.postman.com/)

## Documentation

For generating the documentation based on the `docstrings` we use [pdoc](https://pdoc3.github.io/pdoc/doc/pdoc/) 


If a `docstring` has been changed, run:

```bash
$ pdoc api --html -o docs --force
```

This will update the current [index.html](docs/api/index.html)

## Built With

* [Python 3](https://docs.python.org/3/)
* [Flask](https://palletsprojects.com/p/flask/)
* [MongoDB](https://docs.mongodb.com/)
* [Redis](https://redis.io/)
* [Docker](https://www.docker.com/)

## License

&copy; Copyright 2020, Daniel Groh. All Rights Reserved
