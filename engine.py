import random
import time
from players import *


def initrandom(seed):
    random.seed(seed)


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
        self.stfKnowledge = [None,None]



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
        if(not state.curPlayer):
            me = player1
            opp = player2
        else:
            me = player2
            opp = player1
        move = me.chooseAction(state)
        # print(state.hands[0], state.hands[1], move, state.deck)
        # assert sum(state.hands[0]) == state.pk.playerSizes[0], f"P0 hand/size mismatch: {state.hands[0]} vs {state.pk.playerSizes[0]}"
        # assert sum(state.hands[1]) == state.pk.playerSizes[1], f"P1 hand/size mismatch: {state.hands[1]} vs {state.pk.playerSizes[1]}"


        #noping logic should be here
        state.pendingStack.append(move)
        playertonope = state.curPlayer^1
        while(([player1,player2][playertonope]).askNope(state)):
            state.hands[playertonope][1] -= 1
            state.pk.playerSizes[playertonope] -= 1
            state.pk.discardFreq[1] += 1
            playertonope ^= 1
            state.pendingStack.append(move)

        #if the nopes actually went through and noped
        if(len(state.pendingStack)%2==0):
            state.pendingStack = []
            continue
        else:
            state.pendingStack = []

        if(move[0]!=-1):
            state.hands[state.curPlayer][move[0]] -= 1
            state.pk.playerSizes[state.curPlayer] -= 1
            state.pk.discardFreq[move[0]] += 1

        if(move[0]==-1):
            #draw
            drawn = state.deck[-1]
            state.deck.pop()
            state.pk.deckSize = len(state.deck)
            if(drawn != -1):
                state.pk.playerSizes[state.curPlayer] += 1
                state.hands[state.curPlayer][drawn] += 1
            else:
                if(state.hands[state.curPlayer][0] > 0):
                    state.hands[state.curPlayer][0] -= 1
                    state.pk.playerSizes[state.curPlayer] -= 1
                    state.pk.discardFreq[0] += 1
                    nextpos = me.reinsertEK(state)
                    state.deck.insert(nextpos, -1)
                    state.pk.deckSize = len(state.deck)
                    state.pk.deckEpoch += 1
                else:
                    return state.curPlayer^1
            state.turnsLeft -= 1
            if(state.turnsLeft == 0):
                state.curPlayer^=1
                state.turnsLeft = 1
                continue
        elif(move[0]==2):
            #attack
            state.curPlayer ^= 1
            if(state.turnsLeft == 1): #add one turn if draw one card, else stacking rule applie
                state.turnsLeft = 2
            else:
                state.turnsLeft += 2
        elif(move[0]==3):
            #skip
            state.turnsLeft -= 1
            if(state.turnsLeft == 0):
                state.curPlayer^=1
                state.turnsLeft = 1
                continue
        elif(move[0]==4):
            #favor
            if(state.pk.playerSizes[state.curPlayer^1]!=0): #this is such a stupid edge case. If opp has only a nope, then I play a cat card, then they nope the cat card, I nope back, then I must take cat cards with no cards. Therefore I take no cards.
                cardgiven = opp.gotFavored(state)
                state.pk.playerSizes[state.curPlayer^1] -= 1
                state.pk.playerSizes[state.curPlayer] += 1
                state.hands[state.curPlayer^1][cardgiven] -= 1
                state.hands[state.curPlayer][cardgiven] += 1
        elif(move[0]==5):
            #shuffle
            random.shuffle(state.deck)
            state.pk.deckEpoch += 1
        elif(move[0]==6):
            #stf
            stfobject = STFKnowledge(state.deck[-3:][::-1], state.pk.deckSize, state.pk.deckEpoch)
            state.stfKnowledge[state.curPlayer] = stfobject
        else:
            #cat card
            if(state.pk.playerSizes[state.curPlayer^1]!=0): #this is such a stupid edge case. If opp has only a nope, then I play a cat card, then they nope the cat card, I nope back, then I must take cat cards with no cards. Therefore I take no cards.
                cardgiven = random.choices([*range(12)], weights=state.hands[state.curPlayer^1], k=1)[0]
                state.pk.playerSizes[state.curPlayer^1] -= 1
                state.pk.playerSizes[state.curPlayer] += 1
                state.hands[state.curPlayer^1][cardgiven] -= 1
                state.hands[state.curPlayer][cardgiven] += 1

def evaluate(coeffs, drawcoeffs,oppcoeffs=None, oppdrawcoeffs=None, ngames=10000):
    wins = 0
    for _ in range(ngames):
        p1hand, p2hand, deck, pk = dealGame()
        state = GameState()
        state.hands = [p1hand, p2hand]
        state.deck = deck
        state.pk = pk


        isp2 = random.random() < 0.5
        if(isp2):
            player1 = Player(0) if not oppcoeffs else PolyPlayer(0,oppcoeffs,oppdrawcoeffs)
            player2 = PolyPlayer(1, coeffs, drawcoeffs)
        else:
            player1 = PolyPlayer(0, coeffs, drawcoeffs)
            player2 = Player(1) if not oppcoeffs else PolyPlayer(1,oppcoeffs,oppdrawcoeffs)

        whowon = run_game(state,player1,player2)
        if(whowon == isp2):
            wins += 1
    return wins/ngames



def setupGame(coeffs,drawcoeffs):
    p1hand, p2hand, deck, pk = dealGame()
    state = GameState()
    state.hands = [p1hand, p2hand]
    state.deck = deck
    state.pk = pk

    # player1 = Player(0)
    # player2 = PolyPlayer(1, coeffs)
    player1 = PolyPlayer(0, coeffs, drawcoeffs)
    player2 = Player(1)
    return (state, player1, player2)

def main(coeffs,drawcoeffs):
    p1w = 0
    p2w = 0
    start = time.time()
    for _ in range(int(1e3)):
        states = setupGame(coeffs,drawcoeffs)
        whowon = (run_game(*states))
        if(whowon):
            p2w += 1
        else:
            p1w += 1
    stop = time.time()
    print(p1w/(p2w+p1w))
    print("Time", stop-start)

if __name__=='__main__':
    seed = random.randint(0,100000)
    # seed = 12794
    random.seed(seed)
    print(f'{seed=}')
    coeffs = [[random.random() for i in range(5)] for j in range(8)]
    drawcoeffs = [random.random() for i in range(5)]
    main(coeffs,drawcoeffs)
