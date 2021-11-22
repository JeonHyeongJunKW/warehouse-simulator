from Dynamic.DEBUG_tool import DEBUG_log_tag,DEBUG_log
import copy
import time

def make_astar_path_robot(robot, shelf_grid_list, occupy_map, optimal_path):
    part_shelf_grid = []

    for shelf_grid in optimal_path:  # 처음 노드를 제외한 나머지 노드에 대한 피킹 주변지역을 얻습니다.
        part_shelf_grid.append(shelf_grid_list[shelf_grid])  # 실제 shelf 격자들을 얻어온다.
    robot.assign_work_astar(optimal_path,part_shelf_grid,occupy_map)
    return robot
def restart_robot(robot_data,robot_ind):
    temp = robot_data["optimal_path"]
    temp[robot_ind] = []
    robot_data["optimal_path"] = temp

    temp = robot_data["already_gone_node"]
    temp[robot_ind] = []
    robot_data["already_gone_node"] = temp

    temp = robot_data["current_robot_batch"]
    temp[robot_ind] = []
    robot_data["current_robot_batch"] = temp

    temp = copy.deepcopy(robot_data['stop'])
    temp[robot_ind] = True
    robot_data['stop'] = temp


def action_control( robot_data,shelf_grid_list,occupy_map):
    # 로봇 데이터를 기반으로 하여 현재 로봇을 움직인다.
    DEBUG_log("로봇 제어 시작.")
    robots = copy.deepcopy(robot_data['robot'])  # 임시 로봇을 가져온다.
    self_rebatch_flag = [True for _ in range(len(robots))]
    while True:
        start = time.time()


        robots = copy.deepcopy(robot_data['robot'])#임시 로봇을 가져온다.

        if robot_data["reset"]:
            break
        for robot_ind in range(len(robots)):
            # print("로봇은 멈춰야하는가 ?",robot_data['stop'][robot_ind])
            #로봇이 멈춰야한다면 움직이지 않는다.
            if robot_data['stop'][robot_ind]:
                self_rebatch_flag[robot_ind] = True#멈추는 플래그가 열리면, rebatch가 True가된다.
                continue
            else:
            #로봇이 움직여야한다면
                robot = robots[robot_ind]
                #만약에 로봇이 새로운 배치를 할당받앗다면
                if self_rebatch_flag[robot_ind]:
                    self_rebatch_flag[robot_ind] = False
                    optimal_path = robot_data["optimal_path"][robot_ind]

                    DEBUG_log_tag("새로운 배치가 도착하였습니다.",optimal_path)

                    new_robot = make_astar_path_robot(robot, shelf_grid_list,occupy_map,optimal_path)
                    robot = new_robot
                    robots[robot_ind] = robot


                    #Astar 경로 초기화 목표 노드 재설정
                robot.astar_move()
                # 배치에 사용할 정보입니다.
                temp = robot_data['already_gone_node']
                temp[robot_ind]= copy.copy(new_robot.already_gone_node)
                robot_data['already_gone_node'] =temp
                if robot.packing_point_arrive:
                    # print("로봇 : ",robot_ind,"재시작합니다.")
                    robot.packing_point_arrive = False

                    restart_robot(robot_data,robot_ind)

        want_time = 0.1
        real_time = want_time - (time.time() - start)
        if real_time > 0:
            time.sleep(real_time)
        #로봇 업데이트
        robot_data['robot'] = robots

        #GUI 업데이트
