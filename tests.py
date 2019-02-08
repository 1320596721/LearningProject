import unittest
from nowStagram import app


class NowstagramTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.app = app.test_client()
        print('setUp')

    def tearDown(self):
        print('tearDown')

    def register(self, username, password):
        return self.app.post('/register/', data={'username': username, 'password': password}, follow_redirects=True)

    def login(self, username, password):
        return self.app.post('/login/', data={'username': username, 'password': password}, follow_redirects=True)

    def logout(self):
        return self.app.get('/logout/')

    def test_reg_login_logout(self):
        assert self.register("123", "lgx").status_code == 200
        assert b'-123' in self.app.open('/').data
        self.logout()
        assert b'-123' not in self.app.open('/').data
        assert self.login("123", "lgx")
        assert b'-123' in self.app.open('/').data

    def test_profile(self):
        r = self.app.open('/profile/3/', follow_redirects=True)
        assert r.status_code == 200
        assert b'password' in r.data
        self.register("hello", "world")
        assert b"hello" in self.app.open('/profile/1/', follow_redirects=True).data


