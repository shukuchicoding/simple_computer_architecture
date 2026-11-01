# T13: LB LH LBU LHU SB SH - doc/ghi byte va half-word, mo rong dau va khong dau
        addi s0, x0, 0x100
        li   t0, 0x80FF7F01
        sw   t0, 0(s0)        # MEM[0x100] = 0x80FF7F01  (byte 0 = 0x01, 1 = 0x7F, 2 = 0xFF, 3 = 0x80)
        lb   a0, 0(s0)        # 0x01        -> 1
        lb   a1, 1(s0)        # 0x7F        -> 127
        lb   a2, 2(s0)        # 0xFF        -> -1 (mo rong dau)
        lb   a3, 3(s0)        # 0x80        -> -128
        lbu  a4, 2(s0)        # 0xFF        -> 255 (khong dau)
        lbu  a5, 3(s0)        # 0x80        -> 128
        lh   a6, 0(s0)        # 0x7F01      -> 32513
        lh   a7, 2(s0)        # 0x80FF      -> -32513 (mo rong dau)
        lhu  s1, 2(s0)        # 0x80FF      -> 33023
        lw   s2, 0(s0)        # ca word
        sw   x0, 4(s0)        # MEM[0x104] = 0
        li   t1, 0x123456AB
        sb   t1, 4(s0)        # chi byte 0  : MEM[0x104] = 0x000000AB
        sb   t1, 7(s0)        # chi byte 3  : MEM[0x104] = 0xAB0000AB
        sh   t1, 8(s0)        # half thap   : MEM[0x108] = 0x000056AB
        sh   t1, 14(s0)       # half cao    : MEM[0x10C] = 0x56AB0000
        li   t2, -1
        sw   t2, 16(s0)       # MEM[0x110] = 0xFFFFFFFF
        sb   x0, 17(s0)       # xoa byte 1  : MEM[0x110] = 0xFFFF00FF
        sh   x0, 18(s0)       # xoa half cao: MEM[0x110] = 0x000000FF
        lw   s3, 4(s0)
        lw   s4, 16(s0)
        lb   s5, 4(s0)        # 0xAB -> -85 (doc lai byte vua ghi)
        lhu  s6, 14(s0)       # 0x56AB -> 22187
        sb   t1, 20(s0)       # load-use / store-load lien tiep
        lbu  s7, 20(s0)       # -> 0xAB = 171
        add  s8, s7, s7       # dung ngay ket qua lbu -> 342
done:   j done
# EXPECT a0 = 1
# EXPECT a1 = 127
# EXPECT a2 = -1
# EXPECT a3 = -128
# EXPECT a4 = 255
# EXPECT a5 = 128
# EXPECT a6 = 32513
# EXPECT a7 = -32513
# EXPECT s1 = 33023
# EXPECT s2 = 0x80FF7F01
# EXPECT s3 = 0xAB0000AB
# EXPECT s4 = 0x000000FF
# EXPECT s5 = -85
# EXPECT s6 = 22187
# EXPECT s7 = 171
# EXPECT s8 = 342
# EXPECT MEM[0x104] = 0xAB0000AB
# EXPECT MEM[0x108] = 0x000056AB
# EXPECT MEM[0x10C] = 0x56AB0000
# EXPECT MEM[0x110] = 0x000000FF
# EXPECT MEM[0x114] = 0x000000AB
