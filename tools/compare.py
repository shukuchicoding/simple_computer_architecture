#!/usr/bin/env python3
"""Bang so sanh hieu nang cac phien ban CPU (tu mo hinh da kiem chung khop phan cung tung chu ky).
    python tools/compare.py "asm/t[1-6]_*.s" --md report/so_sanh.md
Cot: so lenh that (khong tinh nop) / so chu ky cua tung phien ban (chuong trinh chay DUNG o phien ban do)."""
import argparse, glob, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import rvsim, pipesim

CONFIGS = [  # (ten, lab, pad, pad_load, pad_ctl)
    ("Lab 8 (+3 nop/lenh)", 8, 3, 0, 0),
    ("Lab 9 forwarding (+nop sau lw, nhay)", 9, 0, 1, 2),
    ("Lab 10 +stall (+nop sau nhay)", 10, 0, 0, 2),
    ("Lab 11 day du (khong nop)", 11, 0, 0, 0),
    ("Lab 16 du doan nhanh", 16, 0, 0, 0),
]
def cycles(path, lab, pad, pl, pc):
    w = rvsim.load_words(path, pad, pl, pc); sw = rvsim.parse_sw(path)
    ref, n, halted = rvsim.run_to_halt(w, sw=sw)
    if not halted: return None, False
    p, recs = pipesim.run(w, lab, 20 * n + 200, ref.pc, sw=sw)
    return len(recs), (p.x == ref.x and p.mem == ref.mem)

ap = argparse.ArgumentParser(); ap.add_argument("progs", nargs="+"); ap.add_argument("--md")
a = ap.parse_args()
progs = list(dict.fromkeys(p for pat in a.progs for p in (sorted(glob.glob(pat)) or [pat])))
head = ["Chuong trinh", "So lenh", "Single-cycle (chu ky)"] + [c[0] for c in CONFIGS] + ["CPI Lab 16"]
rows = []
for p in progs:
    ref, n, halted = rvsim.run_to_halt(rvsim.load_words(p), sw=rvsim.parse_sw(p))
    if not halted: continue
    cells = [os.path.basename(p), str(n), str(n)]
    last = None
    for name, lab, pad, pl, pc in CONFIGS:
        c, ok = cycles(p, lab, pad, pl, pc)
        cells.append(f"{c}" if ok else "sai")
        last = c if ok else None
    cells.append(f"{last / n:.2f}" if last else "-")
    rows.append(cells)
out = ["| " + " | ".join(head) + " |", "|" + "---|" * len(head)] + ["| " + " | ".join(r) + " |" for r in rows]
note = ("\n\nGhi chu: CPU single-cycle co 1 chu ky/lenh nhung chu ky rat dai (bang tong tre ca 5 tang); "
        "pipeline co chu ky ngan hon ~5 lan (bang tre tang cham nhat). CPI Lab 16 gom ca vai chu ky nap/xa pipeline ban dau.\n")
print("\n".join(out))
if a.md:
    if os.path.dirname(a.md): os.makedirs(os.path.dirname(a.md), exist_ok=True)
    open(a.md, "w", encoding="utf-8", newline="\n").write("## So sanh hieu nang\n\n" + "\n".join(out) + note)
    print("Da ghi", a.md)
