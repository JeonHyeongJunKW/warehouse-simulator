import time
import math
from multiprocessing import Process
import copy
import numpy as np
from Dynamic.Online_orderbatch import online_order_batch,online_order_batch_FIFO
from Dynamic.Online_ordersequence import solve_tsp_online
from Dynamic.DEBUG_tool import DEBUG_log


class procees_tsp_solver:
    def __init__(self):
        self.sub_process = None
        self.order_data = None
        self.solver_data = None
        self.robot_data = None
        self.node_point_y_x = None
        self.using_order_batch = "FIFO"
        self.using_order_sequence = "TSP_ONLINE"
        self.init_batch_size = 6  # 초기에 로봇에게 할당할 배치사이즈
        self.max_batch_size = 12  # interventionist방식에서 로봇에 대한 최대 배치사이즈(CAPACITY)
        DEBUG_log("초기 배치사이즈 : " + str(self.init_batch_size) + " 최대 배치사이즈 : " + str(self.max_batch_size), "DETAIL")


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
        self.initalize(solver_data)#각 노드의 좌표를 변형합니다.

        while True:
            if self.solver_data["reset"]:
                break
            #로봇정보와 로봇의 대수를 가져옵니다.
            robots, robot_number, current_robot_batch = self.get_robot_number_batches(robot_data)
            # order batch를 합니다.
            # 반환값 : batch된 주문의 인덱스, 바뀐 배치들, 배치가 바뀐 로봇의 인덱스
            solved_orders_index, solved_batches, changed_robot_index = self.solve_batch(order_data,robots, current_robot_batch)
            # 1. batch된 주문들을 현재 주문에서 없앱니다.
            self.delete_orders(order_data, solved_orders_index)
            # 2. 배치를 교체하고, tsp문제를 풀게합니다. 현재 위치가 반영되어야합니다.
            self.change_batch_and_solve_tsp(solved_batches,changed_robot_index,robot_data)

            time.sleep(1)




        #-------------------추가된 부분---------------------
    def solve_batch(self, current_orders, readonly_robot_data, readonly_current_robot_batch):
        '''
        current_orders : 현재 주문정보
        robot_data : 기존에 어떤 배치를 받았는가?(없으면 없는데로, 있으면 용량제한만큼),
        전역변수로 사용되는

        반환값:
        현재 남은 주문상태, 최종적으로 할당된 배치, 바뀐 배치를 가지는 로봇의 인덱스,
        '''
        # item_position = solver_data["node_point_y_x"]


        readonly_orders = copy.deepcopy(current_orders["orders"])  # 읽을수만 있는 현재 최종 order를 가져옵니다.
        if self.using_order_batch == "FIFO":
            return online_order_batch_FIFO(readonly_orders,
                                           self.init_batch_size,
                                           self.max_batch_size,
                                           readonly_current_robot_batch)



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

        self.node_point_y_x = real_cordinate# 실제 선반과 패킹지점들의 좌표

    def get_robot_number_batches(self, robot_data):
        robots = copy.deepcopy(robot_data['robot'])  # 로봇에 대한 정보를 담은 벡터를 가져온다.
        robot_number = robot_data["robot_info"][4]  # 로봇 대수
        current_robot_batch = copy.deepcopy(robot_data['current_robot_batch'])
        return robots, robot_number, current_robot_batch

    def delete_orders(self, current_order, deleted_order):
        deleted_order.sort(reverse=True)
        DEBUG_log("\n--------------------\n", "VERY_DETAIL")
        DEBUG_log("제거해야하는 주문들", "VERY_DETAIL")
        DEBUG_log(deleted_order, "VERY_DETAIL")
        DEBUG_log("현재 주문들", "VERY_DETAIL")
        DEBUG_log(current_order["orders"][0:5], "VERY_DETAIL")
        recent_orders = copy.deepcopy(current_order["orders"])
        DEBUG_log("주문 갯수 : " + str(len(current_order["orders"])), "VERY_DETAIL")
        for order in deleted_order:

            del recent_orders[order]
        current_order["orders"] = recent_orders

        DEBUG_log("삭제된 주문들", "VERY_DETAIL")
        DEBUG_log(current_order["orders"][0:5], "VERY_DETAIL")
        DEBUG_log("주문 갯수 : "+str(len(current_order["orders"])), "VERY_DETAIL")

    def change_batch_and_solve_tsp(self, solved_batches,changed_robot_index,robot_data):
        #배치를 반영합니다
        robot_data['current_robot_batch'] = solved_batches
        DEBUG_log("경로를 수정하는 로봇들", "DETAIL")
        DEBUG_log(changed_robot_index, "DETAIL")
        # DEBUG_log("주문 갯수 : " + str(len(current_order["orders"])), "VERY_DETAIL")

        if self.using_order_sequence == "TSP_ONLINE":
            solve_tsp_online(changed_robot_index,robot_data,self.node_point_y_x)
