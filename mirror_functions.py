"""This module provides objects and functions to write genes to the mirror and to check the validity of the genes.

Variables:
PCI_BOARDS -- The NI addresses for the PCI boards
ACTUATOR_ADDRESSES -- The addresses for the various actuators within the PCI board

Classes:
actuator_array() -- This maps all of the neighboring actuator pairs (including diagonal actuators)
and makes sure the voltage differences aren't too high

Functions:
array_conversion() -- maps the 37 genes to the correct actuators
send_to_board() -- sends two arrays of voltages to the two PCI boards
write_to_mirror() -- organizes genes and makes sure they will not break the mirror
"""

#import pyvisa   # Use this when using the pyvisa code in send_to_board
import win32com.client  # Use this when using the LabVIEW VI in send_to_board # Python ActiveX Client
import numpy as np
import msvcrt
from ctypes import *

# from people import parent

# import mirror_functions as mirror_f
# PCI_BOARDS = #[['ASRL4::INSTR'], ['ASRL4::INSTR']]#[['COM4'],['COM4']]#   # These are the addresses given in NI-MAX or on Device manager
# the top row values are the addresses of actuators 0-18 and the bottom values are the addresses of the actuators 19-36
ACTUATOR_ADDRESSES = np.array([0x34, 0x54, 0x28, 0x38, 0x08, 0x04, 0x24, 0x50, 0x58, 0x2C, 0x30, 0x1C, 0x10, 0x14, 0x0C, 0x00, 0x3C, 0x20, 0x5C, 0x24, 
							  0x5C, 0x58, 0x54, 0x20, 0x10, 0x08, 0x1C, 0x14, 0x0C, 0x04, 0x00, 0x3C, 0x38, 0x34, 0x30, 0x2C, 0x28])

MAX_DIFF = 30 # maximum difference in voltage between neighboring actuators

MAX_VOLTAGE = 100 # maximumm voltage an acuator can have
coeff = 13.72
class acuator_array(object):
	"""actuator_array is an object that represents deformable mirror actuators and checks
	whether the actuator voltage values break the mirror or not

	Attributes
	----------
	dm_actuator_neighbors: deformable mirror actuator neighbors, numpy array
		The array contains all of the pairs of actuators which neighbor each other (including diagonal)
	"""
	def __init__(self):
		# create an array that represents the deformable mirror indices

		# array that represents the indices of acuators on the deformable mirror
		# Note: if you change to a different mirror, you will have to change this and the
		#   first if statement to find the correct neighbors
		dm_array = [[-1,-1,28,27,26,-1,-1],
					[-1,29,14,13,12,25,-1],
					[30,15, 4, 3, 2,11,24],
					[31,16, 5, 0, 1,10,23],
					[32,17, 6, 7, 8, 9,22],
					[-1,33,18,19,20,21,-1],
					[-1,-1,34,35,36,-1,-1]]
		
		dm_actuator_neighbors = []      # initialize the empty list of neighboring actuators

		# The nested for loops go through the entire array and determine which actuators 
		# are neighbors. It includes actuators which are diagonal to each other.
		# It starts at the top left and makes sure the actuator distance from 
		# the center is within the area of the active actuators. It then pairs the 
		# given actuator with the actuators to the east, southeast, south, and 
		# southwest of the starting actuator. It iterates through the entire array
		# logging the neighbor pairs of each actuator. 
		for row_i in range(len(dm_array)):
			for col_j in range(len(dm_array[row_i])):   
				if abs(row_i-3) + abs(col_j-3) < 5:     #make sure the index at (i,j) is close enough to the center to represent a real actuator
					start_actuator = dm_array[row_i][col_j]     # this will be the actuator examined in the for loop
					# if j is not in the last column and the east neighbor isn't -1, add these neighbors to the list 
					if col_j !=len(dm_array[row_i])-1:
						neighbor = dm_array[row_i][col_j+1]
						if neighbor != -1:
							dm_actuator_neighbors.append([start_actuator,neighbor])
					# if row_i is not the last row, the south/southeast/southwest neighbors may be valid
					if row_i!=len(dm_array)-1:
						# determine if the southern neighbor is valid
						neighbor = dm_array[row_i+1][col_j]
						if neighbor != -1:  
							dm_actuator_neighbors.append([start_actuator,neighbor])
						# if col_j is not the last column, determine if the southeastern neighbor is valid
						if col_j != len(dm_array[row_i])-1:
							neighbor = dm_array[row_i+1][col_j+1]
							if neighbor != -1:
								dm_actuator_neighbors.append([start_actuator,neighbor])
						# if col_j is not the first column, determine if the southwestern neighbor is valid
						if col_j!=0:
							neighbor = dm_array[row_i+1][col_j-1]
							if neighbor != -1:
								dm_actuator_neighbors.append([start_actuator,neighbor])
		
		# make the neighbor list an accessible attribute of the object actuator_array
		self.dm_actuator_neighbors = dm_actuator_neighbors  # make the neighbors list an attribute
		""" This is brute force specific to the current 37 actuator mirror
		# array which contains all actuator neighbor pairs
		dm_neighbors = [[0,1],[0,2],[0,3],[0,4],[0,5],[0,6],[0,7],[0,8],[1,2],[1,3],[1,7],[1,8],[1,9],[1,10],
						[1,11],[2,3],[2,12],[2,13],[2,10],[2,11],[2,25],[3,4],[3,12],[3,13],[3,5],[3,14],
						[4,5],[4,13],[4,14],[4,15],[4,16],[4,29],[5,6],[5,7],[5,15],[5,16],[5,17],[6,7],[6,16],
						[6,17],[6,32],[6,19],[6,33],[7,8],[7,32],[7,20],[7,19],[7,18],[8,9],[8,10],[8,19],
						[8,20],[8,21],[9,10],[9,20],[9,21],[9,22],[9,23],[10,11],[10,22],[10,23],[10,24],[11,12],
						[11,23],[11,24],[11,25],[12,13],[12,25],[12,26],[12,27],[13,14],[13,26],[13,27],[13,28],
						[14,15],[14,27],[14,28],[14,29],[15,16],[15,29],[15,30],[15,31],[16,17],[16,30],[16,31],
						[16,32],[17,18],[17,31],[17,32],[17,33],[18,19],[18,33],[18,34],[18,35],[19,20],[19,34],
						[19,35],[19,36],[20,21],[20,35],[20,36],[21,22],[21,36],[22,23],[23,24],[24,25],[25,26],
						[27,28],[28,29],[29,30],[30,31],[31,32],[32,33],[33,34],[34,35],[35,36]]
		"""

	def fits_mirror(self,genes):
		"""Determine if a person breaks the mirror

		Parameters
		----------
		genes: genes, 1D numpy array
			the genes or actuator voltages to be tested

		Returns
		-------
		valid_genes : valid genes, bool
			True if the genes do not break the mirror
		"""
		genes = genes#*coeff   # This is the DM constant used in the original code
		valid_genes = True    # the child is good until proven bad
		for i in range(len(self.dm_actuator_neighbors)):      # Test every actuator value with its neighbors' values
			valid_genes = valid_genes and (abs(genes[self.dm_actuator_neighbors[i][0]]-genes[self.dm_actuator_neighbors[i][1]]) <= MAX_DIFF)  # test voltage difference between neighboring actuators is less than 30
		return valid_genes
	

# def array_conversion(genes):
#     """Maps genes to a different order so that indices in the genes array corresponds to the 
#     outward circular indexing convention given by this diagram.
#     [-1,-1,28,27,26,-1,-1]
#     [-1,29,14,13,12,25,-1]
#     [30,15, 4, 3, 2,11,24]
#     [31,16, 5, 0, 1,10,23]
#     [32,17, 6, 7, 8, 9,22]
#     [-1,33,18,19,20,21,-1]
#     [-1,-1,34,35,36,-1,-1]

#     Parameters
#     ----------
#     genes: genes, 1D numpy array
#         the genes or actuator voltages to be tested

#     Returns
#     -------
#     mapped_genes : mapped genes, 1D numpy array
#         The genes to be tested after being mapped so the index corresponds to the correct actuator
#     """
#     # Change the order of the genes so each index corresponds with the correct index on the deformable mirror
#     # mapped_genes = [genes[17], genes[31], genes[32], genes[8], genes[18], genes[9], genes[1], genes[16], genes[0], genes[23],
#     #                 genes[6], genes[21], genes[20], genes[19], genes[33], genes[22], genes[7], genes[10], genes[5], genes[29],
#     #                 genes[27], genes[26], genes[28], genes[14], genes[35], genes[24], genes[36], genes[34], genes[11], genes[3],
#     #                 genes[2], genes[15], genes[4], genes[25], genes[30], genes[13], genes[12]]

#     mapped_genes = [genes[0], genes[1], genes[2], genes[3], genes[4], genes[5], genes[6], genes[7], genes[8], genes[9],
#                     genes[10], genes[11], genes[12], genes[13], genes[14], genes[15], genes[16], genes[17], genes[18], genes[19],
#                     genes[20], genes[21], genes[22], genes[23], genes[24], genes[25], genes[26], genes[27], genes[28], genes[29],
#                     genes[30], genes[31], genes[32], genes[33], genes[34], genes[35], genes[36]]
#     return np.array(mapped_genes)

def send_to_board(voltages0):#, voltages1):
	"""Write the voltage values to the PCI boards

	Parameters
	----------
	voltages0 : voltages, 1D numpy array
		The array of voltages being sent to board 0
	voltages1 : voltages, 1D numpy array
		The array of voltages being sent to board 1

	"""
	#There are 3 different sets of code to write to the board: calling the LabVIEW VIs themselves, calling functions in a LabVIEW dll, and using pyVISA 
	# This is the code for running the LabView VI which communicates with the deformable mirror 
	
	LabVIEW = win32com.client.Dispatch("Labview.Application")   # Start running Labview
	pci0VI = LabVIEW.getvireference('C:\\Users\lambda3\Desktop\DMfarTable\DM_fartable_picoscope\Volt_to_mirror_2.vi')    # path to the LabVIEW VI for the first board
	# pci0VI = LabVIEW.getvireference('C:\\Users\lambdacubed\Desktop\Jinpu\2017\DMfarTable\DM 64bits with photodiode(0_1)\Send Volt to board x64.vi')    # path to the LabVIEW VI for the first board

	pci0VI._FlagAsMethod("Call")    # Flag "Call" as the method to run the VI in this path
	# pci0VI.setcontrolvalue('error in (no error)', 0)   # set error in
	# pci0VI.setcontrolvalue('addresses', ACTUATOR_ADDRESSES)   # set addresses
	pci0VI.setcontrolvalue('Actuator 1 to 37', voltages0.tolist())   # set values to write
	pci0VI.Call()   # Run the VI
	result = pci0VI.getcontrolvalue('ERROR STATUS')    # retrieve error out
	# print(result)
	# if (result[1] != 0):   # check whether there was an error
	#     print('There was an error writing to mirror 2')
	#     print('Error: ', result)
	#     print('Press anything and enter to exit...')
	#     input()
	#     exit()

	# pci1VI = LabVIEW.getvireference('C:\\Users\lambdacubed\Desktop\Mark\genetic_algorithm_python\Volt_to_board_1.vi')    # path to the LabVIEW VI for the second board
	# pci0VI = LabVIEW.getvireference('C:\\Users\lambdacubed\Desktop\Jinpu\2017\DMfarTable\DM 64bits with photodiode(0_1)\Send Volt to board x64.vi')    # path to the LabVIEW VI for the first board

	# pci1VI._FlagAsMethod("Call")    # Flag "Call" as the method to run the VI in this path
	# pci1VI.setcontrolvalue('error in (no error)', 0)   # set error in
	# pci1VI.setcontrolvalue('addresses', ACTUATOR_ADDRESSES[1])   # set addresses
	# pci1VI.setcontrolvalue('values to write', voltages1.tolist())   # set values to write
	# pci1VI.Call()   # Run the VI
	# result = pci1VI.getcontrolvalue('error out')    # retrieve error out
	# if (result[1] != 0):   # check whether there was an error
	#     print('There was an error writing to board 1 at PXI4::4::INSTR')
	#     print('Error: ', result)
	#     print('Press anything and enter to exit...')
	#     input()
	#     exit()

	return
	"""
	# void  ?test_dll@@YAXPAHQAPAD00PAD@Z(int32_t *argc, int32_t *argv, int32_t *channel, int32_t *voltage, CStr status);
	# This utilizes the dll created from custom made VIs which communicate directly to each pci card
	
	# c = 'spam'.encode('utf-8')
	# a = c_char_p(c)
	# print(a._objects)
	# print(type(a._objects))

	volt_to_board = cdll.LoadLibrary('test_dll.dll')
	argc_var = 0
	argv_var = 0
	channel_var = 0
	voltage_var = voltages0.tolist()
	status_var = c_char_p('Test'.encode('utf-8'))
	volt_to_board.YAXPAHQAPAD00PAD(argc_var, argv_var, channel_var, voltage_var, status_var)
	print(error_out)
	return
	"""

	# This is the code for using pyVISA, but it doesn't support PXI devices at the moment (5/18/2017)
	"""
	rm = pyvisa.ResourceManager()   # instantiate an object to manage all devices connected to the computer
	#print(rm.list_resources())  # show which things are connected to the computer
	deformable_mirror = rm.open_resource(PCI_BOARDS[board_num])
	lib = rm.visalib    # access the library for low-level "hardware" functions
	session = lib.open_default_resource_manager() # open hardware level manager of devices attached to the computer
	dm_session = lib.open(session[0], PCI_BOARDS[board_num]) # open access to the correct pci card
	lib.map_address(dm_session[0], pyvisa.constants.VI_PXI_BAR0_SPACE, 0, 0xFF) # connect the pci memory addresses to the program's memory addresses
	print(type(voltages[0]), 'voltages size')
	for i in range(voltages.size):   # for each of the 37 voltages
		lib.poke_8(dm_session[0], ACTUATOR_ADDRESSES[board_num][i], int(voltages[i]))   # write the voltage into the memory accessed by the pci card
	lib.close(session[0])  # close the pci card
	return
	"""

def write_to_mirror(genes, dm_actuators):
	"""Checks whether the voltage values satisfy the requirements then sends them to the deformable mirror

	Parameters
	----------
	genes: genes, 1D numpy array
		the genes or actuator voltages to be tested
	dm_actuators : object from mirror_functions.py
		This contains the list of neighbors to make sure the genes don't break the mirror.
	"""
	within_range = True # the genes are in the accepted voltage range unless proven to be out of range
	for i in range(genes.size):  # for each gene
		within_range = True and (genes[i] >= 0) and (genes[i] <= MAX_VOLTAGE) # check that the voltages are between 0 and 250
	if within_range:    # if all of the genes are within the correct range
		if  dm_actuators.fits_mirror(genes): # if the genes don't break the mirror
			genes = genes * coeff  # multiply each voltage by 2.65 because this is a constant for Xinetics mirrors
			# print(genes)
			# voltage_array = np.array(genes)# array_conversion(genes) # change the mapping of the indices
			send_to_board(genes)#[:19], genes[19:])
		else:
			print("Error: Tried writing the genes to the mirror, but they would've broken it")
	else:
		print('Error: Genes not in range (within the write_to_mirror function)')
	return

if __name__ == "__main__":
	# while True:
	#     if msvcrt.kbhit():  # if the keyboard was hit
	#         keyboard_input = msvcrt.getwche()   # determine what key was pressed
	#         if keyboard_input == '\r' or keyboard_input == 's':  # if the enter key was pressed
	#             break   # get out of the while loop
		# print('Nothing')
	print('You meant to run GeneticAlgorithm.py')
	# dm_actuators = acuator_array()
	# genes = np.array([10]*37)
	# # print('something')
	# write_to_mirror(genes,dm_actuators)
	# print('The voltage is: {0}'.format(10))

	  


# def new_function():
#     LabVIEW = win32com.client.Dispatch("Labview.Application")   # Start running Labview
#     pci0VI = LabVIEW.getvireference('C:\\Users\lambdacubed\Desktop\Mark\genetic_algorithm_python\Volt_to_mirror_2.vi')    # path to the LabVIEW VI for the first board
#     # pci0VI = LabVIEW.getvireference('C:\\Users\lambdacubed\Desktop\Jinpu\2017\DMfarTable\DM 64bits with photodiode(0_1)\Send Volt to board x64.vi')    # path to the LabVIEW VI for the first board

#     pci0VI._FlagAsMethod("Call")    # Flag "Call" as the method to run the VI in this path
#     # pci0VI.setcontrolvalue('error in (no error)', 0)   # set error in
#     # pci0VI.setcontrolvalue('addresses', ACTUATOR_ADDRESSES)   # set addresses
#     pci0VI.getcontrolvalue('FWHM (fs)', new_var)   # set values to write
#     pci0VI.Call()   # Run the VI
#     result = pci0VI.getcontrolvalue('ERROR STATUS')    # retrieve error out
#     print(result)