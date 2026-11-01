# Máy tính RISC-V 32-bit trên Logisim-evolution

Thiết kế, mô phỏng và kiểm thử một CPU 32-bit theo tập lệnh **RISC-V RV32I**, gồm hai phiên bản:

| Phiên bản | File | Đặc điểm |
|---|---|---|
| Đơn chu kỳ (single-cycle) | `single/riscv_single.circ` | Mỗi lệnh hoàn thành trong 1 chu kỳ |
| Pipeline 5 tầng | `pipeline/riscv_pipe.circ` | IF → ID → EX → MEM → WB, có **forwarding**, **stall** khi load-use, **flush** khi nhảy, **dự đoán nhánh** (BTB 16 mục + bộ đếm 2 bit) |

Hai phiên bản dùng chung thư viện module `modules/riscv_modules.circ`.

## 1. Tập lệnh hỗ trợ

| Nhóm | Lệnh |
|---|---|
| Số học / logic (R) | `add sub and or xor slt sltu sll srl sra` |
| Số học / logic (I) | `addi andi ori xori slti sltiu slli srli srai` |
| Bộ nhớ | `lw sw` và **`lb lh lbu lhu sb sh`** (mở rộng) |
| Nhảy có điều kiện | `beq bne` và **`blt bge bltu bgeu`** (mở rộng) |
| Nhảy không điều kiện | `jal jalr` |
| Nhân/chia (M-extension) | **`mul mulh mulhsu mulhu div divu rem remu`** (mở rộng) |
| Khác | `lui` |

Tổng cộng 44 lệnh (25 lệnh bắt buộc + 19 lệnh mở rộng). Không hỗ trợ `auipc`, `fence`, `ecall`, CSR.

**Vào/ra ánh xạ bộ nhớ** (địa chỉ ≥ `0x80000000`, dùng `lw`/`sw`):

| Địa chỉ | Thiết bị | Ghi | Đọc |
|---|---|---|---|
| `0x80000000` | 8 LED | đặt LED | giá trị đã ghi |
| `0x80000004` | 8 LED 7 đoạn | 8 chữ số hex | giá trị đã ghi |
| `0x80000008` | UART TX → TTY | gửi 1 ký tự | `1` = sẵn sàng |
| `0x8000000C` | 8 công tắc DIP | – | trạng thái công tắc |

Lệnh giả mà assembler chấp nhận: `nop mv li j jr ret beqz bnez`, và `jal nhan` (tương đương `jal ra, nhan`).

Thông số: dữ liệu 32 bit, lệnh 32 bit, 32 thanh ghi × 32 bit (x0 luôn bằng 0), PC 32 bit. Bộ nhớ lệnh (ROM) và bộ nhớ dữ liệu (RAM) mỗi bộ 1024 word = 4 KB, địa chỉ theo byte.

## 2. Yêu cầu phần mềm

- **Logisim-evolution 4.1.0.** Để chạy test bằng dòng lệnh cần file `logisim-evolution-4.1.0-all.jar` và **Java 21** trở lên.
- **Python 3.8+**. Các công cụ chỉ dùng thư viện chuẩn.
- Chỉ khi biên dịch chương trình C: `pip install ziglang` (trình biên dịch clang + lld cho RISC-V, chạy được trên Windows/Linux/macOS).

## 3. Cấu trúc thư mục

```
riscv32/
├── README.md
├── modules/riscv_modules.circ   Thư viện 20 module: ALU, RegFile, ImmGen, BranchCmp, PCUnit, Control,
│                                IF_ID, ID_EX, EX_MEM, MEM_WB, ForwardUnit, WBBypass, HazardUnit,
│                                LoadExt, StoreMerge, MulDiv, IsMul, MemMap, BTB, PredRegs
├── single/riscv_single.circ     CPU đơn chu kỳ (circuit CPU, IMEM, DMEM, IO, main)
├── pipeline/riscv_pipe.circ     CPU pipeline 5 tầng (circuit CPU, IMEM, DMEM, IO, main)
├── asm/                         Chương trình test (assembly)
├── c/                           Thư viện cho chương trình C: start.S, link.ld, riscv_io.h, rt.c
├── demo/calc.c                  Chương trình C demo (công tắc → TTY, LED 7 đoạn, LED)
├── rom/                         File nạp ROM (.hex, định dạng "v2.0 raw"), file ROM điều khiển
├── tests/                       Test vector cho từng module
├── tools/                       Công cụ Python (xem mục 7)
└── report/                      Bảng kết quả kiểm thử (sinh tự động)
```

Hai file CPU nạp thư viện theo **đường dẫn tương đối** `../modules/riscv_modules.circ`. Khi chép project sang máy khác, phải giữ nguyên cấu trúc thư mục.

## 4. Mở project và chạy mô phỏng

1. Mở Logisim-evolution, chọn **File → Open**, chọn `single/riscv_single.circ` hoặc `pipeline/riscv_pipe.circ`.
2. Circuit `main` chứa khối `CPU`, một **Clock**, nút **RESET** và các Probe hiển thị `PC`, `Instr`, `WB`… Bản pipeline hiển thị thêm lệnh ở từng tầng: `Instr_D`, `Instr_E`, `Instr_M`, `Instr_W`.
3. Nhấn **Ctrl+R** để reset mô phỏng (PC về 0, xóa thanh ghi và RAM).
4. Chạy CPU:
   - **Ctrl+T**: tiến nửa chu kỳ. Hai lần Ctrl+T bằng một chu kỳ.
   - **Ctrl+K**: bật/tắt chạy tự động. Đổi tốc độ ở *Simulate → Auto-Tick Frequency*.
5. Quan sát trạng thái:
   - Nhấp đúp khối `CPU`, rồi nhấp đúp `RegFile` để xem 31 thanh ghi `x1…x31`.
   - Nhấp đúp `DMEM` để xem RAM (ô `n` ứng với địa chỉ byte `4n`).

## 5. Nạp chương trình

1. Viết chương trình assembly trong `asm/`, ví dụ `asm/vidu.s`.
2. Dịch ra file nạp ROM:
   ```
   python tools/asm.py asm/vidu.s -o rom/vidu.hex
   ```
   Lệnh in ra listing (địa chỉ, mã máy, lệnh). Nếu có lỗi, nó báo kèm số dòng.
3. Trong Logisim, nhấp đúp `IMEM` ở cây Design, chuột phải vào ROM, chọn **Load Image…** rồi chọn `rom/vidu.hex`.
4. Quay về `main`, nhấn **Ctrl+R**, rồi chạy.

Để xem trước kết quả đúng của chương trình (trạng thái thanh ghi và bộ nhớ cuối cùng), dùng mô phỏng tập lệnh bằng Python:
```
python tools/rvsim.py asm/vidu.s          # thêm -t để in từng lệnh
python tools/pipesim.py asm/vidu.s -t     # sơ đồ pipeline từng chu kỳ (IF/ID/EX/MEM/WB, stall, flush)
```

Chương trình nên kết thúc bằng vòng lặp dừng `done: j done`.

### Chương trình C
```
python tools/cc.py demo/calc.c                     # -> rom/calc.hex, nạp vào ROM như trên
python tools/cc.py demo/calc.c --run --sw 10       # chạy thử bằng mô phỏng Python, in TTY/LED/HEX
```
`cc.py` biên dịch (rv32im, không thư viện chuẩn), kiểm mọi lệnh nằm trong tập lệnh CPU, và sinh thêm đoạn mã đầu ROM để chép dữ liệu (`.rodata`, `.data`) vào RAM. Bộ nhớ cho C: mã từ `0x0`, dữ liệu từ `0x1000`, ngăn xếp từ `0x2000` đi xuống. Thiết bị I/O dùng qua `c/riscv_io.h`.

## 6. Chạy kiểm thử

Mọi lệnh chạy từ thư mục `riscv32`. Có thể đặt biến môi trường `LOGISIM_JAR` thay cho tham số `--jar`.

### 6.1. Toàn bộ, bằng một lệnh
```
python tools/check_all.py --jar <đường dẫn>/logisim-evolution-4.1.0-all.jar
```
Lệnh chạy lần lượt các phần ở mục 6.2–6.4, ghi bảng kết quả vào `report/`, rồi in tổng kết. Mất khoảng 1–2 phút.

### 6.2. Test từng module
```
python tools/run_tests.py --jar <jar>              # tất cả
python tools/run_tests.py --jar <jar> ALU Control  # chỉ một số module
```
Mỗi module được kiểm bằng test vector trong `tests/`:
- module tổ hợp: vét cạn các ca biên và thêm các ca ngẫu nhiên;
- module tuần tự: kiểm theo từng chu kỳ clock, dùng cột `<set>`/`<seq>`.

### 6.3. Test CPU theo từng chu kỳ
```
python tools/cpu_test.py "asm/t*_*.s" --jar <jar>              # CPU đơn chu kỳ
python tools/cpu_test.py "asm/t*_*.s" --pipe 16 --jar <jar>    # CPU pipeline (có dự đoán nhánh)
python tools/cpu_test.py rom/calc_test.hex --sw 13 --jar <jar>  # chương trình C (file .hex), công tắc = 13
```
Với mỗi chương trình, công cụ làm các việc sau:
1. Dịch chương trình.
2. Nạp chương trình vào ROM của một **bản sao** file `.circ` (file gốc không bị sửa).
3. Chạy Logisim ở chế độ dòng lệnh.
4. So sánh **ở mọi chu kỳ** các tín hiệu `PC`, `Instr`, `RegWrite`, `rd`, `WB`, `MemWrite`, `MemAddr`, `MemWData` (và `IOWrite`, khi CPU có pin I/O) với mô hình tham chiếu (`rvsim.py` cho đơn chu kỳ, `pipesim.py` cho pipeline). Giá trị công tắc lấy từ dòng `# SW = ...` trong file `.s` hoặc tùy chọn `--sw`.

Khi có sai lệch, công cụ in ra chu kỳ bị sai, lệnh đang nằm ở từng tầng, và giá trị thực tế so với giá trị mong đợi.

Các tùy chọn khác:
- `--md report/x.md`: ghi bảng kết quả dạng Markdown.
- `--gen tests/x.txt`: chỉ sinh test vector, để chạy bằng menu *Simulate → Test Vector*.

### 6.4. So sánh hiệu năng
```
python tools/compare.py "asm/t*_*.s" --md report/so_sanh.md
```

## 7. Công cụ

| File | Chức năng |
|---|---|
| `tools/asm.py` | Assembler RV32I: từ `.s` sinh `.hex` (Logisim "v2.0 raw") |
| `tools/rvsim.py` | Mô phỏng tập lệnh (mô hình tham chiếu đơn chu kỳ); kiểm các dòng `# EXPECT` trong file `.s` |
| `tools/pipesim.py` | Mô hình pipeline 5 tầng chính xác từng chu kỳ (`--lab 8/9/10/11/16`) |
| `tools/cc.py` | Biên dịch chương trình C thành file nạp ROM (cần `pip install ziglang`) |
| `tools/cpu_test.py` | So sánh CPU Logisim với mô hình, từng chu kỳ |
| `tools/run_tests.py` | Chạy test vector của các module |
| `tools/check_all.py` | Chạy toàn bộ kiểm thử, sinh báo cáo |
| `tools/compare.py` | Bảng so sánh số chu kỳ và CPI |
| `tools/gen_*.py` | Sinh test vector và nội dung ROM điều khiển (`rom/control.rom`, `rom/aluctl.rom`) |
| `tools/package.py` | Đóng gói bài nộp thành file `.zip` |

## 8. Chương trình test

| File | Nội dung | Kết quả chính |
|---|---|---|
| `t1_arith.s` | Số học/logic, tràn số, dịch 0/31/33, so sánh có/không dấu, ghi x0 | 26 giá trị EXPECT |
| `t2_sum.s` | Vòng lặp tổng 1..10 | `x2 = 55`, `MEM[0] = 55` |
| `t3_fib.s` | 12 số Fibonacci ghi vào mảng | `MEM[0x12C] = 89` |
| `t4_recursion.s` | Đệ quy `fib(8)` dùng stack | `s0 = 21` |
| `t5_sort.s` | Sắp xếp nổi bọt 8 số có dấu | mảng tại `0x200` tăng dần |
| `t6_mul.s` | Phép nhân bằng dịch và cộng | `123 × 456 = 56088`, `−7 × 9 = −63` |
| `t7_hazard.s` | Chuỗi lệnh phụ thuộc sát nhau | 17 giá trị EXPECT |
| `t9_forward.s` | Forwarding, bypass WB→ID | 13 giá trị EXPECT |
| `t10_loaduse.s` | Load-use (5 lần stall) | 7 giá trị EXPECT |
| `t11_control.s` | Hazard điều khiển: branch sau `lw`, `jal`/`jalr` liên tiếp | `x31 = 0` (không chạy nhầm lệnh nào) |
| `t13_bytes.s` | LB/LH/LBU/LHU, SB/SH ở mọi vị trí byte | 21 giá trị EXPECT |
| `t14_muldiv.s` | 8 lệnh M, tràn, chia cho 0, giai thừa, UCLN | 22 giá trị EXPECT |
| `t14b_mulhw.s` | Bài toán của `t6_mul` bằng lệnh `mul` | 26 chu kỳ pipeline (so với 653) |
| `t15_io.s` | LED, HEX, UART TX, công tắc; ghi I/O không đè RAM | TTY = `Hi RISC-V!` |
| `t16_predict.s` | Vòng lồng nhau, mẫu xen kẽ, `jal`, hai nhánh trùng chỉ số BTB | 463 chu kỳ (555 khi chưa dự đoán) |
| `test6a…6d_*.s` | Từng nhóm lệnh: ALU, bộ nhớ, branch, JALR | |
| `demo15_io.s` | Demo I/O chạy liên tục (không có vòng dừng) | |

Các giá trị mong đợi được ghi ngay trong file bằng các dòng `# EXPECT x10 = 55`, `# EXPECT MEM[0x100] = 50`, `# EXPECT LED = 0x5A`, `# EXPECT TTY = "Hi\n"`.

## 9. Kết quả kiểm thử

- Test vector module: **25/25 lượt đạt** (20 module thư viện + IMEM, DMEM, IO; 12.255 ca).
- CPU đơn chu kỳ: **19/19 chương trình đạt**.
- CPU pipeline có dự đoán nhánh: **19/19 chương trình đạt mà không chèn `nop`**, khớp mô hình từng chu kỳ.
- Chương trình C `demo/calc.c` chạy khớp mô hình từng chu kỳ trên cả hai CPU.

Chi tiết xem `report/ket_qua_single.md`, `report/ket_qua_pipeline.md`, `report/so_sanh.md`.
