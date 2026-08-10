# Exploding Kittens AI

Hello readers! Since July 2024, I've been working on an AI for the Exploding Kittens Game. I've been introduced to this game by a few cousins during the pandemic (maybe November 2020?) and it is by far my favorite card game.

I've also chosen to study this because it places heavy (but somewhat equal) empahsis on **both strategy and chance** unlike other games (e.g. war, chess) where one significantly outweighs the other.

It's also why I've become **heavily interested in game theory**.

## Methods

### Direct Algorithm
Branches: `main` (most recent).
Note: prior optimizations done on `numpystuffs`, but have been merged to `main`.

Most of the `main` branch is my direct algorithm, which just implements my personal strategy for the exploding kittens game. This is usually something along the lines of (and later fine-tuned in code):

- Draw card if there are a large number of cards in the deck (M
- Play **cat cards** or **favor cards** as early as possible, which is when opponentshave less cards (greater chance of obtaining a **Defuse**)


**Winrate: ~89%**

### PPO
Branches: `rltest`

I've found that **PPO isn't really a good idea** for this game due to the **high input space**. For example, the [typical example](https://keras.io/examples/rl/ppo_cartpole/) of balancing a pole only requires four dimensions of its observations pace: a pole velocity (continuous).

However, in the case of exploding kittens, there are 55 cards in the deck, the opponent can have anywhere between 0 and 55 cards, and there are 12 cards with between 0 and 6 of each card in the deck. This would mean that PPO isn't really able to infer an optimal policy state since **it hasn't even explored many of the states** at all. Furthermore, these are **discrete values**, meaning that adding or removing a card from play may sharply affect decision making.

**Winrate: ~56%**

### Monte Carlo (precomputed)
Branches: `monte2`

I realized that because the AI can work much faster than the human (who may take a couple of seconds), meaning we could use the remaining time to compute future games and optimal decision choices for them. Because our starting game states would be very different than our end game states, it would be wise to follow a game thoroughly, determine if it is won or lost, and adjust the state's winrate accordingly. From here for a given state, the AI can choose an optimal move that increases its winrate.

However, I realized that due to the high input space predicted in the **PPO** approach, many starting and mid-game states would not have been computed yet, leading to **inoptimal endgames** for the AI. Further training to achieve every possible game might be **infeasible** as this would require **hundreds of gigabytes of storage**. In theory this is how the game could become "solved", but there are technological barriers in place as of the moment. 

Update: If future works (e.g. monte carlo or utility-based evolutionary algorithms) fail, I may return to this approach and let a computer run Exploding Kittens games and accumulate totals for every possible game state in a very large storage disk, which can later be retrieved through a database.


### Monte Carlo (live)
Branches: `monte4`

This could theoretically also serve as a good technique because **Exploding Kittens has no time limit per move or game**, unlike games like chess. However, I would want to ensure the AI responds with a move in a few seconds.

**Winrate: ~81%**

Interestingly this still didn't beat my direct algorithm, even after a few modifications that convinces the Monte Carlo search to consider my **Direct algorithm**.

Note: This version doesn't implement see the future cards *yet*. Because the AI also **hoards see the future cards**, I would expect that the winrate can soar over **90%** since **it often fails near the end**, when it already has many see the future cards to know that an Exploding Kitten exists.

### Utility functions

The current approach I am working on uses utility functions of every single card. This is mostly because the value of each different card varies, but is predictable. For example, a defuse card is valuable at the beginning, extremely valuable at the middle of the game, but sharply drops in use when only 1 card is left in the game since it is as useful as a skip card. See the future cards are not so valuable at the start of a game, but can sharply change the endgame's outcome since a player can know where the exploding kitten is an plan moves accordingly.

Therefore, guessing function forms and using an evolutionary algorithm to refine hyperparameters would find the proper "value" of a card at any stage in the game.

## UI
I've also worked on a UI accessible on the `ui` branch where players can play the game through a simple Flask server.


