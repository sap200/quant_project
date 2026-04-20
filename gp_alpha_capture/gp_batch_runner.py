from gp_engine.gp import GeneticProgramming
from gp_engine.individual import Individual
from gp_engine.population import Population
from gp_engine.evaluators import evaluate
from gp_engine.fitness import compute_fitness
from gp_engine.node import print_tree


# =========================================================
# RUN ONE GP INSTANCE
# =========================================================

def run_single_gp(seed_tree, X_train, y_train):

    seed_ind = Individual(seed_tree, name="seed")

    population = Population([seed_ind])

    gp = GeneticProgramming(
        initial_population=population,
        price_df=X_train,
        returns_df=y_train,
        npop=30,
        pcrossover=0.4,
        pmutation=0.5,
        max_generations=25,
        tournament_k=5,
        verbose=False
    )

    best = gp.run()

    return best


# =========================================================
# RUN MULTIPLE GPS (CORE DESIGN)
# =========================================================

def run_gp_batch(seed_alphas, X_train, y_train):

    evolved = []
    seeds = []

    for i, tree in enumerate(seed_alphas):

        # print(f"\n====================")
        # print(f"RUNNING GP {i}")
        # print(f"====================")

        best = run_single_gp(tree, X_train.copy(), y_train.copy())

        seeds.append(tree)
        evolved.append(best.tree)

    return seeds, evolved