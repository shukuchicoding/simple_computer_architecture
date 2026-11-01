# T6: Nhan bang phan mem (dich va cong), goi ham nhieu lan
        li   a0, 123
        li   a1, 456
        jal  ra, mul
        mv   s0, a0           # 56088
        li   a0, -7
        li   a1, 9
        jal  ra, mul
        mv   s1, a0           # -63
        li   a0, 9
        li   a1, -7
        jal  ra, mul          # so nhan am: lap 32 lan
        mv   s2, a0           # -63
        li   a0, 0x10000
        li   a1, 0x10000
        jal  ra, mul
        mv   s3, a0           # 2^32 tran -> 0
        sw   s0, 0x40(x0)
        sw   s1, 0x44(x0)
done:   j done

mul:    addi t0, x0, 0        # a0 * a1 -> a0 (32 bit thap)
mloop:  beqz a1, mdone
        andi t1, a1, 1
        beqz t1, mskip
        add  t0, t0, a0
mskip:  slli a0, a0, 1
        srli a1, a1, 1
        j    mloop
mdone:  mv   a0, t0
        ret
# EXPECT s0 = 56088
# EXPECT s1 = -63
# EXPECT s2 = -63
# EXPECT s3 = 0
# EXPECT MEM[0x040] = 56088
# EXPECT MEM[0x044] = -63
