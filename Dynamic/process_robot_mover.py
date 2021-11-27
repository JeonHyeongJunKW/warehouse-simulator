import math
from Dynamic.Dynamic_Robot import W_Robot
from multiprocessing import Process,Manager
from Dynamic.dynamic_action_controller import action_control
from Dynamic.DEBUG_tool import DEBUG_log
from Dynamic.Color_setting import getColorSet, getbrightColorSet


class procees_robot_mover:
    def __init__(self):
        self.sub_process = None
        self.robot_data = None
        self.robotnum = 3

    def run(self,gui_data):
        self.gui_data = gui_data
        self.robot_data["reset"] = False  # 리셋플레그를 false로합니다.
        if self.sub_process != None:
            if self.sub_process.is_alive():
                self.sub_process.kill()

        self.sub_process = Process(target=self.process, args=(self.robot_data,gui_data))

        self.sub_process.start()

    def reset(self):
        # while 탈출 및 sub process를 죽입니다.
        if self.sub_process ==None:
            return
        self.robot_data["reset"] = True
        if self.sub_process.is_alive():
            self.sub_process.kill()

    def process(self, robot_data, gui_data):
        ## dynamic order make
        shelf_grid_list = self.shelf_grid_list#grid상에 좌표(목표점 생성에 사용)
        occupy_map = self.occupy_map#Astar 알고리즘을 통한 경로생성에 사용
        action_control(robot_data,shelf_grid_list,occupy_map, gui_data)

    def initialize_robot(self,robot_data, gui_data):
        #로봇 초기화를 위한 파라미터들
        self.robot_data = robot_data
        robot_cap = self.robot_data["robot_info"][3]
        robot_number = self.robotnum
        init_map_x = self.robot_data["ui_data"][0]
        init_map_y = self.robot_data["ui_data"][1]
        map_data = self.robot_data['map_data']
        saved_pk_point = map_data['pack_point']
        map_width = map_data['map_size'][0]
        map_height = map_data['map_size'][1]
        map_resolution = map_data['map_resolution'][0]
        map_resolution_2 = map_data['map_resolution'][1]
        self.occupy_map = map_data['occupay_map']
        res_width = map_width / map_resolution
        res_height = map_height / map_resolution_2
        saved_shelf_point = map_data['shelf_point']


        self.shelf_grid_list = []##각 선반별로 차지하고 있는 격자를 리스트의 형태로 저장합니다.
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
            self.shelf_grid_list.append(grid_list)
        #로봇 초기화
        robots = []
        robot_ind = []

        for i in range(robot_number):
            packing_ind = math.floor(i / robot_number * len(saved_pk_point))
            robot_ind.append(packing_ind)
            robot_pos_x = math.floor((saved_pk_point[packing_ind][0] - init_map_x) / res_width)
            robot_pos_y = math.floor((saved_pk_point[packing_ind][1] - init_map_y) / res_height)
            packing_point = [robot_pos_y, robot_pos_x]  # 로봇의 초기 위치는 y,x를 반대로 해서 넣습니다.
            current_pose = [robot_pos_y, robot_pos_x - 1]  # 패키지점 한칸 옆에 만듭니다.
            robot = W_Robot(capacity=robot_cap, packing_station=packing_point,
                                    packing_station_ind=packing_ind + 20001, current_point=current_pose)

            robots.append(robot)
        self.robot_data['robot'] =robots# W_Robot객체를 저장합니다.
        self.robot_data['current_robot_batch'] = [[] for _ in range(len(robot_data['robot']))]#로봇에게 할당된 배치입니다.
        self.robot_data['past_robot_batch'] = [[] for _ in range(len(robot_data['robot']))]#과거에 로봇에게 할당된 배치입니다.
        self.robot_data['stop'] = [True for _ in range(len(robot_data['robot']))]#로봇에게 할당된 배치입니다.
        self.robot_data['already_gone_node'] = [[] for _ in range(len(robot_data['robot']))]#과거에 로봇이 이미 이동한 노드입니다.
        self.robot_data['not_go'] = [[] for _ in range(len(robot_data['robot']))]  # 과거에 로봇이 이미 이동한 노드입니다.
        self.robot_data['optimal_path'] = [[] for _ in range(len(robot_data['robot']))]#현재 로봇에 대한 최적경로
        self.robot_data['new_batch'] = [False for _ in range(len(robot_data['robot']))]  # 현재 로봇에 대한 최적경로
        self.robot_data["packing_pose_recovery"] = [init_map_y,init_map_x,res_width,res_height]
        self.robot_data["robot_coordinates"] = []  # 로봇의 위치
        ##------------------------------------GUI를 그리기 위한 부분--------------------------------------------------
        gui_data["current_robot_position"] = [[0, 0] for _ in range(len(robot_data['robot']))]# 로봇의 현재 위치
        gui_data["short_path"] = [[] for _ in range(len(robot_data['robot']))]# 로봇의 과거 위치
        gui_data["long_path"] = [[] for _ in range(len(robot_data['robot']))]
        # gui_data["all_target"] = [[] for _ in range(len(robot_data['robot']))]
        gui_data["current_target"] = [[] for _ in range(len(robot_data['robot']))]
        gui_data["packing_color"] = getColorSet(len(saved_pk_point))
        gui_data["route_color"] = getbrightColorSet(len(saved_pk_point))
        gui_data["packing_point"] = saved_pk_point
        gui_data["packing_ind"] = robot_ind
        gui_data["zero_robot_pick_point"] = []
        ##------------------------------------시뮬레이션 결과를 저장하기 위한 부분---------------------------------------
        self.robot_data["the_end"] = False
        self.robot_data["full_algorithm_time"] =0
        self.robot_data["full_algorithm_count"] = 0
        self.robot_data["completion_time"] = 0
        self.robot_data["robot_step"] = [0 for _ in range(len(robot_data['robot']))]
