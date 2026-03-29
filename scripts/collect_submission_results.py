"""
Collect Socket.IO responses for a fixed query list; write results for coursework submission.
Run from repository root: python scripts/collect_submission_results.py
Requires: Redis, 8007/8008/8009/8080 services, .env with ENTRY_URL and API credentials.
"""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "results"
sys.path.insert(0, str(ROOT))

os.chdir(ROOT)
from dotenv import load_dotenv  # noqa: E402

load_dotenv(ROOT / ".env")

import socketio  # noqa: E402

URL = os.environ.get("ENTRY_URL", "http://127.0.0.1:8080")

QUERIES = [
    "你好",
    "导航去充电站",
    "停下",
    "怎么抓取易碎物品",
    "扫描一下周围环境",
]


def main() -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    jsonl_path = RESULTS / "samples.jsonl"
    summary_path = RESULTS / "summary.txt"

    lines_out: list[str] = []
    summary_lines: list[str] = []

    for i, query in enumerate(QUERIES):
        events: list[dict] = []
        sio = socketio.Client(
            logger=False,
            engineio_logger=False,
            request_timeout=60,
        )

        @sio.on("request_nlu")
        def on_resp(data, bucket=events):
            p = json.loads(data) if isinstance(data, str) else dict(data)
            bucket.append(p)

        try:
            sio.connect(URL, wait_timeout=45)
        except Exception as e:
            summary_lines.append(f"FAIL connect {URL}: {e}")
            summary_lines.append("Start Redis, three infer services, and start.py, then retry.")
            summary_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
            print(summary_path.read_text(encoding="utf-8"))
            return 1

        payload = {
            "sender_id": f"submit{i}",
            "trace_id": f"s{i}",
            "query": query,
            "enable_dm": True,
        }
        sio.emit("request_nlu", json.dumps(payload, ensure_ascii=False))
        time.sleep(32)
        sio.disconnect()
        time.sleep(0.3)

        record = {"query": query, "responses": events}
        lines_out.append(json.dumps(record, ensure_ascii=False))

        merged = ""
        for ev in events:
            f = ev.get("frame")
            if isinstance(f, str) and f.strip():
                merged += f
        fn = None
        for ev in reversed(events):
            if ev.get("function"):
                fn = ev.get("function")
                break
        summary_lines.append(f"Q: {query}")
        summary_lines.append(f"  frames: {len(events)} last_function={fn!r}")
        if merged.strip():
            preview = merged.strip().replace("\n", " ")[:200]
            summary_lines.append(f"  chat_preview: {preview!r}")

    jsonl_path.write_text("\n".join(lines_out) + "\n", encoding="utf-8")
    summary_lines.append(f"Wrote {jsonl_path.name} ({len(lines_out)} queries).")
    summary_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")
    print(summary_path.read_text(encoding="utf-8"))

    import subprocess

    r = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / "build_results_report.py")],
        cwd=str(ROOT),
    )
    if r.returncode != 0:
        print("(report.html skipped — build_results_report failed)")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
