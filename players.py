import random
import math

class Player: #a player that acts entirely randomly
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
        modified.append(1)
        randaction = random.choices([*range(12)]+[-1], weights = modified, k=1)[0]

        if(randaction in {4,7,8,9,10,11}):
            return [randaction, self.playerNum^1]
        else:
            return [randaction, -1]

    def askNope(self,state): #returns y/n if nope, contracts that it will deduct/be honest, currently just random
        if(state.hands[self.playerNum][1] == 0):
            return False
        return random.random() < 0.5 #half chance you actually use the move, just for Proof of concept

    def gotFavored(self, state): #how else do you resolve a favor, you tell them which card you're giving away
        randcard = random.choices([*range(12)], weights=state.hands[self.playerNum], k=1)[0]
        return randcard

    def reinsertEK(self, state): #at which point in the deck would you return a EK
        return random.randint(0,state.pk.deckSize)


class PolyPlayer(Player):  # a player who uses a linear model over features to determine best card fit
    def __init__(self, playerNum, coeffs, drawcoeffs):
        super().__init__(playerNum)
        self.coeffs = coeffs
        self.drawcoeffs = drawcoeffs
    def getFeatures(self, deckSize, oppHandSize):
        x = deckSize/17
        oppnorm = oppHandSize/15
        return [1, x, x*x, oppnorm, x*oppnorm]
    def chooseAction(self, state):
        hand = state.hands[self.playerNum]
        deckSize = state.pk.deckSize
        oppHandSize = state.pk.playerSizes[self.playerNum ^ 1]
        feats = self.getFeatures(deckSize, oppHandSize)
        bestcard = -1
        besty = float('inf')
        for card in range(12):
            if hand[card] == 0 or card == 0 or card == 1:  # do not use a card you cannot use
                continue
            if card in (7,8,9,10,11) and state.hands[self.playerNum][card] < 2:
                continue
            if card in (4,7,8,9,10,11) and oppHandSize == 0:  # do not use a card you should not use
                continue
            a, b, c, d, e = self.coeffs[min(card,7)]
            f1, f2, f3, f4, f5 = feats
            y = a*f1+b*f2+c*f3+d*f4+e*f5
            if y < besty:
                besty = y
                bestcard = card
        drawy = sum(c*f for c, f in zip(self.drawcoeffs, feats))
        if bestcard == -1 or drawy < besty:
            return [-1, -1]  # draw
        target = self.playerNum ^ 1 if bestcard in (4,7,8,9,10,11) else -1
        return [bestcard, target]
    def askNope(self, state):
        if state.hands[self.playerNum][1] == 0:
            return False
        deckSize = state.pk.deckSize
        oppHandSize = state.pk.playerSizes[self.playerNum ^ 1]
        feats = self.getFeatures(deckSize, oppHandSize)
        y = sum(c*f for c, f in zip(self.coeffs[1], feats))
        y = max(-500.0, min(500.0, y))  # clip before exponentiating to avoid overflow
        p = 1/(1+math.exp(y))
        return random.random() < p
