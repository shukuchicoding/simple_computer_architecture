# Lab 6B: LW / SW
        addi x1, x0, 0x100
        addi x2, x0, 123
        sw   x2, 0(x1)        # MEM[0x100] = 123
        sw   x1, 4(x1)        # MEM[0x104] = 0x100
        lw   x3, 0(x1)        # x3 = 123
        lw   x4, 4(x1)        # x4 = 0x100
        addi x5, x3, 1        # x5 = 124 (dung ngay gia tri vua load)
        sw   x5, -4(x1)       # MEM[0x0FC] = 124 (offset am)
        lw   x6, -4(x1)       # x6 = 124
        li   x7, -1
        sw   x7, 0x7FC(x0)    # MEM[0x7FC] = 0xFFFFFFFF
        lw   x8, 0x7FC(x0)    # x8 = -1
        lw   x0, 0(x1)        # x0 van = 0
        sw   x0, 4(x1)        # MEM[0x104] = 0
        lw   x9, 4(x1)        # x9 = 0
