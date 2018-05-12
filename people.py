"""This file contains functions to generate and modify the "people" or actuator voltages 

Classes:
person() -- Create a person.
parent() -- Create a parent.
parent_group() -- A container for multiple parents
child() -- Creates a child from parents
child_group() -- A container for multiple children
"""

WAITING_TIME = 0.01 # seconds between writing to the mirror and starting the figure of merit function

import numpy as np
import math
import time
import mirror_functions as mirror_f
import file_functions as file_f
import figure_of_merit_functions as figure_of_merit_f
import operator

class person(object):
	"""A person is the object written to the mirror actuators. 

	Attributes
	----------
	genes: genes, numpy array
		The array containing this person's genes
	amount_mutated: amount of mutation, float
		The amount this person has mutated
	num_genes: number of genes, int
		The number of genes this person has.
	"""
	def __init__(self, num_genes):
		self.genes = np.empty(num_genes, 'float', 'C')  # a person should have an empty array the size its number of genes
		self.amount_mutated = 0.0       # the person hasn't mutated at all when they are created (this is absolutely unnecessary but is used for backwards compatibility)
		self.num_genes = num_genes      # store the number of genes the person has
		self.figure_of_merit = 0
	  
	def test_person(self, dm_actuators, ps):
		"""write each person to the mirror to measure the figure of merits

		Parameters
		----------
		dm_actuators : object from mirror_functions.py
			This contains the list of neighbors to make sure the genes don't break the mirror.

		Returns
		-------
		figure_of_merit : figure of merit, float
			The figure of merit of this specific person.
		"""
		mirror_f.write_to_mirror(self.genes, dm_actuators)       # write the genes to the mirror
		time.sleep(WAITING_TIME)    # wait for the given amount of time
		self.figure_of_merit = figure_of_merit_f.test_genes(ps) # measure the figure of merit
		return self.figure_of_merit # return the measured figure of merit

 
class parent(person):
	"""Parent is a person with a good figure of merit who makes new children
	
	Attributes
	----------
	All attributes are the same as the person class
	"""
	def __init__(self, num_genes, init_voltage = None, person_genes = None):
		super().__init__(num_genes)     # inherit the attributes from the person class
		if not (init_voltage is None):  # check if an initial voltage was entered
			for i in range(self.num_genes):    # for each gene in the parent
				self.genes[i] = init_voltage    # make each gene's value equal to the initial voltage
		elif not (person_genes is None):    # check if another person's genes were entered
			self.genes = person_genes   # this parent's genes are the other person's genes now
		else:   # if none of the above initialization information was entered
			print('Error: parent not given enough initialization information')


class parent_group(object):
	"""Creates and modifies an array of parents
	
	Attributes
	----------
	num_genes: number of genes, int
		The number of genes each person has.
	num_parents: number of parents, int
		The number of parents in the parents array
	parents: parents, 1D numpy array containing the parent class
		The array containing the parents.
	"""
	def __init__(self, num_parents, num_genes, init_voltage = None, filename = None, all_people = None):   # construct a group of parents based on inputs
		self.num_genes = num_genes          # set the number of parents in the group
		self.num_parents = num_parents      # keep track of the number of genes in each parent
		if not (init_voltage is None) and not (filename is None):   # if both an initial voltage and another person's genes are entered
			print('Error: You tried to create a parent from another person and using an initial voltage')
		if not (all_people is None):    # if indices of the best children and parents were given
			parents = np.empty(0, parent)   # initialize the array of parents
			for i in range(num_parents):
				parents = np.append(parents, parent(num_genes, None, all_people.people[i].genes))
			self.parents = parents  # make the new parents array the class object
		elif not (init_voltage is None):    # if an initial voltage is given
			self.parents = np.full((num_parents),parent(num_genes, init_voltage),parent,'C')    # create an array of parents where every gene is the initial voltage
		elif not (filename is None):    # if a filename to read from was given
			file_genes = file_f.read_adf(filename, num_genes)  # read the genes from a file
			self.parents = np.full((num_parents),parent(num_genes, None, file_genes),parent,'C')    # create an array of parents from the file genes
		else:
			print("Error: parents weren't given enough initialization information")   # the correct output arguments weren't given


class child(person):
	"""Child contains genes (actuator voltages), figure of merit, and mutation amount
	
	Attributes
	----------
	All attributes are the same as the person class
	"""
	def __init__(self, num_genes, parent_group, dm_actuators):
		super().__init__(num_genes)     # inherit the attributes from the person class
		self.inherit_genes(parent_group, dm_actuators)    # inherit genes from the parent(s) who are making children

	def inherit_genes(self, parent_group, dm_actuators):
		"""inherit each gene from a random parent
		
		Parameters
		----------
		parent_group : object from people.py
			This contains the parents used for this generation of children.
		dm_actuators : object from mirror_functions.py
			This contains the list of neighbors to make sure the genes don't break the mirror.
		"""
		while True:     # keep inheriting genes until the child doesn't break the mirror
			for j in range(self.num_genes):     # for each of the child's genes
				random_parent = np.random.randint(0,parent_group.num_parents)   # choose a random parent to inherit from
				self.genes[j] = parent_group.parents[random_parent].genes[j]    # inherit the jth gene from this random parent
			if dm_actuators.fits_mirror(self.genes):     # check if the child breaks the mirror
				break       # if the child doesn't break the mirror, leave the while loop
			'''else:    # if the genes broke the mirror
				print('broken inherited genes')'''

	def mutate_child(self, mut_squared, dm_actuators):
		"""mutates each child according to the mutation percentage given

		Parameters
		----------
		mut_squared : mutation percentage squared, float
			This is a relative measure of how much the genes will be mutated.
		dm_actuators : object from mirror_functions.py
			This contains the list of neighbors to make sure the genes don't break the mirror.
		"""
		while True:     # Make sure the mutated child doesn't break the mirror
			new_genes = self.genes.copy()  # don't mutate the genes directly in case the mutated genes break the mirror
			mutation_vector = np.empty(0,float,'C')     # Initialize vector to store the amounts that genes are mutated by
			mutation_amount = np.random.random_integers(-10000,10000,self.num_genes)/10000    # create num_genes number of random numbers from -1 to 1
			mutation_condition = np.random.random_integers(0,10000,self.num_genes)/10000    # Generate num_genes number of random numbers from 0 and 1
			for j in range(self.num_genes):        # Attempt to mutate every gene
				gauss_num = math.exp(-mutation_amount[j]*mutation_amount[j]/mut_squared)      # Generate random number in a gaussian distribution
				if (mutation_condition[j] < gauss_num):    # this makes smaller mutations more probable
					new_gene = abs(mutation_amount[j]*15 + new_genes[j])     # mutate the gene
					if new_gene < 100:     # new_gene is good if abs(new_gene) < 100
						new_genes[j] = new_gene  # pass on the new gene
						mutation_vector = np.append(mutation_vector, mutation_amount[j])      # remember the amount of mutation for that gene
				# Note: if one of the if statement conditions isn't met, the original gene is kept
			if dm_actuators.fits_mirror(new_genes):    # determine whether this child is safe for the mirror
				if mutation_vector.size:    # if there were any mutations
					self.amount_mutated = np.mean(mutation_vector)     # store the amount this gene was mutated by
				self.genes = new_genes      # the child's new genes are the successfully mutated genes
				break   # get out of the while loop and exit the function


class child_group(object):
	"""creates and modifies an array of children
	
	Attributes
	----------
	num_genes: number of genes, int
		The number of genes each person has.
	num_children: number of children, int
		The number of children in the children array
	children: children, 1D numpy array containing the children class
		The array containing the children.
	"""
	def __init__(self, num_children, parent_group, dm_actuators):
		if parent_group.num_parents > num_children:     # create more children than parents
			print('Error: You tried to create less children than parents')
		self.num_genes = parent_group.num_genes     # the number of genes in each child is the same as the number of genes in each parent
		self.num_children = num_children        # set the number of children
		children = np.empty(0)      # initialize the children matrix
		for i in range(num_children):   # create i children
			children = np.append(children,child(self.num_genes,parent_group, dm_actuators))   # append a new child onto the children array
		# Note: must append the children instead of initializing becuase initializing creates num_children instances of the same child in the vector
		self.children = children    # set this array to be the children attribute

	def mutate(self, mutation_percentage, dm_actuators):
		"""Mutates approximately the mutation percentage proportion of children
		
		Parameters
		----------
		mutation_percentage : mutation percentage, float
			This is a relative measure of how much the genes will be mutated.
		dm_actuators : object from mirror_functions.py
			This contains the list of neighbors to make sure the genes don't break the mirror.
		"""
		mutation = mutation_percentage / 100    # convert the percentage to a decimal
		mutation_squared = mutation*mutation    # square the mutation percentage for later use
		for i in range(self.num_children):   # Mutate each child
			self.children[i].mutate_child(mutation_squared, dm_actuators)        # call the mutate attribute    

class person_group(object):
	"""creates and modifies an array of children
	
	Attributes
	----------
	num_genes: number of genes, int
		The number of genes each person has.
	num_people: number of people, int
		The number of people in the people group
	people: people, list containing the person class
		The array containing the persons.
	"""
	def __init__(self, parent_group, child_group):
		self.num_genes = parent_group.num_genes     # the number of genes in each child is the same as the number of genes in each parent
		self.num_people = parent_group.num_parents + child_group.num_children        # set the number of children
		self.people = list(parent_group.parents) + list(child_group.children)    # initialize the children matrix

	def test_and_sort_people(self, dm_actuators,ps):
		"""Determine the figure of merit for each parent and child.

		Parameters
		----------
		dm_actuators : object from mirror_functions.py
			This contains the list of neighbors to make sure the genes don't break the mirror.
		"""
		for each_person in self.people: # go through every person in all_people
			each_person.test_person(dm_actuators,ps)   # measure the figure of merit of every person
		self.people.sort(key=operator.attrgetter('figure_of_merit'), reverse = True)    # sort the people so that the highest figure of merit is 0th indexed and the lowest figure of merit is last

	def best_figures_of_merit(self, num_parents):
		"""Output the best figures of merit.

		Parameters
		----------
		num_parents : number of parents, int
			The number of parents currently used in the algorithm

		Returns
		-------
		figures_of_merit : figures of merit, numpy 2d array
			The best figures of merit of this batch of people.
		"""
		figures_of_merit = np.zeros((num_parents,1))   # initialize a vector to store the figures of merit
		for i in range(num_parents):    # only go through the first num_parents number of people
			figures_of_merit[i] = self.people[i].figure_of_merit    # record their figure of merit
		return figures_of_merit     # return the vector of top figures of merit

if __name__ == "__main__":
	print('You meant to run GeneticAlgorithm.py')
