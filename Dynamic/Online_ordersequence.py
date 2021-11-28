from Dynamic.DEBUG_tool import DEBUG_log_tag, DEBUG_log
import copy
import numpy as np
from Dynamic.tsp_solver_for_online import static_aco_tsp_solver
import time
import math
import random


def update_tsp_node(robot_data, robot_index, mode="SIMPLE"):
    # 로봇의 과거배치를 받습니다.
    if len(robot_data["current_robot_batch"][robot_index]) == 0:
        print("뭔가 이상합니다..")
    past_batch = robot_data['past_robot_batch'][robot_index]
    union_batch = list(set(sum(past_batch, [])))  # 과거배치를 전부 합칩니다.

    # 로봇이 이전에 간 노드를 얻습니다.
    already_gone_node = robot_data['already_gone_node'][robot_index]
    DEBUG_log_tag("로봇의 이전의 배치 노드", already_gone_node, "VERY_DETAIL")

    # 이미 간 노드를 제거합니다.
    temp_batch = union_batch
    union_batch = [node for node in union_batch if node not in already_gone_node]
    # print("--------------------------------------------------------------")
    # print("실제에 추가된 배치",robot_data["current_robot_batch"][robot_index])
    # print("과거에 가진 배치", robot_data["past_robot_batch"][robot_index])
    # print("단독 ",union_batch)
    # print("임시 배치 ",temp_batch)
    # print("이미 간",already_gone_node)

    DEBUG_log_tag("로봇이 아직 안간 노드", union_batch, "VERY_DETAIL")

    # 배치에서 새로운 주문을 확인합니다. set을 사용하여 노드화합니다.
    DEBUG_log_tag("로봇의 과거 배치사이즈", len(past_batch), "VERY_DETAIL")
    DEBUG_log_tag("로봇의 최근 추가된 배치", robot_data['current_robot_batch'][robot_index][len(past_batch):], "VERY_DETAIL")
    DEBUG_log_tag("set연산직후", set(sum(robot_data['current_robot_batch'][robot_index][len(past_batch):], [])),
                  "VERY_DETAIL")
    new_order = list(set(sum(robot_data['current_robot_batch'][robot_index][len(past_batch):], [])))

    # 아직 가지않은 노드와 새로운 노드를 더합니다.
    if mode == "OPT":
        tsp_node = union_batch
        new_order = list(set(new_order).difference(tsp_node))
    else:
        tsp_node = list(set(new_order + union_batch))

    DEBUG_log_tag("로봇이 앞으로 가야하는 노드", tsp_node, "VERY_DETAIL")
    # 다시 초기화
    temp = copy.deepcopy(robot_data['already_gone_node'])
    temp[robot_index] = []
    robot_data['already_gone_node'] = temp

    temp = copy.deepcopy(robot_data['past_robot_batch'])
    temp[robot_index] = robot_data['current_robot_batch'][robot_index]
    robot_data['past_robot_batch'] = temp

    if mode == "OPT":
        return new_order, tsp_node
    else:
        return tsp_node


def recovery(recovery_param, point):
    point = [point[0] * recovery_param[3] + recovery_param[0], point[1] * recovery_param[2] + recovery_param[1]]
    return point


def solve_tsp_online(changed_robot_index, robot_data, node_point_y_x):
    DEBUG_log("-----SOLVE TSP : Independent------", "DETAIL")
    additional_time = 0
    additional_count = 0
    for changed_robot in changed_robot_index:
        # 로봇을 멈춥니다.

        temp = copy.deepcopy(robot_data['stop'])  # 로봇이 멈추도록설정
        temp[changed_robot] = True
        robot_data['stop'] = temp

        # 로봇의 현재위치를 받습니다.
        current_coordinate = robot_data['robot'][changed_robot].current_point
        # 로봇의 패킹지점위치를 받습니다.
        packing_coordinate = robot_data['robot'][changed_robot].home_packing_station

        current_coordinate = recovery(robot_data["packing_pose_recovery"], current_coordinate)  # 괜찮아

        packing_coordinate = recovery(robot_data["packing_pose_recovery"], packing_coordinate)  # 괜찮아

        # tsp문제에 사용할 order node를 얻습니다.
        tsp_node = update_tsp_node(robot_data, changed_robot)

        # 현재 시작 위치(노드)에 대해서 tsp문제를 풉니다.
        start_time = time.time()
        optimized_path = static_aco_tsp_solver(current_coordinate,
                                               packing_coordinate,
                                               tsp_node,
                                               node_point_y_x)
        additional_time += (time.time() - start_time)
        additional_count += 1
        # 경로를 등록합니다.
        temp = copy.deepcopy(robot_data["optimal_path"])
        temp[changed_robot] = optimized_path
        robot_data["optimal_path"] = temp

        # print("생성된 최적의 경로 : ",robot_data["optimal_path"][changed_robot])
        # 다시 움직이게 합니다.
        temp = copy.deepcopy(robot_data['stop'])
        temp[changed_robot] = False
        robot_data['stop'] = temp  # 로봇이 달리게만들어버림..

        temp = copy.deepcopy(robot_data['new_batch'])
        temp[changed_robot] = True
        robot_data['new_batch'] = temp  # 로봇이 달리게만들어버림..

    return additional_time, additional_count


def solve_tsp_opt_online(changed_robot_index, robot_data, node_point_y_x):
    additional_time = 0
    additional_count = 0
    # print("changed robot index = ", changed_robot_index)

    for changed_robot in changed_robot_index:
        # 로봇을 멈춥니다.
        temp = copy.deepcopy(robot_data['stop'])
        temp[changed_robot] = True
        robot_data['stop'] = temp

        # 로봇의 현재위치를 받습니다.
        current_coordinate = robot_data['robot'][changed_robot].current_point
        # 로봇의 패킹지점위치를 받습니다. 좌표 정보로 넘어온다.
        packing_coordinate = robot_data['robot'][changed_robot].home_packing_station

        current_coordinate = recovery(robot_data["packing_pose_recovery"], current_coordinate)
        packing_coordinate = recovery(robot_data["packing_pose_recovery"], packing_coordinate)

        # tsp문제에 사용할 order node를 얻습니다.

        new_nodes, tsp_node = update_tsp_node(robot_data, changed_robot, "OPT")
        # print("new_nodes, tsp_node = ", new_nodes, tsp_node)
        check = copy.deepcopy(robot_data["optimal_path"])
        start_time = time.time()
        if len(tsp_node) == 0:
            # alg_time1 = time.time()
            tsp_node = new_nodes
            optimized_path = static_aco_tsp_solver(current_coordinate,
                                                   packing_coordinate,
                                                   tsp_node,  # 이부분에서 다시 추가 안되게 해야한다.
                                                   node_point_y_x)
            # print("ACO = ", time.time() - alg_time1)
        else:

            optimized_path = check[changed_robot]
            optimized_path = opt_tsp_solver(current_coordinate,
                                            packing_coordinate,
                                            optimized_path,
                                            new_nodes,
                                            node_point_y_x)

        additional_time += (time.time() - start_time)
        additional_count += 1
        # optimal path의 index를 가져온다.

        temp = copy.deepcopy(robot_data["optimal_path"])
        temp[changed_robot] = optimized_path
        robot_data["optimal_path"] = temp  # 기존 tsp로 저장한 최적의 경로

        # print("생성된 최적의 경로 : ",robot_data["optimal_path"][changed_robot])
        # 다시 움직이게 합니다.
        temp = copy.deepcopy(robot_data['stop'])
        temp[changed_robot] = False
        robot_data['stop'] = temp

        temp = copy.deepcopy(robot_data['new_batch'])
        temp[changed_robot] = True
        robot_data['new_batch'] = temp  # 로봇이 달리게만들어버림..

    return additional_time, additional_count


def opt_tsp_solver(current_coordinate, packing_coordinate, opt_nodes, new_nodes, node_point_y_x):
    # opt_path : 최적의 경로 인덱스 list 형

    first_point = current_coordinate
    first_ind = 1000
    end_point = packing_coordinate
    end_ind = 2000

    # rest_node 의 값을 통해서 edge 생성하기
    rest_edge = [[opt_nodes[i], opt_nodes[i + 1]] for i in range(len(opt_nodes) - 1)]
    rest_edge.insert(0, [first_ind, opt_nodes[0]])
    rest_edge.append([opt_nodes[-1], end_ind])

    best_route = []

    # print("new_nodes = ", new_nodes)
    for new_node in new_nodes:
        # print("current_node = ", new_node)
        best_score = math.inf
        for i in range(math.ceil(len(rest_edge))):
            random_ind = random.randrange(len(rest_edge))
            test_edge = copy.deepcopy(rest_edge)
            del_ind = test_edge.pop(random_ind)

            test_edge.insert(random_ind, [new_node, del_ind[1]])
            test_edge.insert(random_ind, [del_ind[0], new_node])
            opt_route = test_edge

            check_score = sum([math.dist(node_point_y_x[opt_route[i][0]],
                                         node_point_y_x[opt_route[i][1]]) for i in range(1, (len(opt_route) - 1))])
            check_score = check_score + math.dist(first_point, node_point_y_x[opt_route[0][1]]) + math.dist(
                node_point_y_x[opt_route[-1][0]], end_point)

            if best_score > check_score:
                best_score = check_score
                best_route = opt_route

        rest_edge = best_route

    best_route = opt_check(best_route, first_point, end_point, node_point_y_x, best_score, best_route)
    # best_route(edge)를 ind 로 변환
    set_ind = []
    result = []

    for point in best_route:
        set_ind = set_ind + point
    for value in set_ind:
        if value not in result:
            result.append(value)
    del result[0]
    del result[-1]

    return result


def opt_check(input_route, first_point, end_point, node_point_y_x, best_score, opt_route):
    action_flag = True
    route = copy.deepcopy(input_route)
    # opt 를 통해서 경로를 수정한다.

    next_point = 2

    for ind1 in range(len(route)):
        opt_score = best_score
        ind_list = [ind1 - 1, ind1, ind1 + 1]
        m_edge = route[ind1]
        if ind1 == len(route) - 1:
            break

        for ind2 in range(len(route)):
            c_edge = route[ind2]
            if ind2 in ind_list or ind2 < ind1:
                continue
            # print("ind1 , ind2 = ", ind1, ind2)
            sub_route = copy.deepcopy(route)
            # print("before_sub_route =", sub_route)
            change_edge1 = [m_edge[0], c_edge[0]]
            change_edge2 = [m_edge[1], c_edge[1]]
            # print("change_edge =", change_edge1, change_edge2)
            sub_route.insert(ind1, change_edge1)
            sub_route.remove(sub_route[ind1 + 1])

            # print("sum_ind = ", ind2)
            sub_route.insert(ind2, change_edge2)
            sub_route.remove(sub_route[ind2 + 1])

            score = sum([math.dist(node_point_y_x[sub_route[i][0]],
                                   node_point_y_x[sub_route[i][1]]) for i in range(1, (len(sub_route) - 1))])
            score = score + math.dist(first_point, node_point_y_x[sub_route[0][1]]) + math.dist(
                node_point_y_x[sub_route[-1][0]], end_point)

            if opt_score > score:
                opt_score = score
                opt_route = resolve_route(sub_route, ind1, ind2)
            # print("after_sub_route =", sub_route, "\n")
        route = opt_route  # 정렬하는 코드가 필요
        best_score = opt_score
        next_point += 1

    return route


def resolve_route(route, ind1, ind2):
    # print("route = ",route)

    gap_route = route[ind1 + 1: ind2]
    # print("gap_route =", gap_route)
    gap_route.reverse()  # 리버스 바꾸기
    # print("gap_route =", gap_route)

    for i, edge in enumerate(gap_route):
        # print(edge)
        edge.reverse()
        # print(edge)
        route[i + ind1 + 1] = edge

    return route


def NN_tsp_solver(current_coordinate, packing_coordinate, opt_path, gone_node, new_nodes, node_point_y_x):
    first_point = node_point_y_x[current_coordinate]
    end_point = node_point_y_x[packing_coordinate]
    # optimal path에서 지나온 지점 제거
    opt_node = np.array(opt_path)
    rest_node = np.setdiff1d(opt_node, gone_node).tolist()  # 수정이 필요

    for new_node in new_nodes:

        check_dis = []
        sum_dis = []

        for rest in rest_node:
            opt_len = math.dist(node_point_y_x[rest], node_point_y_x[new_node])
            check_dis.append(opt_len)

        for i in range(len(check_dis) - 1):
            check_sum = check_dis[i] + check_dis[i + 1]
            sum_dis.append(check_sum)

        ind = max(sum_dis)
        max_ind = sum_dis.index(ind)
        rest_node.insert(new_node, max_ind + 1)

    return rest_node
