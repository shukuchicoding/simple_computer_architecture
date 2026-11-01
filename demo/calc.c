/* Demo toan trinh: "May tinh so hoc" chay tren CPU RISC-V tu thiet ke (Logisim).
 *   Dau vao : 8 cong tac DIP  -> so n (0..255)
 *   Dau ra  : TTY  - in bang ket qua n, n!, fib(n), tong 1..n, n co phai so nguyen to
 *             HEX  - fib(n) dang thap phan (doi sang BCD), hoac EEEEEEEE neu qua 8 chu so
 *             LED  - n o dang nhi phan
 * Moi khi gat cong tac, chuong trinh tinh lai va in dong moi.
 * Bien dich voi -D ONESHOT: chi tinh 1 lan roi dung (de kiem thu tu dong). */
#include "riscv_io.h"

static unsigned fact(unsigned n) {               /* MUL; tra ve 0 neu tran 32 bit (n > 12) */
    unsigned r = 1;
    for (unsigned i = 2; i <= n; i++) {
        if (r > 0xFFFFFFFFu / i) return 0;       /* DIVU de kiem tra tran */
        r *= i;
    }
    return r;
}

static unsigned fib(unsigned n) {                /* vong lap: nhanh du doan tot */
    unsigned a = 0, b = 1;
    while (n--) { unsigned t = a + b; a = b; b = t; }
    return a;
}

static int is_prime(unsigned n) {                /* REMU */
    if (n < 2) return 0;
    for (unsigned d = 2; d * d <= n; d++)
        if (n % d == 0) return 0;
    return 1;
}

static void report(unsigned n) {
    unsigned f = fib(n), fa = fact(n);
    IO_LED = n;
    IO_HEX = (f <= 99999999u && n <= 47) ? to_bcd(f) : 0xEEEEEEEEu;
    puts_("n="); putu(n);
    puts_("  n!="); if (fa) putu(fa); else puts_("tran");
    puts_("  fib="); if (n <= 47) putu(f); else puts_("tran");
    puts_("  tong="); putu(n * (n + 1) / 2);
    puts_(is_prime(n) ? "  nguyen to\n" : "\n");
}

int main(void) {
    puts_("RISC-V Logisim - gat cong tac DIP\n");
#ifdef ONESHOT
    report(IO_SW & 0xFF);
    return 0;
#else
    unsigned last = 0x100;                        /* gia tri khong the co -> in ngay lan dau */
    for (;;) {
        unsigned n = IO_SW & 0xFF;
        if (n != last) { report(n); last = n; }
    }
#endif
}
