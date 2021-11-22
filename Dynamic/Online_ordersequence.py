from Dynamic.DEBUG_tool import DEBUG_log_tag,DEBUG_log
import copy
import numpy as np
from Dynamic.tsp_solver_for_online import static_aco_tsp_solver


def update_tsp_node(robot_data,robot_index):
    # 로봇의 과거배치를 받습니다.
    past_batch = robot_data['past_robot_batch'][robot_index]
    union_batch = np.array(list(set(sum(past_batch, []))))  # 과거배치를 전부 합칩니다.

    # 로봇이 이전에 간 노드를 얻습니다.
    already_gone_node = robot_data['already_gone_node'][robot_index]
    DEBUG_log_tag("로봇의 이전의 배치 노드", union_batch, "VERY_DETAIL")

    # 이미 간 노드를 제거합니다.
    union_batch = np.delete(union_batch, already_gone_node)
    DEBUG_log_tag("로봇이 아직 안간 노드", union_batch, "VERY_DETAIL")

    # 배치에서 새로운 주문을 확인합니다. set을 사용하여 노드화합니다.
    DEBUG_log_tag("로봇의 과거 배치사이즈", len(past_batch), "VERY_DETAIL")
    DEBUG_log_tag("로봇의 최근 추가된 배치", robot_data['current_robot_batch'][robot_index][len(past_batch):], "VERY_DETAIL")
    DEBUG_log_tag("set연산직후", set(sum(robot_data['current_robot_batch'][robot_index][len(past_batch):],[])), "VERY_DETAIL")
    new_order = list(set(sum(robot_data['current_robot_batch'][robot_index][len(past_batch):],[])))

    # 아직 가지않은 노드와 새로운 노드를 더합니다.
    tsp_node = list(set(new_order + union_batch.tolist()))
    DEBUG_log_tag("로봇이 앞으로 가야하는 노드", tsp_node, "VERY_DETAIL")

    # 다시 초기화
    robot_data['already_gone_node'][robot_index] = []# 이미 간 노드를
    robot_data['past_robot_batch'][robot_index] = robot_data['current_robot_batch']


    return tsp_node

def solve_tsp_online(changed_robot_index,robot_data,node_point_y_x):
    DEBUG_log("-----SOLVE TSP : Independent------","DETAIL")

    '''
    1. 바뀐 tsp각 로봇별로 정지시키고, 현재위치에서 이미 간곳을 제외하고 tsp를 다시 풉니다. 
        필요한 정보 
            - 각 로봇이 이전 배치에서 현재까지 이동한 노드
            - 각 로봇이 이전 배치에서 아직 이동하지 않은 노드 
            - 각 로봇의 현재 위치 
            - 각 로봇의 추가된 노드들  
    2. 하나를 풀때마다 먼저 이동시킨다.
    '''
    for changed_robot in changed_robot_index:
        # 로봇을 멈춥니다.
        temp = copy.deepcopy(robot_data['stop'])
        temp[changed_robot] = True
        robot_data['stop'] = temp
        # 로봇의 현재위치를 받습니다.
        current_coordinate =robot_data['robot'][changed_robot].current_point

        # 로봇의 패킹지점위치를 받습니다.
        packing_coordinate =robot_data['robot'][changed_robot].home_packing_station

        #tsp문제에 사용할 order node를 얻습니다.
        tsp_node = update_tsp_node(robot_data, changed_robot)

        #현재 시작 위치(노드)에 대해서 tsp문제를 풉니다.
        optimized_path = static_aco_tsp_solver(current_coordinate,
                                               packing_coordinate,
                                               tsp_node,
                                               node_point_y_x)
        #경로를 등록합니다.
        temp = copy.deepcopy(robot_data["optimal_path"])
        temp[changed_robot] = optimized_path
        robot_data["optimal_path"] = temp

        # print("생성된 최적의 경로 : ",robot_data["optimal_path"][changed_robot])
        #다시 움직이게 합니다.
        temp = copy.deepcopy(robot_data['stop'])
        temp[changed_robot] = False
        robot_data['stop'] = temp





