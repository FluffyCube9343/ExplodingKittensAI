import random
import numpy as np
rng = np.random.default_rng()
import lmdb
import pickle

# Initialize LMDB environment (must match your existing path and map_size)
states_env = lmdb.open("lmdb_states", map_size=int(1e9), readonly=True, lock=False)


class Player: #RandomPlayer
    def __init__(self, name, hand):
        self.name = name
        self.numPlayable = sum(hand[2:7]) + sum([hand[i]//2 for i in range(7,12)])
        self.numCards = 8
        self.hand = hand
    def inform(self, player, move, moveData):
        if(player!=self.name and move>=7 and moveData['victim']==int(self.name)):
            cardtaken = moveData['cardtaken']
            if(2<=cardtaken<=6): self.numPlayable -= 1
            elif(cardtaken >= 7 and self.hand[cardtaken]%2==1): self.numPlayable -= 1
            return
        if(player==self.name and (move==4 or move>=7)):
            cardtaken = moveData['cardtaken']
            if(2<=cardtaken<=6): self.numPlayable += 1
            elif(cardtaken >= 7 and self.hand[cardtaken]%2==0): self.numPlayable += 1

        
    def getMove(self, toDraw, lendeck, p1stf, deckhandlens):
        #Return None = draw ONE card
        chosenmove = giveRandomMove(self.hand,self.name,deckhandlens, self.numPlayable)
        if(chosenmove!=None): self.numPlayable -= 1
        # print('moving!', self.name, chosenmove)
        return chosenmove
    def cardDrawn(self,card): #THIS CANNOT BE OVERWRITTEN
        if(card==-1):
            if(not self.hand[0]):
                return 0
            else:
                self.hand[0] -= 1
                self.numCards -= 1
                return 1
        else:
            self.hand[card] += 1
            self.numCards += 1
            if(card >= 7): #catcard
                if(self.hand[card]%2==0):
                    self.numPlayable += 1
            elif(card >= 2): #not catcard, but still playable
                self.numPlayable += 1
            return 2
    def getFavored(self):
        togiveaway = random.choices([0,1,2,3,4,5,6,7,8,9,10,11], weights=self.hand, k=1)[0]
        self.hand[togiveaway] -= 1
        self.numCards -= 1
        if(2 <= togiveaway <= 6): self.numPlayable -= 1
        elif(togiveaway >= 7 and self.hand[togiveaway]%2==1): self.numPlayable -= 1
        return togiveaway
    def reinsertEK(self, decklen):
        return int(random.random()*(decklen+1))
        # return random.randint(0,decklen)

class MonteCarloPlayer(Player):

    def getMove(self, toDraw, lendeck, p1stf, deckhandlens):
        best_move = None
        best_ratio = -1.0
        
        with states_env.begin() as txn:
            for move in range(12):
                state_key = [lendeck, toDraw] + p1stf + self.hand + [deckhandlens, move]
                key_str = str(state_key).encode()

                val = txn.get(key_str)
                if val:
                    record = pickle.loads(val)
                    won = record.get("won", 0)
                    total = record.get("total", 1)  # prevent division by zero
                    ratio = won / total
                else:
                    ratio = 0

                if ratio > best_ratio:
                    best_ratio = ratio
                    best_move = move
            if(best_move!=None):
                return best_move
            else:
                chosenmove = giveRandomMove(self.hand,self.name,deckhandlens, self.numPlayable)
                if(chosenmove!=None): self.numPlayable -= 1
                return chosenmove


def weighted_random_choice(choices, weights):
    cum_weights = np.cumsum(weights)
    total_weight = cum_weights[-1]
    rand_val = np.random.rand() * total_weight
    idx = np.searchsorted(cum_weights, rand_val)
    return choices[idx]


    
def giveRandomMove(deck,name,deckhandlens,numPlayable,victim=None,includeNone=True):
    
    if(numPlayable == 0): return None
    # print(numPlayable, deck, deckhandlens)
    if(includeNone and not int(random.random()*(numPlayable+1))): return None
    # if(includeNone and not random.randint(0,numPlayable)): return None
    
    if(victim == None): victim = 1 if int(name)==0 else 0

    possible = list(deck)
    possible[0] = 0
    possible[1] = 0
    if deckhandlens:
        possible[7] = possible[7]//2
        possible[8] = possible[8]//2
        possible[9] = possible[9]//2
        possible[10] = possible[10]//2
        possible[11] = possible[11]//2
    else:
        possible[4] = 0
        possible[7] = 0
        possible[8] = 0
        possible[9] = 0
        possible[10] = 0
        possible[11] = 0

    if(possible==[0]*12): return None
    numbers = [0,1,2,3,4,5,6,7,8,9,10,11]

    # return weighted_random_choice(numbers, possible)
    return random.choices(numbers, weights=possible, k=1)[0]

def LCG(x, a, c, m): #https://www.ams.org/journals/mcom/1999-68-225/S0025-5718-99-00996-5/S0025-5718-99-00996-5.pdf
    return (a*x+c)%m