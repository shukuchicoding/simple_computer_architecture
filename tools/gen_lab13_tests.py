#!/usr/bin/env python3
# Lab 13 - sinh tests/loadext.txt, tests/storemerge.txt, tests/dmem.txt (DMEM co them chan funct3)
#   python tools/gen_lab13_tests.py      (chay tu thu muc riscv32)
import random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rvsim import mem_load, mem_store
random.seed(13)
M = 0xFFFFFFFF
H = lambda v: f"0x{v & M:08X}"
B = lambda v, n: format(v, f"0{n}b")
F3S = [0, 1, 2, 4, 5]                      # lb lh lw lbu lhu (cac gia tri hop le)
WORDS = [0x80FF7F01, 0x7F80FF00, 0xFFFFFFFF, 0x00000000, 0x12345678, 0xDEADBEEF, 0x8000_8000, 0x0000_7FFF, 0xA5A5_5A5A]

# ---------- LoadExt: Word[32] A[2] funct3[3] -> Y[32] ----------
rows = []
for w in WORDS + [random.getrandbits(32) for _ in range(30)]:
    for a in range(4):
        for f3 in range(8):                # vet can ca funct3 khong hop le (3, 6, 7)
            rows.append((w, a, f3, mem_load([w], a, f3)))
with open("tests/loadext.txt", "w", newline="\n") as f:
    f.write("# Test vector LoadExt (to hop). Y = mo rong(Word >> A*8) theo funct3\n")
    f.write("Word[32] A[2] funct3[3] Y[32]\n")
    for w, a, f3, o in rows: f.write(f"{H(w)} {B(a,2)} {B(f3,3)} {H(o)}\n")
n_le = len(rows)

# ---------- StoreMerge: Old[32] WData[32] A[2] funct3[3] -> Merged[32] ----------
rows = []
pairs = [(0x00000000, 0x123456AB), (0xFFFFFFFF, 0x00000000), (0xAB0000AB, 0xFFFFFFFF), (0x11223344, 0xCAFEBABE)]
pairs += [(random.getrandbits(32), random.getrandbits(32)) for _ in range(30)]
for old, wd in pairs:
    for a in range(4):
        for f3 in range(8):
            mem = [old]; mem_store(mem, a, wd, f3)
            rows.append((old, wd, a, f3, mem[0]))
with open("tests/storemerge.txt", "w", newline="\n") as f:
    f.write("# Test vector StoreMerge (to hop). Merged = (Old & ~(K<<A*8)) | (D<<A*8)\n")
    f.write("Old[32] WData[32] A[2] funct3[3] Merged[32]\n")
    for o, w, a, f3, n in rows: f.write(f"{H(o)} {H(w)} {B(a,2)} {B(f3,3)} {H(n)}\n")
n_sm = len(rows)

# ---------- DMEM (tuan tu): Addr WData MemWrite funct3 clk -> RData ----------
rows = []
class D:
    def __init__(s, sid): s.mem = {}; s.set = sid; s.seq = 0
    def _rd(s, addr, f3):
        i = (addr >> 2) & 0x3FF
        if i not in s.mem: return "<DC>"
        return H(mem_load(s._arr(i), addr, f3))
    def _arr(s, i):
        a = [0] * 1024; a[i] = s.mem[i]; return a
    def row(s, addr, wd, we, f3, clk):
        s.seq += 1; rows.append((s.set, s.seq, addr, wd, we, f3, clk, s._rd(addr, f3)))
    def write(s, addr, wd, f3=2):
        i = (addr >> 2) & 0x3FF
        known = i in s.mem or (f3 & 3) >= 2
        s.row(addr, wd, 1, f3, 0)
        a = [0] * 1024; a[i] = s.mem.get(i, 0); mem_store(a, addr, wd, f3)
        if known: s.mem[i] = a[i]
        s.row(addr, wd, 1, f3, 1)
    def read(s, addr, f3=2):
        s.row(addr, 0, 0, f3, 0); s.row(addr, 0, 0, f3, 1)

d = D(1)                                    # Set 1: ghi/doc word nhu Lab 4 (funct3 = 010)
for i, v in enumerate([0x11111111, 0x22222222, 0xDEADBEEF, 0x7FFFFFFF, 0x80000000]):
    d.write(4 * i, v)
for i in range(5): d.read(4 * i)
d.read(0x0FFC); d.write(0x0FFC, 0xCAFEF00D); d.read(0x0FFC)
d.write(0x1000, 0x0BADF00D); d.read(0x0000)               # dia chi 0x1000 quay vong ve o 0
d = D(2)                                    # Set 2: MemWrite = 0 khong ghi
d.write(0x40, 0xAAAA5555); d.row(0x40, 0x12345678, 0, 2, 0); d.row(0x40, 0x12345678, 0, 2, 1); d.read(0x40)
d = D(3)                                    # Set 3: doc byte/half co dau va khong dau
d.write(0x100, 0x80FF7F01)
for a in range(4):
    for f3 in (0, 4): d.read(0x100 + a, f3)
for a in (0, 2):
    for f3 in (1, 5): d.read(0x100 + a, f3)
d = D(4)                                    # Set 4: SB / SH chi sua dung byte/half
d.write(0x200, 0x00000000)
d.write(0x200, 0x123456AB, 0); d.read(0x200)
d.write(0x203, 0x123456AB, 0); d.read(0x200)
d.write(0x204, 0xFFFFFFFF); d.write(0x205, 0, 0); d.read(0x204)
d.write(0x206, 0, 1); d.read(0x204)
d.write(0x208, 0x11223344); d.write(0x208, 0xBEEF, 1); d.read(0x208); d.read(0x20A, 5); d.read(0x20A, 1)
d = D(5)                                    # Set 5: ngau nhien
for i in range(16): d.write(0x300 + 4 * i, random.getrandbits(32))
for _ in range(60):
    addr = 0x300 + random.randrange(64)
    if random.random() < 0.5:
        f3 = random.choice([0, 1, 2]); addr &= ~((1 << f3) - 1) if f3 else ~0
        d.write(addr, random.getrandbits(32), f3)
    else:
        f3 = random.choice(F3S); addr &= ~(1 if f3 in (1, 5) else 0) & ~(3 if f3 == 2 else 0)
        d.read(addr, f3)
with open("tests/dmem.txt", "w", newline="\n") as f:
    f.write("# Test vector DMEM (tuan tu), Lab 13: co chan funct3. <DC> = o nho chua ghi, khong kiem tra.\n")
    f.write("<set> <seq> Addr[32] WData[32] MemWrite funct3[3] clk RData[32]\n")
    for st, sq, a, wd, we, f3, c, rd in rows:
        f.write(f"{st} {sq} {H(a)} {H(wd)} {we} {B(f3,3)} {c} {rd}\n")
print(f"loadext: {n_le} dong, storemerge: {n_sm} dong, dmem: {len(rows)} dong")
