# T10: Load-use - lw roi dung ngay ket qua (chay dung tu Lab 10, khong can nop; khong co lenh nhay)
        addi x1, x0, 0x100
        addi x2, x0, 11
        sw   x2, 0(x1)        # MEM[0x100] = 11
        addi x3, x0, 0x104
        sw   x3, 4(x1)        # MEM[0x104] = 0x104 (mot con tro)
        lw   x4, 0(x1)
        add  x5, x4, x4       # load-use o rs1 va rs2: STALL 1 chu ky      -> 22
        lw   x6, 0(x1)
        sub  x7, x0, x6       # load-use chi o rs2: STALL                    -> -11
        lw   x8, 4(x1)
        lw   x9, 0(x8)        # dung ket qua load lam DIA CHI: STALL         -> MEM[0x104] = 0x104
        lw   x10, 0(x1)
        sw   x10, 8(x1)       # load -> du lieu store: STALL                 MEM[0x108] = 11
        lw   x11, 0(x1)
        addi x12, x0, 7       # lenh doc lap: KHONG stall
        add  x13, x11, x12    # cach 2 lenh: forward tu WB, KHONG stall     -> 18
        lw   x0, 0(x1)        # load vao x0 ...
        add  x14, x0, x0      # ... KHONG duoc stall, x14 = 0
        lw   x15, 8(x1)
        lw   x16, 0(x1)       # hai load lien tiep
        add  x17, x15, x16    # x16 vua load: STALL; x15 tu WB              -> 22
done:   j done
# EXPECT x5 = 22
# EXPECT x7 = -11
# EXPECT x9 = 0x104
# EXPECT x13 = 18
# EXPECT x14 = 0
# EXPECT x17 = 22
# EXPECT MEM[0x108] = 11
