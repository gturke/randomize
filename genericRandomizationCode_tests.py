from genericRandomizationCode import randomization
import pandas as pd

#df = pd.DataFrame({'humans':['Grace', 'Audrey', 'Joe', 'Paul', 'Genny'], 'myStrata':['F', 'F', 'M', 'M', 'F']})
#df = 'YOLO'
df = pd.read_csv("http://www.ats.ucla.edu/stata/data/binary.csv")


#test randomization with user definitions
rdm = randomization(df, 'myStrata', 12823, .1, 3)
#test without user defs
#rdm = randomization()
print('seed: ' + str(rdm.seed))
print('number of conditions: ' + str(rdm.numConditions))
print('minimum p value: ' + str(rdm.minPval))
print('Data Frame: ' + str(df))
print('Strata Column Name: ' + rdm.strataName)

#isn't a complete function
print(rdm.randomStrata())

#Does not error
#print(rdm.randomSort(df))

#Does not error
#print(rdm.assignCondition(rdm.randomSort(df)))
