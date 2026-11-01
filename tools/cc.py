#!/usr/bin/env python3
"""Bien dich chuong trinh C thanh file nap ROM cho CPU RISC-V tren Logisim.

    python tools/cc.py demo/calc.c                       -> rom/calc.hex
    python tools/cc.py demo/calc.c --run --sw 10         -> chay thu bang mo phong Python, in TTY/LED/HEX
    python tools/cc.py demo/calc.c -D ONESHOT -o rom/calc_test.hex

Can: Python 3.8+ va trinh bien dich Zig (chua clang + lld cho RISC-V):  pip install ziglang

Cac buoc:
  1. zig cc bien dich + lien ket (rv32im, khong thu vien chuan) theo c/link.ld
  2. Doc file ELF: .text (ROM, tu 0x0) va .rodata/.data (RAM, tu 0x1000)
  3. CPU la kien truc Harvard: lenh load khong doc duoc ROM, va Ctrl+R xoa RAM. Vi vay cong cu
     SINH THEM mot doan ma o dau ROM, ghi tung word du lieu khac 0 vao RAM (lui/addi/sw),
     roi nhay toi _start. Lien ket lai lan 2 voi .text dat ngay sau doan ma do.
  4. Kiem tra moi lenh deu nam trong tap lenh CPU ho tro (RV32I tru auipc/fence/ecall + M), ghi .hex
"""
import argparse, os, struct, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CDIR = os.path.join(ROOT, "c")
sys.path.insert(0, HERE)
import asm, rvsim

RAM_BASE, RAM_END, ROM_WORDS = 0x1000, 0x2000, 1024

def zig_cc(src, out, defines, text_start, opt):
    import re
    ld = os.path.join(os.path.dirname(out), "link.ld")      # ban sao link.ld voi TEXT_START da thay
    txt = open(os.path.join(CDIR, "link.ld"), encoding="utf-8").read()
    open(ld, "w", encoding="utf-8").write(re.sub(r"TEXT_START = 0x[0-9a-fA-F]+;", f"TEXT_START = 0x{text_start:x};", txt))
    cmd = [sys.executable, "-m", "ziglang", "cc", "-target", "riscv32-freestanding-none",
           "-mcpu=generic_rv32+m+relax",           # RV32I + M; +relax: loi goi ham thanh 'jal' (khong dung auipc)
           opt, "-ffreestanding", "-nostdlib", "-fno-pic", "-mcmodel=medlow",
           "-fno-asynchronous-unwind-tables", "-fomit-frame-pointer", "-fno-jump-tables",
           "-I", CDIR, "-T", ld,
           os.path.join(CDIR, "start.S"), os.path.join(CDIR, "rt.c"), *src, "-o", out]
    cmd += [f"-D{d}" for d in defines]
    r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    if r.returncode:
        print(r.stdout)
        if "No module named ziglang" in r.stdout:
            print("=> Cai trinh bien dich:  pip install ziglang")
        sys.exit("LOI: bien dich that bai")

def read_elf(path):
    """Tra ve danh sach (ten, dia chi, bytes) cua cac section PROGBITS co SHF_ALLOC."""
    b = open(path, "rb").read()
    assert b[:4] == b"\x7fELF" and b[4] == 1, "khong phai ELF 32 bit"
    shoff, = struct.unpack_from("<I", b, 0x20)
    shentsize, shnum, shstrndx = struct.unpack_from("<HHH", b, 0x2E)
    sh = [struct.unpack_from("<IIIIIIIIII", b, shoff + i * shentsize) for i in range(shnum)]
    stroff = sh[shstrndx][4]
    name = lambda o: b[stroff + o: b.index(b"\0", stroff + o)].decode()
    out = []
    for nm, typ, flags, addr, off, size, *_ in sh:
        if typ == 1 and flags & 2 and size:                 # SHT_PROGBITS, SHF_ALLOC
            out.append((name(nm), addr, b[off:off + size]))
    return out

def words_of(data):
    data = data + b"\0" * (-len(data) % 4)
    return list(struct.unpack(f"<{len(data) // 4}I", data))

def init_stub(ram_words, entry):
    """Doan ma ghi cac word du lieu (khac 0) vao RAM roi nhay toi entry."""
    lines, cur_hi = [], None
    for addr, v in sorted(ram_words.items()):
        if v == 0: continue
        lo = addr & 0xFFF; lo = lo - 0x1000 if lo >= 0x800 else lo
        hi = ((addr - lo) >> 12) & 0xFFFFF
        if hi != cur_hi: lines.append(f"lui t1, {hi}"); cur_hi = hi
        lines.append(f"li t0, {v if v < 0x80000000 else v - (1 << 32)}")
        lines.append(f"sw t0, {lo}(t1)")
    lines.append("nop")                     # cho trong, duoc thay bang jal ben duoi
    tmp = tempfile.NamedTemporaryFile("w", suffix=".s", delete=False)
    tmp.write("\n".join(lines) + "\n"); tmp.close()
    try:
        w, _ = asm.assemble(tmp.name)
    finally:
        os.remove(tmp.name)
    pc = 4 * (len(w) - 1)
    w[-1] = asm.encode("jal", ["x0", str(entry - pc)], pc, {})   # nhay tuong doi toi entry
    return w

def check_isa(words):
    bad = []
    for i, w in enumerate(words):
        op, f3, f7 = w & 0x7F, (w >> 12) & 7, w >> 25
        ok = (op in (0x37, 0x6F, 0x13) or
              (op == 0x67 and f3 == 0) or
              (op == 0x33 and f7 in (0, 1, 0x20) and (f7 != 0x20 or f3 in (0, 5))) or
              (op == 0x03 and f3 in (0, 1, 2, 4, 5)) or
              (op == 0x23 and f3 in (0, 1, 2)) or
              (op == 0x63 and f3 in (0, 1, 4, 5, 6, 7)))
        if not ok: bad.append((4 * i, w))
    return bad

def build(src, defines, opt="-O2"):
    with tempfile.TemporaryDirectory() as td:
        elf = os.path.join(td, "a.elf")
        text_start = 0
        for _ in range(4):                       # lap: do dai doan khoi tao phu thuoc noi dung RAM
            zig_cc(src, elf, defines, text_start, opt)
            rom, ram = {}, {}
            for nm, addr, data in read_elf(elf):
                tgt = ram if addr >= RAM_BASE else rom
                for k, v in enumerate(words_of(data)): tgt[addr + 4 * k] = v
            need = (4 * len(init_stub(ram, text_start)) + 15) & ~15
            if text_start >= need and text_start > 0: break
            text_start = need + 16               # du phong de lan sau chac chan vua
        else:
            sys.exit("LOI: khong dat duoc doan khoi tao RAM")
    stub = init_stub(ram, text_start)
    size = max(rom) + 4 if rom else text_start
    words = [0x00000013] * (size // 4)             # o trong = nop
    for i, w in enumerate(stub): words[i] = w
    for a, v in rom.items(): words[a // 4] = v
    data_end = max(ram) + 4 if ram else RAM_BASE
    return words, dict(stub=len(stub), text_start=text_start, text_words=len(rom),
                       data_bytes=data_end - RAM_BASE, data_nonzero=sum(1 for v in ram.values() if v))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", nargs="+", help="file .c")
    ap.add_argument("-o", help="file .hex ra (mac dinh rom/<ten>.hex)")
    ap.add_argument("-D", action="append", default=[], help="dinh nghia macro, vi du -D ONESHOT")
    ap.add_argument("-O", default="2", help="muc toi uu (0, 1, 2, s)")
    ap.add_argument("--run", action="store_true", help="chay thu bang mo phong tap lenh (rvsim)")
    ap.add_argument("--sw", type=lambda s: int(s, 0), default=0, help="gia tri 8 cong tac khi --run")
    ap.add_argument("-n", type=int, default=2_000_000, help="so lenh toi da khi --run")
    a = ap.parse_args()
    out = a.o or os.path.join(ROOT, "rom", os.path.splitext(os.path.basename(a.src[0]))[0] + ".hex")
    words, info = build(a.src, a.D, "-O" + a.O)
    bad = check_isa(words)
    if bad:
        for addr, w in bad[:10]: print(f"  0x{addr:04X}: {w:08x}  <- lenh CPU khong ho tro")
        sys.exit("LOI: chuong trinh dung lenh ngoai tap lenh cua CPU")
    if len(words) > ROM_WORDS: sys.exit(f"LOI: chuong trinh {len(words)} word > ROM {ROM_WORDS} word")
    if RAM_BASE + info["data_bytes"] > RAM_END - 512: print("CANH BAO: du lieu lon, ngan xep con < 512 byte")
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    asm.write_hex(words, out)
    print(f"Da ghi {out}: {len(words)} word ROM ({4 * len(words)} byte)")
    print(f"  doan khoi tao RAM: {info['stub']} lenh (ghi {info['data_nonzero']} word du lieu), main bat dau tai 0x{info['text_start']:X}")
    print(f"  du lieu trong RAM: {info['data_bytes']} byte tu 0x{RAM_BASE:X}; ngan xep tu 0x{RAM_END:X} di xuong")
    if a.run:
        rv = rvsim.RV(words, a.sw)
        last = len(rv.io.tty)
        for n in range(1, a.n + 1):
            pc = rv.pc; rv.step()
            if rv.pc == pc: break
        print(f"\n--- Chay thu (rvsim), SW = 0x{a.sw:02X}: {n} lenh{' (dung tai vong lap)' if rv.pc == pc else ' (het gioi han -n)'} ---")
        print("TTY:"); print(rv.io.text(), end="" if rv.io.text().endswith("\n") else "\n")
        print(f"LED = {rv.io.led & 0xFF:08b}   HEX = {rv.io.hex:08X}")

if __name__ == "__main__":
    main()
