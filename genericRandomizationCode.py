import numpy as np
import pandas as pd
#import sklearn
import statsmodels.api as sm #GT: I think statsmodels may be better than scikit learn b/c with sklearn we have to calculate p-vals by hand -- might be worth writing the code so we can do other things with sklearn, but for this project it doesn't seem like the best available option

#TODO: Find places in script where user may want output
class randomization(object):
    def __init__(self, universeDf, strataName=None, seed=None, minPval=None, numConditions=None, balanceVars=None):
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
        self.balanceVars = balanceVars
        if not isinstance(self.balanceVars, list):
            raise Exception('Column "balanceVars" must be submitted in list.')

    def randomSort(self, sortFrame):
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

    """
    balanceCheck takes a DataFrame,
    runs a logistic regression of the treatment assignment on the variables defined by the user (in balanceVars)
    should be a multinomial logit always or when there is more than 2 conditions, otherwise logit
    figure out multinomial logit function(s) available in python and if it works on a binomial DV
    or run logit on each treatment against control (always 0)
    """
    #pd.get_dummies() -- probably won't need this for conditions
    def balanceCheck(self, balanceFrame):
        mlogit = sm.MNLogit(balanceFrame['condition'], balanceFramce[self.balanceVars])
        lgtResult = mlogit.fit()
        #lgtSummary = lgtResult.summary() #TODO: give user output
        pVals = lgtResults.pvalues
        pVals.columns = conditionCodes[1:]
        pVals = pVals.reset_index()
        pVals = pVals.rename(columns={'index':'variable'})
        for index, row in pVals.iterrows():
            rowName = row[0]
            counter = 1
            for val in row[1:]:
                if val <= self.minPval:
                    raise Exception('P value for variable {} for condition {} is less than minimum p value, {}.'.format(rowName, counter, minPval))
                counter += 1
        print('Minimum p value requirement of {} met.'.format(self.minPval))
         
        
    #ODO: Determine best way to handle strata.
    def randomStrata(self):
        #univStrata = self.universeDf
        if self.strataName == None:
            #calls random sort function on entire universe
            self.universeDf = self.__randomSort(self.universeDf)
        else:
            strataVals = [x for x in set(self.universeDf[self.strataName])]
            strataVals = [x for x in set(self.universeDf[self.strataName])] 
            #not to be used in final script
            finalDf = pd.DataFrame()
            for strataVal in strataVals:
                strataFrame = pd.DataFrame(self.universeDf.loc[self.universeDf[self.strataName] == strataVal])
                strataFrame = self.randomSort(strataFrame)
                strataFrame = self.assignCondition(strataFrame)
                finalDf = finalDf.append(strataFrame)
        return finalDf


              
     
