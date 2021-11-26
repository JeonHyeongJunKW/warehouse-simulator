import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
import urllib.request
import json
import psutil
form_class = uic.loadUiType("./main_window.ui")[0]
from PyQt5.QtCore import Qt
from Map import *
from SimSet import *
from Simulator import *
import os

#멀티프로세스를 위한 패키지
from multiprocessing import Process, Manager
from sub_proc_simulator import *
from fast_simulation import *

from Dynamic.dynamic_sim_gui import Dynamic_Sim
class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super(WindowClass,self).__init__()
        self.setupUi(self)
        self.setWindowTitle("TSP 시뮬레이터")
        self.a = 0
        self.move(500, 300)
        self.setFixedWidth(263)
        self.setFixedHeight(476)

        self.mapMaker = Widget_Warehouse()
        self.ui_info = [self.mapMaker.init_map_x, self.mapMaker.init_map_y]
        self.mapMaker.hide()

        self.simulation_maker = Widget_SimSet()
        self.simulation_maker.hide()

        self.simulator = Widget_Simulator_no_gui()
        self.simulator.hide()
        self.map_data = None
        self.run_count = 0#시물레이션을 돌린횟수입니다.
        #시그널링 설정
        self.button_openmapmaker.clicked.connect(self.openMap)
        self.button_loadMap.clicked.connect(self.loadMap)
        self.button_paramset.clicked.connect(self.setSim)
        self.button_simStart.clicked.connect(self.openSimulator)
        self.button_simStart_dynamic.clicked.connect(self.openDynamicSimulator)

        #---21-11-17 : 다이나믹 시물레이션 추가
        self.dynamic_simulation = None

    def openDynamicSimulator(self):
        '''
        동적 시물레이션을 엽니다.
        '''
        if self.dynamic_simulation :
            del self.dynamic_simulation#시물레이터를 삭제합니다.

        self.dynamic_simulation = Dynamic_Sim()#다시만듭니다.
        self.dynamic_simulation.start(self.map_data, self.simulation_maker.sim_data, self.ui_info)

    def getProcess(self, order_maker,warehouse_fast_solver,warehouse_tsp_solver):
        self.order_maker = order_maker
        self.warehouse_tsp_solver = warehouse_tsp_solver
        self.warehouse_fast_solver = warehouse_fast_solver

    def set_data(self, order_data,sim_data):
        self.order_data = order_data
        self.sim_data = sim_data

    def closeEvent(self, QCloseEvent):
        self.sim_data['is_kill_robot_move'] = True
        time.sleep(1)
        # self.order_maker.kill()
        # self.warehouse_tsp_solver.kill()
        # self.warehouse_fast_solver.kill()
        self.simulator=None

    def openSimulator(self):
        if self.simulator :
            del self.simulator#시물레이터를 삭제합니다.

        self.simulator = Widget_Simulator_no_gui()#다시만듭니다.
        if not self.map_data:#맵이 있는지 확인합니다.
            msgBox = QMessageBox()
            msgBox.setWindowTitle("경고")
            msgBox.setText("맵의 정보가 없습니다.")
            msgBox.exec_()
            return False

        # self.simulator.setMapInfo(self.map_data, self.ui_info)
        if not self.simulation_maker.sim_data: #시물레이션 정보를 얻어옵니다.
            msgBox = QMessageBox()
            msgBox.setWindowTitle("경고")
            msgBox.setText("시물레이션의 정보가 없습니다.")
            msgBox.exec_()
            return False

        self.simulator.set_data(self.order_data, self.sim_data,self.map_data, self.ui_info)


        #시물레이션간에 필요한 사전정보를 넣어줍니다.
        self.order_data['sim_data'] = self.simulation_maker.sim_data
        self.sim_data['ui_info'] = self.ui_info
        self.sim_data['map_data'] = self.map_data

        #이제 order를 만들어주는 쪽과 시물레이션을 돌리는쪽에서 결과를 얻어옵니다.
        # self.order_data['is_start'] = True
        # self.sim_data['is_start'] = True

        self.simulator.start_setting()  # 그냥 시작합니다.
        self.simulator.timer.start(500)
        self.simulator.show()
        # self.simulator.show()#실제 시물레이션을 킵니다.
        self.run_count +=1#몇번돌렸는지를 확인합니다.

    def openMap(self):
        if self.mapMaker :
            del self.mapMaker
        self.mapMaker = Widget_Warehouse()

        self.mapMaker.show()

    def loadMap(self):

        FileSave = QFileDialog.getOpenFileName(self, '맵 불러오기', './Map/', "Map File (*.json)")[0]
        if FileSave == "":
            pass

        else:
            with open(FileSave, 'r') as fp:
                data = json.load(fp)
                self.map_data = data

    def setSim(self):
        if self.simulation_maker.is_safe_close:
            self.simulation_maker.show()
            self.simulation_maker.is_safe_close= False
            self.last_is_randomorder = self.simulation_maker.is_randomOrder
            self.last_init_order = int(self.simulation_maker.lineEdit_initorder.text())
            self.last_order_rate = int(self.simulation_maker.lineEdit_orderrate.text())
            self.last_robot_cap  = int(self.simulation_maker.lineEdit_robotcap.text())
            self.last_robot_number = int(self.simulation_maker.lineEdit_robotnumber.text())
        else :
            if self.last_is_randomorder:
                self.simulation_maker.radioButton_orderrandom.setChecked(True)  # 랜덤으로 아이템을 배치하는 의미로 라디오버튼을 킵니다.
                self.simulation_maker.lineEdit_initorder.setDisabled(True)
                self.simulation_maker.lineEdit_orderrate.setDisabled(True)
            else:
                self.simulation_maker.radioButton_orderdirect.setChecked(True)  # 랜덤으로 아이템을 배치하는 의미로 라디오버튼을 킵니다.
                self.simulation_maker.lineEdit_initorder.setEnabled(True)
                self.simulation_maker.lineEdit_orderrate.setEnabled(True)
            self.simulation_maker.lineEdit_initorder.setText(str(self.last_init_order))
            self.simulation_maker.lineEdit_orderrate.setText(str(self.last_order_rate))
            self.simulation_maker.lineEdit_robotcap.setText(str(self.last_robot_cap))
            self.simulation_maker.lineEdit_robotnumber.setText(str(self.last_robot_number))
            self.simulation_maker.show()

if __name__ == "__main__":
    try:
        os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] ='1'
        app = QApplication(sys.argv)
        app.setAttribute(Qt.AA_EnableHighDpiScaling)
        #시물레이션을 본격적으로 돌리는 프로세스 입니다.
        sim_data = Manager().dict()
        order_data = Manager().dict()
        sim_data["tsp_solver"] = 'NO_TSP'
        order_data["is_start"] = False
        sim_data["is_start"] = False
        sim_data["fast_start"] = False
        sim_data["robot_cordinates"] =[]
        sim_data["goal_cordinates"] = []
        sim_data["shelf_node"] = []
        sim_data["robot_routes"] = []
        sim_data["packing_ind"] = []
        sim_data["packing_color"] = []
        sim_data["packing_point"] = []
        sim_data["robot_full_routes"] = []
        sim_data["number_order"] =0
        sim_data['compare_robot_ind'] =0
        sim_data['compare_route'] = []
        sim_data["compare_tsp_solver"] = "NO_TSP"
        sim_data["tsp_length"] = [1000,1000,1000,1000,1000,1000]
        sim_data['compare_time'] = [0,0,0,0,0,0]
        order_data["is_set_order"] = False#선반의 개수가 다 정해졋는지 확인할 때, 사용하는변수
        order_data["is_set_initOrder"] = False#초기 주문들이 다 정해졋을때, 사용하는 변수
        order_data["len_order"] =0
        order_data["end_flag"] = False

        #연속적인 시물레이션 사용간에 사용되는 변수들
        sim_data['solver_set'] = ['NO_TSP',"DC","GREEDY","PSO","GA","ACO"]
        sim_data['solver_ind'] = 0
        sim_data['order_do'] = 0
        sim_data['algorithm_time'] = [[],[],[],[],[],[]]
        sim_data['algorithm_step'] = [[], [], [], [], [], []]
        sim_data['algorithm_full_time'] = [0. for _ in range(len(sim_data['solver_set']))]
        sim_data['simulation_end'] = False
        sim_data['Total_elapsed_time'] = [0. for _ in range(len(sim_data['solver_set']))]
        sim_data['Average_travel_time'] = [0. for _ in range(len(sim_data['solver_set']))]
        sim_data['Average_travel_distance'] = [0. for _ in range(len(sim_data['solver_set']))]
        sim_data['Computation_time'] = [0. for _ in range(len(sim_data['solver_set']))]
        sim_data["force_die"] = False
        sim_data["doing_order"] =0
        # order_maker = Process(target=warehouse_order_maker,args=(order_data,1))
        # warehouse_tsp_solver = Process(target=warehouse_tsp_solver, args=(sim_data,order_data))
        # warehouse_fast_solver = Process(target=process_Fast_sim, args=(sim_data, order_data))
        # order_maker.start()
        # warehouse_tsp_solver.start()
        # warehouse_fast_solver.start()
        #GUI를 담당하는 프로세스 입니다.
        myWindow = WindowClass()
        # myWindow.getProcess(order_maker,warehouse_fast_solver,warehouse_tsp_solver)
        myWindow.set_data(order_data,sim_data)
        myWindow.show()
        sys.exit(app.exec_())
    except:
        # order_maker.join()
        # warehouse_fast_solver.join()
        print(" ")





