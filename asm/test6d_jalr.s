# Lab 6D: JALR, goi ham / tra ve. Ket qua: a0 = 28, t3 = 42, t4 = 1, x31 = 0
        addi a0, x0, 7
        jal  ra, double       # a0 = 14
        jal  ra, double       # a0 = 28
        jal  t1, base         # t1 = dia chi 'base'
base:   jalr t2, t1, 13       # dich = (base + 13) & ~1 = base + 12 = target; t2 = base + 4
        addi x31, x0, 1       # khong duoc chay
        addi x31, x0, 2       # khong duoc chay
target: addi t3, x0, 42
        jal  ra, f2
        addi t4, x0, 1        # f2 phai quay ve day
        j    done
double: add  a0, a0, a0
        ret
f2:     jalr ra, ra, 0        # rd = rs1: dich phai tinh tu ra CU
done:   j    done
