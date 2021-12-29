"""Pandalog collection of entrypoint scripts

Scripts:
- pandalog
- pandalog-auth

To install the collection, use either one of the following options:

1) Build the Dockerfile and run the application
2) Run "python3 setup.py install"

The scripts are installed as executable binaries under /usr/local/bin.

It is always preferable to isolate the application execution in a
virtual environment or a container.
"""
import click
import logging
from pandalog.client import GraylogAPIClient


@click.group()
@click.version_option()
def auth_entrypoint():
    """Pandalog Auth - Retrieve STS tokens for Pandalog user

    \b
    Example usage:
    \b
    $ pandalog-auth get-sts-token -h $HOST -u $USER
    $ pandalog-auth get-sts-token -h $HOST -u $USER -p ${PASS}
    """
    pass


@auth_entrypoint.command()
@click.option("-h", "--host",
              required=True,
              envvar="GRAYLOG_HOST",
              type=str,
              help="graylog host")
@click.option("-u", "--user",
              required=True,
              envvar="GRAYLOG_USER",
              type=str,
              help="graylog user")
@click.option("-p", "--password",
              prompt=True,
              hide_input=True,
              type=str,
              envvar="GRAYLOG_PASS",
              help="graylog password")
def get_sts_token(host: str,
                  user: str,
                  password: str):
    """get/issue a temporary session token"""
    # initialize graylog API client
    client = GraylogAPIClient(host)
    # retrieve, dump STS token
    print(client.get_sts_token(user, password))


@click.group()
@click.version_option()
def entrypoint():
    """Pandalog - Bitpanda Graylog Python Wrapper

    \b
    Example Usage:
    \b
    $ GRAYLOG_HOST=logs.staging.bitpanda
    $ GRAYLOG_TOKEN=$(pandalog-auth get-sts-token -u ${USER} -p ${PASS})
    $ pandalog get-teams
    $ pandalog get-streams
    $ pandalog to-stream --all "All Pandas,developer"
    $ pandalog from-stream --streams "API,ledger" "staging-developer"
    """
    pass


@entrypoint.command()
@click.option("-h", "--host",
              required=True,
              envvar="GRAYLOG_HOST",
              type=str,
              help="graylog host")
@click.option("-t", "--token",
              required=True,
              envvar="GRAYLOG_TOKEN",
              type=str,
              help="graylog API token")
def get_teams(host: str,
              token: str):
    """list teams"""

    # initialize graylog API client
    client = GraylogAPIClient(host)
    # retrieve list of all teams
    teams = client.get_teams(token)
    # print stdout header
    print("ID\t\t\t\t\tNAME")
    # sort teams in alphanumerical order
    ordered = sorted(teams, key=lambda x: x["name"])
    # loop over sorted list
    for team in ordered:
        # print team ID and name
        print("{}\t\t{}".format(team.get("id"),
                                team.get("name")))


@entrypoint.command()
@click.option("-h", "--host",
              required=True,
              envvar="GRAYLOG_HOST",
              type=str,
              help="graylog host")
@click.option("-t", "--token",
              required=True,
              envvar="GRAYLOG_TOKEN",
              type=str,
              help="graylog API token")
def get_streams(host: str,
                token: str):
    """list streams"""

    # initialize graylog API client
    client = GraylogAPIClient(host)
    # retrieve list of all streams
    streams = client.get_streams(token)
    # print stdout header
    print("ID\t\t\t\t\tTITLE")
    # sort streams in alphanumerical order
    ordered = sorted(streams, key=lambda x: x["title"])
    # loop over sorted list
    for stream in ordered:
        # print stream ID and title
        print("{}\t\t{}".format(stream.get("id"),
                                stream.get("title")))


@entrypoint.command()
@click.option("-h", "--host",
              required=True,
              envvar="GRAYLOG_HOST",
              type=str,
              help="graylog host")
@click.option("-t", "--token",
              required=True,
              envvar="GRAYLOG_TOKEN",
              type=str,
              help="graylog API token")
@click.option("-a", "--all",
              is_flag=True,
              type=bool,
              help="all streams")
@click.option("-s", "--stream-names",
              required=False,
              type=str,
              help="comma-separated list of streams")
@click.argument("team-names", nargs=-1)
def to_stream(host: str,
              token: str,
              all: bool,
              stream_names: str,
              team_names: list):
    """share stream(s) with team(s)"""

    # initialize graylog API client
    client = GraylogAPIClient(host)
    # initialize empty list of teams
    teams = []
    # loop over team names
    for team in team_names:
        # retrieve team based on the name and append to the list
        teams.append(client.get_team(team, token))

    # initialize empty list of streams
    streams = []
    # if --all flag is set
    if all:
        # gather list of all streams
        streams = client.get_streams(token)
    # else (i.e., if --stream-names is defined)
    else:
        # if streams were provided
        if stream_names is not None:
            split_streams = [s.strip() for s in stream_names.split(",")]
            # for each specified stream
            for stream in split_streams:
                # append stream to list
                streams.append(client.get_stream(stream, token))
        # if --all flag is not set and no stream was provided
        else:
            # print error and exit
            raise SystemExit("please provide streams or set the --all flag")

    # loop over streams
    for stream in streams:
        # add view permissions to specified teams to current stream
        client.to_stream(stream.get("id"), "view", teams, token)


@entrypoint.command()
@click.option("-h", "--host",
              required=True,
              envvar="GRAYLOG_HOST",
              type=str,
              help="graylog host")
@click.option("-t", "--token",
              required=True,
              envvar="GRAYLOG_TOKEN",
              type=str,
              help="graylog API token")
@click.option("-a", "--all",
              is_flag=True,
              type=bool,
              help="all streams")
@click.option("-s", "--stream-names",
              required=False,
              type=str,
              help="comma-separated list of streams")
@click.argument("team-names", nargs=-1)
def from_stream(host: str,
                token: str,
                all: bool,
                stream_names: str,
                team_names: list):
    """unshare stream(s) with team(s)"""
    # initialize graylog API client
    client = GraylogAPIClient(host)
    # initialize empty list of teams
    teams = []
    # loop over team names
    for team in team_names:
        # retrieve team based on the name and append to the list
        teams.append(client.get_team(team, token))

    # initialize empty list of streams
    streams = []
    # if --all flag is set
    if all:
        # gather list of all streams
        streams = client.get_streams(token)
    # else (i.e., if --stream-names is defined)
    else:
        # if streams were provided
        if stream_names is not None:
            split_streams = [s.strip() for s in stream_names.split(",")]
            # for each specified stream
            for stream in split_streams:
                # append stream to list
                streams.append(client.get_stream(stream, token))
        # if --all flag is not set and no stream was provided
        else:
            # print error and exit
            raise SystemExit("please provide streams or set the --all flag")

    # loop over streams
    for stream in streams:
        # remove view permissions from specified teams from current stream
        client.from_stream(stream.get("id"), "view", teams, token)
