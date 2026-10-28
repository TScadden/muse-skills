#!/usr/bin/env python3
"""pdfjson.py -- recover ESPN API JSON from a browser-saved PDF.

The browser task cannot return large JSON as text (get_text truncates at
~131k chars), so it saves the API page as PDF instead. This script
extracts the text with pdftotext, strips the PDF artifacts, and writes
clean validated JSON.

Artifacts handled:
  - Chrome JSON-viewer "Pretty-print" header repeated on every page
  - Form-feed (\\x0c) page-break characters inserted mid-string
  - Trailing whitespace per extracted line

Usage:
    .venv/bin/python pdfjson.py in.pdf out.json
Requires: pdftotext on PATH.
"""

import json
import os
import subprocess
import sys


def fail(msg):
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(1)


def main():
    if len(sys.argv) != 3:
        fail("usage: pdfjson.py in.pdf out.json")
    pdf_path, out_path = sys.argv[1], sys.argv[2]
    if not os.path.exists(pdf_path):
        fail(f"file not found: {pdf_path}")

    proc = subprocess.run(
        ["pdftotext", pdf_path, "-"],
        capture_output=True,
        text=True,
        timeout=300,
    )
    if proc.returncode != 0:
        fail(f"pdftotext failed: {proc.stderr.strip()[:200]}")

    text = proc.stdout.replace("Pretty-print", "")
    body = "".join(
        line.rstrip() for line in text.split("\n") if line.strip()
    ).replace("\x0c", "")

    try:
        data = json.loads(body)
    except json.JSONDecodeError as e:
        fail(f"extracted text is not valid JSON: {e}")

    with open(out_path, "w") as f:
        json.dump(data, f)
    print(f"OK: wrote {out_path} ({len(body)} chars, top keys: {list(data.keys())[:8]})")


if __name__ == "__main__":
    main()
