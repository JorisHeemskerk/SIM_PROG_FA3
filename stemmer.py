import mesa
import math
import random

class Stemmer(mesa.Agent):
    '''
    Stemmer agent class

    hierin zit informatie over de stemmer, zoals zijn politieke positie, hoe kritisch die is en ook functies om
    de stem te bepalen.
    '''
    def __init__(self, unique_id, x, y, model):
        super().__init__(unique_id, model)
        self.x = x
        self.y = y
        self.vote = -1

        n = 99
        res = -1
        ballot = []
        for i in range(len(self.model.partijen)):
            p = self.model.partijen[i]
            new = math.sqrt((self.x - p[0])**2 + (self.y - p[1])**2)
            if new < n:
                n = new
                ballot.append(res)
                res = i
            else:
                ballot.append(i)

        ballot = ballot[1:]
        ballot.append(res)

        self.ballot = ballot
        self.c = random.randint(1, len(self.ballot) - 1) #hoe kritisch iemand is; wordt gebruikt in approval_vote

    def plurality_vote(self):
        '''
        stemt op favoriete partij
        als eer meerdere jaren gerunt worden kan er tactisch gestemd worden:
        wanneer de winner of de runner-up niet de favoriet is, is er een kans dat de stemmer besluit op de 'beste' van
        de twee te stemmen, iets wat je vaak ziet in bijvoorbeeld verkiezingen in de VS.
        hoe groter het aandeel stemmen van de top 2 partijen is, hoe eerder iemand tactisch zal stemmen
        '''
        res = self.ballot[len(self.ballot)-1]

        if (not self.model.data.empty):
            last_winnaar = int(self.model.winnaar)
            last_runnerup = int(self.model.data['vote'].value_counts().index[1])

        if (not self.model.data.empty) and (res != last_winnaar) and (res != last_runnerup):
            p = (self.model.data['vote'].value_counts().iloc[0] + self.model.data['vote'].value_counts().iloc[1]) / self.model.num_agents

            if random.random() < p: #tactisch stemmen:
                p1 = self.model.partijen[last_winnaar]
                p2 = self.model.partijen[last_runnerup]
                if math.sqrt((self.x - p1[0])**2 + (self.y - p1[1])**2) < \
                    math.sqrt((self.x - p2[0])**2 + (self.y - p2[1])**2):
                    self.vote = last_winnaar
                else: self.vote = last_runnerup
            else:
                self.vote = res
        else:
            self.vote = res

    def runoff_vote(self):
        '''
        stemt gewoon de partijen op volgorde van favoriet. Omdat je stem al op volgorde is is er niet veel incentive
        om tactisch te stemmen
        '''
        self.vote = self.ballot

    def approval_vote(self):
        '''
        stemt op het x aantal favoriete partijen; tactisch stemmen kan gebeuren wanneer de agent door heeft dat diens
        partij een grotere kans op winnen heeft wanneer er partijen van de stem weggelaten worden.
        '''

        self.vote = self.ballot[(len(self.ballot) - self.c):len(self.ballot)]
        if not self.model.data.empty and \
            (self.ballot[len(self.ballot)-1] != self.model.winnaar) and \
            (random.random() < .5):
            pos = self.ballot.index(self.model.winnaar)
            if (len(self.ballot) - self.c) <= pos:
                self.c -= (pos - (len(self.ballot) - self.c) + 1)
                self.vote = self.ballot[(len(self.ballot) - self.c):len(self.ballot)]

    def step(self):
        if(self.model.systeem == 'p'):
            self.plurality_vote()
        elif(self.model.systeem == 'r'):
            self.runoff_vote()
        elif(self.model.systeem == 'a'):
            self.approval_vote()
        else:
            self.vote = -1
