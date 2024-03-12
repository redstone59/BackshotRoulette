# Backshot Roulette

A bot that finds the best move in any given position of Buckshot Roulette.
It does this by minimising the chance that the Dealer can kill the Player.

# How does it work?

There are two major parts the bot, searching and evaluating.

## Searching

Searching consists of the following steps, finding obvious moves, predicting move evaluation if there are no obvious moves, then doing a minimax search.

### Finding "Obvious Moves"

In order to save time and prune nodes from the tree, in specific circumstance, the bot will only check one move only.

| Condition | Obvious Move |
| --------- | ------------ |
| Is the shell live and the current player does not have a hand saw? | Shoot the other player |
| Is the shell live, does the current player has a hand saw, and is the other player's health is equal to 2? | Use the hand saw |
| Is the shell blank? | Shoot self |
| Does the current player have a magnifying glass, and is the current shell unknown? | Use the magnifying glass |
| Is the current player not on maximum health? | Use cigarettes |
| Is there more than 2 shells in the gun, with at least one blank shell? | Use handcuffs |

### Predicting Evaluation

If there is no obvious move in the position, it will get all moves and predict evaluation based on the following criteria.

### Minimax Search

Backshot Roulette uses a minimax search with alpha-beta pruning. 
Essentially, the bot goes through every possible position and picks the move that leads to the best possible evaluation.

For a better explanation, see [this video](https://www.youtube.com/watch?v=l-hh51ncgDI).

## Evaluating

