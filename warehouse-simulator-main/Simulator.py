from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import math
import json
import time
from PDFmake import *
import matplotlib.pyplot as plt
import copy

class Simulator(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)
        self.draw_image =False
        self.sim_data= None
        self.timer = QTimer(self)
        self.timer.start(100)
        self.timer.timeout.connect(self.update)
        self.is_view_shelf = False
        self.is_view_route = False
        self.is_view_full_route = False
        self.is_mode_compare = False

    def setData(self,sim_data, map_data,ui_info):
        self.sim_data = sim_data
        self.map_data = map_data
        self.shelfs =map_data['shelf_point']
        self.map_width = map_data['map_size'][0]
        self.map_height = map_data['map_size'][1]
        self.map_resolution = map_data['map_resolution'][0]
        self.map_resolution_2 = map_data['map_resolution'][1]
        self.ui_info = ui_info
        self.res_width = self.map_width / self.map_resolution
        self.res_heigth = self.map_height / self.map_resolution_2




    def setMapImage(self,image_name):
        self.qPixmapVar = QPixmap("./sim/"+image_name)
        self.draw_image = True

    def paintEvent(self,e):
        qp = QPainter()
        qp.begin(self)
        if self.draw_image:
            qp.drawPixmap(self.rect(),self.qPixmapVar)
        if self.sim_data:
            robot_cordlist =self.sim_data["robot_cordinates"]
            robot_shelf = self.sim_data["shelf_node"]
            goal_cordinates = self.sim_data["goal_cordinates"]
            packing_color = self.sim_data["packing_color"]
            robot_routes = self.sim_data["robot_routes"]
            packing_point = self.sim_data['packing_point']
            robot_full_routes = self.sim_data["robot_full_routes"]
            compare_route = self.sim_data['compare_route']
            for i,[y, x] in enumerate(robot_cordlist):
                qp.setBrush(QColor(0, 0, 0))
                qp.setPen(QPen(QColor(189, 189, 189), 2))
                qp.drawRect(self.map_width/self.map_resolution *x, self.map_height/self.map_resolution_2 *y, self.map_width/self.map_resolution, self.map_height/self.map_resolution_2)
            init_x = self.ui_info[0]
            init_y = self.ui_info[1]
            if self.is_view_shelf:
                for i, ind_list in enumerate(robot_shelf):
                    qp.setBrush(QColor(255, 187, 0))

                    # x =self.shelfs[ind-1][0]- self.ui_info[0]
                    # y =self.shelfs[ind-1][1]- self.ui_info[1]

                    for ind in ind_list[1:-1]:

                        point = self.shelfs[ind-1]
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


                        small_x_index = math.floor((lefttop[0] - init_x) / self.res_width)  # 맨왼쪽 포함
                        big_x_index = math.ceil((rightbottom[0] - init_x) / self.res_width)
                        small_y_index = math.floor((lefttop[1] - init_y) / self.res_heigth)
                        big_y_index = math.ceil((rightbottom[1] - init_y) / self.res_heigth)
                        for i in range(small_y_index, big_y_index):
                            for j in range(small_x_index, big_x_index):
                                lefttop_x = self.res_width * j
                                lefttop_y = self.res_heigth * i
                                qp.drawRect(lefttop_x, lefttop_y, self.res_width, self.res_heigth)
            if self.is_view_full_route:
                init_x = self.ui_info[0]
                init_y = self.ui_info[1]

                for j, points in enumerate(robot_full_routes):
                    color = packing_color[self.sim_data['packing_ind'][j]]
                    qp.setPen(QPen(QColor(color[0], color[1], color[2]), 4))
                    for i in range(len(points)-1):

                        start =points[i]
                        end = points[i+1]
                        qp.drawLine(self.map_width / self.map_resolution * start[1]+self.res_width/2,
                                    self.map_height / self.map_resolution_2 * start[0]+self.res_heigth/2,
                                    self.map_width / self.map_resolution * end[1] + self.res_width / 2,
                                    self.map_height / self.map_resolution_2 * end[0] + self.res_heigth / 2)
            if self.is_view_route:
                init_x = self.ui_info[0]
                init_y = self.ui_info[1]


                for j, points in enumerate(robot_routes):
                    color = packing_color[self.sim_data['packing_ind'][j]]
                    qp.setPen(QPen(QColor(color[0], color[1], color[2]), 2))
                    for i in range(len(points)-1):

                        start =points[i]
                        end = points[i+1]
                        qp.drawLine(self.map_width / self.map_resolution * start[1]+self.res_width/2,
                                    self.map_height / self.map_resolution_2 * start[0]+self.res_heigth/2,
                                    self.map_width / self.map_resolution * end[1] + self.res_width / 2,
                                    self.map_height / self.map_resolution_2 * end[0] + self.res_heigth / 2)
                #경로를 어떻게 다른색으로 표현할까?
            qp.setPen(QPen(QColor(189,189,189), 2))
            #로봇의 현재 목표점을 그립니다.
            for i, [y, x] in enumerate(goal_cordinates):
                qp.setBrush(QColor(255, 0, 0))

                qp.drawRect(self.map_width / self.map_resolution * x,
                            self.map_height / self.map_resolution_2 * y,
                            self.map_width / self.map_resolution,
                            self.map_height / self.map_resolution_2)
            for i, [x,y] in enumerate(packing_point):
                color = packing_color[i]
                qp.setBrush(QColor(color[0], color[1], color[2]))
                small_x_index = math.floor((x- init_x) / self.res_width)  # 맨왼쪽 포함
                small_y_index = math.floor((y - init_y) / self.res_heigth)
                small_x_index = self.res_width * small_x_index
                small_y_index = self.res_heigth * small_y_index
                qp.drawRect(small_x_index, small_y_index,
                            self.map_width / self.map_resolution, self.map_height / self.map_resolution_2)

            if self.is_mode_compare:
                # 각 알고리즘별 경로를 그립니다.
                if len(compare_route) ==6:
                    qp.setBrush(QColor(217, 65, 197))

                    comp_ind =self.sim_data['compare_robot_ind']
                    if len(robot_shelf)>0:
                        for ind in robot_shelf[comp_ind][1:-1]:
                            point = self.shelfs[ind - 1]
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

                            small_x_index = math.floor((lefttop[0] - init_x) / self.res_width)  # 맨왼쪽 포함
                            big_x_index = math.ceil((rightbottom[0] - init_x) / self.res_width)
                            small_y_index = math.floor((lefttop[1] - init_y) / self.res_heigth)
                            big_y_index = math.ceil((rightbottom[1] - init_y) / self.res_heigth)
                            for i in range(small_y_index, big_y_index):
                                for j in range(small_x_index, big_x_index):
                                    lefttop_x = self.res_width * j
                                    lefttop_y = self.res_heigth * i
                                    qp.drawRect(lefttop_x, lefttop_y, self.res_width, self.res_heigth)

                        cordinate = self.sim_data["real_cordinate"]
                        # print(cordinate)
                        Qpens = [QPen(QColor(255,0,0), 2),
                                 QPen(QColor(255,228,0), 2),
                                 QPen(QColor(29,219,22), 2),
                                 QPen(QColor(0,84,225), 2),
                                 QPen(QColor(255,0,221), 2),
                                 QPen(QColor(0,216,255), 2)
                                 ]

                        for num, route in enumerate(compare_route):
                            qp.setPen(Qpens[num])
                            for i in range(len(route)-1):
                                [y_1, x_1]= cordinate[route[i]]
                                [y_2, x_2] = cordinate[route[i+1]]
                                qp.drawLine(x_1,y_1,x_2,y_2)
                            [y_1, x_1] = cordinate[route[-1]]
                            [y_2, x_2] = cordinate[route[0]]
                            qp.drawLine(x_1, y_1, x_2, y_2)

                        solver = self.sim_data["tsp_solver"]

                        if solver == "NO_TSP":
                            Qpens[0] = QPen(QColor(255, 0, 0), 10)
                            num =0
                            qp.setPen(Qpens[num])
                            for i in range(len(compare_route[num]) - 1):
                                [y_1, x_1] = cordinate[compare_route[num][i]]
                                [y_2, x_2] = cordinate[compare_route[num][i + 1]]
                                qp.drawLine(x_1, y_1, x_2, y_2)
                            [y_1, x_1] = cordinate[compare_route[num][-1]]
                            [y_2, x_2] = cordinate[compare_route[num][0]]
                            qp.drawLine(x_1, y_1, x_2, y_2)
                        elif solver == "GA":
                            Qpens[1] = QPen(QColor(255, 187, 0), 10)
                            num = 1
                            qp.setPen(Qpens[num])
                            for i in range(len(compare_route[num]) - 1):
                                [y_1, x_1] = cordinate[compare_route[num][i]]
                                [y_2, x_2] = cordinate[compare_route[num][i + 1]]
                                qp.drawLine(x_1, y_1, x_2, y_2)
                            [y_1, x_1] = cordinate[compare_route[num][-1]]
                            [y_2, x_2] = cordinate[compare_route[num][0]]
                            qp.drawLine(x_1, y_1, x_2, y_2)
                        elif solver == "PSO":
                            Qpens[2] = QPen(QColor(29, 219, 22), 10)
                            num = 2
                            qp.setPen(Qpens[num])
                            for i in range(len(compare_route[num]) - 1):
                                [y_1, x_1] = cordinate[compare_route[num][i]]
                                [y_2, x_2] = cordinate[compare_route[num][i + 1]]
                                qp.drawLine(x_1, y_1, x_2, y_2)
                            [y_1, x_1] = cordinate[compare_route[num][-1]]
                            [y_2, x_2] = cordinate[compare_route[num][0]]
                            qp.drawLine(x_1, y_1, x_2, y_2)
                        elif solver == "ACO":
                            Qpens[3] = QPen(QColor(0, 84, 225), 10)
                            num = 3
                            qp.setPen(Qpens[num])
                            for i in range(len(compare_route[num]) - 1):
                                [y_1, x_1] = cordinate[compare_route[num][i]]
                                [y_2, x_2] = cordinate[compare_route[num][i + 1]]
                                qp.drawLine(x_1, y_1, x_2, y_2)
                            [y_1, x_1] = cordinate[compare_route[num][-1]]
                            [y_2, x_2] = cordinate[compare_route[num][0]]
                            qp.drawLine(x_1, y_1, x_2, y_2)
                        elif solver == "DC":
                            Qpens[4] = QPen(QColor(255, 0, 221), 10)
                            num = 4
                            qp.setPen(Qpens[num])
                            for i in range(len(compare_route[num]) - 1):
                                [y_1, x_1] = cordinate[compare_route[num][i]]
                                [y_2, x_2] = cordinate[compare_route[num][i + 1]]
                                qp.drawLine(x_1, y_1, x_2, y_2)
                            [y_1, x_1] = cordinate[compare_route[num][-1]]
                            [y_2, x_2] = cordinate[compare_route[num][0]]
                            qp.drawLine(x_1, y_1, x_2, y_2)
                        elif solver == "GREEDY":
                            Qpens[5] = QPen(QColor(0, 216, 255), 10)
                            num = 5
                            qp.setPen(Qpens[num])
                            for i in range(len(compare_route[num]) - 1):
                                [y_1, x_1] = cordinate[compare_route[num][i]]
                                [y_2, x_2] = cordinate[compare_route[num][i + 1]]
                                qp.drawLine(x_1, y_1, x_2, y_2)
                            [y_1, x_1] = cordinate[compare_route[num][-1]]
                            [y_2, x_2] = cordinate[compare_route[num][0]]
                            qp.drawLine(x_1, y_1, x_2, y_2)


                #후보 경로들을 모두 시각화합니다. 비교대상으로 쓰이는 로봇을 더 눈에 뛰게 합니다.
                [y, x] = robot_cordlist[self.sim_data['compare_robot_ind']]

                brush = QBrush(QColor(29, 219, 22), style =Qt.Dense2Pattern)
                qp.setBrush(brush)
                qp.setPen(QPen(QColor(255, 0, 0), 2))
                qp.drawRect(self.map_width / self.map_resolution * x, self.map_height / self.map_resolution_2 * y,
                            self.map_width / self.map_resolution, self.map_height / self.map_resolution_2)

        qp.end()




class Widget_drawMap(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)

        '''
        맵을 한번다시 그려서 저장하는 모듈 이제 쓸일없다.
        '''
    def draw_and_save(self, map_data, map_image_name,ui_info):
        self.map_data = map_data
        self.map_width = map_data['map_size'][0]
        self.map_height = map_data['map_size'][1]
        self.map_resolution = map_data['map_resolution'][0]
        self.map_resolution_2 = map_data['map_resolution'][1]
        self.occupy_map = map_data['occupay_map']
        self.saved_shelf_point = map_data['shelf_point']
        self.saved_block_point = map_data['block_point']
        self.saved_pk_point = map_data['pack_point']
        self.saved_sp_point = map_data['start_point']

        self.image = QImage(QSize(self.map_width,self.map_height),QImage.Format_RGB32)
        self.image.fill(Qt.white)
        self.ui_info = ui_info



        qp = QPainter()
        qp.begin(self.image)
        self.draw(qp)
        qp.end()
        self.image.save("./sim/"+map_image_name)





    def draw(self, qp):
        init_x = 0
        init_y = 0
        qp.setPen(QPen(QColor(189,189,189), 2))
        qp.drawRect(init_x, init_y, self.map_width, self.map_height)
        res_width = self.map_width / self.map_resolution
        res_heigth = self.map_height / self.map_resolution_2
        # 맵의 격자를 그립니다.
        for i in range(self.map_resolution):
            res_x = int(init_x + (i + 1) * res_width)
            qp.drawLine(res_x, init_y, res_x, init_y + self.map_height)

        for i in range(self.map_resolution_2):
            res_y = int(init_y + (i + 1) * res_heigth)
            qp.drawLine(init_x, res_y, init_x + self.map_width, res_y)

        # 선반 그리기
        #마우스 좌표가 이전에 찍힌 위치를 기준으로 형성되어있음..초기선반위치는 0으로 하고 좌표에서 빼야함
        for ind, point in enumerate(self.saved_shelf_point):

            point_x = point[0] - self.ui_info[0]
            point_y = point[1] - self.ui_info[1]
            if point[2] == 0 or point[2] == 180:
                lefttop = [point_x - int(point[3] / 2),
                           point_y - int(point[4] / 2)]
                rightbottom = [point_x + int(point[3] / 2),
                               point_y + int(point[4] / 2)]
            else:
                lefttop = [point_x - int(point[4] / 2),
                           point_y - int(point[3] / 2)]
                rightbottom = [point_x + int(point[4] / 2),
                               point_y + int(point[3] / 2)]
            qp.setBrush(QColor(0, 100, 0))
            qp.setPen(QPen(QColor(189,189,189), 2))
            init_x = 0
            init_y = 0

            small_x_index = math.floor((lefttop[0] - init_x) / res_width)  # 맨왼쪽 포함
            big_x_index = math.ceil((rightbottom[0] - init_x) / res_width)
            small_y_index = math.floor((lefttop[1] - init_y) / res_heigth)
            big_y_index = math.ceil((rightbottom[1] - init_y) / res_heigth)
            for i in range(small_y_index, big_y_index):
                for j in range(small_x_index, big_x_index):
                    lefttop_x = init_x + res_width * j
                    lefttop_y = init_y + res_heigth * i
                    qp.drawRect(lefttop_x, lefttop_y, res_width, res_heigth)
        # 벽그리기

        for ind, block_point in enumerate(self.saved_block_point):

            init_x = 0
            init_y = 0
            block_point_x = block_point[0] - self.ui_info[0]
            block_point_y = block_point[1] - self.ui_info[1]
            qp.setBrush(QColor(0, 0, 0))
            qp.setPen(QPen(QColor(189,189,189), 2))
            small_x_index = math.floor((block_point_x - init_x) / res_width)  # 맨왼쪽 포함
            big_x_index = math.ceil((block_point_x - init_x) / res_width)
            small_y_index = math.floor((block_point_y - init_y) / res_heigth)
            big_y_index = math.ceil((block_point_y - init_y) / res_heigth)
            small_x_index = init_x + res_width * small_x_index
            # big_x_index = init_x + res_width * big_x_index
            small_y_index = init_y + res_heigth * small_y_index
            # big_y_index = init_y + res_heigth * big_y_index
            qp.drawRect(small_x_index, small_y_index, res_width, res_heigth)

        # 시작지점그리기
        for ind, block_point in enumerate(self.saved_sp_point):
            init_x = 0
            init_y = 0
            block_point_x = block_point[0] - self.ui_info[0]
            block_point_y = block_point[1] - self.ui_info[1]
            qp.setBrush(QColor(255, 0, 127))
            qp.setPen(QPen(QColor(189,189,189), 2))
            small_x_index = math.floor((block_point_x - init_x) / res_width)  # 맨왼쪽 포함
            big_x_index = math.ceil((block_point_x - init_x) / res_width)
            small_y_index = math.floor((block_point_y - init_y) / res_heigth)
            big_y_index = math.ceil((block_point_y - init_y) / res_heigth)
            small_x_index = init_x + res_width * small_x_index
            big_x_index = init_x + res_width * big_x_index
            small_y_index = init_y + res_heigth * small_y_index
            big_y_index = init_y + res_heigth * big_y_index
            qp.drawRect(small_x_index, small_y_index, res_width, res_heigth)

        # 패킹지점그리기
        for ind, block_point in enumerate(self.saved_pk_point):
            init_x = 0
            init_y = 0
            block_point_x = block_point[0] - self.ui_info[0]
            block_point_y = block_point[1] - self.ui_info[1]
            qp.setBrush(QColor(0, 0, 255))
            qp.setPen(QPen(QColor(189,189,189), 2))
            small_x_index = math.floor((block_point_x - init_x) / res_width)  # 맨왼쪽 포함
            big_x_index = math.ceil((block_point_x - init_x) / res_width)
            small_y_index = math.floor((block_point_y - init_y) / res_heigth)
            big_y_index = math.ceil((block_point_y - init_y) / res_heigth)
            small_x_index = init_x + res_width * small_x_index
            big_x_index = init_x + res_width * big_x_index
            small_y_index = init_y + res_heigth * small_y_index
            big_y_index = init_y + res_heigth * big_y_index
            qp.drawRect(small_x_index, small_y_index, res_width, res_heigth)


class Widget_Simulator(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("Simulator.ui",self)

        self.is_view_shelf = False
        self.is_view_route =False
        self.is_view_full_route = False
        self.checkBox_viewAllShelf.stateChanged.connect(self.viewShelf)
        self.timer = QTimer(self)

        self.timer.timeout.connect(self.update_orders)
        self.radioButton_ACO.clicked.connect(self.set_aco)
        self.radioButton_GA.clicked.connect(self.set_ga)
        self.radioButton_PSO.clicked.connect(self.set_pso)
        self.radioButton_DC.clicked.connect(self.set_dc)
        self.radioButton_GREEDY.clicked.connect(self.set_greedy)
        self.radioButton_notsp.clicked.connect(self.set_notsp)


        self.checkBox_viewRoute.stateChanged.connect(self.viewRoute)
        self.checkBox_viewFullRoute.stateChanged.connect(self.viewFullRoute)

        self.checkBox_modecompare.stateChanged.connect(self.modeCompare)
        self.is_mode_compare = False
        self.tsp_mode = "NO_TSP"
        self.label_lengthsay.hide()
        self.label_timesay.hide()
        self.image = Simulator(self)
        '''
        해야할 것.
        1. 맵에 대한 visualization을 해야함.(성공)
        - 맵을 위젯위에 한번그리고 난뒤 이미지로 저장
        - 그후에 저장된 이미지를 이미지 위젯위에 표시
        - 이미지 위젯 위에 draw함수를 사용해서 로봇 및 경로? 표시 
        - 문제점 : 과연 위젯 위에 draw가 될까? 
        2. 
        '''
    def modeCompare(self):
        if self.is_mode_compare:
            self.is_mode_compare = False
            self.image.is_mode_compare= False
            self.label_lengthsay.hide()
            self.label_timesay.hide()
        else :
            self.is_mode_compare = True
            self.image.is_mode_compare = True
            self.label_lengthsay.show()
            self.label_timesay.show()
            if self.is_view_full_route:
                self.checkBox_viewFullRoute.toggle()
                self.is_view_full_route = False
                self.image.is_view_full_route = False
            if self.is_view_route:
                self.checkBox_viewRoute.toggle()
                self.is_view_route = False
                self.image.is_view_route = False

    def closeEvent(self, QCloseEvent):
        self.sim_data['is_kill_robot_move'] = True
        time.sleep(0.3)

        self.sim_data["tsp_solver"] = "DC"
        self.order_data["is_start"] = False
        self.sim_data["is_start"] = False
        self.sim_data["robot_cordinates"] = []
        self.sim_data["goal_cordinates"] = []
        self.sim_data["shelf_node"] = []
        self.sim_data["robot_routes"] = []
        self.sim_data["packing_ind"] = []
        self.sim_data["packing_color"] = []
        self.sim_data["packing_point"] = []
        self.sim_data["robot_full_routes"] = []
        self.sim_data['compare_robot_ind'] = 0
        self.order_data["is_set_order"] = False  # 선반의 개수가 다 정해졋는지 확인할 때, 사용하는변수
        self.order_data["is_set_initOrder"] = False  # 초기 주문들이 다 정해졋을때, 사용하는 변수
        self.sim_data["reset"] =True
        self.order_data["reset"] = True
        self.sim_data["doing_order"] =0
        self.image.timer.stop()
        self.timer.stop()



    def set_process(self, order_maker, warehouse_tsp_solver):
        self.order_maker =order_maker
        self.warehouse_tsp_solver = warehouse_tsp_solver

    def set_greedy(self):
        self.tsp_mode = "GREEDY"
        self.sim_data["tsp_solver"] = self.tsp_mode

    def set_dc(self):
        self.tsp_mode = "DC"
        self.sim_data["tsp_solver"] = self.tsp_mode

    def viewFullRoute(self):
        if self.is_view_full_route:
            self.is_view_full_route = False
            self.image.is_view_full_route = False
        else:
            self.is_view_full_route = True
            self.image.is_view_full_route = True
    def viewRoute(self):
        if self.is_view_route:
            self.is_view_route = False
            self.image.is_view_route = False
        else:
            self.is_view_route = True
            self.image.is_view_route = True
    def set_aco(self):
        self.tsp_mode ="ACO"
        self.sim_data["tsp_solver"] =self.tsp_mode
    def set_ga(self):
        self.tsp_mode ="GA"
        self.sim_data["tsp_solver"] = self.tsp_mode
    def set_pso(self):
        self.tsp_mode ="PSO"
        self.sim_data["tsp_solver"] = self.tsp_mode
    def set_notsp(self):
        self.tsp_mode ="NO_TSP"
        self.sim_data["tsp_solver"] =self.tsp_mode

    def set_data(self, order_data,sim_data):
        self.order_data = order_data
        self.sim_data = sim_data
        self.sim_data["tsp_solver"] = self.tsp_mode

    def viewShelf(self):
        if self.is_view_shelf:
            self.is_view_shelf = False
            self.image.is_view_shelf = False
        else:
            self.is_view_shelf = True
            self.image.is_view_shelf = True

    def setMapInfo(self,map_data,ui_info):
        self.map_data = map_data
        self.map_width = map_data['map_size'][0]
        self.map_height = map_data['map_size'][1]
        self.map_resolution = map_data['map_resolution'][0]
        self.map_resolution_2 = map_data['map_resolution'][1]
        self.occupy_map = map_data['occupay_map']
        #위의 맵은 행 크기 : map_resolution, 열 크기 : map_resolution_2
        #각 선반에 대해서 차지하고 있는 영역이 1부터 선반 수로 인덱싱이 되있음
        #각 블록이 차지하고 있는 영역은 -1부터 -블럭수로 인덱싱되있음
        #시작점은 없으니 제외
        #각 패킹지점이 차지하고 있는 영역은 20001부터 20000+패키지점수로 인덱싱되있음
        #그 외에 지점은 0으로 인덱싱 되있음
        self.saved_shelf_point = map_data['shelf_point']
        self.saved_block_point = map_data['block_point']
        self.saved_pk_point = map_data['pack_point']
        self.saved_sp_point = map_data['start_point']
        self.map_drawer = Widget_drawMap(self)
        self.map_drawer.hide()
        self.map_name = 'map.jpg'

        #맵을 한번 그려서 저장합니다.
        self.map_drawer.draw_and_save(self.map_data,self.map_name,ui_info)
        self.ui_info =ui_info

    def update_orders(self):
        a =self.order_data['sim_data'][1] - self.sim_data["doing_order"]
        self.lineEdit_lastOrder.setText(str(a))
        self.update()

    def paintEvent(self,e):
        if self.is_mode_compare:
            qp = QPainter()
            qp.begin(self)

            Qpens = [QPen(QColor(255, 0, 0), 2),
                     QPen(QColor(255, 187, 0), 2),
                     QPen(QColor(29, 219, 22), 2),
                     QPen(QColor(0, 84, 225), 2),
                     QPen(QColor(255, 0, 221), 2),
                     QPen(QColor(0, 216, 255), 2)
                     ]
            length = self.sim_data["tsp_length"]
            compare_time = self.sim_data["compare_time"]
            for i in range(6):
                x = 0
                y = 0
                if i==0:
                    x =self.groupBox_viewer.geometry().left()+self.radioButton_notsp.geometry().left()+90
                    y =self.groupBox_viewer.geometry().top()+self.radioButton_notsp.geometry().top()+11
                    # print("hi")
                elif i ==1:
                    x = self.groupBox_viewer.geometry().left()+self.radioButton_GA.geometry().left()+90
                    y = self.groupBox_viewer.geometry().top()+self.radioButton_GA.geometry().top()+11
                elif i ==2:
                    x = self.groupBox_viewer.geometry().left()+self.radioButton_PSO.geometry().left()+90
                    y = self.groupBox_viewer.geometry().top()+self.radioButton_PSO.geometry().top()+11
                elif i==3:
                    x = self.groupBox_viewer.geometry().left()+self.radioButton_ACO.geometry().left()+90
                    y = self.groupBox_viewer.geometry().top()+self.radioButton_ACO.geometry().top()+11
                elif i==4:
                    x = self.groupBox_viewer.geometry().left()+self.radioButton_DC.geometry().left()+90
                    y = self.groupBox_viewer.geometry().top()+self.radioButton_DC.geometry().top()+11
                elif i==5:
                    x = self.groupBox_viewer.geometry().left()+self.radioButton_GREEDY.geometry().left()+90
                    y = self.groupBox_viewer.geometry().top()+self.radioButton_GREEDY.geometry().top()+11
                qp.setPen(Qpens[i])
                qp.setFont(QFont('Arial', 9))
                qp.drawText(x,y,str(math.ceil(length[i])))
                qp.drawText(x+70, y, str(math.ceil(compare_time[i]*1000)/1000))

            qp.end()

    def setSimInfo(self,sim_data):

        self.is_randomOrder = sim_data[0]
        self.initOrder = sim_data[1]
        self.last_order_rate = sim_data[2]
        self.robot_cap = sim_data[3]
        self.robot_number = sim_data[4]
    def set_shared_data(self,sim_data):
        self.sim_shared_data = sim_data


    def start_setting(self):
        self.image = Simulator(self)
        self.image.setMapImage(self.map_name)#self.map_name의 이미지를 다운로드해서 그립니다.
        self.image.resize(self.map_width,self.map_height)#그려지는 이미지의 사이즈를 원래 맵의 형태로 합니다.
        self.image.setData(self.sim_shared_data,self.map_data,self.ui_info)

        # 전체 시물레이션의 위젯 크기를 조정합니다.
        self.setFixedWidth(self.map_width+10+self.groupBox_viewer.width()+10)
        self.groupBox_viewer.move(self.map_width+10,20)
        self.setFixedHeight(self.map_height)

        self.image.show()
        self.image.update()#맵을 그립니다.
        self.timer.start(100)


####위에는 visualize가되어 있는 코드입니다.
class sim_viwer(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("simulation_result_viewer.ui", self)
        self.pushButton_viewresult.clicked.connect(self.startreal_sim)
        self.simulator = Widget_Simulator()
        self.simulator.hide()
        self.sim_data = None
        self.order_data = None
    def startreal_sim(self):
        if self.simulator :
            del self.simulator#시물레이터를 삭제합니다.
        self.simulator = Widget_Simulator()
        self.order_data["reset"] = True  # order 생성을 리셋합니다.
        self.order_data["is_set_order"] = False  # 선반의 개수가 다 정해졋는지 확인할 때, 사용하는변수
        self.order_data["is_set_initOrder"] = False  # 초기 주문들이 다 정해졋을때, 사용하는 변수
        self.order_data['is_start'] = True
        self.sim_data['is_start'] = True

        self.map_data = self.sim_data['map_data']
        self.ui_info = self.sim_data['ui_info']
        self.simulator.setMapInfo(self.map_data, self.ui_info)
        self.simulator.set_shared_data(self.sim_data)
        self.simulator.set_data(self.order_data, self.sim_data)
        self.simulator.start_setting()  # 그냥 시작합니다.
        self.simulator.show()


    def ViewData(self,order_data,sim_data,to_el_time,av_tr_time,av_tr_distance):
        self.sim_data = sim_data
        self.order_data =order_data
        temp = sim_data["sim_info_ronum_rocap_initorder"]#로봇수, 로봇의 허용량, 초기 주문량등이 정해져있다.
        robot_number = temp[0]
        robot_cap = temp[1]
        init_order = temp[2]
        map_data = sim_data['map_data']

        map_width = map_data['map_size'][0]
        map_height = map_data['map_size'][1]
        map_resolution = map_data['map_resolution'][0]
        map_resolution_2 = map_data['map_resolution'][1]
        occupy_map = map_data['occupay_map']
        res_width = map_width / map_resolution
        shelf_number = len(map_data['shelf_point'])
        # print(robot_number,robot_cap,init_order)
        self.label_robot_number.setText(str(robot_number))
        self.label_order_number.setText(str(init_order))
        # self.label_capacity.setText(str(robot_cap))
        self.label_robotspeed.setText(str(1)+"m/s")
        self.label_w_size.setText(str(map_width)+" X "+str(map_height)+"m")
        self.label_shelves.setText(str(shelf_number))
        algorithm_name = ['Random',"Div & Conq","Greedy","PSO","GA","ACO"]
        algorithm_color = ['black', 'red', 'gold', 'lawngreen', 'deepskyblue', 'darkviolet']
        fig = plt.figure(figsize=(6, 5.5))
        # 전체 수행시간에 대한 막대그래프를 그립니다.
        al_length = len(to_el_time)
        x = np.arange(al_length)
        robot_value = to_el_time
        plt.title("Total elapsed time", fontsize=12)
        plt.bar(x, robot_value, width=0.8, color=algorithm_color)
        plt.xticks(x,algorithm_name,fontsize= 8)
        plt.xlabel("Algorithm", fontsize=10)
        plt.ylabel("Minute", fontsize=10)
        plt.savefig("result/전체수행시간.png")
        plt.clf()

        fig = plt.figure(figsize=(5, 4.7))
        # 전체 수행시간에 대한 막대그래프를 그립니다.
        al_length = len(to_el_time)
        x = np.arange(al_length)
        robot_value = sim_data['Computation_time']
        plt.title("Computation time", fontsize=12)
        plt.bar(x, robot_value, width=0.8, color=algorithm_color)
        plt.xticks(x, algorithm_name, fontsize=8)
        plt.xlabel("Algorithm", fontsize=10)
        plt.ylabel("Second", fontsize=10)
        plt.savefig("result/전체_계산시간.png")
        plt.clf()

        fig = plt.figure(figsize=(6, 5.5))
        b_data = copy.copy(sim_data['algorithm_step'])
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
        plt.savefig("result/평균이동거리.png")
        plt.clf()

        fig = plt.figure(figsize=(5, 5))
        b_data = copy.copy(sim_data['algorithm_time'])
        plt.title("Travel time", fontsize=12)
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
        plt.ylabel("Minute", fontsize=10)
        plt.savefig("result/평균이동시간.png")
        plt.clf()



        self.qPixmapVar = QPixmap()
        self.qPixmapVar.load("./sim/"+'map.jpg')
        self.qPixmapVar = self.qPixmapVar.scaled(self.label_wi.width(),self.label_wi.height(),Qt.KeepAspectRatio)
        self.label_wi.setPixmap(self.qPixmapVar)

        self.qPixmapVar = QPixmap()
        self.qPixmapVar.load("result/전체수행시간.png")
        self.qPixmapVar = self.qPixmapVar.scaled(self.label_tet.width(), self.label_tet.height(),Qt.KeepAspectRatio)
        # self.qPixmapVar = self.qPixmapVar.scaled(self.label_tet.width(), self.label_tet.height())
        self.label_tet.setPixmap(self.qPixmapVar)

        self.qPixmapVar = QPixmap()
        self.qPixmapVar.load("result/평균이동거리.png")
        self.qPixmapVar = self.qPixmapVar.scaled(self.label_att.width(), self.label_att.height(),Qt.KeepAspectRatio)
        self.label_att.setPixmap(self.qPixmapVar)

        self.qPixmapVar = QPixmap()
        self.qPixmapVar.load("result/평균이동시간.png")
        self.qPixmapVar = self.qPixmapVar.scaled(self.label_atd.width(), self.label_atd.height(),Qt.KeepAspectRatio)
        # self.qPixmapVar = self.qPixmapVar.scaled(self.label_atd.width(), self.label_atd.height())
        self.label_atd.setPixmap(self.qPixmapVar)

        self.qPixmapVar = QPixmap()
        self.qPixmapVar.load("result/전체_계산시간.png")
        self.qPixmapVar = self.qPixmapVar.scaled(self.label_ct.width(), self.label_ct.height(), Qt.KeepAspectRatio)
        self.label_ct.setPixmap(self.qPixmapVar)

        # self.qPixmapVar = QPixmap()
        # self.qPixmapVar.load("result/notsp_bp.png")
        # self.qPixmapVar = self.qPixmapVar.scaled(self.label_no_tsp.width(), self.label_no_tsp.height())
        # self.label_no_tsp.setPixmap(self.qPixmapVar)

class Widget_Simulator_no_gui(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("info_simulator.ui",self)
        # self.is_view_shelf = False
        # self.is_view_route =False
        # self.is_view_full_route = False
        # self.checkBox_viewAllShelf.stateChanged.connect(self.viewShelf)
        self.timer = QTimer(self)
        self.tsp_mode = "ACO"
        self.timer.timeout.connect(self.update_progress)
        self.button_saveresult.clicked.connect(self.saveresult)
        self.button_showresult.clicked.connect(self.showresult)
        self.sim_viwer_a = sim_viwer()
        self.button_saveresult.hide()

    def showresult(self):
        to_el_time = self.sim_data['Total_elapsed_time']
        av_tr_time = self.sim_data['Average_travel_time']
        av_tr_distance = self.sim_data['Average_travel_distance']
        self.sim_viwer_a.ViewData(self.order_data,self.sim_data, to_el_time,av_tr_time,av_tr_distance)
        self.sim_viwer_a.show()
        # print('Algorithm_execution_time', self.sim_data['Total_elapsed_time'])
        # print('Average_travel_time', self.sim_data['Average_travel_time'])
        # print('Average_travel_distance', self.sim_data['Average_travel_distance'])

    def closeEvent(self, QCloseEvent):
        self.order_data['is_start'] = False
        self.sim_data["fast_start"] = False
        self.order_data["is_set_order"] = False  # 선반의 개수가 다 정해졋는지 확인할 때, 사용하는변수
        self.order_data["is_set_initOrder"] = False  # 초기 주문들이 다 정해졋을때, 사용하는 변수
        self.order_data["reset"] = True
        self.sim_data['solver_ind'] = 0
        self.sim_data['order_do'] = 0
        self.sim_data['algorithm_time'] = [[], [], [], [], [], []]
        self.sim_data['algorithm_step'] = [[], [], [], [], [], []]
        self.sim_data['algorithm_full_time'] = [0. for _ in range(len(self.sim_data['solver_set']))]
        self.sim_data['simulation_end'] = False
        self.sim_data['Total_elapsed_time'] = [0. for _ in range(len(self.sim_data['solver_set']))]
        self.sim_data['Average_travel_time'] = [0. for _ in range(len(self.sim_data['solver_set']))]
        self.sim_data['Average_travel_distance'] = [0. for _ in range(len(self.sim_data['solver_set']))]
        self.sim_data["force_die"] = True
        self.button_showresult.setDisabled(True)
        self.button_saveresult.setDisabled(True)
        # print("all dead")
        self.timer.stop()

    def saveresult(self):
        al_time = self.sim_data['algorithm_time']
        al_step = self.sim_data['algorithm_step']
        al_full_time = self.sim_data['algorithm_full_time']
        makePDF(al_time,al_step,al_full_time)

    def update_progress(self):
        do_order = self.sim_data['order_do']
        full_order =self.order_data['sim_data'][1]*6.
        percent = int(do_order/full_order*100)
        self.progressBar.setValue(percent)
        if percent ==100 :
            self.button_showresult.setEnabled(True)
            # self.button_saveresult.setEnabled(True)

            self.map_drawer = Widget_drawMap(self)
            self.map_drawer.hide()
            self.map_name = 'map.jpg'

            # 맵을 한번 그려서 저장합니다.
            self.map_drawer.draw_and_save(self.map_data, self.map_name, self.ui_info)

    def set_data(self, order_data,sim_data,map_data,ui_info):
        self.order_data = order_data
        self.sim_data = sim_data
        self.map_data = map_data
        self.ui_info = ui_info


    def start_setting(self):
        self.order_data['is_start'] = True
        self.sim_data["fast_start"] = True
