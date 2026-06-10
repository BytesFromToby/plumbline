from PIL import Image, ImageDraw, ImageFont

# ---- canvas / scale ----
W, H, S = 1000, 300, 2
def sc(v): return int(round(v * S))

# ---- palette ----
BG          = (13, 17, 23)
IDLE_BORDER = (48, 54, 61)
IDLE_TEXT   = (110, 118, 129)
ACCENT      = (88, 166, 255)
ACCENT_FILL = (24, 43, 71)
DONE_BORDER = (56, 96, 150)
GREEN       = (63, 185, 80)
GREEN_FILL  = (18, 51, 31)
GATE        = (240, 180, 70)
WHITE       = (235, 240, 246)
MUTED       = (139, 148, 158)

def font(path, size):
    try: return ImageFont.truetype(path, sc(size))
    except Exception: return ImageFont.load_default()

F_TITLE = font(r"C:\Windows\Fonts\segoeuib.ttf", 30)
F_SUB   = font(r"C:\Windows\Fonts\segoeui.ttf", 15)
F_BADGE = font(r"C:\Windows\Fonts\segoeuib.ttf", 16)
F_PILL  = font(r"C:\Windows\Fonts\segoeuib.ttf", 18)
F_ART   = font(r"C:\Windows\Fonts\consola.ttf", 14)
F_STAT  = font(r"C:\Windows\Fonts\segoeui.ttf", 17)

# ---- the two rows we animate ----
BUILD = [
    ("scaffold",  "git, skeleton, CLAUDE.md"),
    ("architect", "spec.md"),
    ("foreman",   "blueprint.md"),
    ("builder",   "code + tests"),
    ("inspector", "fidelity-checked PASS"),
]
WALK = [
    ("walkthrough", "baseline"),
    ("surveyor",    "drift report"),
    ("inspector",   "proof + evidence"),
]

PILL_H, PILL_TOP = 54, 108
PILL_CY = PILL_TOP + PILL_H / 2

def layout(n):
    """Even spread of n pills across the canvas."""
    margin = 24
    pw = 150 if n >= 5 else 200
    gap = (W - 2 * margin - n * pw) / (n - 1) if n > 1 else 0
    lefts = [margin + i * (pw + gap) for i in range(n)]
    return pw, lefts

def ctext(d, cx, cy, text, fnt, fill):
    b = d.textbbox((0, 0), text, font=fnt)
    d.text((sc(cx) - (b[2]-b[0]) / 2, sc(cy) - (b[3]-b[1]) / 2 - b[1]), text, font=fnt, fill=fill)

def rtext(d, rx, y, text, fnt, fill):
    b = d.textbbox((0, 0), text, font=fnt)
    d.text((sc(rx) - (b[2]-b[0]), sc(y)), text, font=fnt, fill=fill)

def check(d, cx, cy, color):
    r = 11
    d.ellipse([sc(cx-r), sc(cy-r), sc(cx+r), sc(cy+r)], fill=color)
    d.line([(sc(cx-5), sc(cy)), (sc(cx-1), sc(cy+4)), (sc(cx+6), sc(cy-5))],
           fill=BG, width=sc(2), joint="curve")

def tri_up(d, cx, top, color, size=7):
    d.polygon([(sc(cx), sc(top)), (sc(cx-size), sc(top+size)), (sc(cx+size), sc(top+size))], fill=color)

def arrow(d, x1, x2, y, frac):
    d.line([(sc(x1), sc(y)), (sc(x2), sc(y))], fill=IDLE_BORDER, width=sc(3))
    if frac > 0:
        xf = x1 + (x2 - x1) * frac
        d.line([(sc(x1), sc(y)), (sc(xf), sc(y))], fill=ACCENT, width=sc(3))
    col = ACCENT if frac >= 1 else IDLE_BORDER
    ah = 7
    d.polygon([(sc(x2), sc(y)), (sc(x2-ah), sc(y-ah)), (sc(x2-ah), sc(y+ah))], fill=col)

def render(stages, active, done, arrows, artifacts, status, status_color,
           final=False, caption="", gate=None, gate_text=""):
    n = len(stages)
    pw, lefts = layout(n)
    def cx(i): return lefts[i] + pw / 2
    img = Image.new("RGB", (sc(W), sc(H)), BG)
    d = ImageDraw.Draw(img)
    # title + subtitle + mode badge
    d.text((sc(24), sc(26)), "Plumbline", font=F_TITLE, fill=ACCENT)
    d.text((sc(26), sc(64)), "a spec-driven workflow of AI-agent skills", font=F_SUB, fill=MUTED)
    if caption:
        rtext(d, W - 24, 40, caption, F_BADGE, ACCENT)
    # arrows between pills
    for k in range(n - 1):
        arrow(d, lefts[k] + pw, lefts[k + 1], PILL_CY, arrows.get(k, 0.0))
    # pills
    for i, (name, art) in enumerate(stages):
        L = lefts[i]
        box = [sc(L), sc(PILL_TOP), sc(L + pw), sc(PILL_TOP + PILL_H)]
        is_done = i in done
        is_active = i == active
        last_green = final and i == n - 1
        if is_active:
            d.rounded_rectangle(box, radius=sc(12), fill=ACCENT_FILL, outline=ACCENT, width=sc(3)); tcol = WHITE
        elif last_green:
            d.rounded_rectangle(box, radius=sc(12), fill=GREEN_FILL, outline=GREEN, width=sc(3)); tcol = WHITE
        elif is_done:
            d.rounded_rectangle(box, radius=sc(12), outline=DONE_BORDER, width=sc(2)); tcol = MUTED
        else:
            d.rounded_rectangle(box, radius=sc(12), outline=IDLE_BORDER, width=sc(2)); tcol = IDLE_TEXT
        ctext(d, cx(i), PILL_CY, name, F_PILL, tcol)
        if is_done or last_green:
            check(d, L + pw - 13, PILL_TOP + 13, GREEN if (last_green or i == n - 1) else ACCENT)
        # gate flag wins over the artifact label on its pill
        if gate == i:
            tri_up(d, cx(i), PILL_TOP + PILL_H + 6, GATE)
            ctext(d, cx(i), PILL_TOP + PILL_H + 26, gate_text, F_ART, GATE)
        elif i in artifacts:
            acol = GREEN if i == n - 1 else (ACCENT if i == active else MUTED)
            ctext(d, cx(i), PILL_TOP + PILL_H + 26, art, F_ART, acol)
    ctext(d, W / 2, 252, status, F_STAT, status_color)
    return img.resize((W, H), Image.LANCZOS)

# ---------- frame assembly ----------
frames, durs = [], []
def add(img, d): frames.append(img); durs.append(d)

def animate_chain(stages, caption, baton_text, activate_ms, settle_ms,
                  final_status, final_color, hold_ms,
                  gate=None, gate_text="", gate_hold_ms=0,
                  baton_fracs=(0.34, 0.67, 1.0), baton_ms=70):
    n = len(stages)
    last = None
    for i, (name, art) in enumerate(stages):
        base = {k: 1.0 for k in range(i)}
        if i > 0:
            for fr in baton_fracs:
                a = dict(base); a[i - 1] = fr
                last = render(stages, None, set(range(i)), a, set(range(i)),
                              baton_text, MUTED, caption=caption)
                add(last, baton_ms)
        # activate
        last = render(stages, i, set(range(i)), {k: 1.0 for k in range(i)}, set(range(i)),
                      f"{name}   →   {art}", ACCENT, caption=caption)
        add(last, activate_ms)
        # settle (artifact or gate flag appears)
        last = render(stages, i, set(range(i)), {k: 1.0 for k in range(i)}, set(range(i + 1)),
                      f"{name}   →   {art}", ACCENT, caption=caption,
                      gate=(gate if gate == i else None), gate_text=gate_text)
        add(last, settle_ms)
        # gate pause — the one stop in the contractor sweep
        if gate == i and gate_hold_ms:
            last = render(stages, i, set(range(i)), {k: 1.0 for k in range(i)}, set(range(i + 1)),
                          "stop — you approve the spec", GATE, caption=caption,
                          gate=i, gate_text=gate_text)
            add(last, gate_hold_ms)
    # final settle
    add(render(stages, None, set(range(n)), {k: 1.0 for k in range(n - 1)}, set(range(n)),
               final_status, final_color, final=True, caption=caption), hold_ms)

import os
def save_gif(name):
    frames[0].save(name, save_all=True, append_images=frames[1:],
                   duration=durs, loop=0, optimize=True, disposal=2)
    print(f"{name:18} frames {len(frames):3d}  sec {sum(durs)/1000:4.1f}  "
          f"MB {os.path.getsize(name)/1e6:.2f}")

# ---- demo_diagram.gif — the build hero, unchanged (no badge) ----
frames, durs = [], []
add(render(BUILD, None, set(), {}, set(), "a plain-language prompt in . . .", MUTED), 750)
animate_chain(BUILD, caption="", baton_text="passing the baton . . .",
              activate_ms=140, settle_ms=680,
              final_status="trust, but verify  —  idea to verified, working code",
              final_color=GREEN, hold_ms=1600,
              gate=1, gate_text="your approval", gate_hold_ms=950)
save_gif("demo_diagram.gif")

# ---- walkthrough.gif — maintain mode, unattended ----
frames, durs = [], []
add(render(WALK, None, set(), {}, set(), "point it at a built project — then walk away . . .",
           MUTED, caption="walkthrough"), 850)
animate_chain(WALK, caption="walkthrough · maintain mode",
              baton_text="walking the project . . .", activate_ms=135, settle_ms=560,
              final_status="Quick-Path fixes applied  ·  Recommendations for review",
              final_color=GREEN, hold_ms=1700)
save_gif("walkthrough.gif")
