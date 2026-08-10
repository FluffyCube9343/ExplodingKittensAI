import random
class PublicKnowledge:
    #EK is -1
    #[DEF, NOPE, ATK, SKIP, FVR, SHUF, STF, C1, C2, C3, C4, C5]
    #[0.   1,    2,   3,    4,   5,    6,   7,  8,  9, 10, 11]
    def __init__(self):
        self.defaultDeck = [4,5,4,4,4,4,5,4,4,4,4,4]
        self.discardFreq = [0]*12
        self.deckSize = -1 #the game has not started yet
        self.playerSizes = [-1]*2 #the game has not started yet
        self.deckEpoch = 0 #incremented any time a shuffle is played or a EK is drawn to invalidate a STF


# Currently just sitting here so STF actually gets implemeneted properly
class STFKnowledge:
    def __init__(self, cards, deckSize, deckEpoch):
        self.cards = cards
        self.deckSize = deckSize
        self.deckEpoch = deckEpoch

class GameState:
    def __init__(self):
        self.hands = [[0]*12,[0]*12]
        self.deck = []
        self.pk = PublicKnowledge
        self.pendingStack = []
        self.curPlayer = 0
        self.turnsLeft = 1
        self.STFKnowledge = [None,None]

def dealGame():
    pk = PublicKnowledge()
    p1hand = [0]*12
    p1hand[0] = 1
    p2hand = [0]*12
    p2hand[0] = 1
    deck = []
    for idx in range(1,12):
        deck.extend([idx for i in range(pk.defaultDeck[idx])])
    random.shuffle(deck)
    for i in range(7):
        p1hand[deck[-1]]+=1
        deck.pop()
    for i in range(7):
        p2hand[deck[-1]]+=1
        deck.pop()
    deck.extend([-1,0,0])
    random.shuffle(deck)

    pk.deckSize = len(deck)
    pk.playerSizes = [8,8]
    return (p1hand, p2hand, deck, pk)

def run_game():
    pass

def main():
    pass
