import numpy as np
import pandas as pd
import statsmodels.api as sm

#TODO: Find places in script where user may want output
class randomization(object):
    def __init__(self, universeDf, strataName=None, seed=None, minPval=None, numConditions=None, balanceVars=None, minRuns=None, maxRuns=None, minJointP=None):
        """Randomization (with optional re-randomization for optimum P-val) of created or defined strata within assigned conditions.

        Args:
        universeDf -- Pandas dataframe of data to be randomized.
        strataName -- Name of field containing strata definition. Must be pre-created by user.
        seed -- Arbitrary value to allow reproducible randomization of data. We recommend generating a random number using Random.org. The value must be between 0 and 4,294,967,295.
        minPval -- The minimum acceptable p-value for each variable when using multinomial logistic regression to check the balance of assignment to treatment.
        numConditions -- Number of groups (treatments plus control) to randomly assign.
        balanceVars -- List of variables to use to ensure balanced assignment to treatment. These should be entered as a list of strings.
        minRuns -- The minimum number of times the list will be re-randomized.
        maxRuns -- The minimum number of times the list will be re-randomized. If only minRuns or maxRuns is specified by the user, the values will be equal to one another. If no values are specified by the user, the default value is 10.
        minJointP -- The minimum joint p-value acceptable for the optimal randomization when using re-randomization. The default value is 0.5. This ensures in a balance check, all variables yield a p-value above or equal to the specified threshold.
        """
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
            self.seed = np.random.randint(4294967295)
        self.balanceVars = balanceVars
        if not isinstance(self.balanceVars, list):
            raise Exception('Column "balanceVars" must be submitted as a list of strings.')
        self.minRuns = minRuns
        self.maxRuns = maxRuns
        if self.minRuns == None:
            if self.maxRuns == None:
                self.minRuns = 10
            else:
                self.minRuns = self.maxRuns
        if self.maxRuns == None:
            self.maxRuns = self.minRuns
        if self.maxRuns < self.minRuns:
            raise Exception ('Maximum runs value cannot be less than the minimum runs value.')
        self.minJointP = minJointP
        if self.minJointP == None:
            self.minJointP = 0.5

    def randomSort(self, sortFrame):
        np.random.seed(self.seed) # Sets seed for reproducibility
        sortFrame['rdmSortVal'] = np.random.choice(len(sortFrame)+1, len(sortFrame), replace = False)    # Generates random values from 0 to length of file, and assigns a unique value to each observation
        sortFrame = sortFrame.sort(['rdmSortVal']) # Sorts frame according to random value
        del sortFrame['rdmSortVal'] # Removes sort value from data frame
        return sortFrame # Returns data frame, randomly sorted

    def assignCondition(self, assignFrame):
        conditionCodes = list(range(self.numConditions))
        startCode = np.random.choice(conditionCodes) # Arbitrarily begins assigmnment with one of the condition codes. This ensures treatment assignment is random and not biased toward control and lower condition numbers when the number of observations is not evenly divisible by the number of conditions.
        assignList = conditionCodes[startCode:] + conditionCodes[:startCode]
        assignList = ((len(assignFrame)//self.numConditions)*assignList) + assignList[:(len(assignFrame)%self.numConditions)] # Creates a list of condition codes equal in length to the data frame
        assignFrame['condition'] = assignList # Applies condition codes to the data frame as variable 'condition'
        return assignFrame # Returns full data frame with 'condition' appended

    def pValCheck(self, balanceFrame):
        if 'condition' not in balanceFrame.columns:
            raise Exception('You must assign conditions before performing a balance check.')
        conditionCodes = list(range(self.numConditions))
        mlogit = sm.MNLogit(balanceFrame['condition'], balanceFrame[self.balanceVars]) # Runs a multinomial logistic regression (mlogit) of balance variables on condition assignment
        lgtResult = mlogit.fit() # Fits model
        pVals = lgtResult.pvalues # Captures p-values from the mlogit in a data frame
        pVals.columns = conditionCodes[1:] # Sets column names of the p-values data frame to the condition code represented by each column
        pVals = pVals.reset_index()
        pVals = pVals.rename(columns={'index':'variable'}) # Renames column 'index' to 'variable'
        return pVals # Returns a data frame of the p-values returned by a balance check mlogit

    def balanceCheck(self, balanceFrame):
        pVals = self.pValCheck(balanceFrame)
        for index, row in pVals.iterrows(): # Iterates through values of p-values data frame and captures the smallest p-value in that frame
            rowName = row[0]
            counter = 1
            for val in row[1:]:
                if val <= self.minPval:
                    raise Exception('P-value for variable {} for condition {} is less than minimum p-value, {}.'.format(rowName, counter, self.minPval)) # If any p-values in data frame are less than the minimum p-value allowed, raises exception
                counter += 1
        print('Minimum p-value requirement of {} met.'.format(self.minPval)) # If no exception is raised, returns statement that specified p-value requirements have been met.

    def randomStrata(self):
        if self.strataName == None: # If no strata are defined, randomly sorts the entire data frame and assigns conditions
            strataFrame = self.randomSort(self.universeDf)
            strataFrame = self.assignCondition(strataFrame)
            finalDf = strataFrame # Returns randomly-sorted data frame with 'condition' appended
        else:
            finalDf = pd.DataFrame() # Creates an empty data frame
            strataVals = [x for x in set(self.universeDf[self.strataName])] # Creates a list of the unique strata values
            for strataVal in strataVals: # Loops through unique values of the strata
                strataFrame = pd.DataFrame(self.universeDf.loc[self.universeDf[self.strataName] == strataVal]) # Creates a data frame for each strata
                strataFrame = self.randomSort(strataFrame) # Randomly sorts the data frame of that strata
                strataFrame = self.assignCondition(strataFrame) # Assigns conditions to the data frame of that strata
                finalDf = finalDf.append(strataFrame) # Appends randomly-sorted data frame of that strata with 'condition' appended to initially empty data frame
        return finalDf # Returns complete data frame with condition assigned. Data frame will be ordered by strata and randomly sorted within strata

    def reRandomize(self):
        n = 1 # Creates a counter to track number of times original data frame has been randomized
        pValDict = {} # Creates an empty dictionary that will be used to store the seed of the randomization and the minimum p-value from a balance check on that condition assignment
        print("Starting seed: " + str(self.seed) + "\n") # Documents starting seed for reproducibility
        while n <= self.maxRuns: # Begins a while loop that will run until the number of randomization runs equals the maximum number of runs (maxRuns) specified by the user
            dfN = self.randomStrata() # Runs the randomStrata function on the original data frame
            pValsN = self.pValCheck(dfN) # Creates a DataFrame of all p-values from a balance check
            lowP = 1
            for index, row in pValsN.iterrows():  # Iterates through all p-values, finds the smallest value, and stores this variable as 'lowP'
                rowname = row[0]
                counter = 1
                for val in row[1:]:
                    if val <= lowP:
                        lowP = val
                    counter +=1
                pValDict[self.seed]=lowP # Adds key:value pair of seed:lowest p-value to the initially empty dictionary pValDict
            print("Run: "+ str(n) + "\nSeed: " + str(self.seed) + "\nMinimum p-value: " + str(pValDict[self.seed]) + "\n") # Documents the number of runs, the seed used, and minimum p-value for each randomization
            if n < self.minRuns: # Continues re-randomizing so long as n is less than the minRuns
                self.seed = np.random.choice(4294967295) # Generates a new seed
                n+=1
            elif n >= self.minRuns: # If n is greater than or equal to minRuns and less than maxRuns , continues if minJointP has not been reached, stops if minJointP has been reached
                if max(pValDict.values()) >= self.minJointP:
                    self.seed = max(pValDict, key=lambda k: pValDict[k])
                    # print("\nSeed, p-value dictionary:\n" + str(pValDict)) # Documents seed, p-value dictionary for user
                    print("\nThe final, optimal seed selected is {0}, and the minimum p-value associated with this randomization in a balance check is {1:.2f}.".format(self.seed, pValDict[self.seed])) # Documents seed and minimum p-value for user knowledge, reproducibility
                    return self.randomStrata() # Returns randomly-sorted data frame with condition assigned to user
                    n = self.maxRuns+1 # Stops the while loop
                elif n == self.maxRuns: # If n is equal to maxRuns and minJointP has not been reached, reports failure to user
                    raise Exception("Specified value for minimum joint p-value {} not achieved in maximum number of runs alotted ({}).".format(self.minJointP, self.maxRuns))
                else: # If n is les than maxRuns and minJointP has not been reached, continues re-randomization
                    self.seed = np.random.choice(4294967295)
                    n +=1
