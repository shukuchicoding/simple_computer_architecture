# T5: Sap xep noi bot (bubble sort) 8 so co dau tai 0x200
        addi s0, x0, 0x200
        li t0, 5
        sw t0, 0(s0)
        li t0, -3
        sw t0, 4(s0)
        li t0, 12
        sw t0, 8(s0)
        sw x0, 12(s0)
        li t0, 7
        sw t0, 16(s0)
        li t0, -8
        sw t0, 20(s0)
        li t0, 1
        sw t0, 24(s0)
        li t0, 3
        sw t0, 28(s0)
        addi s1, x0, 8        # n
outer:  addi s1, s1, -1
        beqz s1, sorted
        addi t2, x0, 0        # j
        mv   t3, s0           # p = &a[0]
inner:  beq  t2, s1, outer
        lw   t4, 0(t3)
        lw   t5, 4(t3)
        bge  t5, t4, noswap   # a[j+1] >= a[j]: khong doi cho
        sw   t5, 0(t3)
        sw   t4, 4(t3)
noswap: addi t3, t3, 4
        addi t2, t2, 1
        j    inner
sorted: lw   a0, 0(s0)        # nho nhat
        lw   a1, 28(s0)       # lon nhat
done:   j done
# EXPECT a0 = -8
# EXPECT a1 = 12
# EXPECT MEM[0x200] = -8
# EXPECT MEM[0x204] = -3
# EXPECT MEM[0x208] = 0
# EXPECT MEM[0x20C] = 1
# EXPECT MEM[0x210] = 3
# EXPECT MEM[0x214] = 5
# EXPECT MEM[0x218] = 7
# EXPECT MEM[0x21C] = 12
