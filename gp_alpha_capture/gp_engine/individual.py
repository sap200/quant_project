import numpy as np
from .evaluators import evaluate
class Individual:
    def __init__(self, tree, name=None):
        self.tree = tree
        self.name = name
        self.fitness = None   # IC / RankIC / ICIR later
        self.alpha_matrix = None  # cached evaluation
        self.ic = None
        self.icir = None
        self.rank_ic = None
        self.rank_icir = None

    def evaluate(self, prices_df):
        """
        Runs GP tree → alpha matrix
        """
        self.alpha_matrix = evaluate(self.tree, prices_df)
        return self.alpha_matrix

    def set_fitness(self, fitness_value):
        self.fitness = fitness_value

    def __repr__(self):
        return f"Individual(fitness={self.fitness})"