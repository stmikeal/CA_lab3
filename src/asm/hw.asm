.data:
    hw 'Hello, World!'
.text:
    .start:
        pprt hw
        je .hlt
        jmp .start
    .hlt:
        hlt