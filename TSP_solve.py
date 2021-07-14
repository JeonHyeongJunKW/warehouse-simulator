
def solve_tsp(orders, packing_point, tsp_solve_way,distance_cost,shelf_size):
    used_packing_point = shelf_size+ (packing_point-20001)
    # print(packing_point, orders)
    refined_orders = [order-1 for order in orders]
    refined_orders = [used_packing_point] + refined_orders
    '''
    refined_orders : 리스트 형, 패킹지점과 선반의 인덱스가 적혀있음, 알고리즘이 끝나면 패킹지점, 최적화된 인덱스로 표시되어야함
    distance_cost : 2차원 리스트 형, 패킹지점과 선반들 사이의 cost가 정해져있음
    '''

    if tsp_solve_way == "NO_TSP":
        pass
    elif tsp_solve_way == "GA":
        pass
    elif tsp_solve_way == "PSO":
        pass
    elif tsp_solve_way == "ACO":
        pass


    ##풀린 경로를 반환하는 부분 건드리질 말것.
    return_orders = []
    for i, order in enumerate(refined_orders):
        if i ==0:
            continue
        else:
            return_orders.append(order+1)


    return return_orders