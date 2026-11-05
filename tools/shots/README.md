# Homepage screenshots

`./run.sh` replays a scripted chat on a scratch SekurIRCd (`irc.sekurnet.org`, network SekurNet, 8 bot nicks).
It drives iSekur in `tmux -L iskshot`, turns each `capture-pane -e` into a terminal-window page (`ans2html.py`)
and screenshots it at 2x (`render.js`). The webchat shots come from the same session (`web.js`, login `me`/`shot`),
and `og.html` is the social card. Results go into `../../img`.

Gotchas the scripts already handle: one ircd per theme (CHATHISTORY would replay earlier runs);
`flood_interval_ms = 0`; quit with `/exit -y` (killing tmux only detaches iSekur);
`TERM=xterm-256color` for italics; a short config dir (`/tmp/iskshot`) for the detach socket.
The `doc-*.png` images in the docs section are not covered yet.
