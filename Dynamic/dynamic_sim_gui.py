from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from multiprocessing import Process, Manager
from Dynamic.process_order_maker import procees_order_maker
from Dynamic.process_tsp_solver import procees_tsp_solver
from Dynamic.process_robot_mover import procees_robot_mover
from Dynamic.DEBUG_tool import DEBUG_log

class Dynamic_Sim(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("./Dynamic/dynamic_sim_gui.ui",self)
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
        self.process_order_maker = procees_order_maker() # 동적으로 주문을 만드는 프로세스
        DEBUG_log("order메이커 초기화가 끝났습니다.")
        self.process_tsp_solver = procees_tsp_solver() # DTSP + alpha 알고리즘을 풀어주는 프로세스
        DEBUG_log("tsp solver 초기화가 끝났습니다.")
        self.process_robot_mover = procees_robot_mover() # 로봇들에 대한 움직임을 처리하는 프로세스, 로봇 데이터에 대한 초기화가 이루어진다.
        DEBUG_log("robot 무브메이커 초기화가 끝났습니다.")
        # 시각적으로 그려주는 GUI 위젯
        self.gui_simulation = None



        self.buttonRealView.clicked.connect(self.Real_Simulation_Start)

    def start(self,map_data,sim_data,ui_data):

        # 정보 확인 점검
        if not map_data:#맵이 있는지 확인합니다.
            msgBox = QMessageBox()
            msgBox.setWindowTitle("경고")
            msgBox.setText("맵의 정보가 없습니다.")
            msgBox.exec_()
            return False

        if not sim_data: #시물레이션 정보가 있는지 확인합니다.
            msgBox = QMessageBox()
            msgBox.setWindowTitle("경고")
            msgBox.setText("시물레이션의 정보가 없습니다.")
            msgBox.exec_()
            return False

        # 데이터 저장 및 실행
        self.map_data = map_data
        self.ui_data = ui_data
        self.sim_data = sim_data
        self.show()

        #process_order_maker를 위한 데이터 설정
        self.order_worker_data["simulation_order_set"] = self.sim_data
        self.order_worker_data["order_kind"] = len(self.map_data['shelf_point'])

        # process_order_maker를 위한 데이터 설정
        self.tsp_solver_data["ui_data"] = self.ui_data
        self.tsp_solver_data["map_data"] = self.map_data

        # 로봇의 움직임을 저장하기 위한 데이터
        self.robot_mover_data["robot_info"] = self.sim_data
        self.robot_mover_data["map_data"] = self.map_data
        self.robot_mover_data["ui_data"] = self.ui_data

        #로봇만들기전에 선행되는 전처리과정
        self.process_robot_mover.initialize_robot(self.robot_mover_data)


    def Real_Simulation_Start(self):
        #시물레이션 프로세스를 시작합니다.
        DEBUG_log("시물레이션 시작")
        # self.process_robot_mover.run()
        self.process_order_maker.run(self.order_worker_data)
        # 초기화된 robot_mover_data를 이용합니다.
        self.process_tsp_solver.run(self.order_worker_data,
                                    self.tsp_solver_data,
                                    self.robot_mover_data)

    def closeEvent(self, QCloseEvent):
        self.process_order_maker.reset()
        self.process_tsp_solver.reset()

