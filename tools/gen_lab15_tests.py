#!/usr/bin/env python3
# Lab 15 - sinh tests/memmap.txt (MemMap, to hop) va tests/io.txt (circuit IO, tuan tu)
#   python tools/gen_lab15_tests.py      (chay tu thu muc riscv32)
import random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rvsim import IO, is_io
random.seed(15)
M = 0xFFFFFFFF
H = lambda v: f"0x{v & M:08X}"
B = lambda v, n: format(v, f"0{n}b")

# ---------- MemMap: Addr[32] MemWrite MemRData[32] IORData[32] -> RamWE IOWrite RData[32] ----------
addrs = [0, 4, 0x100, 0xFFC, 0x1000, 0x7FFFFFFC, 0x7FFFFFFF, 0x80000000, 0x80000004, 0x80000008, 0x8000000C, 0xFFFFFFFC, 0xC0000000]
addrs += [random.getrandbits(32) for _ in range(40)]
rows = []
for a in addrs:
    for we in (0, 1):
        mr, ir = random.getrandbits(32), random.getrandbits(32)
        io = is_io(a)
        rows.append((a, we, mr, ir, int(we and not io), int(we and io), ir if io else mr))
with open("tests/memmap.txt", "w", newline="\n") as f:
    f.write("# Test vector MemMap (to hop). I/O khi Addr >= 0x80000000\n")
    f.write("Addr[32] MemWrite MemRData[32] IORData[32] RamWE IOWrite RData[32]\n")
    for r in rows: f.write(f"{H(r[0])} {r[1]} {H(r[2])} {H(r[3])} {r[4]} {r[5]} {H(r[6])}\n")
n_mm = len(rows)

# ---------- IO (tuan tu): Addr WData IOWrite SW[8] clk -> RData LED[8] HEX[32] TTYData[7] TTYWE ----------
rows = []
class T:
    def __init__(s, sid): s.io = IO(); s.set = sid; s.seq = 0
    def row(s, addr, wd, we, sw, clk):
        s.io.sw = sw; s.seq += 1
        k = (addr >> 2) & 3
        rows.append((s.set, s.seq, addr, wd, we, sw, clk, s.io.read(addr), s.io.led & 0xFF, s.io.hex, wd & 0x7F, int(we and k == 2)))
    def write(s, addr, wd, sw=0):
        s.row(addr, wd, 1, sw, 0); s.io.sw = sw; s.io.write(addr, wd); s.row(addr, wd, 1, sw, 1)
    def read(s, addr, sw=0):
        s.row(addr, 0, 0, sw, 0); s.row(addr, 0, 0, sw, 1)
t = T(1)                                       # Set 1: ghi/doc LED va HEX
t.read(0x80000000); t.read(0x80000004)
t.write(0x80000000, 0x000000A5); t.read(0x80000000)
t.write(0x80000004, 0x12345678); t.read(0x80000004); t.read(0x80000000)
t.write(0x80000000, 0xFFFFFF3C); t.read(0x80000000)
t.row(0x80000000, 0x99, 0, 0, 0); t.row(0x80000000, 0x99, 0, 0, 1)        # IOWrite = 0: khong ghi
t = T(2)                                       # Set 2: UART TX va SW
t.read(0x80000008)
for c in b"Hi!\n": t.write(0x80000008, c)
t.write(0x80000008, 0xFFFFFF41)
for sw in (0x00, 0x5A, 0xFF, 0x81): t.read(0x8000000C, sw)
t.write(0x8000000C, 0x1234, 0x0F); t.read(0x80000000); t.read(0x80000004)  # ghi vao SW: khong anh huong
t = T(3)                                       # Set 3: ngau nhien
for _ in range(60):
    a = 0x80000000 | (random.randrange(4) << 2)
    if random.random() < 0.5: t.write(a, random.getrandbits(32), random.getrandbits(8))
    else: t.read(a, random.getrandbits(8))
with open("tests/io.txt", "w", newline="\n") as f:
    f.write("# Test vector circuit IO (tuan tu). Addr[3:2]: 0 LED, 1 HEX, 2 UART TX (doc = 1), 3 SW\n")
    f.write("<set> <seq> Addr[32] WData[32] IOWrite SW[8] clk RData[32] LED[8] HEX[32] TTYData[7] TTYWE\n")
    for st, sq, a, wd, we, sw, c, rd, led, hx, td, twe in rows:
        f.write(f"{st} {sq} {H(a)} {H(wd)} {we} {B(sw,8)} {c} {H(rd)} {B(led,8)} {H(hx)} {B(td,7)} {twe}\n")
print(f"memmap: {n_mm} dong, io: {len(rows)} dong")
