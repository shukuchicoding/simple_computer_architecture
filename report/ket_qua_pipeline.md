## Ket qua kiem thu CPU pipeline 5 tang

| Chuong trinh | Muc dich | So lenh | Chu ky | CPI | Stall | Flush | Dong test dat | Ket qua |
|---|---|---|---|---|---|---|---|---|
| `t10_loaduse.s` | T10: Load-use - lw roi dung ngay ket qua (chay dung tu Lab 10, khong can nop; khong co lenh nhay) | 22 | 36 | 1.64 | 5 | 1 | 71/71 | **PASS** |
| `t11_control.s` | T11: Hazard dieu khien - nhay ngay sau lenh tinh dieu kien, sau load, jal/jalr lien tiep (chay dung tu Lab 11) | 36 | 66 | 1.83 | 1 | 11 | 131/131 | **PASS** |
| `t13_bytes.s` | T13: LB LH LBU LHU SB SH - doc/ghi byte va half-word, mo rong dau va khong dau | 33 | 43 | 1.30 | 1 | 1 | 85/85 | **PASS** |
| `t14_muldiv.s` | T14: M-extension - MUL MULH MULHSU MULHU DIV DIVU REM REMU, ca bien va phu thuoc lien tiep | 97 | 115 | 1.19 | 1 | 5 | 229/229 | **PASS** |
| `t14b_mulhw.s` | T14b: cung bai toan nhu t6_mul.s nhung dung lenh MUL phan cung (de so sanh so chu ky) | 17 | 26 | 1.53 | 0 | 1 | 51/51 | **PASS** |
| `t15_io.s` | T15: I/O anh xa bo nho - LED, HEX (7 doan), UART TX (TTY), cong tac SW | 124 | 165 | 1.33 | 24 | 5 | 329/329 | **PASS** |
| `t16_predict.s` | T16: Du doan nhanh - vong lap long nhau, mau xen ke, hai nhanh trung chi so BTB, goi ham bang jal | 356 | 463 | 1.30 | 0 | 50 | 925/925 | **PASS** |
| `t1_arith.s` | T1: So hoc / logic va cac ca bien (tran so, dich 0/31, so am, x0) | 32 | 41 | 1.28 | 0 | 1 | 81/81 | **PASS** |
| `t2_sum.s` | T2: Vong lap tinh tong 1..10, luu vao bo nho | 35 | 48 | 1.37 | 0 | 3 | 95/95 | **PASS** |
| `t3_fib.s` | T3: 12 so Fibonacci dau tien, luu mang tai 0x100 | 90 | 103 | 1.14 | 0 | 3 | 205/205 | **PASS** |
| `t4_recursion.s` | T4: De quy fib(8) dung stack (JAL/JALR/SW/LW voi sp) | 637 | 914 | 1.43 | 66 | 102 | 1827/1827 | **PASS** |
| `t5_sort.s` | T5: Sap xep noi bot (bubble sort) 8 so co dau tai 0x200 | 283 | 364 | 1.29 | 28 | 23 | 727/727 | **PASS** |
| `t6_mul.s` | T6: Nhan bang phan mem (dich va cong), goi ham nhieu lan | 446 | 509 | 1.14 | 0 | 28 | 1017/1017 | **PASS** |
| `t7_hazard.s` | T7: Chuoi lenh phu thuoc sat nhau (de kiem tra pipeline o Lab 9-11) | 36 | 60 | 1.67 | 5 | 6 | 119/119 | **PASS** |
| `t9_forward.s` | T9: Forwarding - phu thuoc sat nhau, khong load-use, khong nhay (chay dung tu Lab 9, khong can nop) | 20 | 29 | 1.45 | 0 | 1 | 57/57 | **PASS** |
| `test6a_alu.s` | Lab 6A: lenh ALU R-type, I-type, LUI (chua co nhay, chua co bo nho) | - | 39 | - | 0 | 0 | 77/77 | **PASS** |
| `test6b_mem.s` | Lab 6B: LW / SW | - | 27 | - | 0 | 0 | 53/53 | **PASS** |
| `test6c_branch.s` | Lab 6C: BEQ BNE BLT BGE BLTU BGEU, JAL. x10 dem so nhanh dung = 8, x31 phai = 0 | 28 | 55 | 1.96 | 0 | 10 | 109/109 | **PASS** |
| `test6d_jalr.s` | Lab 6D: JALR, goi ham / tra ve. Ket qua: a0 = 28, t3 = 42, t4 = 1, x31 = 0 | 15 | 42 | 2.80 | 0 | 10 | 83/83 | **PASS** |

*So lenh*: so lenh thuc thi (mo hinh tap lenh) toi vong lap dung. *Chu ky*: so chu ky da so sanh (gom ca chu ky nap/xa pipeline). *Dong test dat*: so dong test vector khop (2 dong/chu ky).
