#!/usr/bin/env python3
"""Sinh tests/hazardunit.txt (Lab 10)."""
import random
rnd = random.Random(10)
B = lambda v, w: f"{v:0{w}b}"
def stall(mr, rd_e, rs1, rs2):
    return int(bool(mr and rd_e != 0 and (rd_e == rs1 or rd_e == rs2)))
rows = []
regs = [0, 1, 2, 3, 31]
for mr in (0, 1):
    for rd in regs:
        for rs1 in regs:
            for rs2 in regs:
                rows.append((mr, rd, rs1, rs2))
for _ in range(150):
    rows.append((rnd.getrandbits(1), rnd.randrange(32), rnd.randrange(32), rnd.randrange(32)))
with open("tests/hazardunit.txt", "w", newline="\n") as f:
    f.write("# HazardUnit: Stall = MemRead_e AND rd_e != 0 AND (rd_e == rs1_d OR rd_e == rs2_d)\n")
    f.write("MemRead_e rd_e[5] rs1_d[5] rs2_d[5] Stall\n")
    for mr, rd, rs1, rs2 in rows:
        f.write(f"{mr} {B(rd,5)} {B(rs1,5)} {B(rs2,5)} {stall(mr, rd, rs1, rs2)}\n")
print("hazardunit:", len(rows), "dong")
