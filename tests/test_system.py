import asyncio

import pytest

data_for_test = {}


class TestUserAuth:

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
        print(resp.text)
        resp.raise_for_status()
        resp = resp.json()
        assert resp == {"message": "User created"}

    def test_activate_link(self, session, base_path_to_api):
        resp = session.get(f'{base_path_to_api["user"]}/activate/{self.activate_user_key}')
        print(resp.text)
        resp.raise_for_status()
        resp = resp.json()
        assert resp == {"message": "User activated"}

        resp = session.get(f'{base_path_to_api["user"]}/activate/{self.activate_user_key}')
        print(resp.text)
        assert resp.status_code == 400
        resp = resp.json()
        assert resp == {"message": "User already activated"}

        resp = session.get(f'{base_path_to_api["user"]}/activate/{self.invalid_activate_user_key}')
        print(resp.text)
        assert resp.status_code == 404
        resp = resp.json()
        assert resp == {"message": "User does not exist"}

        resp = session.get(f'{base_path_to_api["user"]}/activate/qw12W')
        print(resp.text)
        assert resp.status_code == 500

    def test_token_for_user_without_totp(self, session, base_path_to_api, user_data):
        resp = session.post(f'{base_path_to_api["auth"]}/token')
        print(resp.text)
        assert resp.status_code != 200

        resp = session.post(f'{base_path_to_api["auth"]}/token', json={
            "email": user_data['email'],
            "password": user_data['password'],
        })
        print(resp.text)
        resp.raise_for_status()
        assert resp.json()['message'] == "Token create successfully"
        data_for_test['access_token'] = resp.json()['access_token']

    def test_user_login(self, session, base_path_to_api, user_data):
        resp = session.get(f'{base_path_to_api["auth"]}/login', headers={
            "X-CSRF-TOKEN": session.cookies['csrf_access_token']
        }, cookies={
            "access_token": session.cookies.get('access_token'),
            "csrf_access_token": session.cookies.get('csrf_access_token')
        })
        print(resp.text)
        assert resp.json() == {"message": "Login in successfully"}
        assert resp.status_code == 200

        resp = session.get(f'{base_path_to_api["auth"]}/login', headers={
            "X-CSRF-TOKEN": session.cookies['csrf_access_token']
        }, cookies={
            "access_token": session.cookies.get('access_token'),
        })
        print(resp.text)
        assert resp.json() == {"message": "Missing csrf_access_token"}
        assert resp.status_code == 400

        resp = session.get(f'{base_path_to_api["auth"]}/login', cookies={
            "access_token": session.cookies.get('access_token'),
        })
        print(resp.text)
        assert resp.json() == {"message": "Missing X-CSRF-TOKEN"}
        assert resp.status_code == 400

    def test_get_user_info(self, session, base_path_to_api, user_data):
        resp = session.get(f'{base_path_to_api["user"]}/profile', headers={
            "X-CSRF-TOKEN": session.cookies['csrf_access_token']
        }, cookies={
            "access_token": session.cookies.get('access_token'),
            "csrf_access_token": session.cookies.get('csrf_access_token')
        })
        print(resp.text)
        resp.raise_for_status()
        resp = resp.json()
        assert resp['email'] == user_data['email']
        assert resp['password'] == ""
