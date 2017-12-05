import module

DataManagerList = [] # list of sites 10 for this situation
VariableSiteList = {} # 20 list store site for each variable
TransactionList = [] # all transaction


if __name__ == "__main__":
    #generateMarket()
    TM = module.TransactionMachine()
    DM = module.DataManager(0)
    print("get main.")