# T4: De quy fib(8) dung stack (JAL/JALR/SW/LW voi sp)
        li   sp, 0x1000       # dinh stack (0x1000 quay vong ve 0x000, push dau tien vao 0xFFC)
        addi a0, x0, 8
        jal  ra, fib
        mv   s0, a0           # fib(8) = 21
        sw   s0, 0x80(x0)
done:   j done

fib:    addi t0, x0, 2        # a0 = n -> a0 = fib(n)
        blt  a0, t0, base     # n < 2: tra ve n
        addi sp, sp, -12
        sw   ra, 8(sp)
        sw   a0, 4(sp)
        addi a0, a0, -1
        jal  ra, fib          # fib(n-1)
        sw   a0, 0(sp)
        lw   a0, 4(sp)
        addi a0, a0, -2
        jal  ra, fib          # fib(n-2)
        lw   t1, 0(sp)
        add  a0, a0, t1
        lw   ra, 8(sp)
        addi sp, sp, 12
base:   ret
# EXPECT s0 = 21
# EXPECT sp = 0x1000
# EXPECT MEM[0x080] = 21
