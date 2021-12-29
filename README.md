### Pandalog

Pandalog is a bundle of independent, executable scripts to bridge gaps in the new Graylog [permission model](https://docs.graylog.org/docs/permission-management#).

The executable scripts are modularized and highly extensible, so future use-cases can be easily integrated into the application.

The following use-cases are currently supported:
- create/retrieve an STS token (requires user password)
- share one or multiple streams with one or multiple teams
- share all streams with one or multiple teams
- "unshare" one or multiple streams with one or multiple teams
- "unshare" all streams with one or multiple teams

At the time of this writing, we're not enforcing PKI infrastructure; for this reason Pandalog does not install CA root certificates to establish trust, thus HTTPS requests skip verification.

### Usage

```
Usage: pandalog [OPTIONS] COMMAND [ARGS]...

  Pandalog - Bitpanda Graylog Python Wrapper

  Example Usage:

  $ export GRAYLOG_HOST=graylog.example.bitpanda
  $ export GRAYLOG_TOKEN=$(pandalog-auth get-sts-token -u ${USER} -p ${PASS})
  $ pandalog get-teams
  ID					        NAME
  6197bfc8eda84503ac69a8c8		All Pandas
  6197bfc8eda84503ac69a8c9		External
  6197bfc8eda84503ac69a8c1		staging-developer
  ... TRUNCATED ...
  $ pandalog get-streams
  ID					        TITLE
  614da2ff22df8b0d6d1e2485		AKHQ
  5e37f50e84c5320016ebd0c6		API
  5e380901978444001608e368		API Internal
  5f7df10d972d6200141676f7		Admin
  ... TRUNCATED ...
  $ pandalog to-stream --all "All Pandas,Some Pandas"
  $ pandalog from-stream --streams "API,ACME" "staging-developer"

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  from-stream  unshare stream(s) with team(s)
  get-streams  list streams
  get-teams    list teams
  to-stream    share stream(s) with team(s)
```

### Installation

Pre-requisites:
- Docker OR
- Python3

There are three ways to install pandalog:
1. Build the Dockerfile
2. Run the installation script inside a virtual environment
3. Pull the image from ECR registry (in roadmap, not available yet)

To build the Dockerfile locally:

```
# clone repo and go to the project root directory
$ git clone ssh://git@git.github.com/bitpanda-labs/pandalog.git && cd pandalog
# build the docker image
$ DOCKER_BUILDKIT=1 docker build -t ${image}:${tag} -f ci/docker/Dockerfile .
```

To install it in a virtual environment:

```
# install venv package
$ python3 -m pip install virtualenv
# clone repo and go to the project root directory
$ git clone ssh://git@git.github.com/bitpanda-labs/pandalog.git && cd pandalog
# create a virtualenv inside the directory
$ python3 -m venv env
# activate the virtualenv
$ source env/bin/activate
# install pandalog inside the virtualenv
(env)$ python3 setup.py install 
```

### Authentication

Before you are able to interact with Graylog API, you should obtain a temporary session token.

To create or retrieve an existing token, you can use `pandalog-auth`. Of course, to create that token, you will need to provide your password the first time around.

Pandalog supports three different ways of providing/storing the password:

1. `GRAYLOG_PASS` environment variable
2. `-p/--password` optional command-line argument
3. if none of the above is specified, pandalog will prompt you for the password (safest option)

For instance:

```
$ pandalog-auth get-sts-token -u ${USER}
Password: <- provide your password
edc9df021...truncated... <- copy the token and store it somewhere safe
```

Once you get a hold of the token, you can authenticate your requests by passing it along with the `-t/--token` flag, or by storing it in a `GRAYLOG_TOKEN` environment variable. The token expires within 24 hours.

### Limitations

- Graylog API does not include a `PATCH` method for adding/removing shares, i.e. every `POST` request must contain in the JSON body all the existing grants +/- the grants being updated)
- Due to the limitation above, additional API calls are made to merge grants, taking anywhere between 5-10 seconds to fulfill a request end-to-end
- As already mentioned, HTTPS requests are not verified due to lack of a PKI infrastructure for self-signed certificates

### Next Steps

- Write unit tests
- Add logging capabilities
- Extend functionality to enable sharing at user-level
- Extend functionality by accepting files instead of command-line arguments
