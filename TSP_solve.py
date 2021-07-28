import ACO
from DC import *
from PSO import *
from NN import *
import Genetic_TSP as gen
import time
import math


def solve_tsp(orders, packing_point, tsp_solve_way,distance_cost,shelf_size,real_cordinate):
    used_packing_point = shelf_size+ (packing_point-20001)
    # print(packing_point, orders)
    refined_orders = [order-1 for order in orders]
    refined_orders = [used_packing_point] + refined_orders
    '''
    refined_orders : 리스트 형, 패킹지점과 선반의 인덱스가 적혀있음, 알고리즘이 끝나면 패킹지점, 최적화된 인덱스로 표시되어야함
    distance_cost : 2차원 리스트 형, 패킹지점과 선반들 사이의 cost가 정해져있음
    real_cordinate : 2차원 리스트 형, 패킹지점과 선반들의 [y,x]좌표가 들어가있다.
    '''
    # print("origin",refined_orders)
    if tsp_solve_way == "NO_TSP":
        pass
    elif tsp_solve_way == "GA":
        refined_orders = gen.get_path(refined_orders, distance_cost)
    elif tsp_solve_way == "PSO":
        refined_orders = tsp_pso(refined_orders, distance_cost)
    elif tsp_solve_way == "ACO":
        refined_orders = ACO.get_path(refined_orders, distance_cost)
    elif tsp_solve_way == "DC":
        refined_orders = tsp_dc(refined_orders, distance_cost, real_cordinate)
    elif tsp_solve_way == "GREEDY":
        refined_orders = tsp_nn(refined_orders, distance_cost)



    ##풀린 경로를 반환하는 부분 건드리질 말것.
    return_orders = []
    for i, order in enumerate(refined_orders):
        if i == 0:
            continue
        else:
            return_orders.append(order+1)


    return return_orders

def get_length(refined_orders, distance_cost):
    full_length =0
    # print(len(refined_orders))
    lengths = []
    cumul_lenths =[]
    for i in range(len(refined_orders)-1):
        full_length += distance_cost[refined_orders[i]][refined_orders[i+1]]
        cumul_lenths.append(full_length)
        lengths.append(distance_cost[refined_orders[i]][refined_orders[i+1]])
    full_length+=distance_cost[refined_orders[-1]][refined_orders[0]]
    lengths.append(distance_cost[refined_orders[-1]][refined_orders[0]])
    cumul_lenths.append(full_length)

    # print(lengths)
    # print(cumul_lenths)
    return full_length

def solve_tsp_all_algorithm(orders, packing_point, tsp_solve_way,distance_cost,shelf_size,real_cordinate,already_answer,duration):
    used_packing_point = shelf_size+ (packing_point-20001)
    # print(packing_point, orders)
    refined_orders = [order-1 for order in orders]
    refined_orders = [used_packing_point] + refined_orders
    '''
    refined_orders : 리스트 형, 패킹지점과 선반의 인덱스가 적혀있음, 알고리즘이 끝나면 패킹지점, 최적화된 인덱스로 표시되어야함
    distance_cost : 2차원 리스트 형, 패킹지점과 선반들 사이의 cost가 정해져있음
    real_cordinate : 2차원 리스트 형, 패킹지점과 선반들의 [y,x]좌표가 들어가있다.
    '''
    # print("origin",refined_orders)
    all_route = []
    all_length = []
    all_time = []
    return_orders = []

    all_route.append(refined_orders)
    all_length.append(get_length(all_route[0], distance_cost))
    all_time.append(0)
    #GA
    if tsp_solve_way == "GA":
        refined_orders_pre = [order - 1 for order in already_answer]
        refined_orders_pre = [used_packing_point] + refined_orders_pre
        all_route.append(refined_orders_pre)
        all_length.append(get_length(all_route[1], distance_cost))
        all_time.append(duration)
    else:
        start = time.time()
        refined_orders_2 = gen.get_path(refined_orders, distance_cost)
        end = time.time()
        all_route.append(refined_orders_2)
        all_length.append(get_length(all_route[1], distance_cost))
        all_time.append(end - start)
    #PSO

    if tsp_solve_way == "PSO":

        refined_orders_pre = [order - 1 for order in already_answer]
        refined_orders_pre = [used_packing_point] + refined_orders_pre
        all_route.append(refined_orders_pre)
        all_length.append(get_length(all_route[2], distance_cost))
        all_time.append(duration)

    else:
        start = time.time()
        refined_orders_3 = tsp_pso(refined_orders, distance_cost)
        all_route.append(refined_orders_3)
        all_length.append(get_length(all_route[2], distance_cost))
        end = time.time()
        all_time.append(end - start)

    #ACO
    if tsp_solve_way == "ACO":
        refined_orders_pre = [order - 1 for order in already_answer]
        refined_orders_pre = [used_packing_point] + refined_orders_pre
        all_route.append(refined_orders_pre)
        all_length.append(get_length(all_route[3], distance_cost))
        all_time.append(duration)
    else:
        start = time.time()
        refined_orders_4 = ACO.get_path(refined_orders, distance_cost)
        end = time.time()
        all_route.append(refined_orders_4)
        all_length.append(get_length(all_route[3], distance_cost))
        all_time.append(end - start)

    if tsp_solve_way == "DC":
        refined_orders_pre = [order - 1 for order in already_answer]
        refined_orders_pre = [used_packing_point] + refined_orders_pre
        all_route.append(refined_orders_pre)
        all_length.append(get_length(all_route[4], distance_cost))
        all_time.append(duration)
    else:
        start = time.time()
        refined_orders_5 = tsp_dc(refined_orders, distance_cost,real_cordinate)
        end = time.time()
        all_route.append(refined_orders_5)
        all_length.append(get_length(all_route[4], distance_cost))
        all_time.append(end - start)

    #NN

    if tsp_solve_way == "NN":
        refined_orders_pre = [order - 1 for order in already_answer]
        refined_orders_pre = [used_packing_point] + refined_orders_pre
        all_route.append(refined_orders_pre)
        all_length.append(get_length(all_route[5], distance_cost))
    else:
        start = time.time()
        refined_orders_6 = tsp_nn(refined_orders, distance_cost)
        end = time.time()
        all_route.append(refined_orders_6)
        all_length.append(get_length(all_route[5], distance_cost))
        all_time.append(end - start)

    #각 알고리즘별 시간과 거리

    # print("length", all_length)
    print("time", all_time)

    return all_route, all_length, all_time