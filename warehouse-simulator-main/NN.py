import math


def run_nn(index, distance_cost):
    check_flag = True
    path = [index[0]]
    index.pop(0)
    while check_flag:
        min_cost = math.inf
        for num, end in enumerate(index):
            cost = distance_cost[path[-1]][end]
            if cost < min_cost:
                min_cost = cost
                best_index = num
                best_ind = end
        path.append(index[best_index])
        index.pop(best_index)

        if not index:
            check_flag = False

    return path


def tsp_nn(index, distance_cost):
    check = index[:]
    return run_nn(check, distance_cost)