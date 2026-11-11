#!/usr/bin/env python3
"""Windows post-build smoke tests. Uses only Python stdlib; no device needed."""
from pathlib import Path
import subprocess
import tempfile
import json
import sys

def make_pdf(path, pages=2):
    objects = []
    def obj(data):
        objects.append(data)
        return len(objects)
    catalog = obj(b"<< /Type /Catalog /Pages 2 0 R >>")
    kids = " ".join(f"{i} 0 R" for i in range(4, 4 + 2 * pages, 2))
    obj(f"<< /Type /Pages /Kids [{kids}] /Count {pages} >>".encode())
    obj(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    for i in range(pages):
        pageid = 4 + 2*i
        streamid = pageid + 1
        obj(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents {streamid} 0 R >>".encode())
        stream = f"BT /F1 18 Tf 70 700 Td (DocRevisor test page {i+1}) Tj ET".encode()
        obj(b"<< /Length " + str(len(stream)).encode() + b" >>\nstream\n" + stream + b"\nendstream")
    data = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0]
    for i, v in enumerate(objects, 1):
        offsets.append(len(data))
        data += f"{i} 0 obj\n".encode() + v + b"\nendobj\n"
    start = len(data)
    data += f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode()
    for pos in offsets[1:]:
        data += f"{pos:010d} 00000 n \n".encode()
    data += f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{start}\n%%EOF\n".encode()
    path.write_bytes(data)

def main(exe):
    rows = []
    with tempfile.TemporaryDirectory() as temp:
        d=Path(temp)
        src=d/"input.pdf"
        make_pdf(src)
        def run(label,*args):
            cmd=[str(exe),*map(str,args)]
            p=subprocess.run(cmd, capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=90)
            rows.append({"test":label,"pass":p.returncode==0,"exit":p.returncode,"stderr":p.stderr[-500:]})
            if p.returncode != 0:
                raise RuntimeError(f"{label} failed: {p.stderr[-600:]} {p.stdout[-400:]}")
            return p.stdout
        out=run("help","--help")
        assert "docrevisor-cli" in out.lower(), out[:500]
        run("version","--version")
        summary=run("info","info",src)
        json.loads(summary)
        extracted=run("text","text",src)
        assert "DocRevisor test page 1" in extracted
        img=d/"page.png"
        run("render","render",src,"--page","1","--dpi","72","--out",img)
        assert img.is_file() and img.read_bytes()[:8]==b"\x89PNG\r\n\x1a\n"
        edited=d/"edit.pdf"
        run("edit","edit",src,"--out",edited,"--title","DocRevisor QA")
        assert edited.is_file()
        combined=d/"combine.pdf"
        run("combine","combine",src,src,"--out",combined)
        assert combined.is_file()
        extracted_pdf=d/"extract.pdf"
        run("extract","extract",src,"--pages","1","--out",extracted_pdf)
        assert extracted_pdf.is_file()
        split_dir=d/"split"
        split_dir.mkdir()
        run("split","split",src,"--every","1","--out-dir",split_dir)
        assert list(split_dir.glob("*.pdf"))
        run("audit","audit",src)
        run("check","check",src,"--timeout","30","--dpi","36")
        report=d/"regression-results.json"
        report.write_text(json.dumps({"passed":len(rows),"tests":rows},indent=2))
        print(report.read_text())
    return 0

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: smoke.py path/to/DocRevisor-cli.exe")
    raise SystemExit(main(Path(sys.argv[1]).resolve()))
