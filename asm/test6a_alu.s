# Lab 6A: lenh ALU R-type, I-type, LUI (chua co nhay, chua co bo nho)
        addi x1, x0, 5
        addi x2, x0, -3
        add  x3, x1, x2       # x3  = 2
        sub  x4, x1, x2       # x4  = 8
        and  x5, x1, x2       # x5  = 5
        or   x6, x1, x2       # x6  = -3  (0xFFFFFFFD)
        xor  x7, x1, x2       # x7  = -8  (0xFFFFFFF8)
        slt  x8, x2, x1       # x8  = 1   (-3 < 5)
        sltu x9, x2, x1       # x9  = 0   (0xFFFFFFFD > 5)
        sll  x10, x1, x1      # x10 = 160 (5 << 5)
        srl  x11, x2, x1      # x11 = 0x07FFFFFF
        sra  x12, x2, x1      # x12 = -1
        andi x13, x2, 0xFF    # x13 = 0xFD
        ori  x14, x1, -16     # x14 = 0xFFFFFFF5
        xori x15, x2, -1      # x15 = 2
        slti x16, x2, 0       # x16 = 1
        sltiu x17, x1, -1     # x17 = 1   (5 < 0xFFFFFFFF)
        slli x18, x1, 31      # x18 = 0x80000000
        srli x19, x18, 31     # x19 = 1
        srai x20, x18, 31     # x20 = -1
        lui  x21, 0x12345     # x21 = 0x12345000
        addi x21, x21, 0x678  # x21 = 0x12345678
        addi x22, x0, -1024   # x22 = -1024 (bit 30 = 1, khong duoc thanh SUB)
        addi x0, x0, 7        # x0 van = 0
        add  x23, x0, x0      # x23 = 0
        li   x24, 0xDEADBEEF  # lui + addi
