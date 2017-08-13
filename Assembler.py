# Assembler for NAND to Tetris

# TODO add whitelist

ROMaddr = 0
totalusersymbols = 0

symbols = {"SCREEN":"16384", "KBD":"24576",
           "SP":"0", "LCL":"1", "ARG":"2", "THIS":"3", "THAT":"4"}

compcodes = {"0":"101010", "1":"111111", "-1":"111010",
             "D":"001100", "A":"110000", "M":"110000",
             "!D":"001101", "!A":"110001", "!M":"110001",
             "-D":"001111", "-A":"110011", "-M":"110011",
             "D+1":"011111", "A+1":"110111", "M+1":"110111",
             "D-1":"001110", "A-1":"110010", "M-1":"110010",
             "D+A":"000010", "D+M":"000010",
             "D-A":"010011" , "D-M":"010011",
             "A-D":"000111", "M-D":"000111",
             "D&A":"000000", "D&M":"000000",
             "D|A":"010101", "D|M":"010101"}

# picking out the target file name
source = "Max.asm"
base = source[:source.rfind(".asm")]
target = base + ".hack"

# prep target file
hack = open(target, "w+")

# open up the source and get to work
with open(source) as f:
    # putting file contents in a list like this removes /n newline characters
    file = f.read().splitlines()

    # 1st pass finds & adds label symbols to symbols dict before the real run through
    for line in file:

        # removes comments
        if line.rfind("//") >= 0:
            line = line[:line.rfind("//")]

        # removes empty lines
        if not line:
            continue

        # loop handling, assumes the Hack programmer knows to close these: () parentheses
        if line[0] == "(":
            line = line.strip("(")
            line = line.strip(")")
            line = line.strip()

            # adds label symbol value to dict, referencing how far we are thru the program
            symbols[line] = str(ROMaddr)
            continue
        ROMaddr += 1

    # 2nd pass translates each instruction
    for line in file:
        # removes comments
        if line.rfind("//") >= 0:
            line = line[:line.rfind("//")]
        line = line.strip()
        # removes empty lines
        if not line:
            continue

        # A instruction processing
        if line[0] == "@":
            line = line[1:]

            # handle symbols in a more sane way
            #removes R from R addresses, replaces symbols w/ their value in the dict
            if not line.isdecimal():
                if line[0] == "R":
                    if int(line[1:]) <= 15:
                        line = line[1:]
                # gives new variables a value, starting at 16
                elif line not in symbols:
                    symbols[line] = (16+totalusersymbols)
                    line = symbols[line]
                    totalusersymbols += 1

                elif line in symbols:
                    line = symbols[line]

            # convert decimal to binary
            if str(line).isdecimal():
                line = "{0:b}".format(int(line))

            # ensures our number is 15 bits long
            while len(str(line)) + 1 <= 16:
                line = "0" + str(line)

            hack.write(line + "\n")
            continue

        # C instruction processeing
        elif "=" in line:
            # split the former from the latter operand
            args = line.split("=")

            # start building
            output = "111"

            # determines the "a" control bit
            if "M" in args[1]:
                output += "1"
            else:
                output += "0"

            # starting to enumerate thru possible operands & their respective comp codes
            if args[1] in compcodes:

                output += str(compcodes[args[1]])

            # assign destination control bits
            dest = ""
            if "A" in args[0]:
                dest += "1"
            else:
                dest += "0"
            if "D" in args[0]:
                dest += "1"
            else:
                dest += "0"
            if "M" in args[0]:
                dest += "1"
            else:
                dest += "0"
            output += str(dest)
            # for the jump bits, always 0 if there's an equation
            output += "000"

            hack.write(output + "\n")

        # Jump instruction handling
        elif ";" in line:
            # starts the output off
            output = "1110"

            # assign jump instruction bits
            args = line.split(";")
            args[0].strip()

            if args[0] in compcodes:
                output += str(compcodes[args[0]])

            # adding dest bits
            output += "000"

            args[1].strip()
            if args[1] == "JGT":
                output += "001"
            elif args[1] == "JEQ":
                output += "010"
            elif args[1] == "JGE":
                output += "011"
            elif args[1] == "JLT":
                output += "100"
            elif args[1] == "JNE":
                output += "101"
            elif args[1] == "JLE":
                output += "110"
            elif args[1] == "JMP":
                output += "111"
            else:
                output += "000"

            hack.write(output + "\n")
