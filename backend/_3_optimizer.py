import json
import pickle
import sys

from termcolor import cprint
from _2_parser import SymbolTable

xpr = {}
rpl = {}
srcs = set()
dsts = set()


class utils:
    @staticmethod
    def getActualValue(x):
        try:
            return int(x)
        except:
            ...
        try:
            return float(x)
        except:
            ...
        return x

    @staticmethod
    def setZero(x):
        if type(x) == type(""):
            return 0
        return x

    @staticmethod
    def performOp(operation, var1, var2):
        t = type(var1)
        print(var1, var2)
        var1 = utils.setZero(var1)
        var2 = utils.setZero(var2)
        if operation == "ADD":
            return t(var1 + var2)
        elif operation == "SUB":
            return t(var1 - var2)
        elif operation == "MUL":
            return t(var1 * var2)
        elif operation == "DIV":
            return t(var1 / var2)

    @staticmethod
    def updateElement(elt, updated_val=None):
        if updated_val != None:
            temp = updated_val
            return str(temp)
        elif elt in SymTable.symbols and SymTable.symbols[elt]["value"] != None:
            temp = SymTable.symbols[elt]["value"]
            return str(temp)
        else:
            temp = utils.getVal(elt, SymTable)
            return str(temp)

    @staticmethod
    def updateExprs(expr, value):
        """
        expr : tuple
                (operation, var1, var2)
        """
        xpr[expr] = value

    @staticmethod
    def exprExists(expr):
        """
        expr : tuple
                (operation, var1, var2)
        """
        return expr in xpr.keys()

    @staticmethod
    def getExprVal(expr):
        return xpr[expr]

    @staticmethod
    def opOpt(optimized_tac):
        with open(f"optimized-3code", "w") as file:
            for line in optimized_tac:
                x = "\t".join(line) + "\n"
                if x[0] != "l":
                    x = "\t" + x
                file.write(str(x))

    @staticmethod
    def updateRepl(var, val):
        rpl[var] = val

    @staticmethod
    def replExists(var):
        return var in rpl.keys()

    @staticmethod
    def getRepl(var):
        return rpl[var]

    @staticmethod
    def getVal(x, SymTable):
        if x in SymTable.symbols and SymTable.symbols[x]["value"] != None:
            return SymTable.symbols[x]["value"]
        else:
            return utils.getActualValue(x)


if __name__ == "__main__":
    SymTable = pickle.load(open("symbol_table.pkl", "rb"))

    tac = []
    for i in open("3code.txt", "r"):
        x = i.strip().split("\t")
        tac.append(x)

    optimized_tac = []

    for line in tac:
        try:
            if line[3][0] != "l" and line[0] != "VAR":
                dsts.add(line[3])
        except:
            ...
        instruction = line[0]  # [op	var1	var2	result] --> Quadruple Format

        """ -----------------------------------------------------------------------------------------------------------
            |	NO OPTIMIZATION SECTION
            ----------------------------------------------------------------------------------------------------------- """

        if instruction == "VAR":
            optimized_tac.append(line)
        elif instruction == "GOTO":
            optimized_tac.append(line)
        elif instruction[0] == "l":
            optimized_tac.append(line)
            """ -----------------------------------------------------------------------------------------------------------
                |	ASSIGNMENT OPERATION OPTIMIZATION
                ----------------------------------------------------------------------------------------------------------- """
        elif instruction == "ASSIGN":  # [	=	var1	(emp)	result	] --> Quadruple Format
            variable = line[3]  # Result field in the quadruple
            value = utils.getVal(line[1], SymTable)
            SymTable.update_val(variable, value)
            SymTable.update_type(variable, type(value))

            if utils.replExists(line[1]):
                print(
                    f"Replacing {line[1]} -> {utils.getRepl(line[1])} in line: ",
                    end="\t",
                )
                print("\t".join(line))
                value = utils.getVal(utils.getRepl(line[1]), SymTable)
                srcs.add(utils.getRepl(line[1]))
            else:
                if type(utils.getActualValue(line[1])) == type(""):
                    srcs.add(line[1])

            utils.updateRepl(line[3], line[1])

            if line[3][0] != "t":
                line[1] = utils.updateElement(line[1], updated_val=value)
                optimized_tac.append(line)

            """ -----------------------------------------------------------------------------------------------------------
                |	MATHEMATICAL OPERATION OPTIMIZATION
                ----------------------------------------------------------------------------------------------------------- """

        elif instruction in ["ADD", "SUB", "MUL", "DIV"]:
            variable = line[3]
            variable1 = utils.getVal(line[1], SymTable)
            variable2 = utils.getVal(line[2], SymTable)
            value = utils.performOp(operation=line[0], var1=variable1, var2=variable2)
            SymTable.update_val(variable, value)
            SymTable.update_type(variable, type(value))

            if utils.replExists(line[1]):
                print(
                    f"Replacing {line[1]} -> {utils.getRepl(line[1])} in line: ",
                    end="\t",
                )
                print("\t".join(line))
                line[1] = utils.getRepl(line[1])

            if utils.replExists(line[2]):
                print(
                    f"Replacing {line[2]} -> {utils.getRepl(line[2])} in line: ",
                    end="\t",
                )
                print("\t".join(line))
                line[2] = utils.getRepl(line[2])

            expr = (line[0], line[1], line[2])
            if not utils.exprExists(expr):
                utils.updateExprs(expr, variable)
            else:
                utils.updateRepl(variable, utils.getExprVal(expr))
                continue

            if type(utils.getActualValue(line[1])) == type(""):
                srcs.add(line[1])
            if type(utils.getActualValue(line[2])) == type(""):
                srcs.add(line[2])

            if line[3][0] != "t":
                line[1] = utils.updateElement(line[1])
                line[2] = utils.updateElement(line[2])
                optimized_tac.append(line)

            """ -----------------------------------------------------------------------------------------------------------
                |	RELATIONAL OPERATOR OPTIMIZATION
                ----------------------------------------------------------------------------------------------------------- """

        elif instruction in ["LT", "GT", "LE", "GE", "EQ", "NEQ"]:
            # ['LT','GT','LE','GE','EQ','NEQ',]
            variable1 = line[1]  #
            variable2 = line[2]
            line[1] = utils.updateElement(line[1])
            line[2] = utils.updateElement(line[2])
            optimized_tac.append(line)

            # for i in range(1,3):
            # if type(utils.getActualValue(line[i])) == type(""):
            # sources.add(line[i])

            if type(utils.getActualValue(line[1])) == type(""):
                srcs.add(line[1])
            if type(utils.getActualValue(line[2])) == type(""):
                srcs.add(line[2])

    utils.opOpt(optimized_tac)

    with open("./optimized-3code", "r") as f:
        for i in f.readlines():
            cprint(i, "cyan", end="")

    SymTable.display()