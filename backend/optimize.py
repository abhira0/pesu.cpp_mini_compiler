from main1 import ClassSymbolTable
import pickle
import sys

expressions = {}
replacements = {}
sources = set()
destinations = set()

def _get_value(x):
	try:
		return int(x)
	except:
		pass

	try:
		return float(x)
	except:
		pass

	return x

def get_operations():
	return [
		'ADD',
		'SUB',
		'MUL',
		'DIV',
	]

def get_relops():
	return [
		'LT',
		'GT',
		'LE',
		'GE',
		'EQ',
		'NEQ',
	]

def perform_operation(operation, var1, var2):
	t = type(var1)
	if operation == 'ADD':
		return t(var1 + var2)
	if operation == 'SUB':
		return t(var1 - var2)
	if operation == 'MUL':
		return t(var1 * var2)
	if operation == 'DIV':
		return t(var1 / var2)

def update_element(elt, *, updated_val = None):
	if updated_val != None:
		temp = updated_val
		return str(temp)
	elif elt in SymbolTable.symbols and SymbolTable.symbols[elt]['value'] != None:
		temp = SymbolTable.symbols[elt]['value']
		return str(temp)
	else:
		temp = get_value(elt, SymbolTable)         # get value
		return str(temp)

def update_expressions(expr, value):
	'''
	expr : tuple
		(operation, var1, var2)
	'''
	expressions[expr] = value

def expression_exists(expr):
	'''
	expr : tuple
		(operation, var1, var2)
	'''
	return expr in expressions.keys()

def get_expression_val(expr):
	return expressions[expr]

def write_optimized_file(optimized_tac):
	with open(f'optimized-{sys.argv[1]}', 'w') as file:
		for line in optimized_tac:
			x = '\t'.join(line) + '\n'
			if x[0] != 'l':
				x = '\t' + x
			file.write(str(x))

def update_replacements(var, val):
	replacements[var] = val

def replacement_exists(var):
	return var in replacements.keys()

def get_replacement(var):
	return replacements[var]

def get_value(x, SymbolTable):
	if x in SymbolTable.symbols and SymbolTable.symbols[x]['value'] != None:
		return SymbolTable.symbols[x]['value']
	else:
		return _get_value(x)

if __name__ == '__main__':
	#SymbolTable = pickle.load(open('symbol_table.pkl', 'rb'))
	with open("./symbol_table.json") as f:
        symbol_table = json.load(f)
	
	tac = []
	f = open(sys.argv[1], 'r')
	for i in f:
		x = i.strip().split('\t')
		tac.append(x)

	optimized_tac = []

	for line in tac:
		try:
			if line[3][0] != 'l' and line[0] != 'VAR':
				destinations.add(line[3])
		except:
			pass

		instruction = line[0]									# [op	var1	var2	result] --> Quadraple Format
		if instruction == 'VAR':
			optimized_tac.append(line)
		elif instruction == 'ASSIGN':							# [=	var1	(emp)	result] --> Quadraple Format
			variable = line[3]									# Result field in the quadraple
			value = get_value(line[1], SymbolTable)				
			SymbolTable.update_val(variable, value)
			SymbolTable.update_type(variable, type(value))

			if replacement_exists(line[1]):
				print(f'Replacing {line[1]} -> {get_replacement(line[1])} in line: ', end='\t')
				print('\t'.join(line))
				value = get_value(get_replacement(line[1]), SymbolTable)
				sources.add(get_replacement(line[1]))
			else:
				if type(_get_value(line[1])) == type(""):
					sources.add(line[1])

			update_replacements(line[3], line[1])

			if line[3][0] != 't':
				line[1] = update_element(line[1], updated_val=value)
				optimized_tac.append(line)
		elif instruction in get_operations():
			variable = line[3]
			variable1 = get_value(line[1], SymbolTable)
			variable2 = get_value(line[2], SymbolTable)
			value = perform_operation(
						operation=line[0],
						var1=variable1,
						var2=variable2
					)
			SymbolTable.update_val(variable, value)
			SymbolTable.update_type(variable, type(value))

			if replacement_exists(line[1]):
				print(f'Replacing {line[1]} -> {get_replacement(line[1])} in line: ', end='\t')
				print('\t'.join(line))
				line[1] = get_replacement(line[1])

			if replacement_exists(line[2]):
				print(f'Replacing {line[2]} -> {get_replacement(line[2])} in line: ', end='\t')
				print('\t'.join(line))
				line[2] = get_replacement(line[2])

			expr = (line[0], line[1], line[2])
			if not expression_exists(expr):
				update_expressions(expr, variable)
			else:
				update_replacements(variable, get_expression_val(expr))
				continue

			if type(_get_value(line[1])) == type(""):
				sources.add(line[1])
			if type(_get_value(line[2])) == type(""):
				sources.add(line[2])

			if line[3][0] != 't':
				line[1] = update_element(line[1])
				line[2] = update_element(line[2])
				optimized_tac.append(line)

		elif instruction[0] == 'l':
			optimized_tac.append(line)

		elif instruction in get_relops():		# relop		Var1	Var2	(=	a	b)
			variable1 = line[1]
			variable2 = line[2]
			line[1] = update_element(line[1])
			line[2] = update_element(line[2])
			optimized_tac.append(line)

			# for i in range(1,3):
				# if type(_get_value(line[i])) == type(""):
					# sources.add(line[i])

			if type(_get_value(line[1])) == type(""):
				sources.add(line[1])
			if type(_get_value(line[2])) == type(""):
				sources.add(line[2])

		elif instruction == 'GOTO':
			optimized_tac.append(line)


	write_optimized_file(optimized_tac)

	# SymbolTable.display()







