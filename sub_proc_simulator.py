import time
import random
import math
from TSP_solve import *
import os
from Astar import *
from multiprocessing import Process, Manager

class warehouse_Robot:
    def __init__(self,capacity,packing_station,packing_station_ind,current_point,property=None):
        self.capcity = capacity
        self.property =property
        self.is_work = False#로봇이 일하고 있는가?
        self.home_packing_station = packing_station#시작하고 돌아오는 패킹지점
        self.packing_station_ind = packing_station_ind#occupy map에서 패킹지점의 인덱스
        self.current_point = current_point#occupy_grid map에서의 현재 로봇 위치
        self.is_ghost = True#로봇이 다른 로봇을 통과하는가?
        self.picking_point = []#로봇에게 부여된 피킹지점들
        self.last_ind = 0 #이미 들린 마지막 장소의 인덱스(패킹지점 포함) ex) 0(패킹지점) - 1(첫 번째 선반) -
        self.prev_point = self.home_packing_station#로봇의 현재 위치 이전의 좌표
        self.goal_point = []#현재 로봇이 향하는 목표점
        self.occupy_map =None
        self.route =[]
        self.route_maxind =6
        self.full_route =[]
        #Astar를 추가하였습니다.
        self.astar_route = []
        self.astar_ind = 0

    def move(self):
        if self.is_work:
            #알고리즘 적용
            move_control = [[0,1],[1,0],[0,-1],[-1,0]]
            blocked_flag = True
            find_goal = False
            best_cand = -1
            min_dis =10000
            list_ind = []
            for i, control in enumerate(move_control):
                cand_y = control[0] + self.current_point[0]
                cand_x = control[1] + self.current_point[1]
                list_ind.append(self.occupy_map[cand_y][cand_x])
                if cand_y == self.prev_point[0] and cand_x == self.prev_point[1]:
                    continue#이미 지나간 곳이면 무시한다.

                elif self.occupy_map[cand_y][cand_x] ==0:#자유영역이라면
                    curr_dis = (self.goal_point[0] -cand_y)*(self.goal_point[0] -cand_y) +(self.goal_point[1] -cand_x)*(self.goal_point[1] -cand_x)
                    blocked_flag = False
                    if curr_dis <min_dis:
                        min_dis =curr_dis
                        best_cand = i

                elif self.occupy_map[cand_y][cand_x] == self.picking_point[self.last_ind+1]:#주변에 사변이 해당로봇이 가야하는 지점과 목표 값이 같다면,
                    find_goal = True
                    blocked_flag = False
                    break

            self.prev_point = [self.current_point[0],self.current_point[1]]


            if not blocked_flag :

                if not find_goal :#아직 도착을 못했다면,
                    self.current_point[0] = self.current_point[0] +move_control[best_cand][0]
                    self.current_point[1] = self.current_point[1] +move_control[best_cand][1]
                else :#골에 도착했다면 목표위치를 바꾼다.
                    if self.chanage_goal():
                        self.is_work =False
            else :
                print("error occur : blocked robot")
            #로봇의 경로를 저장해둡니다. 시각적인 표시용
            if len(self.route)<= self.route_maxind:
                route_x = self.current_point[1]
                route_y = self.current_point[0]
                self.route.append([route_y,route_x])
            else :
                self.route.pop(0)
                route_x = self.current_point[1]
                route_y = self.current_point[0]
                self.route.append([route_y, route_x])
            route_x = self.current_point[1]
            route_y = self.current_point[0]
            self.full_route.append([route_y, route_x])

    def astar_move(self):
        if self.is_work:
            # 알고리즘 적용
            blocked_flag = True
            find_goal = False
            move_control = [[0,1],[1,0],[0,-1],[-1,0],[1,1],[1,-1],[-1,-1],[-1,1]]
            if len(self.astar_route) == 1:#이미 도착했다면(처음시작점과 도착점이 같아버림)
                if self.chanage_goal_astar():#다음위치로 가버립니다.
                    self.is_work = False
            next_pos = self.astar_route[self.astar_ind]#astar_ind를 기반으로 하여 바뀐 위치 아직 실제 로봇에 적용은 안함.
            self.astar_ind +=1
            # blocked_flag = False#막힌곳이 없을것이다.
            #print(next_pos)
            for control in move_control:
                cand_y = control[0] + next_pos[0]#현재 이동한지점 주변에 도착했는지 찾습니다.
                cand_x = control[1] + next_pos[1]#현재 이동한지점 주변에 도착했는지 찾습니다.
                if self.occupy_map[cand_y][cand_x] == self.picking_point[self.last_ind+1]: # 주변에 사변이 해당로봇이 가야하는 지점과 목표 값이 같다면,
                    find_goal = True

            self.prev_point = [self.current_point[0], self.current_point[1]]
            #현재 경로를 갱신하는부분
            self.current_point[0] = next_pos[0]
            self.current_point[1] = next_pos[1]

            if find_goal:# 골에 도착했다면 목표위치를 바꾼다.
                if self.chanage_goal_astar():
                    self.is_work = False

            #최근경로를 저장하는부분
            if len(self.route)<= self.route_maxind:
                route_x = self.current_point[1]
                route_y = self.current_point[0]
                self.route.append([route_y,route_x])
            else :
                self.route.pop(0)
                route_x = self.current_point[1]
                route_y = self.current_point[0]
                self.route.append([route_y, route_x])

            route_x = self.current_point[1]
            route_y = self.current_point[0]
            self.full_route.append([route_y, route_x])

    def chanage_goal(self):#패킹지점인지 확인한다.
        last_index = len(self.picking_point)-1
        if self.last_ind != last_index-1 :#last_ind가 패킹 선반 다돌고, 마지막 패킹지점으로 오지 않았다면(last_ind가 마지막에서 한 개 전이어야함.)
            if self.last_ind <last_index-2:
                goal_candidate = self.shelf_grid_list[self.last_ind+1]#해당 선반이 포함하고 있는 모든 점을 찾는다.
                min_dis = 1000
                min_ind = -1
                for i, point in enumerate(goal_candidate):
                    dis = (point[0] - self.current_point[0]) * (point[0] - self.current_point[0]) + (
                                point[1] - self.current_point[1]) * (point[1] - self.current_point[1])
                    if dis < min_dis:
                        min_ind = i
                        min_dis = dis
                self.goal_point = goal_candidate[min_ind]  # 로봇과 가까운 지점.
            else :
                self.goal_point = self.home_packing_station#골 후보를 그냥 패킹지점으로 준다.

            self.last_ind +=1
            return False
        else :#last_ind가 패킹 선반 다돌고, 마지막 패킹지점으로 왔다면
            self.last_ind =0
            self.route = []
            self.full_route = []
            return True
    def chanage_goal_astar(self):#패킹지점인지 확인한다.
        last_index = len(self.picking_point)-1
        if self.last_ind != last_index-1 :#last_ind가 패킹 선반 다돌고, 마지막 패킹지점으로 오지 않았다면(last_ind가 마지막에서 한 개 전이어야함.)
            if self.last_ind <last_index-2:
                goal_candidate = self.shelf_grid_list[self.last_ind+1]#해당 선반이 포함하고 있는 모든 점을 찾는다.
                min_dis = 1000
                min_ind = -1
                for i, point in enumerate(goal_candidate):
                    dis = (point[0] - self.current_point[0]) * (point[0] - self.current_point[0]) + (
                                point[1] - self.current_point[1]) * (point[1] - self.current_point[1])
                    if dis < min_dis:
                        min_ind = i
                        min_dis = dis
                self.goal_point = goal_candidate[min_ind]  # 로봇과 가까운 지점.
                self.astar_ind = 0
                self.astar_route = astar_path(self.occupy_map, self.current_point, self.goal_point)
            else :
                self.goal_point = self.home_packing_station#골 후보를 그냥 패킹지점으로 준다.
                self.astar_ind = 0
                self.astar_route = astar_path(self.occupy_map, self.current_point, self.goal_point)
            self.last_ind +=1
            return False
        else :#last_ind가 패킹 선반 다돌고, 마지막 패킹지점으로 왔다면
            self.last_ind =0
            self.route = []
            self.full_route = []
            return True
    def assign_work_astar(self, picking_point, shelf_grid_list,occupy_map):
        self.picking_point = [self.packing_station_ind] + picking_point + [self.packing_station_ind]
        self.shelf_grid_list = shelf_grid_list
        self.is_work = True
        goal_candidate = self.shelf_grid_list[self.last_ind]  # 해당 선반이 포함하고 있는 모든 점을 찾는다.
        min_dis = 1000
        min_ind = -1
        for i, point in enumerate(goal_candidate):
            dis = (point[0] - self.current_point[0]) * (point[0] - self.current_point[0]) + (
                    point[1] - self.current_point[1]) * (point[1] - self.current_point[1])
            if dis < min_dis:
                min_ind = i
                min_dis = dis
        self.goal_point = goal_candidate[min_ind]  # 로봇과 가까운 목표 선반 포인트를 찾는다.
        self.occupy_map = occupy_map
        self.astar_route = astar_path(self.occupy_map, self.current_point, self.goal_point)
        self.astar_ind = 0
        self.full_route = []

    def assign_work(self, picking_point, shelf_grid_list,occupy_map):
        self.picking_point = [self.packing_station_ind] + picking_point + [self.packing_station_ind]
        self.shelf_grid_list = shelf_grid_list
        self.is_work = True
        goal_candidate = self.shelf_grid_list[self.last_ind]  # 해당 선반이 포함하고 있는 모든 점을 찾는다.
        min_dis = 1000
        min_ind = -1
        for i, point in enumerate(goal_candidate):
            dis = (point[0] - self.current_point[0]) * (point[0] - self.current_point[0]) + (
                    point[1] - self.current_point[1]) * (point[1] - self.current_point[1])
            if dis < min_dis:
                min_ind = i
                min_dis = dis
        self.goal_point = goal_candidate[min_ind]  # 로봇과 가까운 지점.
        self.occupy_map = occupy_map
        self.full_route = []



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


def robot_mover(robot_data,sim_data):
    move_ind = 0
    while True:
        start = time.time()
        # 로봇의 위치를 공유변수에 저장합니다.
        robot_cordinates = []
        # 로봇의 현재 목표위치(선반의 일부)를 공유변수에 저장합니다.
        goal_cordinates = []
        # 로봇이 가야하는 경로를 공유변수에 저장합니다.
        shelf_node = []
        # 로봇의 6번의 경로를 저장합니다.
        robot_routes = []
        # 로봇의 전체 경로를 저장합니다.
        robot_full_routes = []
        robot_list = robot_data['robot']
        routes = []
        for ro in robot_list:
            routes.append(ro.route)
        for robot_ind in range(len(robot_list)):
            robot = robot_list[robot_ind]
            if robot.is_work:
                robot.astar_move()
                goal_cordinates.append(robot.goal_point)
                shelf_node.append(robot.picking_point)
                robot_routes.append(robot.route)
                robot_full_routes.append(robot.full_route)
                robot_list[robot_ind] = robot
            robot_cordinates.append(robot.current_point)
        routes = []
        for ro in robot_list:
            routes.append(ro.route)
        robot_data['robot'] = robot_list
        sim_data["robot_cordinates"] = robot_cordinates
        sim_data["goal_cordinates"] = goal_cordinates
        sim_data["shelf_node"] = shelf_node
        sim_data["robot_routes"] = robot_routes
        sim_data["robot_full_routes"] = robot_full_routes
        move_ind = move_ind +1
        want_time =0.1
        real_time = want_time- (time.time()-start)
        if real_time >0:
            time.sleep(real_time)


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
                distance_cost[i][j] = (i_pos[0]-j_pos[0])*(i_pos[0]-j_pos[0]) +(i_pos[1]-j_pos[1])*(i_pos[1]-j_pos[1])



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
        robot_data = Manager().dict()
        robot_data['robot'] =robots
        sim_data["packing_ind"] = robot_ind
        #선반이 차지하는 격자맵을 얻습니다.
        shelf_grid_list =[]
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
                    grid_list.append([i,j])
            shelf_grid_list.append(grid_list)

        order_data["is_set_order"] =True


        while not order_data["is_set_initOrder"]:
            pass

        robot_move = Process(target=robot_mover, args=(robot_data, sim_data))
        robot_move.start()
        sim_data['is_kill_robot_move'] = False
        while True :
            robots = robot_data['robot']
            for robot_ind in range(len(robots)):
                if sim_data["reset"] :
                    break
                if sim_data['is_kill_robot_move']:
                    robot_move.kill()
                if not robots[robot_ind].is_work:
                    robot = robots[robot_ind]
                    if len(order_data["orders"]) < 100:
                        print("too small ordrers")
                        break
                    '''
                    할당 FIFO
                    '''
                    order = order_data["orders"][:robot.capcity]
                    order_data["orders"] = order_data["orders"][robot.capcity:]
                    '''
                    경로생성 
                    '''
                    new_order = []
                    for small_order in order:
                        new_order = new_order + small_order
                    new_order_2 = list(set(new_order))
                    solved_order = solve_tsp(new_order_2,robot.packing_station_ind,sim_data["tsp_solver"],distance_cost,shelf_size,real_cordinate)

                    '''
                    로봇에게 업무할당간에 전처리
                    '''
                    part_shelf_grid = []
                    for shelf_grid in solved_order:
                        part_shelf_grid.append(shelf_grid_list[shelf_grid-1])
                    robot.assign_work_astar(solved_order,part_shelf_grid,occupy_map)
                    # 현재 남은 주문량을 공유변수에 저장합니다.
                    sim_data["number_order"] = len(order_data["orders"])
                    robots = robot_data['robot']
                    robots[robot_ind] = robot
                    robot_data['robot'] = robots
                    # 로봇을 이동시킵니다.
            if sim_data["reset"]:
                break






def warehouse_order_maker(order_info, no_use):
    #여기는 일단 끝
    while True:
        order_info["reset"] = False
        while not order_info["is_start"]:
            pass
        # print("order maker",os.getpid())

        initOrder = order_info['sim_data'][1]
        order_rate = order_info['sim_data'][2]

        '''
        기본 order들을 생성합니다. 
        선반의 개수에 맞춰서 생성합니다. 
        '''
        while not order_info["is_set_order"]:
            pass
        kind = order_info['order_kind']
        # order_info["orders"] = [random.choice(list(range(1,kind+1))) for i in range(initOrder)]
        order_info["orders"] = [list(set([random.choice(list(range(1, kind + 1))) for i in range(5)])) for i in range(initOrder)]
        order_info["is_set_initOrder"] = True
        while True:
            if order_info["reset"]:
                break
            time.sleep(1)
            # new_order = [random.choice(list(range(1,kind+1))) for i in range(order_rate)]
            # order_info["orders"] = order_info["orders"] +new_order
            #order를 2차원배열의 형태로 추가합니다.
            new_order = [list(set([random.choice(list(range(1,kind+1))) for i in range(5)])) for i in range(order_rate)]
            order_info["orders"] = order_info["orders"] + new_order