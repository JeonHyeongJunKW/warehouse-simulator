import numpy as np
import math
from Dynamic.DEBUG_tool import DEBUG_log_tag
import random
import time

def static_aco_tsp_solver(current_position,packing_position,tsp_node, node_point_y_x):
    alpha = 1  # 페로몬 가중치
    beta = 6  # 휴리스틱 가중치
    evap = 0.80  # 남는비율 (1-증발율)
    evap_step = 1  # 증발주기
    evap_count = 0
    w_elit = 0.2  # 엘리트 엔트 추가율
    ant_size = 100  # 엔트 사이즈
    cur_it = 0
    max_it = 100
    map_size = len(tsp_node)+2
    convergence_iter =40
    aco_tsp_node = [i for i in tsp_node]
    cur_index = 0
    packing_index = map_size-1
    DEBUG_log_tag("현재 위치",[current_position[1]],"VERY_DETAIL")
    DEBUG_log_tag("피킹지점들", np.array(node_point_y_x)[:,1][aco_tsp_node].tolist(),"VERY_DETAIL")
    DEBUG_log_tag("돌아올 지점", [packing_position[1]],"VERY_DETAIL")

    heuristic_vector_x = np.array([current_position[1]]+np.array(node_point_y_x)[:,1][aco_tsp_node].tolist()+[packing_position[1]])
    heuristic_vector_y = np.array([current_position[0]]+np.array(node_point_y_x)[:,0][aco_tsp_node].tolist()+[packing_position[0]])

    # DEBUG_log_tag("x값", heuristic_vector_x, "SIMPLE")
    # DEBUG_log_tag("y값", heuristic_vector_y, "SIMPLE")
    heuristic_matrix_x = np.tile(heuristic_vector_x, reps=[len(heuristic_vector_x),1])
    heuristic_matrix_y = np.tile(heuristic_vector_y, reps=[len(heuristic_vector_y), 1])
    # DEBUG_log_tag("x 늘린거 값", heuristic_matrix_x, "SIMPLE")
    # DEBUG_log_tag("y 늘린거 값", heuristic_matrix_y, "SIMPLE")
    heuristic_map = np.sqrt((heuristic_matrix_y.T-heuristic_matrix_y)**2 +(heuristic_matrix_x.T-heuristic_matrix_x)**2)
    # DEBUG_log_tag("heuristic_matrix example",np.round_(heuristic_map,1).tolist(),"SIMPLE")

    pheromone_map = np.ones((map_size, map_size))
    pheromone_map[np.eye(map_size) == 1] = 0
    pheromone_map = pheromone_map

    # 엘리트 맵을 생성합니다.
    elit_map = np.ones((map_size, map_size))
    elit_map[np.eye(map_size) == 1] = 0

    sum_map = pheromone_map * (1 - w_elit) + elit_map * w_elit
    sub_pheromone_map = []
    for _ in range(ant_size):
        sub_pheromone_map.append(np.zeros((map_size, map_size)))
    # 각 개미에 대해서, 초기 페로몬이 0.1인 상태에서 시작한다.
    best_ant_ind = 0
    best_ant_length = 100000
    best_ant_changed = False
    best_ant_path = []
    best_path = []
    # print(heuristic_map)
    no_change = 0
    init_length = 0
    while True:
        path_list = []
        path_length = []
        for ant_ind in range(ant_size):
            '''
            처음에 개미가 시작지점을 무조건 0번이라고 하자. 그상태에서 시작임 
            각 도시에서 확률적으로 검사함
            '''
            is_not_go = list(range(map_size))
            is_not_go.remove(cur_index)  # 0번도시를 제거
            is_not_go.remove(packing_index)  # 마지막 도시를 제거
            current_city = 0  # 현재 있는 도시
            city_path = [0]
            while True:
                current_pheromone = [
                    math.pow(sum_map[current_city, i], alpha) *
                    math.pow(1 / heuristic_map[current_city, i], beta) for i in is_not_go]
                # 남은 노드중에서 페로몬을 다시구한다.

                rand_pro = random.random()
                pro_current_pheromone = [current_pheromone[h] / sum(current_pheromone) for h in
                                         range(len(current_pheromone))]
                cum_ind = 0
                cum_pro = 0
                for k, sub_pro in enumerate(pro_current_pheromone):
                    cum_pro += sub_pro
                    if rand_pro < cum_pro:
                        cum_ind = is_not_go[k]
                        break
                try:
                    is_not_go.remove(cum_ind)  # 이 노드는 들렸기때문에 제외한다.
                except ValueError:
                    print(is_not_go)
                    print(cum_ind)
                current_city = cum_ind
                city_path.append(cum_ind)  # 경로에 추가한다.
                if len(is_not_go) == 0:
                    city_path.append(packing_index)
                    break

            # 해당 경로의 길이를 구한다.
            city_path_length = 0
            for i in range(len(city_path)-1):#----------------------------------------------------------수정한 부분 마지막 경로 길이 하나가 없음..아닌가..
                city_path_length += heuristic_map[city_path[i], city_path[i + 1]]  # 전체 경로를 구한다.
            path_list.append(city_path)
            path_length.append(city_path_length)

            if best_ant_length > city_path_length:
                best_ant_path = city_path
                best_ant_ind = ant_ind
                best_ant_length = city_path_length
                best_ant_changed = True
            if cur_it ==0:
                init_length = city_path_length

        # 가장 적은 경로 확인
        small_path_index = path_length.index(min(path_length))
        small_path = path_list[small_path_index]
        if evap_count % evap_step == 0:
            pheromone_map = pheromone_map * evap
        for i in range(len(small_path) - 1):
            start = small_path[i]
            end = small_path[i + 1]
            pheromone_map[start, end] += 1 / min(path_length)
            pheromone_map[end, start] += 1 / min(path_length)
        pheromone_map = pheromone_map / pheromone_map.sum()  # 정규화

        # 만약에 지금까지 가장 낮은 해가 나왔다면
        if best_ant_changed:
            best_ant_changed = False
            elit_map = np.ones((map_size, map_size)) / (map_size * map_size)
            for i in range(len(path_list[best_ant_ind]) - 1):
                start = path_list[best_ant_ind][i]
                end = path_list[best_ant_ind][i + 1]
                elit_map[start, end] = 1 / path_length[best_ant_ind]
                elit_map[end, start] = 1 / path_length[best_ant_ind]
            elit_map = elit_map / elit_map.sum()#정규화

            no_change = 0

        sum_map = pheromone_map * (1 - w_elit) + elit_map * w_elit

        no_change += 1
        if no_change > convergence_iter:
            break
        evap_count += 1
        cur_it += 1
        if cur_it > max_it:
            break

    best_path = [tsp_node[i - 1] for i in best_ant_path[1:-1]]
    # DEBUG_log_tag("초기경로", tsp_node, "SIMPLE")
    # DEBUG_log_tag("나중경로", best_path, "SIMPLE")
    # DEBUG_log_tag("초기경로길이", init_length, "SIMPLE")
    # DEBUG_log_tag("나중경로길이", best_ant_length, "SIMPLE")
    # DEBUG_log_tag("no_change", no_change, "SIMPLE")
    # DEBUG_log_tag("cur_it", cur_it, "SIMPLE")



    return best_path