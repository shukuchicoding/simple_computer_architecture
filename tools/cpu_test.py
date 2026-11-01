#!/usr/bin/env python3
"""Kiem thu CPU bang cach so sanh TUNG CHU KY voi mo hinh tham chieu.

Single-cycle (mo hinh: rvsim.py), circuit "CPU" trong single/riscv_single.circ:
    python tools/cpu_test.py "asm/t*_*.s" --jar <logisim.jar>
Pipeline (mo hinh: pipesim.py), circuit "CPU" trong pipeline/riscv_pipe.circ:
    python tools/cpu_test.py "asm/t[1-6]_*.s" --pipe 8 --pad 3 --jar <logisim.jar>    (Lab 8: chen 3 nop)
    python tools/cpu_test.py "asm/t*_*.s"     --pipe 11 --jar <logisim.jar>          (Lab 11: day du)
    python tools/cpu_test.py "asm/t*_*.s"     --pipe 16 --jar <logisim.jar>          (Lab 16: + du doan nhanh)
Chi sinh test vector de chay bang giao dien (tu nap ROM bang file .hex tuong ung):
    python tools/cpu_test.py asm/t2_sum.s --gen tests/cpu_t2.txt [--pipe 8 --pad 3]
Bang ket qua cho bao cao: them --md report/ket_qua.md --label "..."

File .circ goc khong bi sua (chuong trinh duoc nap vao ROM cua mot BAN SAO).
Circuit duoc kiem phai co cac pin:
   in : clk, Reset
   out: PC[32] Instr[32] RegWrite rd[5] WB[32] MemWrite MemAddr[32] MemWData[32]
   (Lab 15, tu nhan biet) them: in IORData[32], out IOWrite
Y nghia o pipeline: PC/Instr = tang IF; RegWrite/rd/WB = tang WB; MemWrite/MemAddr/MemWData = tang MEM.
"""
import argparse, glob, os, re, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import asm, rvsim, pipesim

H = lambda v: f"0x{v:08X}"
HEADER = "<set> <seq> clk Reset PC[32] Instr[32] RegWrite rd[5] WB[32] MemWrite MemAddr[32] MemWData[32]"
STAGE = ["IF", "ID", "EX", "MEM", "WB"]

# ---------------------------------------------------------------- tao ban ghi tung chu ky
def trace_single(words, max_cycles, sw=0):
    rv, recs, extra = rvsim.RV(words, sw), [], None
    for _ in range(max_cycles):
        pc = rv.pc
        r = rv.step()
        recs.append(dict(pc=r["pc"], instr=r["ins"], regwrite=r["regwrite"], rd=r["rd"], wb=r["wb"],
                         memwrite=r["memwrite"], maddr=r["maddr"], mwdata=r["mwdata"], stages=None,
                         iowrite=r["iowrite"], iordata=r["iordata"]))
        if extra is None and (rv.pc == pc or rv.pc >= 4 * len(words) + 8): extra = 2
        if extra is not None:
            extra -= 1
            if extra < 0: break
    return recs, dict(cycles=len(recs))

def trace_pipe(words, lab, max_cycles, sw=0):
    ref, ninstr, halted = rvsim.run_to_halt(words, sw=sw)
    if halted: max_cycles = min(max_cycles, 4 * ninstr + 100)      # tranh chay mai khi hazard lam chuong trinh lap vo han
    else: max_cycles = min(max_cycles, len(words) + 12)               # chuong trinh khong co vong dung: chay het roi xa pipeline
    p, raw = pipesim.run(words, lab, max_cycles, ref.pc if halted else None, sw=sw)
    recs = []
    for r in raw:
        mem = r["memwrite"] or r["memread"]
        recs.append(dict(pc=r["pc"], instr=r["instr"], regwrite=r["regwrite"], rd=r["rd"], wb=r["wb"],
                         memwrite=r["memwrite"], maddr=r["maddr"] if mem else None,
                         mwdata=r["mwdata"] if r["memwrite"] else None,
                         stages=list(zip(r["stages"], r["instrs"])), stall=r["stall"], flush=r["flush"],
                         iowrite=r["iowrite"], iordata=r["iordata"]))
    same = p.x == ref.x and p.mem == ref.mem and (p.io.led, p.io.hex, p.io.tty) == (ref.io.led, ref.io.hex, ref.io.tty)
    return recs, dict(cycles=len(recs), ninstr=ninstr if halted else None, stalls=p.stalls, flushes=p.flushes,
                      model_ok=same)

IO_COLS = False      # True khi circuit CPU co pin IORData/IOWrite (Lab 15)
def row(seq, clk, r):
    rd = f"{r['rd']:05b}" if r["regwrite"] else "<DC>"
    wb = H(r["wb"]) if r["regwrite"] else "<DC>"
    ma = H(r["maddr"]) if r["maddr"] is not None else "<DC>"
    md = H(r["mwdata"]) if r["mwdata"] is not None else "<DC>"
    io = f" {H(r['iordata'])} {r['iowrite']}" if IO_COLS else ""
    return f"1 {seq} {clk} 0 {H(r['pc'])} {H(r['instr'])} {r['regwrite']} {rd} {wb} {r['memwrite']} {ma} {md}{io}"

def gen_vector(recs, note=""):
    lines = [f"# Test vector CPU (tung chu ky) {note}",
             "# Dong clk=0: trang thai chu ky hien tai; dong clk=1: ngay sau canh len (chu ky ke tiep)",
             HEADER + (" IORData[32] IOWrite" if IO_COLS else "")]
    seq = 1
    lines.append(row(seq, 0, recs[0])); seq += 1
    for k in range(1, len(recs)):
        lines.append(row(seq, 1, recs[k])); seq += 1
        lines.append(row(seq, 0, recs[k])); seq += 1
    return "\n".join(lines) + "\n"

# ---------------------------------------------------------------- nap ROM vao ban sao .circ
def patch_rom(circ_text, words):
    m = re.search(r'<circuit name="IMEM">.*?</circuit>', circ_text, re.S)
    if not m: sys.exit("LOI: khong tim thay circuit IMEM trong file .circ")
    block = m.group(0)
    rom = re.search(r'(<comp lib="\d+" loc="[^"]*" name="ROM">)(.*?)(</comp>)', block, re.S)
    if not rom: sys.exit("LOI: khong tim thay ROM trong IMEM")
    body = rom.group(2)
    data = "addr/data: 10 32\n" + "\n".join(" ".join(f"{w:x}" for w in words[i:i+8]) for i in range(0, len(words), 8)) + "\n"
    if '<a name="contents">' in body:
        body = re.sub(r'<a name="contents">.*?</a>', lambda _: f'<a name="contents">{data}</a>', body, flags=re.S)
    else:
        body += f'      <a name="contents">{data}</a>\n'
    block2 = block[:rom.start(2)] + body + block[rom.end(2):]
    return circ_text[:m.start()] + block2 + circ_text[m.end():]

def run_logisim(java, jar, circuit, circ_path, circ_text, words, vec_text):
    tmp_circ = os.path.join(os.path.dirname(os.path.abspath(circ_path)), "_cpu_test_tmp.circ")  # cung thu muc: giu duong dan thu vien
    fd, tmp_vec = tempfile.mkstemp(suffix=".txt"); os.close(fd)
    try:
        open(tmp_circ, "w", encoding="utf-8").write(patch_rom(circ_text, words))
        open(tmp_vec, "w", newline="\n").write(vec_text)
        r = subprocess.run([java, "-jar", jar, "--test-vector", circuit, tmp_vec, tmp_circ],
                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    finally:
        for f in (tmp_circ, tmp_vec):
            try: os.remove(f)
            except OSError: pass
    return r.stdout

# ---------------------------------------------------------------- doc va in loi
def hx(b):
    b = b.replace(" ", "")
    if not b or set(b) - set("01"):
        return b + ("  (U = tha noi/chua noi, E = xung dot)" if set(b) & set("UXE") else "")
    return f"0x{int(b, 2):0{max(1, (len(b) + 3) // 4)}X}"

def report_errors(out, recs, listing, verbose):
    errs = []
    for blk in re.split(r"Error on test vector ", out)[1:]:
        mnum = re.match(r"(\d+):", blk)
        if not mnum: continue
        diffs = re.findall(r"^\s+(\S+) = ([^()\n]+?) \(expected ([^()\n]+?)\)", blk, re.M)
        errs.append((int(mnum.group(1)), diffs))
    def txt(pc, ins):
        return "bubble" if ins == 0 else (listing.get(pc) or f"{ins:08x}")
    for idx, diffs in errs[: (20 if verbose else 3)]:
        k = idx // 2                     # dong 1 -> chu ky 0; dong 2,3 -> chu ky 1; ...
        r = recs[k] if k < len(recs) else None
        clk = 0 if idx == 1 or idx % 2 == 1 else 1
        if r is None:
            print(f"    dong {idx}:"); continue
        if r["stages"] is None:
            print(f"    dong {idx} (chu ky {k}, clk={clk}): PC={H(r['pc'])}  {txt(r['pc'], r['instr'])}")
        else:
            st = "  ".join(f"{s}:{txt(pc, ins)}" for s, (pc, ins) in zip(STAGE, r["stages"]))
            print(f"    dong {idx} (chu ky {k}, clk={clk}{', STALL' if r['stall'] else ''}{', FLUSH' if r['flush'] else ''}):")
            print(f"        cac tang theo mo hinh -> {st}")
        for name, got, exp in diffs:
            print(f"        {name:9s} = {hx(got):12s} (mong doi {hx(exp)})")
    if not verbose and len(errs) > 3: print(f"    ... con {len(errs) - 3} dong loi (them -v de xem)")
    print("    Goi y: loi o dong DAU TIEN la quan trong nhat; cac dong sau thuong la he qua.")

# ---------------------------------------------------------------- bang bao cao
def describe(path):
    if path.endswith(".s"):
        for line in open(path, encoding="utf-8-sig"):
            if line.strip().startswith("#"): return line.strip().lstrip("#").strip()
    return ""

def write_md(path, results, label, pipe):
    if pipe:
        head = ["| Chuong trinh | Muc dich | So lenh | Chu ky | CPI | Stall | Flush | Dong test dat | Ket qua |",
                "|---|---|---|---|---|---|---|---|---|"]
    else:
        head = ["| Chuong trinh | Muc dich | So lenh | Chu ky | Dong test dat | EXPECT | Ket qua |",
                "|---|---|---|---|---|---|---|"]
    rows = []
    for p, info, ps, fl, exps in results:
        status = "LOI CHAY" if ps is None else ("PASS" if fl == 0 else "FAIL")
        tests = "-" if ps is None else f"{ps}/{ps + fl}"
        ninstr = info.get("ninstr")
        if pipe:
            cpi = f"{info['cycles'] / ninstr:.2f}" if ninstr else "-"
            rows.append(f"| `{os.path.basename(p)}` | {describe(p)} | {ninstr or '-'} | {info['cycles']} | {cpi} | "
                        f"{info['stalls']} | {info['flushes']} | {tests} | **{status}** |")
        else:
            e = f"{sum(x == y for _, x, y in exps)}/{len(exps)}" if exps else "-"
            rows.append(f"| `{os.path.basename(p)}` | {describe(p)} | {ninstr or '-'} | {info['cycles']} | {tests} | {e} | **{status}** |")
    note = ("\n\n*So lenh*: so lenh thuc thi (mo hinh tap lenh) toi vong lap dung. *Chu ky*: so chu ky da so sanh "
            "(gom ca chu ky nap/xa pipeline). *Dong test dat*: so dong test vector khop (2 dong/chu ky).\n")
    if os.path.dirname(path): os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(f"## Ket qua kiem thu CPU {label}".rstrip() + "\n\n" + "\n".join(head + rows) + note)
    print(f"Da ghi bang ket qua: {path}")

# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("progs", nargs="+")
    ap.add_argument("--pipe", type=int, choices=[8, 9, 10, 11, 16], help="kiem CPU pipeline o muc lab nay (16 = co du doan nhanh)")
    ap.add_argument("--pad", type=int, default=0, help="chen N nop sau moi lenh (Lab 8: --pad 3)")
    ap.add_argument("--pad-load", type=int, default=0, help="chen N nop sau moi load (Lab 9: 1)")
    ap.add_argument("--pad-ctl", type=int, default=0, help="chen N nop sau moi lenh nhay (Lab 9, 10: 2)")
    ap.add_argument("--gen", help="chi ghi test vector ra file nay (1 chuong trinh)")
    ap.add_argument("--jar", default=os.environ.get("LOGISIM_JAR"))
    ap.add_argument("--java", default="java")
    ap.add_argument("--circ", help="mac dinh: single/riscv_single.circ hoac pipeline/riscv_pipe.circ")
    ap.add_argument("--circuit", default="CPU")
    ap.add_argument("-n", type=int, default=20000, help="so chu ky toi da")
    ap.add_argument("--md", help="ghi bang ket qua (Markdown) cho bao cao")
    ap.add_argument("--label", default="")
    ap.add_argument("--sw", type=lambda v: int(v, 0), help="gia tri cong tac DIP (mac dinh: dong '# SW = ...' trong file .s, hoac 0)")
    ap.add_argument("-v", action="store_true", help="in chi tiet hon cac dong loi")
    a = ap.parse_args()
    circ = a.circ or ("pipeline/riscv_pipe.circ" if a.pipe else "single/riscv_single.circ")
    progs = list(dict.fromkeys(p for pat in a.progs for p in (sorted(glob.glob(pat)) or [pat])))   # bo trung lap

    def build(p):
        words = rvsim.load_words(p, a.pad, a.pad_load, a.pad_ctl)
        sw = a.sw if a.sw is not None else rvsim.parse_sw(p)
        recs, info = trace_pipe(words, a.pipe, a.n, sw) if a.pipe else trace_single(words, a.n, sw)
        if not a.pipe:
            ref, ninstr, halted = rvsim.run_to_halt(words, sw=sw); info["ninstr"] = ninstr if halted else None
        return words, recs, info

    global IO_COLS
    if os.path.isfile(circ):
        cm = re.search(r'<circuit name="%s">.*?</circuit>' % re.escape(a.circuit), open(circ, encoding="utf-8").read(), re.S)
        IO_COLS = bool(cm and 'val="IORData"' in cm.group(0) and 'val="IOWrite"' in cm.group(0))
    if a.gen:
        words, recs, info = build(progs[0])
        open(a.gen, "w", newline="\n").write(gen_vector(recs, os.path.basename(progs[0])))
        hexname = os.path.splitext(a.gen)[0] + ".hex"
        asm.write_hex(words, hexname)
        print(f"Da ghi {a.gen} ({info['cycles']} chu ky) va {hexname}. Nap {hexname} vao ROM truoc khi chay test vector.")
        return
    if not a.jar or not os.path.isfile(a.jar):
        sys.exit("LOI: can --jar <logisim-evolution-4.1.0-all.jar> (hoac bien LOGISIM_JAR), hoac dung --gen")
    if not os.path.isfile(circ):
        sys.exit(f"LOI: khong thay file {circ} (dung --circ de chi dinh)")
    circ_text = open(circ, encoding="utf-8").read()
    ok_all, results = True, []
    for p in progs:
        words, recs, info = build(p)
        name = os.path.basename(p)
        if a.pipe and not info["model_ok"]:
            print(f"{name:20s} CANH BAO: chuong trinh nay KHONG chay dung tren pipeline lab {a.pipe}"
                  f"{' (voi cac nop da chen)' if (a.pad or a.pad_load or a.pad_ctl) else ''} (do hazard). Van so sanh voi mo hinh pipeline.")
        out = run_logisim(a.java, a.jar, a.circuit, circ, circ_text, words, gen_vector(recs, name))
        mm = re.search(r"Passed\s*:\s*(\d+),\s*Failed\s*:\s*(\d+)", out)
        padded = a.pad or a.pad_load or a.pad_ctl
        exps = rvsim.check_expect(p, rvsim.run_to_halt(words, sw=a.sw if a.sw is not None else rvsim.parse_sw(p))[0]) if not padded else []
        if not mm:
            ok_all = False
            print(f"{name:20s} LOI CHAY:\n" + "\n".join("    " + l for l in out.strip().splitlines()[-8:]))
            results.append((p, info, None, None, exps)); continue
        ps, fl = int(mm.group(1)), int(mm.group(2))
        ok_all &= fl == 0
        extra = f", {info['stalls']} stall, {info['flushes']} flush" if a.pipe else ""
        print(f"{name:20s} {'PASS' if fl == 0 else 'FAIL'}  {info['cycles']} chu ky{extra}, passed={ps} failed={fl}")
        results.append((p, info, ps, fl, exps))
        if fl:
            listing = {pc: t for pc, _, t in asm.assemble(p, a.pad, a.pad_load, a.pad_ctl)[1]} if p.endswith(".s") else {}
            report_errors(out, recs, listing, a.v)
    if a.md: write_md(a.md, results, a.label, bool(a.pipe))
    sys.exit(0 if ok_all else 1)

if __name__ == "__main__":
    main()
