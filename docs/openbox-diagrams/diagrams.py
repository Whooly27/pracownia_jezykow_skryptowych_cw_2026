"""Draws the OpenBox sequence diagrams as SVGs with a white background.

Run: python3 diagrams.py   (writes one .svg per diagram next to this file)

Each diagram is a list of participants and steps:
  ("msg", from, to, label)     solid arrow (request)
  ("ret", from, to, label)     dashed arrow (response)
  ("open", kind, label)        start a "loop" / "alt" frame
  ("close",)                   end the frame
"""
from pathlib import Path
from xml.sax.saxutils import escape

FONT = "-apple-system, 'Segoe UI', Helvetica, Arial, sans-serif"
INK, MUTED, LINE = "#111827", "#6b7280", "#9ca3af"
BOX_FILL, BOX_STROKE = "#eef2ff", "#4f46e5"
FRAME_FILL, FRAME_STROKE = "#fffbeb", "#d97706"

DIAGRAMS = {
    "list-files-v1": (["Browser", "API", "Postgres"], [
        ("msg", 0, 1, "GET /files?limit=50"),
        ("msg", 1, 2, "read the user's first 50 files"),
        ("msg", 1, 1, "add the user's permissions to each file"),
        ("ret", 1, 0, "200 items, has_more"),
        ("msg", 0, 1, "GET /files?after={last file id}"),
        ("open", "alt", "after isn't in this list"),
        ("ret", 1, 0, "422 invalid_after"),
        ("close",),
        ("ret", 1, 0, "200 next 50 files, has_more"),
    ]),
    "upload-a-file-v4": (["Browser", "API", "Postgres", "Vercel Blob"], [
        ("msg", 0, 1, "POST /uploads {files}"),
        ("msg", 1, 2, "type allowed? size allowed? name free?"),
        ("msg", 1, 2, "save allowed files as pending"),
        ("ret", 1, 0, "201 uploads + errors for rejected files"),
        ("msg", 0, 3, "PUT the file's bytes to put_url"),
        ("open", "alt", "size or type differs from what was declared"),
        ("ret", 3, 0, "storage rejects the PUT"),
        ("close",),
        ("ret", 3, 0, "200"),
        ("msg", 0, 1, "POST /uploads/{upload id}/complete"),
        ("msg", 1, 3, "did the bytes arrive?"),
        ("open", "alt", "bytes missing, or started over 15 min ago"),
        ("ret", 1, 0, "409 upload_incomplete · 410 upload_expired"),
        ("close",),
        ("msg", 1, 2, "mark the file ready"),
        ("ret", 1, 0, "200 file"),
    ]),
    "download-a-file-v4": (["Browser", "API", "Postgres", "Vercel Blob"], [
        ("msg", 0, 1, "POST /files/{file id}/download"),
        ("msg", 1, 2, "can the user see the file?"),
        ("open", "alt", "file missing or not visible"),
        ("ret", 1, 0, "404 not_found"),
        ("close",),
        ("msg", 1, 1, "sign a storage URL for the file, valid 60 s"),
        ("ret", 1, 0, "200 {url, expires_at}"),
        ("msg", 0, 3, "GET url"),
        ("open", "alt", "url older than 60 s"),
        ("ret", 3, 0, "storage rejects the request"),
        ("close",),
        ("ret", 3, 0, "200 file bytes, saved as Q4 Budget.xls"),
    ]),
    "open-a-share-link-v6": (["Owner", "Recipient", "API", "Cognito", "Postgres"], [
        ("msg", 0, 2, "POST /files/{file id}/links {permissions, expires_at}"),
        ("open", "alt", "not the file's owner"),
        ("ret", 2, 0, "403 forbidden"),
        ("close",),
        ("msg", 2, 4, "save the link, store a hash of its token"),
        ("ret", 2, 0, "201 link with url (shown once)"),
        ("ret", 0, 1, "owner sends the url"),
        ("msg", 1, 2, "opens /links/{token} → POST /links/redeem"),
        ("open", "alt", "recipient not signed in"),
        ("ret", 2, 1, "401 unauthenticated"),
        ("msg", 1, 2, "GET /auth/login?return_to=/links/{token}"),
        ("ret", 2, 1, "302 to Cognito"),
        ("msg", 1, 3, "sign in or create an account"),
        ("ret", 3, 2, "GET /auth/callback"),
        ("ret", 2, 1, "session cookie, 302 to /links/{token}"),
        ("msg", 1, 2, "POST /links/redeem {token}"),
        ("close",),
        ("msg", 2, 4, "find the link by its token hash"),
        ("open", "alt", "unknown, expired or deleted link, or removed by the owner"),
        ("ret", 2, 1, "403 forbidden · 404 not_found · 410 link_expired · 410 link_deleted"),
        ("close",),
        ("msg", 2, 4, "give the recipient the link's permissions"),
        ("ret", 2, 1, "200 file → app opens Shared with me"),
    ]),
    "delete-files-v2": (["Browser", "API", "Postgres", "Vercel Blob"], [
        ("msg", 0, 0, "user confirms: deleted for everyone"),
        ("msg", 0, 1, "POST /files/delete {ids: [file ids]}"),
        ("msg", 1, 2, "delete allowed files and their grants"),
        ("msg", 1, 3, "remove their stored bytes"),
        ("ret", 1, 0, "200 deleted ids + per-item errors"),
    ]),
}


def text_w(s, size=13):
    return len(s) * size * 0.56


def layout(names, steps):
    box_w = [max(110, text_w(n, 14) + 32) for n in names]
    x = [0.0] * len(names)
    for i in range(1, len(names)):
        x[i] = x[i - 1] + (box_w[i - 1] + box_w[i]) / 2 + 40
    # Widen gaps until every label fits between its two lifelines.
    for _ in range(20):
        for s in steps:
            if s[0] not in ("msg", "ret"):
                continue
            a, b, label = s[1], s[2], s[3]
            need = text_w(label) + 40
            if a == b:
                if a + 1 < len(names):
                    gap = x[a + 1] - x[a]
                    if gap < need + 30:
                        for k in range(a + 1, len(names)):
                            x[k] += need + 30 - gap
                continue
            lo, hi = min(a, b), max(a, b)
            if x[hi] - x[lo] < need:
                extra = (need - (x[hi] - x[lo])) / (hi - lo)
                for k in range(lo + 1, len(names)):
                    x[k] += extra * min(k - lo, hi - lo)
    pad = 30 + box_w[0] / 2
    x = [v + pad for v in x]
    width = x[-1] + box_w[-1] / 2 + 30
    if any(s[0] in ("msg", "ret") and s[1] == s[2] == len(names) - 1 for s in steps):
        width += 260
    return x, box_w, width


def render(name, names, steps):
    x, box_w, width = layout(names, steps)
    top, box_h, row = 20, 40, 46
    y = top + box_h + 34
    body, frames, stack = [], [], []
    for s in steps:
        kind = s[0]
        if kind == "open":
            stack.append((s[1], s[2], y - 18, len(body)))
            y += 34
            continue
        if kind == "close":
            fk, fl, fy, _ = stack.pop()
            frames.append((fk, fl, fy, y - 20))
            y += 20
            continue
        a, b, label = s[1], s[2], s[3]
        dash = ' stroke-dasharray="5 4"' if kind == "ret" else ""
        if a == b:
            x0 = x[a]
            body.append(f'<path d="M{x0},{y} h36 v18 h-34" fill="none" stroke="{INK}" stroke-width="1.4"{dash} marker-end="url(#arrow)"/>')
            body.append(f'<text x="{x0 + 46}" y="{y + 13}" font-size="13" fill="{INK}">{escape(label)}</text>')
            y += row + 6
            continue
        x1, x2 = x[a], x[b]
        end = x2 - 4 if x2 > x1 else x2 + 4
        body.append(f'<line x1="{x1}" y1="{y}" x2="{end}" y2="{y}" stroke="{INK}" stroke-width="1.4"{dash} marker-end="url(#arrow)"/>')
        body.append(f'<text x="{(x1 + x2) / 2}" y="{y - 7}" font-size="13" fill="{INK}" text-anchor="middle">{escape(label)}</text>')
        y += row
    height = y + 4
    left, right = x[0] - box_w[0] / 2 + 6, x[-1] + box_w[-1] / 2 - 6
    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}" font-family="{FONT}">',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
        f'<path d="M0,0 L10,5 L0,10 z" fill="{INK}"/></marker></defs>',
        f'<rect width="100%" height="100%" fill="#ffffff"/>',
    ]
    for fk, fl, fy, fy2 in frames:
        out.append(f'<rect x="{left}" y="{fy}" width="{right - left}" height="{fy2 - fy}" fill="{FRAME_FILL}" stroke="{FRAME_STROKE}" stroke-width="1" rx="4"/>')
    for xi in x:
        out.append(f'<line x1="{xi}" y1="{top + box_h}" x2="{xi}" y2="{height - 4}" stroke="{LINE}" stroke-width="1" stroke-dasharray="3 4"/>')
    for fk, fl, fy, fy2 in frames:
        tab_w = text_w(f"{fk}  [{fl}]", 12) + 20
        out.append(f'<rect x="{left}" y="{fy}" width="{tab_w}" height="24" fill="{FRAME_FILL}" stroke="{FRAME_STROKE}" stroke-width="1" rx="4"/>')
        out.append(f'<text x="{left + 10}" y="{fy + 16}" font-size="12" font-weight="600" fill="{FRAME_STROKE}">{fk}  <tspan font-weight="400" fill="{MUTED}">[{escape(fl)}]</tspan></text>')
    for xi, w, n in zip(x, box_w, names):
        out.append(f'<rect x="{xi - w / 2}" y="{top}" width="{w}" height="{box_h}" rx="6" fill="{BOX_FILL}" stroke="{BOX_STROKE}" stroke-width="1.4"/>')
        out.append(f'<text x="{xi}" y="{top + 25}" font-size="14" font-weight="600" fill="{INK}" text-anchor="middle">{escape(n)}</text>')
    out += body
    out.append("</svg>")
    (Path(__file__).parent / f"{name}.svg").write_text("\n".join(out))


if __name__ == "__main__":
    for key, (names, steps) in DIAGRAMS.items():
        render(key, names, steps)
        print("wrote", key + ".svg")
