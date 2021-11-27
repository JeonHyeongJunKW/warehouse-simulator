from Dynamic.DEBUG_tool import DEBUG_log_tag,DEBUG_log
import copy
import time

def make_astar_path_robot(robot, shelf_grid_list, occupy_map, optimal_path):
    part_shelf_grid = []

    for shelf_grid in optimal_path:  # 처음 노드를 제외한 나머지 노드에 대한 피킹 주변지역을 얻습니다.
        part_shelf_grid.append(shelf_grid_list[shelf_grid])  # 실제 shelf 격자들을 얻어온다.
    robot.assign_work_astar(optimal_path,part_shelf_grid,occupy_map)
    return robot


def restart_robot(robot_data,robot,robot_ind):
    temp = copy.deepcopy(robot_data)
    temp["optimal_path"][robot_ind] = []
    robot_data["optimal_path"] = temp["optimal_path"]

    temp2 = copy.deepcopy(robot_data)
    temp2["already_gone_node"][robot_ind] = []
    robot_data["already_gone_node"] = temp2["already_gone_node"]

    temp3 = copy.deepcopy(robot_data)
    temp3["current_robot_batch"][robot_ind] = []
    robot_data["current_robot_batch"] = temp3["current_robot_batch"]

    temp4 = copy.deepcopy(robot_data)
    temp4['stop'][robot_ind] = True
    robot_data['stop'] = temp4['stop']

    temp = copy.deepcopy(robot_data['past_robot_batch'])
    temp[robot_ind] = []
    robot_data['past_robot_batch'] = temp


def gui_data_update(robots, gui_data,robot_data):
    #로봇의 현재위치를 갱신합니다.
    '''
        gui_data["current_robot_position"] = [[0, 0] for _ in range(len(robot_data['robot']))]# 로봇의 현재 위치
        gui_data["short_path"] = [[] for _ in range(len(robot_data['robot']))]# 로봇의 과거 위치
        gui_data["long_path"] = [[] for _ in range(len(robot_data['robot']))]
        gui_data["all_target"] = [[] for _ in range(len(robot_data['robot']))]
        gui_data["current_target"] = [[] for _ in range(len(robot_data['robot']))]
    '''
    temp_gui_data = copy.deepcopy(gui_data)
    temp_robots =copy.deepcopy( robots)

    for robot_ind in range(len(robots)):
        robot_point = temp_robots[robot_ind].current_point
        temp_gui_data["current_robot_position"][robot_ind] = robot_point

        if len(temp_gui_data["short_path"][robot_ind]) >4:
            temp_gui_data["short_path"][robot_ind].pop(0)
        temp_gui_data["short_path"][robot_ind].append(robot_point)


        temp_gui_data["long_path"][robot_ind].append(robot_point)

        temp_gui_data["current_target"][robot_ind] = temp_robots[robot_ind].goal_point

        if robot_ind ==0:
            batches = robot_data['current_robot_batch'][robot_ind]
            temp_gui_data["zero_robot_pick_point"] =  list(set(sum(batches, [])))  # 과거배치를 전부 합칩니다.

    gui_data["current_robot_position"] = temp_gui_data["current_robot_position"]
    gui_data["short_path"] = temp_gui_data["short_path"]
    gui_data["long_path"] = temp_gui_data["long_path"]
    gui_data["current_target"] = temp_gui_data["current_target"]
    gui_data["zero_robot_pick_point"] = temp_gui_data["zero_robot_pick_point"]


def action_control( robot_data,shelf_grid_list,occupy_map, gui_data):
    # 로봇 데이터를 기반으로 하여 현재 로봇을 움직인다.
    DEBUG_log("로봇 제어 시작.")
    robots = copy.deepcopy(robot_data['robot'])  # 임시 로봇을 가져온다.


    self_rebatch_flag = [True for _ in range(len(robots))]

    while True:
        start = time.time()
        robot_coordinates = []
        pre_coordinates = copy.deepcopy(robot_data["robot_coordinates"])
        prec_coordinates = copy.deepcopy(pre_coordinates)

        robots = copy.deepcopy(robot_data['robot'])#임시 로봇을 가져온다.
        if robot_data["reset"]:
            break
        for robot_ind in range(len(robots)):

            # print("로봇은 멈춰야하는가 ?",robot_data['stop'][robot_ind])
            # 로봇이 멈춰야한다면 움직이지 않는다.
            if robot_data['stop'][robot_ind]:#바로 True로 갈수도 있다..

                self_rebatch_flag[robot_ind] = True#멈추는 플래그가 열리면, rebatch가 True가된다.
                robot_coordinates.append([0, 0])
                continue

            else:
            # 로봇이 움직여야한다면
                robot = robots[robot_ind]
                # 만약에 로봇이 새로운 배치를 할당받앗다면

                if self_rebatch_flag[robot_ind] or robot_data['new_batch'][robot_ind]:
                    # 주의!) 안멈추고 바로 새로운 배치가 할당될 수 있음. 다음 for문에서 self_rebatch_flag[robot_ind] = True가 되기전에 새 배치 할당 가능
                    self_rebatch_flag[robot_ind] = False

                    temp = copy.deepcopy(robot_data['new_batch'])
                    temp[robot_ind] = False
                    robot_data['new_batch'] = temp

                    optimal_path = robot_data["optimal_path"][robot_ind]

                    new_robot = make_astar_path_robot(robot, shelf_grid_list, occupy_map,optimal_path)
                    robot = new_robot
                    robots[robot_ind] = robot


                    # Astar 경로 초기화 목표 노드 재설정
                robot.astar_move(pre_coordinates, robot_coordinates, prec_coordinates, robot_ind)
                if len(pre_coordinates) == len(robots):
                    pre_coordinates[robot_ind] = robot.current_point



                # 배치에 사용할 정보입니다.
                temp = robot_data['already_gone_node']
                temp[robot_ind]= copy.copy(robot.already_gone_node)
                robot_data['already_gone_node'] =temp

                temp = robot_data['not_go']
                temp[robot_ind] = copy.copy(robot.not_go)
                robot_data['not_go'] = temp
                if robot.packing_point_arrive:
                    robot.packing_point_arrive = False
                    restart_robot(robot_data, robot, robot_ind)
                    temp2 = copy.deepcopy(gui_data["long_path"])
                    temp2[robot_ind] = []
                    gui_data["long_path"] = temp2

            robot_coordinates.append(robot.current_point)

        robot_data["robot_coordinates"] = robot_coordinates

        # DEBUG_log_tag("할당된 배치들", robot_data["current_robot_batch"])
        # GUI 업데이트
        gui_data_update(robots, gui_data, robot_data)
        #시간 동기화
        want_time = 0.1
        real_time = want_time - (time.time() - start)
        if real_time > 0:
            time.sleep(real_time)
        #로봇 업데이트
        robot_data['robot'] = robots