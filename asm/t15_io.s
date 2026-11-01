# T15: I/O anh xa bo nho - LED, HEX (7 doan), UART TX (TTY), cong tac SW
# SW = 0x5A
        li   s0, 0x80000000       # dia chi co so vung I/O
        li   t0, 0x1111
        sw   t0, 0(x0)            # RAM[0] = 0x1111 (de kiem: ghi I/O khong duoc ghi de RAM)
        li   t0, 0xA5
        sw   t0, 0(s0)            # LED = 0xA5
        li   t0, 0x12345678
        sw   t0, 4(s0)            # HEX = 12345678
        lw   a0, 0(s0)            # doc lai LED
        lw   a1, 4(s0)            # doc lai HEX
        lw   a2, 12(s0)           # doc cong tac SW
        add  a3, a2, a2           # dung ngay ket qua doc I/O (load-use)
        lw   a4, 0(x0)            # RAM[0] van la 0x1111
        # dat chuoi "Hi RISC-V!\n" vao RAM tai 0x200 (little-endian, 4 ky tu / word)
        li   t0, 0x52206948       # "Hi R"
        sw   t0, 0x200(x0)
        li   t0, 0x2D435349       # "ISC-"
        sw   t0, 0x204(x0)
        li   t0, 0x000A2156       # "V!\n\0"
        sw   t0, 0x208(x0)
        # in chuoi ra TTY qua UART TX: doc trang thai (1 = san sang) roi ghi ky tu
        li   t2, 0x200
print:  lbu  t1, 0(t2)
        beqz t1, pdone
wait:   lw   t3, 8(s0)
        beqz t3, wait
        sw   t1, 8(s0)
        addi t2, t2, 1
        j    print
pdone:  sw   a2, 0(s0)            # LED = SW
        li   t4, 0                # dem 0..5 tren HEX
        li   t5, 5
count:  addi t4, t4, 1
        sw   t4, 4(s0)
        bne  t4, t5, count
        lw   a5, 4(s0)
done:   j    done
# EXPECT a0 = 0xA5
# EXPECT a1 = 0x12345678
# EXPECT a2 = 0x5A
# EXPECT a3 = 0xB4
# EXPECT a4 = 0x1111
# EXPECT a5 = 5
# EXPECT MEM[0x000] = 0x1111
# EXPECT LED = 0x5A
# EXPECT HEX = 5
# EXPECT TTY = "Hi RISC-V!\n"
