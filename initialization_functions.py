"""This file contains functions to initialize variables and to change the default values if desired

Functions:
change_value() -- Change any variable value in the program utilizing user input.
change_others() -- This function checks if the user wants to change any other variables.
initialize() -- This function contains all default values and defines all initial variables.
"""
import msvcrt

def change_value(datatype, lowerbound = None, upperbound = None):
	"""Change any variable value in the program utilizing user input.

	Parameters
	----------
	datatype : enter 'int', 'float', or 'string'
		The type of the variable to be changed.
	lowerbound : either an int or float, optional
		The lowest value the variable can be changed to.
	upperbound : either an int or float, optional
		The lowest value the variable can be changed to. 

	Returns
	-------
	new_value : new variable value, of type datatype
		The new value the user input to have the value changed to
	"""
	while True: # create infinite loop
		print('What would you like to change it to?')
		if datatype == 'string':    # if the variable to be changed is a string
			new_value = input()    # get the new value of the variable from the user
			print('Is this input okay: ', new_value, ' (Enter y or n)')
			good = input()  # get input from the user
			if good == 'y': # if the input was good
				break   # exit the while loop
		if datatype == 'int':   # if the variable to be changed is an int
			new_value = int(input())    # get the new value of the variable from the user
			if not(lowerbound is None) and not(upperbound is None):     # if both upper and lower bounds were given
				if (new_value <= lowerbound) or (new_value >= upperbound):  # check if this value is within the given bounds
					print('Error: You entered a value that is not within (', lowerbound, ', ', upperbound, ')')
					break
			elif not(lowerbound is None):   # if no upper bound was given 
				if (new_value <= lowerbound):   # check if the value is too low
					print('Error: You entered a value that is lower than or equal to ', lowerbound)
					break            
			elif not(upperbound is None):   # if no lower bound was given 
				if (new_value <= lowerbound) or (new_value >= upperbound):  # check if the value is too high
					print('Error: You entered a value that is higher than or equal to ',upperbound)
					break
			print('Is this input okay: ', new_value, ' (Enter y or n)')
			good = input()  # get input from the user
			if good == 'y': # if the input was good
				break
		if datatype == 'float': # if the variable to be changed is a float
			new_value = float(input())  # get the new value of the variable from the user
			if not(lowerbound is None) and not(upperbound is None): # if both upper and lower bounds were given
				if (new_value <= lowerbound) or (new_value >= upperbound):  # check if this value is within the given bounds
					print('Error: You entered a value that is not within (', lowerbound, ', ', upperbound, ')')
					break
			elif not(lowerbound is None):   # if no upper bound was given
				if (new_value <= lowerbound):   # check if the input value is too low
					print('Error: You entered a value that is lower than or equal to ', lowerbound)
					break
			elif not(upperbound is None):   # if no lower bound was given, check if the value is too high
				if (new_value >= upperbound):   # check if the input value is too high
					print('Error: You entered a value that is higher than or equal to ',upperbound)
					break
			print('Is this input okay: ', new_value, ' (Enter y or n)')
			good = input()  # get input from the user
			if good == 'y': # if the input was good
				break
	return new_value

def change_others():
	"""This function checks if the user wants to change any other variables."""
	print('Would you like to change anything other variables?')
	print('Enter y or n')
	while True:
		user = input()  # get input from the user
		if user == 'y': # if the input was good
			return True
		elif user == 'n':   # if the input was bad
			return False
		else:
			print('You entered an incorrect command')


def initialize():
	"""This function defines all of the user specified values.
	
	Parameters
	----------

	Returns
	-------
	num_genes : number of genes, int
		This is the number of genes (or actuators) each person has.
	num_init_parents : number of initial parents, int
		This is the number of parents which starts the program.
	num_init_children : number of initial children, int
		This is the number of children to make from the first parent(s).
	init_voltage : intial voltage, float
		When starting, the parent(s) genes will either all be an initial voltage or loaded from a file.
	filename : name of a .adf file, string
		When starting, the parent(s) genes will either be read from 'filename' or all be the intial voltage.
	num_parents : number of parents, int
		The number of parents to be used after the first iteration.
	num_children : number of children, int
		The number of children to be used after the first iteration.
	mutation_percentage : mutation percentage, float
		This value is proportional to both the number of genes which change and the amount the mutating genes change.
	"""
	num_genes = 37              # number of genes of each person (or mirror actuators)
	num_init_parents = 1        # number of parents to start with
	num_init_children = 10     # number of starting children
	
	"""Note: You can either have an initial voltage or a filename to read from, not both"""
	init_voltage = 70           # initial voltage on mirror actuators
	filename = None             # name of file to read from
	'''Note: Also, it can only read the file if it is in saved_mirrors'''

	num_parents = 10            # number of parents in loop iterations
	num_children = 100          # number of children in loop iterations
	mutation_percentage = 20    # if you want 20% mutation, enter 20

	if not (init_voltage is None) and not (filename is None):
		print('Error: You have both an initial voltage and a filename to read from')

	print("These are the current variables' values: ")
	print('\tNumber of initial parents: ', num_init_parents)
	print('\tNumber of initial children: ', num_init_children, '\n')
	print('\tNumber of parents: ', num_parents)
	print('\tNumber of children: ', num_children, '\n')
	print('\tFilename to read from: ', filename)
	print('\tInitial voltage of starting parent: ', init_voltage, '\n')
	print('\tMutation percentage: ', mutation_percentage, '\n')
	print('Would you like to change any of these values?\nEnter "y" or "n"')
	print('Note: the locations of all important variables are in the README.txt file')
	keyboard_input = input()    # get input from the user
	if keyboard_input == 'y':    # if the key pressed was the enter key
		while True:
			print('To change the number of initial parents, enter "initial parents"')
			print('To change the number of initial children, enter "initial children"')
			print('To change the number of parents, enter "parents"')
			print('To change the number of children, enter "children"')
			print('To change the mutation percentage, enter "mutation percentage"')
			print('To change the filename or initial voltage, enter "init setting"')
			print('To change nothing, enter "none"')
			key_input = input() # get input from the user
			if key_input == 'initial parents':  # determine what the user input
				print('You are changing the number of initial parents')
				num_init_parents = change_value('int', 0, num_init_children+1)  # change the variable's value
				if not change_others(): # determine if the user wants to change any other parameters
					break
			elif key_input == 'initial children':   # determine what the user input
				print('You are changing the number of initial children')
				num_init_children = change_value('int', num_init_parents-1) # change the variable's value
				if not change_others(): # determine if the user wants to change any other parameters
					break
			elif key_input == 'parents':    # determine what the user input
				print('You are changing the number of parents')
				num_parents = change_value('int', 0, num_children+1)    # change the variable's value
				if not change_others(): # determine if the user wants to change any other parameters
					break
			elif key_input == 'children':   # determine what the user input
				print('You are changing the number of children')
				num_children = change_value('int', num_parents-1)   # change the variable's value
				if not change_others(): # determine if the user wants to change any other parameters
					break
			elif key_input == 'mutation percentage':   # determine what the user input
				print('You are changing the mutation percentage')
				mutation_percentage = change_value('int', 0, 50)   # change the variable's value
				if not change_others(): # determine if the user wants to change any other parameters
					break
			elif key_input == 'init setting':   # determine what the user input
				print('You are changing the initialization setting')
				print('Would you like to change the filename or the initial voltage?')
				print('Enter "filename", "initial voltage", or "none"')
				keyboard_press = input()    # get input from the user
				if keyboard_press == 'filename':    # determine what the user input
					print('You are changing the filename')
					print('When entering filenames, enter the name without the .adf extension')
					print('Note: The file must be in the saved_mirrors directory for the program to be able to read it')
					filename = change_value('string')   # change the variable's value
					init_voltage = None # set init_voltage to none because only one initialization setting can be defined at one time
					if not change_others(): # determine if the user wants to change any other parameters
						break
				elif keyboard_press == 'initial voltage': # determine what the user input
					print('You are changing the initial voltage')
					init_voltage = change_value('float', 0, 71) # change the variable's value
					filename = None # set filename to none because only one initialization setting can be defined at one time
					if not change_others(): # determine if the user wants to change any other parameters
						break
				elif keyboard_press == 'none':    # determine what the user input
					if not change_others(): # determine if the user wants to change any other parameters
						break
				else:
					print('You did not enter a correct input')
			elif key_input == 'none':   # determine what the user input
				print('You are not changing anything')
				break
			else:
				print('You did not enter a valid command')
	return num_genes, num_init_parents, num_init_children, init_voltage, filename, num_parents, num_children, mutation_percentage

if __name__ == "__main__":
	print('You meant to run GeneticAlgorithm.py')
