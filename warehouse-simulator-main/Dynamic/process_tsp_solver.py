import time
import math
from multiprocessing import Process
import copy
from Dynamic.Online_orderbatch import online_order_batch
class procees_tsp_solver:
    def __init__(self):
        self.sub_process = None
        self.order_data = None
        self.solver_data = None
        self.robot_data = None


    def run(self, order_data,solver_data,robot_data):
        self.order_data = order_data
        self.solver_data = solver_data
        self.robot_data = robot_data
        self.solver_data["reset"] = False  # 리셋플레그를 false로합니다.

        if self.sub_process != None:
            if self.sub_process.is_alive():
                self.sub_process.kill()

        # 새로운 프로세스를 할당합니다.
        self.sub_process = Process(target=self.process, args=(self.order_data,
                                                              self.solver_data,
                                                              self.robot_data))
        self.sub_process.start()

    def reset(self):
        #while 탈출 및 sub process를 죽입니다.
        self.solver_data["reset"] = True
        if self.sub_process.is_alive():
            self.sub_process.kill()

    def process(self,order_data, solver_data,robot_data):
        self.initalize(solver_data)

        while True:
            robots = copy.deepcopy(robot_data['robot'])  # 로봇에 대한 정보를 담은 벡터를 가져온다.
            robot_number = robot_data["robot_info"][4]  # 로봇 대수
            # for robot_ind in range(robot_number):
            #     if self.solver_data["reset"] :
            #         return 0
            #     if not robot_data['is_work'][robot_ind]:#만약에 특정로봇이 일을 안하고 있다면
            #         robot = copy.deepcopy(robots[robot_ind])# 해당 로봇을 딥 카피해서 정보만을 가져온다.
            # robot_data#--------------------여기까지 짬
            changed_information = self.solve_batch(order_data,robots)

            self.solve_tsp(changed_information,robots)


        #-------------------추가된 부분---------------------
    def solve_tsp(self, solved_changed_information,robots):
        #todo
        '''
        이 안에서
        '''
        print("solve tsp")
    def solve_batch(self, orders, solver_data):

        item_position = solver_data["node_point_y_x"]
        init_batch_size = 6
        max_batch_size = 12
        # current_robot_batch =
        # online_order_batch(orders, item_position, init_batch_size, max_batch_size, current_robot_batch)


    def initalize(self, solver_data):
        ## dynamic order make

        init_map_x = solver_data["ui_data"][0]
        init_map_y = solver_data["ui_data"][1]

        #맵정보 변수 얻기
        map_data = solver_data["map_data"]
        map_width = map_data['map_size'][0]
        map_height = map_data['map_size'][1]
        map_resolution = map_data['map_resolution'][0]
        map_resolution_2 = map_data['map_resolution'][1]
        occupy_map = map_data['occupay_map']
        res_width = map_width / map_resolution
        res_height = map_height / map_resolution_2

        saved_shelf_point = map_data['shelf_point']
        saved_block_point = map_data['block_point']
        saved_pk_point = map_data['pack_point']
        saved_sp_point = map_data['start_point']

        #선반과 패킹지점을 포함한 크기
        shelf_size = len(saved_shelf_point)
        node_size = shelf_size + len(saved_pk_point)
        nxn_dist_cost = [[0 for _ in range(node_size)] for _ in range(node_size)]
        real_cordinate = [] #  shelf 후에 packing 지점

        #거리값을 기반으로한 노드 좌표 및
        for i in range(node_size):
            if i >= shelf_size:  # 만약에 선반이 아닌 패킹지점에 대한거라면
                i_pos_x = saved_pk_point[i - shelf_size][0] - init_map_x
                i_pos_y = saved_pk_point[i - shelf_size][1] - init_map_y
                pose_point = [i_pos_y, i_pos_x]
            else:  # 선반에 대한거라면
                i_pos_x = saved_shelf_point[i][0] - init_map_x
                i_pos_y = saved_shelf_point[i][1] - init_map_y
                pose_point = [i_pos_y, i_pos_x]
            real_cordinate.append(pose_point)

            for j in range(node_size):
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
                nxn_dist_cost[i][j] = math.sqrt((i_pos[0]-j_pos[0])*
                                                (i_pos[0]-j_pos[0])+
                                                (i_pos[1]-j_pos[1])*
                                                (i_pos[1]-j_pos[1]))

        solver_data["node_point_y_x"] = real_cordinate
