// Accounts UI: first-run setup, sign-in, invite/reset links, settings (account, users, roads, server).
// Loaded after the main script, which defines D(), SP(), units, loadData(), DATA, map ... (shared global scope).
let STATE = null, PREFS = {};
async function api(path, body) {
  const opt = body === undefined ? {cache: "no-store"} : {method: "POST", headers: {"Content-Type": "application/json", "X-Requested-With": "switchback"}, body: JSON.stringify(body)};
  const r = await fetch(path, opt); let j = {}; try { j = await r.json(); } catch {}
  if (r.status === 401 && STATE && STATE.user && STATE.auth) { location.reload(); }
  if (!r.ok) { const e = new Error(j.error || r.statusText); e.status = r.status; throw e; }
  return j;
}
const $a = id => document.getElementById(id);

// Password fields get a Show/Hide button (handy when a password has to be typed from another device) and a warning
// when the value starts or ends with a space, a common result of copy and paste.
const pwInput = (attrs = "") => `<span class="pw"><input type="password" autocapitalize="off" autocorrect="off" spellcheck="false" ${attrs}><button type="button" class="eye" aria-label="Show password">Show</button></span><span class="pwwarn"></span>`;
document.addEventListener("click", e => {
  const b = e.target.closest(".eye"); if (!b) return;
  const i = b.parentElement.querySelector("input"), show = i.type === "password"; i.type = show ? "text" : "password"; b.textContent = show ? "Hide" : "Show"; b.setAttribute("aria-label", show ? "Hide password" : "Show password");
});
document.addEventListener("input", e => {
  const i = e.target; if (!i.closest || !i.closest(".pw")) return;
  const w = i.closest(".pw").nextElementSibling; if (w && w.classList.contains("pwwarn")) w.textContent = i.value && i.value !== i.value.trim() ? "Note: there is a space at the start or end of this password." : "";
});

// ---- preferences live on the account (units, home); old browser-only values are migrated on first sign-in
async function savePrefs() { try { await api("/api/prefs", {prefs: PREFS}); } catch {} }
function migrateLocalPrefs() {
  let changed = false;
  try {
    const u = localStorage.getItem("switchback.units"), h = JSON.parse(localStorage.getItem("switchback.home") || "null");
    if (!PREFS.units && u) { PREFS.units = u; changed = true; }
    if (!PREFS.home && h) { PREFS.home = h; changed = true; }
  } catch {}
  if (changed) savePrefs();
}

// ---- full-screen cards for setup / sign-in / invite / reset
function authCard(title, intro, fields, button, onSubmit, footer = "") {
  const el = $a("auth"); el.style.display = "flex";
  el.innerHTML = `<form class="authcard"><img src="logo.png" alt="Switchback" style="width:220px;max-width:70%;align-self:center">
    <h2>${esc(title)}</h2><p class="mute">${intro}</p>
    ${fields.map(f => f.type === "password"
      ? `<label>${esc(f.label)}${pwInput(`name="${f.name}" autocomplete="${f.ac || "off"}" required`)}</label>`
      : `<label>${esc(f.label)}<input name="${f.name}" type="${f.type || "text"}" autocapitalize="off" autocorrect="off" spellcheck="false" autocomplete="${f.ac || "off"}" ${f.value ? `value="${esc(f.value)}"` : ""} ${f.ro ? "readonly" : ""} required></label>`).join("")}
    <div class="err" id="autherr"></div><button class="primary" type="submit">${esc(button)}</button>${footer}</form>`;
  const form = el.querySelector("form"); form.querySelector("input:not([readonly])")?.focus();
  form.onsubmit = async e => {
    e.preventDefault(); const v = Object.fromEntries([...form.elements].filter(x => x.name).map(x => [x.name, x.value])); $a("autherr").textContent = "";
    try { await onSubmit(v); } catch (err) { $a("autherr").textContent = err.message; }
  };
}
const pwHint = "At least 10 characters.";

async function boot() {
  STATE = await api("/api/state");
  const q = new URLSearchParams(location.search);
  const clean = () => history.replaceState(null, "", location.pathname);
  if (STATE.setup) {
    return authCard("Welcome to Switchback", "Create the admin account for this server. The setup code is printed in the server log when it first starts.",
      [{name: "code", label: "Setup code"}, {name: "username", label: "Admin username", ac: "username"}, {name: "password", label: "Password (" + pwHint + ")", type: "password", ac: "new-password"}],
      "Create admin account", async v => { await api("/api/setup", v); location.reload(); });
  }
  if (q.get("invite")) {
    const tok = q.get("invite"); let role = "rider";
    try { role = (await api("/api/invite/" + encodeURIComponent(tok))).role; }
    catch { return authCard("Invite not valid", "This invite link is invalid, expired or already used. Ask the person who invited you for a new one.", [], "Go to sign in", () => { clean(); location.reload(); }); }
    return authCard("You're invited", `Choose a username and password to join as ${esc(role)}.`,
      [{name: "username", label: "Username", ac: "username"}, {name: "password", label: "Password (" + pwHint + ")", type: "password", ac: "new-password"}],
      "Create my account", async v => { await api("/api/accept", {token: tok, ...v}); clean(); location.reload(); });
  }
  if (q.get("reset")) {
    const tok = q.get("reset"); let name = "";
    try { name = (await api("/api/reset/" + encodeURIComponent(tok))).username; }
    catch { return authCard("Reset link not valid", "This link is invalid, expired or already used. Ask an admin for a new one.", [], "Go to sign in", () => { clean(); location.reload(); }); }
    return authCard("Choose a new password", `For ${esc(name)}.`, [{name: "password", label: "New password (" + pwHint + ")", type: "password", ac: "new-password"}],
      "Set password and sign in", async v => { await api("/api/reset", {token: tok, ...v}); clean(); location.reload(); });
  }
  if (!STATE.user) {
    return authCard(STATE.settings.server_name || "Sign in", "Sign in to plan rides.", [{name: "username", label: "Username", ac: "username"}, {name: "password", label: "Password", type: "password", ac: "current-password"}],
      "Sign in", async v => { await api("/api/login", v); location.reload(); }, `<p class="mute">No account? Ask an admin for an invite link.</p>`);
  }
  $a("auth").style.display = "none";
  PREFS = STATE.user.prefs || {}; migrateLocalPrefs();
  if (PREFS.units && PREFS.units !== units) { units = PREFS.units; try { unitBtn(); } catch {} }
  $a("userbtn").textContent = "⚙ " + STATE.user.username; $a("userbtn").style.display = "";
  loadData(true);
}

// ---- settings
const isAdmin = () => STATE.user.role === "admin";
const fmtDate = t => new Date(t * 1000).toISOString().slice(0, 10);
function copyBox(text) { return `<div class="copy"><input readonly value="${esc(text)}" onclick="this.select()"><button onclick="navigator.clipboard&&navigator.clipboard.writeText(this.previousElementSibling.value);this.textContent='Copied'">Copy</button></div>`; }

async function openSettings(tab) {
  const el = $a("settings"); el.style.display = "flex";
  const tabs = [["account", "Account"], ["roads", "My roads"]];
  if (isAdmin() && STATE.auth) tabs.push(["users", "Users"]);
  if (isAdmin() && STATE.auth) tabs.push(["server", "Server"]);
  tab = tab || "account";
  el.innerHTML = `<div class="setcard"><div class="settop"><b>Settings</b><button id="setclose">✕</button></div>
    <div class="settabs">${tabs.map(([k, t]) => `<button data-tab="${k}" class="${k === tab ? "on" : ""}">${t}</button>`).join("")}</div><div id="setbody"></div></div>`;
  $a("setclose").onclick = () => el.style.display = "none";
  el.onclick = e => { if (e.target === el) el.style.display = "none"; };
  el.querySelectorAll("[data-tab]").forEach(b => b.onclick = () => openSettings(b.dataset.tab));
  const body = $a("setbody");
  if (tab === "account") return settingsAccount(body);
  if (tab === "roads") return settingsRoads(body);
  if (tab === "users") return settingsUsers(body);
  if (tab === "server") return settingsServer(body);
}

function note(el, msg, bad) { el.textContent = msg; el.className = bad ? "err" : "ok"; }

function settingsAccount(body) {
  const home = PREFS.home;
  body.innerHTML = `<h3>${esc(STATE.user.username)} <span class="mute">${esc(STATE.user.role)}</span></h3>
    <div class="grp"><b>Units</b><label><input type="radio" name="u" value="mi" ${units === "mi" ? "checked" : ""}> Miles</label><label><input type="radio" name="u" value="km" ${units === "km" ? "checked" : ""}> Kilometres</label></div>
    <div class="grp"><b>Home</b><div class="mute">${home ? esc(home.label || "saved") : "Not set. Search an address on the main screen and press “Save as home”."}</div>${home ? `<button id="clearhome">Clear home</button>` : ""}</div>
    ${STATE.auth ? `<div class="grp"><b>Change password</b>Current password${pwInput(`id="pw0" autocomplete="current-password"`)}New password (${pwHint})${pwInput(`id="pw1" autocomplete="new-password"`)}<button id="pwgo">Change password</button><div id="pwmsg"></div></div>
    <div class="grp"><button id="signout">Sign out</button></div>` : `<p class="mute">Single-user mode: no sign-in is needed on this computer.</p>`}`;
  body.querySelectorAll("[name=u]").forEach(r => r.onchange = () => { units = r.value; PREFS.units = units; savePrefs(); try { unitBtn(); renderList(); renderRide(); if (route) { showTotals(route); showMsg(route); } } catch {} });
  $a("clearhome")?.addEventListener("click", () => { delete PREFS.home; savePrefs(); try { $a("gohome").disabled = true; if (homeMarker) { map.removeLayer(homeMarker); homeMarker = null; } } catch {} settingsAccount(body); });
  $a("pwgo")?.addEventListener("click", async () => {
    try { await api("/api/password", {old: $a("pw0").value, new: $a("pw1").value}); note($a("pwmsg"), "Password changed. Other devices were signed out."); $a("pw0").value = $a("pw1").value = ""; }
    catch (e) { note($a("pwmsg"), e.message, true); }
  });
  $a("signout")?.addEventListener("click", async () => { await api("/api/logout", {}); location.reload(); });
}

async function settingsRoads(body) {
  const mine = DATA.candidates.filter(c => c.manual && (c.mine || isAdmin()));
  let rows = mine.map(c => ({id: c.id, name: c.name, shared: c.shared, who: c.added_by, on: c.added_on, mine: c.mine}));
  if (isAdmin() && STATE.auth) {      // admins also see other people's private roads, so nothing is hidden from moderation
    try { const u = await api("/api/users"); rows = u.roads.map(r => ({id: 100000 + r.id, name: r.name, shared: !!r.shared, who: r.owner || "a former user", on: fmtDate(r.created), mine: false})); } catch {}
  }
  body.innerHTML = `<p class="mute">Roads highlighted by hand. ${STATE.auth ? "A shared road is visible to everyone on this server, with the name of who added it." : ""}</p>` +
    (rows.length ? `<table class="tbl"><tr><th>Road</th><th>Added</th>${STATE.auth ? "<th>Shared</th>" : ""}<th></th></tr>${rows.map(r => `<tr><td>${esc(r.name)}</td><td>${esc(r.who)}<br><span class="mute">${esc(r.on)}</span></td>${STATE.auth ? `<td><input type="checkbox" data-share="${r.id}" ${r.shared ? "checked" : ""}></td>` : ""}<td><button data-del="${r.id}">Remove</button></td></tr>`).join("")}</table>` : `<p>You haven't added any roads yet. Use “＋ Add a road” on the main screen.</p>`);
  body.querySelectorAll("[data-share]").forEach(c => c.onchange = async () => { await api("/api/custom/share", {id: +c.dataset.share, shared: c.checked}); await loadData(false); });
  body.querySelectorAll("[data-del]").forEach(b => b.onclick = async () => { if (confirm("Remove this road for good?")) { await api("/api/custom/delete", {id: +b.dataset.del}); await loadData(false); settingsRoads(body); } });
}

async function settingsUsers(body) {
  const d = await api("/api/users");
  const me = STATE.user.id;
  body.innerHTML = `<div class="grp"><b>Invite someone</b><div class="row"><select id="invrole"><option value="rider">Rider</option><option value="admin">Admin</option></select><input id="invnote" placeholder="Who is this for? (optional)"><button id="invgo" class="primary">Create invite link</button></div><div id="invout"></div>
      <div class="mute">Links work once and expire in 7 days. Send it by message or email; the person picks their own username and password.</div></div>
    ${d.invites.length ? `<div class="grp"><b>Pending invites</b>${d.invites.map(i => `<div class="mute">${esc(i.role)} · ${esc(i.note || "no note")} · by ${esc(i.created_by || "?")} · expires ${esc(fmtDate(i.expires))}</div>`).join("")}</div>` : ""}
    <div class="grp"><b>Create an account with a password</b><div class="row"><input id="nuser" placeholder="Username"><input id="npw" type="text" placeholder="Temporary password"><select id="nrole"><option value="rider">Rider</option><option value="admin">Admin</option></select><button id="ngo">Create</button></div><div id="nmsg"></div></div>
    <table class="tbl"><tr><th>User</th><th>Role</th><th></th></tr>${d.users.map(u => `<tr${u.disabled ? ' class="off"' : ""}><td>${esc(u.username)}${u.id === me ? " (you)" : ""}<br><span class="mute">joined ${esc(fmtDate(u.created))}${u.disabled ? " · disabled" : ""}</span></td>
      <td><select data-role="${u.id}"><option ${u.role === "rider" ? "selected" : ""} value="rider">Rider</option><option ${u.role === "admin" ? "selected" : ""} value="admin">Admin</option></select></td>
      <td class="acts"><button data-pw="${u.id}">Set password</button><button data-link="${u.id}">Reset link</button><button data-dis="${u.id}" data-to="${u.disabled ? 0 : 1}">${u.disabled ? "Enable" : "Disable"}</button><button data-rm="${u.id}">Delete</button></td></tr>`).join("")}</table><div id="umsg"></div>`;
  const msg = (t, bad) => note($a("umsg"), t, bad), run = async (fn) => { try { await fn(); } catch (e) { msg(e.message, true); } };
  $a("invgo").onclick = () => run(async () => {
    const j = await api("/api/invite", {role: $a("invrole").value, note: $a("invnote").value});
    $a("invout").innerHTML = copyBox(`${location.origin}${location.pathname}?invite=${j.token}`); });
  $a("ngo").onclick = () => run(async () => { await api("/api/users/create", {username: $a("nuser").value, password: $a("npw").value, role: $a("nrole").value}); settingsUsers(body); });
  body.querySelectorAll("[data-role]").forEach(s => s.onchange = () => run(async () => { await api("/api/users/role", {id: +s.dataset.role, role: s.value}); msg("Role updated."); }).then(() => settingsUsers(body)));
  body.querySelectorAll("[data-pw]").forEach(b => b.onclick = () => run(async () => { const p = prompt("New password for this user (at least 10 characters). They will be signed out everywhere."); if (p) { await api("/api/users/password", {id: +b.dataset.pw, password: p}); msg("Password set."); } }));
  body.querySelectorAll("[data-link]").forEach(b => b.onclick = () => run(async () => { const j = await api("/api/users/reset-link", {id: +b.dataset.link}); $a("umsg").className = ""; $a("umsg").innerHTML = "Reset link (valid 24 hours, one use):" + copyBox(`${location.origin}${location.pathname}?reset=${j.token}`); }));
  body.querySelectorAll("[data-dis]").forEach(b => b.onclick = () => run(async () => { await api("/api/users/disable", {id: +b.dataset.dis, disabled: b.dataset.to === "1"}); settingsUsers(body); }));
  body.querySelectorAll("[data-rm]").forEach(b => b.onclick = () => run(async () => { if (confirm("Delete this user? Their private roads are deleted, shared roads stay.")) { await api("/api/users/delete", {id: +b.dataset.rm}); settingsUsers(body); } }));
}

function settingsServer(body) {
  body.innerHTML = `<div class="grp"><b>Hand-added roads</b><label><input type="checkbox" id="shdef" ${STATE.settings.share_roads_default ? "checked" : ""}> New roads are visible to everyone by default</label>
    <div class="mute">Each person can still make their own roads private or shared from the road's card. Shared roads show “added by name on date”.</div></div>
    <div class="grp"><b>Server name</b><input id="sname" value="${esc(STATE.settings.server_name)}" maxlength="40"><button id="snamego">Save</button><div id="smsg"></div></div>`;
  $a("shdef").onchange = async e => { await api("/api/settings", {settings: {share_roads_default: e.target.checked}}); STATE.settings.share_roads_default = e.target.checked; };
  $a("snamego").onclick = async () => { try { await api("/api/settings", {settings: {server_name: $a("sname").value}}); STATE.settings.server_name = $a("sname").value; note($a("smsg"), "Saved."); } catch (e) { note($a("smsg"), e.message, true); } };
}

$a("userbtn").onclick = () => openSettings();
boot();
