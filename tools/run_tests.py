#!/usr/bin/env python3
"""Chay toan bo test vector bang Logisim-evolution (che do dong lenh).

Dung (chay tu thu muc riscv32):
    python tools/run_tests.py --jar C:\\duong\\dan\\logisim-evolution-4.1.0-all.jar
    python tools/run_tests.py --jar ... ALU DMEM        # chi chay mot so module
Co the dat bien moi truong LOGISIM_JAR thay cho --jar.
"""
import argparse, os, re, subprocess, sys

# (circuit, file test, file .circ)
TESTS = [
    ("ALU",       "tests/alu.txt",       "modules/riscv_modules.circ"),
    ("RegFile",   "tests/regfile.txt",   "modules/riscv_modules.circ"),
    ("ImmGen",    "tests/immgen.txt",    "modules/riscv_modules.circ"),
    ("BranchCmp", "tests/branchcmp.txt", "modules/riscv_modules.circ"),
    ("PCUnit",    "tests/pcunit.txt",    "modules/riscv_modules.circ"),
    ("Control",   "tests/control.txt",   "modules/riscv_modules.circ"),
    ("IF_ID",     "tests/if_id.txt",     "modules/riscv_modules.circ"),   # Lab 8
    ("ID_EX",     "tests/id_ex.txt",     "modules/riscv_modules.circ"),
    ("EX_MEM",    "tests/ex_mem.txt",    "modules/riscv_modules.circ"),
    ("MEM_WB",    "tests/mem_wb.txt",    "modules/riscv_modules.circ"),
    ("ForwardUnit", "tests/forwardunit.txt", "modules/riscv_modules.circ"),   # Lab 9
    ("WBBypass",  "tests/wbbypass.txt",  "modules/riscv_modules.circ"),
    ("HazardUnit", "tests/hazardunit.txt", "modules/riscv_modules.circ"),   # Lab 10
    ("LoadExt",   "tests/loadext.txt",   "modules/riscv_modules.circ"),   # Lab 13
    ("StoreMerge", "tests/storemerge.txt", "modules/riscv_modules.circ"),
    ("MulDiv",    "tests/muldiv.txt",    "modules/riscv_modules.circ"),   # Lab 14
    ("IsMul",     "tests/ismul.txt",     "modules/riscv_modules.circ"),
    ("MemMap",    "tests/memmap.txt",    "modules/riscv_modules.circ"),   # Lab 15
    ("BTB",       "tests/btb.txt",       "modules/riscv_modules.circ"),   # Lab 16
    ("PredRegs",  "tests/predregs.txt",  "modules/riscv_modules.circ"),
    ("IMEM",      "tests/imem_lab0.txt", "single/riscv_single.circ"),   # tu nap rom/lab0_check.hex vao ban sao
    ("DMEM",      "tests/dmem.txt",      "single/riscv_single.circ"),     # Lab 13: dmem.txt co cot funct3
    ("DMEM",      "tests/dmem.txt",      "pipeline/riscv_pipe.circ"),
    ("IO",        "tests/io.txt",        "single/riscv_single.circ"),     # Lab 15
    ("IO",        "tests/io.txt",        "pipeline/riscv_pipe.circ"),
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jar", default=os.environ.get("LOGISIM_JAR"))
    ap.add_argument("--java", default="java")
    ap.add_argument("--verbose", "-v", action="store_true", help="in chi tiet dong loi")
    ap.add_argument("only", nargs="*", help="ten circuit can chay (mac dinh: tat ca)")
    a = ap.parse_args()
    if not a.jar or not os.path.isfile(a.jar):
        sys.exit("LOI: can --jar <logisim-evolution-4.1.0-all.jar> (hoac bien LOGISIM_JAR)")
    ok_all = True
    for circ, vec, proj in TESTS:
        if a.only and circ not in a.only: continue
        if not (os.path.isfile(vec) and os.path.isfile(proj)) or ("<circuit name=\"%s\">" % circ) not in open(proj, encoding="utf-8").read():
            print(f"{circ:10s} BO QUA (chua co circuit hoac file test)"); continue
        run_proj = proj
        if circ == "IMEM":      # tu nap rom/lab0_check.hex vao ban sao (khong phu thuoc ROM dang nap gi)
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            import cpu_test, rvsim
            run_proj = os.path.join(os.path.dirname(os.path.abspath(proj)), "_imem_test_tmp.circ")
            open(run_proj, "w", encoding="utf-8").write(
                cpu_test.patch_rom(open(proj, encoding="utf-8").read(), rvsim.load_words("rom/lab0_check.hex")))
        try:
            r = subprocess.run([a.java, "-jar", a.jar, "--test-vector", circ, vec, run_proj],
                               stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
        finally:
            if run_proj != proj and os.path.exists(run_proj): os.remove(run_proj)
        out = r.stdout
        m = re.search(r"Passed\s*:\s*(\d+),\s*Failed\s*:\s*(\d+)", out)
        if m:
            p, f = int(m.group(1)), int(m.group(2))
            print(f"{circ:10s} {'PASS' if f == 0 else 'FAIL'}  passed={p} failed={f}")
            ok_all &= (f == 0)
            if f and a.verbose:
                for line in out.splitlines():
                    if line.startswith("Error") or "expected" in line: print("    " + line.strip())
        else:
            ok_all = False
            print(f"{circ:10s} LOI CHAY:\n" + "\n".join("    " + l for l in out.strip().splitlines()[-8:]))
    print("==> TAT CA DAT" if ok_all else "==> CO LOI")
    sys.exit(0 if ok_all else 1)

if __name__ == "__main__":
    main()
