#!/usr/bin/env python3
# Lab 14 - sinh tests/muldiv.txt va tests/ismul.txt
#   python tools/gen_lab14_tests.py      (chay tu thu muc riscv32)
import random, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rvsim import muldiv, is_m
import asm
random.seed(14)
M = 0xFFFFFFFF
H = lambda v: f"0x{v & M:08X}"
B = lambda v, n: format(v, f"0{n}b")

# ---------- MulDiv: A[32] B[32] funct3[3] -> Y[32] ----------
edge = [0, 1, 2, 3, 7, 9, 0x7FFFFFFF, 0x80000000, 0xFFFFFFFF, 0xFFFFFFFE, 0xFFFFFFF9, 0x12345678, 0x9ABCDEF0, 0x10000, 0xFFFF]
pairs = [(a, b) for a in edge for b in edge]
pairs += [(random.getrandbits(32), random.getrandbits(32)) for _ in range(80)]
pairs += [(random.getrandbits(32), random.getrandbits(random.randint(1, 12))) for _ in range(40)]   # so chia nho
rows = [(a, b, f3, muldiv(f3, a, b)) for a, b in pairs for f3 in range(8)]
with open("tests/muldiv.txt", "w", newline="\n") as f:
    f.write("# Test vector MulDiv (to hop). funct3: 0 MUL 1 MULH 2 MULHSU 3 MULHU 4 DIV 5 DIVU 6 REM 7 REMU\n")
    f.write("A[32] B[32] funct3[3] Y[32]\n")
    for a, b, f3, y in rows: f.write(f"{H(a)} {H(b)} {B(f3,3)} {H(y)}\n")
n_md = len(rows)

# ---------- IsMul: Instr[32] -> IsM ----------
src = []
for m in ["mul", "mulh", "mulhsu", "mulhu", "div", "divu", "rem", "remu",
          "add", "sub", "sll", "slt", "sltu", "xor", "srl", "sra", "or", "and"]:
    src.append(f"{m} x{random.randint(0,31)}, x{random.randint(0,31)}, x{random.randint(0,31)}")
src += ["addi x5, x6, 33", "addi x1, x2, -1", "lw x3, 32(x4)", "sw x7, -4(x8)", "beq x1, x2, 0", "jal x1, 0",
        "jalr x1, x2, 0", "lui x5, 0xFFFFF", "slli x1, x2, 3", "srai x3, x4, 7", "lb x1, 1(x2)", "sh x3, 2(x4)"]
words = []
for s in src:
    m, rest = s.split(None, 1)
    ops = [o.strip() for o in rest.split(",")]
    for mm, oo in asm.expand(m, ops): words.append(asm.encode(mm, oo, 0, {}))
for _ in range(150):                                   # lenh R ngau nhien voi funct7 bat ky + word ngau nhien
    words.append((random.getrandbits(7) << 25) | (random.getrandbits(18) << 7) | 0x33)
    words.append(random.getrandbits(32))
for w in (0x02000033, 0x02000013, 0x00000033, 0xFE000033, 0x020000B3, 0x02000073, 0x02000032):
    words.append(w)
with open("tests/ismul.txt", "w", newline="\n") as f:
    f.write("# Test vector IsMul (to hop). IsM = 1 khi opcode = 0110011 va bit 25 = 1\n")
    f.write("Instr[32] IsM\n")
    for w in words: f.write(f"{H(w)} {int(is_m(w))}\n")
print(f"muldiv: {n_md} dong, ismul: {len(words)} dong")
