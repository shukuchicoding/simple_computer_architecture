# T9: Forwarding - phu thuoc sat nhau, khong load-use, khong nhay (chay dung tu Lab 9, khong can nop)
        addi x1, x0, 5
        add  x2, x1, x1       # A, B lay tu EX/MEM                          -> 10
        add  x3, x2, x1       # A tu EX/MEM (x2), B tu MEM/WB (x1)          -> 15
        add  x4, x1, x3       # A: x1 cach 3 lenh -> bypass WB->ID; B tu EX/MEM -> 20
        sub  x5, x4, x2       # A tu EX/MEM; B: x2 cach 3 lenh -> bypass     -> 10
        addi x6, x0, 1
        addi x6, x0, 2        # ghi x6 hai lan lien tiep
        add  x7, x6, x6       # phai lay ban MOI NHAT (EX/MEM uu tien)      -> 4
        addi x0, x0, 99       # ghi vao x0 ...
        add  x8, x0, x0       # ... khong duoc forward (x0 luon = 0)        -> 0
        sw   x7, 0x40(x0)     # du lieu store: x7 cach 3 lenh -> bypass      MEM[0x40] = 4
        addi x9, x0, 77
        sw   x9, 0x44(x0)     # du lieu store forward tu EX/MEM             MEM[0x44] = 77
        addi x10, x0, 0x48
        sw   x9, 0(x10)       # dia chi tu EX/MEM, du lieu tu MEM/WB        MEM[0x48] = 77
        lui  x11, 0x12345
        addi x11, x11, 0x678  # lui -> addi                                  -> 0x12345678
        sub  x12, x11, x11    # ca hai nguon tu EX/MEM                       -> 0
        or   x13, x12, x9     # A tu EX/MEM, B tu MEM/WB? (x9 cach xa)       -> 77
done:   j done
# EXPECT x2 = 10
# EXPECT x3 = 15
# EXPECT x4 = 20
# EXPECT x5 = 10
# EXPECT x6 = 2
# EXPECT x7 = 4
# EXPECT x8 = 0
# EXPECT x11 = 0x12345678
# EXPECT x12 = 0
# EXPECT x13 = 77
# EXPECT MEM[0x040] = 4
# EXPECT MEM[0x044] = 77
# EXPECT MEM[0x048] = 77
