from __future__ import division
import math
import random
import numpy as np
import itertools

class Randomize(object):

    def __init__(self, strata,
                 treat_distrib=[0.5, 0.25, 0.25],
                 seed=1234):
        """ Strata = list with strata numbers
        Treat_Distrib = distribution of treatment
        Labels = Labels for Treatment, default is Control, Treatment 1, etc."""
        self.strata = np.array(strata)
        self.treat_distrib = self.checkTreatDistrib(treat_distrib)
        self.seed = seed

    # Helper function to check if treatment distribution is valid
    def checkTreatDistrib(self, treat_distrib):
        treat_distrib = np.array(treat_distrib)
        assert sum(treat_distrib <= 0) == 0, \
            'All distribution probs must be > 0'
        # scale distribution
        if sum(treat_distrib) != 1:
            treat_distrib = [x / sum(treat_distrib) for x in treat_distrib]
            print('Treatment distrib did not add to 1, rescaled to {}'.format(
                treat_distrib))
        return np.array(treat_distrib)

    # Generate treatment counts for a fixed value
    def genTreatCounts(self, n, treat_distrib):
        """ n = numiber of units being randomized"""
        np.random.seed(self.seed)
        # Assign preliminary counts
        counts = [math.floor(x) for x in (n * treat_distrib)]
        # Find number of remainders
        unassigned = int((n - sum(counts)))
        remainder = [1] * unassigned + [0] * (len(counts) - unassigned)
        # Randomize and add to counts
        random.shuffle(remainder)
        counts = np.array(counts) + np.array(remainder)
        return(counts)

    # Perform stratified randomization
    def strat_rand(self):
        np.random.seed(self.seed)
        final_assign = np.array([99] * len(self.strata))
        for i in set(self.strata):
            assign_count = self.genTreatCounts(n=sum(self.strata == i),
                                               treat_distrib=self.treat_distrib)
            tmp_assign = [[t] * assign_count[t]
                          for t in range(len(assign_count))]
            tmp_assign = list(itertools.chain(*tmp_assign))
            random.shuffle(tmp_assign)
            final_assign[self.strata == i] = tmp_assign
        return final_assign

if __name__ == '__main__':
    strata = [1] * 100 + [2] * 101 + [3] * 30
    x = Randomize(strata=strata,
                  treat_distrib=[0.25, 0.25, 0.25],
                  seed=628491)
    assign = x.strat_rand()
    import pandas as pd
    print pd.crosstab(strata, assign)