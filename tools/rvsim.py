#!/usr/bin/env python3
"""Mo phong tap lenh RV32I (mo hinh tham chieu cho CPU Logisim).

    python tools/rvsim.py asm/test6a_alu.s            # chay va in trang thai cuoi
    python tools/rvsim.py rom/prog.hex -n 200 -t      # -t: in tung lenh

Mo phong dung nhu phan cung trong cac lab:
  - IMEM 1024 word (dia chi PC[11:2]), DMEM 1024 word (dia chi [11:2]), RAM ban dau = 0
  - opcode khong hop le -> khong lam gi (nhu control word = 0), PC = PC + 4
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

M = 0xFFFFFFFF
def s32(x): return x - (1 << 32) if x & 0x80000000 else x
def sext(v, n): return (v - (1 << n)) & M if (v >> (n - 1)) & 1 else v
def bits(x, hi, lo): return (x >> lo) & ((1 << (hi - lo + 1)) - 1)

ABI = "zero ra sp gp tp t0 t1 t2 s0 s1 a0 a1 a2 a3 a4 a5 a6 a7 s2 s3 s4 s5 s6 s7 s8 s9 s10 s11 t3 t4 t5 t6".split()

def mem_load(mem, addr, f3):
    """Giong het khoi LoadExt: v = word >> (addr[1:0]*8), roi cat byte/half va mo rong dau theo funct3."""
    v = mem[(addr >> 2) & 0x3FF] >> ((addr & 3) * 8)
    if f3 == 0: return sext(v & 0xFF, 8)          # LB
    if f3 == 1: return sext(v & 0xFFFF, 16)       # LH
    if f3 == 4: return v & 0xFF                   # LBU
    if f3 == 5: return v & 0xFFFF                 # LHU
    return v                                      # LW (va cac funct3 khac)

def mem_store(mem, addr, val, f3):
    """Giong het khoi StoreMerge: doc-sua-ghi ca word.
    funct3[1:0] = 0 (SB): D = val & 0xFF,   K = 0xFF
                  1 (SH): D = val & 0xFFFF, K = 0xFFFF
                  2/3(SW): D = val,         K = 0xFFFFFFFF
    New = (Old & ~(K << s)) | (D << s),  s = addr[1:0]*8"""
    i, s, k = (addr >> 2) & 0x3FF, (addr & 3) * 8, f3 & 3
    d, m = [(val & 0xFF, 0xFF), (val & 0xFFFF, 0xFFFF), (val, M), (val, M)][k]
    mask = (m << s) & M
    mem[i] = (mem[i] & ~mask & M) | ((d << s) & M)

def is_m(ins):
    """Lenh M-extension: opcode = 0110011 va funct7 = 0000001 (chi can kiem bit 25)."""
    return (ins & 0x7F) == 0x33 and (ins >> 25) & 1 == 1

def muldiv(f3, a, b):
    """Giong khoi MulDiv (Lab 14). Chia cho 0: thuong = 0xFFFFFFFF, du = a (theo dac ta RISC-V)."""
    sa, sb = s32(a), s32(b)
    if f3 == 0: return (a * b) & M                       # MUL
    if f3 == 1: return ((sa * sb) >> 32) & M             # MULH   (co dau x co dau)
    if f3 == 2: return ((sa * b) >> 32) & M              # MULHSU (co dau x khong dau)
    if f3 == 3: return ((a * b) >> 32) & M               # MULHU
    if b == 0: return M if f3 in (4, 5) else a           # chia cho 0
    if f3 == 4:                                          # DIV (lam tron ve 0; -2^31/-1 = -2^31)
        q = abs(sa) // abs(sb); return (-q if (sa < 0) != (sb < 0) else q) & M
    if f3 == 5: return a // b                            # DIVU
    if f3 == 6:                                          # REM (dau theo so bi chia)
        r = abs(sa) % abs(sb); return (-r if sa < 0 else r) & M
    return a % b                                         # REMU

IO_BASE = 0x80000000
def is_io(addr):
    """Lab 15: dia chi >= 0x80000000 la vung I/O (khoi MemMap so sanh Addr < 0x80000000)."""
    return addr >= IO_BASE

class IO:
    """Giong circuit IO (Lab 15). Chon thiet bi bang Addr[3:2]:
       0x80000000 LED  (ghi/doc)      0x80000004 HEX (ghi/doc, 8 LED 7 doan)
       0x80000008 UART TX: ghi = gui ky tu ra TTY, doc = 1 (luon san sang)
       0x8000000C SW   (doc, 8 cong tac DIP)"""
    def __init__(self, sw=0):
        self.led, self.hex, self.sw, self.tty = 0, 0, sw & 0xFF, []
    def read(self, addr):
        return [self.led, self.hex, 1, self.sw][(addr >> 2) & 3]
    def write(self, addr, val):
        k = (addr >> 2) & 3
        if k == 0: self.led = val
        elif k == 1: self.hex = val
        elif k == 2: self.tty.append(val & 0x7F)
    def text(self):
        return "".join(chr(c) for c in self.tty)

class RV:
    def __init__(self, words, sw=0):
        self.io = IO(sw)
        self.imem = [0] * 1024
        for i, w in enumerate(words[:1024]): self.imem[i] = w
        self.x = [0] * 32
        self.mem = [0] * 1024
        self.pc = 0

    def step(self):
        """Thuc thi 1 lenh. Tra ve ban ghi nhung gi CPU phai the hien trong chu ky nay."""
        pc, ins = self.pc, self.imem[(self.pc >> 2) & 0x3FF]
        op, rd, f3 = ins & 0x7F, bits(ins, 11, 7), bits(ins, 14, 12)
        rs1, rs2, b30 = bits(ins, 19, 15), bits(ins, 24, 20), bits(ins, 30, 30)
        a, b = self.x[rs1], self.x[rs2]
        iI = sext(bits(ins, 31, 20), 12)
        iS = sext(bits(ins, 31, 25) << 5 | bits(ins, 11, 7), 12)
        iB = sext(bits(ins, 31, 31) << 12 | bits(ins, 7, 7) << 11 | bits(ins, 30, 25) << 5 | bits(ins, 11, 8) << 1, 13)
        iU = ins & 0xFFFFF000
        iJ = sext(bits(ins, 31, 31) << 20 | bits(ins, 19, 12) << 12 | bits(ins, 20, 20) << 11 | bits(ins, 30, 21) << 1, 21)
        rec = dict(pc=pc, ins=ins, regwrite=0, rd=None, wb=None, memwrite=0, maddr=None, mwdata=None, iowrite=0, iordata=0)
        npc = (pc + 4) & M

        def alu(f3, x, y, sub_or_sra):
            sh = y & 31
            if f3 == 0: return (x - y if sub_or_sra else x + y) & M
            if f3 == 1: return (x << sh) & M
            if f3 == 2: return int(s32(x) < s32(y))
            if f3 == 3: return int(x < y)
            if f3 == 4: return x ^ y
            if f3 == 5: return (s32(x) >> sh) & M if sub_or_sra else x >> sh
            if f3 == 6: return x | y
            return x & y

        wb = None
        if op == 0x33 and is_m(ins):                     # M-extension (Lab 14)
            wb = muldiv(f3, a, b)
        elif op == 0x33:                                 # R-type
            wb = alu(f3, a, b, b30)
        elif op == 0x13:                                 # I-type ALU
            wb = alu(f3, a, iI & M, b30 if f3 == 5 else 0)
        elif op == 0x03:                                 # LOAD (LB LH LW LBU LHU)
            addr = (a + iI) & M
            rec['maddr'] = addr
            if is_io(addr): wb = rec['iordata'] = self.io.read(addr)     # I/O: luon doc ca word
            else: wb = mem_load(self.mem, addr, f3)
        elif op == 0x23:                                 # STORE (SB SH SW)
            addr = (a + iS) & M
            rec.update(memwrite=1, maddr=addr, mwdata=b)
            if is_io(addr): rec['iowrite'] = 1; self.io.write(addr, b)   # khong ghi vao RAM
            else: mem_store(self.mem, addr, b, f3)
        elif op == 0x63:                                 # BRANCH
            cond = {0: a == b, 1: a != b, 4: s32(a) < s32(b), 5: s32(a) >= s32(b),
                    6: a < b, 7: a >= b}.get(f3, False)
            if cond: npc = (pc + iB) & M
        elif op == 0x6F:                                 # JAL
            wb, npc = (pc + 4) & M, (pc + iJ) & M
        elif op == 0x67:                                 # JALR
            wb, npc = (pc + 4) & M, ((a + iI) & M) & ~1 & M
        elif op == 0x37:                                 # LUI
            wb = iU
        if wb is not None:
            rec.update(regwrite=1, rd=rd, wb=wb)
            if rd: self.x[rd] = wb
        self.pc = npc
        return rec

def load_words(path, pad=0, pad_load=0, pad_ctl=0):
    if path.endswith('.s'):
        import asm
        return asm.assemble(path, pad, pad_load, pad_ctl)[0]
    words = []
    for line in open(path).read().split('\n')[1:]:
        words += [int(w, 16) for w in line.split()]
    return words

import re as _re
def parse_expect(path):
    """Doc cac dong '# EXPECT <x5|a0|MEM[0x100]> = <gia tri>' trong file .s"""
    if not path.endswith('.s'): return []
    out = []
    for line in open(path, encoding='utf-8-sig'):
        m = _re.match(r'\s*#\s*EXPECT\s+TTY\s*=\s*(".*")\s*$', line)
        if m:
            import ast; out.append(("TTY", ast.literal_eval(m.group(1)))); continue
        m = _re.match(r'\s*#\s*EXPECT\s+(\S+)\s*=\s*(\S+)', line)
        if m: out.append((m.group(1), int(m.group(2), 0) & M))
    return out

def parse_sw(path):
    """Gia tri cong tac DIP dung khi mo phong: dong '# SW = 0x5A' trong file .s (mac dinh 0)."""
    if not path.endswith('.s'): return 0
    for line in open(path, encoding='utf-8-sig'):
        m = _re.match(r'\s*#\s*SW\s*=\s*(\S+)', line)
        if m: return int(m.group(1), 0)
    return 0

def read_target(rv, name):
    if name == "TTY": return rv.io.text()
    if name.upper() == "LED": return rv.io.led
    if name.upper() == "HEX": return rv.io.hex
    m = _re.match(r'MEM\[(\w+)\]', name, _re.I)
    if m: return rv.mem[(int(m.group(1), 0) >> 2) & 0x3FF]
    import asm
    return rv.x[asm.REGS[name]]

def run_to_halt(words, max_cycles=100000, sw=0):
    """Chay toi vong lap dung 'j .'; tra ve (rv, so lenh da thuc thi, co gap vong lap dung khong)."""
    rv = RV(words, sw)
    for n in range(1, max_cycles + 1):
        pc = rv.pc
        rv.step()
        if rv.pc == pc: return rv, n, True
    return rv, max_cycles, False

def check_expect(path, rv):
    return [(name, exp, read_target(rv, name)) for name, exp in parse_expect(path)]

def dump_regs(x):
    out = []
    for i in range(0, 32, 4):
        out.append("   ".join(f"x{j:<2}({ABI[j]:>4}) = 0x{x[j]:08X}" for j in range(i, i + 4)))
    return "\n".join(out)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prog", help=".s hoac .hex")
    ap.add_argument("-n", type=int, default=1000, help="so chu ky toi da")
    ap.add_argument("-t", action="store_true", help="in tung lenh")
    a = ap.parse_args()
    import asm
    rv = RV(load_words(a.prog), parse_sw(a.prog))
    seen_halt = 0
    for cyc in range(a.n):
        pc = rv.pc
        r = rv.step()
        if a.t:
            extra = f"x{r['rd']} <- 0x{r['wb']:08X}" if r['regwrite'] and r['rd'] else ""
            if r['memwrite']: extra = f"{'IO' if r['iowrite'] else 'MEM'}[0x{r['maddr']:08X}] <- 0x{r['mwdata']:08X}"
            print(f"{cyc:4d}  pc={pc:08X}  {r['ins']:08X}  {extra}")
        if rv.pc == pc:                                # vong lap "done: j done"
            seen_halt = 1; break
    print(f"\nDung sau {cyc + 1} chu ky" + (" (gap vong lap dung tai PC=0x%08X)" % rv.pc if seen_halt else ""))
    print(dump_regs(rv.x))
    exps = check_expect(a.prog, rv)
    if exps:
        bad = [(n, e, g) for n, e, g in exps if e != g]
        print(f"\nKiem tra EXPECT: {len(exps) - len(bad)}/{len(exps)} dung")
        f = lambda v: repr(v) if isinstance(v, str) else f"0x{v:08X}"
        for n, e, g in bad: print(f"  SAI {n}: mong doi {f(e)}, mo phong ra {f(g)}")
    io = rv.io
    if io.led or io.hex or io.tty:
        print(f"\nI/O: LED = 0x{io.led:08X}   HEX = 0x{io.hex:08X}   SW = 0x{io.sw:02X}   TTY = {io.text()!r}")
    used = [(i * 4, v) for i, v in enumerate(rv.mem) if v]
    if used:
        print("\nO nho khac 0:")
        for addr, v in used: print(f"  MEM[0x{addr:03X}] = 0x{v:08X} ({s32(v)})")

if __name__ == "__main__":
    main()
