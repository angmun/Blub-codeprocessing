# Angelica Munyao
# HW 5 - Part 2

# Write a program that processes Program objects written in "Blub" assembly language.
# The program should be interpreted based on its parts: labels, instructions,
# registers, immediate values and so on.

# Assumptions made prior to code writing:
#   The passed program file is written such that labels are expected to be on the
#   same line as the first instruction they represent.
#
#   Label declarations always end with a colon. the colon is not part of the
#   label name.
#
#   Instructions ending in 'i' are immediate instructions with its last
#   operand being an immediate value.
#
#   Registers start with an 'r' that is succeeded by a number.
#
#   Spaces separate instruction names from the operands.
#
#   Commas separate the operands.
#
#   There may be extra whitespace within an instruction in the passed program.

# The blubvm.py program should be runnable from the command line. To do so, we
# require the sys module.
import sys

# To initialize an array as our representation of registers, we will need the array module.
import array

# To create Program objects, and access Instruction attributes, import the blub module.
import blub


# Write the Machine class to interpret a Program object and run it.
class Machine:

    """
    A class that creates a Machine object to interpret and run a Program object.
    """

    # Class variables:
    # Initialize an array of size 32 to represent registers.
    registers = array.array('i', [0 for i in range(32)])

    # Define functions to test conditions for the branch operation in a blub program.
    # Greater than:
    def gt(self):
        return not(bool(self.flags['n'])) and not(bool(self.flags['z']))
    # Greater than or equal to:
    def ge(self):
        return bool(self.flags['z']) or not(bool(self.flags['n']))
    # Equal to:
    def eq(self):
        return bool(self.flags['z'])
    # Not equal to:
    def ne(self):
        return not(bool(self.flags['z']))
    # Less than or equal to:
    def le(self):
        return bool(self.flags['z']) or bool(self.flags['n'])
    # Less than:
    def lt(self):
        return bool(self.flags['n']) and not(bool(self.flags['z']))

    # Initialize a dictionary reference for conditions and the flag combinations necessary for them to be met.
    conditions = {'gt': gt, 'ge': ge, 'eq': eq, 'ne':ne,'le': le, 'lt': lt}

    # Initialize a dictionary of sets that represent the instructions with a single operand, the instructions with
    # two operands, and the instructions with three operands.
    # NB// Given the processing of blub programs, any branch instruction is divided into 'b' as the instruction
    # and following sequence of characters as a condition when setting up the Instruction object.
    Ops ={'ops1':{'prnt','b'}, 'ops2':{'movi', 'cmpi'}, 'ops3':{'andi','add','lsri'}}


    # Class constructor:
    def __init__(self, aProgram : blub.Program):
        """
        The constructor for the Machine class.
        It takes a Program object containing 'blub' code and sets it up for interpretation.

        :param aProgram: A Program object to interpret and run.
        """

        # Instance variables:
        # Initialize a code variable to store the given Program object.
        self.code = aProgram

        # Initialize a program counter variable to store the value of the current line in the program being
        # executed. Start it at the first line number.
        self.pc = 1

        # Initialize a dictionary to store flag values that are results from the "cmp" instruction.
        # NB:// Given this implementation of this interpreter using pure Python, we need not really worry about
        # overflow or carry outs from the operations done. The operations are on integers so far, and from
        # online research, recent versions of Python have their integers with arbitrary precision, where the
        # limit to the size of an integer is based on available memory. I have included the 'c' and 'v' flags
        # nonetheless so that all the flags are there.
        self.flags = {'n':0, 'z':0, 'c':0, 'v':0}



    # Instruction functions:
    # NB:// Given the design for interpretation of the code that I have decided to go with, I would require some
    # placeholder parameters for instructions with less than three inputs. This allows the passing of the three
    # operand values from an Instruction object, which has three operand attributes defined. As such, some of
    # the functions will have a *args parameter to capture the extra arguments without using them.

    # Compare two values and modify the flag values accordingly to determine whether a condition has been met.
    def cmpi(self, reg, val, *placeHolder):
        """
        Compares two values and modifies the condition flag values accordingly based on the comparison result.

        :param reg: A register in which a value to be compared with another is found.
        :param val: A value to be compared with the value in a given register.

        """

        # Get the value in the given register.
        valr = self.registers[reg]

        # Compare will modify the values of 'n' and/or 'z', as it determines the relationship between two
        # numerical values based on their difference:

        # Valr is greater than val:
        if ((valr - val) > 0):
            # The difference is not zero and non-negative.
            self.flags['n'] = 0
            self.flags['z'] = 0

        # Valr is equal to val:
        elif ((valr - val) == 0):
            # The difference is zero.
            self.flags['z'] = 1

        # Valr is less than val:
        else:
            # The difference is not zero and negative.
            self.flags['n'] = 1
            self.flags['z'] = 0



    # Branch to a label either with or without a condition.
    def b(self, label, *cond):
        """
        Branches to a given label in the program. May do so given the satisfaction of an optional condition.
        Does so by updating the program counter with the line number of the label.

        :param label: A label in a blub program to branch to.
        :param cond: An optional condition to be met before branching to a given label.

        """

        # Check whether the condition has been met if a condition is passed to the function.
        if cond[0] == '' or self.conditions[cond[0]](self):
            # Update the program counter if there is no condition passed.
            # NB:// The interpreter increments the program counter as it goes through each instruction
            # line to move to the next instruction. as such, we update the program counter with the label's
            # line number minus 1, so that the increment results in the correct line number being the next
            # to be executed.
            self.pc = self.code.labelLocator[label] - 1



    # 'Bitwise and' two given values.
    def andi(self,retReg, reg, val):
        """
        Finds the 'bitwise and' of two given values and stores it in the given destination register.

        :param retReg: A register to which the result is assigned.
        :param reg: A register where the value to be 'bitwise and'ed with another is found.
        :param val: A value to 'bitwise and' with the value in the given register.

        """

        # Get the value in the given register.
        valr = self.registers[reg]

        # Find the 'bitwise and' of the two values.
        bitand = valr & val

        # Store the 'bitwise and' result in the given destination register.
        self.registers[retReg] = bitand



    # Add two given values.
    def add(self, retReg, reg1, reg2):
        """
        Finds the sum of two given values and stores it in the given destination register.

        :param retReg: A register to which the result is assigned.
        :param reg1: A register address where the value to be added to another is found.
        :param reg2: A register address where the value to be added to another is found.

        """

        # Get the values in the given register addresses.
        val1 = self.registers[reg1]
        val2 = self.registers[reg2]

        # Find the sum of the two values.
        theSum = val1 + val2

        # Store the sum in the given destination register address.
        self.registers[retReg] = theSum



    # Perform a logical shift right by a given number of bits on a given value.
    def lsri(self, retReg, reg, val):
        """
        Performs a logical right shift on a given value by a given number of bits and stores the result
        in the given destination register.

        :param retReg: The register to which the result is assigned.
        :param reg: A register where the value to be shifted right is found.
        :param val: A number of bits by which to shift the value in the given register.

        """

        # Get the value in the given register.
        valr = self.registers[reg]

        # Shift valr by val number of bits.
        lsr = valr >> val

        # Store the result of the shift in the given destination register.
        self.registers[retReg] = lsr



    # Move a given value into a given register.
    def movi(self, retReg, val, *placeHolder):
        """
        Moves a given value into a given register.

        :param retReg: A register into which the given value is to be placed.
        :param val: A value to load into the given register.

        """

        # Move the value into the given register.
        self.registers[retReg] = val



    # Print the value in a given register.
    def prnt(self, retReg, *placeHolder):
        """
        Prints the value stored in a given register.

        :param retReg: The register from which we get the value to print.

        """

        #Print the value in the given register
        print(self.registers[retReg])



    # Initialize a dictionary of instructions and the operations they map to.
    operators = {'cmpi':cmpi, 'b':b, 'andi': andi, 'add':add, 'lsri':lsri, 'movi':movi, 'prnt':prnt}



    # Instance methods:
    # Add an instruction to the Machine object. This assumes that one who intends to do so is familiar with
    # the general syntax of 'blub' instructions, and have taken that into account when defining their function.
    def __setitem__(self, instrName, aFunction, noOfOps):
        """
        Adds an instruction definition to the Machine object.

        :param instrName: The name of the instruction.
        :param aFunction: The function representing an instruction.
        :param noOfOps: The number of operands the instruction has.

        """

        #First check whether the given number of operands is between 1 and 3.
        if noOfOps < 1 or noOfOps > 3:
            #We cannot add the instruction.
            exit("Instruction must have at least one operand and at most three operands to be added.")

        # Add the instruction to our dictionary of operators.
        self.operators[instrName] = aFunction

        #Add the instruction to the appropriate set based on its number of operands.
        self.Ops['ops' + str(noOfOps)].add(instrName)



    # Delete an instruction in the Machine object.
    # NB:// For those instructions we have defined within this class, we need not have them removed as their
    # definitions would still remain within the class. Let us consider them base instructions and allow the
    # deletion of added instructions.
    def __delitem__(self, instrName):
        """
        Removes an instruction definition from the Machine object if it is not a base instruction defined
        within the class.

        :param instrName: The name of the instruction to be removed.

        """
        if not (instrName in {x for x in self.operators.keys()} ):
            del self.operators[instrName]



    # Define decorators for error checking based on the number of operands an instruction has.
    def ops1error(self, anInstruction):
        def check(self, *args):
            # There are more operands than required.
            # A non-register was passed for a non-branch instruction.
            # A non-existent label was passed for a branch instruction.
            # A non-existent condition was passed for a branch instruction.

            if (anInstruction.__name__ != 'b' and args[1]) or args[2] \
                    or (anInstruction.__name__ != 'b' and (args[0][:1] != 'r' or (not args[0][1:].isdigit()))) \
                    or (anInstruction.__name__ == 'b' and (not args[0] in self.code.labelLocator.keys()))\
                    or (anInstruction.__name__ == 'b' and args[1] and (not args[1] in self.conditions.keys())):
                exit("Error: " + anInstruction.__name__)

            else:
                # Get the operand values and convert them to numbers (if appropriate) so they can be used to
                # execute the respective instruction:

                # Accommodate a 'b' instruction so that a label string is captured.
                op1 = (int(args[0].replace('r', '')) if anInstruction.__name__ != 'b'
                       else args[0])
                # Accommodate a 'b' instruction so that any condition if it exists is captured.
                op2 = args[1]

                return anInstruction(self, op1, op2)
        return check


    def ops2error(self, anInstruction):
        def check(self,*args):
            # There are more or less operands than required.
            # Non-registers were passed for register instructions.
            # Non-integer was passed for immediate instruction's last operand.
            if (not args[1]) or args[2]\
                     or args[0][:1] != 'r' or (not args[0][1:].isdigit())\
                     or (anInstruction.__name__[-1] != 'i' and (args[1][:1] != 'r' or (not args[1][1:].isdigit()))) \
                     or (anInstruction.__name__[-1] == 'i' and (not args[1].isdigit())):
                exit("Error: " + anInstruction.__name__)

            else:
                # Get the operand values and convert them to numbers (if appropriate) so they can be used to
                # execute the respective instruction:
                op1 = int(args[0].replace('r', ''))
                op2 = int(args[1].replace('r', ''))

                return anInstruction(self, op1, op2)
        return check


    def ops3error(self, anInstruction):
        def check(self, *args):
            # There are less operands than required.
            # NB// We only expect a maximum of 3 operand inputs based on the structure of an Instruction object.
            # Non-registers were passed for register instructions.
            # Non-integer was passed for immediate instruction's last operand.
            if not args[1] or not args[2]\
                     or args[0][:1] != 'r' or (not args[0][1:].isdigit())\
                     or args[1][:1] != 'r' or (not args[1][1:].isdigit())\
                     or (anInstruction.__name__[-1] == 'i' and (not args[2].isdigit()))\
                     or (anInstruction.__name__[-1] != 'i' and (args[2][:1] != 'r' or (not args[2][1:].isdigit()))):
                exit("Error: " + anInstruction.__name__)

            else:
                # Get the operand values and convert them to numbers so they can be used to
                # execute the respective instruction:
                op1 = int(args[0].replace('r', ''))
                op2 = int(args[1].replace('r', ''))
                op3 = int(args[2].replace('r', ''))

                return anInstruction(self, op1, op2, op3)
        return check



    # Interpret and run the program.
    def interpret(self):

        # Interpret the instructions of the program until there are no more instructions to do so.
        while self.pc <= len(self.code):
            # Work on each of the lines of the program, accessing them by line number.

            # First check whether the line has an instruction, the instruction is defined in the machine, and
            # it has at least one operand.
            if self.code[self.pc].instruction != '' and self.code[self.pc].op1 != '' and \
                self.code[self.pc].instruction in self.operators.keys():

                # We can work on the instruction. At this point we know that the instruction should at
                # least have one operation.

                #Add the relevant decorator to the function based on its number of operands.
                if self.code[self.pc].instruction in self.Ops['ops1']:
                    #Add the appropriate decorator:
                    self.ops1error(self.operators[self.code[self.pc].instruction])(self, self.code[self.pc].op1,
                                                                   self.code[self.pc].condition,
                                                                   self.code[self.pc].op2)

                elif self.code[self.pc].instruction in self.Ops['ops2']:
                    #Add the appropriate decorator:
                    self.ops2error(self.operators[self.code[self.pc].instruction])(self, self.code[self.pc].op1,
                                                                   self.code[self.pc].op2,
                                                                   self.code[self.pc].op3)

                else:
                    #Add the appropriate decorator:
                    self.ops3error(self.operators[self.code[self.pc].instruction])(self, self.code[self.pc].op1,
                                                                   self.code[self.pc].op2,
                                                                   self.code[self.pc].op3)

                # Update the program counter:
                self.pc += 1

            # The line of code has not met the minimum requirements for interpretation.
            else:
                # Exit out of the program since an error was encountered.
                exit("Error: Improperly formatted instruction encountered. Cannot interpret the program.")



# The main program of blub.py
if __name__ == '__main__':
    # User will input the name of the program in the command line.
    # Capture the name and create a Program object, then print its contents.
    prog = blub.Program(sys.argv[1])

    #Prints the program with line numbers starting from 1.
    print(prog)

    #Run the program
    interpreter = Machine(prog)
    print("Result:")
    interpreter.interpret()
