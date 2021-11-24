import time
import math
from multiprocessing import Process
import copy
import numpy as np
from Dynamic.Online_orderbatch import online_order_batch,online_order_batch_FIFO
from Dynamic.Online_ordersequence import solve_tsp_online
from Dynamic.DEBUG_tool import DEBUG_log,DEBUG_log_tag


class procees_tsp_solver:
    def __init__(self):
        self.sub_process = None
        self.order_data = None
        self.solver_data = None
        self.robot_data = None
        self.node_point_y_x = None
        self.using_order_batch = "FIFO"
        self.using_order_sequence = "TSP_ONLINE"
        self.init_batch_size = 3  # 초기에 로봇에게 할당할 배치사이즈
        self.max_batch_size = 6  # interventionist방식에서 로봇에 대한 최대 배치사이즈(CAPACITY)
        self.all_mission_clear = False
        self.max_order =1000
        self.order_counter =0
        self.start_time =0
        
        DEBUG_log("초기 배치사이즈 : " + str(self.init_batch_size) + " 최대 배치사이즈 : " + str(self.max_batch_size), "DETAIL")
        
        self.algorithm_time = 0.0
        self.algorithm_count = 0

        self.work_time = 0
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
        if self.sub_process ==None:
            return
        self.solver_data["reset"] = True
        if self.sub_process.is_alive():
            self.sub_process.kill()

    def process(self,order_data, solver_data,robot_data):
        self.initalize(solver_data)#각 노드의 좌표를 변형합니다.
        self.start_time = time.time()
        while True:
            if self.solver_data["reset"]:
                break
            #로봇정보와 로봇의 대수를 가져옵니다.
            robots, robot_number = self.get_robot_number_batches(robot_data)
            solved_orders_index, solved_batches, changed_robot_index = self.solve_batch(order_data,robots, robot_data)
            #다끝났는지 확인하는 법.. 일단. 더이상 order를 생성 못해야함. orders도 확인해야함. 모든 로봇들이 새로운 배치를 기다리는지도 확인해야함.
            self.is_simulation_end(solved_orders_index, changed_robot_index,robot_data)
            if self.all_mission_clear:
                self.work_time = time.time()-self.start_time
                break
            self.delete_orders(order_data, solved_orders_index)
            self.change_batch_and_solve_tsp(solved_batches,changed_robot_index,robot_data)
        #-------------------추가된 부분---------------------
            time.sleep(0.1)
        self.save_result(robot_data)


    def solve_batch(self, current_orders, readonly_robot_data, robot_data):
        readonly_orders = copy.deepcopy(current_orders["orders"])  # 읽을수만 있는 현재 최종 order를 가져옵니다.
        if self.using_order_batch == "FIFO":
            return online_order_batch_FIFO(readonly_orders,
                                           self.init_batch_size,
                                           self.max_batch_size,
                                           robot_data)

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
        return robots, robot_number

    def delete_orders(self, current_order, deleted_order):
        deleted_order.sort(reverse=True)
        recent_orders = copy.deepcopy(current_order["orders"])
        for order in deleted_order:
            try :
                del recent_orders[order]
            except IndexError:
                print("삭제하다가 에러발생")
                print(recent_orders)
                print(deleted_order)
                print(order)
        current_order["orders"] = recent_orders

        DEBUG_log("삭제된 주문들", "VERY_DETAIL")
        DEBUG_log(current_order["orders"][0:5], "VERY_DETAIL")
        DEBUG_log("주문 갯수 : "+str(len(current_order["orders"])), "VERY_DETAIL")

    def change_batch_and_solve_tsp(self, solved_batches,changed_robot_index,robot_data):
        #배치를 반영합니다
        for robot_ind in changed_robot_index:
            temp = copy.deepcopy(robot_data["current_robot_batch"])
            if len(solved_batches[robot_ind])==0:
                print("배치하기에는 작습니다..")
            temp[robot_ind] = solved_batches[robot_ind]
            robot_data["current_robot_batch"] = temp
        DEBUG_log(changed_robot_index, "VERY_DETAIL")
        # DEBUG_log("주문 갯수 : " + str(len(current_order["orders"])), "VERY_DETAIL")

        if self.using_order_sequence == "TSP_ONLINE":
            additional_time, additional_count = solve_tsp_online(changed_robot_index,robot_data,self.node_point_y_x)
            self.algorithm_time += additional_time
            self.algorithm_count += additional_count

    def is_simulation_end(self,solved_orders_index, changed_robot_index,robot_data):
        self.order_counter += len(solved_orders_index)
        if self.max_order == self.order_counter:
            if len(changed_robot_index) ==0:
                flag_check = True
                for move in robot_data['stop']:
                    if not move:
                        flag_check = False
                        break

                if flag_check:
                    self.all_mission_clear = True
    def save_result(self,robot_data):
        robot_data["full_algorithm_time"] = self.algorithm_count
        robot_data["full_algorithm_count"] = self.algorithm_time
        robot_data["completion_time"] = self.work_time
        temp_list = []
        for robot in robot_data["robot"]:
            temp_list.append(robot.step)
        robot_data["robot_step"] = temp_list
        #이제 하나 끝났습니다.
        robot_data["the_end"] = True

                    

