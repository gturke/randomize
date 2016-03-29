# import *

class reRandomization(object):
    def __init__(self, conditions, conditionName, runs, balance, minPval, jointPval, seed):
         """
         args:
         conditions - Number of treatments plus control (groups) to randomly assign.
         conditionName - Nameplace assiged to groupings determined by conditions argument.
         runs - Number of times randomization is run.
         balance - List of variables to use to ensure balanced assignment to treatment.    
         minPval - The minimum acceptable p-value found after balancing variables.
         jointPval - TBD.
         seed - Arbitrary value to allow reproducible randomization of data.
         """
