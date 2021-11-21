from Dynamic.DEBUG_tool import DEBUG_log_tag,DEBUG_log

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