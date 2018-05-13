"""This file runs the genetic algorithm

Functions:
genetic_algorithm() -- Start, run, and end the genetic algorithm.
"""
import people
import msvcrt
import mirror_functions as mirror_f
import file_functions as file_f
import numpy as np
import initialization_functions as initialization_f
import time
import plot_functions as plot_f
import warnings
import os
from picoscope import ps2000a
import runps

ADF_FOLDER = 'C:\\Users\lambda3\Desktop\DMfarTable\DM_fartable_picoscope\saved_mirrors\\'     # directory for mirror actuator files
FOM_GRAPH_FOLDER = 'C:\\Users\lambda3\Desktop\DMfarTable\DM_fartable_picoscope\saved_graphs\\'    # directory for figure of merit graphs

# TODO plot and save graph of mirror
# TODO unable to change number of children or parents during the algorithm


	

def save_different_directory(different_directory):
	print("Would you like to save to a different directory? Enter 'y' or 'n'")
	while True:
		different = input()
		if different == 'y':
			print('Enter another directory (make sure to have a \ at the end)')
			different_directory = input()
			if os.path.exists(different_directory):
				break
		elif different == 'n':
			break
		print('You did not enter a y or n, or the directory you entered does not exist')
	return different_directory

def anything_else():    # determine if the user wants to save anything else from the algorithm
	while True:
		print('Would you like to do anything else? (y or n)')  
		doing_more = input()    # see if the user wants to do more with the given data
		if doing_more == 'y' or doing_more == 'n':
			break   # exit the infinite loop
		print('You did not enter a y or n')
	return doing_more

def genetic_algorithm():
	
	ps = runps.run_ps()
	
	warnings.filterwarnings("ignore",".*GUI is implemented.*")  # filter out the plotting warning about deprecation

	"""Start, run, and end the genetic algorithm."""

	print('You are running the genetic algorithm')

	#This function sets all of the values of the number of parents, children, and mutation amount
	num_genes, num_init_parents, num_init_children, init_voltage, filename, num_parents, num_children, mutation_percentage = initialization_f.initialize()
	"""Note: To change the default values, go into inialization_functions.py in the initialize function"""

	print('\nNOTE: LabView must be open in order to run the program\n')
	print('Here are the options you have while the program is running:')
	print('\tPress the enter key (or s) to stop the program')
	print('\tPress "m" if you would like to change the mutation percentage')
	#print('\tPress "c" if you would like to change the number of children')
	#print('\tPrees "p" if you would like to change the number of parents')
	print('Press "r" then enter enter to run the program')
	while True: # run an infinite loop until a key is pressed
		keyboard_input = input()  # if the keyboard was hit
		if keyboard_input == '\r' or keyboard_input == '\n' or keyboard_input == 'r':    # if the key pressed was the enter key
			break   # break out of the infinite loop
	
	print('Starting...')
	start_time = time.time()    # determine the time when the algorithm starts
	dm_actuators = mirror_f.acuator_array() # initialize the class to determine if actuator voltages break the mirror or not
	iteration_number = 0

	parents = people.parent_group(num_init_parents, num_genes, init_voltage, filename)    # create parents from above constraints
	children = people.child_group(num_init_children, parents, dm_actuators)       # create children from the given parents
	children.mutate(mutation_percentage, dm_actuators)    # mutate the children
	
	# all_people = people.person_group(parents, children)     # combine all of the children and parents into a single container

	all_people = people.person_group(parents, children, children, children, children, children)
	
	all_people.test_and_sort_people(dm_actuators,ps)   # measure the figures of merits and sort the people so the highest figure of merit is 0th indexed
	
	best_person = all_people.people[0]  # the best person is the 0th indexed person in all_people
	print('best_person\n', best_person.figure_of_merit) # show the best person's genes and figure of merit
	
	past_figures_of_merit = all_people.best_figures_of_merit(num_parents)

	print('Total running time: ', time.time() - start_time, ' seconds')    # print out the number of seconds since the algorithm started

	while True:     # run an infinite loop until user says to stop
		if msvcrt.kbhit():  # if the keyboard was hit
			keyboard_input = msvcrt.getwche()   # determine what key was pressed
			if keyboard_input == 's':  # if the enter key was pressed ######fix me
			# if keyboard_input == '\r' or keyboard_input == 's':  # if the enter key was pressed ######fix me

				break   # get out of the while loop
			elif keyboard_input == 'm':   # if the m key was pressed######fix me
				print('\nThis is the current mutation percentage: ', mutation_percentage)
				mutation_percentage = initialization_f.change_value('float', 0, 100)    # change the mutation percentage to what the user wants
			"""
			elif keyboard_input == 'c':   # if the c key was pressed
				print('\nThis is the current number of children: ', num_children)   
				mutation_percentage = initialization_f.change_value('int', num_parents-1)   # change the number of children to what the user wants
			elif keyboard_input == 'p':   # if the p key was pressed
				print('\nThis is the current number of parents: ', num_parents)
				mutation_percentage = initialization_f.change_value('float', 0, num_children+1) # change the number of parents to what the user wants
			"""
		
		parents = people.parent_group(num_parents,num_genes, None, None, all_people)   # create parents from the best performing children
		children = people.child_group(num_children, parents, dm_actuators)       # create children from the just created parents
		children.mutate(mutation_percentage, dm_actuators)    # mutate the children

		# all_people = people.person_group(parents, children)     # combine all of the children and parents into a single container

		all_people = people.person_group(parents, children, children, children, children, children)

		all_people.test_and_sort_people(dm_actuators,ps)   # measure the figures of merits and sort the people so the highest figure of merit is 0th indexed

		
		new_best_person = all_people.people[0]  # the best person is the 0th indexed person in all_people
		if new_best_person.figure_of_merit > best_person.figure_of_merit:     # determine if the best person's figure of merit in this run is better than the current best person's figure of merit
			best_person = new_best_person   # if the new best person is better, they are the overall best person ever
		print('best_person\n', best_person.figure_of_merit) # print out the best person ever made

		figures_of_merit = np.concatenate((past_figures_of_merit, all_people.best_figures_of_merit(num_parents)), axis=1)   # concatenate the previous figure of merit matrix with the current figures of merit
		iteration_number, past_figures_of_merit = plot_f.plot_performance(iteration_number, figures_of_merit)   # plot the progressions of figures of merit
		
		print('Total running time: ', time.time() - start_time, ' seconds')    # print out the number of seconds since the algorithm started
	

	runps.close_ps(ps)
	# ps.stop()
	# ps.close()

	print('What would you like to do with the best person?')    # once the loop has finished, the user decides what to do with the genes made
	while True:     # create an infinite loop
		print('\tFor writing the actuator voltages to a file, input "write"')
		print('\tFor saving graph data, input "graph"')
		print('\tFor doing nothing, input "none"')
		saving_option = input() # get user input for what they want to do
		if saving_option == 'write':    # if they want to write the genes to a file
			directory = ADF_FOLDER
			print("\tThe default directory is " + ADF_FOLDER)
			directory = save_different_directory(directory)
			print("Enter the file name you want to be saved (for test.adf, input test):\nNote: this will overwrite a file with the same name")
			filename = input()  # get user input from for what filename they want
			file_f.write_adf(best_person, directory + filename)    # write the genes to the input file
			if anything_else() == 'n':   # if they don't want to do anything else
				break   # break out of the while loop
		elif saving_option == 'graph':  # if the user wants to save the graph
			directory = FOM_GRAPH_FOLDER
			print("\tThe default directory is " + FOM_GRAPH_FOLDER)
			directory = save_different_directory(directory)
			print("Enter the file name you want to be saved (for test.csv, input test):\nNote: this will overwrite a file with the same name")
			filename = input()  # get user input from for what filename they want
			file_f.write_figures_of_merit(figures_of_merit, directory + filename)   # write the figures of merit to a comma separated value file
			if anything_else() == 'n':   # if they don't want to do anything else
				break   # break out of the while loop
		elif saving_option == 'none':   # if the user doesn't want to do anything with the data
			break   # break out of the while loop
		else:   # if they didn't enter one of the options
			print("You didn't enter a correct command")

# If this function is being run explicitly, I want the genetic algorithm funciton to be run.
# Otherwise, do not run the main function and so it only has the import functionality
if __name__ == "__main__":

	genetic_algorithm()
	
	#print(help(mirror_f))
	#dm_actuators = mirror_f.acuator_array() # initialize the class to determine if actuator voltages break the mirror or not
	#genes = file_f.read_adf('test.adf',37)
	#mirror_f.write_to_mirror(genes, dm_actuators)
