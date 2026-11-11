#!/usr/bin/env python3
"""Create neutral DocRevisor PDF icons without external Python packages."""
from pathlib import Path
import struct
import zlib
import sys

def png(n):
    p=bytearray()
    for y in range(n):
        for x in range(n):
            a=(x/n,y/n)
            bg=(26,39,67,255)
            # Rounded rectangle page with folded corner and teal content lines
            rect=.22*n<=x<.75*n and .12*n<=y<.86*n
            fold=.62*n<=x<.75*n and .12*n<=y<.27*n and x-y/n*.01>.63*n
            if rect:
                c=(243,247,251,255)
                if fold: c=(123,198,203,255)
                if .32*n<=y<.36*n or .43*n<=y<.47*n or .54*n<=y<.58*n:
                    if .31*n<=x<.65*n: c=(30,135,147,255)
            else: c=bg
            p.extend(c)
    raw=b''.join(b'\x00'+p[y*n*4:(y+1)*n*4] for y in range(n))
    def chunk(t,d):
        return struct.pack('>I',len(d))+t+d+struct.pack('>I',zlib.crc32(t+d)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',n,n,8,6,0,0,0))+chunk(b'IDAT',zlib.compress(raw,9))+chunk(b'IEND',b'')
def main(root):
    icon=root/'assets/app-icon'
    data=png(1024)
    (icon/'docrevisor-1024.png').write_bytes(data)
    path=icon/'hicolor/256x256/apps/ai.storyteller.docrevisor.png'
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_bytes(png(256))
    icon_128=icon/'hicolor/128x128/apps/ai.storyteller.docrevisor.png'
    icon_128.parent.mkdir(parents=True,exist_ok=True)
    icon_128.write_bytes(png(128))
    sizes=[16,32,48,256]
    chunks=[png(n) for n in sizes]
    head=struct.pack('<HHH',0,1,len(sizes))
    off=6+16*len(sizes)
    for n,d in zip(sizes,chunks):
        head+=struct.pack('<BBBBHHII',n if n<256 else 0,n if n<256 else 0,0,0,1,32,len(d),off)
        off+=len(d)
    for name in ['docrevisor.ico','docrevisor-document.ico']:
        (icon/name).write_bytes(head+b''.join(chunks))
    print('Generated custom DocRevisor icons')
if __name__=='__main__':
    main(Path(sys.argv[1]))
