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
		self.value = 10 * index # retun to initialize
		self.accessible = fail
		print("Variable {0} with type {1} version {2} and value {3} and accessible {4}".format(self.index,self.type,self.version,self.value,self.accessible))
	def updateValue(self,value):
		self.value = value
		_grantedAccessible()
		print("variable {0} with type {1} and value {2} updated to version {3}".format(self.index,self.type,self.value,self.version))
	def _grantedAccessible(self):
		if self.accessible == False:
			self.accessible = True
			print("variable {0} is accessible".format(self.index))

class VariableInCommand(object):
	def __init__(self, index, variabletype,value):
		self.type = variabletype
		self.index = index
		self.value = value # none for not read only 
		

class Lock(object):
	def __init__(self, locktype, transactionNum, commandNum):
		self.locktype = locktype # read lock, write lock
		self.status = global_var.LOCK_STATUS_INITIALIZE # -1 for initialize, 0 for get and 1 for wait
		self.transactionNum = transactionNum # may drop transactionList in DM
		self.commandNum = commandNum
	def lockGranted(self, currentLockList):
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
				if l.locktype == project.LOCK_TYPE_WRITE and l.transactionNum != self.transactionNum:
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
	def __init__(self, commandtype, transactionNum, variableNum, value, commandNum):
		self.commandtype = commandtype # 1 for read, 2 for write
		self.transactionNum = transactionNum 
		if variableNum % 2 == 0:
			self.variable = VariableInCommand(variableNum,0,value)
		else:
			self.variable = VariableInCommand(variableNum,1,value)
		self.value = value # none for read
		self.status = global_var.COMMAND_STATUS_INITIALIZE # -1 for initialize, 0 for success, 1 for wait, 2 for fail 
		self.commandNum = commandNum
		
	def putLock(self,commandLock):
		self.commandLock = commandLock

class TransactionMachine(object):
	def __init__(self):
		self.index = 0
		self.graph = {}
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
		commandLock = Lock(global_var.LOCK_TYPE_WRITE,transactionNum,variableNum)
		commandTmp = Command(2, transactionNum, variableNum, variableValue,commandNum)# create command object 

		if 'variableNum' in global_var.VariableSiteList.keys():# check if variable legal, if not change transaction's status to fail directly
			global_var.TransactionList[transactionNum].status = global_var.TRANSACTION_STATUS_ABORT
			print("variable not exist, transaction {0} abort.".format(transactionNum))
			# abort now? 
		
		siteList = global_var.VariableSiteList[variableNum]# get site list
		result_success = False
		result_wait =False
		result_fail = False
		for i in siteList:# go through list and checkLock()
			print("chack lock from site {}".format(i))
			TNum1, TNum2List, Fail = global_var.DataManagerList[i].checkLock(transactionNum,variableNum,commandLock)
			print(TNum2List, Fail)
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
		# deadlock detect
		print("Transaction {0} want to write to variable {1} with value {2} granted? {3}".format(transactionNum,variableNum,variableValue,commandLock.status))
		return

	def read(self,transactionNum, variableNum):
		# create command object
		# check if variable legal, if not change transaction's status to fail directly
		# get site list
		commandTmp = Command()
		return

	def end(self,transactionNum):
		return

	def fail(self,datamanagerNum):
		global_var.DataManagerList[datamanagerNum].fail()
		return

	def recover(self,datamanagerNum):
		global_var.DataManagerList[datamanagerNum].recover()
		return

	def beginRO(self,transactionNum):
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
	def __addVertex(self,transactionNum):
		self.graph[transactionNum] = []
		return
	def __addEdge(self,transactionNum1,transactionNum2):
		for i in transactionNum2:
			if i not in self.graph[transactionNum1]:
				self.graph[transactionNum1].append(i)
		print("current graph {}".format(self.graph))
		return
	def __deleteVertex(self):
		return
	def __deadLock(self):
		return true

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
			lockResult = lock.lockGranted(self.currentlockTable[variableNum])
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
	def removeLock(self,transactionNum, variableNum):
		# remove lock, change next wait lock's state
		# remove edge// not needed since the whole vertex will be remove 
		# return new granted lock for further check
		removeLockList = []
		for l in self.currentLockList:
			if l.transactionNum == transactionNum:
				removeLockList.append(l)
		for l in removeLockList:
			self.currentLockList.remove(l)
		removeLockList = []
		newGrantedLock = []
		for l in self.waitlockTable:
			lockResult = l.lockGranted(self.currentLockList)
			if lockResult:
				removeLockList.append(l) # remove
				self.currentLockList.append(l) # add to currentLockList
				newGrantedLock.append(l) # return 
			else:
				break
		for l in removeLockList:
			self.currentLockList.remove(l)
		return newGrantedLock
	def fail(self):
		self.status = False 
		print("site {0} failed".format(self.index))
		return
	def recover(self):
		# clear lock table, remove lock, change transaction status, change variable's accessible
		transactionList = []
		for l in currentLockList:
			if l.transactionNum not in transactionList:
				transactionList.append(l.transactionNum)
		for l in waitlockTable:
			if l.transactionNum not in transactionList:
				transactionList.append(l.transactionNum)
		for t in transactionList:
			if global_var.TransactionList[i].status != global_var.TRANSACTION_STATUS_COMMIT:
				global_var.TransactionList[i].status = global_var.TRANSACTION_STATUS_ABORT
		for v in self.variables:
			# donot remove version 
			if v.type == global_var.VARIABLE_TYPE_REPLICATE:
				v.notAccessible()
		self.currentLockList = {}
		self.waitlockTable = {}
		self.status = True
		return
	def getValue(self,variableNum,transactionNum):
		# return -1 when accessible == false, return value if transactionType is not readOnly
		# return the latest version which version less than transactionVersion
		# if not 
		Fail = False
		if self.status == False:
			Fail = True
		vTmpVersion = -1
		vTmpValue = -1
		transactionVersion = global_var.TransactionList[transactionNum].index
		if not Fail:
			for vTmp in self.variables[variableNum]:
				if vTmp.accessible == False:
					Fail = True
					break
				if vTmp.version > vTmpVersion and vTmp.version < transactionVersion:
					vTmpValue = vTmp.value
					vTmpVersion = transactionVersion
		return vTmpValue, Fail
	def update(self,variableNum,value,transactionNum):
		# return -1 when accessible == false, return 1 if success add new version 
		# change variable's accessible 
		Fail = False
		if self.status == False:
			Fail = True
		transactionVersion = global_var.TransactionList[transactionNum].index
		variabletype = -1
		if variableNum % 2 == 0:
			variabletype = global_var.VARIABLE_TYPE_REPLICATE
		else:
			variabletype = global_var.VARIABLE_TYPE_NORMAL
		if not Fail:
			variableTmp = VariableInSite(variableNum,variabletype,transactionVersion)
			self.variables[variableNum].append(variableTmp)
			for v in self.variables[variableNum]:
				if v.accessible == False:
					v.accessible = True
		return Fail

		
		