import numpy as np
import pandas as pd

from gp_engine.node import Node, print_tree
from gp_engine.individual import Individual
from gp_engine.population import Population
from gp_engine.evaluators import evaluate
from gp_engine.fitness import compute_fitness


from gp_engine.gp import GeneticProgramming

from splitter import (
    get_feature_matrix,
    build_forward_returns,
    train_test_split_time
)

from data_collector import load_data, calculate_close_returns, TICKERS  
from gp_engine.build_alpha101 import build_alpha_conditional


def run(df):

    X = get_feature_matrix(df)

    y = build_forward_returns(df, horizon=5)

    # STEP 3: ALIGN + SPLIT
    X_train, X_test, y_train, y_test = train_test_split_time(X, y, test_ratio=0.2)

    print("Train shape:", X_train.shape, y_train.shape)
    print("Test shape:", X_test.shape, y_test.shape)

    # -------------------------
    # STEP 4: INITIAL INDIVIDUAL
    # -------------------------
    seed_tree = build_alpha_conditional()
    
        


    seed_ind = Individual(seed_tree, name="seed_alpha")

    population = Population([seed_ind])


    gp = GeneticProgramming(
        initial_population=population,
        price_df=X_train,
        returns_df=y_train,
        npop=50,
        pcrossover=0.5,
        pmutation=0.4,
        max_generations=25,
        tournament_k=3
    )

    best = gp.run()

    print("\n========================")
    print("FINAL TRAIN BEST ALPHA")
    print("========================")
    print(best)
    
    print("\n========================")
    print("INITIAL ALPHA TREE")
    print("========================")
    print_tree(seed_tree)
    
    print("\n========================")
    print("EVOLVED ALPHA TREE")
    print("========================")
    print_tree(best.tree)
    # -------------------------
    # STEP 7: TEST EVALUATION
    # -------------------------
    print("\n========================")
    print("OUT OF SAMPLE TEST")
    print("========================")
    
    

    test_alpha = evaluate(best.tree, X_test)

    # compute test IC manually using your fitness function logic
    test_ind = Individual(best.tree)
    test_ind.alpha_matrix = test_alpha

    test_icir = compute_fitness(test_ind, y_test)

    print("TEST RankICIR:", test_icir)

    return best


if __name__ == "__main__":


    df = load_data()
    df = calculate_close_returns(df, tickers=TICKERS)

    best = run(df)

    # print("\nBEST ALPHA:", best)