"""
Generates the SVG artwork for Rithik Sharma's GitHub profile README.

Every SVG embeds its own subset of JetBrains Mono (400 + 800) as base64 woff2,
because GitHub serves README images through a proxy where external font
requests are blocked. JetBrains Mono's advance width is exactly 0.6em, so all
text positions below are computed, not eyeballed.
"""
import base64, io, textwrap
from fontTools import subset
from fontTools.ttLib import TTFont

FONT_DIR = "fonts/"
C = dict(
    void="#080B0A", panel="#0D1311", sunk="#0A0F0D", rule="#1C2622",
    green="#3DFF8F", greenDim="#1E6B45", greenFaint="#12301F",
    ink="#D8E6DE", muted="#7D928A", faint="#4A5A53", amber="#FFB84D", amberBg="#3A2A0E",
)
CHARSET = "".join(chr(c) for c in range(32, 127)) + "·'"

def font_b64(weight):
    f = TTFont(f"{FONT_DIR}jetbrains-mono-latin-{weight}-normal.woff2")
    opts = subset.Options(); opts.flavor = "woff2"; opts.layout_features = []
    s = subset.Subsetter(opts); s.populate(text=CHARSET); s.subset(f)
    buf = io.BytesIO(); f.flavor = "woff2"; f.save(buf)
    return base64.b64encode(buf.getvalue()).decode()

FONTS = {w: font_b64(w) for w in (400, 800)}

def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def W(n, size):
    """Exact pixel width of n monospace characters."""
    return n * size * 0.6

def svg(w, h, body, extra_css="", title=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{esc(title)}">
<title>{esc(title)}</title>
<style>
@font-face{{font-family:'JBM';font-weight:400;src:url(data:font/woff2;base64,{FONTS[400]}) format('woff2');font-display:swap;}}
@font-face{{font-family:'JBM';font-weight:800;src:url(data:font/woff2;base64,{FONTS[800]}) format('woff2');font-display:swap;}}
text{{font-family:'JBM',ui-monospace,monospace;}}
.b{{font-weight:800}}
@keyframes blink{{0%,49%{{opacity:1}}50%,100%{{opacity:0}}}}
.cursor{{animation:blink 1.05s steps(1) infinite}}
{extra_css}
@media (prefers-reduced-motion: reduce){{ *{{animation:none!important}} .rm-hide{{display:none}} }}
</style>
{body}
</svg>'''

def t(x, y, s, size=14, fill=C["ink"], bold=False, anchor="start", extra=""):
    cls = ' class="b"' if bold else ""
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}"{cls} text-anchor="{anchor}" {extra}>{esc(s)}</text>'

def frame(w, h, path, tag=None):
    """Card chrome: panel, hairline border, a title bar showing a shell path."""
    out = [f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="14" fill="{C["panel"]}" stroke="{C["rule"]}"/>',
           f'<line x1="0" y1="40" x2="{w}" y2="40" stroke="{C["rule"]}"/>',
           t(22, 25, "~/", 12, C["greenDim"]), t(22 + W(2, 12), 25, path, 12, C["muted"])]
    if tag:
        tw = W(len(tag), 11) + 20
        out.append(f'<rect x="{w-22-tw}" y="12" width="{tw}" height="18" rx="9" fill="none" stroke="{C["greenDim"]}"/>')
        out.append(t(w - 22 - tw / 2, 25, tag, 11, C["green"], anchor="middle"))
    return "\n".join(out)

def chip(x, y, label, size=12, stroke=C["greenDim"], fill="none", color=C["ink"], lpad=10):
    w = W(len(label), size) + 10 + lpad
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{size+14}" rx="{(size+14)/2}" fill="{fill}" stroke="{stroke}"/>'
            + t(x + lpad, y + size + 3, label, size, color)), w

def wrap(s, width):
    return textwrap.wrap(s, width)

def check(x, y, color=C["green"]):
    return f'<path d="M{x} {y} l3.5 3.5 l7 -8" fill="none" stroke="{color}" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>'

def arrow(x1, y, x2, color=C["greenDim"]):
    return (f'<line x1="{x1}" y1="{y}" x2="{x2-6}" y2="{y}" stroke="{color}" stroke-width="1.5"/>'
            f'<path d="M{x2-7} {y-4} L{x2} {y} L{x2-7} {y+4}" fill="none" stroke="{color}" stroke-width="1.5" stroke-linejoin="round"/>')

def dot(x, y, r=4, color=C["green"]):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>'

def save(name, content):
    open(f"assets/{name}", "w").write(content)
    print(f"  {name:<22} {len(content)/1024:6.1f} KB")

# ============================================================== HERO
def hero():
    w, h = 1000, 392
    b = [f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="16" fill="{C["panel"]}" stroke="{C["rule"]}"/>',
         f'<line x1="0" y1="44" x2="{w}" y2="44" stroke="{C["rule"]}"/>']

    # Prompt line with a typed command and blinking cursor
    prompt = "rithik@sec:~$ "
    cmd = "./profile --inspect"
    px = 24
    b.append(t(px, 28, prompt, 13, C["green"], bold=True))
    cx = px + W(len(prompt), 13)
    b.append(t(cx, 28, cmd, 13, C["ink"]))
    # Cover that slides right in steps to "type" the command
    cw = W(len(cmd), 13) + 4
    b.append(f'<rect class="typer rm-hide" x="{cx-1}" y="14" width="{cw}" height="20" fill="{C["panel"]}"/>')
    b.append(f'<rect class="cursor" x="{cx + W(len(cmd),13) + 3}" y="17" width="8" height="15" fill="{C["green"]}"/>')
    b.append(t(w - 24, 28, "capture: rithik.pcap", 12, C["faint"], anchor="end"))

    # Left: identity
    lx = 44
    b.append(t(lx, 104, "OFFENSIVE SECURITY  /  IOT SECURITY", 12, C["green"], bold=True, extra='letter-spacing="1.5"'))
    b.append(t(lx, 172, "RITHIK", 68, C["ink"], bold=True))
    b.append(t(lx, 240, "SHARMA A", 68, C["ink"], bold=True))
    b.append(t(lx, 282, "Final-year B.E. Cyber Security", 14, C["muted"]))
    b.append(t(lx, 304, "KCG College of Technology, Chennai", 14, C["muted"]))

    # Status chips
    y = 334
    live, lw = chip(lx, y, "open to trainee security roles", 12, stroke=C["green"], fill=C["greenFaint"], color=C["green"], lpad=26)
    b.append(live); b.append(dot(lx + 16, y + 13, 3.5))
    c2, w2 = chip(lx + lw + 10, y, "class of 2027", 12)
    b.append(c2)
    c3, _ = chip(lx + lw + 10 + w2 + 10, y, "chennai, IN", 12)
    b.append(c3)

    # Right: bytes pane
    data = "WHOAMI: RITHIK SHARMA A ROLE: OFFENSIVE SEC FOCUS: IOT+WEB APPS."
    data = data[:64].ljust(64, "\0")
    sel_start = data.index("OFFENSIVE SEC"); sel_end = sel_start + len("OFFENSIVE SEC")
    raw = data.encode()

    px0, py0, pw, ph = 548, 70, 420, 282
    b.append(f'<rect x="{px0}" y="{py0}" width="{pw}" height="{ph}" rx="10" fill="{C["sunk"]}" stroke="{C["rule"]}"/>')
    fs = 12.5
    ox, hx, ax = px0 + 18, px0 + 18 + W(7, fs), px0 + 18 + W(7, fs) + W(25, fs)
    b.append(t(ox, py0 + 26, "offset", 11, C["faint"]))
    b.append(t(hx, py0 + 26, "hex", 11, C["faint"]))
    b.append(t(ax, py0 + 26, "ascii", 11, C["faint"]))
    b.append(f'<line x1="{px0}" y1="{py0+38}" x2="{px0+pw}" y2="{py0+38}" stroke="{C["rule"]}"/>')

    row_h = 23
    first_row_y = py0 + 60
    # Scan line: a faint band stepping down the rows
    b.append(f'<rect class="scan" x="{px0+1}" y="{first_row_y-15}" width="{pw-2}" height="{row_h-2}" fill="{C["green"]}" opacity="0.06"/>')

    for r in range(8):
        y = first_row_y + r * row_h
        b.append(t(ox, y, f"{r*8:04x}", fs, C["faint"]))
        for c in range(8):
            i = r * 8 + c
            byte = raw[i]
            bx = hx + W(c * 3, fs)
            axx = ax + W(c, fs)
            selected = sel_start <= i < sel_end
            ch = chr(byte) if 32 <= byte < 127 else "."
            if selected:
                b.append(f'<rect x="{bx-2}" y="{y-12}" width="{W(2,fs)+4}" height="16" rx="2" fill="{C["amberBg"]}"/>')
                b.append(f'<rect x="{axx-1}" y="{y-12}" width="{W(1,fs)+2}" height="16" fill="{C["amberBg"]}"/>')
            colour = C["amber"] if selected else (C["muted"] if byte else C["faint"])
            b.append(t(bx, y, f"{byte:02x}", fs, colour))
            b.append(t(axx, y, ch, fs, C["amber"] if selected else (C["ink"] if byte else C["faint"])))

    # Detail line, like Wireshark's packet-details pane
    dy = py0 + ph - 22
    b.append(f'<line x1="{px0}" y1="{dy-20}" x2="{px0+pw}" y2="{dy-20}" stroke="{C["rule"]}"/>')
    b.append(f'<path d="M{ox} {dy-9} l6 4 l-6 4 z" fill="{C["amber"]}"/>')
    b.append(t(ox + 14, dy, f"role: Offensive Security  [{sel_end-sel_start} bytes selected]", 12, C["amber"]))

    steps = cmd.__len__()
    css = f'''
@keyframes type{{from{{transform:translateX(0)}}to{{transform:translateX({cw}px)}}}}
.typer{{animation:type 1.5s steps({steps}) 0.4s forwards}}
@keyframes scan{{0%{{transform:translateY(0)}}100%{{transform:translateY({row_h*8}px)}}}}
.scan{{animation:scan 4.8s steps(8) infinite}}
'''
    save("hero.svg", svg(w, h, "\n".join(b), css,
        "Rithik Sharma A. Offensive security and IoT security. Final-year B.E. Cyber Security at KCG College of Technology, Chennai. Open to trainee security engineer roles."))

# ============================================================== LINK BUTTONS
def button(name, label, sub):
    w, h = 236, 56
    b = [f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="12" fill="{C["panel"]}" stroke="{C["greenDim"]}"/>',
         t(18, 24, label, 13, C["green"], bold=True),
         t(18, 42, sub, 12, C["muted"]),
         f'<path d="M{w-30} 22 l8 6 l-8 6" fill="none" stroke="{C["green"]}" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>']
    save(f"link-{name}.svg", svg(w, h, "\n".join(b), title=f"{label}: {sub}"))

# ============================================================== ARSENAL
def arsenal():
    w = 1000
    groups = [
        ("Recon & traffic", ["Nmap", "Wireshark", "Nessus"]),
        ("Web & exploitation", ["Burp Suite", "OWASP ZAP", "Metasploit", "OWASP Top 10"]),
        ("Languages", ["Python", "C", "Java", "Bash", "JavaScript", "TypeScript", "SQL"]),
        ("Platforms", ["Linux", "Git / GitHub", "Google Cloud", "Azure", "Cisco networking"]),
    ]
    col_w = (w - 48 - 3 * 24) / 4
    body = []
    max_y = 0
    for gi, (name, items) in enumerate(groups):
        x0 = 24 + gi * (col_w + 24)
        body.append(f'<rect x="{x0}" y="70" width="3" height="14" fill="{C["green"]}"/>')
        body.append(t(x0 + 12, 82, name, 13, C["ink"], bold=True))
        x, y = x0, 102
        for it in items:
            cw = W(len(it), 12) + 20
            if x + cw > x0 + col_w:
                x, y = x0, y + 36
            c, cw = chip(x, y, it, 12)
            body.append(c)
            x += cw + 8
        max_y = max(max_y, y + 26)
    h = int(max_y + 30)
    b = frame(w, h, "arsenal") + "\n" + "\n".join(body)
    save("arsenal.svg", svg(w, h, b, title="Tools and languages: Nmap, Wireshark, Nessus, Burp Suite, OWASP ZAP, Metasploit, OWASP Top 10, Python, C, Java, Bash, JavaScript, TypeScript, SQL, Linux, Git, Google Cloud, Azure, Cisco networking."))

# ============================================================== SENTINEL OTA (featured)
def sentinel():
    w, h = 1000, 300
    b = [frame(w, h, "projects/sentinel-ota", "featured")]
    b.append(t(28, 92, "SentinelOTA", 30, C["ink"], bold=True))
    desc = "Secure over-the-air firmware updates for mixed IoT fleets. Every package is encrypted and signed, every device checks the version before it installs, and risky nodes get quarantined."
    for i, line in enumerate(wrap(desc, 58)):
        b.append(t(28, 124 + i * 21, line, 13, C["muted"]))
    y = 124 + 4 * 21 + 8
    x = 28
    for s in ["TypeScript", "Embedded C", "Signed payloads", "Anti-rollback"]:
        c, cw = chip(x, y, s, 11)
        b.append(c); x += cw + 8

    # Pipeline diagram on the right
    stages = [("build", "firmware"), ("sign", "+ encrypt"), ("gateway", "API-key auth"), ("device", "verify")]
    sx, sy, bw, bh, gap = 560, 84, 92, 54, 16
    for i, (a, bsub) in enumerate(stages):
        x0 = sx + i * (bw + gap)
        final = i == len(stages) - 1
        b.append(f'<rect x="{x0}" y="{sy}" width="{bw}" height="{bh}" rx="9" fill="{C["sunk"]}" stroke="{C["green"] if final else C["rule"]}"/>')
        b.append(t(x0 + bw / 2, sy + 23, a, 12, C["green"] if final else C["ink"], bold=True, anchor="middle"))
        b.append(t(x0 + bw / 2, sy + 41, bsub, 10.5, C["muted"], anchor="middle"))
        if not final:
            b.append(arrow(x0 + bw + 2, sy + bh / 2, x0 + bw + gap - 1))
    # travelling packet
    b.append(f'<circle class="pkt" cx="{sx + bw/2}" cy="{sy + bh + 14}" r="4" fill="{C["green"]}"/>')
    b.append(f'<line x1="{sx + bw/2}" y1="{sy+bh+14}" x2="{sx + 3*(bw+gap) + bw/2}" y2="{sy+bh+14}" stroke="{C["rule"]}" stroke-dasharray="2 4"/>')

    checks = ["signature valid", "version newer than installed", "device health above threshold"]
    cy = sy + bh + 50
    for i, c in enumerate(checks):
        b.append(check(sx + 2, cy + i * 24 - 4))
        b.append(t(sx + 20, cy + i * 24, c, 12, C["ink"]))
    b.append(t(sx, h - 22, "ESP32 · ESP8266 · ATmega328P · STM32", 11.5, C["faint"]))

    travel = 3 * (bw + gap)
    css = f'''@keyframes pkt{{0%{{transform:translateX(0);opacity:0}}8%{{opacity:1}}85%{{opacity:1}}100%{{transform:translateX({travel}px);opacity:0}}}}
.pkt{{animation:pkt 3.2s ease-in-out infinite}}'''
    save("proj-sentinelota.svg", svg(w, h, "\n".join(b), css,
        "SentinelOTA: secure over-the-air firmware updates for ESP32, ESP8266, ATmega328P and STM32 with signed, encrypted packages and anti-rollback checks."))

# ============================================================== SMALL PROJECT CARDS
def small(slug, path, name, desc, stack, motif, tag=None, alt=""):
    w, h = 490, 228
    b = [frame(w, h, path, tag)]
    b.append(t(24, 86, name, 22, C["ink"], bold=True))
    for i, line in enumerate(wrap(desc, 38)):
        b.append(t(24, 114 + i * 19, line, 12.5, C["muted"]))
    x = 24
    for s in stack:
        c, cw = chip(x, h - 44, s, 11)
        b.append(c); x += cw + 8
    b.append(motif)
    save(f"proj-{slug}.svg", svg(w, h, "\n".join(b), title=alt))

def motif_wipe(x, y):
    # rows of bytes being overwritten to zero, pass by pass
    out = []
    rows = ["a7 3f 91 0c", "00 00 00 00", "00 00 00 00"]
    labels = ["data", "clear", "verify"]
    for i, (r, l) in enumerate(zip(rows, labels)):
        yy = y + i * 18
        out.append(t(x, yy, l, 10, C["faint"]))
        out.append(t(x + 52, yy, r, 11, C["green"] if i == 2 else C["muted"]))
    return "\n".join(out)

def motif_pixels(x, y):
    out = []; n = 6; s = 11
    hidden = {(1, 2), (2, 4), (3, 1), (4, 3), (1, 5), (5, 2)}
    for r in range(n):
        for c in range(n):
            on = (r, c) in hidden
            shade = ["#16201C", "#1A2621", "#1D2B25"][(r + c) % 3]
            out.append(f'<rect x="{x + c*(s+2)}" y="{y + r*(s+2)}" width="{s}" height="{s}" rx="2" fill="{C["green"] if on else shade}" opacity="{0.85 if on else 1}"/>')
    return "\n".join(out)

def motif_ticket(x, y):
    return (f'<rect x="{x}" y="{y}" width="84" height="54" rx="8" fill="none" stroke="{C["greenDim"]}"/>'
            f'<line x1="{x+58}" y1="{y+6}" x2="{x+58}" y2="{y+48}" stroke="{C["greenDim"]}" stroke-dasharray="3 3"/>'
            + t(x + 10, y + 24, "CYBER", 10, C["green"], bold=True) + t(x + 10, y + 40, "FEST'26", 10, C["ink"], bold=True))

def motif_progress(x, y):
    return (t(x, y, "status", 10, C["faint"])
            + f'<rect x="{x}" y="{y+10}" width="96" height="6" rx="3" fill="{C["rule"]}"/>'
            + f'<rect x="{x}" y="{y+10}" width="38" height="6" rx="3" fill="{C["amber"]}"/>'
            + t(x, y + 34, "in progress", 10.5, C["amber"]))

# ============================================================== LOG: experience + certs
def log():
    w, h = 1000, 400
    b = [frame(w, h, "log", None)]
    b.append(t(28, 80, "Experience", 15, C["ink"], bold=True))
    exp = [
        ("May - Jun 2025", "AI-Azure Intern", "Microsoft program via Edunet Foundation (AICTE)",
         ["ML pipelines on Azure", "identity & access, DevSecOps", "anomaly detection for threat intel"]),
        ("Jan - Feb 2025", "Cyber Security Intern", "Edunet Foundation (AICTE)",
         ["network scanning with Nmap, Wireshark", "vulnerability assessment", "findings + mitigation write-ups"]),
    ]
    tx = 36
    b.append(f'<line x1="{tx}" y1="110" x2="{tx}" y2="{110 + 132}" stroke="{C["rule"]}" stroke-width="2"/>')
    for i, (when, role, org, pts) in enumerate(exp):
        y = 110 + i * 132
        b.append(f'<circle cx="{tx}" cy="{y}" r="6" fill="{C["panel"]}" stroke="{C["green"]}" stroke-width="2"/>')
        b.append(t(tx + 20, y + 4, when, 11, C["green"]))
        b.append(t(tx + 20, y + 26, role, 15, C["ink"], bold=True))
        b.append(t(tx + 20, y + 46, org, 12, C["muted"]))
        for j, p in enumerate(pts):
            b.append(f'<rect x="{tx+20}" y="{y + 60 + j*18}" width="6" height="2" fill="{C["greenDim"]}"/>')
            b.append(t(tx + 34, y + 64 + j * 18, p, 11.5, C["muted"]))

    # Certifications
    cx0 = 520
    b.append(f'<line x1="{cx0-24}" y1="64" x2="{cx0-24}" y2="{h-24}" stroke="{C["rule"]}"/>')
    b.append(t(cx0, 80, "Certifications", 15, C["ink"], bold=True))
    certs = [
        ("2026", "CCNA: Switching, Routing & Wireless", "Cisco"),
        ("2026", "Google Cloud Associate Cloud Engineer", "Google"),
        ("2025", "CCNA: Introduction to Networks", "Cisco"),
        ("2025", "Vulnerability Assessment & Pen Testing", "Datayaan"),
        ("2025", "Practical Cyber Security for Practitioners", "NPTEL"),
        ("2025", "Privacy & Security in Online Social Media", "NPTEL"),
        ("2025", "AI Machine Learning Engineer", "Skill India"),
    ]
    for i, (yr, name, iss) in enumerate(certs):
        y = 116 + i * 40
        b.append(t(cx0, y, yr, 11, C["green"]))
        b.append(t(cx0 + 48, y, name, 12.5, C["ink"]))
        b.append(t(cx0 + 48, y + 17, iss, 11, C["faint"]))
    save("log.svg", svg(w, h, "\n".join(b),
        title="Experience: AI-Azure intern, Microsoft program via Edunet Foundation, 2025; Cyber Security intern, Edunet Foundation, 2025. Seven certifications including Cisco CCNA, Google Cloud ACE and VAPT."))

# ============================================================== FOOTER
def footer():
    w, h = 1000, 120
    b = [f'<rect x="0.5" y="0.5" width="{w-1}" height="{h-1}" rx="14" fill="{C["panel"]}" stroke="{C["rule"]}"/>']
    b.append(t(28, 44, "rithik@sec:~$ ", 13, C["green"], bold=True))
    b.append(t(28 + W(14, 13), 44, "echo $ETHICS", 13, C["ink"]))
    b.append(t(28, 76, "All testing is performed only on systems I own or have explicit written permission to test.", 13, C["muted"]))
    b.append(t(28, 98, "Break it in the lab. Fix it before production.", 12, C["faint"]))
    b.append(f'<rect class="cursor" x="{28 + W(47,12) + 4}" y="87" width="7" height="13" fill="{C["green"]}"/>')
    save("footer.svg", svg(w, h, "\n".join(b), title="All testing is performed only on systems I own or have explicit written permission to test."))

print("Generating assets:")
hero(); arsenal(); sentinel(); log(); footer()
button("portfolio", "Portfolio", "rithiksharma.me")
button("linkedin", "LinkedIn", "in/rithiksharma19")
button("email", "Email", "a.rithiksharma@gmail.com")
small("shredx", "projects/shredx", "ShredX",
      "Cross-platform data sanitisation aligned with NIST SP 800-88 Rev. 1, for secure IT-asset disposal.",
      ["NIST SP 800-88", "team project"], motif_wipe(330, 74), alt="ShredX: NIST SP 800-88 aligned data sanitisation, team project.")
small("stego", "projects/steganography", "Steganography App",
      "Hides AES-encrypted messages inside ordinary images: confidential and invisible. Deployed live.",
      ["Python", "Flask", "OpenCV", "AES"], motif_pixels(386, 64), alt="Steganography app: AES-encrypted messages hidden in images, built with Python, Flask and OpenCV.")
small("cyberfest", "projects/cyberfest26", "CyberFest'26",
      "Event registration platform for the department's cyber festival. Responsive, fast, and dependency-free.",
      ["HTML", "CSS", "JavaScript"], motif_ticket(382, 64), alt="CyberFest'26: event registration platform in HTML, CSS and JavaScript.")
small("kcgerp", "projects/kcg-erp", "KCG ERP",
      "An ERP for the CSE Cyber Security department. By the students, for the students.",
      ["student-built"], motif_progress(372, 70), alt="KCG ERP: department ERP, in progress.")
