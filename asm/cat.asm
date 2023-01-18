.data:
.text:
    .start:
        rd
        prt
        je .hlt
        jmp .start
    .hlt:
        hlt