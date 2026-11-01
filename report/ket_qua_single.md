## Ket qua kiem thu CPU single-cycle

| Chuong trinh | Muc dich | So lenh | Chu ky | Dong test dat | EXPECT | Ket qua |
|---|---|---|---|---|---|---|
| `t10_loaduse.s` | T10: Load-use - lw roi dung ngay ket qua (chay dung tu Lab 10, khong can nop; khong co lenh nhay) | 22 | 24 | 47/47 | 7/7 | **PASS** |
| `t11_control.s` | T11: Hazard dieu khien - nhay ngay sau lenh tinh dieu kien, sau load, jal/jalr lien tiep (chay dung tu Lab 11) | 36 | 38 | 75/75 | 9/9 | **PASS** |
| `t13_bytes.s` | T13: LB LH LBU LHU SB SH - doc/ghi byte va half-word, mo rong dau va khong dau | 33 | 35 | 69/69 | 21/21 | **PASS** |
| `t14_muldiv.s` | T14: M-extension - MUL MULH MULHSU MULHU DIV DIVU REM REMU, ca bien va phu thuoc lien tiep | 97 | 99 | 197/197 | 22/22 | **PASS** |
| `t14b_mulhw.s` | T14b: cung bai toan nhu t6_mul.s nhung dung lenh MUL phan cung (de so sanh so chu ky) | 17 | 19 | 37/37 | 6/6 | **PASS** |
| `t15_io.s` | T15: I/O anh xa bo nho - LED, HEX (7 doan), UART TX (TTY), cong tac SW | 124 | 126 | 251/251 | 10/10 | **PASS** |
| `t16_predict.s` | T16: Du doan nhanh - vong lap long nhau, mau xen ke, hai nhanh trung chi so BTB, goi ham bang jal | 356 | 358 | 715/715 | 7/7 | **PASS** |
| `t1_arith.s` | T1: So hoc / logic va cac ca bien (tran so, dich 0/31, so am, x0) | 32 | 34 | 67/67 | 26/26 | **PASS** |
| `t2_sum.s` | T2: Vong lap tinh tong 1..10, luu vao bo nho | 35 | 37 | 73/73 | 4/4 | **PASS** |
| `t3_fib.s` | T3: 12 so Fibonacci dau tien, luu mang tai 0x100 | 90 | 92 | 183/183 | 13/13 | **PASS** |
| `t4_recursion.s` | T4: De quy fib(8) dung stack (JAL/JALR/SW/LW voi sp) | 637 | 639 | 1277/1277 | 3/3 | **PASS** |
| `t5_sort.s` | T5: Sap xep noi bot (bubble sort) 8 so co dau tai 0x200 | 283 | 285 | 569/569 | 10/10 | **PASS** |
| `t6_mul.s` | T6: Nhan bang phan mem (dich va cong), goi ham nhieu lan | 446 | 448 | 895/895 | 6/6 | **PASS** |
| `t7_hazard.s` | T7: Chuoi lenh phu thuoc sat nhau (de kiem tra pipeline o Lab 9-11) | 36 | 38 | 75/75 | 17/17 | **PASS** |
| `t9_forward.s` | T9: Forwarding - phu thuoc sat nhau, khong load-use, khong nhay (chay dung tu Lab 9, khong can nop) | 20 | 22 | 43/43 | 13/13 | **PASS** |
| `test6a_alu.s` | Lab 6A: lenh ALU R-type, I-type, LUI (chua co nhay, chua co bo nho) | - | 31 | 61/61 | - | **PASS** |
| `test6b_mem.s` | Lab 6B: LW / SW | - | 19 | 37/37 | - | **PASS** |
| `test6c_branch.s` | Lab 6C: BEQ BNE BLT BGE BLTU BGEU, JAL. x10 dem so nhanh dung = 8, x31 phai = 0 | 28 | 30 | 59/59 | - | **PASS** |
| `test6d_jalr.s` | Lab 6D: JALR, goi ham / tra ve. Ket qua: a0 = 28, t3 = 42, t4 = 1, x31 = 0 | 15 | 17 | 33/33 | - | **PASS** |

*So lenh*: so lenh thuc thi (mo hinh tap lenh) toi vong lap dung. *Chu ky*: so chu ky da so sanh (gom ca chu ky nap/xa pipeline). *Dong test dat*: so dong test vector khop (2 dong/chu ky).
