#!/usr/bin/env python3
"""Dong goi bai nop thanh mot file .zip (chay tu thu muc riscv32).

    python tools/package.py                      -> ../riscv32_nopbai.zip
    python tools/package.py -o D:/nop/nhom1.zip
"""
import argparse, os, zipfile

INCLUDE = ["README.md", "modules", "single", "pipeline", "tools", "asm", "c", "demo", "rom", "tests", "report"]
SKIP_DIRS = {"__pycache__", ".git"}
SKIP_FILES = {"_cpu_test_tmp.circ", "_imem_test_tmp.circ"}

ap = argparse.ArgumentParser()
ap.add_argument("-o", default=os.path.join("..", "riscv32_nopbai.zip"))
a = ap.parse_args()
n = 0
with zipfile.ZipFile(a.o, "w", zipfile.ZIP_DEFLATED) as z:
    for item in INCLUDE:
        if os.path.isfile(item):
            z.write(item, os.path.join("riscv32", item)); n += 1; continue
        if not os.path.isdir(item):
            print(f"  (bo qua: khong co {item})"); continue
        for root, dirs, files in os.walk(item):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for f in files:
                if f in SKIP_FILES or f.endswith(".pyc"): continue
                p = os.path.join(root, f)
                z.write(p, os.path.join("riscv32", p)); n += 1
print(f"Da dong goi {n} file vao {os.path.abspath(a.o)}")
