import numpy as np
import pandas as pd

class randomization(object):
    def __init__(self, universeDf, strataName=None, seed=None, minPval=None, numConditions=None):
        """
        args:
        numConditions - Number of treatments plus control (groups) to randomly assign.
        conditionName - Nameplace assiged to groupings determined by conditions argument.
        # runs - Number of times randomization is run.
        balanceVars - List of variables to use to ensure balanced assignment to treatment.    
        minPval - The minimum acceptable p-value found after balancing variables.
        jointPval - TBD.
        seed - Arbitrary value to allow reproducible randomization of data.
        # GT: add jointpval later
        """
        #if statements handle possible issues with arguments for init
        self.universeDf = universeDf
        if not isinstance(self.universeDf, pd.DataFrame):
            raise Exception('Argument universeDf requires DataFrame object.')
        self.strataName = strataName
        if type(self.strataName) != str:
            raise Exception('Argument strataName must be a string.')
        elif self.strataName not in self.universeDf.columns:
            raise Exception('Column {} does not exist in your file. If using strata, please add to file before randomization.'.format(self.strataName))
        self.numConditions = numConditions
        if self.numConditions == None:
            self.numConditions = 2
        self.minPval = minPval
        if self.minPval == None:
            self.minPval = .05
        #TODO: send error if user seed seems weird
        self.seed = seed
        if seed == None:
            self.seed = np.random.randint(4294967295)

    def __randomSort(self, sortFrame):
        np.random.seed(self.seed)
        #generating random values from 0 to length of file, and assigning a unique value to each observation
        sortFrame['rdmSortVal'] = np.random.choice(len(sortFrame)+1, len(sortFrame), replace = False)
        sortFrame = sortFrame.sort(['rdmSortVal'])
        return sortFrame
    
    def assignCondition(self, assignFrame):
        conditionCodes = list(range(self.numConditions))
        startCode = np.random.choice(conditionCodes)
        assignList = conditionCodes[startCode:] + conditionCodes[:startCode]
        assignList = ((len(assignFrame)//self.numConditions)*assignList) + assignList[:(len(assignFrame)%self.numConditions)]
        assignFrame['condition'] = assignList
        return assignFrame

    #def balanceCheck(self):

    #ODO: Determine best way to handle strata.
    def randomStrata(self):
        #univStrata = self.universeDf
        if self.strataName == None:
            #calls random sort function on entire universe
            self.universeDf = self.__randomSort(self.universeDf) 
        else:
            strataVals = [x for x in set(self.universeDf[self.strataName])] 
        #    myFinalDf = #this is where the dataframes will get appended to one another after randomizing and balancing within strata 
            for strataVal in strataVals:
                strataFrame = self.universeDf.loc[self.universeDf[self.strataName] == strataVal]
                strataFrame = self.__randomSort(strataFrame)
                strataFrame = self.assignCondition(strataFrame)
        return strataFrame
              
     
