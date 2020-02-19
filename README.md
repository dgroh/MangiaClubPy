# Mangia Club

This is the repository of the API of the **Mangia Club App**

## Getting Started

### Prerequisites

* [Git](https://git-scm.com/)
* [Docker](https://www.docker.com/) with [docker-compose](https://docs.docker.com/compose/install/)

The API is containerized and can be run inside [Docker](https://www.docker.com/). Therefore there is no need to install any other dependencies.

### Running the application

First clone the repository:

```
$ git clone https://github.com/dgroh/mangia.club.git
```

Then inside the repository folder start the docker container:

```
$ docker-compose build
```

```
$ docker-compose up
```

This will start the API on http://127.0.0.1:5000 and also [MongoDB](https://docs.mongodb.com/)

To test the [MongoDB](https://docs.mongodb.com/) commands against the containerized database, run in a separated window the following command:

```
$ docker run -it --network mangiaclub_default --rm mongo mongo --host db
```

To test the API you can use [Postman](https://www.postman.com/)

## Built With

* [Python 3](https://docs.python.org/3/)
* [Flask](https://palletsprojects.com/p/flask/)
* [MongoDB](https://docs.mongodb.com/)
* [Docker](https://www.docker.com/)

## License

&copy; Copyright 2020, Daniel Groh. All Rights Reserved