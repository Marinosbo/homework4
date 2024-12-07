import struct
import sys

COMMANDS = {
    "LOAD_CONST": 25,
    "READ_MEM": 31,
    "WRITE_MEM": 8,
    "SGN": 10,
    "ADD": 50,
    "SUB": 51,
    "JZ": 52,
    "JMP": 53,
    "HALT": 54,
}

def assemble(input_file, binary_file, log_file):
    labels = {}
    with open(input_file, 'r') as asm_file:
        lines = asm_file.readlines()

    # First pass: Collect labels and store their line numbers
    current_line = 0
    for line in lines:
        line = line.split("#")[0].strip()  # Remove comments
        if not line:
            continue

        if ":" in line:  # Check if it's a label
            label = line.split(":")[0].strip()
            labels[label] = current_line
        else:
            current_line += 1  # Increase line number for non-label lines

    # Second pass: Assemble the instructions
    with open(binary_file, 'wb') as bin_file, open(log_file, 'w') as log:
        for line in lines:
            line = line.split("#")[0].strip()
            if not line:
                continue

            if ":" in line:  # Skip label lines
                continue

            parts = line.split()
            command = parts[0]
            args = parts[1:]

            if command not in COMMANDS:
                raise ValueError(f"Unknown command: {command}")
            opcode = COMMANDS[command]

            # Resolve label references in arguments
            resolved_args = []
            for arg in args:
                if arg in labels:
                    # If the argument is a label, replace it with its address
                    resolved_args.append(labels[arg])
                else:
                    # Otherwise, it's a literal value, so convert it to an integer
                    try:
                        resolved_args.append(int(arg))
                    except ValueError:
                        raise ValueError(f"Invalid argument: {arg} for command {command}")

            # Now `resolved_args` contains either integers or addresses
            args = resolved_args

            if command in ["LOAD_CONST", "READ_MEM", "SGN"]:
                if args[0] < 0 or args[0] > 8191:  # 13 bits
                    raise ValueError(f"Operand {args[0]} out of range (0-8191)")
                packed = (opcode << 13) | args[0]
                bin_file.write(struct.pack(">I", packed))  # 32-bit format
            elif command == "WRITE_MEM":
                if args[0] < 0 or args[0] > 524287:  # 19 bits
                    raise ValueError(f"Operand {args[0]} out of range (0-524287)")
                packed = (opcode << 19) | args[0]
                bin_file.write(struct.pack(">I", packed))  # 32-bit format
            log.write(f"command={command}, args={args}\n")


COMMANDS.update({
    "ADD": 50,
    "SUB": 51,
    "JZ": 52,
    "JMP": 53,
    "HALT": 54,
})

def interpret(binary_file, result_file, memory_size=1024):
    memory = [0] * memory_size
    accumulator = 0
    program_counter = 0
    changed_memory = set()  # Адреса измененных ячеек памяти

    with open(binary_file, 'rb') as bin_file:
        instructions = list(iter(lambda: bin_file.read(4), b""))
        while program_counter < len(instructions):
            byte_data = instructions[program_counter]
            program_counter += 1

            command = int.from_bytes(byte_data, "big")
            opcode = command >> 13
            operand = command & 0x1FFF

            if opcode == COMMANDS["LOAD_CONST"]:
                accumulator = operand
            elif opcode == COMMANDS["READ_MEM"]:
                accumulator = memory[operand]
            elif opcode == COMMANDS["WRITE_MEM"]:
                memory[operand] = accumulator
                changed_memory.add(operand)  # Отмечаем, что адрес изменился
            elif opcode == COMMANDS["SGN"]:
                accumulator = 1 if accumulator > 0 else -1 if accumulator < 0 else 0
            elif opcode == COMMANDS["ADD"]:
                accumulator += operand
            elif opcode == COMMANDS["SUB"]:
                accumulator -= operand
            elif opcode == COMMANDS["JZ"]:
                if accumulator == 0:
                    program_counter = operand
            elif opcode == COMMANDS["JMP"]:
                program_counter = operand
            elif opcode == COMMANDS["HALT"]:
                break

    # Записываем измененные адреса памяти
    with open(result_file, 'w') as res_file:
        writer = csv.DictWriter(res_file, fieldnames=["address", "value"])
        writer.writeheader()
        for address in sorted(changed_memory):
            writer.writerow({"address": address, "value": memory[address]})

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Usage: script.py assemble|interpret input_file output_file [log_file]", file=sys.stderr)
        sys.exit(1)

    mode = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]
    log_file = sys.argv[4] if len(sys.argv) > 4 else None

    if mode == "assemble":
        assemble(input_file, output_file, log_file)
    elif mode == "interpret":
        interpret(input_file, output_file)
    else:
        print(f"Unknown mode: {mode}", file=sys.stderr)
