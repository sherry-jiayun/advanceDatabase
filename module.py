import project 


'''
# global state 

VARIABLE_TYPE_REPLICATE = 0
VARIABLE_TYPE_NORMAL = 1

LOCK_TYPE_READ = 0
LOCK_TYPE_WRITE = 1

LOCK_STATUS_INITIALIZE = -1
LOCK_STATUS_GRANTED = 0
LOCK_STATUS_WAIT = 1

TRANSACTION_STATUS_INITIALIZE = -1
TRANSACTION_STATUS_COMMIT = 0
TRANSACTION_STATUS_WAIT = 1
TRANSACTION_STATUS_ABORT = 2 

COMMAND_STATUS_INITIALIZE = -1
COMMAND_STATUS_SUCCESS = 0
COMMAND_STATUS_WAIT = 1
COMMAND_STATUS_FAIL = 2
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
	def __init__(self, locktype, transactionNum):
		self.locktype = locktype # read lock, write lock
		self.status = project.LOCK_STATUS_INITIALIZE # -1 for initialize, 0 for get and 1 for wait
		sefl.transactionNum = transactionNum # may drop transactionList in DM
	def lockGranted(self, currentLockList):
		granted = True
		if self.locktype == project.LOCK_TYPE_WRITE:
			for l in currentLockList:
				# 如果有同一个transaction两次试图writelock同一个variable?
				# 如果当前时一个写lock, 拒绝所有不是自己的lock
				if l.transactionNum != self.transactionNum:
					granted = False
					break 
		if self.locktype == project.LOCK_TYPE_READ:
			for l in currentLockList:
				# 如果前面有读操作的话，读的是以前的还是改过的呢？
				# 如果当前是一个读lock,前面不能有任何不是自己的写lock
				if l.locktype == project.LOCK_TYPE_WRITE and l.transactionNum != self.transactionNum:
					# 前面有写操作，并且不是同一个transaction，拒绝
					granted = False
					break
		return granted


class Transaction(object):
	def __init__(self, index, transactionNum, readOnly,currentVariableValue = {}):
		self.index = index # time stamp
		self.name = transactionNum # transaction number 
		self.readOnly = readOnly # true or false
		self.commandlist = [] # store all command
		self.status = -1 # -1 for initialize, 0 for success, 1 for wait, 2 for fail
		self.currentVariableValue = currentVariableValue # for readOnly


class Command(object):
	def __init__(self, commandtype, transactionNum, variableNum, value):
		self.commandtype = commandtype # 1 for read, 2 for write
		self.transactionNum = transactionNum 
		if variableNum % 2 == 0:
			self.variable = VariableInCommand(variableNum,0,value)
		else:
			self.variable = VariableInCommand(variableNum,1,value)
		self.value = value # none for read
		self.status = project.COMMAND_STATUS_INITIALIZE # -1 for initialize, 0 for success, 1 for wait, 2 for fail 

class TransactionMachine(object):
	def __init__(self):
		self.index = 0
		self.graph = {}
	def begin(self,transactionNum):
		# input is the number of transaction
		transTmp = Transaction(self.index, transactionNum, False)# create transaction
		self.index = self.index + 1# add index
		project.TransactionList[transactionNum] = transTmp# append to transactionList
		__addVertex(self,transactionNum)# add vertex to graph
		# return nothing
		print("Transaction {} begin.".format(transactionNum))
		return

	def write(self,transactionNum, variableNum, variableValue):
		commandTmp = Command(2, transactionNum, variableNum, variableValue)# create command object 
		if project.VariableSiteList.has_key(variableValue) == False:# check if variable legal, if not change transaction's status to fail directly
			project.TransactionList[transactionNum].status = project.TRANSACTION_STATUS_ABORT
		siteList = project.VariableSiteList[variableValue]# get site list

		fail = True
		for i in siteList:# go through list and checkLock()
			TNum1, TNum2List, Result = siteList[i].checkLock(transactionNum,commandtype,variableNum)
			# if result contains wait, change command's status to wait and add edges
			if TNum1 == project.LOCK_STATUS_WAIT:
				__addEdge(self,transactionNum,TNum2)	
				commandTmp.status = project.COMMAND_STATUS_WAIT
				fail = False
			# if result contains only success or fail and success > 0, change command's status to success
			elif TNum1 == project.LOCK_STATUS_GRANTED:
				commandTmp.status = project.COMMAND_STATUS_SUCCESS
				fail = False
		if fail:
			commandTmp.status = project.COMMAND_STATUS_FAIL
		project.transactionList[transactionNum].commandlist.append(commandTmp)

		# deadlock detect

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
		return

	def recover(self,datamanagerNum):
		return

	def beginRO(self,transactionNum):
		return

	def __addVertex(self,transactionNum):
		self.graph[transactionNum] = []
		return
	def __addEdge(self,transactionNum1,transactionNum2):
		self.graph[transactionNum2].append(transactionNum1)	
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

				self.currentlockTable[iNum] = {}
				self.waitlockTable[iNum] = {}

				self.variables[iNum] = []
				variableTmp = VariableInSite(iNum,project.VARIABLE_TYPE_REPLICATE)
				self.variables[iNum].append(variableTmp)
			else: 
				if iNum % 10 + 1 == self.index:

					self.currentlockTable[iNum] = {}
					self.waitlockTable[iNum] = {}

					self.variables[iNum] = []
					variableTmp = VariableInSite(iNum,project.VARIABLE_TYPE_NORMAL)
					self.variables[iNum].append(variableTmp)

		for vl in self.variables.keys():
			for v in self.variables[vl]:
				v.getInfo()

	def checkLock(self,transactionNum, variableNum, locktype):
		# get transactionNum
		# return -1 for site failed, 0 for success, 1 for lock conflict, 
		# return TNum1 and TNum2 where TNum1 is waiting for TNum2 
		# return TNum2 = _ if success or failed
		Fail = False
		TNum1 = transactionNum
		TNum2List = []
		if self.status == False:
			Fail = True # site fail
		else:
			if locktype == project.LOCK_TYPE_READ and not self.variables[variableNum].accessible:
				Fail = True
		if not Fail:
			lockTmp = Lock(locktype,transactionNum)
			lockResult = lockTmp.lockGranted(self.currentlockTable[variableNum])
			if not lockResult:
				# add lock into waittable
				self.waitlockTable[variableNum].append(lockTmp)
				for l in self.currentlockTable[variableNum]:
					TNum2.append(l.transactionNum)
			else:
				# add lock into currentLockTable
				self.currentlockTable[variableNum].append(lockTmp)
		return TNum1, TNum2List, Fail
	def removeLock(self,transactionNum, variableNum):
		# remove lock, change next wait lock's state
		# remove edge ???? 
		removeLockList = []
		for l in self.currentLockList:
			if l.transactionNum == transactionNum:
				removeLockList.append(l)
		for l in removeLockList:
			self.currentLockList.remove(l)
		removeLockList = []
		for l in self.waitlockTable:
			lockResult = l.lockGranted(self.currentLockList)
			if lockResult:
				removeLockList.append(l) # remove
				self.currentLockList.append(l) # add to currentLockList
			else:
				break
		for l in removeLockList:
			self.currentLockList.remove(l)
		return
	def fail(self):
		self.state = False 
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
			if project.TransactionList[i].status != project.TRANSACTION_STATUS_COMMIT:
				project.TransactionList[i].status = project.TRANSACTION_STATUS_ABORT
		for v in self.variables:
			# donot remove version 
			if v.type == project.VARIABLE_TYPE_REPLICATE:
			for vTmp in v:
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
		transactionVersion = project.TransactionList[transactionNum].index
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
		transactionVersion = project.TransactionList[transactionNum].index
		variabletype = -1
		if variableNum % 2 == 0:
			variabletype = project.VARIABLE_TYPE_REPLICATE
		else:
			variabletype = project.VARIABLE_TYPE_NORMAL
		if not Fail:
			variableTmp = VariableInSite(variableNum,variabletype,transactionVersion)
			self.variables[variableNum].append(variableTmp)
			for v in self.variables[variableNum]:
				if v.accessible == False:
					v.accessible = True
		return Fail

		
		