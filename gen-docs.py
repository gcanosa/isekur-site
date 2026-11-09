#!/usr/bin/env python3
# Regenerates docs.json from iSekur's sources, so the docs page says what the app says:
#   python3 gen-docs.py ../iSekur > docs.json
# commands: src/help.cpp CMDS (what /help shows), guide: src/help.cpp GUIDE (/guide),
# settings: iSekur.conf.example (every key with its comment).
import html, json, os, re, sys

root = sys.argv[1]
src = open(os.path.join(root, "src/help.cpp"), encoding="utf-8").read()

# ---- a tiny C reader: string literals, #define macros, braces -----------------
TOK = re.compile(r'"((?:[^"\\]|\\.)*)"|([A-Za-z_]\w*)|([{}(),])|//[^\n]*|/\*.*?\*/|\s+|.', re.S)


def cstr(body):  # one C literal; each is decoded alone, so "\x03" "08" stays two pieces
    return re.sub(r'\\(x[0-9a-fA-F]+|[0-7]{1,3}|.)', lambda m: (
        chr(int(m.group(1)[1:], 16)) if m.group(1)[0] == 'x' else
        chr(int(m.group(1), 8)) if m.group(1)[0].isdigit() else
        {'n': '\n', 't': '\t', '\\': '\\', '"': '"', "'": "'"}.get(m.group(1), m.group(1))), body)


def tokens(text):
    out = []
    for m in TOK.finditer(text):
        if m.group(1) is not None: out.append(('s', cstr(m.group(1))))
        elif m.group(2): out.append(('id', m.group(2)))
        elif m.group(3): out.append(('p', m.group(3)))
    return out


macros = {}  # name -> (params or None, tokens)
for m in re.finditer(r'^#define (\w+)(\(([^)]*)\))?[ \t]+(.*)$', src, re.M):
    body = re.sub(r'//.*', '', m.group(4))
    macros[m.group(1)] = ([p.strip() for p in m.group(3).split(',')] if m.group(2) else None, tokens(body))


def expand(toks):
    out, i = [], 0
    while i < len(toks):
        t = toks[i]
        if t[0] == 'id' and t[1] in macros:
            params, body = macros[t[1]]
            if params is None:
                out += expand(body); i += 1; continue
            # function-like: collect the arguments
            i += 2; depth, args, cur = 0, [], []
            while True:
                x = toks[i]
                if x == ('p', '(') : depth += 1
                if x == ('p', ')'):
                    if depth == 0: break
                    depth -= 1
                if x == ('p', ',') and depth == 0: args.append(cur); cur = []
                else: cur.append(x)
                i += 1
            args.append(cur); i += 1
            sub = dict(zip(params, args))
            out += expand([y for b in body for y in (sub[b[1]] if b[0] == 'id' and b[1] in sub else [b])])
            continue
        out.append(t); i += 1
    return out


def parse(toks, i=0):  # {...} -> list, adjacent strings -> one string
    assert toks[i] == ('p', '{')
    i += 1; items, cur = [], None
    while toks[i] != ('p', '}'):
        t = toks[i]
        if t == ('p', '{'):
            cur, i = parse(toks, i); continue
        if t[0] == 's': cur = (cur or '') + t[1]
        elif t == ('p', ','): items.append(cur); cur = None
        i += 1
    if cur is not None: items.append(cur)
    return items, i + 1


def table(name):
    start = src.index(name)
    toks = expand(tokens(src[src.index('=', start) + 1:]))
    return parse(toks)[0]

# ---- mIRC formatting -> HTML ---------------------------------------------------
MIRC = ["#ffffff", "#000000", "#00007f", "#009300", "#ff0000", "#7f0000", "#9c009c", "#fc7f00",
        "#ffff00", "#00fc00", "#009393", "#00ffff", "#0000fc", "#ff00ff", "#7f7f7f", "#d2d2d2"]


def mirc_html(s):
    out, st = [], dict(b=False, i=False, u=False, fg=None, bg=None)
    def span(text):
        css = ''
        if st['fg'] is not None: css += f'color:{MIRC[st["fg"] % 16]};'
        if st['bg'] is not None: css += f'background:{MIRC[st["bg"] % 16]};'
        if st['b']: css += 'font-weight:700;'
        if st['i']: css += 'font-style:italic;'
        if st['u']: css += 'text-decoration:underline;'
        out.append(f'<span style="{css}">{html.escape(text)}</span>' if css else html.escape(text))
    for m in re.finditer(r'\x03(?:(\d{1,2})(?:,(\d{1,2}))?)?|([\x02\x0f\x1d\x1f\x16])|([^\x02\x03\x0f\x1d\x1f\x16]+)', s):
        if m.group(4): span(m.group(4))
        elif m.group(3):
            c = m.group(3)
            if c == '\x02': st['b'] = not st['b']
            elif c == '\x1d': st['i'] = not st['i']
            elif c == '\x1f': st['u'] = not st['u']
            elif c == '\x0f': st.update(b=False, i=False, u=False, fg=None, bg=None)
        else:
            st['fg'] = int(m.group(1)) if m.group(1) else None
            st['bg'] = int(m.group(2)) if m.group(2) else (st['bg'] if m.group(1) else None)
    return ''.join(out)


plain = lambda s: re.sub(r'\x03(\d{1,2}(,\d{1,2})?)?|[\x02\x0f\x1d\x1f\x16]', '', s or '')

commands = []
for c in table('CMDS'):
    c += [None] * (7 - len(c))
    commands.append(dict(name=c[0], group=c[1], usage=plain(c[2]), summary=plain(c[3]), details=plain(c[4]),
                         examples=[plain(e) for e in (c[5] or [])], aliases=(c[6] or '').split()))

guide = [dict(title=g[0], html=[mirc_html(l) for l in g[1]]) for g in table('GUIDE')]

# ---- settings from the config template ------------------------------------------
settings, sec, note, skip = [], None, [], False
conf_lines = [l.rstrip('\n') for l in open(os.path.join(root, "iSekur.conf.example"), encoding="utf-8")]
# comment lines right above a [section] header are that section's intro, not an optional key of the one before
intro_lines, i = set(), 0
while i < len(conf_lines):
    if re.match(r'^\s*[#;]', conf_lines[i]):
        j = i
        while j < len(conf_lines) and re.match(r'^\s*[#;]', conf_lines[j]): j += 1
        if j < len(conf_lines) and re.match(r'^\s*\[', conf_lines[j]): intro_lines.update(range(i, j))
        i = j
    else: i += 1
for n, line in enumerate(conf_lines):
    t = re.sub(r'^\s*[#;]\s?', '', line) if re.match(r'^\s*[#;]', line) else None
    if re.match(r'^\s*\[', line):
        name = line.strip()[1:-1]
        sec = dict(section=name, intro=' '.join(note), keys=[]); settings.append(sec); note = []; skip = False
    elif t is not None and t.startswith('['):
        skip = True; note = []  # a commented-out example section (twitch)
    elif t is not None and re.match(r'^\w+\s*=', t) and n not in intro_lines:
        if sec is not None and not skip:  # an optional key, shown commented out
            k, _, v = t.partition('=')
            val, _, com = v.partition(' ;')
            sec['keys'].append(dict(key=k.strip(), default='', example=val.strip(), doc=com.strip()))
    elif t is not None:
        note.append(t.strip())
    elif '=' in line and sec is not None:
        k, _, v = line.partition('=')
        val, _, com = v.partition(' ;')
        sec['keys'].append(dict(key=k.strip(), default=val.strip(), doc=(' '.join(note) + ' ' + com.strip()).strip()))
        note = []
    elif not line.strip():
        note = []
srv = [x for x in settings if x['section'].startswith('server.')]
merged = dict(section='server.<name>', intro=srv[0]['intro'], keys=[])
for x in srv:  # every key the example servers show, once
    for k in x['keys']:
        if k['key'] not in [m['key'] for m in merged['keys']]: merged['keys'].append(k)
settings = [x for x in settings if x['keys'] and not x['section'].startswith('server.')]
settings.insert(1, merged)

print(json.dumps(dict(commands=commands, guide=guide, settings=settings), ensure_ascii=False, separators=(',', ':')))
