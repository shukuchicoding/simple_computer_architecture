# T3: 12 so Fibonacci dau tien, luu mang tai 0x100
        addi s0, x0, 0x100    # con tro mang
        addi s1, x0, 12       # so phan tu
        addi t0, x0, 0        # F(0)
        addi t1, x0, 1        # F(1)
loop:   sw   t0, 0(s0)
        add  t2, t0, t1
        mv   t0, t1
        mv   t1, t2
        addi s0, s0, 4
        addi s1, s1, -1
        bnez s1, loop
        lw   a0, -4(s0)       # phan tu cuoi F(11)
done:   j done
# EXPECT a0 = 89
# EXPECT MEM[0x100] = 0
# EXPECT MEM[0x104] = 1
# EXPECT MEM[0x108] = 1
# EXPECT MEM[0x10C] = 2
# EXPECT MEM[0x110] = 3
# EXPECT MEM[0x114] = 5
# EXPECT MEM[0x118] = 8
# EXPECT MEM[0x11C] = 13
# EXPECT MEM[0x120] = 21
# EXPECT MEM[0x124] = 34
# EXPECT MEM[0x128] = 55
# EXPECT MEM[0x12C] = 89
