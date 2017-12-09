# Author: Jiayun Yu, Kailin Luo
# Date: Dec 8th, 2017
# Final Project for Advanced Database System class

from __future__ import print_function
import project 
import status as global_var


class VariableInSite(object):
	'''
	Object: In each site, variables stored with different versions.
	function: 	getinfo - print variable info
				not Accessible - change accessible to be false
				updateValue - change value 
				_grantedAccessible - change accessible to be false
	'''
	def __init__(self, index, variabletype, version = 0):
		self.type = variabletype 				# 0 for replicate and 1 for not
		self.index = index
		self.value = 10 * index 				# for initialize 
		self.accessible = True 					# True for initialize
		self.version = version 					# 0 for initialize increase by transaction index 
	def getInfo(self):
		print("Variable {0} with type {1} version {2} and value {3} and accessible {4}".format(self.index,self.type,self.version,self.value,self.accessible))
		return
	def notAccessible(self):
		self.accessible = False
	def updateValue(self,value):
		self.value = value
		self._grantedAccessible()
	def _grantedAccessible(self):
		if self.accessible == False:
			self.accessible = True
			print("Variable {0} : is accessible".format(self.index))

class VariableInCommand(object):
	'''
	Object: Variable in command
	'''
	def __init__(self, index, variabletype, value):
		self.index = index
		self.value = value # none for not read only transaction
		
class Lock(object):
	'''
	Object: Lock
	function: lockGranted - return if granted the lock
	'''
	def __init__(self, locktype, transactionNum, commandNum):
		self.locktype = locktype 								# read lock, write lock
		self.transactionNum = transactionNum 				
		self.commandNum = commandNum
	def lockGranted(self, currentLockList, waitLockList):
		granted = True
		if self.locktype == global_var.LOCK_TYPE_WRITE:			#for write lock
			for l in currentLockList:							
				if l.transactionNum != self.transactionNum:		#if there is other locks, then not granted
					granted = False
					break 
		if self.locktype == global_var.LOCK_TYPE_READ:			#for read lock
			for l in currentLockList:
				if l.locktype == global_var.LOCK_TYPE_WRITE and l.transactionNum != self.transactionNum:
					granted = False 							#if there is other write locks, then not granted
					break
			for l in waitLockList:
				if l.locktype == global_var.LOCK_TYPE_WRITE and l.transactionNum == self.transactionNum:
					granted = False 							#if there is write locks of same transaction waiting, then not granted
					break
		return granted


class Transaction(object):
	'''
	Object: Transaction
	function: 	addCommand - add new command in this transaction
				getNexCommandNum - retrun next command number
				setLastCommitedVersion - update last committed version in this transaction
	'''
	def __init__(self, index, transactionNum, readOnly,currentVariableValue = {}):
		self.index = index 								# time stamp
		self.name = transactionNum 						# transaction number 
		self.readOnly = readOnly 						# true or false
		self.commandlist = {} 							# store all command
		self.status = -1 								# -1 for initialize, 0 for success, 1 for wait, 2 for fail
		self.currentVariableValue = {} 					# for readOnly
		self.commandNum = 0 							# initialized with 0 
		self.lastCommitedVersion = 0
	def addCommand(self,command):
		self.commandlist[command.commandNum] = command
		self.commandNum = self.commandNum + 1
	def getNexCommandNum(self):
		return self.commandNum
	def setLastCommitedVersion(self,lastCommitedVersion):
		self.lastCommitedVersion = lastCommitedVersion

class Command(object):
	'''
	Object: Command
	function: 	putLock - get lock
				putResult - get read value
	'''
	def __init__(self, index, commandtype, transactionNum, variableNum, value, commandNum):
		self.index = index 										# time stamp
		self.commandtype = commandtype 							# 1 for read, 2 for write
		self.transactionNum = transactionNum 
		self.variableNum = variableNum
		self.value = value 										# read value
		self.status = global_var.COMMAND_STATUS_INITIALIZE 		# initial status
		self.commandNum = commandNum
		self.lockGrantedNum = 0									# number of granted locks
		if variableNum % 2 == 0:								# number of required locks
			self.lockRequiredNum = 10 
		else:
			self.lockRequiredNum = 1
		if(self.commandtype == 1):
			print("Transaction {0} : create read command with commandNum {1}".format(self.transactionNum, self.commandNum))
		else:
			print("Transaction {0} : create write command with commandNum {1}".format(self.transactionNum, self.commandNum))
	def putLock(self,commandLock):
		self.commandLock = commandLock
	def putResult(self,value):
		self.value = value

class TransactionMachine(object):
	'''
	Object: TransactionMachine

	'''
	def __init__(self):
		self.index = 0							# timestamp
		self.graph = {}							# graph for detect deadlock
		self.waitcommittransaction = []			# wait commit transaction list
		self.waitCommandList = []				# wait transaction list
		self.cycleTransaction = []				# cycle list 
		self.lastCommitedVersion = 0			# last commit version number
	def begin(self,transactionNum):
		# Function: begin a transactionNum
		# Input: the transaction number 
		# Output: message
		transTmp = Transaction(self.index, transactionNum, False)	# create transaction
		self.index = self.index + 1									# add index
		global_var.TransactionList[transactionNum] = transTmp		# append to transactionList
		self.__addVertex(transactionNum)							# add vertex to graph
		print("Transaction {} : begin.".format(transactionNum))
		print()
		return

	def write(self,transactionNum, variableNum, variableValue):
		# Function: write a variable a new value
		# Input: transaction number, variable number, value
		# Output: message
		success = True
		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_ABORT:
			print("Transaction {0} : abort and will not execute any command".format(transactionNum))
			print()
			return False
		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_WAIT:
			# add command to wait list directly
			self.waitCommandList.append(['W',transactionNum,variableNum,variableValue])
			print("Transaction {0} : command will wait since former command in transaction {0} doesn't finish".format(transactionNum))
			print("Transaction {0} : Current wait list:{1}".format(transactionNum,self.waitCommandList))
			print()
			return False

		commandNum = global_var.TransactionList[transactionNum].getNexCommandNum()					# get a command number
		commandLock = Lock(global_var.LOCK_TYPE_WRITE,transactionNum,commandNum)					# create a lock 
		commandTmp = Command(self.index, 2, transactionNum, variableNum, variableValue,commandNum)	# create command object
		
		siteList = global_var.VariableSiteList[variableNum]											# get site list
		result_success = False
		result_wait =False
		result_fail = False
		for i in siteList:																			# go through list and checkLock()
			print("Transaction {0} : check lock from site {1}".format(transactionNum, i))
			TNum1, TNum2List, Fail = global_var.DataManagerList[i].checkLock(transactionNum,variableNum,commandLock)

			if not Fail and len(TNum2List) <= 0:													#if success(not fail and no wait)
				result_success = True
				commandTmp.lockGrantedNum = commandTmp.lockGrantedNum + 1
			if not Fail and len(TNum2List) > 0:														# if not fail but wait for lock
				self.__addEdge(transactionNum,TNum2List) 											# add edge in graph
				result_wait = True
			if Fail:																				# if fail to get lock
				result_fail = True
				commandTmp.lockRequiredNum = commandTmp.lockRequiredNum - 1
		if result_success and not result_wait and not result_fail:  								# If success in all site in siteList
			commandTmp.putLock(commandLock)
			global_var.TransactionList[transactionNum].currentVariableValue[variableNum] = variableValue # add variable to transaction
			commandTmp.status = global_var.COMMAND_STATUS_SUCCESS
			print("Transaction {0} : get lock success".format(transactionNum))
			print("Transaction {0} : add to changed variable list, new list: {1}".format(transactionNum, global_var.TransactionList[transactionNum].currentVariableValue))

		elif not result_success and result_wait and not result_fail:								# If wait
			commandTmp.putLock(commandLock)
			commandTmp.status = global_var.COMMAND_STATUS_WAIT
			print("Transaction {0} : wait for lock".format(transactionNum))

		elif result_success and not result_wait and result_fail:   									 # If success but some sites failed
			commandTmp.putLock(commandLock)
			global_var.TransactionList[transactionNum].currentVariableValue[variableNum] = variableValue
			commandTmp.status = global_var.COMMAND_STATUS_SUCCESS
			print("Transaction {0} : get lock success but some site failed".format(transactionNum))
			print("Transaction {0} : add to changed variable list, new list: {1}".format(transactionNum, global_var.TransactionList[transactionNum].currentVariableValue))

		elif not result_success and result_wait and result_fail:									# If wait but some sites failed
			commandTmp.putLock(commandLock)
			commandTmp.status = global_var.COMMAND_STATUS_WAIT
			print("Transaction {0} : wait for lock and some site failed".format(transactionNum))

		elif not result_success and not result_wait and result_fail:								# If all sites failed then wait
			global_var.TransactionList[transactionNum].status = global_var.TRANSACTION_STATUS_WAIT
			global_var.TransactionList[transactionNum].addWaitCommand(['W',transactionNum,variableNum,variableValue])
			print("Transaction {0} : wait for failed sites and command add to transaction {0} wait list".format(transactionNum))
			print("Transaction {0} : Current wait list:{1}".format(transactionNum,self.waitCommandList))
			success = False
			return False
		else:
			commandTmp.putLock(commandLock)
			commandTmp.status = global_var.COMMAND_STATUS_WAIT
			print("Transaction {0} : Wait".format(transactionNum))
	
		global_var.TransactionList[transactionNum].addCommand(commandTmp)

		self.index = self.index + 1
		# deadlock detect
		print("Transaction {0} : want to write to variable {1} with value {2}.".format(transactionNum,variableNum,variableValue))
		self.__deadLock()
		print()

		return success
	def readCommand(self,transactionNum,variableNum):
		# Function: call read functions(read or readonly)
		# Input: transaction number, variable number
		# Output: return read success or not
		success = True
		if global_var.TransactionList[transactionNum].readOnly:
			success = self.readRO(transactionNum,variableNum)
		else:
			success = self.read(transactionNum,variableNum)
		return success
	def readRO(self,transactionNum,variableNum):
		# Function: read only transaction to call read command
		# Input: transaction number, variable number
		# Output: messages and return read success or not
		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_ABORT:
			print("ReadOnly Transaction {0} : abort and will not execute any command".format(transactionNum))
			print()
			return False
		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_WAIT:
			# add command to wait list directly
			self.waitCommandList.append(['R',transactionNum,variableNum])
			print("ReadOnly Transaction {0} : command will wait since former command in transaction {0} doesn't finish".format(transactionNum))
			print("ReadOnly Transaction {0} : Current wait list: {1}".format(transactionNum, self.waitCommandList))
			print()
			return False
		success = True

		commandIndex = global_var.TransactionList[transactionNum].index  				  # contain same index as transaction
		commandNum = global_var.TransactionList[transactionNum].getNexCommandNum()
		commandTmp = Command(commandIndex, 1, transactionNum, variableNum, -1,commandNum) # create a new command object 

		siteList = global_var.VariableSiteList[variableNum] 							  # get site list
		result_success = False
		result_wait =False
		result_fail = False
		readResult = -1
		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_WAIT:
			global_var.TransactionList[transactionNum].addCommand(commandTmp)
			print("ReadOnly Transaction {1} : command {0} for read only transaction {1} wait because have previous wait command".format(commandNum,transactionNum))
			print()
			return
		for i in siteList:																   # go through list and checkLock()
			print("ReadOnly Transaction {0} : check value from site {1}".format(transactionNum, i))
			readResultTmp,readResultFail = global_var.DataManagerList[i].getValue(variableNum,commandTmp.index,True,global_var.TransactionList[transactionNum].lastCommitedVersion)
			if not readResultFail: 							# may be failed because site just recover and inaccessible 
				readResult = readResultTmp
				result_success = True
				break
			else:
				result_fail = True
		if result_success and not result_wait and not result_fail:						# read success
			commandTmp.putResult(readResult)
			commandTmp.status = global_var.COMMAND_STATUS_SUCCESS	
			global_var.TransactionList[transactionNum].addCommand(commandTmp)
			print("ReadOnly Transaction {0} : read success".format(transactionNum))
		elif result_success and not result_wait and result_fail:						# read success but some sites failed
			commandTmp.putResult(readResult)
			commandTmp.status = global_var.COMMAND_STATUS_SUCCESS
			global_var.TransactionList[transactionNum].addCommand(commandTmp)
			print("ReadOnly Transaction {0} : read success but some sites failed".format(transactionNum))
		elif not result_success and not result_wait and result_fail:					# all sites failed
			commandTmp.status = global_var.COMMAND_STATUS_WAIT
			global_var.TransactionList[transactionNum].status = global_var.TRANSACTION_STATUS_WAIT
			self.waitCommandList.append(['R',transactionNum,variableNum])
			print("ReadOnly Transaction {0} : wait and command add to transaction {0} wait list".format(transactionNum))
			print("ReadOnly Transaction {0} : Current wait list {1}:".format(transactionNum,self.waitCommandList))
			success = False
		print("ReadOnly Transaction {0} : want to read to variable {1} with value {2}".format(transactionNum,variableNum,commandTmp.value))
		print()
		return success
	def read(self,transactionNum, variableNum):
		# Function: not readonly transaction to call read command
		# Input: transaction number, variable number
		# Output: messages and return read success or not
		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_ABORT:
			print("Transaction {0} : Aborted and will not execute any command".format(transactionNum))
			print()
			return False
		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_WAIT:
			# add command to wait list directly
			self.waitCommandList.append(['R',transactionNum,variableNum])
			print("Transaction {0} : command will wait since former command in transaction {0} doesn't finish".format(transactionNum))
			print("Current wait list:".format(self.waitCommandList))
			print()
			return False
		success = True
		commandNum = global_var.TransactionList[transactionNum].getNexCommandNum()     				# get command number
		commandLock = Lock(global_var.LOCK_TYPE_READ,transactionNum,commandNum)		   				# create a lock 
		commandTmp = Command(self.index, 1, transactionNum, variableNum, -1,commandNum)				# create command object 
		
		siteList = global_var.VariableSiteList[variableNum]	# get site list
		result_success = False
		result_wait =False
		result_fail = False
		readResult = -1
		for i in siteList:									# go through list and checkLock()
			print("Transaction {0} : check lock from site {1}".format(transactionNum, i))
			TNum1, TNum2List, Fail = global_var.DataManagerList[i].checkLock(transactionNum,variableNum,commandLock)
			if not Fail and len(TNum2List) <= 0:			#if success(not fail and no wait)
				result_success = True
				readResultTmp,readResultFail = global_var.DataManagerList[i].getValue(variableNum,commandTmp.index) # get the read value
				if not readResultFail: 						# if not get value failed because site just recover and is not accessiable 
					readResult = readResultTmp
					# print(readResult)
					break
				# stop ask for lock once get 
			if not Fail and len(TNum2List) > 0:				# if not fail but wait for lock
				self.__addEdge(transactionNum,TNum2List) 	# add edge in graph
				result_wait = True
			if Fail:										# if fail to get lock
				result_fail = True


		if result_success and not result_wait and not result_fail:				# If success in all site in siteList
			commandTmp.putLock(commandLock)
			if variableNum in global_var.TransactionList[transactionNum].currentVariableValue.keys(): # if write command before in same transaction
				readResult = global_var.TransactionList[transactionNum].currentVariableValue[variableNum]  # read the value this transaction wrote
				print(transactionNum,global_var.TransactionList[transactionNum].currentVariableValue)
			commandTmp.putResult(readResult)
			commandTmp.status = global_var.COMMAND_STATUS_SUCCESS
			print("Transaction {0} : get lock".format(transactionNum))
		elif not result_success and result_wait and not result_fail:			# If wait
			commandTmp.putLock(commandLock)
			commandTmp.status = global_var.COMMAND_STATUS_WAIT
			print("Transaction {0} : wait for lock".format(transactionNum))
		elif result_success and not result_wait and result_fail:				# If success but some sites failed
			commandTmp.putLock(commandLock)
			if variableNum in global_var.TransactionList[transactionNum].currentVariableValue.keys(): # if write command before in same transaction
				readResult = global_var.TransactionList[transactionNum].currentVariableValue[variableNum] # read the value this transaction wrote
			commandTmp.putResult(readResult)
			commandTmp.status = global_var.COMMAND_STATUS_SUCCESS
			print("Transaction {0} : get lock but some site failed".format(transactionNum))
		elif not result_success and result_wait and result_fail:				# If wait but some sites failed
			commandTmp.putLock(commandLock)
			commandTmp.status = global_var.COMMAND_STATUS_WAIT
			print("Transaction {0} : wait for lock but some site failed".format(transactionNum))
		elif not result_success and not result_wait and result_fail:			# If all sites failed
			global_var.TransactionList[transactionNum].status = global_var.TRANSACTION_STATUS_WAIT
			self.waitCommandList.append(['R',transactionNum,variableNum])
			print("Transaction {0} : wait for lock and command add to transaction {0} wait list".format(transactionNum))
			print("Transaction {0} : Current wait list:{1}".format(transactionNum,self.waitCommandList))
			success =False
			return False
		else:
			print("Transaction {0} : wait".format(transactionNum))
		
		global_var.TransactionList[transactionNum].addCommand(commandTmp)
		self.index = self.index + 1
		self.__deadLock()						# deadlock detect
		print("Transaction {0} : want to read to variable {1} with value {2}.".format(transactionNum,variableNum,commandTmp.value))
		print()
		return success
	def endCommand(self,transactionNum):
		# Function: call end functions(normal transactions or readonly transactions)
		# Input: transaction number
		if global_var.TransactionList[transactionNum].readOnly:
			self.endRO(transactionNum)
		else:
			self.end(transactionNum)

	def endRO(self,transactionNum):
		# Function: readonly transaction to call end command
		# Input: transaction number
		# Output: messages and return end success or not
		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_ABORT:
			print("ReadOnly Transaction {0} : Aborted and will not execute any command".format(transactionNum))
			print()
			return False
		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_WAIT:
			# add command to wait list directly
			self.waitCommandList.append(['end',transactionNum])
			print("ReadOnly Transaction {0} : command will wait since former command in transaction {0} doesn't finish".format(transactionNum))
			print("ReadOnly Transaction {0} : Current wait list:{1}".format(transactionNum, self.waitCommandList))
			print()
			return False
		validate = True
		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_ABORT:
			validate = False
		for commandNum in global_var.TransactionList[transactionNum].commandlist:
			commandTmp = global_var.TransactionList[transactionNum].commandlist[commandNum]
			if commandTmp.status != global_var.COMMAND_STATUS_SUCCESS:
				validate = False
				print()
				break
		if validate:			# commit success
			global_var.TransactionList[transactionNum].status = global_var.TRANSACTION_STATUS_COMMIT
			print("ReadOnly Transaction {0} : Committed!".format(transactionNum))
		else:					# wait commit, still some commands waiting
			if global_var.TransactionList[transactionNum].status != global_var.TRANSACTION_STATUS_ABORT:
				global_var.TransactionList[transactionNum].status = global_var.TRANSACTION_STATUS_WAIT_COMMIT
				if transactionNum not in self.waitcommittransaction:
					self.waitcommittransaction.append(transactionNum)
				print("ReadOnly Transaction {0} : Wait for commit".format(transactionNum))
			else:
				print("ReadOnly Transaction {0} : Aborted".format(transactionNum))
		print()
		return True

	def end(self,transactionNum):
		# Function: not readonly transaction to call end command
		# Input: transaction number
		# Output: messages and return end success or not
		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_ABORT:
			print("Transaction {0} : Aborted and will not execute any command".format(transactionNum))
			print()
			return False
		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_WAIT:
			# add command to wait list directly
			self.waitCommandList.append(['end',transactionNum])
			print("Transaction {0} : command will wait since former command in transaction {0} doesn't finish".format(transactionNum))
			print("Transaction {0} : Current wait list:".format(self.waitCommandList))
			print()
			return False
		validate = True
		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_ABORT:
			validate = False
		for commandNum in global_var.TransactionList[transactionNum].commandlist:
			commandTmp = global_var.TransactionList[transactionNum].commandlist[commandNum]
			if commandTmp.status != global_var.COMMAND_STATUS_SUCCESS:
				validate = False
				print("Transaction {0} : cannot commit because of unsuccess command{1}".format(transactionNum, commandNum))
				print (commandTmp.index,commandTmp.commandtype,commandTmp.variableNum,commandTmp.status)
				break
		newGrantedLockList = []
		if validate:
			# safe to commit
			print("Transaction {0} : Committed!".format(transactionNum))
			for commandNum in global_var.TransactionList[transactionNum].commandlist:
				commandTmp = global_var.TransactionList[transactionNum].commandlist[commandNum]
				siteList = global_var.VariableSiteList[commandTmp.variableNum]
				lockTmp = commandTmp.commandLock
				for s in siteList:
					if commandTmp.commandtype == 2:
						Fail = global_var.DataManagerList[s].update(commandTmp)
						# fail may caused by site fail
						if self.lastCommitedVersion < commandTmp.index:
							self.lastCommitedVersion = commandTmp.index
					# remove lock
					newGrantedLock = global_var.DataManagerList[s].removeLock(transactionNum,commandTmp.variableNum,commandTmp.commandLock)
					for l in newGrantedLock:
						commandT = global_var.TransactionList[l.transactionNum].commandlist[l.commandNum]
						if commandT.commandtype == 2:
							commandT.lockGrantedNum = commandT.lockGrantedNum + 1
							if commandT.lockGrantedNum == commandT.lockRequiredNum and l not in newGrantedLockList:
								newGrantedLockList.append(l)
						elif commandT.commandtype == 1 and l not in newGrantedLockList:
							newGrantedLockList.append(l)
			global_var.TransactionList[transactionNum].status = global_var.TRANSACTION_STATUS_COMMIT
			if transactionNum in self.waitcommittransaction:
				self.waitcommittransaction.remove(transactionNum)
			# remove edge from list 
			self.__deleteVertex(transactionNum)
			newChangedTransaction = []
			for l in newGrantedLockList:
				# find command by lock
				commandTmp = global_var.TransactionList[l.transactionNum].commandlist[l.commandNum]
				if commandTmp.commandtype == 1:
					# read 
					readResult = -1
					siteList = global_var.VariableSiteList[commandTmp.variableNum]
					for s in siteList:
						readResultTmp,readResultFail = global_var.DataManagerList[s].getValue(commandTmp.variableNum,commandTmp.index)
						if not readResultFail: 
							# may caused because site just recover and unaccisable 
							readResult = readResultTmp
					if commandTmp.variableNum in global_var.TransactionList[transactionNum].currentVariableValue.keys():
						# may caused by write command in same transaction
						readResult = global_var.TransactionList[transactionNum].currentVariableValue[commandTmp.variableNum]
					commandTmp.putResult(readResult)
					print("Transaction {1} : read command {0} success read variable {2} with value {3}".format(commandTmp.commandNum,commandTmp.transactionNum,commandTmp.variableNum,commandTmp.value))
				else:
					global_var.TransactionList[commandTmp.transactionNum].currentVariableValue[commandTmp.variableNum] = commandTmp.value
					print("Transaction {1} : write command {0} success write variable {2} with value {3}".format(commandTmp.commandNum,commandTmp.transactionNum,commandTmp.variableNum,commandTmp.value))
				commandTmp.status = global_var.COMMAND_STATUS_SUCCESS
				
				if l.transactionNum not in newChangedTransaction:
					newChangedTransaction.append(l.transactionNum)
			for t in newChangedTransaction:
				if t in self.waitcommittransaction:
					self.end(t)
			retryList = self.waitCommandList
			self.waitCommandList = []
			# change all transaction's state to initialize
			for t in global_var.TransactionList.keys():
				if global_var.TransactionList[t].status == global_var.TRANSACTION_STATUS_WAIT:
					global_var.TransactionList[t].status = global_var.TRANSACTION_STATUS_INITIALIZE
			for c in retryList:
				if c[0] == 'W':
					success = self.write(c[1],c[2],c[3])
				if c[0] == 'R':
					success = self.readCommand(c[1],c[2])
				if c[0] == 'end':
					success = self.endCommand(c[1])
			# print(self.waitCommandList)
			print()
		else:
			# change status, put in wait list
			if global_var.TransactionList[transactionNum].status != global_var.TRANSACTION_STATUS_ABORT:
				global_var.TransactionList[transactionNum].status = global_var.TRANSACTION_STATUS_WAIT_COMMIT
				if transactionNum not in self.waitcommittransaction:
					self.waitcommittransaction.append(transactionNum)
				print("Transaction {0} : wait for commit".format(transactionNum))
			else:
				print("Transaction {0} : abort".format(transactionNum))
			print()
		return True

	def recover(self,datamanagerNum):
		# Function: recover site
		# Input: datamanager number
		global_var.DataManagerList[datamanagerNum].recover()
		retryList = self.waitCommandList
		self.waitCommandList = []						# clear wait list
		for t in global_var.TransactionList.keys():		# change all transaction's state to initialize
			if global_var.TransactionList[t].status == global_var.TRANSACTION_STATUS_WAIT:
				global_var.TransactionList[t].status = global_var.TRANSACTION_STATUS_INITIALIZE
		for c in retryList:
			if c[0] == 'W':
				success = self.write(c[1],c[2],c[3])
			if c[0] == 'R':
				success = self.readCommand(c[1],c[2])
			if c[0] == 'end':
				success = self.endCommand(c[1])
		return

	def fail(self,datamanagerNum):
		# Function: fail a site
		# Input: datamanager number
		# Output: massages
		transactionList = global_var.DataManagerList[datamanagerNum].fail()
		print("Site {} : fail".format(datamanagerNum))
		print()

		for t in transactionList:							# abort uncommitted transations
			if global_var.TransactionList[t].status != global_var.TRANSACTION_STATUS_COMMIT:
				global_var.TransactionList[t].status = global_var.TRANSACTION_STATUS_ABORT
				print("Transaction {0} : abort because site {1} failed".format(t,datamanagerNum))
				self.__abort(t)

		retryList = self.waitCommandList					# may cause waitted command continue 
		self.waitCommandList = []							# clear wait list
		for t in global_var.TransactionList.keys():			# change all transaction's state to initialize
			if global_var.TransactionList[t].status == global_var.TRANSACTION_STATUS_WAIT:
				global_var.TransactionList[t].status = global_var.TRANSACTION_STATUS_INITIALIZE
		for c in retryList:
			if c[0] == 'W':
				success = self.write(c[1],c[2],c[3])
			if c[0] == 'R':
				success = self.readCommand(c[1],c[2])
			if c[0] == 'end':
				success = self.endCommand(c[1])
		return

	def beginRO(self,transactionNum):
		# Function: begin a readonly transaction
		# Input: transaction number
		# Output: massages
		transTmp = Transaction(self.index, transactionNum, True)		# create transaction
		transTmp.setLastCommitedVersion(self.lastCommitedVersion)		# get last commited version of variables
		self.index = self.index + 1										# add index
		global_var.TransactionList[transactionNum] = transTmp			# append to transactionList
		self.__addVertex(transactionNum)								# add vertex to graph
		print("ReadOnly Transaction {} : begin.".format(transactionNum))
		print()
		return

	def dumpCommand(self,datamanagerNum = -1,variableNum = -1):
		# Function: print the committed values
		# Input: datamanager number, variable number
		if datamanagerNum != -1:
			self.dump2(datamanagerNum)
		elif variableNum != -1:
			self.dump3(variableNum)
		else:
			self.dump1()

	def dump1(self):
		# Function: print the committed values of all copies of all variables at all sites, sorted per site.
		print("Print the committed values of all copies of all variables at all sites, sorted per site.:")
		print()

		for i in global_var.DataManagerList:
			print()
			print("Site {}".format(i))
			for var in global_var.DataManagerList[i].variables.keys():
				for varVersion in global_var.DataManagerList[i].variables[var]:
					varVersion.getInfo()
		print()
		return

	def dump2(self, datamanagerNum):
		# Function: print the committed values of all copies of all variables at all sites, sorted per site.
		# Input: datamanager Number
		print(" Print the committed values of all copies of all variables at site {}.".format(datamanagerNum))
		print()
		for var in global_var.DataManagerList[datamanagerNum].variables.keys():
			for varVersion in global_var.DataManagerList[datamanagerNum].variables[var]:
				varVersion.getInfo()
		print()
		return

	def dump3(self, variableNum):
		# Function: print the committed values of all copies of variable xj at all sites.
		# Input: variable Number
		print(" Print the committed values of all copies of {} at all site.".format(variableNum))
		print()
		for i in global_var.DataManagerList:
			print("Site {}".format(i))
			for varVersion in global_var.DataManagerList[i].variables[variableNum]:
				varVersion.getInfo()
		print()
		return

	def __abort(self,transactionNum):
		# Function: call when abort happen
		# Input: transaction Number
		# Output: messages
		print("Transaction {0} : Aborted".format(transactionNum))
		print("Transaction {0} : remove locks".format(transactionNum))
		print()

		global_var.TransactionList[transactionNum].status = global_var.TRANSACTION_STATUS_ABORT
		newGrantedLockList = []
		for commandNum in global_var.TransactionList[transactionNum].commandlist:
			commandTmp = global_var.TransactionList[transactionNum].commandlist[commandNum]
			siteList = global_var.VariableSiteList[commandTmp.variableNum]
			for s in siteList:
				# remove lock no update
				newGrantedLock = global_var.DataManagerList[s].removeLock(transactionNum,commandTmp.variableNum,commandTmp.commandLock)
				for l in newGrantedLock:
					if l not in newGrantedLockList:
						newGrantedLockList.append(l)

		if transactionNum in self.waitcommittransaction:
			# remove ransaction from wait commit saction
			self.waitcommittransaction.remove(transactionNum)
		# remove edge from list 
		self.__deleteVertex(transactionNum)
		newChangedTransaction = []

		for l in newGrantedLockList:
			# find command by lock
			commandTmp = global_var.TransactionList[l.transactionNum].commandlist[l.commandNum]
			if commandTmp.commandtype == 1:
				# read 
				readResult = -1
				siteList = global_var.VariableSiteList[commandTmp.variableNum]
				for s in siteList:
					readResultTmp,readResultFail = global_var.DataManagerList[s].getValue(commandTmp.variableNum,commandTmp.index)
					if not readResultFail: 
						# may caused because site just recover and unaccisable 
						readResult = readResultTmp
				if commandTmp.variableNum in global_var.TransactionList[transactionNum].currentVariableValue.keys():
					# may caused by write command in same transaction
					readResult = global_var.TransactionList[transactionNum].currentVariableValue[commandTmp.variableNum]
				commandTmp.putResult(readResult)
				print("Transaction {1} : read command {0} success read variable {2} with value {3}".format(commandTmp.commandNum,commandTmp.transactionNum,commandTmp.variableNum,commandTmp.value))
			else:
				global_var.TransactionList[commandTmp.transactionNum].currentVariableValue[commandTmp.variableNum] = commandTmp.value
				print("Transaction {1} : write command {0} success write variable {2} with value {3}".format(commandTmp.commandNum,commandTmp.transactionNum,commandTmp.variableNum,commandTmp.value))
			commandTmp.status = global_var.COMMAND_STATUS_SUCCESS
			
			if l.transactionNum not in newChangedTransaction:
				newChangedTransaction.append(l.transactionNum)
		for t in newChangedTransaction:
			if t in self.waitcommittransaction:
				self.end(t)
		return
	def __addVertex(self,transactionNum):
		# Function: add vertex in graph
		# Input: transaction Number
		self.graph[transactionNum] = []
		return
	def __addEdge(self,transactionNum1,transactionNum2):
		# Function: add edges in graphs
		# Input: waited transaction list, waiting transaction list
		# Output: messages
		for i in transactionNum2:
			if i not in self.graph[transactionNum1]:
				self.graph[transactionNum1].append(i)
		print("Transaction {0} : add edges in current waiting graph {1}".format(transactionNum1, self.graph))
		return
	def __deleteVertex(self,transactionNum):
		# Function: remove vertex in graphs
		# Input: transaction number
		self.graph.pop(transactionNum,None)
		for key in self.graph.keys():
			if transactionNum in self.graph[key]:
				self.graph[key].remove(transactionNum)
		return
	def __deadLock(self):
		# Function: if deadlock, abort youngest transaction
		# Output: message		
		self.cycleTransaction = []
		cycle = self.__isCyclic()
		youngest = None
		for t in self.cycleTransaction:
			if youngest == None or global_var.TransactionList[youngest].index < global_var.TransactionList[t].index:
				youngest = t
		if cycle and youngest != None:
			print ("Transaction {0} : Deadlock! Abort youngest transaction {0}".format(youngest))
			self.__abort(youngest)
			self.__deadLock()

		return
	def __isCyclicUtil(self,v,visited,recStack):
		# Function: A recursive function uses visited[] and parent to detect
		# cycle in subgraph reachable from vertex v.

		#Mark the current node as visited 
		visited[v]= True
		recStack[v] = True
		#Recur for all the vertices adjacent to this vertex
		for neighbour in self.graph[v]:
			# If the node is not visited then recurse on it
			if visited[neighbour]==False : 
				if(self.__isCyclicUtil(neighbour,visited,recStack)):
					self.cycleTransaction.append(v)
					return True
			# If an adjacent vertex is visited and not parent of current vertex,
			# then there is a cycle
			elif recStack[neighbour] == True:
				self.cycleTransaction.append(v)
				return True
		recStack[v] = False
		return False
	def __isCyclic(self):
		# Mark all the vertices as not visited
		# print(self.graph)
		visited ={}
		recStack = {}
		for key in self.graph.keys():
			visited[key] = False
			recStack[key] = False
		# Call the recursive helper function to detect cycle in different
		#DFS trees
		for node in visited.keys():
			if visited[node] ==False: #Don't recur for u if it is already visited
				if(self.__isCyclicUtil(node,visited,recStack)) == True:
					return True
		
		return False
class DataManager(object):
	'''
	Object: DataManager for each site

	'''
	def __init__(self, index):
		self.status = True 				# true for on false for off
		self.index = index 				# site number
		self.variables = {} 			# store the list of variable in all version 
		self.currentlockTable = {}		# store the lock list for each variable where all locks in this table have being granted
		self.waitlockTable = {} 		# store the lock list for each variable where all locks in this table have to wait
		self.transactionDM = {} 		# store the index of trnsaction that reach this site for each variable, incase duplicate lock
		for i in range(20):
			iNum = i + 1
			if iNum % 2 == 0:
				self.currentlockTable[iNum] = []
				self.waitlockTable[iNum] = []

				self.variables[iNum] = []
				variableTmp = VariableInSite(iNum,global_var.VARIABLE_TYPE_REPLICATE)
				self.variables[iNum].append(variableTmp)
			else: 
				if iNum % 10 + 1 == self.index:
					self.currentlockTable[iNum] = []
					self.waitlockTable[iNum] = []

					self.variables[iNum] = []
					variableTmp = VariableInSite(iNum,global_var.VARIABLE_TYPE_NORMAL)
					self.variables[iNum].append(variableTmp)

		for vl in self.variables.keys():
			for v in self.variables[vl]:
				v.getInfo()
			print()

	def checkLock(self,transactionNum, variableNum, lock):
		# Function: ckeck if the lock is available
		# Input: the transaction number, variable number, lock
		# Output: message
		# 		  return Fail is true if site failed, otherwise false
		# 		  return TNum1 and TNum2 where TNum1 is waiting for TNum2 
		# 		  TNum2 = _ if success or failed
		Fail = False
		TNum1 = transactionNum 	
		TNum2List = []				# list to store the transactions wait for 

		if self.status == False:	# site fail
			Fail = True 
		if lock.locktype == global_var.LOCK_TYPE_READ and not self.variables[variableNum][0].accessible:
			Fail = True
		if not Fail:
			lockResult = lock.lockGranted(self.currentlockTable[variableNum],self.waitlockTable[variableNum])
			if not lockResult:													# need to wait for lock
				#self.waitlockTable[variableNum].append(lock)					# add lock into wait table
				for l in self.currentlockTable[variableNum]:					
					if l.transactionNum not in TNum2List and l.transactionNum != transactionNum:	# add the current locked transactionNum to wait for list
						TNum2List.append(l.transactionNum)
				for l in self.waitlockTable[variableNum]:
					if l.transactionNum not in TNum2List and l.transactionNum != transactionNum:	# add the current locked transactionNum to wait for list
						TNum2List.append(l.transactionNum)
				self.waitlockTable[variableNum].append(lock)										# add lock into wait table
				print("Transaction {2} : {0} lock in site{4} for variable {1}: UNAVAILABLE wait for transaction {3}".format(lock.locktype,variableNum,transactionNum,TNum2List,self.index))
			else:																					# grant lock
				self.currentlockTable[variableNum].append(lock)										# add lock into currentLockTable
				print("Transaction {2} : {0} lock in site{3} for variable {1}: AVAILABLE".format(lock.locktype,variableNum,transactionNum,self.index))
		else:
			print("Transaction {2} : {0} lock in site{3} for variable {1} site FAIL".format(lock.locktype,variableNum,transactionNum,self.index))
		return TNum1, TNum2List, Fail
	def removeLock(self,transactionNum, variableNum, lock):
		# Function: remove lock, change next wait lock's state
		# Input: the transaction number, variable number, lock
		# Output: message
		# 		  return new granted lock for further check

		removeLockList = []
		for l in self.currentlockTable[variableNum]:
			if l == lock:
				removeLockList.append(l)
		for l in removeLockList:
			self.currentlockTable[variableNum].remove(l)
		removeLockList = []
		for l in self.waitlockTable[variableNum]:
			if l == lock:
				removeLockList.append(l)
		for l in removeLockList:
			self.waitlockTable[variableNum].remove(l)
		removeLockList = []
		newGrantedLock = []
		for l in self.waitlockTable[variableNum]:
			lockResult = l.lockGranted(self.currentlockTable[variableNum],[])
			if lockResult:
				removeLockList.append(l) # remove
				self.currentlockTable[variableNum].append(l) # add to currentlocktable
				newGrantedLock.append(l) # return 
				print("Transaction {2} : {0} lock in site {3} for command {1} granted".format(l.locktype,l.commandNum,l.transactionNum,self.index))
			else:
				break
		for l in removeLockList:
			self.waitlockTable[variableNum].remove(l)
		return newGrantedLock
	def fail(self):
		# Function: Fail the site
		# Return new transaction List
		self.status = False
		transactionList = []
		for variableNum in self.currentlockTable.keys():
			for l in self.currentlockTable[variableNum]:
				if l.transactionNum not in transactionList:
					transactionList.append(l.transactionNum)
			self.currentlockTable[variableNum] = []
		for variableNum in self.waitlockTable.keys():
			for l in self.waitlockTable[variableNum]:
				if l.transactionNum not in transactionList:
					transactionList.append(l.transactionNum)
			self.waitlockTable[variableNum] = []
		# abort them if not commit
		for variableNum in self.variables.keys():
			for v in self.variables[variableNum]:
				if v.type == global_var.VARIABLE_TYPE_REPLICATE:
					v.notAccessible()
		return transactionList
	def recover(self):
		# Function: recover the site
		# Output: message
		self.status = True
		print("Site {0} : recover!".format(self.index))
		print()
		return
	def getValue(self,variableNum,commandVersion,transactionType = False, lastCommitedVersion = -1):
		# Function: get read value if accessible
		# Input: variable number, command version
		# Output: message
		# return Fail = false when accessible == false
		# return vTmpValue if transactionType is not readOnly, otherwise return -1

		Fail = False
		if self.status == False:					# if the site is off, fail to read value
			print("Site {1} : cannot get value for variableNum {0} because site fail.".format(self.index, variableNum))
			Fail = True
		vTmpVersion = -1
		vTmpValue = -1
		if not Fail:
			for vTmp in self.variables[variableNum]:
				if vTmp.type == global_var.VARIABLE_TYPE_REPLICATE and vTmp.accessible == False and not transactionType:# if the variable is not accessible, fail to read value
					print("Site {1} : cannot get value for variable {0} because variables in site {1} accessible.".format(variableNum,self.index))
					Fail = True
					break
				if vTmp.version > vTmpVersion and vTmp.version <= commandVersion: # get the value and version of the most recent version
					vTmpValue = vTmp.value
					vTmpVersion = vTmp.version
				elif vTmp.version > vTmpVersion:									
					print("Site {3} : command version{0} access later version {1} with current version {2}".format(commandVersion,vTmp.version,commandVersion,self.index))
		if not Fail:
			print("Site {4} : command with current version {0} read variable {1} version {2} value {3}".format(commandVersion,variableNum,vTmpVersion,vTmpValue,self.index))
		if transactionType and vTmpVersion < lastCommitedVersion:
			print("Site {2} : cannot get value for read only transaction because variable version {0} is update enough for {1}.".format(vTmpVersion,lastCommitedVersion,self.index))
			vTmpValue = -1
			Fail = True
		return vTmpValue, Fail
	def update(self,commandTmp):
		# Function: update the variable value of this site
		# Input: command
		# Output: message
		# return fail = false when accessible == false, otherwise return true
		Fail = False
		if self.status == False:
			Fail = True
		if commandTmp.commandLock not in self.currentlockTable[commandTmp.variableNum]:
			Fail = True
			print ("Site {0} : update for transaction {2} be denied because current site {0} doesn't contain the lock for variable {1}".format(self.index,commandTmp.variableNum,commandTmp.transactionNum))
		commandVersion = commandTmp.index
		variabletype = -1
		if commandTmp.variableNum % 2 == 0:
			variabletype = global_var.VARIABLE_TYPE_REPLICATE
		else:
			variabletype = global_var.VARIABLE_TYPE_NORMAL
		if not Fail:
			variableTmp = VariableInSite(commandTmp.variableNum,variabletype,commandVersion)
			variableTmp.updateValue(commandTmp.value)
			print("Site {0} : update variable {1} to version {2} with value {3}".format(self.index,commandTmp.variableNum,commandVersion,commandTmp.value))
			self.variables[commandTmp.variableNum].append(variableTmp)
			for v in self.variables[commandTmp.variableNum]:		# change variable's accessible 
				if v.accessible == False:
					v.accessible = True
		return Fail

		
		