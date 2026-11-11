#!/usr/bin/env python3
"""Adapt only application-specific i18n catalogs; retain shared catalogs and license files."""
from pathlib import Path
import re
import sys

root = Path(sys.argv[1])
count = 0
for p in root.glob('locales/*/pdfcraft.tsv'):
    text = p.read_text(encoding='utf-8')
    def replace(m):
        s = m.group()
        return 'DOCREVISOR' if s.isupper() else 'docrevisor' if s.islower() else 'DocRevisor'
    text = re.sub('pdfcraft', replace, text, flags=re.IGNORECASE)
    target = p.with_name('docrevisor.tsv')
    target.write_text(text, encoding='utf-8')
    count += 1
if count == 0:
    raise RuntimeError('No original translation catalogs found')
print(f'Adapted {count} language catalogs')
