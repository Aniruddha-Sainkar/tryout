#!/usr/bin/env python3
"""Tryout usability kit: build one self-contained test file.

    python3 kit/build.py <test-folder> [-o output.html]

<test-folder> holds the two project files:
    test-config.js   sets window.UT_CONFIG (words and tasks)
    prototype.html   the prototype fragment (style + markup + script)

The result is a single HTML file you can email to participants. No server, no install.
What it does, in case you need to redo it in another language: read kit/usability-shell.html,
inline the recorder from kit/assets, replace
/*UT:CONFIG*/ with test-config.js and <!--UT:PROTOTYPE--> with prototype.html, write the file.

    python3 kit/build.py --kit      rebuilds kit/builder.html and kit/session-replay.html (kit maintainers only)
"""
import json, pathlib, re, sys

KIT = pathlib.Path(__file__).resolve().parent
A = KIT / "assets"

def shell():
    """The shell with the recorder inlined; the two project markers are left in."""
    s = (KIT / "usability-shell.html").read_text(encoding="utf-8")
    rr = (A / "rrweb-record-2.1.6.js").read_text(encoding="utf-8").replace("//# sourceMappingURL=record.umd.min.cjs.map", "")
    assert "</script" not in rr.lower()
    return s.replace("/*RRWEB_RECORD*/", rr)

def check(config, proto):
    """Catch the mistakes that break a test before a participant finds them."""
    errs, warns = [], []
    proto = re.sub(r"<!--.*?-->", "", proto, flags=re.S)   # comments may mention anything
    if "UT_CONFIG" not in config: errs.append("test-config.js must set window.UT_CONFIG.")
    if "</script" in config.lower(): errs.append("test-config.js must not contain a closing script tag.")
    if "resultsEmail" not in config: errs.append("test-config.js must set resultsEmail: the address participants send their results file to.")
    if re.search(r"<\s*(html|head|body)[\s>]", proto, re.I): errs.append("prototype.html must be a fragment: remove <html>, <head> and <body>.")
    if re.search(r"""(class|id)\s*=\s*["'][^"']*\but-""", proto): errs.append('prototype.html uses a class or id starting with "ut-". That prefix belongs to the shell.')
    if "UT.signal" not in proto and "ut:signal" not in proto: errs.append("prototype.html never reports anything: call UT.signal(type, detail) when the participant acts.")
    if "reset" not in proto: warns.append('prototype.html does not handle UT.on("reset"). "Start over" will not restore the starting state.')
    if re.search(r"position\s*:\s*fixed", proto): warns.append("prototype.html uses position:fixed. Prefer position:absolute inside the prototype root.")
    if re.search(r"(^|\})\s*(body|html|:root|\*)\s*[{,]", proto, re.M): warns.append("prototype.html styles body, html, :root or *. Scope every rule under the prototype's root class.")
    return errs, warns

def build(folder, out=None):
    folder = pathlib.Path(folder)
    config = (folder / "test-config.js").read_text(encoding="utf-8")
    proto = (folder / "prototype.html").read_text(encoding="utf-8")
    errs, warns = check(config, proto)
    for w in warns: print("warning:", w)
    if errs:
        for e in errs: print("error:", e)
        sys.exit(1)
    html = shell().replace("/*UT:CONFIG*/", config).replace("<!--UT:PROTOTYPE-->", proto)
    m = re.search(r"""project\s*:\s*["']([^"']+)["']""", config)
    name = re.sub(r"[^A-Za-z0-9]+", "-", m.group(1)).strip("-") if m else "Prototype"
    out = pathlib.Path(out) if out else folder / f"{name}-usability-test.html"
    out.write_text(html, encoding="utf-8")
    print(f"built {out}  ({len(html)//1024} KB)")
    print("next: open it, run every task once, and check the results email opens.")

def kit():
    """Regenerate the two prebuilt pages from their sources."""
    b = (KIT / "builder-template.html").read_text(encoding="utf-8")
    b = b.replace("/*SHELL_JSON*/", json.dumps(shell()).replace("</", "<\\/"))
    (KIT / "builder.html").write_text(b, encoding="utf-8")
    js = (A / "rrweb-player-2.1.6.js").read_text(encoding="utf-8").replace("//# sourceMappingURL=rrweb-player.umd.min.cjs.map", "")
    css = (A / "rrweb-player-2.1.6.css").read_text(encoding="utf-8").split("/*# sourceMappingURL")[0]
    assert "</script" not in js.lower() and "</style" not in css.lower()
    r = (KIT / "replay-template.html").read_text(encoding="utf-8").replace("/*PLAYER_CSS*/", css).replace("/*PLAYER_JS*/", js)
    (KIT / "session-replay.html").write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"></head><body>' + r + "</body></html>", encoding="utf-8")
    print("rebuilt kit/builder.html and kit/session-replay.html")

if __name__ == "__main__":
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"): print(__doc__); sys.exit(0)
    if args[0] == "--kit": kit(); sys.exit(0)
    build(args[0], args[args.index("-o") + 1] if "-o" in args else None)
