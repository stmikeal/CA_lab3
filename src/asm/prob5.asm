.data:
    result 1
    prime  1
    target 0
    count  0
.text:
    .start:
        rd 
        sv  target
    .loop:
        ld  prime
        add 1
        cmp target
        je .hlt
        sv prime
        sv count
    .inner_loop:
        ld count
        sub 1
        sv count
        cmp 1
        je .mul_to_max
        ld prime
        div count
        jc .inner_loop
        jmp .loop
    .mul_to_max:
        ld 1
    .mul_loop:
        mul prime
        cmp target
        jl .mul_loop
        je .mul_loop
        div prime
        mul result
        sv result
        jmp .loop
    .hlt:
        ld result
        prt
        hlt