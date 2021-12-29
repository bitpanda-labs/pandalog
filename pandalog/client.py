from __future__ import annotations
import requests
import pandalog.utils.transformation as transform

# Graylog plugins path constant
PLUGINS_PATH = "plugins/org.graylog.plugins.security"


class GraylogAPIClient:
    """defines graylog API client"""

    def __init__(self,
                 host: str):
        """constructor method"""

        self.host = f"https://{host}/api"

        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Requested-By": "cli"
        }

    def _get(self,
             endpoint: str,
             params: dict,
             token: str) -> dict:
        """internal implementation of /GET"""

        try:

            resp = requests.get(endpoint,
                                headers=self.headers,
                                params=params,
                                auth=(f"{token}", "session"),
                                verify=False)

            resp.raise_for_status()

        except requests.exceptions.RequestException as err:

            raise SystemExit(err)

        return resp.json()

    def _post(self,
              endpoint: str,
              **kwargs):
        """internal implementation of /POST"""

        params = {}  # params are optional

        payload = {}  # payload is optional (might include auth)

        auth = {}  # auth might be provided as payload for some calls

        if kwargs.get("params"):

            params = kwargs.get("params")

        if kwargs.get("payload"):

            payload = kwargs.get("payload")

        if kwargs.get("auth"):

            auth = kwargs.get("auth")

        try:

            resp = requests.post(endpoint,
                                 headers=self.headers,
                                 json=payload,
                                 auth=auth,
                                 params=params,
                                 verify=False)

            resp.raise_for_status()

        except requests.exceptions.RequestException as err:

            raise SystemExit(err)

        return resp.json()

    def _prepare(self,
                 stream_id: str,
                 token: str):
        """retrieve current user/team shares mapped to stream"""

        stream_grn = transform.to_grn("stream", stream_id)

        endpoint = f"{self.host}/authz/shares/entities/{stream_grn}/prepare"

        auth = (token, "session")

        payload = {}  # /prepare requires an empty payload

        response = self._post(endpoint,
                              headers=self.headers,
                              payload=payload,
                              auth=auth)

        return response.get("selected_grantee_capabilities")

    def get_sts_token(self,
                      user: str,
                      password: str) -> str:
        """retrieve/create a session token"""

        endpoint = f"{self.host}/system/sessions"

        payload = {
            "username": user,
            "password": password,
            "host": ""
        }

        response = self._post(endpoint,
                              headers=self.headers,
                              payload=payload)

        return response.get("session_id")

    def get_teams(self,
                  token: str) -> list:
        """returns all teams"""

        endpoint = f"{self.host}/{PLUGINS_PATH}/teams"

        teams = []

        params = {
            "page": 1,
            "per_page": 100,
            "sort": "name",
            "order": "asc"
        }

        response = self._get(endpoint,
                             params,
                             token).get("teams")

        teams.extend([{"id": team.get("id"),
                      "name": team.get("name")}
                      for team in response])

        return teams

    def get_team(self,
                 name: str,
                 token: str) -> str:
        """returns specified team"""

        endpoint = f"{self.host}/{PLUGINS_PATH}/teams"

        params = {
            "page": 1,
            "per_page": 100,
            "query": name,
            "sort": "name",
            "order": "asc"
        }

        try:

            team = self._get(endpoint,
                             params,
                             token).get("teams")[0]

        except IndexError as err:

            raise SystemExit(f"team not found: {err}")

        return team

    def get_streams(self,
                    token: str) -> list:
        """returns all streams"""

        endpoint = f"{self.host}/streams/paginated"

        streams = []

        params = {
            "page": 1,
            "per_page": 100,
            "sort": "name",
            "order": "asc"
        }

        response = self._get(endpoint,
                             params,
                             token).get("streams")

        streams.extend([{"id": stream.get("id"),
                        "title": stream.get("title")}
                        for stream in response])

        return streams

    def get_stream(self,
                   title: str,
                   token: str) -> list:

        endpoint = f"{self.host}/streams/paginated"

        streams = []

        params = {
            "page": 1,
            "per_page": 100,
            "query": title,
            "sort": "name",
            "order": "asc"
        }

        try:

            stream = self._get(endpoint,
                               params,
                               token).get("streams")[0]

        except IndexError as err:

            raise SystemExit(f"stream not found: {err}")

        return stream

    def to_stream(self, stream_id: str,
                  permission: str,
                  teams: list,
                  token: str):
        """share stream with team(s)"""

        current_mappings = self._prepare(stream_id, token)

        stream_grn = transform.to_grn("stream", stream_id)

        endpoint = f"{self.host}/authz/shares/entities/{stream_grn}"

        grants = current_mappings

        auth = (token, "session")

        payload = {}  # initializing empty payload, to be populated

        for team in teams:

            team_grn = transform.to_grn("team", team.get("id"))

            grants[team_grn] = permission

        payload["selected_grantee_capabilities"] = grants

        response = self._post(endpoint,
                              headers=self.headers,
                              payload=payload,
                              auth=auth)

    def from_stream(self,
                    stream_id: str,
                    permission: str,
                    teams: list,
                    token: str):
        """unshare stream with team(s)"""

        current_mappings = self._prepare(stream_id, token)

        stream_grn = transform.to_grn("stream", stream_id)

        endpoint = f"{self.host}/authz/shares/entities/{stream_grn}"

        grants = current_mappings

        auth = (token, "session")

        payload = {}  # initializing empty payload, to be populated

        for team in teams:

            team_grn = transform.to_grn("team", team.get("id"))

            if team_grn in grants:

                del grants[team_grn]

        payload["selected_grantee_capabilities"] = grants

        response = self._post(endpoint,
                              headers=self.headers,
                              payload=payload,
                              auth=auth)
