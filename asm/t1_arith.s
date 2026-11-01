# T1: So hoc / logic va cac ca bien (tran so, dich 0/31, so am, x0)
        li   x1, 0x7FFFFFFF
        addi x2, x1, 1        # tran so: 0x80000000
        sub  x3, x0, x1       # 0 - 0x7FFFFFFF = 0x80000001
        addi x4, x0, -1
        sub  x5, x0, x4       # 0 - (-1) = 1
        add  x6, x4, x4       # -2
        slt  x7, x2, x1       # 0x80000000 (am) < 0x7FFFFFFF -> 1
        sltu x8, x2, x1       # khong dau: 0x80000000 > 0x7FFFFFFF -> 0
        slt  x9, x1, x1       # bang nhau -> 0
        sltiu x10, x0, 1      # (seqz) 0 < 1 -> 1
        sltiu x11, x4, 1      # 0xFFFFFFFF < 1 -> 0
        slti x12, x4, -2048   # -1 < -2048 -> 0
        xori x13, x1, -1      # NOT 0x7FFFFFFF = 0x80000000
        andi x14, x4, -256    # 0xFFFFFF00 (imm am duoc mo rong dau)
        ori  x15, x0, 0x7FF   # 2047
        addi x16, x0, -2048   # -2048
        addi x17, x0, 33
        sll  x18, x4, x17     # dich 33 -> chi lay 5 bit thap = 1 -> 0xFFFFFFFE
        srl  x19, x4, x0      # dich 0 -> giu nguyen 0xFFFFFFFF
        sra  x20, x2, x15     # 2047 & 31 = 31 -> 0xFFFFFFFF
        srai x21, x1, 31      # so duong >> 31 -> 0
        srli x22, x2, 31      # 1
        slli x23, x4, 31      # 0x80000000
        lui  x24, 0xFFFFF     # 0xFFFFF000
        addi x24, x24, 0x7FF  # 0xFFFFF7FF
        and  x25, x24, x13    # 0x80000000
        or   x26, x15, x16    # 0x7FF | 0xFFFFF800 = 0xFFFFFFFF
        xor  x27, x26, x24    # 0x00000800
        addi x0, x0, 123      # ghi x0 phai bi bo qua
        add  x28, x0, x0      # 0
done:   j done
# EXPECT x2 = 0x80000000
# EXPECT x3 = 0x80000001
# EXPECT x5 = 1
# EXPECT x6 = -2
# EXPECT x7 = 1
# EXPECT x8 = 0
# EXPECT x9 = 0
# EXPECT x10 = 1
# EXPECT x11 = 0
# EXPECT x12 = 0
# EXPECT x13 = 0x80000000
# EXPECT x14 = 0xFFFFFF00
# EXPECT x15 = 2047
# EXPECT x16 = -2048
# EXPECT x18 = 0xFFFFFFFE
# EXPECT x19 = 0xFFFFFFFF
# EXPECT x20 = 0xFFFFFFFF
# EXPECT x21 = 0
# EXPECT x22 = 1
# EXPECT x23 = 0x80000000
# EXPECT x24 = 0xFFFFF7FF
# EXPECT x25 = 0x80000000
# EXPECT x26 = 0xFFFFFFFF
# EXPECT x27 = 0x00000800
# EXPECT x0 = 0
# EXPECT x28 = 0
