import random
import time
import numpy as np
from engine import evaluate

CLIPSIZE = 5
FEATURES = 17
GENOMESIZE = 17*FEATURES  #8 play coeffs + 8 retain coeffs + one for draw

#
def getRandGenome():
    return np.random.uniform(-1,1,size=GENOMESIZE)


def getParams(genome):
    coeffs = genome[:8*FEATURES].reshape(8, FEATURES).tolist()  #8*17 = 136 long
    retaincoeffs = genome[8*FEATURES:16*FEATURES].reshape(8, FEATURES).tolist()  #8*17 = 136 long
    drawcoeffs = genome[16*FEATURES:].tolist()
    return coeffs, drawcoeffs, retaincoeffs


def crossover(parent1, parent2):
    mask = np.random.random(GENOMESIZE)<0.5
    return np.where(mask, parent1, parent2)


def mutate(genome, rate=0.15, strength=.3):
    child = genome.copy()
    mask = np.random.random(GENOMESIZE)<rate
    child[mask] += np.random.normal(0,strength,size=mask.sum())
    return np.clip(child, -CLIPSIZE, CLIPSIZE)


def fitness(genome, gamesPerGenome):
    playercoeffs, playerdrawcoeffs, playerretaincoeffs = getParams(genome)
    random_score = evaluate(playercoeffs, playerdrawcoeffs, playerretaincoeffs, ngames=gamesPerGenome)
    return random_score


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
            score = fitness(genome, gamesPerGenome)
            scores.append((score,genome))
        scores.sort(key=lambda x:x[0], reverse=True)
        best_random = scores[0][0]
        meanscore = float(np.mean([s[0] for s in scores]))
        diversity = getDiversity(population)

        #separate eval: best genome vs HoF
        best_genome = scores[0][1]
        best_coeffs, best_drawcoeffs, best_retaincoeffs = getParams(best_genome)
        pool_eval = random.sample(hof, min(hofsample, len(hof)))

        best_vs_hof = 0
        for oppgenome in pool_eval:
            oppcoeffs, oppdrawcoeffs, oppretaincoeffs = getParams(oppgenome)
            best_vs_hof += evaluate(best_coeffs, best_drawcoeffs, best_retaincoeffs,
                                   oppcoeffs=oppcoeffs, oppdrawcoeffs=oppdrawcoeffs, oppretaincoeffs=oppretaincoeffs,
                                   ngames=gamesPerGenome)
        best_vs_hof /= len(pool_eval)

        history.append((gen, best_random, meanscore, diversity, best_vs_hof, best_random))
        elapsed = time.time()-start
        print(f"Gen {gen:2d}: random={best_random:.3f} mean={meanscore:.3f} div={diversity:.2f} | HoF={best_vs_hof:.3f}  {elapsed:.1f}s")

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

    #after training loop, eval against random
    finalscores = []
    for genome in population:
        score = fitness(genome, gamesPerGenome)
        finalscores.append((score, genome))
    finalscores.sort(key=lambda x:x[0],reverse=True)
    bestscore, bestgenome = finalscores[0]
    return bestscore, bestgenome, history


if __name__ == '__main__':
    start = time.time()
    bestscore, bestgenome, history = main(generations=30, popsize=140, gamesPerGenome=1500, hofsample=8,seed=1010102)
    elapsed = time.time()-start
    print(f'\nTraining time: {elapsed:.1f}s')
    coeffs, drawcoeffs, retaincoeffs = getParams(bestgenome)
    print(f"Best coeffs: {coeffs}")
    print(f"Best drawcoeffs: {drawcoeffs}")
    print(f"Best retaincoeffs: {retaincoeffs}")
    print(f"Winrate vs Random: {bestscore:.3f}")
