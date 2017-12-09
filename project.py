# Author: Jiayun Yu, Kailin Luo
# Date: Dec 8th, 2017
# Final Project for Advanced Database System class

from __future__ import print_function
import module
import sys
import re
import status as global_var


if __name__ == "__main__":
	print()
	print("Database initial information: 20 variables in 10 sites:")
	print()

	# generate variable list
	for i in range(20):
		if (i + 1) % 2 == 0:
			global_var.VariableSiteList[i+1] = [1,2,3,4,5,6,7,8,9,10]
		else:
			global_var.VariableSiteList[i+1] = [1+(i+1) % 10]
	for v in global_var.VariableSiteList.keys():
		print("variable {0} in sites {1}".format(v,global_var.VariableSiteList[v]))
	print()
	# generate data manager
	for i in range(10):
		print("site {}".format(i+1))
		DM = module.DataManager(i+1)
		global_var.DataManagerList[i+1] = DM
		print()
	
	print("---------------------------------------------------------------------")
	TM = module.TransactionMachine()
	print("Transaction Status:")
	print()

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
				line =line.replace(" ", "")
				command = re.search('(([a-zA-Z]+))',line).group(0) if re.search('([a-zA-Z]+)',line) else 'NONE'
				transactionNum = re.search('T([0-9]+)',line).group(1) if re.search('T([0-9]+)',line) else 'NONE'
				variableNum = re.search('[x]([0-9]+)',line).group(1) if re.search('[x]([0-9]+)',line) else 'NONE'

				siteNumFirst = re.search('[(]([0-9]+)[)]',line).group(0) if re.search('[(]([0-9]+)[)]',line) else 'NONE'
				siteNum = re.search('([0-9]+)',siteNumFirst).group(0) if re.search('([0-9]+)',siteNumFirst) else 'NONE'

				valueFirst = re.search('[,]([0-9]+)[)]',line).group(0) if re.search('[,]([0-9]+)[)]',line) else 'NONE'
				value = re.search('([0-9]+)',valueFirst).group(0) if re.search('([0-9]+)',valueFirst) else 'NONE'


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


