# T7: Chuoi lenh phu thuoc sat nhau (de kiem tra pipeline o Lab 9-11)
        addi x1, x0, 5
        add  x2, x1, x1       # phu thuoc khoang cach 1          -> 10
        add  x3, x2, x1       # khoang cach 1 va 2                 -> 15
        add  x4, x3, x2       #                                    -> 25
        sub  x5, x4, x1       # x1 cach 4 lenh                     -> 20
        addi x18, x0, 1
        addi x18, x0, 2       # ghi 2 lan lien tiep cung thanh ghi
        add  x19, x18, x18    # phai dung gia tri moi nhat         -> 4
        sw   x4, 0(x0)        # store data vua tinh                MEM[0] = 25
        lw   x6, 0(x0)
        add  x7, x6, x6       # load-use                           -> 50
        lw   x8, 0(x0)
        sw   x8, 4(x0)        # load -> store                      MEM[4] = 25
        addi x20, x0, 0x100
        sw   x20, 8(x0)
        lw   x21, 8(x0)
        sw   x7, 0(x21)       # load -> dung lam dia chi            MEM[0x100] = 50
        lw   x9, 4(x0)
        beq  x9, x6, L1       # load -> branch
        addi x31, x0, 1       # khong duoc chay
L1:     addi x10, x0, 3
L1b:    addi x10, x10, -1
        bne  x10, x0, L1b     # branch phu thuoc lenh ngay truoc
        jal  x11, L2          # x11 = dia chi L2
L2:     addi x12, x11, 0      # dung ket qua jal ngay
        jalr x13, x12, 16     # jalr phu thuoc lenh truoc -> L2 + 16
        addi x31, x0, 2       # khong duoc chay
        addi x31, x0, 3       # khong duoc chay
        addi x14, x13, 1      # dung ket qua jalr (L2 + 8 + 1)
        addi x0, x0, 99       # ghi x0
        add  x17, x0, x0      # khong duoc lay 99 tu x0          -> 0
        lw   x22, 0(x0)
        lw   x23, 0(x0)
        add  x24, x22, x23    # hai load lien tiep roi dung        -> 50
done:   j done
# EXPECT x2 = 10
# EXPECT x3 = 15
# EXPECT x4 = 25
# EXPECT x5 = 20
# EXPECT x19 = 4
# EXPECT x7 = 50
# EXPECT x10 = 0
# EXPECT x11 = 0x60
# EXPECT x12 = 0x60
# EXPECT x13 = 0x68
# EXPECT x14 = 0x69
# EXPECT x17 = 0
# EXPECT x24 = 50
# EXPECT x31 = 0
# EXPECT MEM[0x000] = 25
# EXPECT MEM[0x004] = 25
# EXPECT MEM[0x100] = 50
