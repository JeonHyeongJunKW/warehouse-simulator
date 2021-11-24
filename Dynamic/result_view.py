from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from multiprocessing import Process, Manager
from Dynamic.process_order_maker import procees_order_maker
from Dynamic.process_tsp_solver import procees_tsp_solver
from Dynamic.process_robot_mover import procees_robot_mover
from Dynamic.DEBUG_tool import DEBUG_log
from Dynamic.Dynamic_viewer import online_simulator
from Dynamic.Map_drawer import map_maker
import time
import matplotlib.pyplot as plt
import numpy as np

class result_sim_view(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("./Dynamic/result_viewer.ui",self)
        self.hide()

        self.map_data = None
        self.ui_data = None
        self.sim_data = None

        # process_order_maker에서 사용하는 공유변수 : 주문에 대한 파라미터들
        self.order_worker_data = Manager().dict()

        # tsp_solver에서 사용하는 공유변수 :
        self.tsp_solver_data = Manager().dict()

        self.robot_mover_data = Manager().dict()
        # 관리되는 프로세스 후보들
        self.process_order_maker = procees_order_maker()  # 동적으로 주문을 만드는 프로세스
        DEBUG_log("order메이커 초기화가 끝났습니다.")
        self.process_tsp_solver = procees_tsp_solver()  # DTSP + alpha 알고리즘을 풀어주는 프로세스
        DEBUG_log("tsp solver 초기화가 끝났습니다.")
        self.process_robot_mover = procees_robot_mover()  # 로봇들에 대한 움직임을 처리하는 프로세스, 로봇 데이터에 대한 초기화가 이루어진다.
        DEBUG_log("robot 무브메이커 초기화가 끝났습니다.")
        # 시각적으로 그려주는 GUI 위젯
        self.gui_simulation = None
        self.gui_data = Manager().dict()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.redo_check)
        self.sim_count =0
        self.saved_result = []

    def start(self):


        self.draw_map()
        self.saved_result = []
        self.sim_count = 0
        self.timer.stop()
        self.pb_getResult.setValue(0)
        self.process_order_maker.reset()
        self.process_tsp_solver.reset()
        self.process_robot_mover.reset()
        self.timer.start(100)

        self.robot_mover_data["the_end"] = True


    def redo_check(self):
        if self.robot_mover_data["the_end"] and self.sim_count<3:
            if self.sim_count==1:
                self.pb_getResult.setValue(33)
                self.saved_result.append([self.robot_mover_data["full_algorithm_time"],
                                          self.robot_mover_data["full_algorithm_count"],
                                          self.robot_mover_data["completion_time"],
                                          self.robot_mover_data["robot_step"]])
            elif self.sim_count==2:
                self.pb_getResult.setValue(66)
                self.saved_result.append([self.robot_mover_data["full_algorithm_time"],
                                          self.robot_mover_data["full_algorithm_count"],
                                          self.robot_mover_data["completion_time"],
                                          self.robot_mover_data["robot_step"]])
            self.run()


            self.sim_count +=1


        if self.robot_mover_data["the_end"] and self.sim_count>=3:
            if self.sim_count == 3:
                self.pb_getResult.setValue(100)
                self.saved_result.append([self.robot_mover_data["full_algorithm_time"],
                                          self.robot_mover_data["full_algorithm_count"],
                                          self.robot_mover_data["completion_time"],
                                          self.robot_mover_data["robot_step"]])
            self.draw_result()
            self.timer.stop()



    def run(self):
        self.process_order_maker.reset()
        self.process_tsp_solver.reset()
        self.process_robot_mover.reset()

        self.process_robot_mover.initialize_robot(self.robot_mover_data, self.gui_data)

        self.process_order_maker.run(self.order_worker_data)
        # 초기화된 robot_mover_data를 이용합니다.
        self.process_tsp_solver.run(self.order_worker_data,
                                    self.tsp_solver_data,
                                    self.robot_mover_data)
        self.process_robot_mover.run(self.gui_data)

    def initialize(self,map_data,ui_data,sim_data):
        self.show()

        self.map_data = map_data
        self.ui_data = ui_data
        self.sim_data = sim_data

        # process_order_maker를 위한 데이터 설정
        self.order_worker_data["simulation_order_set"] = self.sim_data
        self.order_worker_data["order_kind"] = len(self.map_data['shelf_point'])
        self.order_worker_data["orders"] = []

        # process_order_maker를 위한 데이터 설정
        self.tsp_solver_data["ui_data"] = self.ui_data
        self.tsp_solver_data["map_data"] = self.map_data

        # 로봇의 움직임을 저장하기 위한 데이터
        self.robot_mover_data["robot_info"] = self.sim_data
        self.robot_mover_data["map_data"] = self.map_data
        self.robot_mover_data["ui_data"] = self.ui_data

        # GUI담당 프로세스 초기화
        self.gui_data["map_data"] = self.map_data
        self.gui_data["ui_data"] = self.ui_data




    def set_param(self,init_ordernum,update_ordernum,max_itemnum,max_ordercall,robotnum,init_batch_size,max_batch_size,max_order):
        self.process_order_maker.init_ordernum = init_ordernum
        self.process_order_maker.update_ordernum = update_ordernum
        self.process_order_maker.max_itemnum = max_itemnum
        self.process_order_maker.max_ordercall = max_ordercall
        self.process_robot_mover.robotnum = robotnum
        self.process_tsp_solver.init_batch_size = init_batch_size
        self.process_tsp_solver.max_batch_size = max_batch_size
        self.process_tsp_solver.max_order = max_order


    def closeEvent(self, QCloseEvent):
        self.process_order_maker.reset()
        self.process_tsp_solver.reset()
        self.process_robot_mover.reset()
        self.timer.stop()
        self.sim_count = 0

    def draw_map(self):
        self.map_maker = map_maker(self)
        self.map_name = 'map.jpg'
        self.map_maker.draw_and_save(self.map_data, self.map_name, self.ui_data)
        self.map_maker.hide()
        self.qPixmapVar = QPixmap()
        self.qPixmapVar.load("./sim/" + 'map.jpg')
        self.qPixmapVar = self.qPixmapVar.scaled(self.lb_simImage.width(), self.lb_simImage.height(), Qt.KeepAspectRatio)
        self.lb_simImage.setPixmap(self.qPixmapVar)

    def draw_result(self):
        '''
        self.saved_result.append([self.robot_mover_data["full_algorithm_time"],
                                          self.robot_mover_data["full_algorithm_count"],
                                          self.robot_mover_data["completion_time"],
                                          self.robot_mover_data["robot_step"]])
        '''
        algorithm_name = ['FCFS & O-ACO', "HOOB & O-ACO", "HOOB & OD-ACO"]
        algorithm_color = ['black', 'red', 'gold']
        fig = plt.figure(figsize=(6, 5.5))
        plt.title("Average Algorithm time", fontsize=12)
        plt.bar(np.arange(3), np.array([self.saved_result[0][0]/self.saved_result[0][1],
                                         self.saved_result[1][0]/self.saved_result[1][1],
                                         self.saved_result[2][0]/self.saved_result[2][1]]),
                width=0.8, color=algorithm_color)
        plt.xticks(np.arange(3), algorithm_name, fontsize=8)
        plt.xlabel("Algorithm", fontsize=10)
        plt.ylabel("Second", fontsize=10)
        plt.savefig("result/평균 알고리즘 시간.png")
        plt.clf()

        fig = plt.figure(figsize=(6, 5.5))
        plt.title("Total elapsed time", fontsize=12)
        plt.bar(np.arange(3), np.array([self.saved_result[0][2],
                                         self.saved_result[1][2],
                                         self.saved_result[2][2]]),
                width=0.8, color=algorithm_color)
        plt.xticks(np.arange(3), algorithm_name, fontsize=8)
        plt.xlabel("Algorithm", fontsize=10)
        plt.ylabel("Second", fontsize=10)
        plt.savefig("result/전체수행시간.png")
        plt.clf()

        fig = plt.figure(figsize=(6, 5.5))
        b_data = [self.saved_result[0][3],self.saved_result[1][3],self.saved_result[2][3]]
        plt.title("Travel distance", fontsize=12)
        for i, c in enumerate(algorithm_color):
            plt.boxplot([b_data[i]],
                        labels=[algorithm_name[i]],
                        positions=[i],
                        widths=0.5,
                        vert=True,
                        patch_artist=True,
                        boxprops=dict(facecolor=c, color='k'))
        plt.xticks(fontsize=8)
        plt.xlabel("Algorithm", fontsize=10)
        plt.ylabel("Meter", fontsize=10)
        plt.savefig("result/이동거리 박스플롯.png")
        plt.clf()

        self.qPixmapVar = QPixmap()
        self.qPixmapVar.load("result/평균 알고리즘 시간.png")
        self.qPixmapVar = self.qPixmapVar.scaled(self.lb_mean_time.width(), self.lb_mean_time.height(), Qt.KeepAspectRatio)
        # self.qPixmapVar = self.qPixmapVar.scaled(self.label_tet.width(), self.label_tet.height())
        self.lb_mean_time.setPixmap(self.qPixmapVar)

        self.qPixmapVar = QPixmap()
        self.qPixmapVar.load("result/전체수행시간.png")
        self.qPixmapVar = self.qPixmapVar.scaled(self.lb_complete_time.width(), self.lb_complete_time.height(), Qt.KeepAspectRatio)
        self.lb_complete_time.setPixmap(self.qPixmapVar)

        self.qPixmapVar = QPixmap()
        self.qPixmapVar.load("result/이동거리 박스플롯.png")
        self.qPixmapVar = self.qPixmapVar.scaled(self.lb_move_time.width(), self.lb_move_time.height(), Qt.KeepAspectRatio)
        # self.qPixmapVar = self.qPixmapVar.scaled(self.label_atd.width(), self.label_atd.height())
        self.lb_move_time.setPixmap(self.qPixmapVar)
