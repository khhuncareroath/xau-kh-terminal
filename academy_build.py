"""Builds the Academy chapter PDFs: academy_book/chNN.py -> academy_pdfs/chNN.pdf.
Images for {img:name} placeholders live in academy_book/img/chNN_name.png.
Usage: python academy_build.py            (all chapters that have content)
       python academy_build.py 1 2        (just these)"""
import glob
import importlib
import os
import sys

import academy_pdf

HERE = os.path.dirname(os.path.abspath(__file__))


def build(ch):
    c = importlib.import_module(f"academy_book.ch{ch:02d}").CH
    imgs = {os.path.basename(p)[5:-4]: p for p in glob.glob(os.path.join(HERE, "academy_book", "img", f"ch{ch:02d}_*.png"))}
    out = os.path.join(HERE, "academy_pdfs", f"ch{ch:02d}.pdf")
    academy_pdf.build(c, out, imgs)
    os.remove(out.replace(".pdf", ".html"))
    return out


if __name__ == "__main__":
    chs = [int(a) for a in sys.argv[1:]] or sorted(int(os.path.basename(p)[2:4]) for p in glob.glob(os.path.join(HERE, "academy_book", "ch[0-9][0-9].py")))
    for ch in chs:
        print("built", build(ch))
