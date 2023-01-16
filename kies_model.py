import mesa
import math
import random
import numpy as np
import pandas as pd
from stemmer import Stemmer

class KiesModel(mesa.Model):
    '''
    Model class
    '''
    def __init__(self, n_stem, n_partij, systeem):
        self.num_agents = n_stem
        self.systeem = systeem
        self.partijen = []
        self.winnaar = -1
        self.schedule = mesa.time.RandomActivation(self)

        for i in range(n_partij):
            self.partijen.append((random.random(), random.random()))

        self.datacollector = mesa.DataCollector(
            agent_reporters={"x_position": "x", "y_position": "y", "vote": "vote"})

        self.data = pd.DataFrame(
            {"x_position": pd.Series(dtype=float), "y_position": pd.Series(dtype=float), "vote": pd.Series(dtype=int)})

        for i in range(n_stem):
            x = random.random()
            y = random.random()
            a = Stemmer(i, x, y, self)
            self.schedule.add(a)

    def step(self):
        '''
        laat iedereen stemmen en voegt de stemmen toe aan data

        bepaald vervolgens de winnaar aan de hand van het gekozen kiesstelsel
        '''
        self.schedule.step()
        self.datacollector.collect(self)
        self.data = self.datacollector.get_agent_vars_dataframe().tail(self.num_agents)

        if self.systeem == 'p':
            self.winnaar = self.data['vote'].mode()[0] #meest voorkomende stem is de winnaar
        elif self.systeem == 'r':
            self.winnaar = self.runoff_vote()
        elif self.systeem == 'a':
            self.winnaar = self.approval_vote()
        else:
            self.winnaar = -1

    def approval_vote(self):
        '''
        de winnaar is de partij met de meeste stemmen
        '''
        s = pd.Series(np.hstack(self.data['vote']))
        return s.value_counts().index[0]

    def runoff_vote(self):
        '''
        bepaald de winnaar door te kijken of er een partij is met meer dan 50% nr1 stemmen, als dit niet het geval is
        wordt de partij met de minste n1 stemmen geëlimineerd; dit wordt herhaald tot er een winnende partij gevonden is
        '''
        def shift_row(a):
            if a.iloc[-1] == -1:
                n = 1
                for j in range(len(a)-1):
                    try:
                        if a.iloc[-(2+j)] == -1:
                            n+=1
                        else:
                            break
                    except TypeError:
                        break

                return a.shift(periods=n)
            return a

        df = pd.DataFrame(np.vstack(self.data['vote']))

        for _ in range(len(self.partijen)-1):
            # Comment in for individual run analysis.
            # print(df[len(self.partijen) - 1].value_counts())
            if df[len(self.partijen)-1].value_counts().iloc[0] >= (self.num_agents/2):
                return df[len(self.partijen)-1].value_counts().index[0]
            else:
                p = df[len(self.partijen)-1].value_counts().index
                verliezer = p[len(p)-1]
                df.replace(to_replace=verliezer, value=-1, inplace=True)
                df = df.apply(lambda a: shift_row(a), axis=1).astype('Int64')
        # Comment in for individual run analysis.
        # print(df[len(self.partijen) - 1].value_counts())
        return -1

    def condorcet(self):
        '''
        vindt de condorcet winnaar:
        elke partij doet een pairwise runoff tegen elke andere partij, de partij die van elke partij wint is de
        condorcet winnaar. wanneer er geen condorcet winnaar is wordt er -1 gereturnt
        '''
        df = self.data
        p1 = self.partijen[0]
        n = 0
        for i in range(len(self.partijen)-1):
            p2 = self.partijen[i+1]
            df['n'] = df.apply(lambda a: self.pairwise_runoff(p1,p2,(a['x_position'], a['y_position']),n,i+1), axis=1)
            n = df['n'].mode()[0]
            p1 = self.partijen[n]

        if n!=0:
            for i in range(len(self.partijen)):
                if (i == n): break
                p2 = self.partijen[i]
                df['n'] = df.apply(lambda a:
                                   self.pairwise_runoff(p1,p2,(a['x_position'], a['y_position']),n,i+1), axis=1)
                if df['n'].mode()[0] != n:
                    return -1

        return n

    def pairwise_runoff(self, p1, p2, v, n1, n2):
        if((math.sqrt((p1[0] - v[0])**2 + (p1[1] - v[1])**2) - math.sqrt((p2[0] - v[0])**2 + (p2[1] - v[1])**2)) > 0):
            return n2
        else:
            return n1
