import numpy as np
import math
import copy
from TSP_solve import *
from Astar import *

class warehouse_robot_info_saver:
    def __init__(self, capacity, packing_station, packing_station_ind, current_point, property=None):
        self.capcity = capacity#로봇 용량
        self.property = property#안쓰는거
        self.is_work = False#로봇이 일하고 있는가?
        self.home_packing_station = packing_station# 시작하고 돌아오는 패킹지점 좌표
        self.packing_station_ind = packing_station_ind  # occupy map에서 패킹지점의 인덱스
        self.current_point = current_point  # occupy_grid map에서의 현재 로봇 위치, 패키지점 바로옆이다.
        self.step = 0 #할당된 batch에 대해서 astar로 기록된 정보
        self.cur_step =0#알고리즘 할당되는 시간
        self.shelfs =0



    def get_step(self, picking_point, shelf_grid_list,occupy_map):
        self.shelfs +=len(picking_point)
        self.picking_point = [self.packing_station_ind] + picking_point + [self.packing_station_ind]#picking point를 찾습니다.
        self.shelf_grid_list = [[self.home_packing_station]]+shelf_grid_list+[[self.home_packing_station]]#현재 맵의 shelf 리스트를 찾습니다.
        self.is_work = True
        self.cur_step =0
        self.occupy_map =occupy_map
        step_viwer = 0
        for local_goal_ind in range(1,len(self.picking_point)):
            min_dis = 1000
            min_ind = -1
            # print("최소 그리드 후보점들", self.shelf_grid_list[local_goal_ind])
            goal_candidate = self.shelf_grid_list[local_goal_ind]#index가 넘어버림
            for i, point in enumerate(goal_candidate):  # 현재로봇과 가장가까운점을 찾는다.
                # print("검사하는 점들 마지막",point)
                dis = (point[0] - self.current_point[0]) * (point[0] - self.current_point[0]) + (
                        point[1] - self.current_point[1]) * (point[1] - self.current_point[1])
                if dis < min_dis:
                    min_ind = i
                    min_dis = dis
            local_goal_point = goal_candidate[min_ind]
            local_astar_route = astar_path(self.occupy_map, self.current_point, local_goal_point)
            self.step += len(local_astar_route)
            self.cur_step += len(local_astar_route)
            self.current_point = local_goal_point
            step_viwer +=1

def process_Fast_sim(sim_data,order_data):
    end_time_full_algorithm = 0
    while True:
        while not sim_data["fast_start"]:
            pass

        loading_time =0
        loading_constant =60
        ui_info = sim_data['ui_info']
        # 로봇 셋팅
        robot_cap = order_data['sim_data'][3]
        robot_number = order_data['sim_data'][4]
        initOrder = order_data['sim_data'][1]
        sim_data["sim_info_ronum_rocap_initorder"] = [robot_number, robot_cap, initOrder]

        # ui로 인해서 마우스 좌표가 잘못되는거 보정
        init_map_x = ui_info[0]
        init_map_y = ui_info[1]
        # 맵정보 기록
        map_data = sim_data['map_data']

        map_width = map_data['map_size'][0]
        map_height = map_data['map_size'][1]
        map_resolution = map_data['map_resolution'][0]
        map_resolution_2 = map_data['map_resolution'][1]
        occupy_map = map_data['occupay_map']
        res_width = map_width / map_resolution
        res_height = map_height / map_resolution_2

        # 위의 맵은 행 크기 : map_resolution, 열 크기 : map_resolution_2
        # 각 선반에 대해서 차지하고 있는 영역이 1부터 선반 수로 인덱싱이 되있음
        # 각 블록이 차지하고 있는 영역은 -1부터 -블럭수로 인덱싱되있음
        # 시작점은 없으니 제외
        # 각 패킹지점이 차지하고 있는 영역은 20001부터 20000+패키지점수로 인덱싱되있음
        # 그 외에 지점은 0으로 인덱싱 되있음
        saved_shelf_point = map_data['shelf_point']
        saved_block_point = map_data['block_point']
        saved_pk_point = map_data['pack_point']
        saved_sp_point = map_data['start_point']
        order_data["order_kind"] = len(saved_shelf_point)

        '''
        각 선반사이에 거리를 설정한다. 공장환경이라서 굳이 astar 안해도 된다. 유클리드 거리만 써도 충분
        '''
        the_number_of_node = len(saved_shelf_point) + len(saved_pk_point)
        shelf_size = len(saved_shelf_point)
        distance_cost = [[0 for _ in range(the_number_of_node)] for _ in range(the_number_of_node)]
        real_cordinate = []
        # 실제 좌표에 대한 유클리드 거리르 사용한다.
        # 패킹지점을 포함한 모든점에 대한 좌표를 2차원리스트의 형태로 저장합니다.
        for i in range(the_number_of_node):
            if i >= shelf_size:  # 만약에 선반이 아닌 패킹지점에 대한거라면
                i_pos_x = saved_pk_point[i - shelf_size][0] - init_map_x
                i_pos_y = saved_pk_point[i - shelf_size][1] - init_map_y
                pose_point = [i_pos_y, i_pos_x]
            else:  # 선반에 대한거라면
                i_pos_x = saved_shelf_point[i][0] - init_map_x
                i_pos_y = saved_shelf_point[i][1] - init_map_y
                pose_point = [i_pos_y, i_pos_x]
            real_cordinate.append(pose_point)

            for j in range(the_number_of_node):
                if i >= shelf_size:  # 만약에 선반이 아닌 패킹지점에 대한거라면
                    i_pos_x = saved_pk_point[i - shelf_size][0] - init_map_x
                    i_pos_y = saved_pk_point[i - shelf_size][1] - init_map_y
                    i_pos = [i_pos_x, i_pos_y]
                else:  # 선반에 대한거라면
                    i_pos_x = saved_shelf_point[i][0] - init_map_x
                    i_pos_y = saved_shelf_point[i][1] - init_map_y
                    i_pos = [i_pos_x, i_pos_y]
                if j >= shelf_size:  # 만약에 선반이 아닌 패킹지점에 대한거라면
                    j_pos_x = saved_pk_point[j - shelf_size][0] - init_map_x
                    j_pos_y = saved_pk_point[j - shelf_size][1] - init_map_y
                    j_pos = [j_pos_x, j_pos_y]
                else:  # 선반에 대한거라면
                    j_pos_x = saved_shelf_point[j][0] - init_map_x
                    j_pos_y = saved_shelf_point[j][1] - init_map_y
                    j_pos = [j_pos_x, j_pos_y]
                distance_cost[i][j] = math.sqrt(
                    (i_pos[0] - j_pos[0]) * (i_pos[0] - j_pos[0]) + (i_pos[1] - j_pos[1]) * (i_pos[1] - j_pos[1]))

        sim_data["real_cordinate"] = real_cordinate
        sim_data["packing_point"] = map_data['pack_point']
        # 로봇의 위치를 세팅한다.
        '''
        패킹지점 별로 할당받아야함 
        '''
        robots = []
        robot_ind = []
        for i in range(robot_number):
            packing_ind = math.floor(i / robot_number * len(saved_pk_point))
            robot_ind.append(packing_ind)
            robot_pos_x = math.floor((saved_pk_point[packing_ind][0] - init_map_x) / res_width)
            robot_pos_y = math.floor((saved_pk_point[packing_ind][1] - init_map_y) / res_height)
            packing_point = [robot_pos_y, robot_pos_x]  # 로봇의 초기 위치는 y,x를 반대로 해서 넣습니다.
            current_pose = [robot_pos_y, robot_pos_x - 1]  # 패키지점 한칸 옆에 만듭니다.
            robot = warehouse_robot_info_saver(capacity=robot_cap, packing_station=packing_point,
                                    packing_station_ind=packing_ind + 20001, current_point=current_pose)

            robots.append(robot)
        shelf_grid_list = []
        for ind, point in enumerate(saved_shelf_point):
            if point[2] == 0 or point[2] == 180:
                lefttop = [point[0] - int(point[3] / 2),
                           point[1] - int(point[4] / 2)]
                rightbottom = [point[0] + int(point[3] / 2),
                               point[1] + int(point[4] / 2)]
            else:
                lefttop = [point[0] - int(point[4] / 2),
                           point[1] - int(point[3] / 2)]
                rightbottom = [point[0] + int(point[4] / 2),
                               point[1] + int(point[3] / 2)]

            init_x = init_map_x
            init_y = init_map_y
            small_x_index = math.floor((lefttop[0] - init_x) / res_width)  # 맨왼쪽 포함
            big_x_index = math.ceil((rightbottom[0] - init_x) / res_width)
            small_y_index = math.floor((lefttop[1] - init_y) / res_height)
            big_y_index = math.ceil((rightbottom[1] - init_y) / res_height)
            grid_list = []
            for i in range(small_y_index, big_y_index):
                for j in range(small_x_index, big_x_index):
                    grid_list.append([i, j])#하나의 선반이 차지하는 격자셀성분이다.
            shelf_grid_list.append(grid_list)#선반별로 차지하는 격자를 저장한다.

        ##메인코드 실행

        end_time = [0. for _ in robots]
        last_end_time=0
        order_data["is_set_order"] = True
        last_duration =0
        j =0
        while not order_data["is_set_initOrder"]:
            pass
        start_astar = time.time()
        while order_data["orders"] !=[]:
            if sim_data["force_die"]:
                break;
            small_robot_ind = end_time.index(min(end_time))
            robot = robots[small_robot_ind]#작은 end time을 가지는 로봇을 찾습니다.

            order = copy.deepcopy(order_data["orders"][:robot.capcity])  # capacity *5의 양으로 하고있구나..
            order_data["orders"] = copy.deepcopy(order_data["orders"][robot.capcity:])
            new_order = []  # 로봇에게 할당된 order수에 맞춰서 새롭게 저장하고, set을 시켜버립니다.
            for small_order in order:
                new_order = new_order + small_order
            new_order_2 = list(set(new_order))
            loading_time += len(new_order_2)
            solver_method = sim_data['solver_set'][sim_data['solver_ind']]  # 알고리즘별로 다른걸해줍니다.
            start = time.time()
            solved_order = solve_tsp(new_order_2, robot.packing_station_ind, solver_method, distance_cost, shelf_size,
                                     real_cordinate)
            duration = time.time() - start  # 각 문제를 푸는 시간 및 각 로봇의 시작시간입니다.
            last_duration +=duration
            part_shelf_grid = []
            for shelf_grid in solved_order:
                part_shelf_grid.append(shelf_grid_list[shelf_grid - 1])
            robot.get_step(solved_order, part_shelf_grid, occupy_map)  # 각 순서, 순서별 할당된 grid, occupy map
            if last_end_time < end_time[small_robot_ind]:
                last_end_time = end_time[small_robot_ind]  # 알고리즘을 할당하기 시작한 시간을 여기에 넣습니다.
            end_time[small_robot_ind] = last_end_time + (
                    duration + robot.cur_step *res_width)  # 한칸 당 1초라면 해당 노드에 대해서,로봇이 다음 목표를 수행할 수 있는 시간
            sim_data['order_do'] += len(order)
            last_end_time +=duration
        if sim_data["force_die"]:
            sim_data["force_die"] = False
            continue
        robot_speed = 1
        Total_elapsed_time = max(end_time)
        Average_travel_time =0
        for robot in robots:
            Average_travel_time +=robot.step*res_width/robot_speed
        Average_travel_time /= len(robots)

        end_astar = time.time()-start_astar-last_duration
        end_time_full_algorithm += last_duration

        Average_travel_distance = Average_travel_time*res_width
        Average_travel_time += (loading_time*loading_constant)/len(robots)
        Average_travel_time /=60
        # print(sim_data["tsp_solver"])
        # print("Total_elapsed_time", Total_elapsed_time)
        # print("Average_travel_time", Average_travel_time)
        # print("Average_travel_distance", Average_travel_distance)
        # print("tsp 푸는데 걸린 알고리즘 총시간",last_duration)
        # print("시물레이션 현재 시간", end_time_full_algorithm)
        al_ex_time = sim_data['Total_elapsed_time']
        al_tr_distance = sim_data['Average_travel_distance']
        al_tr_time = sim_data['Average_travel_time']
        c_time =sim_data['Computation_time']


        al_ex_time[sim_data['solver_ind']] = copy.copy(Total_elapsed_time)
        al_tr_distance[sim_data['solver_ind']] = copy.copy(Average_travel_distance)
        al_tr_time[sim_data['solver_ind']] = copy.copy(Average_travel_time)
        c_time[sim_data['solver_ind']] = copy.copy(last_duration)
        sim_data['Total_elapsed_time'] = al_ex_time
        sim_data['Average_travel_distance'] =al_tr_distance
        sim_data['Average_travel_time'] =al_tr_time
        sim_data['Computation_time'] = c_time

        steps = []
        times = []
        for robot in robots:
            steps.append(robot.step*res_width)
            each_robot_time = (robot.step*res_width/robot_speed + robot.shelfs*loading_constant)/60
            #로봇이 지나간 그리드 수 * 그리드의 너비 / 로봇의 속도 + 로봇이 들린 선반의 개수(패킹지점제외) x 로봇이 로딩하는데 걸리는시간
            times.append(each_robot_time)


        temp_alstep = sim_data['algorithm_step']
        temp_alstep[sim_data['solver_ind']] = copy.copy(steps)
        sim_data['algorithm_step'] =temp_alstep

        temp_alstep = sim_data['algorithm_time']
        temp_alstep[sim_data['solver_ind']] = copy.copy(times)
        sim_data['algorithm_time'] = temp_alstep
        if sim_data["tsp_solver"] != "ACO":
            sim_data['solver_ind'] += 1
            sim_data["tsp_solver"] = sim_data['solver_set'][sim_data['solver_ind']]  # 초기 tsp를 바꿉니다.
            order_data["reset"] = True  # order 생성을 리셋합니다.
            order_data["is_set_order"] = False
            order_data["is_set_initOrder"] = False
        else:
            sim_data['solver_ind'] = 0
            sim_data["tsp_solver"] = 'NO_TSP'
            order_data["is_start"] = False  #order 생성을 다시합니다.
            sim_data["fast_start"] = False  #이 코드를 다시 시작합니다.
            order_data["is_set_order"] = False
            order_data["is_set_initOrder"] = False
