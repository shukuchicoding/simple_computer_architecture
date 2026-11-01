#!/usr/bin/env python3
# Sinh tests/alu.txt cho Logisim: python tools/gen_alu_test.py > tests/alu.txt
import random
M = 0xFFFFFFFF
def s32(x): return x - (1 << 32) if x & 0x80000000 else x
OPS = {0:'ADD',1:'SUB',2:'AND',3:'OR',4:'XOR',5:'SLT',6:'SLTU',7:'SLL',8:'SRL',9:'SRA',10:'PASSB'}
def alu(a, b, c):
    sh = b & 31
    if c == 0: y = a + b
    elif c == 1: y = a - b
    elif c == 2: y = a & b
    elif c == 3: y = a | b
    elif c == 4: y = a ^ b
    elif c == 5: y = int(s32(a) < s32(b))
    elif c == 6: y = int(a < b)
    elif c == 7: y = a << sh
    elif c == 8: y = a >> sh
    elif c == 9: y = s32(a) >> sh
    elif c == 10: y = b
    else: raise ValueError
    return y & M
edge = [0, 1, 2, 5, 7, 31, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF, 0xFFFFFFFE, 0x12345678, 0xF0F0F0F0]
random.seed(1)
cases = []
for c in OPS:
    for a in edge:
        for b in (0, 1, 4, 7, 31, 32, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF):
            cases.append((a, b, c))
    for _ in range(10):
        cases.append((random.getrandbits(32), random.getrandbits(32), c))
print("# Test vector ALU - Logisim Evolution (Simulate > Test Vector)")
print("A[32] B[32] ALUctl[4] Y[32] Zero")
for a, b, c in cases:
    y = alu(a, b, c)
    print(f"0x{a:08X} 0x{b:08X} 0x{c:X} 0x{y:08X} {int(y == 0)}")
