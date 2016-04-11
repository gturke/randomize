import numpy as np
import pandas as pd
import statsmodels.api as sm #GT: I think statsmodels may be better than scikit learn b/c with sklearn we have to calculate p-vals by hand -- might be worth writing the code so we can do other things with sklearn, but for this project it doesn't seem like the best available option

#TODO: Find places in script where user may want output
class randomization(object):
    def __init__(self, universeDf, strataName=None, seed=None, minPval=None, numConditions=None, balanceVars=None, minRuns=None, maxRuns=None, minJointP=None):
        """
        args:
        numConditions - Number of treatments plus control (groups) to randomly assign.
        conditionName - Nameplace assiged to groupings determined by conditions argument.
        balanceVars - List of variables to use to ensure balanced assignment to treatment.
        minPval - The minimum acceptable p-value found after balancing variables.
        seed - Arbitrary value to allow reproducible randomization of data.
        # GT: for reRandomization: add minJointP, minRuns maxRuns
        minRuns - The minimum number of times the list will be re-randomized, default value is 10.
        maxRuns - The minimum number of times the list will be re-randomized, default value is 10.
        minJointP - The minimum joint p-value acceptable for the optimal randomization when using re-randomization.
        The the minimum joint p-value the is the smallest p-value obtained in a balnace check. The default value is 0.5.
        """
        #if statements handle possible issues with arguments for init
        self.universeDf = universeDf
        if not isinstance(self.universeDf, pd.DataFrame):
            raise Exception('Argument universeDf requires DataFrame object.')
        self.strataName = strataName
        if self.strataName !=None:
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
            self.seed = np.random.randint(4294967295) #TODO: Return seed to user (upon request or always?) when the user doesn't input a seed
        self.balanceVars = balanceVars
        if not isinstance(self.balanceVars, list):
            raise Exception('Column "balanceVars" must be submitted as a list of strings.')
        self.minRuns = minRuns
        if self.minRuns == None:
            self.minRuns = 10
        self.maxRuns = maxRuns
        if self.maxRuns == None:
            self.maxRuns = 10
        self.minJointP = minJointP
        if self.minJointP == None:
                self.minJointP = 0.5

    def randomSort(self, sortFrame):
        np.random.seed(self.seed)
        #generating random values from 0 to length of file, and assigning a unique value to each observation
        sortFrame['rdmSortVal'] = np.random.choice(len(sortFrame)+1, len(sortFrame), replace = False)
        sortFrame = sortFrame.sort(['rdmSortVal'])
        del sortFrame['rdmSortVal'] #Remove variable for cases where randomization is run more than once(?)
        return sortFrame

    def assignCondition(self, assignFrame):
        conditionCodes = list(range(self.numConditions))
        startCode = np.random.choice(conditionCodes)
        assignList = conditionCodes[startCode:] + conditionCodes[:startCode]
        assignList = ((len(assignFrame)//self.numConditions)*assignList) + assignList[:(len(assignFrame)%self.numConditions)]
        assignFrame['condition'] = assignList
        return assignFrame

    def pValCheck(self, balanceFrame):
        if 'condition' not in balanceFrame.columns:
            raise Exception('You must assign conditions before performing a balance check.')
        conditionCodes = list(range(self.numConditions))
        mlogit = sm.MNLogit(balanceFrame['condition'], balanceFrame[self.balanceVars])
        lgtResult = mlogit.fit()
        pVals = lgtResult.pvalues
        pVals.columns = conditionCodes[1:]
        pVals = pVals.reset_index()
        pVals = pVals.rename(columns={'index':'variable'})
        return pVals

    def balanceCheck(self, balanceFrame):
        pVals = self.pValCheck(balanceFrame)
        for index, row in pVals.iterrows():
            rowName = row[0]
            counter = 1
            for val in row[1:]:
                if val <= self.minPval:
                    raise Exception('P value for variable {} for condition {} is less than minimum p value, {}.'.format(rowName, counter, self.minPval))
                counter += 1
        print('Minimum p value requirement of {} met.'.format(self.minPval))

    def randomStrata(self):
        if self.strataName == None:
            strataFrame = self.randomSort(self.universeDf)
            strataFrame = self.assignCondition(strataFrame)
            finalDf = strataFrame
        else:
            finalDf = pd.DataFrame()
            strataVals = [x for x in set(self.universeDf[self.strataName])]
            for strataVal in strataVals:
                strataFrame = pd.DataFrame(self.universeDf.loc[self.universeDf[self.strataName] == strataVal])
                strataFrame = self.randomSort(strataFrame)
                strataFrame = self.assignCondition(strataFrame)
                finalDf = finalDf.append(strataFrame)
        return finalDf

    # TODO: Add syntax to re-randomize until maxRuns if minJointP threshold is not met
    def reRandomize(self):
        n = 1
        pValDict = {}
        while n <= self.minRuns: #default is 10
            # Run randomstrata function - randomly sort and assign conditions
            # Where do we use 'self.' ?
            dfN = self.randomStrata()
            # Save lowest p-val
            pValsN = self.pValCheck(dfN)
            lowP = 1
            for index, row in pValsN.iterrows():
                rowname = row[0]
                counter = 1
                for val in row[1:]:
                    if val <=lowP:
                        lowP = val
                    counter +=1
            #print("Seed: "+ str(self.seed), "\nMax P Val: "+ str(maxVal))
            pValDict[self.seed]=lowP
            # Create a new seed
            self.seed = np.random.choice(self.seed) #Is there a better way to alter this value through iterations?
            n +=1
        # Add in after re-randomizing through maxRuns
        # if max(pValDict.values()) < self.minJointP:
        #     raise Exception("Specified value for minimum joint p-value {} not achieved.".format(self.minJointP))
        self.seed = max(pValDict, key=lambda k: pValDict[k])
        print("\nSeed, minimum p-value pair:")
        print(pValDict)
        print("\nSeed for optimal distribution: "+ str(self.seed))
        print("Smallest p-value with seed {}: ".format(self.seed) + str(pValDict[self.seed]))
        return self.randomStrata()
