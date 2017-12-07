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

	# generate variable list
	for i in range(20):
		if (i + 1) % 2 == 0:
			global_var.VariableSiteList[i+1] = [1,2,3,4,5,6,7,8,9,10]
		else:
			global_var.VariableSiteList[i+1] = [1+(i+1) % 10]
	for v in global_var.VariableSiteList.keys():
		print("variable {0} in sites {1}".format(v,global_var.VariableSiteList[v]))

	# test.printFunction()
	# generate data manager
	for i in range(10):
		print("site {}".format(i+1))
		DM = module.DataManager(i+1)
		global_var.DataManagerList[i+1] = DM
		print()
	
	TM = module.TransactionMachine()
	# Test 1

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
	TM.endCommand(2)'''

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
	TM.readCommand(1,3)
	TM.write(2,8,88)
	TM.fail(2)
	TM.readCommand(2,3)
	TM.write(1,4,91)
	TM.recover(2)
	TM.endCommand(2)
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

	#TM.read(1,1)
	'''TM.write(2,2,202)
	print()
	TM.write(1,2,102)
	#global_var.DataManagerList[2].fail()
	print()
	TM.write(2,1,201)'''
	'''while 1:
		try:
			line = sys.stdin.readline()
		except KeyboardInterrupt:
			break
		if not line:
			break
		command = re.search('(([a-zA-Z]+))',line).group(0) if re.search('([a-zA-Z]+)',line) else 'NONE'
		transactionNum = re.search('T([0-9]+)',line).group(1) if re.search('T([0-9]+)',line) else 'NONE'
		variableNum = re.search('[x]([0-9]+)',line).group(1) if re.search('[x]([0-9]+)',line) else 'NONE'
		if variableNum != 'NONE':
			variableNum = int(variableNum)

		siteNumFirst = re.search('[(]([0-9]+)[)]',line).group(0) if re.search('[(]([0-9]+)[)]',line) else 'NONE'
		siteNum = re.search('([0-9]+)',siteNumFirst).group(0) if re.search('([0-9]+)',siteNumFirst) else 'NONE'

		valueFirst = re.search('[,]([0-9]+)[)]',line).group(0) if re.search('[,]([0-9]+)[)]',line) else 'NONE'
		value = re.search('([0-9]+)',valueFirst).group(0) if re.search('([0-9]+)',valueFirst) else 'NONE'
		print("Command {0} for tansaction {1} or site {2} for variable {3} with value {4}".format(command,transactionNum,siteNum,variableNum,value))

		if 'begin' in command:
			TM.begin(transactionNum)
		if 'W' in command:
			TM.write(transactionNum,variableNum,value)

	print("get main.")'''