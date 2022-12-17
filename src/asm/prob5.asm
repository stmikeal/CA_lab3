%define TASK_TARGET 20              ; Число для которого решается задача

array dd TASK_TARGET                ; Массив с простыми числами

init_array: 
    mov ebx, array
    mov ecx, TASK_TARGET
    mov r8, 0
.array_loop:
    mov [ebx], r8
    add ebx, 4                       ; Работаем с 32 бита, поэтому прибавляем 4
    loop .array_loop
    ret

mark_even:
    mov r8, 1
    mov edx, ecx
.array_loop:
    mov [ebx], r8
    mov ecx, rax
.pointer_loop:
    add ebx, 4
    dec edx
    loop .pointer_loop
    cmp edx, 0
    jnz .array_loop
    ret

inc_result:
    mov eax, rax
.mul_even:
    mul rax
    cmp eax, TASK_TARGET
    jl .mul_even
    div rax
    mul r10
    mov r10, eax
    ret


make_even:
    mov rax, 2                       ; Счетчик текущего числа
    mov ebx, array
    mov ecx, TASK_TARGET             ; Счетчик цикла
    dec ecx
.array_loop:
    add ebx, 4
    cmp [ebx], 0
    push ebx
    push ecx
    je is_even
.end_of_even:
    pop ebx
    pop ecx
    inc rax
    loop .array_loop
    ret
.is_even:
    call mark_even
    call inc_result
    jmp .end_of_even

start:
    mov r10, 1                        ; Результат работы программы
    call init_array
    call make_even


    