from individual import Individual

MUTATION_RATE = 0.105
N = 1000

def percent(pop):
    count = 0
    for i in range(len(pop)):
        if pop[i].needs_evaluation:
            count += 1
    return count

def set_false(pop):
    for ind in pop:
        ind.needs_evaluation = False

def mutate(pop):
    for ind in pop:
        ind.mutate(MUTATION_RATE)

pop = [Individual() for _ in range(100)]

count = 0
for _ in range(N):
    set_false(pop)
    mutate(pop)
    count += percent(pop)
print(count / N /100)
