# T14b: cung bai toan nhu t6_mul.s nhung dung lenh MUL phan cung (de so sanh so chu ky)
        li   a0, 123
        li   a1, 456
        mul  s0, a0, a1           # 56088
        li   a0, -7
        li   a1, 9
        mul  s1, a0, a1           # -63
        li   a0, 9
        li   a1, -7
        mul  s2, a0, a1           # -63
        li   a0, 0x10000
        li   a1, 0x10000
        mul  s3, a0, a1           # 2^32 tran -> 0
        sw   s0, 0x40(x0)
        sw   s1, 0x44(x0)
done:   j done
# EXPECT s0 = 56088
# EXPECT s1 = -63
# EXPECT s2 = -63
# EXPECT s3 = 0
# EXPECT MEM[0x040] = 56088
# EXPECT MEM[0x044] = -63
