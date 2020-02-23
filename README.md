# Mangia Club

This is the repository of the API of the **Mangia Club App**

## Getting Started

### Prerequisites

* [Python 3](https://docs.python.org/3/)
* [Git](https://git-scm.com/)
* [Docker](https://www.docker.com/) (required to run MongoDB)

### Running the application

First clone the repository:

```
$ git clone https://github.com/dgroh/mangia.club.git
```

Open a command line from the root folder of the project and create a [python virtual environment](https://docs.python.org/3/library/venv.html).

From the root folder of the project inside the activated virtual environment create the following environment variables:

**On Windows**

```bash
set FLASK_APP=main.py
set FLASK_ENV=development
set FLASK_DEBUG=0
set MONGO_DB_HOST=localhost
set MONGO_DB_PORT=27017
```

**On Linux/Mac**

```bash
export FLASK_APP=main.py
export FLASK_ENV=development
export FLASK_DEBUG=0
export MONGO_DB_HOST=localhost
export MONGO_DB_PORT=27017
```

Also from the command line, install the project requirements:

```bash
$ pip install -r requirements.txt
```

The app uses [MongoDB](https://docs.mongodb.com/) as default database and the easiest way to run MongoDB with the application is via [Docker](https://www.docker.com/), simply run:

```
$ docker run --rm --name mangia-club-mongo -d -it -p 27017:27017 mongo:latest
```

> By default the API will try to access MongoDB on http://localhost:27017. To change that just re-set the environments variables `MONGO_DB_HOST` and `MONGO_DB_PORT` with the desired values

To run the API runs:

```bash
$ flask run
```

This will start the API on http://localhost:5000

To test the API you can use [Postman](https://www.postman.com/)

## Built With

* [Python 3](https://docs.python.org/3/)
* [Flask](https://palletsprojects.com/p/flask/)
* [MongoDB](https://docs.mongodb.com/)
* [Docker](https://www.docker.com/)

## License

&copy; Copyright 2020, Daniel Groh. All Rights Reserved