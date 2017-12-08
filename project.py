import module
import sys
import re
import status as global_var
import test
# global state 



# global variable

global DataManagerList # list of sites 10 for this situation
global VariableSiteList # 20 list store site for each variable
global TransactionList # all transaction




if __name__ == "__main__":
	print("Database initial information: 20 variables in 10 sites:")
	print()
	# generate variable list
	for i in range(20):
		if (i + 1) % 2 == 0:
			global_var.VariableSiteList[i+1] = [1,2,3,4,5,6,7,8,9,10]
		else:
			global_var.VariableSiteList[i+1] = [1+(i+1) % 10]
	# for v in global_var.VariableSiteList.keys():
	# 	print("variable {0} in sites {1}".format(v,global_var.VariableSiteList[v]))

	# test.printFunction()
	# generate data manager
	for i in range(10):
		print("site {}".format(i+1))
		DM = module.DataManager(i+1)
		global_var.DataManagerList[i+1] = DM
		print()
	
	TM = module.TransactionMachine()
	# Test 1
	'''TM.begin(1)
	TM.begin(2)
	print()
	TM.write(1,1,101)
	print()
	TM.write(2,2,202)
	print()
	TM.write(1,2,102)
	print()
	TM.write(2,1,201)
	print()
	TM.endCommand(1)
	print()
	TM.dumpCommand()'''

	# Test 2
	'''TM.begin(1)
	TM.beginRO(2)
	print()

	TM.write(1,1,101)
	print()
	TM.readCommand(2,2)
	print()
	TM.write(1,2,102)
	print()
	TM.readCommand(2,1)
	print()

	TM.endCommand(1)
	TM.endCommand(2)
	print()
	TM.dumpCommand()'''

	# Test 3
	'''TM.begin(1)
	TM.begin(2)
	print()
	TM.readCommand(1,3)
	print()
	TM.fail(2)
	print()
	TM.write(2,8,88)
	print()
	TM.readCommand(2,3)
	print()
	TM.write(1,5,91)
	print()
	TM.endCommand(2)
	print()
	TM.recover(2)
	print()
	TM.endCommand(1)'''

	# Test 3.5
	'''TM.begin(1)
	TM.begin(2)
	print()
	TM.readCommand(1,3)
	print()
	TM.write(2,8,88)
	print()
	TM.fail(2)
	print()
	TM.readCommand(2,3)
	print()
	TM.write(1,4,91)
	print()
	TM.recover(2)
	print()
	TM.endCommand(2)
	print()
	TM.endCommand(1)'''

	# TM.deadLock_test()

	# Test 4 
	'''TM.begin(1)
	TM.begin(2)
	print()
	TM.readCommand(1,1)
	print()
	TM.fail(2)
	print()
	TM.write(2,8,88)
	print()
	TM.readCommand(2,3)
	print()
	TM.readCommand(1,5)
	print()
	TM.endCommand(2)
	print()
	TM.recover(2)
	print()
	TM.endCommand(1)'''

	# Test 5
	'''TM.begin(1)
	TM.begin(2)
	print()
	TM.write(1,6,66)
	print()
	TM.fail(2)
	print()
	TM.write(2,8,88)
	print()
	TM.readCommand(2,3)
	print()
	TM.readCommand(1,5)
	print()
	TM.endCommand(2)
	print()
	TM.recover(2)
	print()
	TM.endCommand(1)'''

	# Test 6
	'''TM.begin(1)
	TM.begin(2)
	print()
	TM.fail(3)
	TM.fail(4)
	print()
	TM.readCommand(1,1)
	print()
	TM.write(2,8,88)
	print()
	TM.endCommand(1)
	print()
	TM.recover(4)
	TM.recover(3)
	print()
	TM.readCommand(2,3)
	print()
	TM.endCommand(2)'''

	# Test 7
	'''TM.begin(1)
	TM.beginRO(2)
	print()
	TM.readCommand(2,1)
	print()
	TM.readCommand(2,2)
	print()
	TM.write(1,3,33)
	print()
	TM.endCommand(1)
	print()
	TM.readCommand(2,3)
	print()
	TM.endCommand(2)'''

	# Test 8
	'''TM.begin(1)
	TM.beginRO(2)
	print()
	TM.readCommand(2,1)
	print()
	TM.readCommand(2,2)
	print()
	TM.write(1,3,33)
	print()
	TM.endCommand(1)
	print()
	TM.beginRO(3)
	print()
	TM.readCommand(3,3)
	print()
	TM.readCommand(2,3)
	print()
	TM.endCommand(2)
	print()
	TM.endCommand(3)'''

	# Test 9
	'''TM.begin(3)
	TM.begin(1)
	TM.begin(2)
	print()
	TM.write(3,2,22)
	print()
	TM.write(2,4,44)
	print()
	TM.readCommand(3,4)
	print()
	TM.endCommand(2)
	print()
	TM.endCommand(3)
	print()
	TM.readCommand(1,2)
	print()
	TM.endCommand(1)'''

	# Test 10
	'''TM.begin(1)
	TM.begin(2)
	TM.begin(3)
	print()
	TM.write(3,2,22)
	print()
	TM.write(2,4,44)
	print()
	TM.readCommand(3,4)
	print()
	TM.endCommand(2)
	print()
	TM.endCommand(3)
	print()
	TM.readCommand(1,2)
	print()
	TM.endCommand(1)'''

	# Test 11
	'''TM.begin(1)
	TM.begin(2)
	print()
	TM.readCommand(1,2)
	print()
	TM.readCommand(2,2)
	print()
	TM.write(2,2,10)
	print()
	TM.endCommand(1)
	print()
	TM.endCommand(2)'''

	# Test 12
	'''TM.begin(1)
	TM.begin(2)
	print()
	TM.readCommand(1,2)
	print()
	TM.readCommand(2,2)
	print()
	TM.endCommand(1)
	print()
	TM.write(2,2,10)
	print()
	TM.endCommand(2)'''

	# Test 13
	'''TM.begin(1)
	TM.begin(2)
	TM.begin(3)
	print()
	TM.write(3,2,10)
	print()
	TM.write(2,2,10)
	print()
	TM.write(1,2,10)
	print()
	TM.endCommand(3)
	print()
	TM.endCommand(2)
	print()
	TM.endCommand(1)'''

	# Test 14
	'''TM.begin(1)
	TM.begin(2)
	TM.begin(3)
	print()
	TM.write(3,2,10)
	print()
	TM.write(1,2,10)
	print()
	TM.write(2,2,10)
	print()
	TM.endCommand(3)
	print()
	TM.endCommand(1)
	print()
	TM.endCommand(2)'''

	# Test 15
	'''TM.begin(5)
	TM.begin(4)
	TM.begin(3)
	TM.begin(2)
	TM.begin(1)
	print()
	TM.write(1,4,5)
	print()
	TM.fail(2)
	print()
	TM.write(2,4,44)
	print()
	TM.recover(2)
	print()
	TM.write(3,4,55)
	print()
	TM.write(4,4,66)
	print()
	TM.write(5,4,77)
	print()
	TM.endCommand(1)
	print()
	TM.endCommand(2)
	print()
	TM.endCommand(3)
	print()
	TM.endCommand(4)
	print()
	TM.endCommand(5)'''

	# Test 16
	'''TM.begin(3)
	TM.begin(1)
	TM.begin(2)
	print()
	TM.write(3,2,22)
	print()
	TM.write(2,4,44)
	print()
	TM.readCommand(3,4)
	print()
	TM.endCommand(2)
	print()
	TM.endCommand(3)
	print()
	TM.readCommand(1,2)
	print()
	TM.endCommand(1)'''

	# Test 17
	'''TM.begin(3)
	TM.begin(1)
	TM.begin(2)
	print()
	TM.write(3,2,22)
	print()
	TM.write(2,3,44)
	print()
	TM.readCommand(3,3)
	print()
	TM.endCommand(2)
	print()
	TM.fail(4)
	print()
	TM.endCommand(3)
	print()
	TM.readCommand(1,2)
	print()
	TM.endCommand(1)'''

	# Test 18
	'''TM.begin(1)
	TM.begin(2)
	TM.begin(3)
	TM.begin(4)
	TM.begin(5)
	print()
	TM.readCommand(3,3)
	print()
	TM.readCommand(4,4)
	print()
	TM.readCommand(5,5)
	print()
	TM.readCommand(1,1)
	print()
	TM.readCommand(2,2)
	print()
	TM.write(1,2,10)
	print()
	TM.write(2,3,20)
	print()
	TM.write(3,4,30)
	print()
	TM.write(4,5,40)
	print()
	TM.write(5,1,50)
	print()
	TM.endCommand(4)
	print()
	TM.endCommand(3)
	print()
	TM.endCommand(2)
	print()
	TM.endCommand(1)'''

	# Test 19
	'''TM.begin(1)
	TM.begin(2)
	TM.begin(3)
	TM.begin(4)
	TM.begin(5)
	print()
	TM.readCommand(3,3)
	print()
	TM.fail(4)
	print()
	TM.recover(4)
	print()
	TM.readCommand(4,4)
	print()
	TM.readCommand(5,5)
	print()
	TM.readCommand(1,6)
	print()
	TM.readCommand(2,2)
	print()
	TM.write(1,2,10)
	print()
	TM.write(2,3,20)
	print()
	TM.write(3,4,30)
	print()
	TM.write(5,1,50)
	print()
	TM.endCommand(5)
	print()
	TM.write(4,5,40)
	print()
	TM.endCommand(4)
	print()
	TM.endCommand(3)
	print()
	TM.endCommand(2)
	print()
	TM.endCommand(1)'''

	# Test 20 more than one cycle

	'''TM.begin(2)
	TM.begin(4)
	TM.begin(1)
	TM.begin(3)
	print()
	TM.readCommand(2,2)
	print()
	TM.readCommand(2,5)
	print()
	TM.readCommand(1,1)
	print()
	TM.readCommand(3,3)
	print()
	TM.readCommand(4,4)
	print()
	TM.write(1,2,21)
	print()
	TM.write(3,5,53)
	print()
	TM.write(4,1,14)
	print()
	TM.write(4,3,34)
	print()
	TM.write(2,4,42)
	print()
	TM.endCommand(4)
	print()
	TM.endCommand(2)
	print()
	TM.dumpCommand()'''

	# Test 21 nothing special
	'''TM.begin(1)
	TM.begin(2)
	print()
	TM.readCommand(1,1)
	print()
	TM.readCommand(2,1)
	print()
	TM.write(2,1,22)
	print()
	TM.endCommand(1)
	print()
	TM.endCommand(2)
	print()
	TM.dumpCommand()'''

	# Test 22 wait until recover

	'''TM.beginRO(1)
	TM.begin(2)
	TM.begin(3)
	print()
	TM.write(3,3,33)
	print()
	TM.endCommand(3)
	TM.fail(4)
	TM.readCommand(1,3)
	TM.readCommand(2,3)
	TM.recover(4)
	TM.endCommand(1)
	TM.endCommand(2)'''

	# Test 23 find youngest transaction in cycle
	'''TM.begin(1)
	TM.begin(2)
	TM.begin(3)
	TM.begin(4)
	print()
	TM.readCommand(1,1)
	print()
	TM.readCommand(2,2)
	print()
	TM.readCommand(3,3)
	print()
	TM.readCommand(3,5)
	print()
	TM.write(4,3,40)
	print()
	TM.write(3,1,30)
	print()
	TM.write(1,2,10)
	print()
	TM.write(2,5,20)
	print()
	TM.endCommand(4)
	print()
	TM.endCommand(2)
	print()
	TM.endCommand(1)'''

	# Test 24 readOnly transaction return immediately after site recover but normal transaction need to wait until next write commit for replicate variable
	'''TM.fail(1)
	TM.fail(2)
	TM.fail(3)
	TM.fail(4)
	TM.fail(5)
	TM.fail(6)
	TM.fail(7)
	TM.fail(8)
	TM.fail(9)
	TM.fail(10)
	print()
	TM.begin(1)
	TM.begin(2)
	TM.beginRO(3)
	TM.begin(4)
	print()
	TM.readCommand(1,3)
	print()
	TM.readCommand(2,4)
	print()
	TM.readCommand(3,4)
	print()
	TM.recover(4)
	print()
	TM.write(4,4,44)
	print()
	TM.endCommand(1)
	print()
	TM.endCommand(4)
	print()
	TM.endCommand(2)
	print()
	TM.endCommand(3)'''

	# Test sequential
	'''TM.begin(1)
	print()
	TM.fail(2)
	print()
	TM.fail(4)
	print()
	TM.readCommand(1,1)
	print()
	TM.readCommand(1,3)
	print()
	TM.endCommand(1)
	print()
	TM.recover(2)
	print()
	TM.recover(4)'''

	# Test after recover
	'''TM.begin(1)
	print()
	TM.readCommand(1,2)
	print()
	TM.fail(2)
	print()
	TM.recover(2)
	print()
	TM.endCommand(1)'''
	check = True
	if len(sys.argv) < 2:
		print('Error: no input file found.')
		check = False
	if len(sys.argv) > 2:
		print('Error: more than one input file found.')
		check = False
	if check:
		inputFile = sys.argv[1]
		with open(inputFile,'r') as inFile:
			for line in inFile:
				# print(line)
				command = re.search('(([a-zA-Z]+))',line).group(0) if re.search('([a-zA-Z]+)',line) else 'NONE'
				transactionNum = re.search('T([0-9]+)',line).group(1) if re.search('T([0-9]+)',line) else 'NONE'
				variableNum = re.search('[x]([0-9]+)',line).group(1) if re.search('[x]([0-9]+)',line) else 'NONE'

				siteNumFirst = re.search('[(]([0-9]+)[)]',line).group(0) if re.search('[(]([0-9]+)[)]',line) else 'NONE'
				siteNum = re.search('([0-9]+)',siteNumFirst).group(0) if re.search('([0-9]+)',siteNumFirst) else 'NONE'

				valueFirst = re.search('[,]([0-9]+)[)]',line).group(0) if re.search('[,]([0-9]+)[)]',line) else 'NONE'
				value = re.search('([0-9]+)',valueFirst).group(0) if re.search('([0-9]+)',valueFirst) else 'NONE'
				# print(valueFirst,value)
				# print("Command {0} for tansaction {1} or site {2} for variable {3} with value {4}".format(command,transactionNum,siteNum,variableNum,value))


				if 'begin' in command:
					if transactionNum != 'NONE':
						tNum = int(transactionNum)
						if tNum not in global_var.TransactionList.keys():
							if 'beginRO' in command:
								TM.beginRO(tNum)
							else:
								TM.begin(tNum)
						else:
							print("Error: Transaction {} already exist.".format(tNum))
					else:
						print("Error: Please enter transactionNum.")
				
				if 'W' in command:
					if transactionNum != 'NONE' and variableNum != 'NONE' and value != 'NONE':
						tNum = int(transactionNum)
						vNum = int(variableNum)
						valueNum = int(value)
						if tNum in global_var.TransactionList.keys():
							TM.write(tNum,vNum,valueNum)
						else:
							print("Error: Command denied because transaction {} doesn't exist".format(tNum))
					else:
						print("Error: Please enter transaction number/variable number/value")
				if 'R' in command and 'beginRO' not in command:
					if transactionNum != 'NONE' and variableNum != 'NONE':
						tNum = int(transactionNum)
						rNum = int(variableNum)
						if tNum in global_var.TransactionList.keys():
							TM.readCommand(tNum,rNum)
						else:
							print("Error: Command denied because transaction {} doesn't exist".format(tNum))
					else:
						print("Error: Please enter transaction number/variable number")
				if 'end' in command:
					if transactionNum != 'NONE':
						tNum = int(transactionNum)
						if tNum in global_var.TransactionList.keys():
							TM.endCommand(tNum)
						else:
							print("Error: Transaction {} not exist.".format(tNum))
					else:
						print("Error: Please enter transactionNum.")
				if 'fail' in command:
					if siteNum != 'NONE':
						sNum = int(siteNum)
						if sNum in global_var.DataManagerList.keys():
							TM.fail(sNum)
						else:
							print("Error: Site {} not exist".format(sNum))
					else:
						print("Error: Please enter site number.")
				if 'recover' in command:
					if siteNum != 'NONE':
						sNum = int(siteNum)
						if sNum in global_var.DataManagerList.keys():
							TM.recover(sNum)
						else:
							print("Error: Site {} not exist".format(sNum))
					else:
						print("Error: Please enter site number.")
				if 'dump' in command:
					if siteNum == 'NONE' and variableNum == 'NONE':
						TM.dumpCommand()
					elif siteNum != 'NONE' and variableNum == 'NONE':
						sNum = int(siteNum)
						if sNum in global_var.DataManagerList.keys():
							TM.dumpCommand(sNum,-1)
						else:
							print("Error: Site {} not exist".format(sNum))
					elif siteNum == 'NONE' and variableNum != 'NONE':
						vNum = int(variableNum)
						if vNum in global_var.VariableSiteList.keys():
							TM.dumpCommand(-1,vNum)
						else:
							print("Error: variable {} not exist".format(vNum))
					else:
						print("Error: command not recognize.")


