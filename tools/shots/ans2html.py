# ans2html.py capture.ans theme > out.html : a tmux capture-pane -e dump as a macOS-style terminal window
import sys, re, html, os
src = open(sys.argv[1]).read()
src = re.sub(r"\x1b\]8;[^\x1b\x07]*(\x1b\\|\x07)", "", src)  # OSC 8 links
th = open(os.path.join(os.environ.get("ISEKUR", os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../iSekur")), "themes", sys.argv[2] + ".theme")).read()
dfg, dbg = re.search(r"^default\s*=\s*(#\w+)\s+(#\w+)", th, re.M).groups()
P16 = ["#000000","#cd0000","#00cd00","#cdcd00","#0000ee","#cd00cd","#00cdcd","#e5e5e5",
       "#7f7f7f","#ff0000","#00ff00","#ffff00","#5c5cff","#ff00ff","#00ffff","#ffffff"]
def c256(n):
    if n < 16: return P16[n]
    if n < 232:
        n -= 16; v = [0, 95, 135, 175, 215, 255]
        return "#%02x%02x%02x" % (v[n // 36], v[n // 6 % 6], v[n % 6])
    g = 8 + (n - 232) * 10; return "#%02x%02x%02x" % (g, g, g)
def run(line):
    st = dict(fg=None, bg=None, b=0, d=0, i=0, u=0, r=0); out = []
    for tok in re.split(r"(\x1b\[[0-9;:]*m)", line):
        if tok.startswith("\x1b["):
            a = [int(x) if x else 0 for x in re.split("[;:]", tok[2:-1])] or [0]
            k = 0
            while k < len(a):
                x = a[k]
                if x == 0: st = dict(fg=None, bg=None, b=0, d=0, i=0, u=0, r=0)
                elif x == 1: st["b"] = 1
                elif x == 2: st["d"] = 1
                elif x == 3: st["i"] = 1
                elif x == 4: st["u"] = 1
                elif x == 7: st["r"] = 1
                elif x == 22: st["b"] = st["d"] = 0
                elif x == 23: st["i"] = 0
                elif x == 24: st["u"] = 0
                elif x == 27: st["r"] = 0
                elif x in (38, 48):
                    key = "fg" if x == 38 else "bg"
                    if a[k+1] == 2: st[key] = "#%02x%02x%02x" % tuple(a[k+2:k+5]); k += 4
                    else: st[key] = c256(a[k+2]); k += 2
                elif x == 39: st["fg"] = None
                elif x == 49: st["bg"] = None
                elif 30 <= x <= 37: st["fg"] = P16[x-30]
                elif 40 <= x <= 47: st["bg"] = P16[x-40]
                elif 90 <= x <= 97: st["fg"] = P16[x-82]
                elif 100 <= x <= 107: st["bg"] = P16[x-92]
                k += 1
        elif tok:
            fg, bg = st["fg"] or dfg, st["bg"] or dbg
            if st["r"]: fg, bg = bg, fg
            css = f"color:{fg};background:{bg}"
            if st["b"]: css += ";font-weight:700"
            if st["d"]: css += ";opacity:.6"
            if st["i"]: css += ";font-style:italic"
            if st["u"]: css += ";text-decoration:underline"
            out.append(f'<span style="{css}">{html.escape(tok)}</span>')
    return "".join(out)
rows = src.rstrip("\n").split("\n")
body = "\n".join(f'<div class="l">{run(r)}</div>' for r in rows)
print(f"""<!doctype html><meta charset="utf-8"><style>
html,body{{margin:0;background:transparent}}
#shot{{padding:27px 30px 27px 27px;display:inline-block}}
.win{{border-radius:12px;overflow:hidden;box-shadow:0 0 0 1px rgba(0,0,0,.35),0 18px 40px rgba(0,0,0,.28);background:{dbg};width:802px}}
.tb{{height:30px;background:#26252e;position:relative;font:13px -apple-system,BlinkMacSystemFont,sans-serif;color:#c9c9d1;text-align:center;line-height:30px}}
.tb i{{position:absolute;top:9px;width:12px;height:12px;border-radius:50%}}
.t{{padding:10px 11px 12px;font:13px/17px ui-monospace,"SF Mono",Menlo,monospace}}
.l{{white-space:pre;height:17px}}
</style><body><div id="shot"><div class="win"><div class="tb"><i style="left:13px;background:#ff5f57"></i><i style="left:33px;background:#febc2e"></i><i style="left:53px;background:#28c840"></i>isekur</div><div class="t">{body}</div></div></div>""")
