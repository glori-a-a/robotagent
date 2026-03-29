"""Build results/report.html from samples.jsonl + summary.txt for easy screenshots."""
from __future__ import annotations

import html
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"


def main() -> int:
    jsonl = RESULTS / "samples.jsonl"
    summ = RESULTS / "summary.txt"
    out = RESULTS / "report.html"
    if not jsonl.is_file():
        print("Missing results/samples.jsonl — run scripts/collect_submission_results.py first.")
        return 1

    rows = []
    for line in jsonl.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))

    summary_html = ""
    if summ.is_file():
        summary_html = "<pre>" + html.escape(summ.read_text(encoding="utf-8")) + "</pre>"

    blocks = []
    for row in rows:
        q = html.escape(row.get("query", ""))
        blocks.append(f"<h2>Query: {q}</h2>")
        blocks.append("<table><tr><th>#</th><th>intent</th><th>function</th><th>func</th><th>status</th><th>frame (preview)</th></tr>")
        for i, ev in enumerate(row.get("responses") or []):
            frame = ev.get("frame") or ""
            if len(frame) > 120:
                frame = frame[:120] + "…"
            blocks.append(
                "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(
                    i,
                    html.escape(str(ev.get("intent", ""))),
                    html.escape(str(ev.get("function", ""))),
                    html.escape(str(ev.get("func", ""))),
                    html.escape(str(ev.get("status", ""))),
                    html.escape(frame),
                )
            )
        blocks.append("</table>")

    doc = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="utf-8"/>
<title>Robot agent — run report</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 2rem; max-width: 56rem; }}
h1 {{ font-size: 1.25rem; }}
h2 {{ font-size: 1rem; margin-top: 2rem; border-bottom: 1px solid #ccc; }}
table {{ border-collapse: collapse; width: 100%; font-size: 0.85rem; }}
th, td {{ border: 1px solid #ddd; padding: 0.35rem 0.5rem; text-align: left; vertical-align: top; }}
th {{ background: #f4f4f4; }}
pre {{ background: #f8f8f8; padding: 1rem; overflow: auto; font-size: 0.85rem; }}
.note {{ color: #555; font-size: 0.9rem; margin-bottom: 1.5rem; }}
</style>
</head>
<body>
<h1>Robot NLU agent — captured Socket.IO payloads</h1>
<p class="note">Open this file in a browser (double-click). Use Win+Shift+S or your OS screenshot tool to capture this page for your report.</p>
<h2>Summary</h2>
{summary_html}
{"".join(blocks)}
</body>
</html>"""

    out.write_text(doc, encoding="utf-8")
    print(f"Wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
