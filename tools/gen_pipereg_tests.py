#!/usr/bin/env python3
"""Sinh tests/if_id.txt, id_ex.txt, ex_mem.txt, mem_wb.txt (test vector tuan tu cho 4 thanh ghi pipeline)."""
import os, random, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pipe_spec import PIPE_REGS

def fmt(v, w):
    return f"0x{v:08X}" if w == 32 else f"{v:0{w}b}"

def gen(name, fields, seed):
    rnd = random.Random(seed)
    hdr = ["<set>", "<seq>"] + [f"{f}_in" + (f"[{w}]" if w > 1 else "") for f, w, _ in fields] + ["EN", "Flush", "clk", "Reset"] \
          + [f"{f}_out" + (f"[{w}]" if w > 1 else "") for f, w, _ in fields]
    rows, state, prev_clk = [], {f: 0 for f, _, _ in fields}, 0
    seq = 0
    def emit(ins, en, fl, clk, rst):
        nonlocal prev_clk, seq
        if rst:
            for f in state: state[f] = 0
        elif prev_clk == 0 and clk == 1 and (en or fl):
            for f, w, clr in fields: state[f] = 0 if (fl and clr) else ins[f]
        prev_clk = clk; seq += 1
        rows.append(["1", str(seq)] + [fmt(ins[f], w) for f, w, _ in fields] + [str(en), str(fl), str(clk), str(rst)]
                    + [fmt(state[f], w) for f, w, _ in fields])
    def rand_in():
        return {f: rnd.getrandbits(w) for f, w, _ in fields}
    # 1) nap binh thuong, 2) EN=0 giu, 3) Flush (ca khi EN=0), 4) Reset, 5) ngau nhien
    script = [(1, 0)] * 4 + [(0, 0)] * 3 + [(1, 1), (0, 1), (1, 0)] + ["R"] + [(1, 0)] * 2
    script += [(int(rnd.random() < 0.75), int(rnd.random() < 0.2)) for _ in range(60)]
    for step in script:
        if step == "R":
            ins = rand_in(); emit(ins, 0, 0, 0, 1); emit(ins, 0, 0, 0, 0); continue
        en, fl = step
        ins = rand_in()
        emit(ins, en, fl, 0, 0)
        emit(ins, en, fl, 1, 0)
    with open(f"tests/{name.lower()}.txt", "w", newline="\n") as f:
        f.write(f"# Test vector {name} (tuan tu). Sinh boi tools/gen_pipereg_tests.py\n")
        f.write(" ".join(hdr) + "\n")
        for r in rows: f.write(" ".join(r) + "\n")
    return len(rows)

for i, (name, fields) in enumerate(PIPE_REGS.items()):
    print(name, gen(name, fields, 100 + i), "dong")
