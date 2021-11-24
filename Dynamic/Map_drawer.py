from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import math
class map_maker(QWidget):
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