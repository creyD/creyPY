import json

from fastapi.testclient import TestClient


class GenericClient(TestClient):
    def __init__(self, client):
        self.c = TestClient(client)

    def get(self, url: str, r_code:int =200, parse_json=True):
        re = self.c.get(url)
        if re.status_code != r_code:
            print(re.content)
        assert r_code == re.status_code
        return re.json() if parse_json else re.content

    def delete(self, url: str, r_code:int =204):
        re = self.c.delete(url)
        if re.status_code != r_code:
            print(re.content)
        assert r_code == re.status_code
        return re.json() if r_code != 204 else None

    def post(self, url: str, obj: dict ={}, r_code:int =201, raw_response=False, *args, **kwargs):
        re = self.c.post(
            url, data=json.dumps(obj), headers={"Content-Type": "application/json"}, *args, **kwargs
        )
        if re.status_code != r_code:
            print(re.content)
        assert r_code == re.status_code
        return re.json() if not raw_response else re

    def post_file(self, url: str, file, r_code:int =201, raw_response=False, *args, **kwargs):
        re = self.c.post(url, files={"file": file}, *args, **kwargs)
        if re.status_code != r_code:
            print(re.content)
        assert r_code == re.status_code
        return re.json() if not raw_response else re

    def patch(self, url: str, obj: dict ={}, r_code:int =200, raw_response=False, *args, **kwargs):
        re = self.c.patch(
            url, data=json.dumps(obj), headers={"Content-Type": "application/json"}, *args, **kwargs
        )
        if re.status_code != r_code:
            print(re.content)
        assert r_code == re.status_code
        return re.json() if not raw_response else re

    def put(self, url: str, obj: dict = {}, r_code:int =200, raw_response=False, *args, **kwargs):
        re = self.c.put(
            url,
            data=json.dumps(obj),
            headers={
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

    def obj_lifecycle(self, input_obj: dict, url: str, pagination: bool = True):
        # GET LIST
        re = self.get(url)
        if pagination:
            assert re["total"] == 0
            assert len(re["results"]) == 0
        else:
            assert len(re) == 0

        # CREATE
        re = self.post(url, obj=input_obj)
        assert "id" in re
        assert re["id"] is not None
        assert re["created_at"] is not None

        obj_id = str(re["id"])

        # GET
        re = self.get(f"{url}{obj_id}/")
        assert re["id"] == obj_id

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
        self.get(f"{url}{obj_id}", parse_json=False, r_code:int =404)
