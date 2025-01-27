import asyncio
import json

import pytest


class TestUser:

    async def make_activate_user_key(self, fernet, user_data):
        activate_user_key = await fernet.encrypt_data(user_data['email'])
        self.activate_user_key = activate_user_key.decode()

        invalid_activate_user_key = await fernet.encrypt_data("aboba@igoose.ru")
        self.invalid_activate_user_key = invalid_activate_user_key.decode()

    @pytest.fixture(autouse=True)
    def set_activate_user_key(self, fernet, user_data):
        asyncio.run(self.make_activate_user_key(fernet, user_data))

    def test_send_activate_link_to_email(self, session, base_path_to_api, user_data):
        resp = session.post(f'{base_path_to_api["user"]}/',
                            json=user_data)
        resp.raise_for_status()
        resp = resp.json()
        assert resp == {"message": "User created"}

    def test_activate_link(self, session, base_path_to_api):
        resp = session.get(f'{base_path_to_api["user"]}/activate/{self.activate_user_key}')
        resp.raise_for_status()
        resp = resp.json()
        assert resp == {"message": "User activated"}

        resp = session.get(f'{base_path_to_api["user"]}/activate/{self.activate_user_key}')
        assert resp.status_code == 400
        resp = resp.json()
        assert resp == {"message": "User already activated"}

        resp = session.get(f'{base_path_to_api["user"]}/activate/{self.invalid_activate_user_key}')
        assert resp.status_code == 404
        resp = resp.json()
        assert resp == {"message": "User does not exist"}

        resp = session.get(f'{base_path_to_api["user"]}/activate/qw12W')
        assert resp.status_code == 500
