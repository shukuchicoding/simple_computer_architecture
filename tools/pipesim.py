#!/usr/bin/env python3
"""Mo hinh CPU pipeline 5 tang IF-ID-EX-MEM-WB, chinh xac tung chu ky, dung nhu phan cung trong cac lab.

    python tools/pipesim.py asm/t2_sum.s --lab 8 --pad 3        # in trang thai cuoi
    python tools/pipesim.py asm/t7_hazard.s --lab 11 -t         # -t: in noi dung tung tang moi chu ky

Cac muc (--lab):
   8 : chua xu ly hazard (khong forwarding, khong stall, khong flush)
   9 : + forwarding EX/MEM, MEM/WB -> EX va bypass WB -> ID trong RegFile
  10 : + stall 1 chu ky khi load-use
  11 : + flush 2 lenh sai duong khi nhay (du doan khong nhay, quyet dinh o EX)
  16 : + du doan nhanh dong: BTB 16 muc + bo dem bao hoa 2 bit (tra cuu o IF, cap nhat o EX)

Thiet ke duoc mo hinh hoa:
  - Nhay quyet dinh o EX: PCnext = (Branch&Taken | Jump) ? PC_EX + Imm : (Jalr ? (ALU & ~1) : PC_IF + 4)
  - Ket qua EX: Result = MemToReg[1] ? PC4 : ALUout  (JAL/JALR mang PC+4 di tiep)
  - WB: MemToReg[0] ? RData : Result
  - RegFile ghi o canh len; doc cung chu ky voi ghi -> doc gia tri CU (tru khi co bypass, lab >= 9)
  - Bubble = control word 0 (IF/ID flush -> Instr = 0)
"""
import argparse, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rvsim

M = 0xFFFFFFFF
s32, sext, bits = rvsim.s32, rvsim.sext, rvsim.bits

# Bang dieu khien giong Control ROM (Lab 5)
CTRL = {0x33: (1,0,0,0,0,0,0,0,2,0), 0x13: (1,1,0,0,0,0,0,0,3,0), 0x03: (1,1,1,0,1,0,0,0,0,0),
        0x23: (0,1,0,1,0,0,0,0,0,1), 0x63: (0,0,0,0,0,1,0,0,0,2), 0x6F: (1,0,0,0,2,0,1,0,0,4),
        0x67: (1,1,0,0,2,0,0,1,0,0), 0x37: (1,1,0,0,0,0,0,0,1,3)}
F3 = {1: 7, 2: 5, 3: 6, 4: 4, 6: 3, 7: 2}

def decode(ins):
    rw, src, mr, mw, m2r, br, j, jr, aluop, isel = CTRL.get(ins & 0x7F, (0,) * 10)
    f3, b30 = bits(ins, 14, 12), bits(ins, 30, 30)
    if aluop == 0: aluctl = 0
    elif aluop == 1: aluctl = 10
    elif f3 == 0: aluctl = 1 if (aluop == 2 and b30) else 0
    elif f3 == 5: aluctl = 9 if b30 else 8
    else: aluctl = F3[f3]
    imm = [sext(bits(ins, 31, 20), 12),
           sext(bits(ins, 31, 25) << 5 | bits(ins, 11, 7), 12),
           sext(bits(ins, 31, 31) << 12 | bits(ins, 7, 7) << 11 | bits(ins, 30, 25) << 5 | bits(ins, 11, 8) << 1, 13),
           ins & 0xFFFFF000,
           sext(bits(ins, 31, 31) << 20 | bits(ins, 19, 12) << 12 | bits(ins, 20, 20) << 11 | bits(ins, 30, 21) << 1, 21),
           0, 0, 0][isel]
    return dict(regwrite=rw, alusrc=src, memread=mr, memwrite=mw, m2r=m2r, branch=br, jump=j, jalr=jr,
                aluctl=aluctl, imm=imm, rs1=bits(ins, 19, 15), rs2=bits(ins, 24, 20), rd=bits(ins, 11, 7), f3=f3)

def alu(ctl, a, b):
    sh = b & 31
    return [a + b, a - b, a & b, a | b, a ^ b, int(s32(a) < s32(b)), int(a < b),
            a << sh, a >> sh, s32(a) >> sh, b, 0, 0, 0, 0, 0][ctl] & M

def taken(f3, a, b):
    return {0: a == b, 1: a != b, 4: s32(a) < s32(b), 5: s32(a) >= s32(b), 6: a < b, 7: a >= b}.get(f3, False)

CTRL_KEYS = ("regwrite", "alusrc", "memread", "memwrite", "m2r", "branch", "jump", "jalr", "aluctl")
def bubble_idex(d):
    d = dict(d); d.update({k: 0 for k in CTRL_KEYS}); d["instr"] = 0; d["pred"] = 0; return d

# Bang chuyen trang thai bo dem 2 bit: CTR_NEXT[taken][ctr]  (giong ROM trong khoi BTB)
CTR_NEXT = [[0, 0, 1, 2], [1, 2, 3, 3]]

class BTB:
    """Giong khoi BTB (Lab 16): 2 RegFile 32 x 32, chi dung o 16..31; chi so = 16 | PC[5:2].
       TAG[i] = PC | 1   (bit 0 = 1 danh dau muc hop le; sau Reset TAG = 0 -> khong khop)
       TGT[i] = {dich[31:2], bo dem 2 bit}"""
    def __init__(self):
        self.tag = [0] * 32; self.tgt = [0] * 32
    @staticmethod
    def idx(pc): return 16 | ((pc >> 2) & 15)
    def lookup(self, pc):
        i = self.idx(pc)
        hit = self.tag[i] == (pc | 1)
        return int(hit and (self.tgt[i] >> 1) & 1), self.tgt[i] & ~3 & M
    def update(self, pc, target, taken):
        i = self.idx(pc)
        hit = self.tag[i] == (pc | 1)
        if not (hit or taken): return                    # khong cap phat muc moi cho nhanh khong nhay
        ctr = CTR_NEXT[int(taken)][self.tgt[i] & 3] if hit else 2
        self.tag[i] = pc | 1
        self.tgt[i] = (target & ~3 & M) | ctr

class Pipe:
    def __init__(self, words, lab=11, sw=0):
        self.io = rvsim.IO(sw)
        self.fwd = lab >= 9; self.stall_en = lab >= 10; self.flush_en = lab >= 11; self.bp = lab >= 16
        self.btb = BTB()
        self.mispred = 0
        self.imem = [0] * 1024
        for i, w in enumerate(words[:1024]): self.imem[i] = w
        self.x = [0] * 32; self.mem = [0] * 1024; self.pc = 0
        z = dict(pc=0, pc4=0, instr=0)
        self.ifid = dict(z, pred=0)
        self.idex = bubble_idex(dict(pc=0, pc4=0, rd1=0, rd2=0, imm=0, rs1=0, rs2=0, rd=0, f3=0, pred=0))
        self.idex["alusrc"] = 0
        self.exmem = dict(pc=0, result=0, wdata=0, rd=0, f3=0, instr=0, regwrite=0, memread=0, memwrite=0, m2r=0)
        self.memwb = dict(pc=0, result=0, rdata=0, rd=0, instr=0, regwrite=0, m2r=0)
        self.cycle = 0
        self.stalls = self.flushes = 0

    def step(self):
        """Mo phong 1 chu ky. Tra ve ban ghi cac gia tri quan sat duoc TRUOC canh len."""
        ifid, idex, exmem, memwb = self.ifid, self.idex, self.exmem, self.memwb
        # ---- WB
        wbval = memwb["rdata"] if memwb["m2r"] & 1 else memwb["result"]
        wb_we = memwb["regwrite"] and memwb["rd"] != 0
        # ---- MEM
        io_acc = rvsim.is_io(exmem["result"])                          # Lab 15: khoi MemMap
        iordata = self.io.read(exmem["result"])
        rdata = iordata if io_acc else rvsim.mem_load(self.mem, exmem["result"], exmem["f3"])
        # ---- EX (forwarding)
        def fwd(rs, val):
            if self.fwd:
                if exmem["regwrite"] and exmem["rd"] and exmem["rd"] == rs: return exmem["result"]
                if memwb["regwrite"] and memwb["rd"] and memwb["rd"] == rs: return wbval
            return val
        a = fwd(idex["rs1"], idex["rd1"])
        breg = fwd(idex["rs2"], idex["rd2"])
        aluout = alu(idex["aluctl"], a, idex["imm"] if idex["alusrc"] else breg)
        if rvsim.is_m(idex["instr"]): aluout = rvsim.muldiv(idex["f3"], a, breg)   # Lab 14: MUX sau ALU
        t = taken(idex["f3"], a, breg)
        selbr = (idex["branch"] and t) or idex["jump"]
        result = idex["pc4"] if idex["m2r"] & 2 else aluout
        brt = (idex["pc"] + idex["imm"]) & M
        if self.bp:                                                     # Lab 16: so voi du doan
            mt = selbr and not idex["pred"]                             # doan khong nhay, thuc te nhay
            mn = idex["pred"] and not selbr                             # doan nhay, thuc te khong nhay
            pcsel = bool(mt or mn or idex["jalr"])
            target = (aluout & ~1 & M) if idex["jalr"] else (brt if mt else idex["pc4"])
            self.mispred += bool(mt or mn)
        else:
            pcsel = selbr or idex["jalr"]
            target = (aluout & ~1 & M) if idex["jalr"] else brt
        # ---- ID
        d = decode(ifid["instr"])
        def rf(r):
            if self.fwd and wb_we and memwb["rd"] == r: return wbval      # bypass WB -> ID
            return self.x[r]
        rd1_d, rd2_d = rf(d["rs1"]), rf(d["rs2"])                       # doc TRUOC canh len (gia tri cu)
        stall = bool(self.stall_en and idex["memread"] and idex["rd"] and idex["rd"] in (d["rs1"], d["rs2"]))
        flush = bool(self.flush_en and pcsel)
        # ---- IF
        instr_f = self.imem[(self.pc >> 2) & 0x3FF]
        pc4_f = (self.pc + 4) & M
        pred_f, ptgt_f = self.btb.lookup(self.pc) if self.bp else (0, 0)

        rec = dict(pc=self.pc, instr=instr_f,
                   regwrite=memwb["regwrite"], rd=memwb["rd"], wb=wbval,
                   memwrite=exmem["memwrite"], memread=exmem["memread"],
                   maddr=exmem["result"], mwdata=exmem["wdata"],
                   iowrite=int(bool(exmem["memwrite"] and io_acc)), iordata=iordata if (exmem["memread"] and io_acc) else 0,
                   stall=stall, flush=flush,
                   stages=(self.pc, ifid["pc"], idex["pc"], exmem["pc"], memwb["pc"]),
                   instrs=(instr_f, ifid["instr"], idex["instr"], exmem["instr"], memwb["instr"]))

        # ---- canh len
        if wb_we: self.x[memwb["rd"]] = wbval
        if exmem["memwrite"]:
            if io_acc: self.io.write(exmem["result"], exmem["wdata"])
            else: rvsim.mem_store(self.mem, exmem["result"], exmem["wdata"], exmem["f3"])
        self.memwb = dict(pc=exmem["pc"], result=exmem["result"], rdata=rdata, rd=exmem["rd"], instr=exmem["instr"],
                          regwrite=exmem["regwrite"], m2r=exmem["m2r"])
        self.exmem = dict(pc=idex["pc"], result=result, wdata=breg, rd=idex["rd"], f3=idex["f3"], instr=idex["instr"],
                          regwrite=idex["regwrite"], memread=idex["memread"], memwrite=idex["memwrite"], m2r=idex["m2r"])
        new_idex = dict(pc=ifid["pc"], pc4=ifid["pc4"], rd1=rd1_d, rd2=rd2_d, imm=d["imm"],
                        rs1=d["rs1"], rs2=d["rs2"], rd=d["rd"], f3=d["f3"], instr=ifid["instr"], pred=ifid["pred"],
                        **{k: d[k] for k in CTRL_KEYS})
        self.idex = bubble_idex(new_idex) if (stall or flush) else new_idex
        if flush:
            self.ifid = dict(pc=self.pc, pc4=pc4_f, instr=0, pred=0)
        elif not stall:
            self.ifid = dict(pc=self.pc, pc4=pc4_f, instr=instr_f, pred=pred_f)
        if pcsel: self.pc = target
        elif not stall: self.pc = ptgt_f if pred_f else pc4_f
        if self.bp and (idex["branch"] or idex["jump"]):              # cap nhat BTB o canh len
            self.btb.update(idex["pc"], brt, bool(selbr))
        self.stalls += stall; self.flushes += flush
        self.cycle += 1
        return rec

def run(words, lab, max_cycles=20000, halt_pc=None, drain=3, sw=0):
    """Chay toi khi lenh dung (j .) tai halt_pc da toi tang WB 2 lan, them 'drain' chu ky."""
    p, recs, seen, left = Pipe(words, lab, sw), [], 0, None
    halt_ins = p.imem[(halt_pc >> 2) & 0x3FF] if halt_pc is not None else None
    for _ in range(max_cycles):
        r = p.step(); recs.append(r)
        if halt_pc is not None and r["stages"][4] == halt_pc and r["instrs"][4] == halt_ins: seen += 1
        if left is None and seen >= 2: left = drain
        if left is not None:
            left -= 1
            if left <= 0: break
    return p, recs

STAGE = ["IF", "ID", "EX", "MEM", "WB"]
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("prog")
    ap.add_argument("--lab", type=int, default=11, choices=[8, 9, 10, 11, 16])
    ap.add_argument("--pad", type=int, default=0, help="chen N nop sau moi lenh")
    ap.add_argument("--pad-load", type=int, default=0, help="chen N nop sau moi lenh load")
    ap.add_argument("--pad-ctl", type=int, default=0, help="chen N nop sau moi lenh nhay")
    ap.add_argument("-n", type=int, default=20000)
    ap.add_argument("-t", action="store_true", help="in tung chu ky")
    a = ap.parse_args()
    import asm
    words = rvsim.load_words(a.prog, a.pad, a.pad_load, a.pad_ctl)
    listing = {pc: t for pc, _, t in asm.assemble(a.prog, a.pad, a.pad_load, a.pad_ctl)[1]} if a.prog.endswith(".s") else {}
    sw = rvsim.parse_sw(a.prog)
    ref, ninstr, halted = rvsim.run_to_halt(words, sw=sw)
    p, recs = run(words, a.lab, a.n, ref.pc if halted else None, sw=sw)
    if a.t:
        for c, r in enumerate(recs):
            cells = []
            for st, pc, ins in zip(STAGE, r["stages"], r["instrs"]):
                txt = "bubble" if ins == 0 else listing.get(pc, f"{ins:08x}")
                cells.append(f"{st}:{txt[:18]:18s}")
            tag = (" STALL" if r["stall"] else "") + (" FLUSH" if r["flush"] else "")
            print(f"{c:4d} " + " | ".join(cells) + tag)
    if a.lab >= 16: print(f"\nDu doan sai: {p.mispred} lan")
    print(f"\nPipeline lab {a.lab}: {len(recs)} chu ky, {p.stalls} stall, {p.flushes} flush; "
          f"single-cycle: {ninstr} lenh -> CPI ~ {len(recs) / max(ninstr, 1):.2f}")
    diff = [i for i in range(32) if p.x[i] != ref.x[i]]
    mdiff = [i for i in range(1024) if p.mem[i] != ref.mem[i]]
    iodiff = (p.io.led, p.io.hex, p.io.tty) != (ref.io.led, ref.io.hex, ref.io.tty)
    if iodiff:
        print(f"  I/O khac: pipeline LED=0x{p.io.led:08X} HEX=0x{p.io.hex:08X} TTY={p.io.text()!r}; "
              f"dung la LED=0x{ref.io.led:08X} HEX=0x{ref.io.hex:08X} TTY={ref.io.text()!r}")
    if not diff and not mdiff and not iodiff:
        print("Trang thai cuoi KHOP voi mo hinh tap lenh (rvsim).")
    else:
        print("Trang thai cuoi KHAC mo hinh tap lenh (chuong trinh chua an toan voi muc hazard nay):")
        for i in diff: print(f"  x{i}: pipeline 0x{p.x[i]:08X}, dung la 0x{ref.x[i]:08X}")
        for i in mdiff[:10]: print(f"  MEM[0x{i*4:03X}]: pipeline 0x{p.mem[i]:08X}, dung la 0x{ref.mem[i]:08X}")

if __name__ == "__main__":
    main()
