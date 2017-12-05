import module


# global state 

VARIABLE_TYPE_REPLICATE = "replicated"
VARIABLE_TYPE_NORMAL = "normal"

LOCK_TYPE_READ = "read"
LOCK_TYPE_WRITE = "write"

LOCK_STATUS_INITIALIZE = "initialize"
LOCK_STATUS_GRANTED = "granted"
LOCK_STATUS_WAIT = "wait"

TRANSACTION_STATUS_INITIALIZE = "initialize"
TRANSACTION_STATUS_COMMIT = "commit"
TRANSACTION_STATUS_WAIT = "wait"
TRANSACTION_STATUS_ABORT = "abort"

COMMAND_STATUS_INITIALIZE = "initialize"
COMMAND_STATUS_SUCCESS = "success"
COMMAND_STATUS_WAIT = "wait"
COMMAND_STATUS_FAIL = "fail"

# global variable

DataManagerList = [] # list of sites 10 for this situation
VariableSiteList = {} # 20 list store site for each variable
TransactionList = [] # all transaction


if __name__ == "__main__":
    # generate variable list
    for i in range(20):
    	if i % 2 == 0:
    		VariableSiteList[i+1] = [1,2,3,4,5,6,7,8,9,10]
    	else:
    		VariableSiteList[i+1] = [1+(i+1) % 10]
    for v in VariableSiteList.keys():
    	print("variable {0} in sites {1}".format(v,VariableSiteList[v]))

    # generate data manager
    for i in range(10):
    	print("site {}".format(i+1))
    	DM = module.DataManager(i+1)
    	DataManagerList.append(DM)
    	print()

    TM = module.TransactionMachine()
    print("get main.")