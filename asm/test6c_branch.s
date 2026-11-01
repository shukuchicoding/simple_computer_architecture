# Lab 6C: BEQ BNE BLT BGE BLTU BGEU, JAL. x10 dem so nhanh dung = 8, x31 phai = 0
        addi x1, x0, 1
        addi x2, x0, -1
        addi x10, x0, 0
        beq  x1, x1, L1       # nhay
        addi x31, x0, 1       # khong duoc chay
L1:     addi x10, x10, 1
        beq  x1, x2, bad      # khong nhay
        bne  x1, x2, L2       # nhay
        addi x31, x0, 2
L2:     addi x10, x10, 1
        blt  x2, x1, L3       # -1 < 1: nhay
        addi x31, x0, 3
L3:     addi x10, x10, 1
        bltu x2, x1, bad      # 0xFFFFFFFF < 1 (khong dau): khong nhay
        bge  x1, x2, L4       # 1 >= -1: nhay
        addi x31, x0, 4
L4:     addi x10, x10, 1
        bgeu x2, x1, L5       # 0xFFFFFFFF >= 1: nhay
        addi x31, x0, 5
L5:     addi x10, x10, 1
        addi x3, x0, 3        # vong lap nhay lui 3 lan
loop:   addi x3, x3, -1
        addi x10, x10, 1
        bne  x3, x0, loop
        jal  x5, L6           # x5 = dia chi lenh ngay sau jal
        addi x31, x0, 6
L6:     j    done
bad:    addi x31, x0, 99
done:   j    done
