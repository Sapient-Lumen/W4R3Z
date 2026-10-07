#!/usr/bin/env python3
"""Create a new published entry directory with the enforced wiki-facing name.

Usage:
  python3 publishing/create_published_entry.py \
      --date 2026.03.16 \
      --title "Example Title" \
      --source series/synthesis/paper1_receipt_redaction_bounds/paper.tex
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import shutil
import sys

PREFIX = "Anonymity: "
DATE_RE = re.compile(r"^\d{4}\.\d{2}\.\d{2}$")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", required=True, help="Publish date in YYYY.MM.DD format")
    parser.add_argument("--title", required=True, help="Human title without the 'Anonymity: ' prefix")
    parser.add_argument("--source", required=True, help="Path to the source .tex file to freeze")
    parser.add_argument("--root", default=".", help="Repo root")
    args = parser.parse_args()

    root = pathlib.Path(args.root).resolve()
    src = (root / args.source).resolve()

    if not src.exists():
        print(f"error: source file does not exist: {src}", file=sys.stderr)
        return 1
    if src.suffix != ".tex":
        print(f"error: source must be a .tex file: {src}", file=sys.stderr)
        return 1

    if not DATE_RE.match(args.date):
        print(f"error: --date must be in YYYY.MM.DD format: {args.date}", file=sys.stderr)
        return 1
    if args.title.startswith(PREFIX):
        print('error: --title should not include the "Anonymity: " prefix', file=sys.stderr)
        return 1
    title = args.title.strip()
    if not title:
        print("error: --title may not be empty", file=sys.stderr)
        return 1

    dirname = f"{args.date} - {PREFIX}{title}"
    publish_dir = root / "published" / dirname
    tex_name = f"{dirname}.tex"
    target_tex = publish_dir / tex_name
    note_path = publish_dir / "SOURCE.md"
    metadata_path = publish_dir / "METADATA.json"

    if publish_dir.exists():
        print(f"error: published directory already exists: {publish_dir}", file=sys.stderr)
        return 1

    publish_dir.mkdir(parents=True)
    shutil.copy2(src, target_tex)
    note_path.write_text(
        "# Source freeze\n\n"
        f"- Frozen from: `{args.source}`\n"
        f"- Published name: `[[{dirname}]]`\n"
        "- Public label: `Anonymity`\n"
        "- Canonical artifact: `.tex`\n",
        encoding="utf-8",
    )

    metadata_path.write_text(
        json.dumps(
            {
                "published_name": dirname,
                "wikilink": f"[[{dirname}]]",
                "public_label": "Anonymity",
                "published_date": args.date,
                "source_tex": args.source,
                "canonical_artifact": tex_name,
            },
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    print(target_tex.relative_to(root))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
