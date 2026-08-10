import random

from numpy.random.mtrand import rand
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
        self.hands = [None,None]
        self.deck = []
        self.pk = PublicKnowledge()
        self.pendingStack = []
        self.curPlayer = 0
        self.turnsLeft = 1
        self.STFKnowledge = [None,None]

class Player:
    def __init__(self, playerNum):
        self.playerNum = playerNum
    def chooseAction(self, state): #currently random action for base player
        modified = list(state.hands[self.playerNum])

        #cannot actually select a action if you can't do said action
        modified[0] = 0
        modified[1] = 0

        #for now, you cannot favor or cat card the other player if they have no cards!
        if(state.pk.playerSizes[self.playerNum^1] == 0):
            modified[4] = 0
            modified[7] = 0
            modified[8] = 0
            modified[9] = 0
            modified[10] = 0
            modified[11] = 0
        else:
            modified[7] = modified[7]//2
            modified[8] = modified[8]//2
            modified[9] = modified[9]//2
            modified[10] = modified[10]//2
            modified[11] = modified[11]//2

        randaction = random.choices([*range(12)]+[-1], weights = modified, k=1)

        if(randaction in {4,7,8,9,10,11}):
            return [randaction, self.playerNum^1]
        else:
            return [randaction, -1]

    def doNope(self,state): #returns y/n if nope, contracts that it will deduct/be honest, currently just random
        if(state.hands[self.playerNum][1] == 0):
            return False
        return random.random() < 0.5 #half chance you actually use the move, just for Proof of concept

    def gotFavored(self, state): #how else do you resolve a favor, you tell them which card you're giving away
        randcard = random.choices([*range(12)], weights=state.hands[self.playerNum], k=1)[0]
        return randcard


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

def run_game(state, player1, player2):
    while(state.pk.deckSize > 0):
        move = ([player1, player2][state.curPlayer]).chooseAction(state)

        if(move[0]==-1):
            #draw
            pass
        elif(move[0]==2):
            #attack
            pass
        elif(move[0]==3):
            #skip
            pass
        elif(move[0]==4):
            #favor
            pass
        elif(move[0]==5):
            #shuffle
            pass
        elif(move[0]==6):
            #stf
            pass
        else:
            #cat card
            pass



def main():
    p1hand, p2hand, deck, pk = dealGame()
    state = GameState()
    state.hands = [p1hand, p2hand]
    state.deck = deck
    state.pk = pk
    player1 = Player(0)
    player2 = Player(1)
    run_game(state,player1,player2)

main()
