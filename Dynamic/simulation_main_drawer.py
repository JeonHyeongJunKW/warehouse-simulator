from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from Dynamic.DEBUG_tool import DEBUG_log
import math
import copy

class main_drawer(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__( *args, **kwargs)
        self.timer = QTimer(self)
        self.timer.start(100)
        self.timer.timeout.connect(self.update)


        self.is_view_shelf = False
        self.is_view_route = False
        self.is_view_full_route = False
        self.is_view_target = False
        self.is_view_solo_target = False

        #시뮬레이션을 그릴지 확인합니다.
        self.draw_flag = False
    def start_draw(self, gui_data):
        self.gui_data = gui_data
        self.draw_flag = True


    def setMapImage(self,image_name):
        self.qPixmapVar = QPixmap("./sim/"+image_name)
        self.draw_image = True

    def default_set(self,map_data, map_name,ui_info):
        self.map_data = map_data
        self.map_name = map_name
        self.shelfs = map_data['shelf_point']
        self.map_width = map_data['map_size'][0]
        self.map_height =map_data['map_size'][1]
        self.map_resolution = map_data['map_resolution'][0]
        self.map_resolution_2 = map_data['map_resolution'][1]
        self.ui_info = ui_info
        self.res_width = self.map_width / self.map_resolution
        self.res_heigth = self.map_height / self.map_resolution_2
        self.resize(self.map_width,self.map_height)
        simulator_width = self.map_width + 200
        return simulator_width, self.map_height

    def paintEvent(self,e):
        qp = QPainter()
        qp.begin(self)
        if self.draw_flag:
            init_x = self.ui_info[0]
            init_y = self.ui_info[1]
            qPixmapVar = QPixmap("./sim/"+self.map_name)
            qp.drawPixmap(self.rect(),qPixmapVar)
            robot_cordlist =self.gui_data["current_robot_position"]
            goal_cordinates = self.gui_data["current_target"]

            robot_routes = self.gui_data["short_path"]
            robot_full_routes = self.gui_data["long_path"]

            packing_color = self.gui_data["packing_color"]
            packing_point = self.gui_data['packing_point']


            for i,[y, x] in enumerate(robot_cordlist):
                if self.is_view_solo_target and i==0:
                    qp.setPen(QPen(QColor(189, 189, 189), 2))
                    qp.setBrush(QColor(217, 65, 197))
                else:
                    qp.setBrush(QColor(0, 0, 0))
                    qp.setPen(QPen(QColor(189, 189, 189), 2))
                qp.drawRect(self.map_width/self.map_resolution *x, self.map_height/self.map_resolution_2 *y, self.map_width/self.map_resolution, self.map_height/self.map_resolution_2)

            if self.is_view_full_route:


                for j, points in enumerate(robot_full_routes):
                    color = packing_color[self.gui_data['packing_ind'][j]]
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
                    color = packing_color[self.gui_data['packing_ind'][j]]
                    qp.setPen(QPen(QColor(color[0], color[1], color[2]), 2))
                    for i in range(len(points)-1):

                        start =points[i]
                        end = points[i+1]
                        qp.drawLine(self.map_width / self.map_resolution * start[1]+self.res_width/2,
                                    self.map_height / self.map_resolution_2 * start[0]+self.res_heigth/2,
                                    self.map_width / self.map_resolution * end[1] + self.res_width / 2,
                                    self.map_height / self.map_resolution_2 * end[0] + self.res_heigth / 2)

                #경로를 어떻게 다른색으로 표현할까?
            if self.is_view_solo_target:
                qp.setBrush(QColor(255, 187, 0))
                qp.setPen(QPen(QColor(189, 189, 189), 2))
                for ind in self.gui_data["zero_robot_pick_point"]:
                    point = self.shelfs[ind]
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


            qp.setPen(QPen(QColor(189,189,189), 2))
            #로봇의 현재 목표점을 그립니다.
            if self.is_view_target:
                for i, point in enumerate(goal_cordinates):
                    if len(point)==2:
                        x = point[1]
                        y = point[0]
                        qp.setBrush(QColor(255, 0, 0))

                        qp.drawRect(self.map_width / self.map_resolution * x,
                                    self.map_height / self.map_resolution_2 * y,
                                    self.map_width / self.map_resolution,
                                    self.map_height / self.map_resolution_2)
                    else:
                        continue

            for i, [x,y] in enumerate(packing_point):
                color = packing_color[i]
                qp.setBrush(QColor(color[0], color[1], color[2]))
                small_x_index = math.floor((x- init_x) / self.res_width)  # 맨왼쪽 포함
                small_y_index = math.floor((y - init_y) / self.res_heigth)
                small_x_index = self.res_width * small_x_index
                small_y_index = self.res_heigth * small_y_index
                qp.drawRect(small_x_index, small_y_index,
                            self.map_width / self.map_resolution, self.map_height / self.map_resolution_2)


        qp.end()
