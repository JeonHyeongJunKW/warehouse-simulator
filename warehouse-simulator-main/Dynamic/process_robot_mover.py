import math
from Dynamic.Dynamic_Robot import W_Robot


class procees_robot_mover:
    def __init__(self):
        self.robot_data = None
        self.sim_data

    def run(self, order_data):
        self.order_data = order_data
        self.order_data["reset"] = False  # 리셋플레그를 false로합니다.

    def reset(self):
        # while 탈출 및 sub process를 죽입니다.
        self.order_data["reset"] = True
        if self.sub_process.is_alive():
            self.sub_process.kill()

    def process(self, robot_data):
        ## dynamic order make
        shelf_grid_list = robot_data['shelf_grid_list']
        occupy_map = robot_data['occupy_map']


    def initialize_robot(self,robot_data):
        #로봇 초기화를 위한 파라미터들
        self.robot_data = robot_data
        robot_cap = self.robot_data["robot_info"][3]
        robot_number = self.robot_data["robot_info"][4]
        init_map_x = self.robot_data["ui_data"][0]
        init_map_y = self.robot_data["ui_data"][1]

        map_data = self.robot_data['map_data']
        saved_pk_point = map_data['pack_point']
        map_width = map_data['map_size'][0]
        map_height = map_data['map_size'][1]
        map_resolution = map_data['map_resolution'][0]
        map_resolution_2 = map_data['map_resolution'][1]
        occupy_map = map_data['occupay_map']
        res_width = map_width / map_resolution
        res_height = map_height / map_resolution_2
        saved_shelf_point = map_data['shelf_point']


        shelf_grid_list = []##각 선반별로 차지하고 있는 격자를 리스트의 형태로 저장합니다.
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
        self.robot_data['step'] = [0 for _ in range(len(robot_data['robot']))]#로봇의 수만큼 이동 횟수를 저장합니다.
        self.robot_data['is_work'] = [False for _ in range(len(robot_data['robot']))]#로봇의 수만큼 현재 피킹중인지 확인합니다.
        self.robot_data['path'] = [[] for _ in range(len(robot_data['robot']))]#각 로봇이 가야하는 경로입니다.
        self.robot_data['shelf_grid_list'] = shelf_grid_list
        self.robot_data['occupy_map'] = occupy_map