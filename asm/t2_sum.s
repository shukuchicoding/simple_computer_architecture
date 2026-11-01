# T2: Vong lap tinh tong 1..10, luu vao bo nho
        addi x1, x0, 10       # dem nguoc
        addi x2, x0, 0        # tong
loop:   add  x2, x2, x1
        addi x1, x1, -1
        bne  x1, x0, loop
        sw   x2, 0(x0)
        lw   x3, 0(x0)
done:   beq  x0, x0, done
# EXPECT x2 = 55
# EXPECT x3 = 55
# EXPECT x1 = 0
# EXPECT MEM[0x000] = 55
