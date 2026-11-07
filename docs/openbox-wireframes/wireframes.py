"""OpenBox wireframes. Run: python3 wireframes.py  (writes one .svg per screen next to this file)

Low-fidelity: one font, OpenBox blue as the only accent. Each screen lists the API calls it relies on in SCREENS.
"""
from pathlib import Path
from xml.sax.saxutils import escape

INK, MUTED, LINE, FILL, SEL = "#1e2533", "#6b7489", "#d4d9e2", "#f6f8fb", "#dbe8fd"
BLUE, BLUE_SOFT, TINT, TINT_EDGE, DANGER = "#0061fe", "#eef4ff", "#a9cdf7", "#7fb3f0", "#d92d20"
FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
W, H = 1000, 660
PERMS = ["view", "edit", "delete"]


class C:
    def __init__(self, w=W, h=H, clip_r=None):
        self.w, self.h, self.o, self.clip_r = w, h, [], clip_r

    def rect(self, x, y, w, h, fill="#ffffff", stroke=LINE, r=4, sw=1, dash=None, opacity=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' fill-opacity="{opacity}"' if opacity is not None else ""
        st = f'stroke="{stroke}" stroke-width="{sw}"' if stroke else 'stroke="none"'
        self.o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" fill="{fill}"{o} {st}{d}/>')

    def text(self, x, y, t, size=13, weight=400, color=INK, anchor="start"):
        self.o.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{escape(t)}</text>')

    def line(self, x1, y1, x2, y2, color=LINE, sw=1, dash=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.o.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{sw}"{d}/>')

    def circle(self, cx, cy, r, fill=FILL, stroke=LINE):
        self.o.append(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}"/>')

    def svg(self):
        head = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}" font-family="{FONT}">'
                f'<rect width="{self.w}" height="{self.h}" fill="#ffffff"/>')
        if self.clip_r:
            head += (f'<defs><clipPath id="frame"><rect width="{self.w}" height="{self.h}" rx="{self.clip_r}"/></clipPath></defs>'
                     '<g clip-path="url(#frame)">')
            return head + "\n".join(self.o) + "</g>" + f'<rect x="0.5" y="0.5" width="{self.w - 1}" height="{self.h - 1}" rx="{self.clip_r}" fill="none" stroke="{LINE}"/></svg>'
        return head + "\n".join(self.o) + "</svg>"


def tw(s, size=13):
    return len(s) * size * 0.56


# ---------- widgets ----------

def button(c, x, y, w, label, kind="secondary", h=34):
    if kind == "primary":
        c.rect(x, y, w, h, fill=BLUE, stroke=BLUE)
        c.text(x + w / 2, y + h / 2 + 5, label, 13, 600, "#ffffff", "middle")
    elif kind == "danger":
        c.rect(x, y, w, h, fill=DANGER, stroke=DANGER)
        c.text(x + w / 2, y + h / 2 + 5, label, 13, 600, "#ffffff", "middle")
    elif kind == "link":
        c.text(x, y + h / 2 + 5, label, 13, 600, BLUE)
    else:
        c.rect(x, y, w, h, fill="#ffffff", stroke=LINE)
        c.text(x + w / 2, y + h / 2 + 5, label, 13, 500, INK, "middle")


def field(c, x, y, w, label=None, value="", placeholder="", error=None, select=False, h=34):
    if label:
        c.text(x, y - 7, label, 12, 600, INK)
    c.rect(x, y, w, h, stroke=DANGER if error else LINE, sw=1.5 if error else 1, r=6)
    if value:
        c.text(x + 10, y + h / 2 + 5, value, 13, 400, INK)
    elif placeholder:
        c.text(x + 10, y + h / 2 + 5, placeholder, 13, 400, LINE)
    if select:
        cx, cy = x + w - 16, y + h / 2
        c.o.append(f'<path d="M{cx-4},{cy-2} l4,4 l4,-4" fill="none" stroke="{MUTED}" stroke-width="1.5"/>')
    if error:
        c.text(x, y + h + 16, error, 12, 500, DANGER)


def checkbox(c, x, y, checked=False, partial=False, label=None):
    c.rect(x, y, 14, 14, fill=BLUE if checked else "#ffffff", stroke=BLUE if checked else "#b7bfcc", r=3)
    if checked:
        c.o.append(f'<path d="M{x+3},{y+7} l3,3 l5,-6" fill="none" stroke="#fff" stroke-width="2"/>')
    if partial:
        c.line(x + 3, y + 7, x + 11, y + 7, INK, 2)
    if label:
        c.text(x + 22, y + 12, label, 13, 400, INK)


def checkbox_row(c, x, y, labels, checked=(), disabled=(), max_x=None):
    x0 = x
    for l in labels:
        step = 22 + tw(l, 13) + 22
        if max_x and x + step - 22 > max_x:
            x, y = x0, y + 28
        if l in disabled:
            c.rect(x, y, 14, 14, fill=FILL, stroke=SEL, r=2)
            c.text(x + 22, y + 12, l, 13, 400, LINE)
        else:
            checkbox(c, x, y, checked=l in checked, label=l)
        x += step


def icon_file(c, x, y, tag=""):
    c.o.append(f'<path d="M{x},{y} h13 l6,6 v16 h-19 z" fill="#ffffff" stroke="{LINE}"/>')
    if tag:
        c.text(x + 9.5, y + 17, tag, 7, 700, MUTED, "middle")


def placeholder(c, x, y, w, h, label="illustration"):
    c.rect(x, y, w, h, fill=FILL, stroke=LINE, r=6, dash="6 4")
    c.line(x, y, x + w, y + h, LINE, 1, "6 4")
    c.line(x + w, y, x, y + h, LINE, 1, "6 4")
    c.rect(x + w / 2 - tw(label, 12) / 2 - 8, y + h / 2 - 12, tw(label, 12) + 16, 22, fill="#ffffff", stroke="none")
    c.text(x + w / 2, y + h / 2 + 4, label, 12, 500, MUTED, "middle")


def chrome(c, url):
    c.rect(0, 0, c.w, 30, fill=FILL, stroke="none", r=0)
    for i in range(3):
        c.circle(16 + i * 14, 15, 4, fill="#ffffff")
    c.rect(70, 6, 420, 18, fill="#ffffff", stroke=LINE, r=9)
    c.text(82, 19, url, 11, 400, MUTED)




CX, CW = 32, 936          # content column on desktop


def shell(c, nav, crumbs, url, crumb_root=None, me="AL", search=None):
    """Top toolbar: logo, Files / Sharing tabs, search, avatar. Page title below it."""
    chrome(c, url)
    c.rect(0, 30, c.w, 56, fill="#ffffff", stroke=None, r=0)
    c.line(0, 86, c.w, 86, LINE)
    c.text(CX, 65, "OpenBox", 20, 800, BLUE)
    tx = CX + 130
    for n in ["Files", "Sharing"]:
        active = n == nav
        c.text(tx, 63, n, 14, 600 if active else 500, BLUE if active else MUTED)
        if active:
            c.rect(tx, 83, tw(n, 14), 3, fill=BLUE, stroke=None, r=1.5)
        tx += tw(n, 14) + 32
    search_box(c, search, x=CX + CW - 52 - 280, y=40, w=280, h=36)
    c.circle(CX + CW - 18, 58, 17, fill=BLUE_SOFT, stroke=TINT_EDGE)
    c.text(CX + CW - 18, 63, me, 12, 700, BLUE, "middle")
    x = CX
    parts = ([crumb_root] if crumb_root else []) + crumbs
    for i, p in enumerate(parts):
        last = i == len(parts) - 1
        c.text(x, 128, p, 20, 600 if last else 400, INK if last else MUTED)
        x += tw(p, 20) + 6
        if not last:
            c.text(x, 128, "›", 20, 400, MUTED)
            x += 18


def search_box(c, value=None, x=700, y=62, w=216, h=36):
    c.rect(x, y, w, h, stroke=BLUE if value else LINE, r=18)
    cx, cy = x + 18, y + h / 2 - 1
    c.o.append(f'<circle cx="{cx}" cy="{cy}" r="5.5" fill="none" stroke="{MUTED}" stroke-width="1.6"/>')
    c.line(cx + 4, cy + 4, cx + 8, cy + 8, MUTED, 1.6)
    c.text(x + 34, y + h / 2 + 5, value or "Search", 13, 400, INK if value else "#9aa3b2")


COLS = [("", 0), ("Name ▾", 550), ("Modified", 240), ("Members", 146)]


def table(c, x, y, rows, cols=COLS):
    cx = x
    for label, w in cols:
        if label:
            c.text(cx, y + 18, label, 12, 600, MUTED)
        cx += w
    c.line(x, y + 30, x + sum(w for _, w in cols), y + 30)
    ry = y + 30
    for r in rows:
        if r.get("selected"):
            c.rect(x, ry, sum(w for _, w in cols), 46, fill=SEL, stroke="none", r=0)
        nx = x + cols[0][1]
        icon_file(c, nx + 2, ry + 12, r.get("tag", ""))
        c.text(nx + 34, ry + 28, r["name"], 13, 500, INK)
        cx = nx + cols[1][1]
        for (label, w), cell in zip(cols[2:], r["cells"]):
            if isinstance(cell, tuple):
                c.text(cx, ry + 21, cell[0], 12, 400, INK)
                c.text(cx, ry + 36, cell[1], 11, 400, MUTED)
            else:
                c.text(cx, ry + 28, cell, 12, 400, INK if cell != "--" else MUTED)
            cx += w
        ry += 46
        c.line(x, ry, x + sum(w for _, w in cols), ry, SEL)
    return ry


def action_bar(c, actions, primary=None, x=CX, w=CW, y=None):
    """Floating light toolbar, centred under the list: evenly spaced icon buttons."""
    y = c.h - 76 if y is None else y
    h, pad = 44, 6
    items = ([(primary, True)] if primary else []) + [(a, False) for a in actions]
    widths = [(tw(a, 13) * 0.93 + 48) if prim else (tw(a, 13) * 0.93 + 44) for a, prim in items]
    total = pad + sum(widths) + 2 * (len(items) - 1) + pad
    bx = x + (w - total) / 2
    for spread, op in ((10, 0.04), (5, 0.05)):
        c.rect(bx - spread / 2, y - spread / 4 + 3, total + spread, h + spread / 2, fill=INK, stroke=None, r=22 + spread / 2, opacity=op)
    c.rect(bx, y, total, h, fill="#ffffff", stroke=LINE, r=22)
    ax = bx + pad
    for (a, prim), aw in zip(items, widths):
        if prim:
            c.rect(ax, y + 7, aw, 30, fill=BLUE, stroke=None, r=15)
            icon(c, ACTION_ICONS[a], ax + 12, y + 12, "#ffffff")
            c.text(ax + 36, y + 27, a, 13, 600, "#ffffff")
        else:
            red = a in ("Delete", "Remove my access")
            color = DANGER if red else INK
            icon(c, ACTION_ICONS[a], ax + 10, y + 12, DANGER if red else MUTED)
            c.text(ax + 34, y + 27, a, 13, 500, color)
        ax += aw + 2


def modal(c, w, h, title):
    c.rect(0, 30, c.w, c.h - 30, fill=INK, stroke="none", r=0, opacity=0.35)
    x, y = (c.w - w) / 2, max(40, (c.h - h) / 2 + 10)
    c.rect(x, y, w, h, fill="#ffffff", stroke=LINE, r=10)
    c.text(x + 24, y + 38, title, 18, 700, INK)
    c.text(x + w - 28, y + 36, "✕", 16, 400, MUTED, "middle")
    return x + 24, y + 64


OWNER_ROWS = [
    {"kind": "file", "tag": "PDF", "name": "Campaign plan.pdf", "cells": ["3/24/2026 9:12AM", "3 members"]},
    {"kind": "file", "tag": "PNG", "name": "Logo draft.png", "cells": ["3/22/2026 4:40PM", "1 member"]},
    {"kind": "file", "tag": "PPT", "name": "Design all hands 3-22.pptx", "cells": ["3/20/2026 3:15PM", "9 members"]},
    {"kind": "file", "tag": "XLS", "name": "Q4 Budget.xls", "cells": ["3/17/2026 10:33AM", "6 members"]},
    {"kind": "file", "tag": "DOC", "name": "Staff review.docx", "cells": ["3/15/2026 1:28PM", "6 members"]},
]


def files_base(c, rows, url="openbox.app/files"):
    shell(c, "Files", ["My files"], url)
    button(c, CX + CW - 96, 106, 96, "Upload", "primary")
    return table(c, CX, 160, rows)


# ---------- desktop screens ----------

def s_landing():
    c = C()
    chrome(c, "openbox.app")
    c.text(48, 78, "OpenBox", 22, 800, BLUE)
    button(c, 704, 56, 100, "Sign in")
    button(c, 814, 56, 138, "Create account", "primary")
    c.text(48, 230, "Share files with exactly", 38, 800)
    c.text(48, 278, "the people who need them", 38, 800)
    c.text(48, 324, "Upload files, share one file at a time with the right", 16, 400, MUTED)
    c.text(48, 348, "permissions, and send links that expire.", 16, 400, MUTED)
    button(c, 48, 384, 150, "Create account", "primary", 42)
    button(c, 212, 384, 110, "Sign in", h=42)
    hero(c, 760, 318, 1.0)
    return c


def sign_in_form(c, x, w, top):
    c.text(x + w / 2, top, "OpenBox", 26, 800, BLUE, "middle")
    c.text(x + w / 2, top + 36, "Sign in", 15, 500, MUTED, "middle")
    field(c, x, top + 90, w, "Email", "alex@acme.com", h=40)
    field(c, x, top + 168, w, "Password", "••••••••••", h=40)
    c.text(x + w, top + 232, "Forgot password?", 13, 600, BLUE, "end")
    button(c, x, top + 252, w, "Sign in", "primary", 44)
    c.text(x + w / 2, top + 330, "New to OpenBox?", 13, 400, MUTED, "middle")
    c.text(x + w / 2, top + 352, "Create an account", 13, 600, BLUE, "middle")


def s_sign_in():
    c = C()
    chrome(c, "auth.openbox.app/login")
    sign_in_form(c, 340, 320, 120)
    return c


def s_files_file():
    c = C()
    rows = [dict(r) for r in OWNER_ROWS]
    rows[2]["selected"] = True
    files_base(c, rows)
    action_bar(c, ["Download", "Replace", "Rename", "Delete"], "Share")
    return c


SHARED_COLS = [("", 0), ("Name ▾", 500), ("Owner", 200), ("Modified", 236)]
SHARED_ROWS = [
    {"kind": "file", "tag": "PDF", "name": "Brand guide.pdf", "cells": ["Robin", "10/28/2026 2:10PM"]},
    {"kind": "file", "tag": "PNG", "name": "Logo final.png", "cells": ["Robin", "10/12/2026 11:05AM"]},
    {"kind": "file", "tag": "XLS", "name": "Q4 Budget.xls", "cells": ["Alex", "3/17/2026 10:33AM"]},
]


def shared_base(c, selected):
    shell(c, "Sharing", ["Sharing"], "openbox.app/sharing", me="KA")
    for i, (t, x) in enumerate([("Shared with me", CX + CW - 236), ("Shared by me", CX + CW - 100)]):
        c.text(x, 128, t, 14, 600 if i == 0 else 400, BLUE if i == 0 else MUTED)
    c.line(CX + CW - 236, 136, CX + CW - 236 + tw("Shared with me", 14), 136, BLUE, 2)
    rows = [dict(r) for r in SHARED_ROWS]
    if selected is not None:
        rows[selected]["selected"] = True
    table(c, CX, 160, rows, SHARED_COLS)


def s_shared_can_edit():
    c = C()
    shared_base(c, 2)
    action_bar(c, ["Download", "Replace", "Remove my access"])
    return c


def s_shared_view_only():
    c = C()
    shared_base(c, 0)
    action_bar(c, ["Download", "Remove my access"])
    return c


def fit(text, width, size):
    """Truncate text with an ellipsis so it fits in width."""
    if tw(text, size) <= width:
        return text
    while text and tw(text + "…", size) > width:
        text = text[:-1]
    return text.rstrip(" ·") + "…"


def x_icon(c, cx, cy, color=MUTED, s=4.5):
    c.line(cx - s, cy - s, cx + s, cy + s, color, 1.5)
    c.line(cx + s, cy - s, cx - s, cy + s, color, 1.5)


def chevron(c, x, y, w, h, value):
    c.rect(x, y, w, h, stroke=LINE, r=6)
    c.text(x + 10, y + h / 2 + 5, value, 13, 400, INK)
    cx, cy = x + w - 14, y + h / 2
    c.o.append(f'<path d="M{cx-4},{cy-2} l4,4 l4,-4" fill="none" stroke="{MUTED}" stroke-width="1.5"/>')


OWNER_LINKS = [("Can view", "Expires Dec 5, 2026", "Used by 3 people"),
               ("Can edit", "Never expires", "Used by 2 people"),
               ("Can view", "Expires Nov 12, 2026", "Not used yet")]
PERM_TEXT = {"view": "See and download it", "edit": "Replace the contents", "delete": "Delete it for everyone"}


def segmented(c, x, y, w, options, active, h=36):
    c.rect(x, y, w, h, fill=FILL, stroke=None, r=h / 2)
    sw = (w - 8) / len(options)
    for i, o in enumerate(options):
        sx = x + 4 + i * sw
        if i == active:
            c.rect(sx, y + 4, sw, h - 8, fill="#ffffff", stroke=LINE, r=(h - 8) / 2)
        c.text(sx + sw / 2, y + h / 2 + 5, o, 13, 600 if i == active else 500, INK if i == active else MUTED, "middle")


def links_list(c, x, y, w, links):
    for i, (perm, exp, used) in enumerate(links):
        ry = y + i * 56
        if i:
            c.line(x + 48, ry, x + w, ry, SEL)
        c.rect(x, ry + 12, 32, 32, fill=BLUE_SOFT, stroke=None, r=8)
        c.o.append(f'<path d="M{x+13},{ry+31} l6,-6 M{x+11},{ry+27} l-2,2 a3.5,3.5 0 0,0 5,5 l2,-2 '
                   f'M{x+21},{ry+29} l2,-2 a3.5,3.5 0 0,0 -5,-5 l-2,2" fill="none" stroke="{BLUE}" stroke-width="1.7" stroke-linecap="round"/>')
        c.text(x + 44, ry + 24, f"{perm} · {exp}", 13, 600, INK)
        c.text(x + 44, ry + 41, used, 12, 400, MUTED)
        c.text(x + w, ry + 32, "Delete", 12, 600, DANGER, "end")
    return y + len(links) * 56


def perm_rows(c, x, y, w, grantable, checked):
    for i, p in enumerate(PERMS):
        ry = y + i * 52
        off = p not in grantable and p != "view"
        if i:
            c.line(x, ry, x + w, ry, SEL)
        c.text(x, ry + 22, p.capitalize(), 14, 600, LINE if off else INK)
        c.text(x, ry + 40, PERM_TEXT[p], 12, 400, LINE if off else MUTED)
        if p == "view":
            c.rect(x + w - 18, ry + 17, 18, 18, fill="#9ec5ff", stroke="#9ec5ff", r=4)
            c.o.append(f'<path d="M{x+w-14},{ry+26} l4,4 l6,-7" fill="none" stroke="#fff" stroke-width="2"/>')
        elif off:
            c.rect(x + w - 18, ry + 17, 18, 18, fill=FILL, stroke=SEL, r=4)
        else:
            c.rect(x + w - 18, ry + 17, 18, 18, fill=BLUE if p in checked else "#ffffff", stroke=BLUE if p in checked else "#b7bfcc", r=4)
            if p in checked:
                c.o.append(f'<path d="M{x+w-14},{ry+26} l4,4 l6,-7" fill="none" stroke="#fff" stroke-width="2"/>')
    return y + len(PERMS) * 52


def calendar_field(c, x, y, w, value, h=36):
    c.rect(x, y, w, h, stroke=BLUE, r=6)
    c.text(x + 12, y + h / 2 + 5, value, 13, 400, INK)
    ix, iy = x + w - 30, y + h / 2 - 8
    c.rect(ix, iy + 2, 16, 14, fill="#ffffff", stroke=MUTED, r=2)
    c.line(ix, iy + 7, ix + 16, iy + 7, MUTED, 1.2)
    c.line(ix + 4, iy, ix + 4, iy + 4, MUTED, 1.2)
    c.line(ix + 12, iy, ix + 12, iy + 4, MUTED, 1.2)


EXPIRY = ["1 day", "7 days", "30 days", "Never", "Date"]


# ---------- desktop ----------

def share_modal_base(c, w, h, title):
    x, y = modal(c, w, h, title)
    return x, y, w - 48


def footer(c, x, y, w, primary, secondary="Cancel"):
    if secondary:
        button(c, x + w - 210, y, 96, secondary)
    button(c, x + w - 106, y, 106, primary, "primary")


def owner_bg(c):
    rows = [dict(r) for r in OWNER_ROWS]
    rows[3]["selected"] = True
    files_base(c, rows)


def s_share_links():
    c = C()
    owner_bg(c)
    x, y, w = share_modal_base(c, 600, 332, "Share “Q4 Budget.xls”")
    c.text(x, y + 14, "Links · 3", 13, 600, MUTED)
    button(c, x + w - 124, y - 8, 124, "+  Create link", "primary", 36)
    end = links_list(c, x, y + 36, w, OWNER_LINKS)
    c.text(x, end + 26, "Deleting a link removes the access of everyone who joined through it.", 12, 400, MUTED)
    return c


def s_create_link():
    c = C()
    owner_bg(c)
    x, y, w = share_modal_base(c, 560, 434, "Create a link to “Q4 Budget.xls”")
    y += 18
    c.text(x, y + 2, "What people who open it can do", 12, 600, INK)
    end = perm_rows(c, x, y + 12, w, PERMS, ["view", "edit"])
    c.text(x, end + 26, "Expires", 12, 600, INK)
    segmented(c, x, end + 36, w, EXPIRY, 4, h=34)
    calendar_field(c, x, end + 82, 200, "Dec 24, 2026")
    footer(c, x, end + 136, w, "Create link")
    return c


def s_link_created():
    c = C()
    owner_bg(c)
    x, y, w = share_modal_base(c, 520, 250, "Link created")
    check_badge(c, x + 8, y - 3, 8)
    c.text(x + 24, y + 2, "Can edit · Expires Dec 24, 2026", 13, 500, MUTED)
    field(c, x, y + 18, w - 120, value="https://openbox.app/links/7Fq9xKpL2mZr", h=38)
    button(c, x + w - 110, y + 18, 110, "Copy link", "primary", 38)
    c.text(x, y + 82, "Copy it now. You won't be able to see this link again.", 12, 500, INK)
    button(c, x + w - 90, y + 118, 90, "Done")
    return c


SEARCH_COLS = [("", 0), ("Name ▾", 500), ("Owner", 286), ("Modified", 150)]


def s_search():
    c = C()
    shell(c, "Files", ["Search"], "openbox.app/search?q=budget", search="budget")
    c.text(CX + 92, 128, "for “budget”", 16, 400, MUTED)
    rows = [
        {"kind": "file", "tag": "XLS", "name": "Budget 2027 draft.xlsx", "cells": ["Robin", "10/2/2026 4:12PM"], "selected": True},
        {"kind": "file", "tag": "XLS", "name": "Q4 Budget.xls", "cells": ["You", "3/17/2026 10:33AM"]},
        {"kind": "file", "tag": "CSV", "name": "Travel budget.csv", "cells": ["You", "2/9/2026 8:20AM"]},
    ]
    table(c, CX, 160, rows, SEARCH_COLS)
    action_bar(c, ["Download", "Remove my access"])
    return c


# ---------- mobile screens (390 × 800) ----------

MW, MH = 390, 800


def phone(c):
    c.rect(0.5, 0.5, MW - 1, MH - 1, fill="#ffffff", stroke=LINE, r=28)
    c.text(28, 30, "9:41", 13, 600, INK)
    c.rect(MW - 52, 20, 24, 11, fill="#ffffff", stroke=INK, r=3)
    c.rect(MW - 50, 22, 16, 7, fill=INK, stroke=None, r=1)


def m_header(c, title=None, me="AL", plus=True):
    if title:
        c.text(20, 82, title, 20, 700, INK)
    else:
        c.text(20, 82, "OpenBox", 20, 800, BLUE)
    if plus:
        c.circle(MW - 72, 76, 17, fill=BLUE, stroke=BLUE)
        c.line(MW - 78, 76, MW - 66, 76, "#ffffff", 2)
        c.line(MW - 72, 70, MW - 72, 82, "#ffffff", 2)
    c.circle(MW - 34, 76, 17, fill=BLUE_SOFT, stroke=TINT_EDGE)
    c.text(MW - 34, 81, me, 11, 700, BLUE, "middle")


def m_tabbar(c, active):
    c.line(0, MH - 64, MW, MH - 64)
    for i, t in enumerate(["Files", "Sharing"]):
        cx = MW / 4 + i * MW / 2
        on = t == active
        color = BLUE if on else MUTED
        if t == "Files":
            c.o.append(f'<path d="M{cx-8},{MH-53} h10 l6,6 v14 h-16 z" fill="{BLUE_SOFT if on else "#ffffff"}" stroke="{color}" '
                       f'stroke-width="1.7" stroke-linejoin="round"/>')
        else:
            icon(c, "share", cx - 10, MH - 53, color)
        c.text(cx, MH - 18, t, 11, 600 if on else 400, BLUE if on else MUTED, "middle")


def m_search(c, y, value=None, w=None):
    search_box(c, value, x=20, y=y, w=w or MW - 40, h=40)


def m_rows(c, y, rows, selected=None):
    for i, r in enumerate(rows):
        ry = y + i * 64
        if i == selected:
            c.rect(0, ry, MW, 64, fill=SEL, stroke=None, r=0)
        icon_file(c, 22, ry + 19, r.get("tag", ""))
        c.text(56, ry + 28, r["name"], 14, 500, INK)
        c.text(56, ry + 46, r["sub"], 12, 400, MUTED)
        c.text(MW - 24, ry + 36, "⋯", 18, 700, MUTED, "middle")
        c.line(56, ry + 64, MW, ry + 64, SEL)


def icon(c, name, x, y, color):
    """20×20 line icons, drawn with one stroke style so they read as a set."""
    st = f'fill="none" stroke="{color}" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"'
    paths = {
        "share": f"M{x+6},{y+11} m-3,0 a3,3 0 1,0 6,0 a3,3 0 1,0 -6,0 M{x+15},{y+5} m-3,0 a3,3 0 1,0 6,0 a3,3 0 1,0 -6,0 "
                 f"M{x+15},{y+16} m-3,0 a3,3 0 1,0 6,0 a3,3 0 1,0 -6,0 M{x+8.6},{y+9.6} L{x+12.4},{y+6.4} M{x+8.6},{y+12.4} L{x+12.4},{y+14.6}",
        "download": f"M{x+10},{y+3} V{y+13} M{x+6},{y+9} L{x+10},{y+13} L{x+14},{y+9} M{x+4},{y+17} H{x+16}",
        "replace": f"M{x+16},{y+8} A6,6 0 0,0 {x+5},{y+6} M{x+5},{y+2.5} V{y+6} H{x+8.5} "
                   f"M{x+4},{y+12} A6,6 0 0,0 {x+15},{y+14} M{x+15},{y+17.5} V{y+14} H{x+11.5}",
        "rename": f"M{x+4},{y+16} L{x+4.6},{y+12.6} L{x+13},{y+4.2} L{x+15.8},{y+7} L{x+7.4},{y+15.4} Z M{x+11.4},{y+5.8} L{x+14.2},{y+8.6}",
        "delete": f"M{x+4},{y+6} H{x+16} M{x+8},{y+6} V{y+4} H{x+12} V{y+6} M{x+5.5},{y+6} L{x+6.5},{y+17} H{x+13.5} L{x+14.5},{y+6} M{x+9},{y+9} V{y+14} M{x+11},{y+9} V{y+14}",
        "leave": f"M{x+8},{y+8} m-3.2,0 a3.2,3.2 0 1,0 6.4,0 a3.2,3.2 0 1,0 -6.4,0 M{x+2.5},{y+17} C{x+3},{y+13} {x+13},{y+13} {x+13.5},{y+17} M{x+13},{y+9} H{x+18}",
    }
    c.o.append(f'<path d="{paths[name]}" {st}/>')


ACTION_ICONS = {"Share": "share", "Download": "download", "Replace": "replace",
                "Rename": "rename", "Delete": "delete", "Remove my access": "leave"}


def m_sheet(c, item, sub, actions, tag=""):
    """App action sheet: item header, icon rows, destructive action set apart in red."""
    c.rect(0, 0, MW, MH - 64, fill=INK, stroke=None, r=0, opacity=0.35)
    danger = [a for a in actions if a in ("Delete", "Remove my access")]
    normal = [a for a in actions if a not in danger]
    h = 30 + 64 + len(normal) * 52 + len(danger) * 52 + (16 if danger and normal else 0) + 28
    y = MH - 64 - h
    c.rect(0, y, MW, h, fill="#ffffff", stroke=None, r=24)
    c.rect(0, y + h - 24, MW, 24, fill="#ffffff", stroke=None, r=0)
    c.line(0, MH - 64, MW, MH - 64, LINE)
    c.rect(MW / 2 - 20, y + 10, 40, 4, fill=LINE, stroke=None, r=2)
    hy = y + 30
    icon_file(c, 22, hy + 6, tag)
    c.text(56, hy + 18, item, 15, 700, INK)
    c.text(56, hy + 36, sub, 12, 400, MUTED)
    c.line(0, hy + 56, MW, hy + 56, SEL)
    yy = hy + 64

    def row(a, red):
        nonlocal yy
        color = DANGER if red else BLUE
        c.rect(20, yy + 8, 36, 36, fill="#fdecea" if red else BLUE_SOFT, stroke=None, r=10)
        icon(c, ACTION_ICONS[a], 28, yy + 16, color)
        c.text(70, yy + 31, a, 15, 500, DANGER if red else INK)
        yy += 52

    for a in normal:
        row(a, False)
    if danger and normal:
        c.line(20, yy + 8, MW - 20, yy + 8, SEL)
        yy += 16
    for a in danger:
        row(a, True)


M_OWNER_ROWS = [
    {"kind": "file", "tag": "PDF", "name": "Campaign plan.pdf", "sub": "3/24/2026 · 3 members"},
    {"kind": "file", "tag": "PNG", "name": "Logo draft.png", "sub": "3/22/2026 · 1 member"},
    {"kind": "file", "tag": "PPT", "name": "Design all hands 3-22.pptx", "sub": "3/20/2026 · 9 members"},
    {"kind": "file", "tag": "XLS", "name": "Q4 Budget.xls", "sub": "3/17/2026 · 6 members"},
    {"kind": "file", "tag": "DOC", "name": "Staff review.docx", "sub": "3/15/2026 · 6 members"},
]
M_SHARED_ROWS = [
    {"kind": "file", "tag": "PDF", "name": "Brand guide.pdf", "sub": "Robin · 10/28/2026"},
    {"kind": "file", "tag": "PNG", "name": "Logo final.png", "sub": "Robin · 10/12/2026"},
    {"kind": "file", "tag": "XLS", "name": "Q4 Budget.xls", "sub": "Alex · 3/17/2026"},
]


def m_files_base(c, selected=None, rows=None):
    phone(c)
    m_header(c)
    c.text(20, 124, "My files", 14, 600, INK)
    m_search(c, 140)
    m_rows(c, 196, rows or M_OWNER_ROWS, selected)
    m_tabbar(c, "Files")


def m_shared_base(c, selected=None):
    phone(c)
    m_header(c, "Sharing", me="KA", plus=False)
    for i, (t, x) in enumerate([("Shared with me", 20), ("Shared by me", 150)]):
        c.text(x, 124, t, 14, 600 if i == 0 else 400, BLUE if i == 0 else MUTED)
    c.line(20, 132, 20 + tw("Shared with me", 14), 132, BLUE, 2)
    m_rows(c, 148, M_SHARED_ROWS, selected)
    m_tabbar(c, "Sharing")


def m_landing():
    c = C(MW, MH, clip_r=28)
    phone(c)
    c.text(20, 82, "OpenBox", 20, 800, BLUE)
    for i, t in enumerate(["Share files with", "exactly the people", "who need them"]):
        c.text(20, 160 + i * 36, t, 30, 800)
    c.text(20, 276, "Upload files, share one file at a time with", 14, 400, MUTED)
    c.text(20, 296, "the right permissions, and send links that expire.", 14, 400, MUTED)
    hero(c, MW / 2, 482, 0.8)
    # bottom toolbar
    c.rect(0, MH - 132, MW, 132, fill="#ffffff", stroke=None, r=0)
    c.line(0, MH - 132, MW, MH - 132, SEL)
    button(c, 20, MH - 116, (MW - 52) / 2, "Sign in", h=48)
    button(c, 32 + (MW - 52) / 2, MH - 116, (MW - 52) / 2, "Create account", "primary", 48)
    c.rect(MW / 2 - 60, MH - 20, 120, 5, fill=INK, stroke=None, r=3)
    return c


def m_sign_in():
    c = C(MW, MH, clip_r=28)
    phone(c)
    sign_in_form(c, 24, MW - 48, 140)
    return c


def m_files_file():
    c = C(MW, MH, clip_r=28)
    m_files_base(c, 2)
    m_sheet(c, "Design all hands 3-22.pptx", "PPTX · 4.8 MB · 9 members", ["Share", "Download", "Replace", "Rename", "Delete"], tag="PPT")
    return c


def m_shared_can_edit():
    c = C(MW, MH, clip_r=28)
    m_shared_base(c, 2)
    m_sheet(c, "Q4 Budget.xls", "Owner Alex · Can edit", ["Download", "Replace", "Remove my access"], tag="XLS")
    return c


def m_shared_view_only():
    c = C(MW, MH, clip_r=28)
    m_shared_base(c, 0)
    m_sheet(c, "Brand guide.pdf", "Owner Robin · Can view", ["Download", "Remove my access"], tag="PDF")
    return c


def m_page(c, title, back=False):
    phone(c)
    if back:
        c.o.append(f'<path d="M30,70 l-7,7 l7,7" fill="none" stroke="{INK}" stroke-width="2" stroke-linecap="round"/>')
    else:
        x_icon(c, 26, 77, INK, 6)
    c.text(48, 82, fit(title, MW - 68, 17), 17, 700, INK)
    c.line(0, 100, MW, 100)


def m_bottom_button(c, label):
    c.rect(0, MH - 100, MW, 100, fill="#ffffff", stroke=None, r=0)
    c.line(0, MH - 100, MW, MH - 100, SEL)
    button(c, 20, MH - 84, MW - 40, label, "primary", 48)
    c.rect(MW / 2 - 60, MH - 20, 120, 5, fill=INK, stroke=None, r=3)


def m_share_links():
    c = C(MW, MH, clip_r=28)
    m_page(c, "Share “Q4 Budget.xls”")
    c.text(20, 130, "Links · 3", 13, 600, MUTED)
    end = links_list(c, 20, 144, MW - 40, OWNER_LINKS)
    c.text(20, end + 26, "Deleting a link removes the access of", 12, 400, MUTED)
    c.text(20, end + 44, "everyone who joined through it.", 12, 400, MUTED)
    m_bottom_button(c, "+  Create link")
    return c


def m_create_link():
    c = C(MW, MH, clip_r=28)
    m_page(c, "Create link", back=True)
    c.text(20, 130, "What people who open it can do", 12, 600, INK)
    end = perm_rows(c, 20, 140, MW - 40, PERMS, ["view", "edit"])
    c.text(20, end + 26, "Expires", 12, 600, INK)
    segmented(c, 20, end + 36, MW - 40, EXPIRY, 4, h=34)
    calendar_field(c, 20, end + 80, MW - 40, "Dec 24, 2026", h=40)
    m_bottom_button(c, "Create link")
    return c


def m_link_created():
    c = C(MW, MH, clip_r=28)
    m_page(c, "Link created")
    c.circle(MW / 2, 190, 32, fill=BLUE_SOFT, stroke=None)
    c.o.append(f'<path d="M{MW/2-12},190 l8,8 l16,-17" fill="none" stroke="{BLUE}" stroke-width="3" stroke-linecap="round"/>')
    c.text(MW / 2, 256, "Can edit · Expires Dec 24, 2026", 13, 500, MUTED, "middle")
    field(c, 20, 280, MW - 40, value="https://openbox.app/links/7Fq9xKpL2mZr", h=44)
    button(c, 20, 334, MW - 40, "Copy link", "primary", 48)
    c.text(MW / 2, 410, "Copy it now. You won't be able to see", 12, 500, INK, "middle")
    c.text(MW / 2, 428, "this link again.", 12, 500, INK, "middle")
    c.rect(MW / 2 - 60, MH - 20, 120, 5, fill=INK, stroke=None, r=3)
    return c


def m_search_screen():
    c = C(MW, MH, clip_r=28)
    phone(c)
    m_search(c, 56, "budget", w=MW - 110)
    c.text(MW - 20, 81, "Cancel", 14, 600, BLUE, "end")
    c.text(20, 128, "Results for “budget”", 13, 500, MUTED)
    m_rows(c, 144, [
        {"kind": "file", "tag": "XLS", "name": "Budget 2027 draft.xlsx", "sub": "Robin · 10/2/2026"},
        {"kind": "file", "tag": "XLS", "name": "Q4 Budget.xls", "sub": "You · 3/17/2026"},
        {"kind": "file", "tag": "CSV", "name": "Travel budget.csv", "sub": "You · 2/9/2026"},
    ], selected=0)
    m_tabbar(c, "Files")
    m_sheet(c, "Budget 2027 draft.xlsx", "Owner Robin · Can view", ["Download", "Remove my access"], tag="XLS")
    return c


# ---------- illustrations ----------

MID, WARM, RED_SOFT, SKEL = "#c9dcfb", "#ffcf5c", "#fdecea", "#eceff4"


def _sparkle(x, y, r, color=WARM):
    k = r * 0.28
    return (f'<path d="M{x},{y-r} L{x+k},{y-k} L{x+r},{y} L{x+k},{y+k} L{x},{y+r} L{x-k},{y+k} L{x-r},{y} L{x-k},{y-k} Z" '
            f'fill="{color}"/>')


def _backdrop(r=62):
    return (f'<circle r="{r}" fill="{BLUE_SOFT}"/>'
            f'<circle cx="{-r - 10}" cy="{-r * 0.55}" r="4" fill="{TINT}"/>'
            f'<circle cx="{r + 12}" cy="{r * 0.35}" r="3" fill="{TINT}"/>'
            f'<circle cx="{-r * 0.9}" cy="{r * 0.75}" r="2.5" fill="{MID}"/>'
            + _sparkle(r * 0.95, -r * 0.8, 7) + _sparkle(-r * 1.05, r * 0.15, 5, MID))


def _avatar(x, y, r, initials):
    return (f'<circle cx="{x}" cy="{y}" r="{r}" fill="#ffffff" stroke="{TINT_EDGE}" stroke-width="2"/>'
            f'<text x="{x}" y="{y + r * 0.3}" font-size="{r * 0.8:.0f}" font-weight="700" fill="{BLUE}" text-anchor="middle">{initials}</text>')


def _badge(x, y, fill, glyph):
    return (f'<circle cx="{x}" cy="{y}" r="15" fill="{fill}" stroke="#ffffff" stroke-width="3"/>'
            f'<text x="{x}" y="{y + 6}" font-size="17" font-weight="800" fill="#ffffff" text-anchor="middle">{glyph}</text>')


ILLOS = {
    "empty-files": lambda: (
        _backdrop()
        + f'<g transform="translate(0,8)"><path d="M-30,-40 h40 l20,20 v60 h-60 z" fill="#ffffff" stroke="{TINT_EDGE}" stroke-width="2.5"/>'
          f'<path d="M10,-40 v20 h20" fill="none" stroke="{TINT_EDGE}" stroke-width="2.5"/></g>'
        + f'<path d="M0,30 V-14 M-12,-2 L0,-14 L12,-2" fill="none" stroke="{BLUE}" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>'),
    "nothing-shared": lambda: (
        _backdrop()
        + f'<path d="M-30,10 Q0,-40 30,10" fill="none" stroke="{BLUE}" stroke-width="2.5" stroke-dasharray="5 6" stroke-linecap="round"/>'
        + f'<g transform="translate(0,-26) rotate(-6)"><path d="M-12,-15 h16 l8,8 v22 h-24 z" fill="#ffffff" stroke="{TINT_EDGE}" stroke-width="2"/>'
          f'<path d="M4,-15 v8 h8" fill="none" stroke="{TINT_EDGE}" stroke-width="2"/></g>'
        + _avatar(-38, 22, 20, "KA") + _avatar(38, 22, 20, "AL")),
    "no-results": lambda: (
        _backdrop()
        + f'<rect x="-46" y="-34" width="44" height="56" rx="5" fill="#ffffff" stroke="{MID}" stroke-width="2" transform="rotate(-10)"/>'
        + f'<line x1="18" y1="20" x2="44" y2="46" stroke="{BLUE}" stroke-width="11" stroke-linecap="round"/>'
        + f'<circle cx="0" cy="-2" r="30" fill="#ffffff" stroke="{BLUE}" stroke-width="7"/>'
        + f'<text x="0" y="9" font-size="30" font-weight="800" fill="{TINT_EDGE}" text-anchor="middle">?</text>'),
    "no-links": lambda: (
        _backdrop()
        + f'<g transform="rotate(-38)"><rect x="-50" y="-15" width="58" height="30" rx="15" fill="none" stroke="{TINT_EDGE}" stroke-width="8"/>'
          f'<rect x="-8" y="-15" width="58" height="30" rx="15" fill="none" stroke="{BLUE}" stroke-width="8"/></g>'
        + _sparkle(34, 30, 6, BLUE)),
    "load-error": lambda: (
        _backdrop()
        + f'<g transform="scale(0.86)"><path d="M-42,26 a22,22 0 0 1 0,-44 a30,30 0 0 1 56,-8 a24,24 0 0 1 14,52 z" fill="#ffffff" stroke="{TINT_EDGE}" stroke-width="3"/>'
          f'<path d="M-6,-6 l-10,16 h12 l-8,16" fill="none" stroke="{WARM}" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/></g>'
        + _badge(34, 26, DANGER, "!")),
    "opening": lambda: (
        _backdrop()
        + f'<g transform="rotate(-38)"><rect x="-50" y="-15" width="58" height="30" rx="15" fill="none" stroke="{TINT_EDGE}" stroke-width="8"/>'
          f'<rect x="-8" y="-15" width="58" height="30" rx="15" fill="none" stroke="{BLUE}" stroke-width="8"/></g>'
        + f'<circle cx="36" cy="30" r="15" fill="#ffffff" stroke="{SEL}" stroke-width="4"/>'
          f'<path d="M36,15 a15,15 0 0 1 15,15" fill="none" stroke="{BLUE}" stroke-width="4" stroke-linecap="round"/>'),
    "shared-by-me": lambda: (
        _backdrop()
        + f'<path d="M-6,-22 Q30,-40 40,-2" fill="none" stroke="{BLUE}" stroke-width="2.5" stroke-dasharray="5 6" stroke-linecap="round"/>'
        + f'<g transform="translate(-22,6) rotate(-6)"><path d="M-22,-30 h30 l14,14 v46 h-44 z" fill="#ffffff" stroke="{TINT_EDGE}" stroke-width="2.5"/>'
          f'<path d="M8,-30 v14 h14" fill="none" stroke="{TINT_EDGE}" stroke-width="2.5"/>'
          f'<rect x="-14" y="-4" width="26" height="4" rx="2" fill="{MID}"/><rect x="-14" y="6" width="18" height="4" rx="2" fill="{MID}"/></g>'
        + _avatar(42, 18, 18, "?")),
    "broken-link": lambda: (
        _backdrop()
        + f'<g transform="rotate(-38)"><rect x="-58" y="-15" width="52" height="30" rx="15" fill="none" stroke="{TINT_EDGE}" stroke-width="8"/>'
          f'<rect x="6" y="-15" width="52" height="30" rx="15" fill="none" stroke="{BLUE}" stroke-width="8"/></g>'
        + f'<path d="M-6,-30 l-4,-10 M4,-28 l4,-10 M-8,30 l-4,10 M6,30 l4,10" stroke="{WARM}" stroke-width="3.5" stroke-linecap="round"/>'),
    "expired": lambda: (
        _backdrop()
        + f'<path d="M-24,-40 C-24,-10 -5,-6 -5,0 C-5,6 -24,10 -24,40 H24 C24,10 5,6 5,0 C5,-6 24,-10 24,-40 Z" fill="#ffffff" stroke="{TINT_EDGE}" stroke-width="3"/>'
        + f'<path d="M-15,-28 H15 C13,-15 4,-9 0,-5 C-4,-9 -13,-15 -15,-28 Z" fill="{WARM}"/>'
        + f'<path d="M-17,37 C-9,22 9,22 17,37 Z" fill="{WARM}"/>'
        + f'<rect x="-32" y="-48" width="64" height="9" rx="4.5" fill="{BLUE}"/><rect x="-32" y="39" width="64" height="9" rx="4.5" fill="{BLUE}"/>'),
}


def illo(c, kind, cx, cy, s=1.0):
    c.o.append(f'<g transform="translate({cx},{cy}) scale({s})">{ILLOS[kind]()}</g>')


def hero(c, cx, cy, s=1.0):
    """Landing illustration: a shared file, the people it's shared with, and a link."""
    body = (f'<circle r="150" fill="{BLUE_SOFT}"/><circle cx="-110" cy="-96" r="7" fill="{TINT}"/><circle cx="146" cy="10" r="5" fill="{TINT}"/>'
            + _sparkle(120, -110, 10) + _sparkle(-136, 40, 7, MID) + _sparkle(70, 128, 6, BLUE)
            + f'<path d="M-96,-70 Q-60,-30 -40,-20 M96,-74 Q64,-34 44,-22 M100,70 Q60,50 46,34" fill="none" stroke="{BLUE}" stroke-width="2.5" stroke-dasharray="5 7" stroke-linecap="round"/>'
            + f'<g transform="translate(0,6) rotate(-4)"><rect x="-62" y="-80" width="124" height="160" rx="10" fill="#ffffff" stroke="{TINT_EDGE}" stroke-width="2.5"/>'
              f'<rect x="-62" y="-80" width="124" height="38" rx="10" fill="{BLUE_SOFT}"/><rect x="-62" y="-52" width="124" height="10" fill="{BLUE_SOFT}"/>'
              f'<text x="-44" y="-55" font-size="15" font-weight="800" fill="{BLUE}">XLS</text>'
              + "".join(f'<rect x="-44" y="{-24 + i * 22}" width="{w}" height="9" rx="4.5" fill="{MID}"/>' for i, w in enumerate([88, 64, 80, 52]))
              + f'<rect x="-44" y="64" width="40" height="6" rx="3" fill="{SEL}"/></g>' 
            + _avatar(-104, -80, 26, "KA") + _avatar(104, -84, 26, "JO") + _avatar(108, 78, 24, "DA")
            + f'<g transform="translate(-112,84)"><rect x="-50" y="-17" width="100" height="34" rx="17" fill="#ffffff" stroke="{TINT_EDGE}" stroke-width="2"/>'
              f'<g transform="translate(-28,0) rotate(-38)"><rect x="-11" y="-5" width="13" height="10" rx="5" fill="none" stroke="{BLUE}" stroke-width="2.6"/>'
              f'<rect x="-2" y="-5" width="13" height="10" rx="5" fill="none" stroke="{BLUE}" stroke-width="2.6"/></g>'
              f'<text x="12" y="5" font-size="13" font-weight="700" fill="{INK}" text-anchor="middle">Dec 24</text></g>')
    c.o.append(f'<g transform="translate({cx},{cy}) scale({s})">{body}</g>')


# ---------- state widgets ----------

def shadow(c, x, y, w, h, r):
    for spread, op in ((14, 0.04), (6, 0.06)):
        c.rect(x - spread / 2, y - spread / 4 + 4, w + spread, h + spread / 2, fill=INK, stroke=None, r=r + spread / 2, opacity=op)


def skel(c, x, y, w, h=10):
    c.rect(x, y, w, h, fill=SKEL, stroke=None, r=h / 2)


def check_badge(c, cx, cy, r=9):
    c.circle(cx, cy, r, fill=BLUE, stroke="none")
    c.o.append(f'<path d="M{cx-4},{cy} l3,3 l5,-6" fill="none" stroke="#fff" stroke-width="2" stroke-linecap="round"/>')


def alert_badge(c, cx, cy, r=9):
    c.circle(cx, cy, r, fill=DANGER, stroke="none")
    c.text(cx, cy + 4.5, "!", 13, 800, "#ffffff", "middle")


UPLOADS = [("XLSX", "Q1 Budget.xlsx", "done", "197 KB"),
           ("PDF", "Brand brief v2.pdf", 0.64, "1.2 of 1.9 MB"),
           ("EXE", "setup.exe", "error", "Files of type .exe can't be uploaded.")]


def panel_row_h(state):
    return 74 if isinstance(state, float) else 58


def panel_h(rows):
    return 56 + sum(panel_row_h(st) for _, _, st, _ in rows) + 4


def upload_panel(c, x, y, w, rows=UPLOADS, title="Uploading 1 file"):
    h = panel_h(rows)
    shadow(c, x, y, w, h, 12)
    c.rect(x, y, w, h, fill="#ffffff", stroke=LINE, r=12)
    c.text(x + 18, y + 31, title, 14, 700, INK)
    c.o.append(f'<path d="M{x+w-58},{y+22} l5,5 l5,-5" fill="none" stroke="{MUTED}" stroke-width="1.6" stroke-linecap="round"/>')
    x_icon(c, x + w - 24, y + 26, MUTED, 4.5)
    c.line(x, y + 48, x + w, y + 48, SEL)
    ry = y + 56
    for tag, name, state, detail in rows:
        icon_file(c, x + 18, ry + 10, tag[:3])
        c.text(x + 52, ry + 22, fit(name, w - 120, 13), 13, 500, INK)
        if state == "done":
            c.text(x + 52, ry + 40, detail, 12, 400, MUTED)
            check_badge(c, x + w - 28, ry + 24)
        elif state == "error":
            c.text(x + 52, ry + 40, fit(detail, w - 100, 12), 12, 500, DANGER)
            alert_badge(c, x + w - 28, ry + 24)
        else:
            bw = w - 52 - 60
            c.rect(x + 52, ry + 32, bw, 6, fill=SEL, stroke=None, r=3)
            c.rect(x + 52, ry + 32, bw * state, 6, fill=BLUE, stroke=None, r=3)
            c.text(x + 52 + bw, ry + 22, f"{state:.0%}", 12, 600, BLUE, "end")
            c.text(x + 52, ry + 54, detail, 11, 400, MUTED)
            x_icon(c, x + w - 28, ry + 26, MUTED, 4)
        ry += panel_row_h(state)
    return y + h


def confirm_h(lines):
    return 124 + (len(lines) - 1) * 20 + 80


def confirm_card(c, x, y, w, title, lines, action, glyph="delete", danger=True, h=None):
    h = h or confirm_h(lines)
    c.rect(x, y, w, h, fill="#ffffff", stroke=LINE, r=12)
    c.circle(x + 44, y + 44, 20, fill=RED_SOFT if danger else BLUE_SOFT, stroke="none")
    icon(c, glyph, x + 34, y + 34, DANGER if danger else BLUE)
    c.text(x + 24, y + 98, title, 17, 700, INK)
    for i, l in enumerate(lines):
        c.text(x + 24, y + 124 + i * 20, l, 13, 400, MUTED)
    by = y + h - 58
    aw = tw(action, 13) + 36
    button(c, x + w - 24 - aw, by, aw, action, "danger" if danger else "primary")
    button(c, x + w - 24 - aw - 10 - 88, by, 88, "Cancel")
    return h


def confirm_modal(c, w, title, lines, action, glyph="delete"):
    c.rect(0, 30, c.w, c.h - 30, fill=INK, stroke="none", r=0, opacity=0.35)
    h = confirm_h(lines)
    x, y = (c.w - w) / 2, (c.h - h) / 2 + 10
    shadow(c, x, y, w, h, 12)
    confirm_card(c, x, y, w, title, lines, action, glyph)


def m_confirm(c, title, lines, action, glyph="delete"):
    """The app's own dialog card, as on desktop, sized for a phone."""
    c.rect(0, 0, MW, MH, fill=INK, stroke=None, r=0, opacity=0.35)
    h = confirm_h(lines)
    y = (MH - h) / 2
    shadow(c, 16, y, MW - 32, h, 12)
    confirm_card(c, 16, y, MW - 32, title, lines, action, glyph)


def m_alert(c, title, lines, action, top_dim=MH):
    c.rect(0, 0, MW, top_dim, fill=INK, stroke=None, r=0, opacity=0.4)
    w = 286
    h = 66 + len(lines) * 18 + 56
    x, y = (MW - w) / 2, (MH - h) / 2 - 10
    c.rect(x, y, w, h, fill="#f7f8fa", stroke=None, r=16)
    c.text(MW / 2, y + 34, title, 16, 700, INK, "middle")
    for i, l in enumerate(lines):
        c.text(MW / 2, y + 58 + i * 18, l, 13, 400, MUTED, "middle")
    by = y + h - 50
    c.line(x, by, x + w, by, LINE)
    c.line(MW / 2, by, MW / 2, y + h, LINE)
    c.text(x + w / 4, by + 31, "Cancel", 16, 500, BLUE, "middle")
    c.text(x + 3 * w / 4, by + 31, action, 16, 700, DANGER, "middle")


def state_card(c, x, y, w, h, kind, title, lines, actions=()):
    c.rect(x, y, w, h, fill="#ffffff", stroke=LINE, r=12)
    illo(c, kind, x + w / 2, y + 76, 0.74)
    c.text(x + w / 2, y + 156, title, 15, 700, INK, "middle")
    for i, l in enumerate(lines):
        c.text(x + w / 2, y + 180 + i * 19, l, 13, 400, MUTED, "middle")
    state_buttons(c, x + w / 2, y + 180 + (len(lines) - 1) * 19 + 20, actions)


def state_buttons(c, cx, y, actions, h=34):
    widths = [tw(a, 13) + 40 for a, _ in actions]
    bx = cx - (sum(widths) + 10 * (len(actions) - 1)) / 2
    for (label, kind), bw in zip(actions, widths):
        button(c, bx, y, bw, label, kind, h)
        bx += bw + 10


def sheet_label(c, x, y, t):
    c.text(x, y, t.upper(), 11, 700, MUTED)


def toast(c, cx, y, message, action="Dismiss"):
    w = tw(message, 13) + tw(action, 13) + 92
    x = cx - w / 2
    shadow(c, x, y, w, 46, 10)
    c.rect(x, y, w, 46, fill=INK, stroke=None, r=10)
    alert_badge(c, x + 24, y + 23)
    c.text(x + 44, y + 28, message, 13, 500, "#ffffff")
    c.text(x + w - 18, y + 28, action, 13, 700, "#9ec5ff", "end")


# ---------- state screens ----------

def s_upload():
    c = C()
    rows = OWNER_ROWS[:3] + [{"kind": "file", "tag": "XLS", "name": "Q1 Budget.xlsx", "cells": ["11/5/2026 11:02AM", "1 member"]}] + OWNER_ROWS[3:]
    files_base(c, rows)
    upload_panel(c, CX + 536, 376, CW - 536)
    return c


def s_rename():
    c = C()
    rows = [dict(r) for r in OWNER_ROWS]
    rows[3]["selected"] = True
    files_base(c, rows)
    x, y = modal(c, 440, 232, "Rename")
    field(c, x, y + 26, 392, "Name", "Staff review.docx", error="A file named Staff review.docx already exists.", h=38)
    footer(c, x, y + 108, 392, "Rename")
    return c


def s_confirm_delete():
    c = C()
    rows = [dict(r) for r in OWNER_ROWS]
    rows[3]["selected"] = True
    files_base(c, rows)
    confirm_modal(c, 440, "Delete “Q4 Budget.xls”?", ["It's deleted for everyone. This can't be undone."], "Delete")
    return c


def s_confirmations():
    c = C()
    c.rect(0, 0, W, H, fill=FILL, stroke=None, r=0)
    cards = [("Replace", "Replace the contents of “Q4 Budget.xls”?", ["The current contents are deleted for everyone."], "Replace", "replace"),
             ("Remove my access", "Remove “Brand guide.pdf”?", ["It leaves your list. You get it back if it's shared", "again or you open a link to it."],
              "Remove", "leave"),
             ("Delete a link", "Delete this link?", ["It stops working, and 3 people lose the", "access it gave."],
              "Delete link", "delete")]
    w, gap = 456, 24
    for i, (label, title, lines, action, glyph) in enumerate(cards):
        x, y = CX + (i % 2) * (w + gap), 72 + (i // 2) * 290
        row = cards[i - i % 2:i - i % 2 + 2]
        sheet_label(c, x, y - 16, label)
        confirm_card(c, x, y, w, title, lines, action, glyph, h=max(confirm_h(cd[2]) for cd in row))
    return c


def state_grid(c, cards, cols=3):
    c.rect(0, 0, W, H, fill=FILL, stroke=None, r=0)
    gap, h = (24, 270) if cols == 3 else (16, 270)
    w = (CW - gap * (cols - 1)) / cols
    last = len(cards) - len(cards) % cols if len(cards) % cols else len(cards)
    for i, (kind, title, lines, actions) in enumerate(cards):
        x, y = CX + (i % cols) * (w + gap), 48 + (i // cols) * (h + gap)
        if i >= last:
            x += (cols - len(cards) % cols) * (w + gap) / 2
        state_card(c, x, y, w, h, kind, title, lines, actions)
    return c


def s_empty():
    return state_grid(C(), [
        ("empty-files", "No files yet", ["Drop files here, or use Upload."], [("Upload", "primary")]),
        ("nothing-shared", "Nothing shared with you yet", ["Files people share with you", "show up here."], []),
        ("shared-by-me", "You haven't shared anything", ["Files you share with people", "show up here."], []),
        ("no-results", "No matches for “brdget”", ["Check the spelling, or search", "with fewer letters."], []),
        ("no-links", "No links yet", ["Create a link to let anyone", "signed in open this file."], [("+  Create link", "primary")])])


def s_loading():
    c = C()
    shell(c, "Files", [], "openbox.app/files")
    skel(c, CX, 110, 120, 18)
    c.rect(CX + CW - 96, 106, 96, 34, fill=SKEL, stroke=None, r=6)
    c.line(CX, 190, CX + CW, 190)
    for i, (nw, mw) in enumerate([(180, 110), (240, 90), (150, 120), (210, 100), (170, 80), (230, 110)]):
        ry = 190 + i * 46
        c.rect(CX, ry + 12, 22, 22, fill=SKEL, stroke=None, r=4)
        skel(c, CX + 34, ry + 18, nw)
        skel(c, CX + 550, ry + 18, mw)
        skel(c, CX + 790, ry + 18, 70)
        c.line(CX, ry + 46, CX + CW, ry + 46, SEL)
    for label, x in [("Name", CX), ("Modified", CX + 550), ("Members", CX + 790)]:
        c.text(x, 178, label, 12, 600, MUTED)
    return c


def s_errors():
    return state_grid(C(), [
        ("load-error", "Couldn't load your files", ["Check your connection", "and try again."], [("Try again", "primary")]),
        ("expired", "This link has expired", ["Ask the person who sent", "it for a new one."], [("Go to Files", "secondary")]),
        ("broken-link", "This link was deleted", ["Ask the person who sent", "it for a new one."], [("Go to Files", "secondary")]),
        ("no-results", "This link doesn't exist", ["The address is incomplete,", "or its file was deleted."], [("Go to Files", "secondary")])], cols=2)


def s_action_errors():
    c = C()
    files_base(c, OWNER_ROWS[1:])
    toast(c, CX + CW / 2, H - 82, "Couldn't delete Campaign plan.pdf. It no longer exists.")
    return c


def m_state(c, kind, title, lines, actions, cy=360):
    illo(c, kind, MW / 2, cy, 1.0)
    c.text(MW / 2, cy + 110, title, 18, 700, INK, "middle")
    for i, l in enumerate(lines):
        c.text(MW / 2, cy + 136 + i * 20, l, 14, 400, MUTED, "middle")
    if actions:
        state_buttons(c, MW / 2, cy + 136 + len(lines) * 20 + 14, actions, h=42)


def m_progress_sheet(c, title, rows):
    """Phone version of the progress panel: a bottom sheet with large rows, above the tab bar."""
    c.rect(0, 0, MW, MH - 64, fill=INK, stroke=None, r=0, opacity=0.35)
    rh = 72
    y = 196 + 3 * 64          # top edge on a row divider
    h = MH - 64 - y
    c.rect(0, y, MW, h, fill="#ffffff", stroke=None, r=24)
    c.rect(0, y + h - 24, MW, 24, fill="#ffffff", stroke=None, r=0)
    c.line(0, MH - 64, MW, MH - 64, LINE)
    c.rect(MW / 2 - 20, y + 10, 40, 4, fill=LINE, stroke=None, r=2)
    c.text(20, y + 50, title, 17, 700, INK)
    c.text(MW - 20, y + 50, "Hide", 15, 600, BLUE, "end")
    ry = y + 76
    for tag, name, state, detail in rows:
        c.line(20, ry, MW, ry, SEL)
        icon_file(c, 22, ry + 20, tag[:3])
        c.text(58, ry + 30, fit(name, MW - 140, 15), 15, 500, INK)
        if state == "done":
            c.text(58, ry + 52, detail, 13, 400, MUTED)
            check_badge(c, MW - 32, ry + 36, 11)
        elif state == "error":
            c.text(58, ry + 52, fit(detail, MW - 110, 13), 13, 500, DANGER)
            alert_badge(c, MW - 32, ry + 36, 11)
        else:
            bw = MW - 58 - 92
            c.rect(58, ry + 42, bw, 6, fill=SEL, stroke=None, r=3)
            c.rect(58, ry + 42, bw * state, 6, fill=BLUE, stroke=None, r=3)
            c.text(58, ry + 64, f"{detail} · {state:.0%}", 12, 400, MUTED)
            c.text(MW - 20, ry + 41, "Cancel", 14, 600, BLUE, "end")
        ry += rh


def m_upload():
    c = C(MW, MH, clip_r=28)
    m_files_base(c, rows=M_OWNER_ROWS[:3] + [{"kind": "file", "tag": "XLS", "name": "Q1 Budget.xlsx", "sub": "11/5/2026 · 1 member"}] + M_OWNER_ROWS[3:])
    m_progress_sheet(c, "Uploading 1 file", UPLOADS)
    return c


def m_rename():
    c = C(MW, MH, clip_r=28)
    m_page(c, "Rename")
    field(c, 20, 148, MW - 40, "Name", "Staff review.docx", error="A file named Staff review.docx already exists.", h=44)
    m_bottom_button(c, "Rename")
    return c


def m_confirm_delete():
    c = C(MW, MH, clip_r=28)
    m_files_base(c, selected=3)
    m_confirm(c, "Delete “Q4 Budget.xls”?", ["It's deleted for everyone.", "This can't be undone."], "Delete")
    return c


def m_confirmations():
    c = C(MW, MH, clip_r=28)
    m_shared_base(c, selected=0)
    m_confirm(c, "Remove “Brand guide.pdf”?", ["It leaves your list. You get it back if", "it's shared again or you open a link to it."], "Remove", "leave")
    return c


def m_empty():
    c = C(MW, MH, clip_r=28)
    phone(c)
    m_header(c)
    c.text(20, 124, "My files", 14, 600, INK)
    m_search(c, 140)
    m_state(c, "empty-files", "No files yet", ["Tap + to upload files."], [], cy=356)
    m_tabbar(c, "Files")
    return c


def m_loading():
    c = C(MW, MH, clip_r=28)
    phone(c)
    c.text(20, 82, "OpenBox", 20, 800, BLUE)
    m_state(c, "opening", "Opening the link", ["Adding the file to Shared with me."], [], cy=330)
    return c


def m_errors():
    c = C(MW, MH, clip_r=28)
    phone(c)
    c.text(20, 82, "OpenBox", 20, 800, BLUE)
    m_state(c, "expired", "This link has expired", ["Ask the person who sent it", "for a new one."], [("Go to Files", "secondary")], cy=330)
    return c


def m_action_errors():
    c = C(MW, MH, clip_r=28)
    m_files_base(c, rows=M_OWNER_ROWS[1:])
    toast(c, MW / 2, MH - 130, "Campaign plan.pdf no longer exists.", "OK")
    return c


SCREENS = {
    "screen-01-landing": ('Landing', s_landing, m_landing,
        "Signed-out home page."),
    "screen-02-sign-in": ('Sign in', s_sign_in, m_sign_in,
        "Cognito Managed Login with OpenBox branding. Sign-up (name, email, password) and the email code are Cognito's pages too, and so are their errors, such as a wrong password."),
    "screen-03-files-file": ('Files: file selected', s_files_file, m_files_file,
        "My files lists every file you own. Clicking a row selects that file, and only one file can be selected at a time. "
        "The selection opens a toolbar at the bottom (desktop) or an action sheet (mobile) with only the actions the file allows; "
        "clicking the row again clears it. On mobile, + opens Upload; ⋯ on a row opens the same sheet. The owner gets every action, and only the owner sees Share. Replace asks first, then uploads the new contents through the upload panel."),
    "screen-04-upload": ('Upload', s_upload, m_upload,
        "Upload opens the file picker; files can also be dropped on the list. Each file uploads on its own: finished files join the list, "
        "rejected ones show the reason, and the rest keep going. Type and size are checked against `upload_policy` before Start upload, "
        "so each rejected file gets its own reason. On mobile, progress shows in a bottom sheet above the tab bar. A failed or expired upload shows Try again. "
        "Cancel stops an upload; its reserved name frees up when it expires. While files are dragged over the list, it shows a dashed outline and “Drop to upload”."),
    "screen-05-rename": ('Rename', s_rename, m_rename,
        "Only the owner can rename a file. Rename opens a dialog filled with the current name. Empty names, names over 255 characters and names with / are caught as you type; "
        "a taken name is caught when the server answers."),
    "screen-06-confirm-delete": ('Confirm delete', s_confirm_delete, m_confirm_delete,
        "Delete always asks first and names the file. On mobile the same dialog fills the width."),
    "screen-07-shared-can-edit": ('Sharing: file you can edit', s_shared_can_edit, m_shared_can_edit,
        "Kate joined Q4 Budget.xls through a Can edit link. Files shared with you never show Share: only the owner can share a file. "
        "Shared by me shows Members instead of Owner."),
    "screen-08-shared-view-only": ('Sharing: view-only file', s_shared_view_only, m_shared_view_only,
        "Kate can only view Brand guide.pdf."),
    "screen-09-share-links": ('Share', s_share_links, m_share_links,
        "Share shows only on files you own, and lists the file's links: there is no list of people. Each link shows what it gives, when it expires and how many people joined through it. Delete removes the link and everyone who joined through it."),
    "screen-10-create-link": ('Create link', s_create_link, m_create_link,
        "Pick what the link allows and when it expires: 1 day, 7 days or 30 days from now, never, or the end of a chosen day in your time zone. "
        "Days before today can't be picked. View can't be unticked. On mobile, the date opens the app's own calendar sheet."),
    "screen-11-link-created": ('Link created', s_link_created, m_link_created,
        "Done (× on mobile) closes it; the link then shows in Share, without its URL."),
    "screen-12-confirmations": ('Other confirmations', s_confirmations, m_confirmations,
        "Replace, Remove my access and Delete link ask first too. On mobile each is the same dialog at full width. "
        "Delete a link names how many people still have access through it, and with none says only that it stops working."),
    "screen-13-search": ('Search', s_search, m_search_screen,
        "Typing 2+ characters replaces the list with matching names from your files and files shared with you. "
        "Owner shows whose file each result is; Budget 2027 draft.xlsx was shared with you, so it has no Share. Clearing the box goes back to the list you were in."),
    "screen-14-empty": ('Empty states', s_empty, m_empty,
        "Every list has an empty state: My files, Shared with me, Shared by me, search and Share. Upload shows only in My files."),
    "screen-15-loading": ('Loading', s_loading, m_loading,
        "Lists show placeholder rows until the first page arrives, and the Share dialog uses the same rows. Opening a share link shows the mobile page "
        "while it's redeemed; desktop shows the same in the page centre. A button that sends a request shows a spinner and ignores clicks until it answers. "
        "Scrolling to the end adds placeholder rows under the list; if that page fails, a Try again row replaces them, and after `invalid_after` the list reloads from the top."),
    "screen-16-errors": ('Page errors', s_errors, m_errors,
        "A failed load offers Try again. A link that expired, was deleted or was never valid says why and offers a way out."),
    "screen-17-action-errors": ('Action and input errors', s_action_errors, m_action_errors,
        "A failed action shows a toast naming the file, from its error message or the name the app already shows. Input errors show under the field. After a 401 the app signs in again and returns to the same page."),
}

def padded(svg, w, h, pad=28):
    """Wrap a screen in a white card with padding and a rounded border, so it reads as a figure on any background."""
    inner = svg[svg.index(">") + 1:svg.rindex("</svg>")]
    W2, H2 = w + 2 * pad, h + 2 * pad
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W2}" height="{H2}" viewBox="0 0 {W2} {H2}" font-family="{FONT}">'
            f'<rect width="{W2}" height="{H2}" rx="14" fill="#ffffff"/>'
            f'<svg x="{pad}" y="{pad}" width="{w}" height="{h}" viewBox="0 0 {w} {h}">{inner}</svg>'
            f'<rect x="{pad + 0.5}" y="{pad + 0.5}" width="{w - 1}" height="{h - 1}" rx="{28 if w == MW else 6}" fill="none" stroke="{LINE}"/>'
            "</svg>")


if __name__ == "__main__":
    here = Path(__file__).parent
    for old_svg in here.glob("*.svg"):
        old_svg.unlink()
    for key, (title, desktop, mobile, caption) in SCREENS.items():
        name = key.replace("screen-", "view-")
        (here / f"{name}-desktop.svg").write_text(padded(desktop().svg(), W, H))
        (here / f"{name}-mobile.svg").write_text(padded(mobile().svg(), MW, MH))
    print(len(SCREENS), "screens written (desktop + mobile)")
