import copy
import random

from .node import print_tree


# =========================================================
# TREE UTILITIES
# =========================================================

def get_nodes_with_path(node, path=None):
    """
    Returns list of (node, path)
    path = list of child indices from root
    """

    if path is None:
        path = []

    nodes = [(node, path)]

    for i, child in enumerate(node.children):
        nodes.extend(get_nodes_with_path(child, path + [i]))

    return nodes


def get_node_by_path(root, path):
    node = root
    for i in path:
        node = node.children[i]
    return node


def set_node_by_path(root, path, new_subtree):
    node = root
    for i in path[:-1]:
        node = node.children[i]

    node.children[path[-1]] = new_subtree


# =========================================================
# RESTRICTED CROSSOVER (YOUR SPEC)
# =========================================================

def restricted_crossover(parent1, parent2, debug=False):
    """
    Symmetric subtree swap at SAME structural position
    """

    p1 = copy.deepcopy(parent1)
    p2 = copy.deepcopy(parent2)

    # -------------------------
    # GET ALL VALID PATHS (EXCLUDE ROOT)
    # -------------------------
    nodes1 = get_nodes_with_path(p1)

    candidate_paths = [
        path for (_, path) in nodes1
        if len(path) > 0   # exclude root
    ]

    if not candidate_paths:
        return p1, p2

    # -------------------------
    # RANDOM POSITION FROM PARENT1
    # -------------------------
    path = random.choice(candidate_paths)

    # -------------------------
    # EXTRACT SUBTREES FROM SAME POSITION
    # -------------------------
    subtree1 = get_node_by_path(p1, path)
    subtree2 = get_node_by_path(p2, path)
    
    # -------------------------
    # BEFORE SWAP SUBTREES
    # -------------------------
    subtree1_before = get_node_by_path(p1, path)
    subtree2_before = get_node_by_path(p2, path)

    # -------------------------
    # DEEP COPY (IMPORTANT) 
    # -------------------------
    subtree1_copy = copy.deepcopy(subtree1)
    subtree2_copy = copy.deepcopy(subtree2)
    

    # -------------------------
    # SWAP
    # -------------------------
    set_node_by_path(p1, path, subtree2_copy)
    set_node_by_path(p2, path, subtree1_copy)
    
    # -------------------------
    # AFTER SWAP SUBTREES
    # -------------------------
    subtree1_after = get_node_by_path(p1, path)
    subtree2_after = get_node_by_path(p2, path)
    
    # -------------------------
    # DEBUG OUTPUT
    # -------------------------
    if debug:
        print("\n================ CROSSOVER DEBUG ================\n")
        print("Selected path:", path)

        print("\n--- BEFORE SWAP ---")
        print("\nParent1 subtree:")
        print_tree(subtree1_before)

        print("\nParent2 subtree:")
        print_tree(subtree2_before)

        print("\n--- AFTER SWAP ---")
        print("\nParent1 new subtree:")
        print_tree(subtree1_after)

        print("\nParent2 new subtree:")
        print_tree(subtree2_after)

        print("\n--- FULL CHILD 1 ---")
        print_tree(p1)

        print("\n--- FULL CHILD 2 ---")
        print_tree(p2)


    return p1, p2