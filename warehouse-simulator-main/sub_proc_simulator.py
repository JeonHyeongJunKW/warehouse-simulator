import time
import random
import math
from TSP_solve import *
import os
from Astar import *
import copy
from multiprocessing import Process, Manager
from Warehouse_Robot import warehouse_Robot, robot_mover


def warehouse_order_maker(order_info, no_use):
    '''
    order_info : 초기에 주문이 쌓여있는 양, 주문당 아이템의 수, 초기화정보가 담겨있습니다.
    '''
    while True:
        order_info["reset"] = False  # 리셋 플래그를 선언과 동시에 False로 내립니다.
        while not order_info["is_start"]:#초기화가 동기화되면 시작합니다.
            pass
        ## dynamic order make
        initOrder = order_info['sim_data'][1]# 초기 주문량
        order_rate = order_info['sim_data'][2]# 시간당 주문 증가량
        order_rate = 0#증가율을 0으로 만들어버립니다.
        '''
        기본 order들을 생성합니다. 
        선반의 개수에 맞춰서 생성합니다. 
        '''
        while not order_info["is_set_order"]:
            pass
        kind = order_info['order_kind']
        # order_info["orders"] = [random.choice(list(range(1,kind+1))) for i in range(initOrder)]
        random.seed(10)
        order_info["orders"] = [list(set([random.choice(list(range(1, kind + 1))) for _ in range(5)])) for __ in range(initOrder)]
        order_info["is_set_initOrder"] = True
        while True:
            if order_info["reset"]:
                break
            time.sleep(1)
            # new_order = [random.choice(list(range(1,kind+1))) for i in range(order_rate)]
            # order_info["orders"] = order_info["orders"] +new_order
            #order를 2차원배열의 형태로 추가합니다.
            new_order = [list(set([random.choice(list(range(1,kind+1))) for i in range(5)])) for j in range(order_rate)]
            order_info["orders"] = order_info["orders"] + new_order

def warehouse_tsp_solver(sim_data,order_data):
    while True:
        while not sim_data["is_start"]:
            pass
        # print("order handler",os.getpid())
        solver = sim_data["tsp_solver"]
        sim_data["reset"] = False


        ui_info =sim_data['ui_info']
        #로봇 셋팅
        robot_cap = order_data['sim_data'][3]
        robot_number = order_data['sim_data'][4]
        initOrder = order_data['sim_data'][1]
        sim_data["sim_info_ronum_rocap_initorder"] = [robot_number, robot_cap, initOrder]

        #ui로 인해서 마우스 좌표가 잘못되는거 보정
        init_map_x = ui_info[0]
        init_map_y = ui_info[1]
        #맵정보 기록
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
        order_data["order_kind"] =len(saved_shelf_point)

        '''
        각 선반사이에 거리를 설정한다. 공장환경이라서 굳이 astar 안해도 된다. 유클리드 거리만 써도 충분
        '''
        the_number_of_node = len(saved_shelf_point)+len(saved_pk_point)
        shelf_size = len(saved_shelf_point)
        distance_cost = [[0 for _ in range(the_number_of_node)] for _ in range(the_number_of_node)]
        real_cordinate =[]
        #실제 좌표에 대한 유클리드 거리르 사용한다.
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
                if i >=shelf_size:#만약에 선반이 아닌 패킹지점에 대한거라면
                    i_pos_x = saved_pk_point[i-shelf_size][0]- init_map_x
                    i_pos_y = saved_pk_point[i-shelf_size][1]- init_map_y
                    i_pos =[i_pos_x,i_pos_y]
                else :#선반에 대한거라면
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
                distance_cost[i][j] = math.sqrt((i_pos[0]-j_pos[0])*(i_pos[0]-j_pos[0]) +(i_pos[1]-j_pos[1])*(i_pos[1]-j_pos[1]))

        sim_data["real_cordinate"] = real_cordinate

        #패킹지점별 고유 색깔을 지정받는다.
        sim_data["packing_color"] = getColorSet(len(saved_pk_point))

        sim_data["route_color"] = getbrightColorSet(len(saved_pk_point))
        sim_data["packing_point"] = map_data['pack_point']
        #로봇의 위치를 세팅한다.
        '''
        패킹지점 별로 할당받아야함 
        '''
        robots = []
        robot_ind = []
        for i in range(robot_number):
            packing_ind = math.floor(i/robot_number*len(saved_pk_point))
            robot_ind.append(packing_ind)
            robot_pos_x = math.floor((saved_pk_point[packing_ind][0] - init_map_x)/res_width)
            robot_pos_y = math.floor((saved_pk_point[packing_ind][1] - init_map_y)/res_height)
            packing_point = [robot_pos_y, robot_pos_x]#로봇의 초기 위치는 y,x를 반대로 해서 넣습니다.
            current_pose = [robot_pos_y, robot_pos_x-1]#패키지점 한칸 옆에 만듭니다.
            robot = warehouse_Robot(capacity=robot_cap,packing_station=packing_point,packing_station_ind=packing_ind+20001,current_point=current_pose)

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
                    grid_list.append([i, j])
            shelf_grid_list.append(grid_list)

        robot_data = Manager().dict()
        robot_data['robot'] =robots
        robot_data['step'] =[0 for _ in range(len(robot_data['robot']))]
        robot_data['is_work'] = [False for _ in range(len(robot_data['robot']))]
        robot_data['path'] = [[] for _ in range(len(robot_data['robot']))]
        robot_data['shelf_grid_list'] = shelf_grid_list
        robot_data['occupy_map'] =occupy_map
        sim_data["packing_ind"] = robot_ind
        #선반이 차지하는 격자맵을 얻습니다.


        order_data["is_set_order"] =True


        while not order_data["is_set_initOrder"]:
            pass

        robot_move = Process(target=robot_mover, args=(robot_data, sim_data))
        robot_move.start()
        sim_data['is_kill_robot_move'] = False
        algorithm_start_time =time.time()
        one_sim_time = [0 for _ in range(robot_number)]

        while True :
            robots = copy.deepcopy(robot_data['robot'])#로봇에 대한 정보를 담은 벡터를 가져온다. 어차피 full 수행시간을 구할때는 그다지 신경안써도 될듯
            for robot_ind in range(len(robots)):
                if sim_data["reset"] :
                    break
                if sim_data['is_kill_robot_move']:
                    robot_move.kill()
                if not robot_data['is_work'][robot_ind]:
                    robot = copy.deepcopy(robots[robot_ind])
                    last_worker = False
                    for robot_work in robot_data['is_work']:
                        if robot_work:
                            last_worker = True

                    if len(order_data["orders"]) < 1:
                        continue
                    '''
                    할당 FIFO
                    '''
                    order = copy.deepcopy(order_data["orders"][:robot.capcity])#capacity *5의 양으로 하고있구나..
                    order_data["orders"] = copy.deepcopy(order_data["orders"][robot.capcity:])
                    '''
                    경로생성 
                    '''
                    new_order = []
                    for small_order in order:
                        new_order = new_order + small_order
                    new_order_2 = list(set(new_order))


                    solver_method =sim_data["tsp_solver"]
                    new_start = time.time()
                    solved_order = solve_tsp(new_order_2,robot.packing_station_ind,solver_method,distance_cost,shelf_size,real_cordinate)
                    duration = time.time() - new_start
                    one_sim_time[robot_ind] +=duration
                    if robot_ind == sim_data['compare_robot_ind']:
                        all_route,all_length, all_time = solve_tsp_all_algorithm(new_order_2,robot.packing_station_ind,solver_method,distance_cost,shelf_size,real_cordinate,solved_order,duration)
                        sim_data["tsp_length"] = all_length
                        sim_data['compare_route'] = all_route
                        sim_data['compare_time'] = all_time
                        sim_data["compare_tsp_solver"] = sim_data["tsp_solver"]
                    '''
                    로봇을 work로 전환
                    '''

                    temp = copy.deepcopy(robot_data['path'])
                    temp[robot_ind] = solved_order
                    robot_data['path'] = copy.deepcopy(temp)
                    temp = copy.deepcopy(robot_data['is_work'])
                    temp[robot_ind] = True
                    robot_data['is_work'] = copy.deepcopy(temp)


            if sim_data["reset"]:
                break




def getColorSet(color_num):
    color_list = []
    color_base =0
    for i in range(color_num):
        if color_base == 0:
            r = random.randrange(200,255)
            g = random.randrange(0, 100)
            b = random.randrange(0, 100)
        elif color_base == 1:
            r = random.randrange(0, 100)
            g = random.randrange(200, 255)
            b = random.randrange(0, 100)
        elif color_base ==2:
            r = random.randrange(0, 100)
            g = random.randrange(0, 100)
            b = random.randrange(200, 255)
        color_list.append([r,g,b])
        color_base =(color_base+1)%3
    return color_list
def getbrightColorSet(color_num):
    color_list = []
    color_base =0
    for i in range(color_num):
        if color_base == 0:
            r = random.randrange(254,255)
            g = random.randrange(240, 255)
            b = random.randrange(180, 230)
        elif color_base == 1:
            r = random.randrange(180, 230)
            g = random.randrange(254, 255)
            b = random.randrange(240, 255)
        elif color_base ==2:
            r = random.randrange(240, 255)
            g = random.randrange(180, 230)
            b = random.randrange(254, 255)
        elif color_base ==3:
            r = random.randrange(254, 255)
            g = random.randrange(180, 230)
            b = random.randrange(240, 255)
        color_list.append([r,g,b])
        color_base =(color_base+1)%4
    return color_list