## So sanh hieu nang

| Chuong trinh | So lenh | Single-cycle (chu ky) | Lab 8 (+3 nop/lenh) | Lab 9 forwarding (+nop sau lw, nhay) | Lab 10 +stall (+nop sau nhay) | Lab 11 day du (khong nop) | Lab 16 du doan nhanh | CPI Lab 16 |
|---|---|---|---|---|---|---|---|---|
| t10_loaduse.s | 22 | 22 | 94 | 40 | 36 | 36 | 36 | 1.64 |
| t11_control.s | 36 | 36 | sai | sai | sai | 68 | 66 | 1.83 |
| t13_bytes.s | 33 | 33 | 138 | 57 | 43 | 43 | 43 | 1.30 |
| t14_muldiv.s | 97 | 97 | 381 | 141 | 141 | 133 | 115 | 1.19 |
| t14b_mulhw.s | 17 | 17 | 74 | 26 | 26 | 26 | 26 | 1.53 |
| t15_io.s | 124 | 124 | 486 | 239 | 235 | 189 | 165 | 1.33 |
| t16_predict.s | 356 | 356 | 1353 | 611 | 611 | 555 | 463 | 1.30 |
| t1_arith.s | 32 | 32 | 134 | 41 | 41 | 41 | 41 | 1.28 |
| t2_sum.s | 35 | 35 | 137 | 65 | 64 | 62 | 48 | 1.37 |
| t3_fib.s | 90 | 90 | 355 | 124 | 123 | 121 | 103 | 1.14 |
| t4_recursion.s | 637 | 637 | 2587 | 1281 | 1248 | 1048 | 914 | 1.43 |
| t5_sort.s | 283 | 283 | 1089 | 548 | 518 | 418 | 364 | 1.29 |
| t6_mul.s | 446 | 446 | 1703 | 859 | 859 | 653 | 509 | 1.14 |
| t7_hazard.s | 36 | 36 | sai | 67 | 66 | 60 | 60 | 1.67 |
| t9_forward.s | 20 | 20 | 86 | 29 | 29 | 29 | 29 | 1.45 |
| test6c_branch.s | 28 | 28 | 109 | 61 | 61 | 55 | 55 | 1.96 |
| test6d_jalr.s | 15 | 15 | sai | 52 | 52 | 42 | 42 | 2.80 |

Ghi chu: CPU single-cycle co 1 chu ky/lenh nhung chu ky rat dai (bang tong tre ca 5 tang); pipeline co chu ky ngan hon ~5 lan (bang tre tang cham nhat). CPI Lab 16 gom ca vai chu ky nap/xa pipeline ban dau.
