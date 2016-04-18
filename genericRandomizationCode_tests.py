import numpy as np
import pandas as pd
import statsmodels.api as sm
from genericRandomizationCode import randomization

df = pd.read_csv("http://www.ats.ucla.edu/stata/data/binary.csv") # for some reason only works in ipython notebook but returns parsing error when run from command line

#test randomization with user definitions
rdm = randomization(df, seed=12823, minPval=.1, numConditions=3, balanceVars=['gpa','gre'])
print('seed: ' + str(rdm.seed))
print('number of conditions: ' + str(rdm.numConditions))
print('minimum p value: ' + str(rdm.minPval))
print('Data Frame: ' + str(df))
print('Strata Column Name: ' + rdm.strataName)
print(rdm.randomStrata())

#test without user defs
rdm2 = randomization()
print('seed: ' + str(rdm2.seed))
print('number of conditions: ' + str(rdm2.numConditions))
print('minimum p value: ' + str(rdm2.minPval))
print('Data Frame: ' + str(df))
print('Strata Column Name: ' + rdm2.strataName)
print(rdm2.randomStrata())
