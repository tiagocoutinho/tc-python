import collections
import random

pizza = 0
hotdog = 1
hamburger = 2

population = pizza, hotdog, hamburger

probs = {
  (pizza,hotdog): 7,
  (pizza, hamburger): 3,
  (hamburger, pizza): 6,
  (hamburger,hamburger): 2,
  (hamburger,hotdog): 2,
  (hotdog, hamburger): 5,
  (hotdog, hotdog): 5,
}

transition_matrix = [[
    probs.get((row, col), 0) for col in population]
    for row in population
]

state_weights = {}
for state in population:
    cum_weights = []
    weight = 0
    for next_state in population:
        weight += probs.get((state, next_state), 0)
        cum_weights.append(weight)
    state_weights[state] = cum_weights


def step(state, k=1):
    return random.choices(population, cum_weights=state_weights[state], k=k)


def walk(state, n):
    for i in range(n):
        state = step(state)[0]
        yield state


def markov(population, cum_weights, n):
    state = random.choice(population)
    states = walk(state, n)
    counts = collections.Counter(states)
    return {state: count / n for state, count in counts.items()}

