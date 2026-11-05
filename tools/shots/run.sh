#!/bin/sh
# Regenerates the homepage screenshots into ../../img (see README.md).
# Needs: ../../../iSekur built, ../../../sekurircd built, /opt/homebrew/bin/tmux,
# a cached playwright-core (PWC) and an installed Chromium (CHROME).
set -e
cd "$(dirname "$0")"
: "${PWC:=$(ls -d ~/.npm/_npx/*/node_modules/playwright-core | tail -1)}"
: "${CHROME:=$(ls -d ~/Library/Caches/ms-playwright/chromium-*/chrome-mac-arm64/Google\ Chrome\ for\ Testing.app/Contents/MacOS/Google\ Chrome\ for\ Testing | tail -1)}"
export PWC CHROME
mkdir -p out
for t in mirc rose-pine ayu neon catppuccin-latte dracula; do  # one ircd each: CHATHISTORY would replay earlier runs
  python3 scene.py chat $t
  python3 ans2html.py chat-$t.ans $t > t.html && node render.js t.html out/chat-$t.png
done
python3 scene.py ui
python3 ans2html.py theme-picker.ans dayfox > t.html && node render.js t.html out/theme-picker.png
python3 ans2html.py settings.ans catppuccin-mocha > t.html && node render.js t.html out/settings.png
touch web.hold
python3 scene.py web > web.out 2>&1 &
while ! grep -q READY web.out 2>/dev/null; do sleep 1; done
node web.js
rm -f web.hold; wait
node og.js
cp out/*.png ../../img/
rm -rf out *.ans t.html web.out raw.log /tmp/iskshot
