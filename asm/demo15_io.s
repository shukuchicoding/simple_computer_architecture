# Demo Lab 15 (chay trong Logisim, khong co vong dung): bat cong tac DIP -> LED, HEX dem tang, TTY chao
        li   s0, 0x80000000
        li   t0, 0x6C6C6548       # "Hell"
        sw   t0, 0x200(x0)
        li   t0, 0x6F77206F       # "o wo"
        sw   t0, 0x204(x0)
        li   t0, 0x0A646C72       # "rld\n"
        sw   t0, 0x208(x0)
        sw   x0, 0x20C(x0)
        li   t2, 0x200
print:  lbu  t1, 0(t2)
        beqz t1, loop
        sw   t1, 8(s0)            # UART TX -> TTY
        addi t2, t2, 1
        j    print
loop:   lw   t0, 12(s0)           # doc 8 cong tac
        sw   t0, 0(s0)            # hien len 8 LED
        addi s1, s1, 1
        sw   s1, 4(s0)            # HEX dem tang lien tuc
        j    loop
