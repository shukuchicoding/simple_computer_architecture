#!/usr/bin/env python3
"""Sinh tests/forwardunit.txt va tests/wbbypass.txt (Lab 9)."""
import random
rnd = random.Random(9)
H = lambda v: f"0x{v:08X}"
B = lambda v, w: f"{v:0{w}b}"

def fwd(rs, rd_m, rw_m, rd_w, rw_w):
    if rw_m and rd_m != 0 and rd_m == rs: return 2      # 10: lay tu EX/MEM (moi nhat)
    if rw_w and rd_w != 0 and rd_w == rs: return 1      # 01: lay tu MEM/WB
    return 0                                             # 00: dung gia tri doc tu RegFile

rows = []
regs = [0, 1, 2, 3, 31]
for rs1 in regs:                                         # vet can tren tap nho
    for rd_m in regs:
        for rd_w in regs:
            for rw_m in (0, 1):
                for rw_w in (0, 1):
                    rs2 = rnd.choice(regs)
                    rows.append((rs1, rs2, rd_m, rw_m, rd_w, rw_w))
for _ in range(200):
    rows.append((rnd.randrange(32), rnd.randrange(32), rnd.randrange(32), rnd.getrandbits(1), rnd.randrange(32), rnd.getrandbits(1)))
with open("tests/forwardunit.txt", "w", newline="\n") as f:
    f.write("# ForwardUnit. ForwardA/B: 00 = RegFile (ID_EX), 01 = MEM/WB (wb_w), 10 = EX/MEM (result_m)\n")
    f.write("rs1_e[5] rs2_e[5] rd_m[5] RegWrite_m rd_w[5] RegWrite_w ForwardA[2] ForwardB[2]\n")
    for rs1, rs2, rd_m, rw_m, rd_w, rw_w in rows:
        f.write(f"{B(rs1,5)} {B(rs2,5)} {B(rd_m,5)} {rw_m} {B(rd_w,5)} {rw_w} "
                f"{B(fwd(rs1, rd_m, rw_m, rd_w, rw_w),2)} {B(fwd(rs2, rd_m, rw_m, rd_w, rw_w),2)}\n")
n1 = len(rows)

rows = []
for rs1 in regs:
    for rd_w in regs:
        for rw in (0, 1):
            rows.append((rs1, rnd.choice(regs), rd_w, rw, rnd.getrandbits(32), rnd.getrandbits(32), rnd.getrandbits(32)))
for _ in range(200):
    rows.append((rnd.randrange(32), rnd.randrange(32), rnd.randrange(32), rnd.getrandbits(1),
                 rnd.getrandbits(32), rnd.getrandbits(32), rnd.getrandbits(32)))
with open("tests/wbbypass.txt", "w", newline="\n") as f:
    f.write("# WBBypass: RDx = (RegWrite_w && rd_w != 0 && rd_w == rsx) ? WD : RFx\n")
    f.write("rs1[5] rs2[5] rd_w[5] RegWrite_w WD[32] RF1[32] RF2[32] RD1[32] RD2[32]\n")
    for rs1, rs2, rd_w, rw, wd, rf1, rf2 in rows:
        hit = lambda rs: rw and rd_w != 0 and rd_w == rs
        f.write(f"{B(rs1,5)} {B(rs2,5)} {B(rd_w,5)} {rw} {H(wd)} {H(rf1)} {H(rf2)} "
                f"{H(wd if hit(rs1) else rf1)} {H(wd if hit(rs2) else rf2)}\n")
print("forwardunit:", n1, "dong; wbbypass:", len(rows), "dong")
