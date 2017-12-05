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
		self.status = -1 # -1 for initialize, 0 for get and 1 for wait
		sefl.transactionNum = transactionNum # may drop transactionList in DM

class Transaction(object):
	def __init__(self, index, transactionNum, readOnly,currentVariableValue):
		self.index = index # time stamp
		self.name = transactionNum # transaction number 
		self.readOnly = readOnly # true or false
		self.commandlist = [] # store all command
		self.status = -1 # -1 for initialize, 0 for success, 1 for wait, 2 for fail
		# self.currentVariableValue = currentVariableValue # for readOnly


class Command(object):
	def __init__(self, commandtype, transactionNum, variableNum, value):
		self.commandtype = commandtype # 1 for read, 2 for write
		self.transactionNum = transactionNum 
		if variableNum % 2 == 0:
			self.variable = VariableInCommand(variableNum,0,value)
		else:
			self.variable = VariableInCommand(variableNum,1,value)
		self.value = value # none for read
		self.status = -1 # -1 for initialize, 0 for success, 1 for wait, 2 for fail 

class TransactionMachine(object):
	def __init__(self):
		self.index = 0
		self.graph = {}
	def begin(self,transactionNum):
		# input is the number of transaction
		# create transaction
		# add index
		# append to transactionList
		# add vertex to graph
		# return nothing
		print("Transaction {} begin.".format(transactionNum))
		return

	def write(self,transactionNum, variableNum, variableValue):
		# create command object 
		# check if variable legal, if not change transaction's status to fail directly
		# get site list
		# go through list and checkLock()
		# if result contains wait, change transaction's status to wait and add edges
		# if result contains only success or fail and success > 0, change transaction's status to success
		# deadlock detect
		return

	def read(self,transactionNum, variableNum):
		# create command object
		# check if variable legal, if not change transaction's status to fail directly
		# get site list
		# 
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
		return
	def __addEdge(self,transactionNum1,transactionNum2):
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

	def checkLock(self,transactionNum, variableNum):
		# get transactionNum
		# return -1 for site failed, 0 for success, 1 for lock conflict, 
		# return TNum1 and TNum2 where TNum1 is waiting for TNum2 
		# return TNum2 = _ if success or failed
		return TNum1, TNum2 
	def removeLock(self,transactionNum, variableNum):
		# remove lock, change next wait lock's state
		return
	def fail(self):
		self.state = False 
		print("site {0} failed".format(self.index))
		return
	def recover(self):
		# clear lock table, remove lock, change transaction status, change variable's accessible
		return
	def getValue(self,variableNum,transactionType):
		# return -1 when accessible == false, return value if transactionType is not readOnly
		# return _ when readOnly
		return
	def update(self,variableNum,value):
		# return -1 when accessible == false, return 1 if success add new version 
		# change variable's accessible 
		return

		
		