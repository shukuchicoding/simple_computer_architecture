"""Dac ta 4 thanh ghi pipeline: (ten truong, so bit, bi xoa khi Flush?).
Moi truong X co pin vao 'X_in' va pin ra 'X_out'. Chung: EN, Flush, clk, Reset.
Khi canh len: neu EN=1 hoac Flush=1 -> nap; truong danh dau True bi nap 0 neu Flush=1.
Reset (bat dong bo) -> moi truong = 0."""
PIPE_REGS = {
    "IF_ID": [("PC", 32, False), ("PC4", 32, False), ("Instr", 32, True)],
    "ID_EX": [("PC", 32, False), ("PC4", 32, False), ("RD1", 32, False), ("RD2", 32, False), ("Imm", 32, False),
              ("rs1", 5, False), ("rs2", 5, False), ("rd", 5, False), ("f3", 3, False), ("Instr", 32, True),
              ("RegWrite", 1, True), ("ALUSrc", 1, True), ("MemRead", 1, True), ("MemWrite", 1, True),
              ("MemToReg", 2, True), ("Branch", 1, True), ("Jump", 1, True), ("Jalr", 1, True), ("ALUctl", 4, True)],
    "EX_MEM": [("PC", 32, False), ("Result", 32, False), ("WData", 32, False), ("rd", 5, False), ("Instr", 32, True),
               ("RegWrite", 1, True), ("MemRead", 1, True), ("MemWrite", 1, True), ("MemToReg", 2, True)],
    "MEM_WB": [("PC", 32, False), ("Result", 32, False), ("RData", 32, False), ("rd", 5, False), ("Instr", 32, True),
               ("RegWrite", 1, True), ("MemToReg", 2, True)],
}
