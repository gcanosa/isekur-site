# Drives SekurIRCd + bots + iSekur in tmux; writes ANSI captures for the site screenshots.
import sys, os, time, subprocess, json
CODE = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, os.environ.get("SEKURIRCD", CODE + "/sekurircd") + "/tests/itest")
from harness import Server, Client
HERE = os.path.dirname(os.path.abspath(__file__))
ISK = os.environ.get("ISEKUR", CODE + "/iSekur")
TMUX = ["/opt/homebrew/bin/tmux", "-L", "iskshot"]
C = "\x03"; B = "\x02"; O = "\x0f"
HASH = "pbkdf2$sha256$200000$rN4UvnbV7WAxmxQq/JgxkA==$vV4biqDvfNxWzUO6h0CYLACPNERvdWayUApM1d2zBOM="

srv = Server(name="irc.sekurnet.org", cfg={"server": {"network": "SekurNet"}}).start()
open(f"{HERE}/pids", "w").write(str(srv.proc.pid))
bots = {n: srv.client(n, realname=n) for n in ["morpheus", "tank", "niobe", "switch", "apoc", "dozer", "mouse", "trinity", "cypher"]}
m = bots["morpheus"]
for ch in ["#isekur", "#linux", "#retro", "#secret"]:
    m.send(f"JOIN {ch}")
time.sleep(0.3)
m.send(f"TOPIC #isekur :iSekur {C}13colorful{O} terminal IRC client | {B}v0.5{B} out now | https://github.com/gcanosa/iSekur")
for n, b in bots.items():
    if n not in ("morpheus", "cypher"): b.send("JOIN #isekur")
bots["tank"].send("JOIN #retro"); bots["trinity"].send("JOIN #secret")
time.sleep(0.3)
m.send("MODE #isekur +vv tank niobe"); m.send("TOPIC #secret :end-to-end encrypted with /e2e"); m.send("PART #secret")
import socket, threading
PX = socket.socket(); PX.bind(("127.0.0.1", 0)); PX.listen(5); PXPORT = PX.getsockname()[1]
def _pipe(a, b, tag):
    f = open(f"{HERE}/raw.log", "a")
    while True:
        try: d = a.recv(65536)
        except OSError: d = b""
        if not d: break
        for l in d.decode(errors="replace").splitlines(): f.write(tag + l + "\n")
        f.flush(); b.sendall(d)
    a.close(); b.close()
def _accept():
    while True:
        c, _ = PX.accept(); u = socket.create_connection(("127.0.0.1", srv.port))
        threading.Thread(target=_pipe, args=(c, u, "C> "), daemon=True).start()
        threading.Thread(target=_pipe, args=(u, c, "S> "), daemon=True).start()
threading.Thread(target=_accept, daemon=True).start()
def pump():
    for b in bots.values(): b.drain(0.01)

def tmux(*a, **kw): return subprocess.run(TMUX + list(a), capture_output=True, text=True, **kw).stdout
def keys(*k): tmux("send-keys", "-t", "s", *k); time.sleep(0.25)
def typ(line): tmux("send-keys", "-t", "s", "-l", line); keys("Enter"); time.sleep(0.2)
def cap(name):
    time.sleep(0.6)
    open(f"{HERE}/{name}.ans", "w").write(tmux("capture-pane", "-t", "s", "-p", "-e", "-N"))
def say(n, text, ch="#isekur"):
    bots[n].send(f"PRIVMSG {ch} :{text}"); time.sleep(0.15)
def act(n, text): say(n, f"\x01ACTION {text}\x01")

import base64, hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
def seal(pw, text, ch="#secret"):  # what /e2e #secret sends (src/e2e.cpp)
    k = hashlib.scrypt(pw.encode(), salt=b"isekur-chan:" + ch.encode(), n=1 << 15, r=8, p=1, maxmem=128 << 20, dklen=32)
    nonce = os.urandom(12)
    return "+iSE " + base64.b64encode(nonce + AESGCM(k).encrypt(nonce, text.encode(), ch.encode())).decode()
def secret():
    keys("M-6"); typ("/e2e #secret"); time.sleep(0.5); typ("zion"); time.sleep(1)
    say("trinity", seal("zion", "the docks at 0600, bring the keys"), "#secret"); pump()
    typ("copy that. nobody else on the server can read this")
    bots["cypher"].send("JOIN #secret"); time.sleep(0.2)
    say("cypher", seal("mouse", "let me in"), "#secret")
    say("trinity", seal("zion", "cypher keeps trying, wrong password, all he gets is noise"), "#secret")
    bots["cypher"].send("PART #secret"); time.sleep(0.2)
    typ("and the key for an autojoin channel is saved, so no password after a restart")
    say("trinity", seal("zion", "see you there"), "#secret"); time.sleep(0.4); pump()
def click_nick(nick, button=2):  # SGR mouse report on the nick in the user list
    rows = tmux("capture-pane", "-t", "s", "-p").splitlines()
    for y, r in enumerate(rows):
        x = r.find(nick, 70)
        if x >= 0: break
    tmux("send-keys", "-t", "s", "-l", f"\x1b[<{button};{x + 2};{y + 1}M\x1b[<{button};{x + 2};{y + 1}m"); time.sleep(0.4)

def seed_logs():  # the days before today in the log folder, so /logs has a tree, days and something to search
    d = "/tmp/iskshot/logs/sekurnet"; os.makedirs(d, exist_ok=True)
    talk = [("morpheus", "morning all, coffee is on"), ("tank", "pushed the webchat fix for the phone layout"),
            ("niobe", "does the webchat keep the tabs in sync with the terminal?"), ("neo", "yes, same session, it is the same iSekur"),
            ("switch", "CI is green on linux, macos and freebsd"), ("apoc", "who is on the release notes today?"),
            ("morpheus", "I am, after lunch"), ("dozer", "the new themes look great in the webchat too"),
            ("neo", "/grep finds anything in the scrollback, /logs finds it on disk"), ("mouse", "nice, I will try the log browser tonight"),
            ("trinity", "see you all tomorrow")]
    t0 = time.time()
    for back, name, who in [(1, "#isekur", 0), (2, "#isekur", 1), (3, "#isekur", 2), (5, "#isekur", 3), (8, "#isekur", 4), (13, "#isekur", 5),
                            (1, "#linux", 0), (4, "#linux", 2), (2, "#retro", 1), (1, "morpheus", 0), (6, "morpheus", 2)]:
        day = time.strftime("%Y-%m-%d", time.localtime(t0 - back * 86400))
        rows = [f"--- Log opened {day} 08:55:10"]
        ts = 9 * 3600 + 60 * (7 * who % 40)
        for i, (n, text) in enumerate(talk[who % 3: who % 3 + 8]):
            ts += 130 + 71 * i
            hh, mm, ss = ts // 3600, ts % 3600 // 60, ts % 60
            if name.startswith("#") and i == 2:
                rows.append(f"{day} {hh:02}:{mm:02}:{ss:02} -!- {n} (~{n}@127.0.0.1) has joined {name}")
            rows.append(f"{day} {hh:02}:{mm:02}:{ss + 1 if ss < 59 else ss:02} <{n}> {text}")
        if name.startswith("#"): rows.append(f"{day} 17:20:44 -!- apoc (~apoc@127.0.0.1) has quit (Ping timeout)")
        open(f"{d}/{name}.{day}.log", "w").write("\n".join(rows) + "\n")

def stop():
    typ("/exit -y"); time.sleep(0.8); tmux("kill-server"); time.sleep(0.3)

def start(theme, rows, web=False, extra="", logon="off"):
    d = "/tmp/iskshot"; os.makedirs(d, exist_ok=True)
    open(f"{d}/isekur.conf", "w").write(f"""[general]
nick = neo
altnick = neo_
realname = Thomas A.
theme = {theme}
colors = truecolor
show_guide = off
check_updates = off
log = {logon}
keep_history = off
banner_anim = off
flood_interval_ms = 0
{extra}[server.sekurnet]
host = 127.0.0.1
port = {PXPORT}
tls = false
autojoin = #isekur,#linux,#retro,#secret
[web]
autostart = {'on' if web else 'off'}
port = 18443
user = me
password_hash = {HASH}
""")
    tmux("new-session", "-d", "-s", "s", "-x", "100", "-y", str(rows),
         f"cd {ISK} && TERM=xterm-256color COLORTERM=truecolor ./isekur -c {d}/isekur.conf")
    for _ in range(60):
        time.sleep(0.25); pump()
        if "#secret" in tmux("capture-pane", "-t", "s", "-p"): break
    time.sleep(1)

def chat():
    keys("M-3"); time.sleep(0.5); keys("M-4"); time.sleep(0.3)
    say("morpheus", "morning all, coffee is on")
    say("tank", "just pushed the read marker and daily log rotation")
    say("switch", f"{C}09CI{O} is green on linux, macos, freebsd {B}and{B} cygwin")
    act("dozer", "tries the webchat from his phone")
    say("niobe", "the webchat even keeps the tabs in sync, nice")
    say("morpheus", f"neo: the {C}13neon{O} theme looks great on your screen?")
    say("apoc", f"{C}04r{C}07a{C}08i{C}09n{C}12b{C}02o{C}06w{O} mIRC colors render in true color too")
    say("tank", "anyone still running a 486 here?", "#retro")
    time.sleep(0.4); keys("M-3"); pump()
    typ("yes! and /grep finds anything in the scrollback")
    say("mouse", "release notes: https://github.com/gcanosa/iSekur/releases/latest")
    typ("/me detaches with Alt+D and goes for lunch")
    say("trinity", "see you in #secret later")
    time.sleep(0.5); pump()

mode = sys.argv[1]
if mode == "chat":
    for th in sys.argv[2:]:
        start(th, 22); chat(); cap(f"chat-{th}"); stop()
elif mode == "ui":
    start("catppuccin-mocha", 26); chat()
    typ("/theme"); time.sleep(0.5)
    for _ in range(3): keys("Down")
    cap("theme-picker"); keys("Escape"); time.sleep(0.5)
    typ("/set"); time.sleep(0.5)
    keys("Down"); keys("Down"); keys("Down")
    cap("settings"); keys("q"); stop()
elif mode == "docs":
    start("tokyonight", 24); chat()
    keys("M-1"); cap("doc-welcome")
    tmux("resize-window", "-t", "s", "-y", "16"); time.sleep(0.5)  # these two sit side by side on the page: a short window, no empty chat above the table
    keys("M-2"); typ("/list"); time.sleep(1); cap("doc-list"); keys("Escape")
    keys("M-3"); typ("/whois morpheus"); time.sleep(0.6); cap("doc-whois")
    tmux("resize-window", "-t", "s", "-y", "24"); time.sleep(0.5)
    tmux("send-keys", "-t", "s", "-l", "/se"); cap("doc-suggest"); keys("C-u"); keys("Escape")
    keys("C-g"); tmux("send-keys", "-t", "s", "-l", "li"); cap("doc-find"); keys("Escape"); keys("Escape")
    click_nick("morpheus"); cap("doc-nickmenu"); keys("Escape")
    typ("/help server"); cap("doc-help-server")
    secret(); cap("doc-e2e")
    typ("/shell"); time.sleep(0.5); typ("neo"); tmux("send-keys", "-t", "s", "-l", "secret12"); cap("doc-shell-login"); keys("Escape")
    keys("M-3"); typ("/lock"); time.sleep(0.4); typ("shot"); time.sleep(0.6); typ("shot"); time.sleep(1); cap("doc-lock"); typ("shot"); time.sleep(0.5)
    typ("/exit -y"); time.sleep(0.5); typ("shot"); time.sleep(0.8); tmux("kill-server")
elif mode == "windows":  # the core windows: /servers (and its login picker), /logs, /keys, /bans
    seed_logs()
    start("tokyonight", 26, logon="on"); chat()
    for mask in ("troll!*@*", "*!*@spam.example.net", "bot*!*@*"):
        m.send(f"MODE #isekur +b {mask}"); time.sleep(0.2)
    pump(); keys("M-3"); typ("/bans"); time.sleep(1); cap("doc-bans"); keys("Escape")
    keys("F1"); time.sleep(0.8); cap("doc-keys"); keys("Escape")
    for k, v in (("host", "irc.sekurnet.org"), ("port", "6697"), ("tls", "true")): typ(f"/set server.sekurnet.{k} {v}")  # what a reader has, not the scratch proxy (they apply at the next connect)
    typ("/save"); keys("M-3"); typ("/servers"); time.sleep(0.8); cap("doc-servers"); keys("q")
    keys("M-2"); typ("/clear"); tmux("resize-window", "-t", "s", "-y", "12"); time.sleep(0.5)  # the login picker (l) opens over the server's tab: a short window around it
    typ("/servers"); time.sleep(0.6); keys("l"); time.sleep(0.6); cap("doc-login"); keys("Escape"); keys("Escape")
    tmux("resize-window", "-t", "s", "-y", "26"); time.sleep(0.5)
    keys("M-3"); typ("/logs"); time.sleep(1.2); cap("doc-logs")
    keys("Tab"); keys("Up"); keys("/"); tmux("send-keys", "-t", "s", "-l", "webchat"); time.sleep(0.4); keys("Enter"); time.sleep(1.2); cap("doc-logs-find"); keys("Escape")
    stop()
elif mode == "layout":  # tab_bar_position = left: the tabs as a tree down the side
    start("tokyonight", 24, extra="tab_bar_position = left\n"); chat(); cap("doc-layout"); stop()
elif mode == "web":
    start("rose-pine", 22, web=True); secret(); chat()
    print("READY", flush=True)
    while os.path.exists(f"{HERE}/web.hold"): time.sleep(0.5); pump()
    stop()
srv.stop()
