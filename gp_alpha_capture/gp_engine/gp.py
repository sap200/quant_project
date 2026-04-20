import random
import copy

from .population import Population
from .individual import Individual

from .mutation import point_mutation
from .crossover import restricted_crossover
from .node import trees_equal
from tqdm import tqdm


class GeneticProgramming:
    def __init__(
        self,
        initial_population,   # Population object
        price_df,             # X (features)
        returns_df,           # Y (forward returns)
        npop=20,
        pcrossover=0.5,
        pmutation=0.4,
        max_generations=20,
        tournament_k=3,
        verbose=False
    ):
        self.population = initial_population

        self.price_df = price_df
        self.returns_df = returns_df

        self.npop = npop

        self.pcrossover = pcrossover
        self.pmutation = pmutation

        self.max_generations = max_generations
        self.tournament_k = tournament_k
        self.verbose=verbose

    # =====================================================
    # DUPLICATE CHECK (OPTIONAL BUT USEFUL)
    # =====================================================
    
    def is_duplicate(self, individual, population):
        for ind in population:
            if trees_equal(ind.tree, individual.tree):
                return True
        return False

    # =====================================================
    # MAIN LOOP
    # =====================================================



    def run(self):
        
        if self.verbose:
            print("Running GP")

        self.population.evaluate_all(self.price_df)
        self.population.set_fitness_all(self.returns_df)
        

        best = self.population.get_best()
        if self.verbose:
            print("Best:", best)

        # =====================================================
        # EVOLUTION LOOP
        # =====================================================
        best_icir = -float("inf")
        pbar = tqdm(range(self.max_generations), desc="GP Evolution", disable=not self.verbose)

        for t in pbar:

            new_individuals = []

            # -------------------------
            # ELITISM (Line 10)
            # -------------------------
            best = self.population.get_best()
            new_individuals.append(copy.deepcopy(best))

            # -------------------------
            # BUILD NEW POPULATION
            # -------------------------
            while len(new_individuals) < self.npop:

                # ---------------------
                # MUTATION SELECTION
                # ---------------------
                if (t + 1) == 1:
                    mutation_type = "point"   # forced in first gen
                else:
                    r = random.random()

                    if r < self.pcrossover:
                        mutation_type = "crossover"
                    elif r < self.pcrossover + self.pmutation:
                        mutation_type = "point"
                    else:
                        mutation_type = "reproduce"

                # ---------------------
                # CROSSOVER
                # ---------------------
                if mutation_type == "crossover":

                    p1 = self.population.tournament_selection(self.tournament_k)
                    p2 = self.population.tournament_selection(self.tournament_k)

                    child1_tree, _ = restricted_crossover(p1.tree, p2.tree)

                    children = [Individual(child1_tree)]

                # ---------------------
                # POINT MUTATION
                # ---------------------
                elif mutation_type == "point":

                    p = self.population.tournament_selection(self.tournament_k)

                    new_tree = point_mutation(p.tree)

                    children = [Individual(new_tree)]

                # ---------------------
                # REPRODUCTION (COPY)
                # ---------------------
                else:

                    p = self.population.tournament_selection(self.tournament_k)

                    children = [Individual(copy.deepcopy(p.tree))]

                # ---------------------
                # INSERT OFFSPRING
                # ---------------------
                for child in children:

                    if len(new_individuals) >= self.npop:
                        break

                    if not self.is_duplicate(child, new_individuals):
                        new_individuals.append(child)

            # -------------------------
            # NEXT GENERATION
            # -------------------------
            self.population = Population(new_individuals)

            # evaluate
            self.population.evaluate_all(self.price_df)

            # fitness
            self.population.set_fitness_all(self.returns_df)

            best = self.population.get_best()

            if best.fitness > best_icir:
                best_icir = best.fitness
    
            pbar.set_postfix(best_icir=best_icir)

        # -------------------------
        # FINAL RESULT
        # -------------------------
        return self.population.get_best()