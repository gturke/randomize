import numpy as np
import pandas as pd
import statsmodels.api as sm
from genericRandomizationCode import randomization

def testPrint(rdm):
    print('seed: ' + str(rdm.seed))
    print('number of conditions: ' + str(rdm.numConditions))
    print('minimum p value: ' + str(rdm.minPval))
    print('Data Frame: ' + str(df))
    print('Strata Column Name: ' + str(rdm.strataName))
    print(rdm.randomStrata())

#test randomization with user definitions
'''
df = pd.read_csv("binary.csv")
rdm = randomization(df, seed=12823, minPval=.1, numConditions=3, balanceVars=['gpa','gre'])
testPrint(rdm)
rdm.reRandomize()
'''

df = pd.DataFrame({'humans':['Audrey', 'Grace', 'Joe', 'Paul', 'Genny'], 'myStrata':['F', 'F', 'M', 'M', 'F']})
rdm = randomization(df, strataName='myStrata', seed=12823, minPval=.1, numConditions=3, balanceVars=['humans'])
testPrint(rdm)
rdm.reRandomize()