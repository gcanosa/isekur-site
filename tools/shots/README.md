# Site screenshots

`./run.sh` replays a scripted chat on a scratch SekurIRCd (`irc.sekurnet.org`, network SekurNet, 8 bot nicks).
It drives iSekur in `tmux -L iskshot`, turns each `capture-pane -e` into a terminal-window page (`ans2html.py`)
and screenshots it at 2x (`render.js`). The webchat shots come from the same session (`web.js`, login `me`/`shot`),
and `og.html` is the social card. Results go into `../../img`.

Gotchas the scripts already handle: one ircd per theme (CHATHISTORY would replay earlier runs);
`flood_interval_ms = 0`; quit with `/exit -y` (killing tmux only detaches iSekur);
`TERM=xterm-256color` for italics; a short config dir (`/tmp/iskshot`) for the detach socket.
`scene.py docs` makes the docs section's `doc-*.png` (welcome, /list, whois, suggestions, tab finder, nick menu, /help, E2E, lock); `scene.py windows` adds the core windows: `doc-servers`, `doc-login` (the picker), `doc-logs`, `doc-logs-find`, `doc-keys`, `doc-bans` (it writes a few days of logs first, and sets the shown server to irc.sekurnet.org); `web.js` adds `doc-web-*` (login, E2E channel, Servers window).
The E2E lines are sealed in Python the way `src/e2e.cpp` does it (scrypt + AES-GCM, needs `cryptography`).
If a run dies midway, check `pgrep -fl 'isekur -c /tmp/iskshot'`: a detached iSekur left behind is reattached by the next run.
