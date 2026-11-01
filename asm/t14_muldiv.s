# T14: M-extension - MUL MULH MULHSU MULHU DIV DIVU REM REMU, ca bien va phu thuoc lien tiep
        li   s0, 123
        li   s1, 456
        li   s2, -7
        li   s3, 9
        li   s4, 0x80000000       # -2^31
        li   s5, -1
        li   s6, 0x12345678
        li   s7, 0x9ABCDEF0
        mul  a0, s0, s1           # 56088
        mul  a1, s2, s3           # -63
        mul  a2, s6, s7           # 32 bit thap
        mulh a3, s6, s7           # 32 bit cao, co dau x co dau
        mulhsu a4, s7, s6         # co dau (s7 < 0) x khong dau
        mulhu a5, s6, s7          # khong dau x khong dau
        mulh a6, s2, s3           # -63 -> phan cao = -1
        mulhu a7, s5, s5          # 0xFFFFFFFF^2 -> phan cao 0xFFFFFFFE
        div  tp, s2, s3           # -7 / 9 = 0 (lam tron ve 0)
        li   t6, -100
        li   t5, 7
        div  t1, t6, t5           # -14
        rem  t2, t6, t5           # -2 (dau theo so bi chia)
        divu t3, t6, t5           # 0xFFFFFF9C / 7
        remu t4, t6, t5
        sw   t1, 0x100(x0)
        sw   t2, 0x104(x0)
        sw   t3, 0x108(x0)
        sw   t4, 0x10C(x0)
        div  t1, s4, s5           # tran: -2^31 / -1 = -2^31
        rem  t2, s4, s5           # 0
        div  t3, s0, x0           # chia cho 0 -> -1
        divu t4, s0, x0           # -> 0xFFFFFFFF
        rem  t5, s2, x0           # -> so bi chia (-7)
        remu t6, s1, x0           # -> 456
        sw   t1, 0x110(x0)
        sw   t2, 0x114(x0)
        sw   t3, 0x118(x0)
        sw   t4, 0x11C(x0)
        sw   t5, 0x120(x0)
        sw   t6, 0x124(x0)
        # chuoi phu thuoc sat nhau (forwarding vao/ra khoi MulDiv): 10! = 3628800
        li   s8, 1
        li   s9, 1
        li   s10, 11
fact:   mul  s8, s8, s9
        addi s9, s9, 1
        bne  s9, s10, fact
        lw   s11, 0x100(x0)       # load-use vao MulDiv
        mul  s11, s11, s11        # (-14)^2 = 196
        # UCLN(1071, 462) = 21 bang REM
        li   t0, 1071
        li   t1, 462
gcd:    beqz t1, gdone
        rem  t2, t0, t1
        mv   t0, t1
        mv   t1, t2
        j    gcd
gdone:  mv   s3, t0
done:   j done
# EXPECT a0 = 56088
# EXPECT a1 = -63
# EXPECT a2 = 0x242D2080
# EXPECT a3 = 0xF8CC93D6
# EXPECT a4 = 0xF8CC93D6
# EXPECT a5 = 0x0B00EA4E
# EXPECT a6 = -1
# EXPECT a7 = 0xFFFFFFFE
# EXPECT tp = 0
# EXPECT MEM[0x100] = -14
# EXPECT MEM[0x104] = -2
# EXPECT MEM[0x108] = 0x24924916
# EXPECT MEM[0x10C] = 2
# EXPECT MEM[0x110] = 0x80000000
# EXPECT MEM[0x114] = 0
# EXPECT MEM[0x118] = -1
# EXPECT MEM[0x11C] = 0xFFFFFFFF
# EXPECT MEM[0x120] = -7
# EXPECT MEM[0x124] = 456
# EXPECT s8 = 3628800
# EXPECT s11 = 196
# EXPECT s3 = 21
