"""SQLite store for Switchback accounts: users, sessions, invite/reset tokens, hand-added roads and server settings.

Standard library only. Passwords use scrypt; session and invite tokens are random and stored only as SHA-256 hashes.
"""
import hashlib
import hmac
import json
import re
import secrets
import sqlite3
import threading
import time
from pathlib import Path

DAY = 86400
SESSION_DAYS, INVITE_DAYS, RESET_HOURS = 30, 7, 24
USERNAME_RE = re.compile(r"^[A-Za-z0-9._-]{3,32}$")
DEFAULT_SETTINGS = {"share_roads_default": "1", "server_name": "Switchback"}
ROAD_ID_BASE = 100000        # hand-added roads get ids above the scan's (0..N) so they never collide


class ApiError(Exception):
    def __init__(self, status, msg):
        super().__init__(msg); self.status, self.msg = status, msg


def _h(token):
    return hashlib.sha256(token.encode()).hexdigest()


def hash_password(pw, n=2 ** 14, r=8, p=1):
    salt = secrets.token_bytes(16)
    dk = hashlib.scrypt(pw.encode(), salt=salt, n=n, r=r, p=p, dklen=32)
    return f"scrypt${n}${r}${p}${salt.hex()}${dk.hex()}"


def check_password(pw, stored):
    try:
        _, n, r, p, salt, dk = stored.split("$")
        got = hashlib.scrypt(pw.encode(), salt=bytes.fromhex(salt), n=int(n), r=int(r), p=int(p), dklen=32)
        return hmac.compare_digest(got, bytes.fromhex(dk))
    except Exception:
        return False


_DUMMY = hash_password("not-a-real-password")      # burned on unknown usernames so timing does not reveal them


def validate_username(u):
    if not USERNAME_RE.match(u or ""):
        raise ApiError(400, "Username must be 3-32 characters: letters, numbers, dot, dash or underscore.")


def validate_password(pw, username=""):
    if not isinstance(pw, str) or len(pw) < 10:
        raise ApiError(400, "Password must be at least 10 characters.")
    if username and pw.lower() == username.lower():
        raise ApiError(400, "Password must not be the same as the username.")
    if len(pw) > 200:
        raise ApiError(400, "Password is too long.")


class Store:
    def __init__(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(str(path), check_same_thread=False, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.lock = threading.RLock()
        self.fails = {}            # (ip, username) -> [count, locked_until]
        self.db.executescript("""
            CREATE TABLE IF NOT EXISTS users(id INTEGER PRIMARY KEY, username TEXT UNIQUE COLLATE NOCASE NOT NULL, pw TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'rider', disabled INTEGER NOT NULL DEFAULT 0, created INTEGER NOT NULL, prefs TEXT NOT NULL DEFAULT '{}');
            CREATE TABLE IF NOT EXISTS sessions(h TEXT PRIMARY KEY, user_id INTEGER NOT NULL, created INTEGER NOT NULL, expires INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS tokens(h TEXT PRIMARY KEY, kind TEXT NOT NULL, role TEXT, user_id INTEGER, created_by INTEGER,
                created INTEGER NOT NULL, expires INTEGER NOT NULL, used INTEGER NOT NULL DEFAULT 0, note TEXT);
            CREATE TABLE IF NOT EXISTS roads(id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT NOT NULL, cand TEXT NOT NULL,
                shared INTEGER NOT NULL DEFAULT 1, created INTEGER NOT NULL);
            CREATE TABLE IF NOT EXISTS settings(k TEXT PRIMARY KEY, v TEXT NOT NULL);
        """)

    # ---- helpers
    def q(self, sql, *a):
        with self.lock:
            return self.db.execute(sql, a).fetchall()

    def one(self, sql, *a):
        r = self.q(sql, *a)
        return r[0] if r else None

    def x(self, sql, *a):
        with self.lock:
            return self.db.execute(sql, a)

    # ---- settings
    def setting(self, k):
        r = self.one("SELECT v FROM settings WHERE k=?", k)
        return r["v"] if r else DEFAULT_SETTINGS.get(k)

    def settings(self):
        return {k: self.setting(k) for k in DEFAULT_SETTINGS}

    def set_setting(self, k, v):
        if k not in DEFAULT_SETTINGS:
            raise ApiError(400, f"Unknown setting {k}")
        self.x("INSERT INTO settings(k,v) VALUES(?,?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", k, str(v)[:100])

    # ---- first-run setup code (stops a stranger claiming an exposed fresh server)
    def user_count(self):
        return self.one("SELECT COUNT(*) c FROM users")["c"]

    def setup_code(self):
        if self.user_count():
            return None
        c = self.setting("setup_code")
        if not c or c == DEFAULT_SETTINGS.get("setup_code"):
            c = secrets.token_urlsafe(9)
            self.x("INSERT INTO settings(k,v) VALUES('setup_code',?) ON CONFLICT(k) DO UPDATE SET v=excluded.v", c)
        return c

    def check_setup_code(self, given):
        c = self.setup_code()
        return bool(c) and hmac.compare_digest(str(given or "").strip(), c)

    # ---- users
    def public_user(self, u, with_prefs=True):
        d = {"id": u["id"], "username": u["username"], "role": u["role"], "disabled": bool(u["disabled"]), "created": u["created"]}
        if with_prefs:
            d["prefs"] = json.loads(u["prefs"] or "{}")
        return d

    def create_user(self, username, pw, role="rider"):
        username = (username or "").strip()          # a stray space from a phone keyboard or paste is never part of a username
        validate_username(username); validate_password(pw, username)
        if role not in ("admin", "rider"):
            raise ApiError(400, "Role must be admin or rider.")
        try:
            cur = self.x("INSERT INTO users(username,pw,role,created) VALUES(?,?,?,?)", username, hash_password(pw), role, int(time.time()))
        except sqlite3.IntegrityError:
            raise ApiError(409, "That username is taken.")
        return cur.lastrowid

    def user(self, uid):
        return self.one("SELECT * FROM users WHERE id=?", uid)

    def users(self):
        return self.q("SELECT * FROM users ORDER BY username")

    def _active_admins(self, excluding=None):
        return self.one("SELECT COUNT(*) c FROM users WHERE role='admin' AND disabled=0 AND id<>?", excluding or -1)["c"]

    def set_password(self, uid, pw):
        u = self.user(uid)
        if not u:
            raise ApiError(404, "No such user.")
        validate_password(pw, u["username"])
        self.x("UPDATE users SET pw=? WHERE id=?", hash_password(pw), uid)
        self.x("DELETE FROM sessions WHERE user_id=?", uid)      # signs the user out everywhere

    def set_role(self, uid, role):
        if role not in ("admin", "rider"):
            raise ApiError(400, "Role must be admin or rider.")
        if role != "admin" and self.user(uid)["role"] == "admin" and not self._active_admins(uid):
            raise ApiError(400, "There must be at least one admin.")
        self.x("UPDATE users SET role=? WHERE id=?", role, uid)

    def set_disabled(self, uid, disabled):
        if disabled and self.user(uid)["role"] == "admin" and not self._active_admins(uid):
            raise ApiError(400, "You cannot disable the last admin.")
        self.x("UPDATE users SET disabled=? WHERE id=?", 1 if disabled else 0, uid)
        if disabled:
            self.x("DELETE FROM sessions WHERE user_id=?", uid)

    def delete_user(self, uid):
        u = self.user(uid)
        if not u:
            raise ApiError(404, "No such user.")
        if u["role"] == "admin" and not self._active_admins(uid):
            raise ApiError(400, "You cannot delete the last admin.")
        self.x("DELETE FROM sessions WHERE user_id=?", uid)
        self.x("DELETE FROM roads WHERE user_id=? AND shared=0", uid)       # private roads go with the user; shared ones stay
        self.x("DELETE FROM users WHERE id=?", uid)

    def set_prefs(self, uid, prefs):
        blob = json.dumps(prefs, separators=(",", ":"))
        if len(blob) > 20000:
            raise ApiError(400, "Preferences too large.")
        self.x("UPDATE users SET prefs=? WHERE id=?", blob, uid)

    # ---- login with simple lockout (5 failures -> 15 minutes, per client + username)
    def login(self, username, pw, ip):
        username = (username or "").strip()
        key = (ip, username.lower())
        now = time.time()
        f = self.fails.get(key)
        if f and f[1] > now:
            raise ApiError(429, "Too many failed attempts. Try again in a few minutes.")
        u = self.one("SELECT * FROM users WHERE username=?", username or "")
        ok = check_password(pw or "", u["pw"] if u else _DUMMY) and u is not None and not u["disabled"]
        if not ok:
            c = (f[0] if f and f[1] <= now else (f[0] if f else 0)) + 1
            self.fails[key] = [c, now + 900 if c >= 5 else 0]
            raise ApiError(401, "Wrong username or password.")
        self.fails.pop(key, None)
        return u

    # ---- sessions
    def new_session(self, uid):
        t = secrets.token_urlsafe(32); now = int(time.time())
        self.x("INSERT INTO sessions(h,user_id,created,expires) VALUES(?,?,?,?)", _h(t), uid, now, now + SESSION_DAYS * DAY)
        self.x("DELETE FROM sessions WHERE expires<?", now)
        return t

    def user_for_session(self, token):
        if not token:
            return None
        now = int(time.time())
        s = self.one("SELECT * FROM sessions WHERE h=? AND expires>?", _h(token), now)
        if not s:
            return None
        u = self.user(s["user_id"])
        if not u or u["disabled"]:
            return None
        if s["expires"] - now < (SESSION_DAYS - 1) * DAY:          # sliding expiry, refreshed at most daily
            self.x("UPDATE sessions SET expires=? WHERE h=?", now + SESSION_DAYS * DAY, s["h"])
        return u

    def drop_session(self, token):
        self.x("DELETE FROM sessions WHERE h=?", _h(token or ""))

    # ---- invite / password-reset tokens
    def create_token(self, kind, created_by, role=None, user_id=None, note=""):
        t = secrets.token_urlsafe(24); now = int(time.time())
        ttl = INVITE_DAYS * DAY if kind == "invite" else RESET_HOURS * 3600
        self.x("INSERT INTO tokens(h,kind,role,user_id,created_by,created,expires,note) VALUES(?,?,?,?,?,?,?,?)",
               _h(t), kind, role, user_id, created_by, now, now + ttl, note[:100])
        return t, now + ttl

    def peek_token(self, token, kind):
        r = self.one("SELECT * FROM tokens WHERE h=? AND kind=? AND used=0 AND expires>?", _h(token or ""), kind, int(time.time()))
        if not r:
            raise ApiError(410, "This link is invalid, expired or already used.")
        return r

    def use_token(self, token):
        self.x("UPDATE tokens SET used=1 WHERE h=?", _h(token))

    def pending_invites(self):
        return self.q("SELECT t.created, t.expires, t.role, t.note, u.username created_by FROM tokens t LEFT JOIN users u ON u.id=t.created_by "
                      "WHERE t.kind='invite' AND t.used=0 AND t.expires>? ORDER BY t.created DESC", int(time.time()))

    # ---- hand-added roads
    def add_road(self, uid, name, cand, shared):
        cur = self.x("INSERT INTO roads(user_id,name,cand,shared,created) VALUES(?,?,?,?,?)", uid, name, json.dumps(cand, separators=(",", ":")),
                     1 if shared else 0, int(time.time()))
        return ROAD_ID_BASE + cur.lastrowid

    def roads_for(self, uid):
        """Roads this user may see: everything shared, plus their own private ones. Each carries attribution."""
        out = []
        for r in self.q("SELECT r.*, u.username owner FROM roads r LEFT JOIN users u ON u.id=r.user_id WHERE r.shared=1 OR r.user_id=? ORDER BY r.id", uid):
            c = json.loads(r["cand"])
            c.update(id=ROAD_ID_BASE + r["id"], name=r["name"], manual=True, shared=bool(r["shared"]), mine=(r["user_id"] == uid),
                     added_by=r["owner"] or "a former user", added_on=time.strftime("%Y-%m-%d", time.localtime(r["created"])))
            out.append(c)
        return out

    def road(self, rid):
        r = self.one("SELECT * FROM roads WHERE id=?", rid - ROAD_ID_BASE)
        return r

    def all_roads_admin(self):
        return self.q("SELECT r.id, r.name, r.shared, r.created, u.username owner FROM roads r LEFT JOIN users u ON u.id=r.user_id ORDER BY r.id DESC")

    def delete_road(self, rid, user):
        r = self.road(rid)
        if not r:
            raise ApiError(404, "No such road.")
        if r["user_id"] != user["id"] and user["role"] != "admin":
            raise ApiError(403, "Only the person who added a road, or an admin, can remove it.")
        self.x("DELETE FROM roads WHERE id=?", r["id"])

    def set_road_shared(self, rid, user, shared):
        r = self.road(rid)
        if not r:
            raise ApiError(404, "No such road.")
        if r["user_id"] != user["id"] and user["role"] != "admin":
            raise ApiError(403, "Only the person who added a road, or an admin, can change it.")
        self.x("UPDATE roads SET shared=? WHERE id=?", 1 if shared else 0, r["id"])
