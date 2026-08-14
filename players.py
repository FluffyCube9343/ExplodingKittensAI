import random
import math
#
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

class EKKnowledge:
    def __init__(self, deckSize, drawsUntilEK, epoch):
        self.deckSize = deckSize  # pk.deckSize right after we reinserted
        self.drawsUntilEK = drawsUntilEK # do we know how far down the EK is
        self.epoch = epoch # deckEpoch this knowledge is valid for


class PolyPlayer(Player):  # a player who uses a linear model over features to determine best card fit
    def __init__(self, playerNum, coeffs, drawcoeffs, retaincoeffs):
        super().__init__(playerNum)
        self.coeffs = coeffs
        self.drawcoeffs = drawcoeffs
        self.retaincoeffs = retaincoeffs
        self.ekk = None # do we know where we placed the EK at or nah

    def getFeatures(self, deckSize, oppHandSize, discardFreq):
        x = deckSize/17
        oppnorm = oppHandSize/15
        discard_norm = [discardFreq[i]/4 for i in range(12)]
        return [1, x, x*x, oppnorm, x*oppnorm] + discard_norm

    def getKnownEKDistance(self, state):
        ek = self.ekk
        if ek is None or ek.epoch != state.pk.deckEpoch:
            return None  # welp our information isn't valid
        cardsDrawnSinceInsert = ek.deckSize - state.pk.deckSize
        remaining = ek.drawsUntilEK - cardsDrawnSinceInsert
        if remaining < 0:
            return None  # welp this means we dont know where the EK is at since it already passed our window
        return remaining

    def chooseAction(self, state):
        hand = state.hands[self.playerNum]
        deckSize = state.pk.deckSize
        oppHandSize = state.pk.playerSizes[self.playerNum ^ 1]
        feats = self.getFeatures(deckSize, oppHandSize, state.pk.discardFreq)

        # if the EK at the top or nah, or do we know actually for sure we know it is safe
        ekDistance = self.getKnownEKDistance(state)
        topIsKnownEK = (ekDistance == 0)
        topIsKnownSafe = (ekDistance is not None and ekDistance > 0)

        bestcard = -1
        besty = float('inf')
        for card in range(12):
            if hand[card] == 0 or card == 0 or card == 1:  # do not use a card you cannot use
                continue
            if card in (7,8,9,10,11) and state.hands[self.playerNum][card] < 2:
                continue
            if card in (4,7,8,9,10,11) and oppHandSize == 0:  # do not use a card you should not use
                continue
            y = sum(c*f for c, f in zip(self.coeffs[min(card,7)], feats))
            if y < besty:
                besty = y
                bestcard = card

        if topIsKnownEK:
            if bestcard == -1: # welp thats a forced draw
                return [-1, -1]
            target = self.playerNum ^ 1 if bestcard in (4,7,8,9,10,11) else -1
            return [bestcard, target]

        if topIsKnownSafe:
            # if it is not EK then always take it (can only help you).
            return [-1, -1]

        # no info on top card means we are back to normal tactics.
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
        feats = self.getFeatures(deckSize, oppHandSize, state.pk.discardFreq)
        y = sum(c*f for c, f in zip(self.coeffs[1], feats))
        y = max(-500.0, min(500.0, y))  # clip before exponentiating to avoid overflow
        p = 1/(1+math.exp(y))
        return random.random() < p

    def gotFavored(self, state):
        hand = state.hands[self.playerNum]
        deckSize = state.pk.deckSize
        requesterHandSize = state.pk.playerSizes[self.playerNum ^ 1]
        feats = self.getFeatures(deckSize, requesterHandSize, state.pk.discardFreq)

        worstcard = -1
        worsty = float('-inf')
        for card in range(12):
            if card == 0 or card == 1 or hand[card] == 0:  # never give away defuse or nope
                continue
            y = sum(c*f for c, f in zip(self.retaincoeffs[min(card,7)], feats))
            if y>worsty:  # highest retain-score = most disposable
                worsty=y
                worstcard=card

        if worstcard != -1:
            return worstcard

        # forced case: hand is entirely defuse/nope -- let retaincoeffs[0]/[1] decide
        if hand[0] == 0:
            return 1
        if hand[1] == 0:
            return 0
        y0 = sum(c*f for c, f in zip(self.retaincoeffs[0], feats))
        y1 = sum(c*f for c, f in zip(self.retaincoeffs[1], feats))
        return 1 if y1 > y0 else 0

    def reinsertEK(self, state):  # at which point in the deck would you return a EK
        deckSize = state.pk.deckSize
        pos = min(1, deckSize) #in reality, i could improve this, but for now it's just whatever.
        # if im playing against a strategy thats suspicious, then sure, i should probably put this lower down the deck so a STF
        # cannot see it, (e.g. position 5), but for now this shall do since it's just trying to show that
        # i have a strategy that can beat my random opponent that is better than a hand-derived heuristic.
        drawsUntilEK = deckSize - pos
        self.ekk = EKKnowledge(deckSize + 1, drawsUntilEK, state.pk.deckEpoch + 1) #keep track of where we placed the exploding kitten!!!
        #+ 1 is due to the EK being added
        return pos
