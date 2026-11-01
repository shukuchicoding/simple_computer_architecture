#!/usr/bin/env python3
"""Sinh noi dung ROM cho Control Unit va test vector.
   python tools/gen_roms.py      (chay tu thu muc riscv32)
Tao ra: rom/control.rom (128 x 14 bit), rom/aluctl.rom (64 x 4 bit), tests/control.txt
"""
import os, sys, random
sys.path.insert(0, os.path.dirname(__file__))
import asm
random.seed(5)

# ---------------- Bang dieu khien chinh: dia chi = opcode[6:0] ----------------
# Control word (14 bit):
#  bit 0 RegWrite | 1 ALUSrc | 2 MemRead | 3 MemWrite | 5:4 MemToReg (0 ALU,1 Mem,2 PC+4)
#  bit 6 Branch | 7 Jump (JAL) | 8 Jalr | 10:9 ALUOp (0 ADD,1 PASS B,2 R-type,3 I-type)
#  bit 13:11 ImmSel (0 I,1 S,2 B,3 U,4 J)
CTRL = {
 #  opcode     RW Src MR MW M2R Br Jmp Jalr ALUOp Imm
 0b0110011: (1, 0, 0, 0, 0, 0, 0, 0, 2, 0),   # R-type
 0b0010011: (1, 1, 0, 0, 0, 0, 0, 0, 3, 0),   # I-type ALU
 0b0000011: (1, 1, 1, 0, 1, 0, 0, 0, 0, 0),   # LOAD
 0b0100011: (0, 1, 0, 1, 0, 0, 0, 0, 0, 1),   # STORE
 0b1100011: (0, 0, 0, 0, 0, 1, 0, 0, 0, 2),   # BRANCH
 0b1101111: (1, 0, 0, 0, 2, 0, 1, 0, 0, 4),   # JAL
 0b1100111: (1, 1, 0, 0, 2, 0, 0, 1, 0, 0),   # JALR
 0b0110111: (1, 1, 0, 0, 0, 0, 0, 0, 1, 3),   # LUI
}
FIELDS = ["RegWrite","ALUSrc","MemRead","MemWrite","MemToReg","Branch","Jump","Jalr","ALUOp","ImmSel"]
def pack(t):
    rw, s, mr, mw, m2r, br, j, jr, op, imm = t
    return rw | s<<1 | mr<<2 | mw<<3 | m2r<<4 | br<<6 | j<<7 | jr<<8 | op<<9 | imm<<11

# ---------------- ALU control: dia chi = {ALUOp[1:0], funct3[2:0], funct7[5]} ----------------
# ALUctl: 0 ADD 1 SUB 2 AND 3 OR 4 XOR 5 SLT 6 SLTU 7 SLL 8 SRL 9 SRA 10 PASSB
F3 = {1: 7, 2: 5, 3: 6, 4: 4, 6: 3, 7: 2}
def alu_ctl(aluop, f3, b5):
    if aluop == 0: return 0                          # ADD (load/store/jalr)
    if aluop == 1: return 10                         # PASS B (lui)
    if f3 == 0: return 1 if (aluop == 2 and b5) else 0   # SUB chi voi R-type; ADDI bo qua bit 30
    if f3 == 5: return 9 if b5 else 8                # SRA/SRAI : SRL/SRLI
    return F3[f3]

ctrl_rom = [pack(CTRL[o]) if o in CTRL else 0 for o in range(128)]
alu_rom  = [alu_ctl(a >> 4, (a >> 1) & 7, a & 1) for a in range(64)]

def dump(path, vals):
    with open(path, "w", newline="\n") as f:
        f.write("v2.0 raw\n")
        for i in range(0, len(vals), 8):
            f.write(" ".join(f"{v:x}" for v in vals[i:i+8]) + "\n")
os.makedirs("rom", exist_ok=True)
dump("rom/control.rom", ctrl_rom)
dump("rom/aluctl.rom", alu_rom)

# ---------------- Mo hinh Control (doc lai tu chinh noi dung ROM) ----------------
def control(ins):
    w = ctrl_rom[ins & 0x7F]
    aluop = (w >> 9) & 3
    a = aluop << 4 | ((ins >> 12) & 7) << 1 | ((ins >> 30) & 1)
    return dict(RegWrite=w & 1, ALUSrc=w >> 1 & 1, MemRead=w >> 2 & 1, MemWrite=w >> 3 & 1,
                MemToReg=w >> 4 & 3, Branch=w >> 6 & 1, Jump=w >> 7 & 1, Jalr=w >> 8 & 1,
                ImmSel=w >> 11 & 7, ALUctl=alu_rom[a])

# Gia tri mong doi viet tay cho tung lenh (doc lap voi ROM) de kiem cheo
#             RW Src MR MW M2R Br J Jr Imm ALUctl
EXP = {
 'add':  (1,0,0,0,0,0,0,0,0,0), 'sub': (1,0,0,0,0,0,0,0,0,1), 'and': (1,0,0,0,0,0,0,0,0,2),
 'or':   (1,0,0,0,0,0,0,0,0,3), 'xor': (1,0,0,0,0,0,0,0,0,4), 'slt': (1,0,0,0,0,0,0,0,0,5),
 'sltu': (1,0,0,0,0,0,0,0,0,6), 'sll': (1,0,0,0,0,0,0,0,0,7), 'srl': (1,0,0,0,0,0,0,0,0,8),
 'sra':  (1,0,0,0,0,0,0,0,0,9),
 'addi': (1,1,0,0,0,0,0,0,0,0), 'andi':(1,1,0,0,0,0,0,0,0,2), 'ori': (1,1,0,0,0,0,0,0,0,3),
 'xori': (1,1,0,0,0,0,0,0,0,4), 'slti':(1,1,0,0,0,0,0,0,0,5), 'sltiu':(1,1,0,0,0,0,0,0,0,6),
 'slli': (1,1,0,0,0,0,0,0,0,7), 'srli':(1,1,0,0,0,0,0,0,0,8), 'srai':(1,1,0,0,0,0,0,0,0,9),
 'lw':   (1,1,1,0,1,0,0,0,0,0), 'sw':  (0,1,0,1,0,0,0,0,1,0),
 'beq':  (0,0,0,0,0,1,0,0,2,0), 'bne': (0,0,0,0,0,1,0,0,2,0), 'blt': (0,0,0,0,0,1,0,0,2,0),
 'bge':  (0,0,0,0,0,1,0,0,2,0), 'bltu':(0,0,0,0,0,1,0,0,2,0), 'bgeu':(0,0,0,0,0,1,0,0,2,0),
 'jal':  (1,0,0,0,2,0,1,0,4,0), 'jalr':(1,1,0,0,2,0,0,1,0,0), 'lui': (1,1,0,0,0,0,0,0,3,10),
}
r = lambda: f"x{random.randrange(32)}"
def make(m):
    if m in asm.R:  return f"{m} {r()}, {r()}, {r()}"
    if m in asm.SH: return f"{m} {r()}, {r()}, {random.randrange(32)}"
    if m in asm.I:  return f"{m} {r()}, {r()}, {random.randrange(-2048, 2048)}"
    if m == 'lw':   return f"lw {r()}, {random.randrange(-2048, 2048)}({r()})"
    if m == 'sw':   return f"sw {r()}, {random.randrange(-2048, 2048)}({r()})"
    if m in asm.BR: return f"{m} {r()}, {r()}, {random.randrange(-2048, 2048) * 2}"
    if m == 'jal':  return f"jal {r()}, {random.randrange(-2**19, 2**19) * 2}"
    if m == 'jalr': return f"jalr {r()}, {r()}, {random.randrange(-2048, 2048)}"
    if m == 'lui':  return f"lui {r()}, {random.randrange(2**20)}"

rows = []
for m, exp in EXP.items():
    for k in range(6):
        src = make(m)
        p = src.replace(',', ' ').split()
        w = asm.encode(p[0], p[1:], 0, {})
        c = control(w)
        got = tuple(c[f] for f in ["RegWrite","ALUSrc","MemRead","MemWrite","MemToReg","Branch","Jump","Jalr","ImmSel","ALUctl"])
        assert got == exp, (src, hex(w), got, exp)
        rows.append((w, c, src))
# Lenh dac biet: nop, addi am (bit 30 = 1), lenh 0 (bubble), opcode khong hop le
for src, w in [("nop", 0x00000013), ("addi x1,x1,-1024 (bit30=1)", asm.enc_i(-1024, 1, 0, 1, 0x13)),
               ("0x00000000 (bubble)", 0)]:
    rows.append((w, control(w), src))
valid = set(CTRL)
for op in range(128):
    if op not in valid and op % 9 == 0:
        w = random.getrandbits(25) << 7 | op
        c = control(w); assert all(v == 0 for v in c.values())
        rows.append((w, c, f"opcode khong hop le {op:07b}"))

with open("tests/control.txt", "w", newline="\n") as f:
    f.write("# Test vector Control (Instr -> tin hieu dieu khien). Sinh boi tools/gen_roms.py\n")
    f.write("Instr[32] RegWrite ALUSrc MemRead MemWrite MemToReg[2] Branch Jump Jalr ImmSel[3] ALUctl[4]\n")
    for w, c, src in rows:
        f.write(f"0x{w:08X} {c['RegWrite']} {c['ALUSrc']} {c['MemRead']} {c['MemWrite']} {c['MemToReg']:02b} "
                f"{c['Branch']} {c['Jump']} {c['Jalr']} {c['ImmSel']:03b} {c['ALUctl']:04b}   # {src}\n")
print(f"control.rom: 128 tu, aluctl.rom: 64 tu, control.txt: {len(rows)} dong (kiem cheo voi bang viet tay: OK)")
for o in sorted(CTRL): print(f"  opcode {o:07b} -> 0x{pack(CTRL[o]):04X}")
