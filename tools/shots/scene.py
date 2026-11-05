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
bots = {n: srv.client(n, realname=n) for n in ["morpheus", "tank", "niobe", "switch", "apoc", "dozer", "mouse", "trinity"]}
m = bots["morpheus"]
for ch in ["#isekur", "#linux", "#retro", "#secret"]:
    m.send(f"JOIN {ch}")
time.sleep(0.3)
m.send(f"TOPIC #isekur :iSekur {C}13colorful{O} terminal IRC client | {B}v0.5{B} out now | https://github.com/gcanosa/iSekur")
for n, b in bots.items():
    if n != "morpheus": b.send("JOIN #isekur")
bots["tank"].send("JOIN #retro"); bots["trinity"].send("JOIN #secret")
time.sleep(0.3)
m.send("MODE #isekur +vv tank niobe")
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

def stop():
    typ("/exit -y"); time.sleep(0.8); tmux("kill-server"); time.sleep(0.3)

def start(theme, rows, web=False):
    d = "/tmp/iskshot"; os.makedirs(d, exist_ok=True)
    open(f"{d}/isekur.conf", "w").write(f"""[general]
nick = neo
altnick = neo_
realname = Thomas A.
theme = {theme}
colors = truecolor
show_guide = off
check_updates = off
log = off
keep_history = off
banner_anim = off
flood_interval_ms = 0
[server.sekurnet]
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
elif mode == "web":
    start("rose-pine", 22, web=True); chat()
    print("READY", flush=True)
    while os.path.exists(f"{HERE}/web.hold"): time.sleep(0.5); pump()
    stop()
srv.stop()
