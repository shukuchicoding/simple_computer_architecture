#!/usr/bin/env python3
# Lab 16 - sinh tests/btb.txt va tests/predregs.txt (ca hai tuan tu)
#   python tools/gen_lab16_tests.py      (chay tu thu muc riscv32)
import random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pipesim import BTB
random.seed(16)
M = 0xFFFFFFFF
H = lambda v: f"0x{v & M:08X}"

# ---------- BTB: PC_f PC_e Target_e Update Taken clk Reset -> Pred PTarget ----------
rows = []
class T:
    def __init__(s, sid): s.b = BTB(); s.set = sid; s.seq = 0
    def row(s, pcf, pce, tg, up, tk, clk, rst=0):
        s.seq += 1
        if rst: s.b = BTB()
        p, t = s.b.lookup(pcf)
        rows.append((s.set, s.seq, pcf, pce, tg, up, tk, clk, rst, p, t))
    def tick(s, pcf, pce=0, tg=0, up=0, tk=0):
        s.row(pcf, pce, tg, up, tk, 0)
        if up: s.b.update(pce, tg, bool(tk))
        s.row(pcf, pce, tg, up, tk, 1)
t = T(1)                                    # Set 1: mot nhanh: cap phat, bao hoa, giam dan
t.tick(0x40)                                # chua co -> Pred 0
t.tick(0x40, 0x40, 0x10, 1, 0)              # khong nhay + chua co: khong cap phat
t.tick(0x40)
t.tick(0x40, 0x40, 0x10, 1, 1)              # nhay: cap phat, bo dem = 2 -> doan nhay
t.tick(0x40); t.tick(0x44)                  # PC khac -> khong khop
t.tick(0x40, 0x40, 0x10, 1, 1)              # 3
t.tick(0x40, 0x40, 0x10, 1, 1)              # 3 (bao hoa)
t.tick(0x40, 0x40, 0x10, 1, 0)              # 2 -> van doan nhay
t.tick(0x40, 0x40, 0x10, 1, 0)              # 1 -> doan khong nhay
t.tick(0x40, 0x40, 0x10, 1, 0)              # 0
t.tick(0x40, 0x40, 0x10, 1, 0)              # 0 (bao hoa)
t.tick(0x40, 0x40, 0x10, 1, 1)              # 1
t.tick(0x40, 0x40, 0x10, 1, 1)              # 2 -> doan nhay
t.tick(0x80)                                # 0x80 cung chi so voi 0x40 nhung khac tag
t.tick(0x80, 0x80, 0x200, 1, 1)             # ghi de muc cua 0x40
t.tick(0x40); t.tick(0x80)
t.tick(0x40, 0x40, 0x10, 1, 1, ); t.tick(0x40)
t.tick(0x40, 0x40, 0x10, 0, 1)              # Update = 0: khong ghi
t = T(2)                                    # Set 2: Reset xoa toan bo
t.tick(0x100, 0x100, 0x20, 1, 1); t.tick(0x100)
t.row(0x100, 0, 0, 0, 0, 0, rst=1); t.row(0x100, 0, 0, 0, 0, 0); t.tick(0x100)
t = T(3)                                    # Set 3: ngau nhien tren 24 PC (co trung chi so)
pcs = [random.randrange(0, 0x400) & ~3 for _ in range(24)]
tgt = {p: random.randrange(0, 0x1000) & ~3 for p in pcs}
for _ in range(250):
    pf, pe = random.choice(pcs), random.choice(pcs)
    t.tick(pf, pe, tgt[pe], int(random.random() < 0.7), int(random.random() < 0.6))
with open("tests/btb.txt", "w", newline="\n") as f:
    f.write("# Test vector BTB (tuan tu). Chi so = 16 | PC[5:2]; TAG = PC|1; TGT = {dich[31:2], bo dem 2 bit}\n")
    f.write("<set> <seq> PC_f[32] PC_e[32] Target_e[32] Update Taken clk Reset Pred PTarget[32]\n")
    for st, sq, pf, pe, tg, up, tk, c, r, p, pt in rows:
        f.write(f"{st} {sq} {H(pf)} {H(pe)} {H(tg)} {up} {tk} {c} {r} {p} {H(pt)}\n")
n_btb = len(rows)

# ---------- PredRegs: Pred_f EN FlushD FlushE clk Reset -> Pred_d Pred_e ----------
rows = []
st = dict(d=0, e=0, seq=0)
def prow(pf, en, fd, fe, clk, rst=0):
    st["seq"] += 1
    if rst: st["d"] = st["e"] = 0
    rows.append((st["seq"], pf, en, fd, fe, clk, rst, st["d"], st["e"]))
def ptick(pf, en=1, fd=0, fe=0):
    prow(pf, en, fd, fe, 0)
    d, e = st["d"], st["e"]
    st["d"] = 0 if fd else (pf if en else d)
    st["e"] = 0 if fe else d
    prow(pf, en, fd, fe, 1)
for pf in (1, 0, 1, 1, 0): ptick(pf)
ptick(1); ptick(0, en=0); ptick(0, en=0); ptick(0)             # stall: Pred_d giu nguyen
ptick(1); ptick(1, fd=1); ptick(1, fe=1); ptick(1, fd=1, fe=1)  # flush
ptick(1, en=0, fd=1)                                             # flush thang EN
ptick(1); prow(1, 1, 0, 0, 0, rst=1); prow(1, 1, 0, 0, 0)
for _ in range(80):
    ptick(random.randint(0, 1), int(random.random() < 0.8), int(random.random() < 0.2), int(random.random() < 0.2))
with open("tests/predregs.txt", "w", newline="\n") as f:
    f.write("# Test vector PredRegs (tuan tu). Pred_d nhu IF/ID (EN, FlushD); Pred_e nhu ID/EX (luon nap, FlushE)\n")
    f.write("<set> <seq> Pred_f EN FlushD FlushE clk Reset Pred_d Pred_e\n")
    for r in rows: f.write("1 " + " ".join(str(v) for v in r) + "\n")
print(f"btb: {n_btb} dong, predregs: {len(rows)} dong")
