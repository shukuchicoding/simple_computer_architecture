# T16: Du doan nhanh - vong lap long nhau, mau xen ke, hai nhanh trung chi so BTB, goi ham bang jal
        li   s0, 0                # tong
        li   t0, 0                # i
        li   t2, 10
outer:  li   t1, 0                # j
inner:  add  s0, s0, t1           # s0 += j
        addi t1, t1, 1
        blt  t1, t0, inner        # nhanh vong trong: so lan lap thay doi theo i
        addi t0, t0, 1
        bne  t0, t2, outer        # nhanh vong ngoai: nhay 9 lan roi khong nhay
        # mau xen ke nhay / khong nhay (bo dem 2 bit dao dong giua 1 va 2)
        li   t3, 0
        li   s1, 0
        li   t4, 16
alt:    andi t5, t3, 1
        beqz t5, even             # nhay khi t3 chan
        addi s1, s1, 100          # chi chay khi t3 le
even:   addi t3, t3, 1
        bne  t3, t4, alt
        # goi ham 6 lan: jal (du doan duoc qua BTB) + ret (jalr, luon flush)
        li   s2, 0
        li   t6, 6
call:   jal  ra, inc
        addi t6, t6, -1
        bnez t6, call
        j    alias
inc:    addi s2, s2, 7
        ret
        # hai nhanh cach nhau dung 64 byte -> cung chi so BTB (PC[5:2]) nhung khac tag
alias:  li   a0, 0
        li   a1, 5
loopA:  addi a0, a0, 1
        bne  a0, a1, skipA        # nhanh A
        j    pastA
skipA:  nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        nop
        bne  a0, a1, loopA        # nhanh B (cach nhanh A 64 byte)
pastA:  sw   s0, 0x100(x0)
        sw   s1, 0x104(x0)
        sw   s2, 0x108(x0)
done:   j    done
# EXPECT s0 = 120
# EXPECT s1 = 800
# EXPECT s2 = 42
# EXPECT a0 = 5
# EXPECT MEM[0x100] = 120
# EXPECT MEM[0x104] = 800
# EXPECT MEM[0x108] = 42
