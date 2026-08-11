import random
import time
import numpy as np
from engine import evaluate

CLIPSIZE = 5
FEATURES = 5
GENOMESIZE = 9*FEATURES  #8 for each of the cards (note all cat cards should have the saem worth), one for draw


def getRandGenome():
    return np.random.uniform(-1,1,size=GENOMESIZE)


def getParams(genome):
    coeffs = genome[:8*FEATURES].reshape(8, FEATURES).tolist()  #8*5 = 40 long
    drawcoeffs = genome[8*FEATURES:].tolist()
    return coeffs, drawcoeffs


def crossover(parent1, parent2):
    mask = np.random.random(GENOMESIZE)<0.5
    return np.where(mask, parent1, parent2)


def mutate(genome, rate=0.15, strength=.3):
    child = genome.copy()
    mask = np.random.random(GENOMESIZE)<rate
    child[mask] += np.random.normal(0,strength,size=mask.sum())
    return np.clip(child, -CLIPSIZE, CLIPSIZE)


def fitness(genome, pool, gamesPerGenome, randomGames=100):
    playercoeffs, playerdrawcoeffs = getParams(genome)

    #score against hof
    winshof = 0
    totalhof = 0
    for oppgenome in pool:
        oppcoeffs, oppdrawcoeffs = getParams(oppgenome)
        r = evaluate(playercoeffs, playerdrawcoeffs,
                     oppcoeffs=oppcoeffs, oppdrawcoeffs=oppdrawcoeffs,
                     ngames=gamesPerGenome)
        winshof += r*gamesPerGenome
        totalhof += gamesPerGenome
    hofscore = winshof/totalhof

    #random baseline score
    random_score = evaluate(playercoeffs, playerdrawcoeffs, oppcoeffs=None, oppdrawcoeffs=None, ngames=randomGames)

    #hybrid weight is currently 0.7 against hall of famers and 0.3 against random agent
    hybrid = 0.7*hofscore + 0.3*random_score
    return hybrid


def getDiversity(population):
    arr = np.stack(population)
    mean = arr.mean(axis=0)
    return float(np.mean(np.linalg.norm(arr - mean, axis=1)))


def sampleParent(scores, k):
    return max(random.sample(scores, k), key=lambda t: t[0])[1]  #genome having the best score of k


def main(popsize=20, generations=20, hofsize=10, hofsample=4, gamesPerGenome=10000,
         eliteCarryOver=0.15, seed=42):
    np.random.seed(seed)
    random.seed(seed)
    population = [getRandGenome() for i in range(popsize)]
    hof = [getRandGenome() for i in range(hofsize)]
    history = []
    for gen in range(generations):
        start = time.time()

        scores = []
        for genome in population:
            pool = random.sample(hof, min(hofsample, len(hof)))
            score = fitness(genome, pool, gamesPerGenome)
            scores.append((score,genome))
        scores.sort(key=lambda x:x[0], reverse=True)
        best_hybrid = scores[0][0]
        meanscore = float(np.mean([s[0] for s in scores]))
        diversity = getDiversity(population)

        #breakout eval: best genome's actual HoF vs random separately
        best_genome = scores[0][1]
        best_coeffs, best_drawcoeffs = getParams(best_genome)
        pool_eval = random.sample(hof, min(hofsample, len(hof)))

        best_vs_hof = 0
        for oppgenome in pool_eval:
            oppcoeffs, oppdrawcoeffs = getParams(oppgenome)
            best_vs_hof += evaluate(best_coeffs, best_drawcoeffs,
                                   oppcoeffs=oppcoeffs, oppdrawcoeffs=oppdrawcoeffs,
                                   ngames=gamesPerGenome)
        best_vs_hof /= len(pool_eval)

        best_vs_random = evaluate(best_coeffs, best_drawcoeffs, oppcoeffs=None, oppdrawcoeffs=None, ngames=gamesPerGenome)

        history.append((gen, best_hybrid, meanscore, diversity, best_vs_hof, best_vs_random))
        elapsed = time.time()-start
        print(f"Gen {gen:2d}: hybrid={best_hybrid:.3f} mean={meanscore:.3f} div={diversity:.2f} | HoF={best_vs_hof:.3f} random={best_vs_random:.3f}  {elapsed:.1f}s")

        hof.append(scores[0][1])
        while(len(hof)>hofsize):
            hof.pop(0)

        elites = [g[1] for g in scores[:max(2,int(popsize*eliteCarryOver))]]
        nextgen = elites
        while(len(nextgen)<popsize):
            parent1 = sampleParent(scores, k=3)
            parent2 = sampleParent(scores, k=3)
            child = crossover(parent1, parent2)
            #adaptive mutation: more mutation in later generation to avoid convergence easily. might change it doesn't work idk
            mutation_strength = 0.3 + 0.2*(gen/generations)
            mutation_rate = 0.15 + 0.1 *(gen/generations)
            child = mutate(child, rate=mutation_rate, strength=mutation_strength)
            nextgen.append(child)
        population = nextgen

    #after training loop, eval against EVERYONE
    finalscores = []
    for genome in population:
        score = fitness(genome, hof, gamesPerGenome)
        finalscores.append((score, genome))
    finalscores.sort(key=lambda x:x[0],reverse=True)
    bestscore, bestgenome = finalscores[0]
    return bestscore, bestgenome, history


if __name__ == '__main__':
    start = time.time()
    bestscore, bestgenome, history = main(generations=10, popsize=20, gamesPerGenome=10000, hofsample=6)
    elapsed = time.time()-start
    print(f'\nTraining time: {elapsed:.1f}s')
    coeffs, drawcoeffs = getParams(bestgenome)
    print(f"Best coeffs: {coeffs}")
    print(f"Best drawcoeffs: {drawcoeffs}")
    print(f"Winrate vs HOF: {bestscore:.3f}")
