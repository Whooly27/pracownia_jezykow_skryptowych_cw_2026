"""Builds openbox-technical-specification.pdf from openbox-technical-specification.md.

Run: python3 build_spec_pdf.py
Needs Google Chrome (used headless to print the HTML to PDF). No Python packages needed.
"""
import html
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE = HERE / "openbox-technical-specification.md"
HTML_OUT = HERE / "openbox-technical-specification.html"
PDF_OUT = HERE / "openbox-technical-specification.pdf"
DATE = "7 November 2026"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

CSS = """
@page :first { margin: 0; }
@page { @bottom-right { content: counter(page); font: 8.5pt -apple-system, Helvetica, sans-serif; color: #7d8697; } }
@page :first { @bottom-right { content: none; } }
.cover { height: 297mm; box-sizing: border-box; padding: 70mm 22mm 0; break-after: page;
         background: linear-gradient(180deg, #ffffff 0%, #ffffff 62%, #eef4ff 62%, #eef4ff 100%); position: relative; }
.cover .brand { font-size: 15pt; font-weight: 800; color: #0061fe; letter-spacing: -0.01em; }
.cover-title { font-size: 34pt; line-height: 1.1; margin: 6mm 0 4mm; color: #1e2533; letter-spacing: -0.02em; }
.cover-sub { font-size: 13pt; color: #4b5466; margin: 0; }
.cover-date { position: absolute; left: 22mm; top: 200mm; font-size: 11pt; color: #4b5466; }
.toc { break-after: page; }
.toc-title { border: 0; margin: 0 0 4mm; font-size: 20pt; }
.toc-row { display: flex; align-items: baseline; gap: 2mm; color: #1e2533; text-decoration: none; padding: 0.6mm 0; }
.toc-row.l2 { font-weight: 700; font-size: 11.5pt; margin-top: 3mm; }
.toc-row.l3 { font-size: 9.5pt; padding-left: 6mm; color: #4b5466; }
.toc-row .dots { flex: 1; border-bottom: 1px dotted #c6ccd6; transform: translateY(-1mm); }
.toc-row .pg { font-variant-numeric: tabular-nums; min-width: 6mm; text-align: right; }
.toc-row code { background: none; padding: 0; font-size: inherit; }

@page { size: A4; margin: 18mm 16mm 18mm 16mm; }
* { box-sizing: border-box; }
html { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body { font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif; font-size: 10pt; line-height: 1.5; color: #1e2533; margin: 0; }
h1 { font-size: 24pt; margin: 0 0 4mm; color: #0061fe; letter-spacing: -0.01em; }
h1 + p { color: #6b7489; margin-top: 0; }
h2 { font-size: 15pt; margin: 9mm 0 3mm; padding-bottom: 1.5mm; border-bottom: 1px solid #d4d9e2; break-after: avoid; }
h2.page { break-before: page; margin-top: 0; }
h3 { font-size: 11.5pt; margin: 6mm 0 2mm; break-after: avoid; }
h3 code { font-size: 10pt; }
h4 { font-size: 11pt; margin: 8mm 0 1.5mm; padding-top: 4mm; border-top: 1px solid #eef1f5; break-after: avoid; }
h3 + h4, h3 + p + h4 { border-top: 0; padding-top: 0; margin-top: 3mm; }
h4 code { font-size: 9.6pt; background: #eef4ff; color: #0047bb; }
h4 + p { color: #4b5466; }
pre + table { margin-top: 1mm; }
p { margin: 0 0 2.5mm; }
ul { margin: 0 0 3mm; padding-left: 5mm; }
li { margin: 0 0 1mm; }
code { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 8.6pt; background: #f1f4f9; border-radius: 3px; padding: 0.3mm 1mm; }
pre { font-family: "SF Mono", Menlo, Consolas, monospace; font-size: 8pt; line-height: 1.45; background: #f6f8fb; border: 1px solid #e3e7ee;
      border-radius: 6px; padding: 3mm 3.5mm; margin: 0 0 4mm; white-space: pre-wrap; word-break: break-word; overflow-wrap: anywhere; }
pre code { background: none; padding: 0; font-size: inherit; }
pre .l { display: block; text-indent: -4ch; }
pre .c { color: #6b7489; }
table { width: 100%; border-collapse: collapse; margin: 0 0 4mm; font-size: 9pt; break-inside: avoid; }
th { text-align: left; font-weight: 600; color: #4b5466; background: #f6f8fb; }
th, td { border-bottom: 1px solid #e3e7ee; padding: 1.6mm 2.4mm; vertical-align: top; }
td code { white-space: nowrap; }
.status { margin: 3mm 0 1.5mm; break-after: avoid; }
.status strong code { background: #e8f0ff; color: #0047bb; font-weight: 600; }
figure { margin: 2mm 0 2mm; break-inside: avoid; }
figure img { width: 100%; display: block; }
.caption { color: #4b5466; font-size: 9pt; margin-bottom: 6mm; }
.screen { break-inside: avoid; margin-bottom: 7mm; }
.screen h3 { margin-top: 0; }
table.figures { table-layout: fixed; margin-top: 2mm; }
table.figures th { background: none; color: #6b7489; font-size: 8pt; letter-spacing: 0.06em; text-transform: uppercase; padding: 0 0 1.5mm; border: 0; }
table.figures th:first-child, table.figures td:first-child { width: 71%; padding-right: 4mm; }
table.figures td { border: 0; padding: 0; vertical-align: top; }
table.figures img { width: 100%; display: block; }
.status { break-after: avoid; }
pre { break-inside: avoid; }
pre.long { break-inside: auto; }
.tablewrap { break-inside: avoid; display: inline-block; width: 100%; vertical-align: top; }
pre + .tablewrap, pre + pre { break-before: avoid; }
.keep { break-inside: avoid; break-after: avoid; }
.together { break-inside: avoid; }
.mk { font-size: 1px; color: #ffffff; letter-spacing: 0; }
pre:has(+ .tablewrap) { break-after: avoid; }
h3 + .keep, h3 + p { break-before: avoid; }
table.errors { table-layout: fixed; }
table.errors th:nth-child(1) { width: 15%; }
table.errors th:nth-child(2) { width: 31%; }
"""


def inline(text):
    """Escape, then apply `code`, **bold** and *italic*."""
    parts = re.split(r"(`[^`]+`)", text)
    out = []
    for part in parts:
        if part.startswith("`") and part.endswith("`") and len(part) > 1:
            out.append(f"<code>{html.escape(part[1:-1]).replace('*', '&#42;')}</code>")
        else:
            out.append(html.escape(part))
    t = "".join(out)
    t = re.sub(r"!\[(.*?)\]\((.*?)\)", r'<img src="\2" alt="\1">', t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", t)
    return t


def code_block(lines):
    body = []
    for line in lines:
        indent = len(line) - len(line.lstrip(" "))
        line = line[indent:]
        esc = html.escape(line)
        # dim // comments (outside of strings, good enough for the examples)
        m = re.search(r'(^|\s)(//.*)$', line)
        if m and line.count('"', 0, m.start(2)) % 2 == 0:
            cut = len(html.escape(line[:m.start(2)]))
            esc = esc[:cut] + f'<span class="c">{esc[cut:]}</span>'
        body.append(f'<span class="l" style="padding-left:{indent + 4}ch">{esc or "&#8203;"}</span>')
    cls = ' class="long"' if len(lines) > 24 else ""
    return f"<pre{cls}><code>" + "".join(body) + "</code></pre>"


def table(rows):
    cells = [[c.strip() for c in r.strip().strip("|").split("|")] for r in rows]
    head, body = cells[0], cells[2:]
    th = "".join(f"<th>{inline(c)}</th>" for c in head)
    trs = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in body)
    cls = ' class="figures"' if any(c.startswith("![") for r in body for c in r) else (' class="errors"' if head[0] == "Status" else "")
    wrap_cls = "tablewrap figwrap" if "figures" in cls else "tablewrap"
    return f'<div class="{wrap_cls}"><table{cls}><thead><tr>{th}</tr></thead><tbody>{trs}</tbody></table></div>'


def group_endpoints(body, max_code_lines=44):
    """Keep a short endpoint (heading through status table) on one page."""
    start = re.compile(r'<div class="keep">\s*(?:<h3[^>]*>(?:(?!</h3>).)*</h3>\s*(?:<p>(?:(?!</p>).)*</p>\s*)?<div class="keep">\s*)?<h4>', re.S)
    starts, pos = [], 0
    for m in start.finditer(body):
        if m.start() >= pos:
            starts.append(m.start())
            pos = m.end()
    ends = starts[1:] + [len(body)]
    out, last = [], 0
    for a, b in zip(starts, ends):
        h2 = body.find("<h2", a, b)
        b = h2 if h2 != -1 else b
        chunk = body[a:b]
        out.append(body[last:a])
        # rough height in code lines: code, table rows and paragraphs
        code_lines = chunk.count('<span class="l"') + 2 * chunk.count("<tr") + 3 * chunk.count("<p>")
        out.append(f'<div class="together">{chunk}</div>' if code_lines <= max_code_lines else chunk)
        last = b
    out.append(body[last:])
    return "".join(out)


def convert(md):
    lines = md.replace("\\|", "&#124;").split("\n")
    out, i, section = [], 0, ""
    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            out.append(code_block(lines[i + 1:j]))
            i = j + 1
            continue
        if line.startswith("|"):
            j = i
            while j < len(lines) and lines[j].startswith("|"):
                j += 1
            out.append(table(lines[i:j]))
            i = j
            continue
        if line.startswith("- "):
            items = []
            while i < len(lines) and lines[i].startswith("- "):
                items.append(f"<li>{inline(lines[i][2:])}</li>")
                i += 1
            out.append("<ul>" + "".join(items) + "</ul>")
            continue
        m = re.match(r"!\[(.*?)\]\((.*?)\)", line)
        if m:
            out.append(f'<figure><img src="{html.escape(m.group(2))}" alt="{html.escape(m.group(1))}"></figure>')
            if section == "screens" and i + 2 < len(lines) and lines[i + 1] == "" and lines[i + 2] and not lines[i + 2].startswith("#"):
                out.append(f'<p class="caption">{inline(lines[i + 2])}</p>')
                i += 3
                continue
            i += 1
            continue
        if line.startswith("# "):
            pass  # the title lives on the cover page
        elif line.startswith("## "):
            title = line[3:]
            section = "screens" if "Screens" in title else ""
            cls = ' class="page"' if any(k in title for k in ("Flows", "Screens", "API")) else ""
            out.append(f'<h2{cls} id="{slug(title)}">{inline(title)}<span class="mk">@@{slug(title)}@@</span></h2>')
        elif line.startswith("#### "):
            out.append(f"<h4>{inline(line[5:])}</h4>")
        elif line.startswith("### "):
            out.append(f'<h3 id="{slug(line[4:])}">{inline(line[4:])}<span class="mk">@@{slug(line[4:])}@@</span></h3>')
        elif re.match(r"\*\*`\d{3} ", line) or line in ("**Request**", "**Query**"):
            out.append(f'<p class="status">{inline(line)}</p>')
        elif line.strip():
            out.append(f"<p>{inline(line)}</p>")
        i += 1
    body = "\n".join(out)
    # keep each endpoint heading with its description
    body = re.sub(r'(<h4>(?:(?!</h4>).)*</h4>\s*<p>(?:(?!</p>).)*</p>)', r'<div class="keep">\1</div>', body, flags=re.S)
    # keep a group heading and its intro with the first endpoint
    body = re.sub(r'(<h3[^>]*>(?:(?!</h3>).)*</h3>\s*(?:<p>(?:(?!</p>).)*</p>\s*)?<div class="keep">.*?</div>)',
                  r'<div class="keep">\1</div>', body, flags=re.S)
    # keep each screen's heading, figure and caption on one page
    body = re.sub(r'(<h3[^>]*>(?:(?!</h3>).)*</h3>\s*<p>(?:(?!</p>).)*</p>\s*<div class="tablewrap figwrap"><table class="figures">.*?</table></div>)',
                  r'<div class="screen">\1</div>', body, flags=re.S)
    # keep each flow's heading, description and diagram together
    body = re.sub(r'(<h3[^>]*>(?:(?!</h3>).)*</h3>\s*<p>(?:(?!</p>).)*</p>\s*<figure>.*?</figure>)',
                  r'<div class="screen">\1</div>', body, flags=re.S)
    # keep a sentence that introduces a code block with that block
    body = re.sub(r'(<p>(?:(?!</p>).)*:</p>\s*<pre>.*?</pre>)', r'<div class="together">\1</div>', body, flags=re.S)
    body = group_endpoints(body)
    # draw every sequence diagram at the same scale
    widths = {p: float(re.search(r'width="([\d.]+)"', (HERE / p).read_text()).group(1))
              for p in set(re.findall(r'<img src="(openbox-diagrams/[^"]+)"', body))}
    if widths:
        widest = max(widths.values())
        body = re.sub(r'<img src="(openbox-diagrams/[^"]+)"',
                      lambda m: f'<img style="width: {100 * widths[m.group(1)] / widest:.1f}%" src="{m.group(1)}"', body)
    # keep an endpoint's last code block with its status table
    body = re.sub(r'(<pre><code>(?:(?!</pre>).)*</pre>\s*<div class="tablewrap">\s*<table class="errors">.*?</table>\s*</div>)',
                  lambda m: f'<div class="together">{m.group(1)}</div>' if m.group(1).count('<span class="l"') <= 20 else m.group(1),
                  body, flags=re.S)
    return body


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", re.sub(r"`", "", text).lower()).strip("-")


def toc_entries(md):
    """(level, title) for every ## and ### heading."""
    out = []
    for line in md.split("\n"):
        if line.startswith("## "):
            out.append((2, line[3:]))
        elif line.startswith("### "):
            out.append((3, line[4:]))
    return out


def plain(title):
    return re.sub(r"`", "", title)


def cover_and_toc(entries, pages):
    rows = []
    for (level, title), page in zip(entries, pages):
        rows.append(f'<a class="toc-row l{level}" href="#{slug(title)}"><span>{inline(title)}</span>'
                    f'<span class="dots"></span><span class="pg">{page or ""}</span></a>')
    return (f'''<section class="cover">
  <div class="brand">OpenBox</div>
  <h1 class="cover-title">Technical Specification</h1>
  <p class="cover-sub">Access model, flows, screens and HTTP API</p>
  <p class="cover-date">{DATE}</p>
</section>
<section class="toc"><h2 class="toc-title">Contents</h2>{"".join(rows)}</section>''')


def print_pdf(body):
    doc = f"<!doctype html><html><head><meta charset='utf-8'><title>OpenBox — Technical Specification</title><style>{CSS}</style></head><body>{body}</body></html>"
    HTML_OUT.write_text(doc)
    cmd = [CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--allow-file-access-from-files",
           f"--print-to-pdf={PDF_OUT}", HTML_OUT.as_uri()]
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    if result.returncode != 0 or not PDF_OUT.exists():
        sys.exit(f"Chrome failed:\n{result.stderr}")
    HTML_OUT.unlink(missing_ok=True)


def heading_pages(entries):
    """Find the page each heading lands on, using invisible markers next to each heading."""
    text = subprocess.run(["pdftotext", str(PDF_OUT), "-"], capture_output=True, text=True).stdout
    pages = text.split("\f")
    found = []
    for _, title in entries:
        mark = f"@@{slug(title)}@@"
        found.append(next((n + 1 for n, page in enumerate(pages) if mark in page.replace("\n", "")), None))
    return found


def main():
    md = SOURCE.read_text()
    entries = toc_entries(md)
    body = convert(md)
    pages = [None] * len(entries)
    for _ in range(2):          # second pass fills in real page numbers
        print_pdf(cover_and_toc(entries, pages) + body)
        pages = heading_pages(entries)
    print_pdf(cover_and_toc(entries, pages) + re.sub(r'<span class="mk">.*?</span>', '', body))   # final copy without markers
    missing = [plain(t) for (_, t), p in zip(entries, pages) if p is None]
    if missing:
        print("warning: no page found for", missing)
    print(f"wrote {PDF_OUT.name}")


if __name__ == "__main__":
    main()
