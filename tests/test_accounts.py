"""Accounts, sessions, invites, password reset and shared roads, against a real server on an ephemeral port."""
import http.client
import importlib.util
import json
import os
import sys
import tempfile
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

APP = Path(__file__).resolve().parents[1] / "app"
LINE = [[-78.30, 38.66 + i * 0.001] for i in range(12)]


@pytest.fixture(scope="module")
def srv():
    os.environ["SWITCHBACK_DATA"] = tempfile.mkdtemp(); os.environ["SWITCHBACK_AUTH"] = "on"
    sys.path.insert(0, str(APP))
    spec = importlib.util.spec_from_file_location("server_under_test", APP / "server.py"); m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), m.H); threading.Thread(target=httpd.serve_forever, daemon=True).start()
    yield m, httpd.server_address[1]
    httpd.shutdown()


class Client:
    def __init__(self, port):
        self.port, self.cookie = port, None

    def call(self, method, path, body=None, csrf=True):
        c = http.client.HTTPConnection("127.0.0.1", self.port); h = {"Content-Type": "application/json"}
        if csrf:
            h["X-Requested-With"] = "switchback"
        if self.cookie:
            h["Cookie"] = self.cookie
        c.request(method, path, json.dumps(body) if body is not None else None, h); r = c.getresponse(); raw = r.read()
        sc = r.getheader("Set-Cookie")
        if sc:
            self.cookie = sc.split(";")[0] if not sc.startswith("sb_session=;") else None
        try:
            return r.status, json.loads(raw)
        except Exception:
            return r.status, raw

    get = lambda self, p: self.call("GET", p)
    post = lambda self, p, b=None, csrf=True: self.call("POST", p, b or {}, csrf)


def test_setup_and_access(srv):
    m, port = srv; a = Client(port)
    assert a.get("/api/state")[1]["setup"] is True
    assert a.get("/api/candidates")[0] == 401
    assert a.get("/data/candidates.json")[0] == 404 and a.get("/server.py")[0] == 404 and a.get("/static/index.html")[0] == 200
    assert a.post("/api/setup", {"code": "wrong", "username": "boss", "password": "correct horse battery"})[0] == 403
    code = m.STORE.setup_code()
    assert a.post("/api/setup", {"code": code, "username": "boss", "password": "short"})[0] == 400
    assert a.post("/api/setup", {"code": code, "username": "boss", "password": "correct horse battery"})[0] == 200
    assert a.get("/api/state")[1]["user"]["role"] == "admin" and a.get("/api/state")[1]["setup"] is False
    assert a.post("/api/setup", {"code": code, "username": "x2", "password": "correct horse battery"})[0] == 409
    assert a.get("/api/candidates")[0] == 200


def test_csrf_header_required(srv):
    _, port = srv; a = Client(port); a.post("/api/login", {"username": "boss", "password": "correct horse battery"})
    assert a.post("/api/prefs", {"prefs": {}}, csrf=False)[0] == 403


def test_login_lockout(srv):
    _, port = srv
    for _ in range(5):
        assert Client(port).post("/api/login", {"username": "boss", "password": "nope-nope-nope"})[0] == 401
    assert Client(port).post("/api/login", {"username": "boss", "password": "correct horse battery"})[0] == 429


def test_invite_reset_and_roles(srv):
    m, port = srv; m.STORE.fails.clear()
    admin = Client(port); assert admin.post("/api/login", {"username": "boss", "password": "correct horse battery"})[0] == 200
    tok = admin.post("/api/invite", {"role": "rider", "note": "riley"})[1]["token"]
    rider = Client(port)
    assert rider.get("/api/invite/" + tok)[1]["role"] == "rider"
    assert rider.post("/api/accept", {"token": tok, "username": "riley", "password": "tenletters1"})[0] == 200
    assert Client(port).get("/api/invite/" + tok)[0] == 410                       # single use
    assert rider.get("/api/users")[0] == 403 and rider.post("/api/invite", {"role": "admin"})[0] == 403
    # admin sets a password, then issues a reset link
    rid = [u for u in admin.get("/api/users")[1]["users"] if u["username"] == "riley"][0]["id"]
    assert admin.post("/api/users/password", {"id": rid, "password": "brand new pass"})[0] == 200
    assert rider.get("/api/candidates")[0] == 401                                  # old session signed out
    assert Client(port).post("/api/login", {"username": "riley", "password": "brand new pass"})[0] == 200
    rt = admin.post("/api/users/reset-link", {"id": rid})[1]["token"]
    r2 = Client(port); assert r2.get("/api/reset/" + rt)[1]["username"] == "riley"
    assert r2.post("/api/reset", {"token": rt, "password": "reset reset reset"})[0] == 200 and r2.get("/api/state")[1]["user"]["username"] == "riley"
    assert Client(port).get("/api/reset/" + rt)[0] == 410
    # last admin is protected
    aid = admin.get("/api/state")[1]["user"]["id"]
    assert admin.post("/api/users/role", {"id": aid, "role": "rider"})[0] == 400
    assert admin.post("/api/users/disable", {"id": aid, "disabled": True})[0] == 400
    assert admin.post("/api/users/delete", {"id": aid})[0] == 400
    # disabling a rider blocks login
    assert admin.post("/api/users/disable", {"id": rid, "disabled": True})[0] == 200
    assert Client(port).post("/api/login", {"username": "riley", "password": "reset reset reset"})[0] == 401


def test_shared_roads_and_permissions(srv):
    m, port = srv; m.STORE.fails.clear()
    admin = Client(port); admin.post("/api/login", {"username": "boss", "password": "correct horse battery"})
    rid = [u for u in admin.get("/api/users")[1]["users"] if u["username"] == "riley"][0]["id"]
    admin.post("/api/users/disable", {"id": rid, "disabled": False})
    rider = Client(port); assert rider.post("/api/login", {"username": "riley", "password": "reset reset reset"})[0] == 200
    new = rider.post("/api/custom", {"name": "Riley's Ridge", "line": LINE})[1]["id"]                       # public by default
    seen = [c for c in admin.get("/api/candidates")[1]["candidates"] if c["id"] == new][0]
    assert seen["added_by"] == "riley" and seen["shared"] is True and seen["mine"] is False and seen["manual"] is True
    assert rider.post("/api/custom/share", {"id": new, "shared": False})[0] == 200                           # owner makes it private
    assert not [c for c in admin.get("/api/candidates")[1]["candidates"] if c["id"] == new]
    assert [c for c in rider.get("/api/candidates")[1]["candidates"] if c["id"] == new][0]["mine"] is True
    assert admin.post("/api/settings", {"settings": {"share_roads_default": False}})[0] == 200               # server default flips to private
    private = rider.post("/api/custom", {"name": "Secret", "line": LINE})[1]["id"]
    assert not [c for c in admin.get("/api/candidates")[1]["candidates"] if c["id"] == private]
    third = admin.post("/api/invite", {"role": "rider"})[1]["token"]; t = Client(port); t.post("/api/accept", {"token": third, "username": "taylor", "password": "taylor taylor"})
    assert t.post("/api/custom/delete", {"id": new})[0] == 400 or t.post("/api/custom/delete", {"id": new})[0] == 403   # not theirs
    assert admin.post("/api/custom/delete", {"id": new})[0] == 200                                           # admin may remove any


def test_password_hashing_unit():
    sys.path.insert(0, str(APP)); import store
    h = store.hash_password("hunter2hunter2"); assert store.check_password("hunter2hunter2", h) and not store.check_password("x", h) and "hunter2" not in h


def test_username_whitespace_is_trimmed(srv):
    m, port = srv; m.STORE.fails.clear()
    assert Client(port).post("/api/login", {"username": "  BOSS \n", "password": "correct horse battery"})[0] == 200      # case-insensitive and trimmed
    assert Client(port).post("/api/login", {"username": "boss", "password": "correct horse battery "})[0] == 401          # passwords are never trimmed
    m.STORE.fails.clear()
    admin = Client(port); admin.post("/api/login", {"username": "boss", "password": "correct horse battery"})
    assert admin.post("/api/users/create", {"username": "  trimmed.user ", "password": "some long password", "role": "rider"})[0] == 200
    assert Client(port).post("/api/login", {"username": "trimmed.user", "password": "some long password"})[0] == 200
