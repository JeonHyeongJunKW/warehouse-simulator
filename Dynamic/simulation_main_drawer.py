from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *


class main_drawer(QLabel):
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

    def default_set(self,map_data, map_name):
        self.map_data = map_data
        self.map_name = map_name
        self.map_width = map_data['map_size'][0]
        self.map_height =map_data['map_size'][1]
        self.map_resolution = map_data['map_resolution'][0]
        self.map_resolution_2 = map_data['map_resolution'][1]
        self.ui_info = ui_info
        self.res_width = self.map_width / self.map_resolution
        self.res_heigth = self.map_height / self.map_resolution_2

        self.resize(self.map_width,self.map_height)
        simualtor_width = self.map_width + 20

        return simualtor_width, self.map_height
