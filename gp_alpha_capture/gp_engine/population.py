import random
from .fitness import compute_fitness

class Population:
    def __init__(self, individuals):
        self.individuals = individuals

    def evaluate_all(self, price_df):
        """
        Evaluate all individuals → alpha matrices
        """
        for ind in self.individuals:
            ind.evaluate(price_df)

    def set_fitness_all(self, returns_df):
        """
        fitness_fn(individual) → scalar IC score
        """
        for ind in self.individuals:
            f = compute_fitness(ind, returns_df)
            ind.set_fitness(f)

    def get_best(self):
        return max(self.individuals, key=lambda x: x.fitness)

    def tournament_selection(self, k=3):
        """
        pick best of k random individuals
        """
        k = min(k, len(self.individuals))
        candidates = random.sample(self.individuals, k)
        return max(candidates, key=lambda x: x.fitness)

    def size(self):
        return len(self.individuals)