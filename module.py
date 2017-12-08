from __future__ import print_function
import project 
import status as global_var


'''
# global state 

VARIABLE_TYPE_REPLICATE = "replicated"
VARIABLE_TYPE_NORMAL = "normal"

LOCK_TYPE_READ = "read"
LOCK_TYPE_WRITE = "write"

LOCK_STATUS_INITIALIZE = "initialize"
LOCK_STATUS_GRANTED = "granted"
LOCK_STATUS_WAIT = "wait"
LOCK_STATUS_FAIL = "fail"

TRANSACTION_STATUS_INITIALIZE = "initialize"
TRANSACTION_STATUS_COMMIT = "commit"
TRANSACTION_STATUS_WAIT = "wait"
TRANSACTION_STATUS_WAIT_COMMIT = "wait for commit"
TRANSACTION_STATUS_ABORT = "abort"

COMMAND_STATUS_INITIALIZE = "initialize"
COMMAND_STATUS_SUCCESS = "success"
COMMAND_STATUS_WAIT = "wait"
COMMAND_STATUS_FAIL = "fail"
'''


class VariableInSite(object):
	def __init__(self, index, variabletype, version = 0):
		self.type = variabletype # 0 for replicate and 1 for not
		self.index = index
		self.value = 10 * index # for initialize 
		self.accessible = True # for initialize
		self.version = version # 0 for initialize increase by transaction index 
	def getInfo(self):
		print("Variable {0} with type {1} version {2} and value {3} and accessible {4}".format(self.index,self.type,self.version,self.value,self.accessible))
		return
	def notAccessible(self):
		self.accessible = False
		# print("Variable {0} with type {1} version {2} and value {3} and accessible {4}".format(self.index,self.type,self.version,self.value,self.accessible))
	def updateValue(self,value):
		self.value = value
		self._grantedAccessible()
		# print("variable {0} with type {1} and value {2} updated to version {3}".format(self.index,self.type,self.value,self.version))
	def _grantedAccessible(self):
		if self.accessible == False:
			self.accessible = True
			print("variable {0} is accessible".format(self.index))
	def getInfo(self):
		print("x{0} version {1} = {2}\t".format(self.index,self.version,self.value),end="")

class VariableInCommand(object):
	def __init__(self, index, variabletype, value):
		self.index = index
		self.value = value # none for not read only 
		

class Lock(object):
	def __init__(self, locktype, transactionNum, commandNum):
		self.locktype = locktype 								# read lock, write lock
		self.status = global_var.LOCK_STATUS_INITIALIZE 		# initialize/get/wait
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
	def __init__(self, index, transactionNum, readOnly,currentVariableValue = {}):
		self.index = index # time stamp
		self.name = transactionNum # transaction number 
		self.readOnly = readOnly # true or false
		self.commandlist = {} # store all command
		# self.waitCommandList = [] # store all wait command
		self.status = -1 # -1 for initialize, 0 for success, 1 for wait, 2 for fail
		self.currentVariableValue = {} # for readOnly
		self.commandNum = 0 # initialized with 0 
		self.lastCommitedVersion = 0
	def addCommand(self,command):
		self.commandlist[command.commandNum] = command
		self.commandNum = self.commandNum + 1
	def getNexCommandNum(self):
		return self.commandNum
	def setLastCommitedVersion(self,lastCommitedVersion):
		self.lastCommitedVersion = lastCommitedVersion
	'''def addWaitCommand(self,command):
		# append
		self.waitCommandList.append(command)'''

class Command(object):
	def __init__(self, index, commandtype, transactionNum, variableNum, value, commandNum):
		self.index = index # time stamp
		self.commandtype = commandtype # 1 for read, 2 for write
		self.transactionNum = transactionNum 
		self.variableNum = variableNum
		self.value = value # none for read
		self.status = global_var.COMMAND_STATUS_INITIALIZE # -1 for initialize, 0 for success, 1 for wait, 2 for fail 
		self.commandNum = commandNum
		self.lockGrantedNum = 0
		if variableNum % 2 == 0:
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
	def __init__(self):
		self.index = 0
		self.graph = {}
		self.waitcommittransaction = []
		self.waitCommandList = []
		self.cycleTransaction = []
		self.lastCommitedVersion = 0
	def begin(self,transactionNum):
																	# input is the number of transaction
		transTmp = Transaction(self.index, transactionNum, False)	# create transaction
		self.index = self.index + 1									# add index
		global_var.TransactionList[transactionNum] = transTmp		# append to transactionList
		self.__addVertex(transactionNum)							# add vertex to graph
																	# return nothing
		print("Transaction {} : begin.".format(transactionNum))
		print()
		return

	def write(self,transactionNum, variableNum, variableValue):

		success = True
		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_ABORT:
			print("Transaction {0} : abort and will not execute any command".format(transactionNum))
			return False
		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_WAIT:
			# add command to wait list directly
			self.waitCommandList.append(['W',transactionNum,variableNum,variableValue])
			print("Transaction {0} : command will wait since former command in transaction {0} doesn't finish".format(transactionNum))
			print("Current wait list:".format(self.waitCommandList))
			return False

		commandNum = global_var.TransactionList[transactionNum].getNexCommandNum()					# get command number
		commandLock = Lock(global_var.LOCK_TYPE_WRITE,transactionNum,commandNum)					# create a lock 
		commandTmp = Command(self.index, 2, transactionNum, variableNum, variableValue,commandNum)	# create command object
		
		siteList = global_var.VariableSiteList[variableNum]			# get site list
		result_success = False
		result_wait =False
		result_fail = False
		for i in siteList:											# go through list and checkLock()
			print("Transaction {0} : check lock from site {1}".format(transactionNum, i))
			TNum1, TNum2List, Fail = global_var.DataManagerList[i].checkLock(transactionNum,variableNum,commandLock)

			if not Fail and len(TNum2List) <= 0:					#if success(not fail and no wait)
				result_success = True
				commandTmp.lockGrantedNum = commandTmp.lockGrantedNum + 1
			if not Fail and len(TNum2List) > 0:						# if not fail but wait for lock
				self.__addEdge(transactionNum,TNum2List) 			# add edge in graph
				result_wait = True
			if Fail:												# if fail to get lock
				result_fail = True
				commandTmp.lockRequiredNum = commandTmp.lockRequiredNum - 1
		print (commandLock)
		if result_success and not result_wait and not result_fail:  # If success in all site in siteList
			commandTmp.putLock(commandLock)
			global_var.TransactionList[transactionNum].currentVariableValue[variableNum] = variableValue # add variable to transaction
			print(global_var.TransactionList[transactionNum].name)
			print(transactionNum,global_var.TransactionList[transactionNum].currentVariableValue)
			commandTmp.status = global_var.COMMAND_STATUS_SUCCESS
			print("Transaction {0} : lock check granted".format(transactionNum))

		elif not result_success and result_wait and not result_fail:# If wait
			commandTmp.putLock(commandLock)
			commandTmp.status = global_var.COMMAND_STATUS_WAIT
			print("Transaction {0} : lock check waited".format(transactionNum))

		elif result_success and not result_wait and result_fail:    # If success but some sites failed
			commandTmp.putLock(commandLock)
			global_var.TransactionList[transactionNum].currentVariableValue[variableNum] = variableValue
			print(transactionNum,global_var.TransactionList[transactionNum].currentVariableValue)
			commandTmp.status = global_var.COMMAND_STATUS_SUCCESS
			print("Transaction {0} : lock check granted but some site failed".format(transactionNum))

		elif not result_success and result_wait and result_fail:	# If wait but some sites failed
			commandTmp.putLock(commandLock)
			commandTmp.status = global_var.COMMAND_STATUS_WAIT
			print("Transaction {0} : lock check wait and some site failed".format(transactionNum))

		elif not result_success and not result_wait and result_fail:# If all sites failed
			# change transaction's status to wait / add to wait list
			global_var.TransactionList[transactionNum].status = global_var.TRANSACTION_STATUS_WAIT
			global_var.TransactionList[transactionNum].addWaitCommand(['W',transactionNum,variableNum,variableValue])
			print("Transaction {0} : lock check wait and command add to transaction {0} wait list".format(transactionNum))
			print("Current wait list:".format(self.waitCommandList))
			success = False
			return False
		else:
			commandTmp.putLock(commandLock)
			commandTmp.status = global_var.COMMAND_STATUS_WAIT
			print("this situation happened because inconsistent but wait")
	
		global_var.TransactionList[transactionNum].addCommand(commandTmp)

		self.index = self.index + 1
		# deadlock detect
		print("Transaction {0} : want to write to variable {1} with value {2}.".format(transactionNum,variableNum,variableValue))
		self.__deadLock()
		return success
	def readCommand(self,transactionNum,variableNum):
		success = True
		if global_var.TransactionList[transactionNum].readOnly:
			success = self.readRO(transactionNum,variableNum)
		else:
			success = self.read(transactionNum,variableNum)
		return success
	def readRO(self,transactionNum,variableNum):
		# same index as transaction
		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_ABORT:
			print("Transaction {0} : abort and will not execute any command".format(transactionNum))
			return False
		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_WAIT:
			# add command to wait list directly
			self.waitCommandList.append(['R',transactionNum,variableNum])
			print("Transaction {0} : command will wait since former command in transaction {0} doesn't finish".format(transactionNum))
			print("Current wait list:".format(self.waitCommandList))
			return False
		success = True

		commandIndex = global_var.TransactionList[transactionNum].index
		commandNum = global_var.TransactionList[transactionNum].getNexCommandNum()
		commandTmp = Command(commandIndex, 1, transactionNum, variableNum, -1,commandNum)# create command object 

		siteList = global_var.VariableSiteList[variableNum] # get site list
		result_success = False
		result_wait =False
		result_fail = False
		readResult = -1
		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_WAIT:
			# commandTmp.status = global_var.COMMAND_STATUS_WAIT
			global_var.TransactionList[transactionNum].addCommand(commandTmp)
			print("Transaction {1} : command {0} for read only transaction {1} wait because have previous wait command".format(commandNum,transactionNum))
			return
		for i in siteList:# go through list and checkLock()
			# no need to check lock
			print("Transaction {0} : check value from site {1}".format(transactionNum, i))
			readResultTmp,readResultFail = global_var.DataManagerList[i].getValue(variableNum,commandTmp.index,True,global_var.TransactionList[transactionNum].lastCommitedVersion)
			if not readResultFail: 
				# may caused because site just recover and unaccisable 
				readResult = readResultTmp
				result_success = True
				break
			else:
				result_fail = True
		if result_success and not result_wait and not result_fail:
			# get the latest version of 
			commandTmp.putResult(readResult)
			commandTmp.status = global_var.COMMAND_STATUS_SUCCESS	
			global_var.TransactionList[transactionNum].addCommand(commandTmp)
		elif result_success and not result_wait and result_fail:
			# success but some site fail
			commandTmp.putResult(readResult)
			commandTmp.status = global_var.COMMAND_STATUS_SUCCESS
			global_var.TransactionList[transactionNum].addCommand(commandTmp)
		elif not result_success and not result_wait and result_fail:
			# all fail
			commandTmp.status = global_var.COMMAND_STATUS_WAIT
			global_var.TransactionList[transactionNum].status = global_var.TRANSACTION_STATUS_WAIT
			self.waitCommandList.append(['R',transactionNum,variableNum])
			print("Transaction {0} : lock check wait and command add to transaction {0} wait list".format(transactionNum))
			print("Current wait list {}:".format(self.waitCommandList))
			success = False
		print("Read only Transaction {0} : want to read to variable {1} with value {2}".format(transactionNum,variableNum,commandTmp.value))
		return success
	def read(self,transactionNum, variableNum):

		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_ABORT:
			print("Transaction {0} : abort and will not execute any command".format(transactionNum))
			return False
		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_WAIT:
			# add command to wait list directly
			self.waitCommandList.append(['R',transactionNum,variableNum])
			print("Transaction {0} : command will wait since former command in transaction {0} doesn't finish".format(transactionNum))
			print("Current wait list:".format(self.waitCommandList))
			return False
		success = True
		commandNum = global_var.TransactionList[transactionNum].getNexCommandNum()     				# get command number
		commandLock = Lock(global_var.LOCK_TYPE_READ,transactionNum,commandNum)		   				# create a lock 
		commandTmp = Command(self.index, 1, transactionNum, variableNum, -1,commandNum)				# create command object 
		
		siteList = global_var.VariableSiteList[variableNum]# get site list
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
					print(readResult)
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
			print("Transaction {0} : lock check granted".format(transactionNum))
		elif not result_success and result_wait and not result_fail:			# If wait
			commandTmp.putLock(commandLock)
			commandTmp.status = global_var.COMMAND_STATUS_WAIT
			print("Transaction {0} : lock check waited".format(transactionNum))
		elif result_success and not result_wait and result_fail:				# If success but some sites failed
			commandLock.status = global_var.LOCK_STATUS_GRANTED
			commandTmp.putLock(commandLock)
			if variableNum in global_var.TransactionList[transactionNum].currentVariableValue.keys(): # if write command before in same transaction
				readResult = global_var.TransactionList[transactionNum].currentVariableValue[variableNum] # read the value this transaction wrote
			commandTmp.putResult(readResult)
			commandTmp.status = global_var.COMMAND_STATUS_SUCCESS
			print("Transaction {0} : lock check granted but some site failed".format(transactionNum))
		elif not result_success and result_wait and result_fail:				# If wait but some sites failed
			commandTmp.putLock(commandLock)
			commandTmp.status = global_var.COMMAND_STATUS_WAIT
			print("Transaction {0} : lock check waited but some site failed".format(transactionNum))
		elif not result_success and not result_wait and result_fail:			# If all sites failed
			global_var.TransactionList[transactionNum].status = global_var.TRANSACTION_STATUS_WAIT
			self.waitCommandList.append(['R',transactionNum,variableNum])
			print("Transaction {0} : lock check wait and command add to transaction {0} wait list".format(transactionNum))
			print("Current wait list:".format(self.waitCommandList))
			success =False
			return False
		else:
			print("this situation happened because inconsistent")
		
		global_var.TransactionList[transactionNum].addCommand(commandTmp)
		self.index = self.index + 1
		# deadlock detect
		self.__deadLock()
		print("Transaction {0} : want to read to variable {1} with value {2}.".format(transactionNum,variableNum,commandTmp.value))
		return success
	def endCommand(self,transactionNum):
		if global_var.TransactionList[transactionNum].readOnly:
			self.endRO(transactionNum)
		else:
			self.end(transactionNum)

	def endRO(self,transactionNum):

		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_ABORT:
			print("Transaction {0} : abort and will not execute any command".format(transactionNum))
			return False
		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_WAIT:
			# add command to wait list directly
			self.waitCommandList.append(['end',transactionNum])
			print("Transaction {0} : command will wait since former command in transaction {0} doesn't finish".format(transactionNum))
			print("Current wait list:".format(self.waitCommandList))
			return False
		print()
		validate = True
		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_ABORT:
			validate = False
		for commandNum in global_var.TransactionList[transactionNum].commandlist:
			commandTmp = global_var.TransactionList[transactionNum].commandlist[commandNum]
			if commandTmp.status != global_var.COMMAND_STATUS_SUCCESS:
				validate = False
				break
		if validate:
			global_var.TransactionList[transactionNum].status = global_var.TRANSACTION_STATUS_COMMIT
			print("Transaction {0} : commit".format(transactionNum))
		else:
			if global_var.TransactionList[transactionNum].status != global_var.TRANSACTION_STATUS_ABORT:
				global_var.TransactionList[transactionNum].status = global_var.TRANSACTION_STATUS_WAIT_COMMIT
				if transactionNum not in self.waitcommittransaction:
					self.waitcommittransaction.append(transactionNum)
				print("Transaction {0} : wait for commit".format(transactionNum))
			else:
				print("Transaction {0} : abort".format(transactionNum))
		return True

	def end(self,transactionNum):
		# check all command's status
		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_ABORT:
			print("Transaction {0} : abort and will not execute any command".format(transactionNum))
			return False
		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_WAIT:
			# add command to wait list directly
			self.waitCommandList.append(['end',transactionNum])
			print("Transaction {0} : command will wait since former command in transaction {0} doesn't finish".format(transactionNum))
			print("Current wait list:".format(self.waitCommandList))
			return False
		print()
		validate = True
		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_ABORT:
			validate = False
		for commandNum in global_var.TransactionList[transactionNum].commandlist:
			commandTmp = global_var.TransactionList[transactionNum].commandlist[commandNum]
			if commandTmp.status != global_var.COMMAND_STATUS_SUCCESS:
				validate = False
				print (commandTmp.index,commandTmp.commandtype,commandTmp.variableNum,commandTmp.status)
				break
		newGrantedLockList = []
		if validate:
			# safe to commit
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
			print("Transaction {0} : commit".format(transactionNum))

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
			print(self.waitCommandList)
		else:
			# change status, put in wait list
			if global_var.TransactionList[transactionNum].status != global_var.TRANSACTION_STATUS_ABORT:
				global_var.TransactionList[transactionNum].status = global_var.TRANSACTION_STATUS_WAIT_COMMIT
				if transactionNum not in self.waitcommittransaction:
					self.waitcommittransaction.append(transactionNum)
				print("Transaction {0} : wait for commit".format(transactionNum))
			else:
				print("Transaction {0} : abort".format(transactionNum))
		return True

	def recover(self,datamanagerNum):
		global_var.DataManagerList[datamanagerNum].recover()
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
		print(self.waitCommandList)
		return

	def fail(self,datamanagerNum):
		print("site {} fail".format(datamanagerNum))
		transactionList = global_var.DataManagerList[datamanagerNum].fail()
		for t in transactionList:
			if global_var.TransactionList[t].status != global_var.TRANSACTION_STATUS_COMMIT:
				global_var.TransactionList[t].status = global_var.TRANSACTION_STATUS_ABORT
				print("Transaction {0} : abort because site {1} recover".format(t,datamanagerNum))
				self.__abort(t)
		# may cause waitted command continue 
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
		print(self.waitCommandList)

		# check whether contains any readonly transaction 
		'''newChangedTransaction = []
		for t in global_var.TransactionList:
			if global_var.TransactionList[t].readOnly:
				for commandNum in global_var.TransactionList[t].commandlist:
					commandTmp = global_var.TransactionList[t].commandlist[commandNum]
					if commandTmp.status == global_var.COMMAND_STATUS_WAIT:
						siteList = global_var.VariableSiteList[commandTmp.variableNum] # get site list
						result_success = False
						result_wait =False
						result_fail = False
						readResult = -1
						for i in siteList:# go through list and checkLock()
							# no need to check lock
							result_success = True
							readResultTmp,readResultFail = global_var.DataManagerList[i].getValue(commandTmp.variableNum,commandTmp.index)
							if not readResultFail: 
								# may caused because site just recover and unaccisable 
								readResult = readResultTmp
								result_success = True
							else:
								result_fail = True

						if result_success and not result_wait and not result_fail:
							# get the latest version of 
							commandTmp.putResult(readResult)
							commandTmp.status = global_var.COMMAND_STATUS_SUCCESS
							if commandTmp.transactionNum not in newChangedTransaction:
								newChangedTransaction.append(commandTmp.transactionNum)
						elif result_success and not result_wait and result_fail:
							# success but some site fail
							commandTmp.putResult(readResult)
							commandTmp.status = global_var.COMMAND_STATUS_SUCCESS
							if commandTmp.transactionNum not in newChangedTransaction:
								newChangedTransaction.append(commandTmp.transactionNum)
						elif not result_success and not result_wait and result_fail:
							# all fail
							commandTmp.status = global_var.COMMAND_STATUS_WAIT
							print("lock wait because all sites failed")
						print("Read only command want to read to variable {0} with value {1}".format(commandTmp.variableNum,commandTmp.value))
		for t in newChangedTransaction:
			if global_var.TransactionList[t].readOnly and t in self.waitcommittransaction:
				self.endRO(t)'''
		return

	def beginRO(self,transactionNum):
		# input is the number of transaction
		transTmp = Transaction(self.index, transactionNum, True)# create transaction
		transTmp.setLastCommitedVersion(self.lastCommitedVersion)
		print("readOnly transaction's will not able to read version larger than",transTmp.lastCommitedVersion)
		self.index = self.index + 1# add index
		global_var.TransactionList[transactionNum] = transTmp# append to transactionList
		self.__addVertex(transactionNum)# add vertex to graph
		# return nothing
		print("Read only Transaction {} : begin.".format(transactionNum))
		return

	def dumpCommand(self,datamanagerNum = -1,variableNum = -1):
		if datamanagerNum != -1:
			self.dump2(datamanagerNum)
		elif variableNum != -1:
			self.dump3(variableNum)
		else:
			self.dump1()

	def dump1(self):
		for i in global_var.DataManagerList:
			print()
			print("Site {}".format(i))
			for var in global_var.DataManagerList[i].variables.keys():
				print()
				for varVersion in global_var.DataManagerList[i].variables[var]:
					varVersion.getInfo()
			print()
		return

	def dump2(self, datamanagerNum):

		print("Site {}".format(datamanagerNum))
		for var in global_var.DataManagerList[datamanagerNum].variables.keys():
			print()
			for varVersion in global_var.DataManagerList[datamanagerNum].variables[var]:
				varVersion.getInfo()
		print()
		return

	def dump3(self, variableNum):
		for i in global_var.DataManagerList:
			print()
			print("Site {}".format(i))
			for varVersion in global_var.DataManagerList[i].variables[variableNum]:
				varVersion.getInfo()
			print()
		return

	def abort_test(self,transactionNum):
		# a test of using abort, since still miss dealock detection
		global_var.TransactionList[transactionNum].status = global_var.TRANSACTION_STATUS_ABORT
		self.__abort(transactionNum)
	def __abort(self,transactionNum):
		# call when abort happend 
		# print()
		print("transaction {0} abort".format(transactionNum))
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
		self.graph[transactionNum] = []
		return
	def __addEdge(self,transactionNum1,transactionNum2):
		print(transactionNum1,transactionNum2)
		print(self.graph)
		for i in transactionNum2:
			if i not in self.graph[transactionNum1]:
				self.graph[transactionNum1].append(i)
		print("current graph {}".format(self.graph))
		return
	def __deleteVertex(self,transactionNum):
		self.graph.pop(transactionNum,None)
		for key in self.graph.keys():
			if transactionNum in self.graph[key]:
				self.graph[key].remove(transactionNum)
		print("current graph {}".format(self.graph))
		return
	def deadLock_test(self):
		self.graph[1] = []
		self.graph[2] = []
		self.graph[3] = [2]
		print (self.__isCyclic())
		print (self.cycleTransaction)
	def __deadLock(self):
		self.cycleTransaction = []
		cycle = self.__isCyclic()
		youngest = None
		for t in self.cycleTransaction:
			if youngest == None or global_var.TransactionList[youngest].index < global_var.TransactionList[t].index:
				youngest = t
		if cycle and youngest != None:
			print()
			print(self.cycleTransaction)
			print ("Transaction {} : Abort youngest transaction".format(youngest))
			self.__abort(youngest)
			self.__deadLock()

		return
	# A recursive function that uses visited[] and parent to detect
	# cycle in subgraph reachable from vertex v.
	def __isCyclicUtil(self,v,visited,recStack):
		#Mark the current node as visited 
		visited[v]= True
		recStack[v] = True
		# print("visited {}".format(v))
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
				# print ("recStack {}".format(v))
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
	"""docstring for DataManager"""
	def __init__(self, index):
		self.status = True # true for on false for off
		self.index = index # site number
		self.variables = {} # store the list of variable in all version 
		self.currentlockTable = {} # store the lock list for each variable where all locks in this table have being granted
		self.waitlockTable = {} # store the lock list for each variable where all locks in this table have to wait
		self.transactionDM = {} # store the index of trnsaction that reach this site for each variable, incase duplicate lock
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
		# get transactionNum
		# return -1 for site failed, 0 for success, 1 for lock conflict, 
		# return TNum1 and TNum2 where TNum1 is waiting for TNum2 
		# return TNum2 = _ if success or failed
		Fail = False
		TNum1 = transactionNum 	
		TNum2List = []				# list to store the transactions wait for 
		#print("site {0} current status {1}".format(self.index,self.status))
		if self.status == False:
			Fail = True # site fail
		if lock.locktype == global_var.LOCK_TYPE_READ and not self.variables[variableNum][0].accessible:
			Fail = True
		if not Fail:
			lockResult = lock.lockGranted(self.currentlockTable[variableNum],self.waitlockTable[variableNum])
			if not lockResult:													# need to wait for lock
				#self.waitlockTable[variableNum].append(lock)					# add lock into wait table
				for l in self.currentlockTable[variableNum]:					
					if l.transactionNum not in TNum2List and l.transactionNum != transactionNum:						# add the current locked transactionNum to wait for list
						TNum2List.append(l.transactionNum)
				for l in self.waitlockTable[variableNum]:
					if l.transactionNum not in TNum2List and l.transactionNum != transactionNum:						# add the current locked transactionNum to wait for list
						TNum2List.append(l.transactionNum)
				self.waitlockTable[variableNum].append(lock)					# add lock into wait table
				print("Transaction {2} : {0} lock in site{4} for variable {1} wait for transaction {3}".format(lock.locktype,variableNum,transactionNum,TNum2List,self.index))
			else:																# grant lock
				self.currentlockTable[variableNum].append(lock)					# add lock into currentLockTable
				print("Transaction {2} : {0} lock in site{3} for variable {1} succeed".format(lock.locktype,variableNum,transactionNum,self.index))
		else:
			print("Transaction {2} : {0} lock in site{3} for variable {1} site failed".format(lock.locktype,variableNum,transactionNum,self.index))
		return TNum1, TNum2List, Fail
	def removeLock(self,transactionNum, variableNum, lock):
		# remove lock, change next wait lock's state
		# remove edge// not needed since the whole vertex will be remove 
		# return new granted lock for further check
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
		# print(self.currentlockTable,self.waitlockTable,self.variables) 
		return transactionList
	def recover(self):
		# clear lock table, remove lock, change transaction status, change variable's accessible
		# find all transaction that reach this site
		self.status = True
		print("Site {0} : recover".format(self.index))
		return
	def getValue(self,variableNum,commandVersion,transactionType = False, lastCommitedVersion = -1):
		# return -1 when accessible == false, return value if transactionType is not readOnly
		# return the latest version which version less than transactionVersion
		# if not 
		Fail = False
		if self.status == False:					# if the site is off, fail to read value
			print("cannot get value for variableNum {0} because site fail.".format(variableNum))
			Fail = True
		vTmpVersion = -1
		vTmpValue = -1
		if not Fail:
			for vTmp in self.variables[variableNum]:
				if vTmp.type == global_var.VARIABLE_TYPE_REPLICATE and vTmp.accessible == False and not transactionType:		# if the variable is not accessible, fail to read value
					print("cannot get value for variable {0} because variables in site {1} accessible.".format(variableNum,self.index))
					Fail = True
					break
				if vTmp.version > vTmpVersion and vTmp.version <= commandVersion: # get the value and version of the most recent version
					vTmpValue = vTmp.value
					vTmpVersion = vTmp.version
				elif vTmp.version > vTmpVersion:									
					print("command version{0} access later version {1} with current version {2}".format(commandVersion,vTmp.version,commandVersion))
		if not Fail:
			print("command with current version {0} read variable {1} version {2} value {3}".format(commandVersion,variableNum,vTmpVersion,vTmpValue))
		if transactionType and vTmpVersion < lastCommitedVersion:
			print("cannot get value for read only transaction because variable version {0} is update enough for {1}.".format(vTmpVersion,lastCommitedVersion))
			vTmpValue = -1
			Fail = True
		print(vTmpValue,Fail)
		return vTmpValue, Fail
	def update(self,commandTmp):
		# return -1 when accessible == false, return 1 if success add new version 
		# change variable's accessible 
		Fail = False
		if self.status == False:
			Fail = True
		if commandTmp.commandLock not in self.currentlockTable[commandTmp.variableNum]:
			Fail = True
			print ("update for transaction {2} be denied because current site {0} doesn't contain the lock for variable {1}".format(self.index,commandTmp.variableNum,commandTmp.transactionNum))
		commandVersion = commandTmp.index
		variabletype = -1
		if commandTmp.variableNum % 2 == 0:
			variabletype = global_var.VARIABLE_TYPE_REPLICATE
		else:
			variabletype = global_var.VARIABLE_TYPE_NORMAL
		if not Fail:
			variableTmp = VariableInSite(commandTmp.variableNum,variabletype,commandVersion)
			variableTmp.updateValue(commandTmp.value)
			print("site {0} update variable {1} to version {2} with value {3}".format(self.index,commandTmp.variableNum,commandVersion,commandTmp.value))
			self.variables[commandTmp.variableNum].append(variableTmp)
			for v in self.variables[commandTmp.variableNum]:
				if v.accessible == False:
					v.accessible = True
		return Fail

		
		