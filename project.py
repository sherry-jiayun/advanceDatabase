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
		if i % 2 == 0:
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
		global_var.DataManagerList.append(DM)
		print()
	
	TM = module.TransactionMachine()
	TM.begin(1)
	TM.write(1,1,101)
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