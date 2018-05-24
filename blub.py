# Angelica Munyao
# HW 5 - Part 1

# Write a program that processes files written in "Blub" assembly language.
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

# The blub.py program should be runnable from the command line. To do so, we
# require the sys module.
import sys

# To create the class Instruction using a named tuple, we will need the collections
# module.
from collections import namedtuple

#To create a regular expression, we require the re module.
import re


# Write an Instruction class to create Instruction objects that can be used to
# define a Program object.
class Instruction(namedtuple('Instruction', ['label', 'instruction', 'condition',
                                             'op1', 'op2', 'op3'])):
    """
    A class that represents a "blub" assembly language instruction.
    """

    __slots__ = ()  # This ensures that memory requirements are kept low by preventing
    # the creation of instance dictionaries.

    # Class methods
    # Print the instruction:
    # As a string
    def __str__(self):
        """
        Return the string representation of an Instruction object.
        :return: The instruction as a string.
        """

        return ((self.label + ": ") if (self.label != "") else "    ") + self.instruction \
               + self.condition + " " + self.op1 + ((", " + self.op2) if (self.op2 != "")
                                                    else "") + ((", " + self.op3) if (self.op3 != "") else "")

    # As a syntactically correct string that can be used to recreate the object
    # Since we have used namedtuple to define the class, a __repr__ function has been
    # defined for us already using the name-value pairs in the tuple.


# Write the Program class to process a .blub file into a Program object.
class Program:
    """
    A class that represents a "blub" assembly language program.
    """

    # Class constructor
    def __init__(self, aProgramFile):
        """
        The constructor for the Program class.
        It takes a "blub" program as an argument and parses its lines.

        :param aProgramFile: The "blub" program file to be formatted.
        """

        # First open the given file to access its content.
        theFile = open(aProgramFile)

        # As we process each line, we generate a dictionary of instructions to initialize the
        # Program class instance.
        self.program = {}

        # Initialize a value to generate the keys.
        self.aKey = 1

        # Process each line accordingly.
        for aLine in theFile:
            # Format the line accordingly to separate the parts of a single instruction.
            # A line may have a label, an instruction name (may or may not have a condition)
            # and operands (may be a label, registers or immediate values depending on the
            # instruction.
            # Account for extraneous whitespaces.

            # First split the line to get out any existing labels.
            labelSplit = aLine.split(':')

            # Next split the instruction from its operands.
            instructSplit = ([x for x in labelSplit[1].split(" ") if x != '']
                             if len(labelSplit) > 1
                             else [x for x in labelSplit[0].split(" ") if x != ''])

            # Every line would at least have an instruction and one operand. We need not worry about
            # having a line without an instruction or at least one operand. Initialize the
            # instruction for easier use.
            theInstruction = instructSplit[0].strip()

            # Create a regular expression for use in the instruction creation. We will need to take out some
            # characters from some strings generated through splitting a program line.
            strrmv = re.compile('[\s,]')

            # Create an instruction object and add it to the program list.
            self.program[self.aKey] = Instruction(label=(labelSplit[0].strip() if len(labelSplit) > 1 else '')
                                                   , instruction=(theInstruction[0] if theInstruction[0] == 'b'
                                                                  else theInstruction)
                                                   , condition=(theInstruction[1:]
                                                                if theInstruction[0] == 'b' else '')
                                                   , op1=strrmv.sub('', instructSplit[1])
                                                   , op2=(strrmv.sub('', instructSplit[2]) if len(instructSplit) > 2
                                                          else '')
                                                   , op3=(strrmv.sub('', instructSplit[3]) if len(instructSplit) > 3
                                                          else '')
                                                   )

            # Increment aKey
            self.aKey += 1

        # After the loop is completed, we should have a dictionary of instructions.

        # Generate the dictionary with the labels in the program and their line numbers.
        self.labelLocator = {y.label: x for (x, y) in self.program.items() if y.label}



    # Class methods

    # Print the program as a string
    def __str__(self):
        """
        Prints the contents of the program in a better formatted manner.
        :return: The program as a list of instructions.
        """

        # Create a large string to print out.
        programStr = ""

        for aKey in range(1, self.aKey):
            programStr += (str(aKey) + '    ' + str(self.program[aKey]) + "\n")

        return programStr


    # Get an instruction given a line number (line numbers start from one)
    def __getitem__(self, lineNum):
        """
        Get an instruction from the program at the given index.
        :param lineNum: The index  of the desired instruction.
        :return: The desired instruction at the given index.
        """

        return self.program[lineNum]


    #Get the line number of the first instruction within a given label.
    def getAddress(self, aLabel):
        """
        Get the line number of the first instruction within the given label.
        :param aLabel: The label of a set of instructions.
        :return: The line number of the first instruction within the label.
        """

        return self.labelLocator[aLabel]


    # Get the number of instructions in a program
    def __len__(self):
        """
        Get the number of instructions in a program.
        :return: The number of instructions in a program.
        """

        return len(self.program)


    # Add a new instruction to the program
    def __setitem__(self, lineNum, anInstruction : Instruction):
        """
        Add an instruction to the program at the given line number.
        :param lineNum: The line number at which one wishes to add an instruction.
        :param anInstruction: The instruction to be added.
        """

        if (lineNum <= len(self.program)):

            #If the line number given is one already with an instruction, we have to
            #shift some instructions down first before we can add the instruction.
            for num in range((lineNum - 1), self.aKey):
                #Move the instructions from the last to the first one.
                self.program[((lineNum - 1) + len(self.program)) - (num - 1)] = self.program[
                    ((lineNum - 1) + len(self.program)) - num]

            #Add the instruction to the given line number
            self.program[lineNum] = anInstruction

            #Update the values of labelLocator
            self.labelLocator = {x: ((y + 1) if (y >= lineNum) else y) for (x, y) in self.labelLocator.items()}

            # Add the line number to labelLocator if the added instruction has a label.
            if anInstruction.label:
                self.labelLocator[anInstruction.label] = lineNum

        # We assume someone would sensibly add a new instruction to the next available space if
        #the instruction is not added.
        else:
            #Add the instruction.
            self.program[self.aKey] = anInstruction

            #Add the line number to labelLocator if the added instruction has a label.
            if anInstruction.label:
                self.labelLocator[anInstruction.label] = self.aKey

        #Increment aKey in preparation for other instruction additions.
        self.aKey += 1


    # Delete an instruction from the program
    def __delitem__(self, lineNum):
        """
        Remove an instruction from the program at the given line number.
        :param lineNum: The line number from which one wishes to remove an instruction.

        """

        #Delete the instruction
        del self.program[lineNum]

        #Decrement aKey in preparation for other instruction additions.
        self.aKey -= 1

        #We have to shift some instructions up after we remove the instruction.
        for num in range(lineNum, self.aKey):
            #Move the instructions from the last to the first one.
            self.program[num] = self.program[num + 1]

        #Take out the last instruction as it will be a duplicate.
        del self.program[self.aKey]

        #Update the values of labelLocator
        self.labelLocator = {x: ((y - 1) if (y >= lineNum) else y) for (x, y) in self.labelLocator.items()
                             if y != lineNum}



#We shall use this purely as a module to access Program and Instruction classes.

# # The main program of blub.py
# if __name__ == '__main__':
#     # User will input the name of the program in the command line.
#     # Capture the name and create a Program object, then print its contents.
#     prog = Program(sys.argv[1])
#
#     #Prints the program with line numbers starting from 1.
#     print(prog)
