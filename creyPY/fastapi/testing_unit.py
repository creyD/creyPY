import json
import unittest
from typing import Type

from httpx import ASGITransport, AsyncClient, Response
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy_utils import create_database, database_exists, drop_database

from creyPY.fastapi.models.base import Base


class AbstractTestAPI(unittest.IsolatedAsyncioTestCase):
    client: AsyncClient
    default_headers: dict = {}

    @classmethod
    def setUpClass(cls, app, headers={}) -> None:
        cls.client = AsyncClient(
            transport=ASGITransport(app=app), base_url="http://testserver", follow_redirects=True
        )
        cls.default_headers = headers

    @classmethod
    def setup_database(
        cls,
        sync_db_url: str,
        async_db_url: str,
        base: Type[Base],
        btree_gist: bool = False,
        ssl_mode: str = "require",
    ):
        cls.engine_s = create_engine(
            sync_db_url,
            echo=False,
            pool_pre_ping=True,
            connect_args={"sslmode": ssl_mode},
        )
        if database_exists(cls.engine_s.url):
            drop_database(cls.engine_s.url)
        create_database(cls.engine_s.url)

        if btree_gist:
            with cls.engine_s.begin() as conn:
                conn.execute(text("CREATE EXTENSION IF NOT EXISTS btree_gist"))

        # Migrate
        base.metadata.create_all(cls.engine_s)

        cls.engine = create_async_engine(
            async_db_url,
            echo=False,
            pool_pre_ping=True,
            connect_args={"sslmode": ssl_mode},
        )

    async def get(self, url: str, r_code: int = 200, parse_json=True) -> dict | bytes:
        re = await self.client.get(url, headers=self.default_headers)
        if re.status_code != r_code:
            print(re.content)
        self.assertEqual(r_code, re.status_code)
        return re.json() if parse_json else re.content

    async def delete(self, url: str, r_code: int = 204) -> dict | None:
        re = await self.client.delete(url, headers=self.default_headers)
        if re.status_code != r_code:
            print(re.content)
        self.assertEqual(r_code, re.status_code)
        return re.json() if r_code != 204 else None

    async def post(
        self, url: str, obj: dict | str = {}, r_code: int = 201, raw_response=False, *args, **kwargs
    ):
        re = await self.client.post(
            url,
            data=json.dumps(obj) if isinstance(obj, dict) else obj,
            headers=self.default_headers | {"Content-Type": "application/json"},
            *args,
            **kwargs,
        )
        if re.status_code != r_code:
            print(re.content)
        if not raw_response:
            self.assertEqual(r_code, re.status_code)
        return re.json() if not raw_response else re

    async def post_file(
        self, url: str, file, r_code: int = 201, raw_response=False, *args, **kwargs
    ) -> dict | bytes | Response:
        re = await self.client.post(
            url,
            files={"file": file},
            headers=self.default_headers,
            *args,
            **kwargs,
        )
        if re.status_code != r_code:
            print(re.content)
        self.assertEqual(r_code, re.status_code)
        return re.json() if not raw_response else re

    async def patch(
        self, url: str, obj: dict | str = {}, r_code: int = 200, raw_response=False, *args, **kwargs
    ) -> dict | bytes | Response:
        re = await self.client.patch(
            url,
            data=json.dumps(obj) if isinstance(obj, dict) else obj,
            headers=self.default_headers | {"Content-Type": "application/json"},
            *args,
            **kwargs,
        )
        if re.status_code != r_code:
            print(re.content)
        self.assertEqual(r_code, re.status_code)
        return re.json() if not raw_response else re

    async def put(
        self, url: str, obj: dict | str = {}, r_code: int = 200, raw_response=False, *args, **kwargs
    ) -> dict | bytes | Response:
        re = await self.client.put(
            url,
            data=json.dumps(obj) if isinstance(obj, dict) else obj,
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
        self.assertEqual(r_code, re.status_code)
        return re.json() if not raw_response else re

    async def obj_lifecycle(
        self,
        input_obj: dict,
        url: str,
        pagination: bool = True,
        id_field: str = "id",
        created_at_check: bool = True,
        patch: dict | None = None,
    ):
        # GET LIST
        re = await self.get(url)
        if pagination:
            self.assertEqual(re["total"], 0)
            self.assertEqual(len(re["results"]), 0)
        else:
            self.assertEqual(len(re), 0)

        # CREATE
        re = await self.post(url, obj=input_obj)
        self.assertIn(id_field, re)
        self.assertIsNotNone(re[id_field])

        if created_at_check:
            self.assertIn("created_at", re)
            self.assertIsNotNone(re["created_at"])

        obj_id = str(re[id_field])

        # GET
        re = await self.get(f"{url}{obj_id}/")
        self.assertEqual(re[id_field], obj_id)

        # PATCH
        if patch:
            for key, value in patch.items():
                input_obj[key] = value
            re = await self.patch(f"{url}{obj_id}/", obj=input_obj)
            for key, value in patch.items():
                self.assertEqual(re[key], value)

        # GET LIST
        re = await self.get(url)
        if pagination:
            self.assertEqual(re["total"], 1)
            self.assertEqual(len(re["results"]), 1)
        else:
            self.assertEqual(len(re), 1)

        # DELETE
        await self.delete(f"{url}{obj_id}")

        # GET LIST
        re = await self.get(url)
        if pagination:
            self.assertEqual(re["total"], 0)
            self.assertEqual(len(re["results"]), 0)
        else:
            self.assertEqual(len(re), 0)

        # GET
        await self.get(f"{url}{obj_id}", parse_json=False, r_code=404)
