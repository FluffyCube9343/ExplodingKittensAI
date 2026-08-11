import random
import time
import numpy as np
from engine2 import evaluate



coeffs = [[random.random() for i in range(3)] for j in range(12)]
drawcoeffs = [random.random() for i in range(3)]

CLIPSIZE = 5
FEATURES = 5
GENOMESIZE = 13*FEATURES #12 for each of the cards, one for draw

def getRandGenome():
    return np.random.uniform(-1,1,size=GENOMESIZE)

def getParams(genome):
    coeffs = genome[:12*FEATURES].reshape(12,FEATURES).tolist() #12*5 = 60 long
    drawcoeffs = genome[12*FEATURES:] #5 long
    return coeffs, drawcoeffs


def crossover(parent1, parent2):
    mask = np.random.random(GENOMESIZE)<0.5
    return np.where(mask, parent1, parent2)

def mutate(genome, rate=0.15, strength=.3):
    child = genome.copy()
    mask = np.random.random(GENOMESIZE)<rate
    child[mask] += np.random.normal(0,strength,size=mask.sum())
    return np.clip(child, -CLIPSIZE, CLIPSIZE)


def fitness(genome,pool,gamesPerGenome):
    playercoeffs, playerdrawcoeffs = getParams(genome)
    wins = 0
    for oppgenome in pool:
        oppcoeffs, oppdrawcoeffs = getParams(oppgenome)
        wins += evaluate(playercoeffs,playerdrawcoeffs,oppcoeffs=oppcoeffs,oppdrawcoeffs=oppdrawcoeffs,ngames=gamesPerGenome)
    return wins/len(pool) #average winrate

def getDiversity(population):
    arr = np.stack(population)
    mean = arr.mean(axis=0)
    return float(np.mean(np.linalg.norm(arr - mean, axis=1)))

def sampleParent(scores, k):
    return max(random.sample(scores,k), key=lambda t: t[0])[1] #genome having the best score of k

def main(popsize=20, generations=20, hofsize=10, hofsample=4,gamesPerGenome=1000,eliteCarryOver=0.15,seed=42):
    np.random.seed(seed)
    random.seed(seed)

    population = [getRandGenome() for i in range(popsize)]
    hof = [getRandGenome() for i in range(popsize)] #the hall of fame is the best genomes
    history = []

    for gen in range(generations):

        #evaluateme
        start = time.time()
        scores = []
        for genome in population:
            pool = random.sample(hof, min(hofsample, len(hof)))
            score = fitness(genome, pool, gamesPerGenome)
            scores.append((score,genome))
        scores.sort(key=lambda x:x[0], reverse=True)

        bestscore = scores[0][0]
        meanscore = float(np.mean([s[0] for s in scores]))
        diversity = getDiversity(population)
        history.append((gen, bestscore, meanscore, diversity))
        print(f"Gen {gen:2d}: best={bestscore:.3f} mean={meanscore:.3f} diversity={diversity:.2f}  {time.time()-start:.1f}s")

        hof.append(scores[0][1])
        while(len(hof)>hofsize):
            hof.pop(0)

        elites = [g[1] for g in scores[:max(2,int(popsize*eliteCarryOver))]]

        nextgen = elites
        while(len(nextgen)<popsize):
            parent1 = sampleParent(scores, k=3)
            parent2 = sampleParent(scores, k=3)
            child = mutate(crossover(parent1,parent2))
            nextgen.append(child)

        population = nextgen


    #after training loop, eval against EVERYONE
    finalscores = []
    for genome in population:
        score = fitness(genome, hof, gamesPerGenome)
        finalscores.append((score, genome))
    finalscores.sort(key=lambda x:x[0],reverse=True)
    bestscore, bestgenome = finalscores[0]
    return bestscore, bestgenome


if __name__ == '__main__':
    start = time.time()
    bestscore, bestgenome = main()
    print('Training time', time.time()-start)
    coeffs, drawcoeffs = getParams(bestgenome)
    print("Best coeffs", coeffs)
    print("Best drawcoeffs", drawcoeffs)
    print("Winrate", bestscore)
