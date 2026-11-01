#!/usr/bin/env python3
# Sinh tests/pcunit.txt, tests/imem_lab0.txt, tests/dmem.txt
#   python tools/gen_lab4_tests.py      (chay tu thu muc riscv32)
import random
random.seed(4)
M = 0xFFFFFFFF
H = lambda v: f"0x{v:08X}"

# ---------- PCUnit: Register 32 bit, EN, Reset (xoa ve 0), PC4 = PC + 4 ----------
rows = []
class PC:
    def __init__(s, set_id): s.pc = 0; s.prev = 0; s.set = set_id; s.seq = 0
    def step(s, nxt, en, clk, rst=0):
        if rst: s.pc = 0
        elif s.prev == 0 and clk == 1 and en: s.pc = nxt
        s.prev = clk; s.seq += 1
        rows.append((s.set, s.seq, nxt, en, clk, rst, s.pc, (s.pc + 4) & M))
    def tick(s, nxt, en=1):
        s.step(nxt, en, 0); s.step(nxt, en, 1)

p = PC(1)                                   # Set 1: chay tuan tu PC = PC + 4
for _ in range(10): p.tick((p.pc + 4) & M)
p = PC(2)                                   # Set 2: nhay toi dia chi bat ky + bien
for v in (0x100, 0xFFFFFFFC, 0x80000000, 0x7FFFFFFC, 0x00000010): p.tick(v)
p = PC(3)                                   # Set 3: EN = 0 giu nguyen PC (stall)
p.tick(0x40); p.tick(0x44, en=0); p.tick(0x48, en=0); p.tick(0x4C)
p = PC(4)                                   # Set 4: chi doi o canh len
p.tick(0x20); p.step(0x99, 1, 1); p.step(0x30, 1, 0); p.step(0x30, 1, 1)
p = PC(5)                                   # Set 5: Reset dua PC ve 0
p.tick(0x1234); p.step(0x50, 1, 0, rst=1); p.step(0x50, 1, 0, rst=0); p.tick(0x50)
p = PC(6)                                   # Set 6: ngau nhien
for _ in range(40): p.tick(random.getrandbits(30) << 2, en=int(random.random() < 0.8))

with open("tests/pcunit.txt", "w", newline="\n") as f:
    f.write("# Test vector PCUnit (tuan tu). Moi tick = 2 dong clk 0 -> 1.\n")
    f.write("<set> <seq> PCnext[32] EN clk Reset PC[32] PC4[32]\n")
    for st, sq, n, en, c, r, pc, pc4 in rows:
        f.write(f"{st} {sq} {H(n)} {en} {c} {r} {H(pc)} {H(pc4)}\n")
n_pc = len(rows)

# ---------- IMEM: ROM da nap rom/lab0_check.hex ----------
words = []
for line in open("rom/lab0_check.hex").read().split("\n")[1:]:
    words += [int(w, 16) for w in line.split()]
with open("tests/imem_lab0.txt", "w", newline="\n") as f:
    f.write("# Test vector IMEM - CHI DUNG KHI ROM DA NAP rom/lab0_check.hex\n")
    f.write("PC[32] Instr[32]\n")
    for i, w in enumerate(words):
        f.write(f"{H(4*i)} {H(w)}\n")
    for i, w in enumerate(words[:3]):                 # 2 bit thap bi bo qua
        f.write(f"{H(4*i+2)} {H(w)}   # PC khong chia het cho 4\n")
    for i, w in enumerate(words[:3]):                 # bit > 11 bi bo qua (ROM 4 KB)
        f.write(f"{H(0x1000 + 4*i)} {H(w)}   # PC vuot 4 KB quay vong\n")
    f.write(f"{H(4*len(words))} 0x00000000   # sau chuong trinh: ROM = 0\n")
    f.write(f"0x00000FFC 0x00000000\n")
n_im = len(words) + 8

# ---------- DMEM: RAM 1024 x 32, dia chi byte -> Addr[11:2] ----------
rows = []
class DM:
    def __init__(s, set_id): s.m = {}; s.prev = 0; s.set = set_id; s.seq = 0
    def step(s, addr, wd, we, clk):
        if s.prev == 0 and clk == 1 and we: s.m[(addr >> 2) & 0x3FF] = wd
        s.prev = clk; s.seq += 1
        k = (addr >> 2) & 0x3FF
        rd = H(s.m[k]) if k in s.m else "<DC>"        # o chua ghi: khong kiem
        rows.append((s.set, s.seq, addr, wd, we, clk, rd))
    def write(s, addr, wd): s.step(addr, wd, 1, 0); s.step(addr, wd, 1, 1)
    def read(s, addr): s.step(addr, 0, 0, 0)

d = DM(1)                                   # Set 1: ghi roi doc lai
for a, v in [(0x0, 0x11111111), (0x4, 0x22222222), (0x8, 0xDEADBEEF), (0xFFC, 0xCAFEBABE)]:
    d.write(a, v)
for a in (0x0, 0x4, 0x8, 0xFFC): d.read(a)
d = DM(2)                                   # Set 2: MemWrite = 0 khong ghi
d.write(0x10, 0xAAAAAAAA); d.step(0x10, 0x55555555, 0, 0); d.step(0x10, 0x55555555, 0, 1); d.read(0x10)
d = DM(3)                                   # Set 3: dia chi byte -> word, bo 2 bit thap va bit > 11
d.write(0x20, 0x12345678); d.read(0x21); d.read(0x23); d.read(0x1020); d.read(0x80000020)
d.write(0x24, 0x9ABCDEF0); d.read(0x20); d.read(0x24)
d = DM(4)                                   # Set 4: chi ghi o canh len
d.write(0x30, 0x1); d.step(0x30, 0x2, 1, 1); d.read(0x30); d.write(0x30, 0x3); d.read(0x30)
d = DM(5)                                   # Set 5: ngau nhien
addrs = [random.randrange(1024) * 4 for _ in range(16)]
for _ in range(80):
    a = random.choice(addrs)
    if random.random() < 0.5: d.write(a, random.getrandbits(32))
    else: d.read(a)

with open("tests/dmem.txt", "w", newline="\n") as f:
    f.write("# Test vector DMEM (tuan tu). <DC> = o nho chua ghi, khong kiem tra.\n")
    f.write("<set> <seq> Addr[32] WData[32] MemWrite clk RData[32]\n")
    for st, sq, a, wd, we, c, rd in rows:
        f.write(f"{st} {sq} {H(a)} {H(wd)} {we} {c} {rd}\n")
print(f"pcunit: {n_pc} dong, imem_lab0: {n_im} dong, dmem: {len(rows)} dong")
