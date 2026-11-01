addi x1, x0, 5
add  x3, x1, x2
sub  x4, x1, x2
lw   x5, 8(x1)
sw   x5, 12(x1)
beq  x1, x2, end
jal  ra, end
slli x7, x1, 4
srai x8, x2, 1
lui  x9, 0x12345
end: nop