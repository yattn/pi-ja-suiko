#!/usr/bin/env python3
"""Heuristic, non-authoritative checks for risky Japanese proofreading changes.

Only the Python standard library is required. No network, file writes, or
meaning-preservation claims are made by this script.
"""

from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

FENCES = re.compile(r"(?m)^\s*(`{3,}|~{3,})[^\n]*\n.*?^\s*(?:`{3,}|~{3,})\s*$", re.S | re.M)
INLINE_CODE = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")
NUMBERS = re.compile(
    r"(?<![A-Za-z_\d])(?:0[xX][0-9a-fA-F]+|\d+(?:\.\d+)?)"
    r"(?:[％%]|(?:ns|us|ms|s|Hz|kHz|MHz|GHz|KiB|MiB|GiB|KB|MB|GB|円|秒|分|時間|日|件|回|人))?"
)
HEADINGS = re.compile(r"^\s{0,3}(#{1,6})\s+(.*)\s*$", re.M)
JAPANESE_MARKERS = {
    "否定": ["しない", "できない", "してはならない", "禁止", "不可", "不要", "存在しない"],
    "義務": ["必要", "必須", "しなければならない", "すること", "すべき"],
    "条件": ["場合", "とき", "限り", "ただし", "のみ", "原則", "除く"],
    "留保": ["可能性", "場合がある", "おそれ", "推定", "想定", "約", "以上", "以下", "未満"],
}


def multiset_changes(old: list[str], new: list[str]) -> tuple[list[str], list[str]]:
    before, after = Counter(old), Counter(new)
    return list((before - after).elements()), list((after - before).elements())


def analyze(original: str, revised: str) -> list[dict[str, object]]:
    findings: list[dict[str, object]] = []

    def add(kind: str, message: str, before: list[str], after: list[str]) -> None:
        if before or after:
            findings.append({"category": kind, "message": message, "removed": before, "added": after})

    for name, regex in (
        ("fenced_code", FENCES),
        ("inline_code", INLINE_CODE),
        ("number", NUMBERS),
    ):
        b, a = multiset_changes(
            [match.group(0) if name == "fenced_code" else match.group(1) if name == "inline_code" else match.group(0) for match in regex.finditer(original)],
            [match.group(0) if name == "fenced_code" else match.group(1) if name == "inline_code" else match.group(0) for match in regex.finditer(revised)],
        )
        add(name, "原文と推敲案でトークンが異なります。意図した変更か確認してください。", b, a)

    before_heads = [len(level) for level, _ in HEADINGS.findall(original)]
    after_heads = [len(level) for level, _ in HEADINGS.findall(revised)]
    if before_heads != after_heads:
        findings.append({
            "category": "heading_structure",
            "message": "見出し数または階層が異なります。",
            "removed": before_heads,
            "added": after_heads,
        })

    for group, expressions in JAPANESE_MARKERS.items():
        changed = []
        for marker in expressions:
            b, a = original.count(marker), revised.count(marker)
            if b != a:
                changed.append(f"{marker}: {b}→{a}")
        if changed:
            findings.append({
                "category": f"markers_{group}",
                "message": "意味を左右しやすい表現の出現数が変わりました。言い換えが正しいか確認してください。",
                "removed": changed,
                "added": [],
            })
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path, help="UTF-8 original text")
    parser.add_argument("revised", type=Path, help="UTF-8 revised text")
    parser.add_argument("--json", action="store_true", help="Print JSON")
    parser.add_argument("--strict", action="store_true", help="Exit 2 when any finding exists")
    args = parser.parse_args()

    try:
        original = args.original.read_text(encoding="utf-8")
        revised = args.revised.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"read error: {exc}", file=sys.stderr)
        return 1

    findings = analyze(original, revised)
    if args.json:
        print(json.dumps({"findings": findings, "count": len(findings)}, ensure_ascii=False, indent=2))
    elif findings:
        for item in findings:
            print(f"[{item['category']}] {item['message']}")
            if item["removed"]:
                print(f"  removed/changed: {item['removed']}")
            if item["added"]:
                print(f"  added: {item['added']}")
        print(f"{len(findings)} possible risk(s); manual review required")
    else:
        print("No heuristic differences detected; semantic equivalence is NOT guaranteed.")
    return 2 if args.strict and findings else 0


if __name__ == "__main__":
    sys.exit(main())
