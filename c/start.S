# Diem vao cua chuong trinh C: dat con tro ngan xep roi goi main(); main tra ve -> dung
    .section .text.start
    .global _start
_start:
    li   sp, 0x2000          # dinh RAM (o nho 0x1FFC la o cuoi cung)
    jal  ra, main
1:  j    1b                  # vong lap dung (cpu_test nhan biet "j .")
