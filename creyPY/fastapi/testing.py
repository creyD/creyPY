import json

from fastapi.testclient import TestClient


class GenericClient(TestClient):
    def __init__(self, client):
        self.c = TestClient(client)
        self.default_headers = {}

    def get(self, url: str, r_code: int = 200, parse_json=True):
        re = self.c.get(url, headers=self.default_headers)
        if re.status_code != r_code:
            print(re.content)
        assert r_code == re.status_code
        return re.json() if parse_json else re.content

    def delete(self, url: str, r_code: int = 204):
        re = self.c.delete(url, headers=self.default_headers)
        if re.status_code != r_code:
            print(re.content)
        assert r_code == re.status_code
        return re.json() if r_code != 204 else None

    def post(
        self, url: str, obj: dict | str = {}, r_code: int = 201, raw_response=False, *args, **kwargs
    ):
        re = self.c.post(
            url,
            data=json.dumps(obj) if type(obj) == dict else obj,
            headers=self.default_headers | {"Content-Type": "application/json"},
            *args,
            **kwargs,
        )
        if re.status_code != r_code:
            print(re.content)
        assert r_code == re.status_code
        return re.json() if not raw_response else re

    def post_file(self, url: str, file, r_code: int = 201, raw_response=False, *args, **kwargs):
        re = self.c.post(
            url,
            files={"file": file},
            headers=self.default_headers,
            *args,
            **kwargs,
        )
        if re.status_code != r_code:
            print(re.content)
        assert r_code == re.status_code
        return re.json() if not raw_response else re

    def patch(
        self, url: str, obj: dict | str = {}, r_code: int = 200, raw_response=False, *args, **kwargs
    ):
        re = self.c.patch(
            url,
            data=json.dumps(obj) if type(obj) == dict else obj,
            headers=self.default_headers | {"Content-Type": "application/json"},
            *args,
            **kwargs,
        )
        if re.status_code != r_code:
            print(re.content)
        assert r_code == re.status_code
        return re.json() if not raw_response else re

    def put(
        self, url: str, obj: dict | str = {}, r_code: int = 200, raw_response=False, *args, **kwargs
    ):
        re = self.c.put(
            url,
            data=json.dumps(obj) if type(obj) == dict else obj,
            headers=self.default_headers
            | {
                "Content-Type": "application/json",
                "accept": "application/json",
            },
            *args,
            **kwargs,
        )
        if re.status_code != r_code:
            print(re.content)
        assert r_code == re.status_code
        return re.json() if not raw_response else re

    def obj_lifecycle(
        self,
        input_obj: dict,
        url: str,
        pagination: bool = True,
        id_field: str = "id",
        created_at_check: bool = True,
    ):
        # GET LIST
        re = self.get(url)
        if pagination:
            assert re["total"] == 0
            assert len(re["results"]) == 0
        else:
            assert len(re) == 0

        # CREATE
        re = self.post(url, obj=input_obj)
        assert id_field in re
        assert re[id_field] is not None

        if created_at_check:
            assert "created_at" in re
            assert re["created_at"] is not None

        obj_id = str(re[id_field])

        # GET
        re = self.get(f"{url}{obj_id}/")
        assert re[id_field] == obj_id

        # GET LIST
        re = self.get(url)
        if pagination:
            assert re["total"] == 1
            assert len(re["results"]) == 1
        else:
            assert len(re) == 1

        # DELETE
        self.delete(f"{url}{obj_id}")

        # GET LIST
        re = self.get(url)
        if pagination:
            assert re["total"] == 0
            assert len(re["results"]) == 0
        else:
            assert len(re) == 0

        # GET
        self.get(f"{url}{obj_id}", parse_json=False, r_code=404)
