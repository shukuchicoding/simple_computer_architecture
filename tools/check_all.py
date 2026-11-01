#!/usr/bin/env python3
"""Chay TOAN BO kiem thu cua du an va ghi bang ket qua vao thu muc report/.

    python tools/check_all.py --jar <logisim-evolution-4.1.0-all.jar>

Gom 4 phan:
  1. Test vector tung module (tools/run_tests.py)
  2. CPU single-cycle, so sanh tung chu ky voi mo hinh tap lenh   -> report/ket_qua_single.md
  3. CPU pipeline 5 tang, so sanh tung chu ky voi mo hinh pipeline -> report/ket_qua_pipeline.md
  4. Bang so sanh hieu nang cac phien ban                         -> report/so_sanh.md
"""
import argparse, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PROGS = ["asm/t*_*.s", "asm/test6*.s"]

def run(title, args):
    print(f"\n========== {title} ==========", flush=True)
    r = subprocess.run([sys.executable, os.path.join(HERE, args[0])] + args[1:])
    return r.returncode == 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jar", default=os.environ.get("LOGISIM_JAR"))
    a = ap.parse_args()
    if not a.jar or not os.path.isfile(a.jar):
        sys.exit("LOI: can --jar <logisim-evolution-4.1.0-all.jar> (hoac bien LOGISIM_JAR)")
    os.makedirs("report", exist_ok=True)
    ok = {}
    ok["module"] = run("1. Test vector tung module", ["run_tests.py", "--jar", a.jar])
    ok["single"] = run("2. CPU single-cycle", ["cpu_test.py", *PROGS, "--jar", a.jar,
                        "--md", "report/ket_qua_single.md", "--label", "single-cycle"])
    ok["pipeline"] = run("3. CPU pipeline 5 tang", ["cpu_test.py", *PROGS, "--pipe", "16", "--jar", a.jar,
                          "--md", "report/ket_qua_pipeline.md", "--label", "pipeline 5 tang"])
    ok["compare"] = run("4. So sanh hieu nang", ["compare.py", "asm/t*_*.s", "--md", "report/so_sanh.md"])
    print("\n========== TONG KET ==========")
    for k, v in ok.items(): print(f"  {k:9s} {'DAT' if v else 'CO LOI'}")
    sys.exit(0 if all(ok.values()) else 1)

if __name__ == "__main__":
    main()
