#!/usr/bin/env python3
"""Rebrand v0.19.0 Rust source without changing upstream legal attribution."""
from __future__ import annotations
import argparse
import os
import re
from pathlib import Path

SKIP = {".git", "target", ".github", "node_modules"}
TEXT_SUFFIXES = {".rs", ".toml", ".json", ".json5", ".yaml", ".yml", ".md", ".txt", ".ron", ".xml", ".html", ".css", ".js", ".ts", ".tsx", ".jsx", ".sh", ".ps1", ".py", ".bat", ".cmd", ".desktop", ".rc", ".plist", ".svg", ".ini", ".cfg", ".conf", ".lock", ".wxs", ".iss", ".nsi", ".ftl", ".po", ".pot", ".properties"}
NAMES = (("PDFCRAFT", "DOCREVISOR"), ("PdfCraft", "DocRevisor"), ("Pdfcraft", "Docrevisor"), ("pdfcraft", "docrevisor"))
def is_legal(p):
    return p.name.upper().startswith(("LICENSE", "NOTICE", "COPYING", "COPYRIGHT", "OFL-", "AUTHORS", "CONTRIBUTORS"))
def walk(root):
    for parent, dirs, files in os.walk(root):
        dirs[:] = [d for d in dirs if d not in SKIP]
        for filename in files:
            yield Path(parent) / filename
def change(s):
    def replacement(m):
        word = m.group(0)
        if word.isupper():
            return "DOCREVISOR"
        if word.islower():
            return "docrevisor"
        return "DocRevisor"
    return re.sub(r"pdfcraft", replacement, s, flags=re.IGNORECASE)
def run(root):
    if not (root / "apps/pdfcraft/Cargo.toml").exists():
        raise RuntimeError("Expected v0.19.0 source tree (not a compiled ZIP)")
    changed = 0
    for p in walk(root):
        if p.is_symlink() or is_legal(p) or p.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            old = p.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            continue
        new = change(old)
        if old != new:
            p.write_text(new, encoding="utf-8", newline="")
            changed += 1
    renamed = 0
    paths = sorted([p for p in root.rglob("*") if not SKIP.intersection(p.relative_to(root).parts)], key=lambda p: len(p.parts), reverse=True)
    for p in paths:
        new_name = change(p.name)
        if p.name != new_name:
            p.rename(p.with_name(new_name))
            renamed += 1
    missing = [str(p) for p in (root / "apps/docrevisor/Cargo.toml", root / "apps/docrevisor-cli/Cargo.toml") if not p.exists()]
    if missing:
        raise RuntimeError("Renamed app entrypoints not found: " + str(missing))
    remains = []
    for p in walk(root):
        if is_legal(p) or p.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            s = p.read_text(encoding="utf-8")
        except (UnicodeError, OSError):
            continue
        if "pdfcraft" in s.lower():
            remains.append(str(p.relative_to(root)))
    if remains:
        raise RuntimeError("Residual source references: " + ", ".join(remains[:30]))
    print(f"Rebranded {changed} text files, renamed {renamed} paths; legal notices preserved.")
if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("source", type=Path)
    args = ap.parse_args()
    run(args.source.resolve())
