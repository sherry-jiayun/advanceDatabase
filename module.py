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
		print("variable {0} with type {1} and value {2} updated to version {3}".format(self.index,self.type,self.value,self.version))
	def _grantedAccessible(self):
		if self.accessible == False:
			self.accessible = True
			print("variable {0} is accessible".format(self.index))

class VariableInCommand(object):
	def __init__(self, index, variabletype, value):
		self.index = index
		self.value = value # none for not read only 
		

class Lock(object):
	def __init__(self, locktype, transactionNum, commandNum):
		self.locktype = locktype # read lock, write lock
		self.status = global_var.LOCK_STATUS_INITIALIZE # -1 for initialize, 0 for get and 1 for wait
		self.transactionNum = transactionNum # may drop transactionList in DM
		self.commandNum = commandNum
	def lockGranted(self, currentLockList, waitLockList):
		granted = True
		if self.locktype == global_var.LOCK_TYPE_WRITE:
			for l in currentLockList:
				if l.transactionNum != self.transactionNum:
					granted = False
					break 
		if self.locktype == global_var.LOCK_TYPE_READ:
			for l in currentLockList:
				if l.locktype == global_var.LOCK_TYPE_WRITE and l.transactionNum != self.transactionNum:
					granted = False
					break
				if l.locktype == global_var.LOCK_TYPE_WRITE and l.transactionNum != self.transactionNum:
					granted = False
					break
			for l in waitLockList:
				if l.locktype == global_var.LOCK_TYPE_WRITE and l.transactionNum == self.transactionNum:
					granted = False
					break
		return granted


class Transaction(object):
	def __init__(self, index, transactionNum, readOnly,currentVariableValue = {}):
		self.index = index # time stamp
		self.name = transactionNum # transaction number 
		self.readOnly = readOnly # true or false
		self.commandlist = {} # store all command
		self.status = -1 # -1 for initialize, 0 for success, 1 for wait, 2 for fail
		self.currentVariableValue = currentVariableValue # for readOnly
		self.commandNum = 0 # initialized with 0 
	def addCommand(self,command):
		self.commandlist[command.commandNum] = command
		self.commandNum = self.commandNum + 1
	def getNexCommandNum(self):
		return self.commandNum


class Command(object):
	def __init__(self, index, commandtype, transactionNum, variableNum, value, commandNum):
		self.index = index # time stamp
		self.commandtype = commandtype # 1 for read, 2 for write
		self.transactionNum = transactionNum 
		self.variableNum = variableNum
		self.value = value # none for read
		self.status = global_var.COMMAND_STATUS_INITIALIZE # -1 for initialize, 0 for success, 1 for wait, 2 for fail 
		self.commandNum = commandNum
		print("create write command with commandNum {0} in transaction {1}".format(self.commandNum,self.transactionNum))
	def putLock(self,commandLock):
		self.commandLock = commandLock
	def putResult(self,value):
		self.value = value

class TransactionMachine(object):
	def __init__(self):
		self.index = 0
		self.graph = {}
		self.waitcommittransaction = []
		self.cycleTransaction = []
	def begin(self,transactionNum):
		# input is the number of transaction
		transTmp = Transaction(self.index, transactionNum, False)# create transaction
		self.index = self.index + 1# add index
		global_var.TransactionList[transactionNum] = transTmp# append to transactionList
		self.__addVertex(transactionNum)# add vertex to graph
		# return nothing
		print("Transaction {} begin.".format(transactionNum))
		return

	def write(self,transactionNum, variableNum, variableValue):

		commandNum = global_var.TransactionList[transactionNum].getNexCommandNum()
		commandLock = Lock(global_var.LOCK_TYPE_WRITE,transactionNum,commandNum)
		commandTmp = Command(self.index, 2, transactionNum, variableNum, variableValue,commandNum)# create command object 
		'''if 'variableNum' not in global_var.VariableSiteList.keys():# check if variable legal, if not change transaction's status to fail directly
			global_var.TransactionList[transactionNum].status = global_var.TRANSACTION_STATUS_ABORT
			print("variable not exist, transaction {0} abort.".format(transactionNum))
			# abort now? '''
		
		siteList = global_var.VariableSiteList[variableNum]# get site list
		result_success = False
		result_wait =False
		result_fail = False
		for i in siteList:# go through list and checkLock()
			print("chack lock from site {}".format(i))
			TNum1, TNum2List, Fail = global_var.DataManagerList[i].checkLock(transactionNum,variableNum,commandLock)
			# print(TNum2List, Fail)
			# if result contains wait, change command's status to wait and add edges
			if not Fail and len(TNum2List) <= 0:
				# not fail and wait no transaction
				result_success = True
			if not Fail and len(TNum2List) > 0:
				# not fail but wait
				self.__addEdge(transactionNum,TNum2List) # add edge
				result_wait = True
			if Fail:
				# site fail
				result_fail = True
				commandLock.status = global_var.LOCK_STATUS_FAIL
			# if result contains only success or fail and success > 0, change command's status to success
			# situation? site fail write wait, site recovery, what should write do?
		if result_success and not result_wait and not result_fail:
			# success 
			commandLock.status = global_var.LOCK_STATUS_GRANTED
			commandTmp.putLock(commandLock)
			# add variable to transaction
			global_var.TransactionList[transactionNum].currentVariableValue[variableNum] = variableValue
			commandTmp.status = global_var.COMMAND_STATUS_SUCCESS
		elif not result_success and result_wait and not result_fail:
			# wait
			commandLock.status = global_var.LOCK_STATUS_WAIT
			commandTmp.putLock(commandLock)
			commandTmp.status = global_var.COMMAND_STATUS_WAIT
		elif result_success and not result_wait and result_fail:
			# success but some site fail
			commandLock.status = global_var.LOCK_STATUS_GRANTED
			commandTmp.putLock(commandLock)
			global_var.TransactionList[transactionNum].currentVariableValue[variableNum] = variableValue
			commandTmp.status = global_var.COMMAND_STATUS_SUCCESS
			print("lock check granted but some site failed")
		elif not result_success and result_wait and result_fail:
			# wait but some site fail
			commandLock.status = global_var.LOCK_STATUS_WAIT
			commandTmp.putLock(commandLock)
			commandTmp.status = global_var.COMMAND_STATUS_WAIT
			print("lock check wait and some site failed")
		elif not result_success and not result_wait and result_fail:
			# all fail
			commandLock.status = global_var.LOCK_STATUS_WAIT
			commandTmp.putLock(commandLock)
			commandTmp.status = global_var.COMMAND_STATUS_WAIT
			print("lock wait because all sites failed")
		else:
			print("but situation happend because unconsistent")
		
		global_var.TransactionList[transactionNum].addCommand(commandTmp)
		self.index = self.index + 1
		# deadlock detect
		print("Transaction {0} want to write to variable {1} with value {2} granted? {3}".format(transactionNum,variableNum,variableValue,commandLock.status))
		self.__deadLock()
		return
	def readCommand(self,transactionNum,variableNum):
		if global_var.TransactionList[transactionNum].readOnly:
			self.readRO(transactionNum,variableNum)
		else:
			self.read(transactionNum,variableNum)
	def readRO(self,transactionNum,variableNum):
		# same index as transaction
		commandIndex = global_var.TransactionList[transactionNum].index
		commandNum = global_var.TransactionList[transactionNum].getNexCommandNum()
		commandTmp = Command(commandIndex, 1, transactionNum, variableNum, -1,commandNum)# create command object 

		'''if 'variableNum' not in global_var.VariableSiteList.keys():# check if variable legal, if not change transaction's status to fail directly
			global_var.TransactionList[transactionNum].status = global_var.TRANSACTION_STATUS_ABORT
			print("variable not exist, transaction {0} abort.".format(transactionNum))
			# abort now? '''

		siteList = global_var.VariableSiteList[variableNum] # get site list
		result_success = False
		result_wait =False
		result_fail = False
		readResult = -1
		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_WAIT:
			commandTmp.status = global_var.COMMAND_STATUS_WAIT
			global_var.TransactionList[transactionNum].addCommand(commandTmp)
			print("command {0} for read only transaction {1} wait because have previous wait command".format(commandNum,transactionNum))
			return
		for i in siteList:# go through list and checkLock()
			# no need to check lock
			readResultTmp,readResultFail = global_var.DataManagerList[i].getValue(variableNum,commandTmp.index)
			if not readResultFail: 
				# may caused because site just recover and unaccisable 
				readResult = readResultTmp
				result_success = True
			else:
				result_fail = True
		print(result_success,result_wait,result_fail)
		if result_success and not result_wait and not result_fail:
			# get the latest version of 
			commandTmp.putResult(readResult)
			commandTmp.status = global_var.COMMAND_STATUS_SUCCESS	
		elif result_success and not result_wait and result_fail:
			# success but some site fail
			commandTmp.putResult(readResult)
			commandTmp.status = global_var.COMMAND_STATUS_SUCCESS
		elif not result_success and not result_wait and result_fail:
			# all fail
			commandTmp.status = global_var.COMMAND_STATUS_WAIT
			global_var.TransactionList[transactionNum].status = global_var.TRANSACTION_STATUS_WAIT
			print("lock wait because all sites failed change the whole transaction's status")
		global_var.TransactionList[transactionNum].addCommand(commandTmp)
		print("Read only Transaction {0} want to read to variable {1} with value {2}".format(transactionNum,variableNum,commandTmp.value))
	def read(self,transactionNum, variableNum):
		# create command object
		# check if variable legal, if not change transaction's status to fail directly
		# get site list
		commandNum = global_var.TransactionList[transactionNum].getNexCommandNum()
		commandLock = Lock(global_var.LOCK_TYPE_READ,transactionNum,commandNum)
		commandTmp = Command(self.index, 1, transactionNum, variableNum, -1,commandNum)# create command object 

		'''if 'variableNum' not in global_var.VariableSiteList.keys():# check if variable legal, if not change transaction's status to fail directly
			global_var.TransactionList[transactionNum].status = global_var.TRANSACTION_STATUS_ABORT
			print("variable not exist, transaction {0} abort.".format(transactionNum))
			# abort now? '''
		
		siteList = global_var.VariableSiteList[variableNum]# get site list
		result_success = False
		result_wait =False
		result_fail = False
		readResult = -1
		for i in siteList:# go through list and checkLock()
			print("chack lock from site {}".format(i))
			TNum1, TNum2List, Fail = global_var.DataManagerList[i].checkLock(transactionNum,variableNum,commandLock)
			# if result contains wait, change command's status to wait and add edges
			if not Fail and len(TNum2List) <= 0:
				# not fail and wait no transaction
				result_success = True
				readResultTmp,readResultFail = global_var.DataManagerList[i].getValue(variableNum,commandTmp.index)
				if not readResultFail: 
					# may caused because site just recover and unaccisable 
					readResult = readResultTmp
			if not Fail and len(TNum2List) > 0:
				# not fail but wait
				self.__addEdge(transactionNum,TNum2List) # add edge
				result_wait = True
			if Fail:
				# site fail
				result_fail = True
				commandLock.status = global_var.LOCK_STATUS_FAIL
			# if result contains only success or fail and success > 0, change command's status to success
			# situation? site fail write wait, site recovery, what should write do?
		if result_success and not result_wait and not result_fail:
			# success 
			commandLock.status = global_var.LOCK_STATUS_GRANTED
			commandTmp.putLock(commandLock)
			# get the latest version of 
			if variableNum in global_var.TransactionList[transactionNum].currentVariableValue.keys():
				# may caused by write command in same transaction
				readResult = global_var.TransactionList[transactionNum].currentVariableValue[variableNum]
			commandTmp.putResult(readResult)
			commandTmp.status = global_var.COMMAND_STATUS_SUCCESS
		elif not result_success and result_wait and not result_fail:
			# wait
			commandLock.status = global_var.LOCK_STATUS_WAIT
			commandTmp.putLock(commandLock)
			commandTmp.status = global_var.COMMAND_STATUS_WAIT
		elif result_success and not result_wait and result_fail:
			# success but some site fail
			commandLock.status = global_var.LOCK_STATUS_GRANTED
			commandTmp.putLock(commandLock)
			if variableNum in global_var.TransactionList[transactionNum].currentVariableValue.keys():
				# may caused by write command in same transaction
				readResult = global_var.TransactionList[transactionNum].currentVariableValue[variableNum]
			commandTmp.putResult(readResult)
			commandTmp.status = global_var.COMMAND_STATUS_SUCCESS
			print("lock check granted but some site failed")
		elif not result_success and result_wait and result_fail:
			# wait but some site fail
			commandLock.status = global_var.LOCK_STATUS_WAIT
			commandTmp.putLock(commandLock)
			commandTmp.status = global_var.COMMAND_STATUS_WAIT
			print("lock check wait and some site failed")
		elif not result_success and not result_wait and result_fail:
			# all fail
			commandLock.status = global_var.LOCK_STATUS_WAIT
			commandTmp.putLock(commandLock)
			commandTmp.status = global_var.COMMAND_STATUS_WAIT
			print("lock wait because all sites failed")
		else:
			print("but situation happend because unconsistent")
		
		global_var.TransactionList[transactionNum].addCommand(commandTmp)
		self.index = self.index + 1
		# deadlock detect
		self.__deadLock()
		print("Transaction {0} want to read to variable {1} with value {2} granted? {3}".format(transactionNum,variableNum,commandTmp.value,commandLock.status))
		return
	def endCommand(self,transactionNum):
		if global_var.TransactionList[transactionNum].readOnly:
			self.endRO(transactionNum)
		else:
			self.end(transactionNum)

	def endRO(self,transactionNum):
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
			print("transaction {0} commit".format(transactionNum))
		else:
			if global_var.TransactionList[transactionNum].status != global_var.TRANSACTION_STATUS_ABORT:
				global_var.TransactionList[transactionNum].status = global_var.TRANSACTION_STATUS_WAIT
				if transactionNum not in self.waitcommittransaction:
					self.waitcommittransaction.append(transactionNum)
				print("transaction {0} wait for commit".format(transactionNum))
			else:
				print("transaction {0} abort".format(transactionNum))


	def end(self,transactionNum):
		# check all command's status
		print()
		validate = True
		if global_var.TransactionList[transactionNum].status == global_var.TRANSACTION_STATUS_ABORT:
			validate = False
		for commandNum in global_var.TransactionList[transactionNum].commandlist:
			commandTmp = global_var.TransactionList[transactionNum].commandlist[commandNum]
			if commandTmp.status != global_var.COMMAND_STATUS_SUCCESS:
				validate = False
				break
		newGrantedLockList = []
		if validate:
			# safe to commit
			for commandNum in global_var.TransactionList[transactionNum].commandlist:
				commandTmp = global_var.TransactionList[transactionNum].commandlist[commandNum]
				siteList = global_var.VariableSiteList[commandTmp.variableNum]
				for s in siteList:
					if commandTmp.commandtype == 2:
						Fail = global_var.DataManagerList[s].update(commandTmp)
						# fail may caused by site fail
					# remove lock
					newGrantedLock = global_var.DataManagerList[s].removeLock(transactionNum,commandTmp.variableNum,commandTmp.commandLock)
					for l in newGrantedLock:
						if l not in newGrantedLockList:
							newGrantedLockList.append(l)
			global_var.TransactionList[transactionNum].status = global_var.TRANSACTION_STATUS_COMMIT
			if transactionNum in self.waitcommittransaction:
				self.waitcommittransaction.remove(transactionNum)
			# remove edge from list 
			self.__deleteVertex(transactionNum)
			print("transaction {0} commit".format(transactionNum))

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
					print("read command {0} in transaction {1} success read variable {2} with value {3}".format(commandTmp.commandNum,commandTmp.transactionNum,commandTmp.variableNum,commandTmp.value))
				else:
					global_var.TransactionList[commandTmp.transactionNum].currentVariableValue[commandTmp.variableNum] = commandTmp.value
					print("write command {0} in transaction {1} success read variable {2} with value {3}".format(commandTmp.commandNum,commandTmp.transactionNum,commandTmp.variableNum,commandTmp.value))
				commandTmp.status = global_var.COMMAND_STATUS_SUCCESS
				
				if l.transactionNum not in newChangedTransaction:
					newChangedTransaction.append(l.transactionNum)
			for t in newChangedTransaction:
				if t in self.waitcommittransaction:
					self.end(t)
		else:
			# change status, put in wait list
			if global_var.TransactionList[transactionNum].status != global_var.TRANSACTION_STATUS_ABORT:
				global_var.TransactionList[transactionNum].status = global_var.TRANSACTION_STATUS_WAIT
				if transactionNum not in self.waitcommittransaction:
					self.waitcommittransaction.append(transactionNum)
				print("transaction {0} wait for commit".format(transactionNum))
			else:
				print("transaction {0} abort".format(transactionNum))
		return

	def fail(self,datamanagerNum):
		global_var.DataManagerList[datamanagerNum].fail()
		return

	def recover(self,datamanagerNum):
		transactionList = global_var.DataManagerList[datamanagerNum].recover()
		for t in transactionList:
			if global_var.TransactionList[t].status != global_var.TRANSACTION_STATUS_COMMIT:
				global_var.TransactionList[t].status = global_var.TRANSACTION_STATUS_ABORT
				print("transaction {0} abort because site {1} recover".format(t,datamanagerNum))
				self.__abort(t)
		# check whether contains any readonly transaction 
		newChangedTransaction = []
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
				self.endRO(t)
		return

	def beginRO(self,transactionNum):
		# input is the number of transaction
		transTmp = Transaction(self.index, transactionNum, True)# create transaction
		self.index = self.index + 1# add index
		global_var.TransactionList[transactionNum] = transTmp# append to transactionList
		self.__addVertex(transactionNum)# add vertex to graph
		# return nothing
		print("Read only Transaction {} begin.".format(transactionNum))
		return
	def dump(self):
		for i in global_var.DataManagerList:
			for j in global_var.DataManagerList[i].variables:
				print("Site {0} Variable {1} Value {2}".format(i, j, global_var.DataManagerList[i].variables[j]))
		return
	def dump(self, datamanagerNum):
		for j in global_var.DataManagerList[i][datamanagerNum].variables:
			print("Site {0} Variable {1} Value {2}".format(datamanagerNum, j, global_var.DataManagerList[i][datamanagerNum].variables[j]))
		return
	def dump(self, datamanagerNum, variableNum):
		print("Site {0} Variable {1} Value {2}".format(datamanagerNum, variableNum, global_var.DataManagerList[i][datamanagerNum].variables[variableNum]))
		return
	def abort_test(self,transactionNum):
		# a test of using abort, since still miss dealock detection
		global_var.TransactionList[transactionNum].status = global_var.TRANSACTION_STATUS_ABORT
		self.__abort(transactionNum)
	def __abort(self,transactionNum):
		# call when abort happend 
		print()
		print("transaction {0} abort".format(transactionNum))
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
				print("read command {0} in transaction {1} success read variable {2} with value {3}".format(commandTmp.commandNum,commandTmp.transactionNum,commandTmp.variableNum,commandTmp.value))
			else:
				global_var.TransactionList[commandTmp.transactionNum].currentVariableValue[commandTmp.variableNum] = commandTmp.value
				print("write command {0} in transaction {1} success read variable {2} with value {3}".format(commandTmp.commandNum,commandTmp.transactionNum,commandTmp.variableNum,commandTmp.value))
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
		self.graph[1] = [2]
		self.graph[2] = [3]
		self.graph[3] = [4]
		self.graph[4] = [1]
		print (self.__isCyclic())
		print (self.cycleTransaction)
	def __deadLock(self):
		self.cycleTransaction = []
		print()
		cycle = self.__isCyclic()
		print(self.cycleTransaction)
		youngest = None
		for t in self.cycleTransaction:
			if youngest == None or global_var.TransactionList[youngest].index < global_var.TransactionList[t].index:
				youngest = t
		print ("youngest transaction {}".format(youngest))
		if cycle and youngest != None:
			self.__abort(youngest)
		return
	# A recursive function that uses visited[] and parent to detect
	# cycle in subgraph reachable from vertex v.
	def __isCyclicUtil(self,v,visited,recStack):
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
			elif recStack[v] == True:
				self.cycleTransaction.append(v)
				return True
		recStack[v] = False
		return False
	def __isCyclic(self):
		# Mark all the vertices as not visited
		print(self.graph)
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

	def checkLock(self,transactionNum, variableNum, lock):
		# get transactionNum
		# return -1 for site failed, 0 for success, 1 for lock conflict, 
		# return TNum1 and TNum2 where TNum1 is waiting for TNum2 
		# return TNum2 = _ if success or failed
		Fail = False
		TNum1 = transactionNum
		TNum2List = []

		#print("site {0} current status {1}".format(self.index,self.status))
		if self.status == False:
			Fail = True # site fail
		if not Fail:
			lockResult = lock.lockGranted(self.currentlockTable[variableNum],self.waitlockTable[variableNum])
			if not lockResult:
				# add lock into waittable
				self.waitlockTable[variableNum].append(lock)
				for l in self.currentlockTable[variableNum]:
					if l.transactionNum not in TNum2List:
						TNum2List.append(l.transactionNum)
				# lock.status = global_var.LOCK_STATUS_WAIT
				print("{0} lock for variable {1} from transaction {2} wait for transaction {3}".format(lock.locktype,variableNum,transactionNum,TNum2List))
			else:
				# add lock into currentLockTable
				self.currentlockTable[variableNum].append(lock)
				# lock.status = global_var.LOCK_STATUS_GRANTED
				print("{0} lock for variable {1} from transaction {2} succeed".format(lock.locktype,variableNum,transactionNum))
		else:
			# lock.status = global_var.LOCK_STATUS_FAIL
			print("{0} lock for variable {1} from transaction {2} site failed".format(lock.locktype,variableNum,transactionNum))
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
		newGrantedLock = []
		for l in self.waitlockTable[variableNum]:
			lockResult = l.lockGranted(self.currentlockTable[variableNum],[])
			if lockResult:
				removeLockList.append(l) # remove
				self.currentlockTable[variableNum].append(l) # add to currentlocktable
				newGrantedLock.append(l) # return 
				print("{0} lock for command {1} in transaction {2} granted".format(l.locktype,l.commandNum,l.transactionNum))
			else:
				break
		for l in removeLockList:
			self.waitlockTable[variableNum].remove(l)
		return newGrantedLock
	def fail(self):
		self.status = False 
		print("site {0} failed".format(self.index))
		return
	def recover(self):
		# clear lock table, remove lock, change transaction status, change variable's accessible
		# find all transaction that reach this site
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
		self.status = True
		return transactionList
	def getValue(self,variableNum,commandVersion):
		# return -1 when accessible == false, return value if transactionType is not readOnly
		# return the latest version which version less than transactionVersion
		# if not 
		Fail = False
		if self.status == False:
			print("cannot get value for variable{} because site fail.".format(variableNum))
			Fail = True
		vTmpVersion = -1
		vTmpValue = -1
		if not Fail:
			for vTmp in self.variables[variableNum]:
				if vTmp.accessible == False:
					print("cannot get value for variable {0} because variables in site {1} unaccisable.".format(variableNum,self.index))
					Fail = True
					break
				if vTmp.version > vTmpVersion and vTmp.version <= commandVersion:
					vTmpValue = vTmp.value
					vTmpVersion = vTmp.version
				elif vTmp.version > vTmpVersion:
					print("command version{0} access later version {1} with current version {2}".format(commandVersion,vTmp.version,transactionVersion))
		if not Fail:
			print("command with current version {0} read variable {1} version {2} value {3}".format(commandVersion,variableNum,vTmpVersion,vTmpValue))
		return vTmpValue, Fail
	def update(self,commandTmp):
		# return -1 when accessible == false, return 1 if success add new version 
		# change variable's accessible 
		Fail = False
		if self.status == False:
			Fail = True
		if commandTmp.commandLock not in self.currentlockTable[commandTmp.variableNum]:
			Fail = True
			print ("update be denied because current site {0} doesn't contain the lock for variable {1}".format(self.index,commandTmp.variableNum))
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

		
		