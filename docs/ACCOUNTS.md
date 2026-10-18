# Accounts

Two modes:
- **Single user** (`SWITCHBACK_AUTH=off`): no sign-in; everyone is the owner. For a desktop install or localhost.
- **Multi-user** (default): local accounts stored in SQLite (`$SWITCHBACK_DATA/switchback.db`, default `data_private/`).

## First run
The server prints a one-time **setup code** to its log when it starts with no users. Open the app, enter the code and choose the admin username and password. Without the code nobody else can claim a fresh server.

## People
- Admins create **invite links** (single use, 7 days) in Settings, Users. The invitee chooses their own username and password.
- Admins can also create an account with a temporary password, set a password for anyone, issue a **password reset link** (24 hours, single use), change roles, disable or delete users. The last admin cannot be demoted, disabled or deleted.
- Locked out? `python app/server.py reset-password USERNAME` sets a random password and prints it.

## Hand-added roads
Visible to everyone by default, with "added by name on date". Admins change the default in Settings, Server; each person can make their own roads private or shared from the road's card. Admins can moderate every road.

## Security notes
Passwords: scrypt. Sessions and invite/reset tokens: random, stored only as SHA-256 hashes. Cookie: HttpOnly, SameSite=Lax, Secure behind HTTPS (`X-Forwarded-Proto` or `SWITCHBACK_SECURE_COOKIES=1`). Every write needs an `X-Requested-With` header. Login locks out for 15 minutes after 5 failures. Only `/static/` is served publicly; map data needs a session. Put HTTPS in front (a reverse proxy or Tailscale) before exposing it beyond your LAN.
