/* Ban do bo nho cho chuong trinh C (Harvard):
   ROM (IMEM) : 0x0000 - 0x0FFF  ma lenh (.text); cc.py dat doan "khoi tao du lieu" o dau ROM
   RAM (DMEM) : 0x1000 - 0x1FFF  du lieu (.rodata .data .bss) + ngan xep (sp = 0x2000, tang xuong)
                (DMEM chi dung bit 2..11 cua dia chi nen 0x1000 tro vao o 0 cua RAM)
   I/O        : 0x80000000 LED, +4 HEX, +8 UART TX, +0xC SW                                  */
ENTRY(_start)
TEXT_START = 0x0;          /* cc.py thay gia tri nay khi lien ket lan 2 */
SECTIONS {
  .text TEXT_START : { KEEP(*(.text.start)) *(.text .text.*) }
  .rodata 0x1000 : { *(.rodata .rodata.* .srodata .srodata.*) }
  .data : { *(.data .data.* .sdata .sdata.*) }
  .bss : { *(.bss .bss.* .sbss .sbss.* COMMON) }
  _end = .;
  /DISCARD/ : { *(.eh_frame*) *(.comment) *(.riscv.attributes) }
}
