from Dynamic.DEBUG_tool import DEBUG_log_tag,DEBUG_log
import copy
import numpy as np
from Dynamic.tsp_solver_for_online import static_aco_tsp_solver
import time

def update_tsp_node(robot_data,robot_index):
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
    DEBUG_log_tag("set연산직후", set(sum(robot_data['current_robot_batch'][robot_index][len(past_batch):],[])), "VERY_DETAIL")
    new_order = list(set(sum(robot_data['current_robot_batch'][robot_index][len(past_batch):],[])))

    # 아직 가지않은 노드와 새로운 노드를 더합니다.
    tsp_node = list(set(new_order + union_batch))
    DEBUG_log_tag("로봇이 앞으로 가야하는 노드", tsp_node, "VERY_DETAIL")
    # 다시 초기화
    temp = copy.deepcopy(robot_data['already_gone_node'])
    temp[robot_index] = []
    robot_data['already_gone_node'] = temp

    temp = copy.deepcopy(robot_data['past_robot_batch'])
    temp[robot_index] =robot_data['current_robot_batch'][robot_index]
    robot_data['past_robot_batch'] =temp


    return tsp_node
def recovery(recovery_param,point):
    point = [point[0]*recovery_param[3]+recovery_param[0], point[1]*recovery_param[2]+recovery_param[1]]
    return point

def solve_tsp_online(changed_robot_index,robot_data,node_point_y_x):
    DEBUG_log("-----SOLVE TSP : Independent------","DETAIL")
    additional_time =0
    additional_count =0
    for changed_robot in changed_robot_index:
        # 로봇을 멈춥니다.


        temp = copy.deepcopy(robot_data['stop'])
        temp[changed_robot] = True
        robot_data['stop'] = temp
        '''
        robot_pos_x = math.floor((saved_pk_point[packing_ind][0] - init_map_x) / res_width)
        robot_pos_y = math.floor((saved_pk_point[packing_ind][1] - init_map_y) / res_height)
        '''



        # 로봇의 현재위치를 받습니다.
        current_coordinate =robot_data['robot'][changed_robot].current_point
        # 로봇의 패킹지점위치를 받습니다.
        packing_coordinate =robot_data['robot'][changed_robot].home_packing_station

        current_coordinate = recovery(robot_data["packing_pose_recovery"], current_coordinate)

        packing_coordinate = recovery(robot_data["packing_pose_recovery"], packing_coordinate)

        #tsp문제에 사용할 order node를 얻습니다.
        tsp_node = update_tsp_node(robot_data, changed_robot)

        #현재 시작 위치(노드)에 대해서 tsp문제를 풉니다.
        start_time = time.time()
        optimized_path= static_aco_tsp_solver(current_coordinate,
                                               packing_coordinate,
                                               tsp_node,
                                               node_point_y_x)
        additional_time +=(time.time()-start_time)
        additional_count +=1
        #경로를 등록합니다.
        temp = copy.deepcopy(robot_data["optimal_path"])
        temp[changed_robot] = optimized_path
        robot_data["optimal_path"] = temp

        # print("생성된 최적의 경로 : ",robot_data["optimal_path"][changed_robot])
        #다시 움직이게 합니다.
        temp = copy.deepcopy(robot_data['stop'])
        temp[changed_robot] = False
        robot_data['stop'] = temp#로봇이 달리게만들어버림..

        temp = copy.deepcopy(robot_data['new_batch'])
        temp[changed_robot] = True
        robot_data['new_batch'] = temp  # 로봇이 달리게만들어버림..

    return additional_time, additional_count





