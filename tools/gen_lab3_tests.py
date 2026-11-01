#!/usr/bin/env python3
# Sinh tests/immgen.txt va tests/branchcmp.txt
#   python tools/gen_lab3_tests.py
# Quy uoc: cot 32 bit viet hex 0x..., cot nhieu bit nho viet nhi phan du so chu so.
import random, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import asm
random.seed(3)
M = 0xFFFFFFFF
def bits(x, hi, lo): return (x >> lo) & ((1 << (hi - lo + 1)) - 1)
def sext(v, n): return (v - (1 << n)) & M if v >> (n - 1) else v

def immgen(ins, sel):
    if sel == 0: return sext(bits(ins,31,20), 12)                                    # I
    if sel == 1: return sext(bits(ins,31,25) << 5 | bits(ins,11,7), 12)              # S
    if sel == 2: return sext(bits(ins,31,31) << 12 | bits(ins,7,7) << 11 |
                             bits(ins,30,25) << 5 | bits(ins,11,8) << 1, 13)          # B
    if sel == 3: return ins & 0xFFFFF000                                              # U
    if sel == 4: return sext(bits(ins,31,31) << 20 | bits(ins,19,12) << 12 |
                             bits(ins,20,20) << 11 | bits(ins,30,21) << 1, 21)        # J
    return 0                                                                          # 5..7

# ---- Kiem cheo voi assembler: ma hoa imm roi giai ma phai ra dung imm ----
NAME = ['I','S','B','U','J']
named = []   # (instr, sel, chu thich)
for imm in [0, 1, -1, 5, -2048, 2047, 0x7FF, -3, 100]:
    w = asm.enc_i(imm, 1, 0, 2, 0x13); assert immgen(w,0) == imm & M; named.append((w,0,f"addi x2,x1,{imm}"))
    w = asm.enc_s(imm, 5, 2, 2, 0x23); assert immgen(w,1) == imm & M; named.append((w,1,f"sw x5,{imm}(x2)"))
for imm in [0, 8, -8, -4096, 4094, 2048, -2, 0x7FE]:
    w = asm.enc_b(imm, 2, 1, 1, 0x63); assert immgen(w,2) == imm & M; named.append((w,2,f"bne x1,x2,{imm}"))
for imm in [0, 0x12345, 0xFFFFF, 0x80000, 1]:
    w = asm.enc_u(imm, 9, 0x37); assert immgen(w,3) == (imm << 12) & M; named.append((w,3,f"lui x9,{imm:#x}"))
for imm in [0, 16, -16, 0xFFFFE, -0x100000, 2048, 4096, -2]:
    w = asm.enc_j(imm, 1, 0x6f); assert immgen(w,4) == imm & M; named.append((w,4,f"jal ra,{imm}"))

rows = [(w, s, c) for w, s, c in named]
for sel in range(8):                           # ngau nhien, ca ImmSel 5..7 (phai ra 0)
    for _ in range(40 if sel < 5 else 3):
        rows.append((random.getrandbits(32), sel, ""))
for w in (0, M, 0x80000000, 0x7FFFFFFF):        # bien
    for sel in range(5): rows.append((w, sel, "bien"))

with open("tests/immgen.txt", "w", newline="\n") as f:
    f.write("# Test vector ImmGen. ImmSel: 000 I, 001 S, 010 B, 011 U, 100 J\n")
    f.write("Instr[32] ImmSel[3] Imm[32]\n")
    for w, s, c in rows:
        f.write(f"0x{w:08X} {s:03b} 0x{immgen(w,s):08X}" + (f"   # {NAME[s]}: {c}" if c else "") + "\n")

# ---- Branch comparator ----
def s32(x): return x - (1 << 32) if x >> 31 else x
def br(a, b, f3):
    eq, lt, ltu = int(a == b), int(s32(a) < s32(b)), int(a < b)
    taken = {0: eq, 1: 1-eq, 4: lt, 5: 1-lt, 6: ltu, 7: 1-ltu}.get(f3, 0)
    return eq, lt, ltu, taken
edge = [0, 1, 5, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF, 0xFFFFFFFE, 0x12345678]
pairs = [(a, b) for a in edge for b in edge] + [(random.getrandbits(32), random.getrandbits(32)) for _ in range(30)]
pairs += [(x, x) for x in (random.getrandbits(32) for _ in range(5))]
with open("tests/branchcmp.txt", "w", newline="\n") as f:
    f.write("# Test vector BranchCmp. funct3: 000 BEQ 001 BNE 100 BLT 101 BGE 110 BLTU 111 BGEU, 010/011 -> Taken=0\n")
    f.write("A[32] B[32] funct3[3] Eq Lt Ltu Taken\n")
    n = 0
    for a, b in pairs:
        for f3 in range(8):
            eq, lt, ltu, t = br(a, b, f3)
            f.write(f"0x{a:08X} 0x{b:08X} {f3:03b} {eq} {lt} {ltu} {t}\n"); n += 1
print("immgen rows:", len(rows), " branchcmp rows:", n, " (kiem cheo assembler: OK)")
