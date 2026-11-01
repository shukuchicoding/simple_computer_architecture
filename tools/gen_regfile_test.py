#!/usr/bin/env python3
# Sinh tests/regfile.txt: python tools/gen_regfile_test.py > tests/regfile.txt
# Test tuan tu: moi buoc ghi gom 2 dong (clk=0 roi clk=1 -> canh len).
import random
random.seed(2)
rows = []          # (set, seq, rs1, rs2, rd, WD, RegWrite, clk, Reset, RD1, RD2)

class Sim:
    def __init__(s, set_id):
        s.r = [0]*32; s.set = set_id; s.seq = 0; s.prev = 0
    def step(s, rs1, rs2, rd, wd, we, clk, rst=0):
        if rst: s.r = [0]*32
        if s.prev == 0 and clk == 1 and we and rd != 0 and not rst:   # chi ghi o canh len
            s.r[rd] = wd
        s.prev = clk
        s.seq += 1
        rows.append((s.set, s.seq, rs1, rs2, rd, wd, we, clk, rst, s.r[rs1], s.r[rs2]))
    def write(s, rd, wd, we=1, rs1=0, rs2=0):
        s.step(rs1, rs2, rd, wd, we, 0)
        s.step(rs1, rs2, rd, wd, we, 1)
    def read(s, rs1, rs2):
        s.step(rs1, rs2, 0, 0, 0, 0)

# Set 1: ghi x1..x31 gia tri khac nhau, doc lai bang ca 2 cong
s = Sim(1)
vals = {i: (0x01010101 * i) ^ (0x80000000 if i % 2 else 0) for i in range(1, 32)}
for i in range(1, 32):
    s.write(i, vals[i], rs1=i, rs2=i)        # doc ngay sau canh len
for i in range(32):
    s.read(i, 31 - i)

# Set 2: ghi vao x0 phai bi bo qua
s = Sim(2)
s.write(0, 0xDEADBEEF, rs1=0, rs2=0)
s.read(0, 0)

# Set 3: RegWrite = 0 khong duoc ghi
s = Sim(3)
s.write(5, 0x12345678, rs1=5, rs2=5)
s.write(5, 0xFFFFFFFF, we=0, rs1=5, rs2=5)
s.read(5, 5)

# Set 4: chi ghi khi co canh len (doi WD/rd luc clk=1 giu nguyen khong ghi)
s = Sim(4)
s.write(7, 0x00000077, rs1=7, rs2=8)
s.step(7, 8, 8, 0x00000088, 1, 1)            # clk van =1, khong co canh -> khong ghi x8
s.step(7, 8, 8, 0x00000088, 1, 0)
s.step(7, 8, 8, 0x00000088, 1, 1)            # canh len -> ghi x8

# Set 5: ghi de nhieu lan + Reset xoa het
s = Sim(5)
for v in (1, 2, 0xFFFFFFFF):
    s.write(10, v, rs1=10, rs2=11)
s.write(11, 0xCAFEBABE, rs1=10, rs2=11)
s.step(10, 11, 0, 0, 0, 0, rst=1)
s.read(10, 11)

# Set 6: ngau nhien 200 buoc
s = Sim(6)
for _ in range(200):
    s.write(random.randrange(32), random.getrandbits(32), int(random.random() < 0.8),
            random.randrange(32), random.randrange(32))

print("# Test vector Register File - Logisim-evolution 4.x (Simulate > Test Vector)")
print("# Moi lan ghi = 2 dong: clk=0 roi clk=1 (canh len). RD1/RD2 kiem tra sau moi dong.")
print("<set> <seq> rs1[5] rs2[5] rd[5] WD[32] RegWrite clk Reset RD1[32] RD2[32]")
for st, sq, a, b, d, wd, we, c, r, o1, o2 in rows:
    print(f"{st} {sq} {a:05b} {b:05b} {d:05b} 0x{wd:08X} {we} {c} {r} 0x{o1:08X} 0x{o2:08X}")
