import random
import time
import lmdb
import pickle
from collections import Counter
from players import *

ctic = time.time()
rng = random.Random()

# LMDB Environment (map_size is 1GB)
states_env = lmdb.open("lmdb_states", map_size=int(1e9))
favors_env = lmdb.open("lmdb_favors", map_size=int(1e9))

# In-memory counters
state_counter_total = Counter()
state_counter_won = Counter()
favor_counter_total = Counter()
favor_counter_won = Counter()

def log_to_mem(counter, state, kind="total"):
    key = str(state)
    counter[key] += 1

def flush_to_lmdb(env, counter, kind):
    with env.begin(write=True) as txn:
        for key, count in counter.items():
            encoded = key.encode()
            val = txn.get(encoded)
            if val:
                current = pickle.loads(val)
            else:
                current = {"total": 0, "won": 0}
            current[kind] += count
            txn.put(encoded, pickle.dumps(current))
    counter.clear()

def initDeck(deck, playerdecks, players, PLAYERS):
    rng.shuffle(deck)
    for player in playerdecks:
        for i in range(7):
            player[deck.pop()] += 1
    deck.extend([0 for _ in range(1 + (PLAYERS < 5))])
    deck.extend([-1 for _ in range(PLAYERS - 1)])
    rng.shuffle(deck)
    players.append(Player(0, playerdecks[0]))
    players.append(Player(1, playerdecks[1]))

def simulateGame(PLAYERS):
    deck = [1]*5 + [2]*4 + [3]*4 + [4]*4 + [5]*4 + [6]*5 + [7]*4 + [8]*4 + [9]*4 + [10]*4 + [11]*4
    playerdecks = [[1] + [0]*11 for _ in range(PLAYERS)]
    players = []
    initDeck(deck, playerdecks, players, PLAYERS)
    turn, turnctr, movectr, victim, toDraw = 0, 0, 0, 1, 1
    p1stf, p2stf = [-9]*3, [-9]*3
    p1states, p2states, p1favors, p2favors = [], [], [], []

    while toDraw and len(players) > 1:
        move = 'skibidi'
        while move:
            move = players[turn].getMove(toDraw, movectr, turnctr, [players[0].numCards, players[1].numCards]) or 0

            if turn == 0:
                p1states.append([len(deck), toDraw] + p1stf + players[0].hand + [len(players[1].hand), move])
            if turn == 1:
                p2states.append([len(deck), toDraw] + p2stf + players[1].hand + [len(players[0].hand), move])

            if move:
                players[turn].numCards -= 1
                playerdecks[turn][move] -= 1
                if move >= 7:
                    players[turn].numCards -= 1
                    playerdecks[turn][move] -= 1
            victim = turn ^ 1

            if not move:
                continue

            if move == 2:
                toDraw = toDraw + 1 if toDraw == 1 else toDraw + 2
                turn = (turn + 1) % PLAYERS
                turnctr += 1
                movectr += 1
            elif move == 3:
                turn = (turn + 1) % PLAYERS
                turnctr += 1
                movectr += 1
            elif move == 4:
                favorcard = players[victim].getFavored()
                if turn == 1:
                    p1favors.append([len(deck), toDraw] + p1stf + players[0].hand + [len(players[1].hand), favorcard])
                if turn == 10:
                    p2favors.append([len(deck), toDraw] + p2stf + players[1].hand + [len(players[0].hand), favorcard])
                players[turn].hand[favorcard] += 1
                players[turn].numCards += 1
                players[turn].inform(turn, move, {'victim': victim, 'cardtaken': favorcard})
            elif move == 5:
                rng.shuffle(deck)
            elif move == 6:
                if turn == 0:
                    p1stf = deck[:-4:-1]
                elif turn == 1:
                    p2stf = deck[:-4:-1]
            elif move >= 7:
                cardtaken = random.choices(range(12), weights=players[victim].hand, k=1)[0]
                players[victim].hand[cardtaken] -= 1
                players[victim].numCards -= 1
                players[victim].inform(turn, move, {'victim': victim, 'cardtaken': cardtaken})
                players[turn].hand[cardtaken] += 1
                players[turn].numCards += 1
                players[turn].inform(turn, move, {'victim': victim, 'cardtaken': cardtaken})

        nextcard = deck.pop()
        p1stf.pop(0); p1stf.append(-9)
        p2stf.pop(0); p2stf.append(-9)

        safe = players[turn].cardDrawn(nextcard)
        movectr += 1
        if not safe:
            players.pop(turn); toDraw = 1
        else:
            if safe == 1:
                if not deck:
                    deck = [-1]
                else:
                    deck.insert(players[turn].reinsertEK(len(deck)), -1)
            toDraw -= 1
            if toDraw == 0:
                turn = (turn + 1) % PLAYERS
                toDraw = 1
                turnctr += 1

    total = p1states + p2states
    favors = p1favors + p2favors
    winner = players[0].name

    for s in total:
        log_to_mem(state_counter_total, s)
    for s in favors:
        log_to_mem(favor_counter_total, s)

    if winner == 0:
        for s in p1states:
            log_to_mem(state_counter_won, s)
        for s in p1favors:
            log_to_mem(favor_counter_won, s)
    elif winner == 1:
        for s in p2states:
            log_to_mem(state_counter_won, s)
        for s in p2favors:
            log_to_mem(favor_counter_won, s)
    else:
        assert False, "Invalid winner"

    return winner

if __name__ == '__main__':
    onewin = zerowin = 0
    for _ in range(int(1e5)):
        res = simulateGame(2)
        onewin += res == 1
        zerowin += res == 0

    flush_to_lmdb(states_env, state_counter_total, "total")
    flush_to_lmdb(states_env, state_counter_won, "won")
    flush_to_lmdb(favors_env, favor_counter_total, "total")
    flush_to_lmdb(favors_env, favor_counter_won, "won")

    print(zerowin, onewin, zerowin / (onewin + zerowin), onewin / (onewin + zerowin))
    print("Time elapsed:", time.time() - ctic, "seconds")
