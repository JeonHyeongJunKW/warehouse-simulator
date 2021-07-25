from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import math
import json

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
            # print(self.sim_data["robot_cordinates"])
            for i,[y, x] in enumerate(self.sim_data["robot_cordinates"]):
                qp.setBrush(QColor(0, 0, 0))
                qp.setPen(QPen(QColor(189, 189, 189), 2))
                qp.drawRect(self.map_width/self.map_resolution *x, self.map_height/self.map_resolution_2 *y, self.map_width/self.map_resolution, self.map_height/self.map_resolution_2)
            init_x = self.ui_info[0]
            init_y = self.ui_info[1]
            if self.is_view_shelf:

                for i, ind_list in enumerate(self.sim_data["shelf_node"]):
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


                for j, points in enumerate(self.sim_data["robot_full_routes"]):
                    color = self.sim_data["packing_color"][self.sim_data['packing_ind'][j]]
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


                for j, points in enumerate(self.sim_data["robot_routes"]):
                    color = self.sim_data["packing_color"][self.sim_data['packing_ind'][j]]
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
            for i, [y, x] in enumerate(self.sim_data["goal_cordinates"]):
                qp.setBrush(QColor(255, 0, 0))

                qp.drawRect(self.map_width / self.map_resolution * x,self.map_height / self.map_resolution_2 * y,self.map_width / self.map_resolution, self.map_height / self.map_resolution_2)
            for i, [x,y] in enumerate(self.sim_data['packing_point']):
                color = self.sim_data["packing_color"][i]
                # print([x,y])
                qp.setBrush(QColor(color[0], color[1], color[2]))
                small_x_index = math.floor((x- init_x) / self.res_width)  # 맨왼쪽 포함
                small_y_index = math.floor((y - init_y) / self.res_heigth)
                small_x_index = self.res_width * small_x_index
                small_y_index = self.res_heigth * small_y_index
                qp.drawRect(small_x_index, small_y_index,
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
        self.tsp_mode = "ACO"
        self.timer.timeout.connect(self.update_orders)
        self.radioButton_ACO.clicked.connect(self.set_aco)
        self.radioButton_GA.clicked.connect(self.set_ga)
        self.radioButton_PSO.clicked.connect(self.set_pso)
        self.radioButton_DC.clicked.connect(self.set_dc)
        self.radioButton_GREEDY.clicked.connect(self.set_greedy)
        self.radioButton_notsp.clicked.connect(self.set_notsp)

        self.checkBox_viewRoute.stateChanged.connect(self.viewRoute)
        self.checkBox_viewFullRoute.stateChanged.connect(self.viewFullRoute)
        '''
        해야할 것.
        1. 맵에 대한 visualization을 해야함.(성공)
        - 맵을 위젯위에 한번그리고 난뒤 이미지로 저장
        - 그후에 저장된 이미지를 이미지 위젯위에 표시
        - 이미지 위젯 위에 draw함수를 사용해서 로봇 및 경로? 표시 
        - 문제점 : 과연 위젯 위에 draw가 될까? 
        2. 
        '''
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
        self.lineEdit_lastOrder.setText(str(self.sim_data["number_order"]))



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
        self.timer.start(300)

