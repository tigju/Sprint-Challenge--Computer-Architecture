"""CPU functionality."""

import sys

LDI = 0b10000010
PRN = 0b01000111
HLT = 0b00000001
ADD = 0b10100000
SUB = 0b10100001
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
CMP = 0b10100111
JMP = 0b01010100
JEQ = 0b01010101
JNE = 0b01010110
AND = 0b10101000
OR = 0b10101010
XOR = 0b10101011
NOT = 0b01101001
SHL = 0b10101100
SHR = 0b10101101
MOD = 0b10100100


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 255
        self.reg = [0] * 8
        self.reg[7] = 0xF4
        self.pc = 0
        self.sp = 7
        self.halted = False
        self.fl = 0b00000000


    def load(self, filename):
        """Load a program into memory."""
        address = 0
        if len(filename) > 1:
            try:
                with open(filename[1]) as my_file:
                    for line in my_file:
                        split_line = line.split('#')
                        
                        code_value = split_line[0].strip() ## removes white space and new line \n
                        # check that value before # is not empty
                        if code_value == "":
                            continue 
                        instruction = int(code_value, 2)
                        self.ram_write(address, instruction)
                        address += 1

            except FileNotFoundError:
                print(f'{filename[1]} file not found')
                sys.exit(2)
        else:
            print("File name as a second argument is missing. Ex.: python ls8.py filename")
            sys.exit(1)


    def ram_read(self, address):
        """ read from ram by specified address and returns stored value"""
        return self.ram[address]

    def ram_write(self, address, value):
        """ writes the value to a address specified into ram"""
        self.ram[address] = value

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""
        
        if op == ADD:
            self.reg[reg_a] += self.reg[reg_b]
        
        elif op == SUB: 
            self.reg[reg_a] -= self.reg[reg_b]

        elif op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]
        
        elif op == CMP:
            if self.reg[reg_a] == self.reg[reg_b]:
                self.fl = 0b00000001
            elif self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b00000100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b00000010

        elif op == AND:
            self.reg[reg_a] = self.reg[reg_a] & self.reg[reg_b]

        elif op == OR:
            self.reg[reg_a] = self.reg[reg_a] | self.reg[reg_b]

        elif op == XOR:
            self.reg[reg_a] = self.reg[reg_a] ^ self.reg[reg_b]

        elif op == NOT:
            self.reg[reg_a] = ~self.reg[reg_a]

        elif op == SHL:
            self.reg[reg_a] = self.reg[reg_a] << self.reg[reg_b]

        elif op == SHR:
            self.reg[reg_a] = self.reg[reg_a] >> self.reg[reg_b]

        elif op == MOD:
            pass


        
        else:
            raise Exception(f'Unsupported ALU operation {bin(op)}')

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        while not self.halted:
            instruction = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc+1)
            operand_b = self.ram_read(self.pc+2)
            self.execute_instruction(instruction, operand_a, operand_b)

    def execute_instruction(self, instruction, operand_a, operand_b):

        if instruction == LDI:
            self.reg[operand_a] = operand_b
            self.pc += 3

        elif instruction == MUL:
            self.alu(instruction, operand_a, operand_b)
            self.pc += 3
        
        elif instruction == ADD:
            self.alu(instruction, operand_a, operand_b)
            self.pc += 3

        elif instruction == PRN:
            print(self.reg[operand_a])
            self.pc += 2

        elif instruction == PUSH:
            self.reg[self.sp] -= 1 # decrement stack pointer
            self.ram_write(self.reg[self.sp], self.reg[operand_a])
            self.pc += 2

        elif instruction == POP:
            self.reg[operand_a] = self.ram_read(self.reg[self.sp])
            self.reg[self.sp] += 1
            self.pc += 2

        elif instruction == CALL:
            self.reg[self.sp] -= 1  # decrement stack pointer
            # strores the address of next instruction on top of the stack
            address_of_next_instruction = self.pc + 2
            self.ram_write(self.reg[self.sp], address_of_next_instruction)
            # jumps to the address stored in that register
            # we explicitly set the counter in CALL instruction
            self.pc = self.reg[operand_a]

        elif instruction == RET:
            # doesn't take any operands, sets the program counter to the topmost element of the stack and pop it
            self.pc = self.ram_read(self.reg[self.sp])
            self.reg[self.sp] += 1

        elif instruction == CMP:
            self.alu(instruction, operand_a, operand_b)
            self.pc += 3

        elif instruction == JMP:
            self.pc = self.reg[operand_a]
        
        elif instruction == JEQ:
            if self.fl == 1:
                self.pc = self.reg[operand_a]
            else:
                self.pc += 2

        elif instruction == JNE:
            if self.fl != 1:
                self.pc = self.reg[operand_a]
            else:
                self.pc += 2

        elif instruction == HLT:
            self.halted = True
            self.pc += 1
            exit()
            
        else:
            print(f"Unknown opcode! {bin(instruction)}")
            sys.exit(1)
