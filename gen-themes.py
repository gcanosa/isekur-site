#!/usr/bin/env python3
# Regenerates themes.json from iSekur's themes: python3 gen-themes.py ../iSekur/themes > themes.json
import glob, os, json, sys
keys = "default topic tabbar tab_active tab_server tab_home tab_msg tab_hilight tab_data status status_hi timestamp separator nicklist nicklist_title nicklist_op nicklist_voice msg_self marker hilight join notice action info input_prompt".split()
col = lambda x: x if x.startswith('#') else None
out = {}
for f in sorted(glob.glob(os.path.join(sys.argv[1], '*.theme'))):
    sec, c, pal = None, {}, []
    for l in open(f):
        l = l.strip()
        if not l or l.startswith('#'): continue
        l = l.split(';')[0].strip()
        if l.startswith('['): sec = l; continue
        k, _, v = l.partition('='); k = k.strip(); v = v.split()
        if sec == '[colors]' and k in keys: c[k] = v
        if sec == '[nicks]' and k == 'palette': pal = v
    d = c['default']
    bg = (col(d[1]) if len(d) > 1 else None) or '#16161e'
    fg = col(d[0]) or '#c0caf5'
    t = {k: [col(v[0]) or fg] + ([col(v[1]) or bg] if len(v) > 1 and v[1] != 'default' else []) + (['b'] if 'bold' in v else []) for k, v in c.items()}
    t.update(bg=bg, fg=fg, pal=pal)
    out[os.path.basename(f)[:-6]] = t
print(json.dumps(out, separators=(',', ':')))
