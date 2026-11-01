# T11: Hazard dieu khien - nhay ngay sau lenh tinh dieu kien, sau load, jal/jalr lien tiep (chay dung tu Lab 11)
        addi x31, x0, 0       # x31 = so lan chay NHAM vao duong sai (phai = 0)
        addi x1, x0, 3
        addi x2, x0, 3
        beq  x1, x2, L1       # nhay; dieu kien phu thuoc 2 lenh ngay truoc (forwarding vao BranchCmp)
        addi x31, x31, 1      # bi FLUSH
        addi x31, x31, 1      # bi FLUSH
L1:     bne  x1, x2, bad      # KHONG nhay: 2 lenh sau van phai chay
        addi x3, x0, 10
        addi x4, x0, 20
        addi x5, x0, 0x100
        sw   x4, 0(x5)
        lw   x6, 0(x5)        # x6 = 20
        beq  x6, x4, L2       # branch ngay sau load: STALL roi moi so sanh, sau do FLUSH
        addi x31, x31, 1
L2:     addi x7, x0, 4        # vong lap lui 4 lan
        addi x8, x0, 0
loop:   addi x8, x8, 5
        addi x7, x7, -1
        bnez x7, loop         # nhay lui 3 lan, lan cuoi khong nhay
        jal  ra, f            # goi ham
        addi x10, x10, 1      # sau khi tra ve: x10 = 101
        jal  x0, J1           # jal toi jal
J1:     jal  x0, J2
        addi x31, x31, 1
J2:     addi x11, x0, 0x70    # dia chi cua nhan tgt (xem listing cua asm.py)
        jalr x12, x11, 0      # jalr phu thuoc lenh ngay truoc
        addi x31, x31, 1
        addi x31, x31, 1
tgt:    addi x13, x0, 13
        j    done
bad:    addi x31, x31, 100
done:   j    done
f:      addi x10, x0, 100
        ret
# EXPECT x31 = 0
# EXPECT x3 = 10
# EXPECT x4 = 20
# EXPECT x6 = 20
# EXPECT x8 = 20
# EXPECT x10 = 101
# EXPECT x12 = 0x68
# EXPECT x13 = 13
# EXPECT MEM[0x100] = 20
