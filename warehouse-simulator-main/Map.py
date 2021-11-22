import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import  *
from PyQt5.QtCore import Qt
import math
import json


class Warehouse_Shelf :
    def __init__(self, center_x, center_y, shelf_index, shelf_shape =(2,3),item_type=[1,1,1,1,1,1] ,item_amount=[10,10,10,10,10,10],supply_limit= 3,infinite_amount = True):
        self.center_x = center_x
        self.center_y = center_y
        self.shelf_shape =shelf_shape
        self.item_type = item_type
        self.item_amount = item_amount
        self.shelf_index = shelf_index# 선반 번호
        self.supply_list = [] #재고가 얼마없는 부분
        self.supply_limit =supply_limit# 재고가 얼마없다고 느끼는 양
        self.infinite_amount= infinite_amount #물건의 개수가 무한대인가? 공급필요 x
    '''
    고려사항 :
    - 선반안에 재고의  수가 무한인지
    - 선반의 크기, 각 칸별 종류
    - 꺼낼때, 선반의 위치를 따지는지 
    '''

    def isEmpty(self):
        if len(self.supply_list) >0:
            return True
        else:
            return False

    def mode_infinity(self, infinite_amount):#선반안에 재고의  수가 무한인지
        self.infinite_amount= infinite_amount

    def delete_item(self, item_type,item_point = None,delete_amount=1):# 이 선반의 특정 위치의 item수를 줄입니다.
        if item_point is None: #만약에 물건의 위치가 아닌 해당 선반이 가진 물건 종류로만 따진다면
            #해당 아이템을 가진 선반을 찾습니다.
            item_type_ind = [self.item_amount[i] for i,value in enumerate(self.item_type) if i == item_type and (self.item_amount[i] > delete_amount or self.infinite_amount)]
            if len(item_type_ind) ==0:
                print("there is no-item error ", self.shelf_index, self.item_type)
                return False
            else :
                # 첫 번째 인덱스의 물건에서 해당 물건만큼뺍니다.
                if not self.infinite_amount:
                    self.item_amount[item_type_ind[0]] -= delete_amount
                # 만약에 물건이 바닥난다면, 공급리스트에 추가합니다.
                if self.item_amount[item_type_ind[0]] < self.supply_limit:
                    self.supply_list.append(item_type_ind[0])
                return True
        else:   #만약에 물건의 종류뿐만 아니라 선반의 위치까지 신경쓴다면?
            item_ind = 3*item_point[1] +item_point[0]
            if self.item_amount[item_ind] > delete_amount:
                if not self.infinite_amount:
                    self.item_amount[item_ind] -=delete_amount
                if self.item_amount[item_ind] <self.supply_limit:
                    self.supply_list.append(item_ind)
                return True
            else :
                print("there is no-item error ", self.shelf_index, self.item_type)
                return False

    def supply_item(self, item_type, item_point=None, supply_amount=1):  # 이 선반의 특정 위치의 item수를 줄입니다.
        if item_point is not None:
            item_ind = 3 * item_point[1] + item_point[0]
            self.item_amount[item_ind] += supply_amount
        else :
            for i in self.supply_list:
                if self.item_type[i] == item_type:#item 타입이 같은 선반이 있다면
                    self.item_amount[i] += supply_amount#해당 선반의 물건 개수를 늘립니다.

class Warehouse_Map:
    '''
    그림으로 표현할때, 어떻게 해야할까.격자로 나누고, 각각의 화물개수를 표현할 수 있게끔 2차원배열을 만들어서 연산을 시켜야하나
    내가 원하는 것 첫째는 세세하게 고르는 기능을 만들어서 넣기 두번째는 마우스 등으로 옮겨서 수정시키기(통로의 크기등을 정할 수 있음)
    '''
    def __init__(self, wh_width = 500, wh_height= 400, resolution=3):
        '''
        로봇의 상황과 관련되어서,

        :param shelf_list : 선반의 객체체
        :param pack_sps : 패킹스테이션의 위치들과 좌표
        :param picking_sps : 픽킹스테이션의 위치들과 좌표
        :param wh_width : 이미지의 width
        :param wh_height : 이미지의 height
        :param resolution : 이미지의 resolution
        '''
        self.wh_width = wh_width
        self.wh_height = wh_height
        self.resolution = resolution
    def change_map_size(self, wh_width, wh_height,resolution):
        self.wh_height = wh_height
        self.wh_width = wh_width
        self.resolution = resolution


class Widget_Warehouse(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("w_map_editer.ui",self)
        self.setWindowTitle("맵 생성도구")
        self.setFixedWidth(1618)
        self.setFixedHeight(856)
        self.map_height = 400
        self.map_width = 500
        self.map_resolution = 10
        self.map_resolution_2 = 10
        self.setupSignal()
        self.preview_map.hide()
        self.preview_shelf.hide()
        self.max_map_width = 1100
        self.max_map_height = 750
        self.max_map_resolution = 200
        self.max_map_resolution_2 = 200



        self.shelf_height =10
        self.shelf_width =20
        self.shelf_maxitem = 2
        self.isoneside = False
        self.init_map_x = self.groupBox_map.geometry().left() + self.preview_map.geometry().left()
        self.init_map_y = self.groupBox_map.geometry().top() + self.preview_map.geometry().top()
        self.init_shelf_x = self.groupBox_shelf.geometry().left() + self.preview_shelf.geometry().center().x()
        self.init_shelf_y = self.groupBox_shelf.geometry().top() + self.preview_shelf.geometry().center().y()
        self.mode = "Make Map"
        self.current_mouse_x = 0
        self.current_mouse_y =0
        self.current_rotation_angle =0
        self.saved_shelf_point = []
        self.occupy_map = [[0 for col in range(30)] for row in range(30)]
        self.current_upper_curser_ind =0
        self.current_clicked_curser_ind =0
        self.saved_block_point = []
        self.current_upper_curser_ind_block = 0
        self.current_clicked_curser_ind_block = 0
        self.click_target = False
        self.saved_sp_point = []
        self.saved_pk_point = []
        #map 크기 및 resolution 설정을 위한 모드를 위한 기본설정
        self.init_mode_1()

        #self.hide_warehouse_setting()
    def init_mode_1(self):
        # map 크기 및 resolution 설정을 위한 모드를 위한 기본설정
        button_h = self.groupBox_2.geometry().bottom()+1
        button_w = self.groupBox_2.geometry().center().x()+1-(self.pushMapsize.geometry().width()+1)/2
        self.pushMapsize.move(button_w, button_h)
        self.hide_shelfsetting()

    def hide_shelfsetting(self):
        # self.button_deleteblock.hide()
        self.groupBox_shelf.hide()
        self.preview_shelf.hide()
        self.flag_hide_preview = True

    def hide_warehouse_setting(self):
        self.groupBox.hide()
        self.groupBox_2.hide()

    def draw(self, qp):
        init_x = self.init_map_x
        init_y = self.init_map_y
        qp.setPen(QPen(QColor(189,189,189), 2))
        qp.drawRect(init_x, init_y, self.map_width, self.map_height)
        res_width = self.map_width/self.map_resolution
        res_heigth = self.map_height/self.map_resolution_2
        #맵의 격자를 그립니다.
        for i in range(self.map_resolution):
            res_x = int(init_x +(i+1)*res_width)
            qp.drawLine(res_x,init_y,res_x,init_y+self.map_height)

        for i in range(self.map_resolution_2):
            res_y = int(init_y +(i+1)*res_heigth)
            qp.drawLine(init_x,res_y,init_x+self.map_width,res_y)

        init_x = self.init_shelf_x
        init_y = self.init_shelf_y
        # 선반 미리보기
        if not self.flag_hide_preview :
            #선반을 표시할 영역을 그립니다.
            qp.drawRect(self.groupBox_shelf.geometry().left()+self.preview_shelf.geometry().left(),
                    self.groupBox_shelf.geometry().top()+self.preview_shelf.geometry().top(),
                    self.preview_shelf.geometry().width(),
                    self.preview_shelf.geometry().height())


            qp.setBrush(QColor(0,100,240))
            qp.setPen(QPen(QColor(0,100,240),2))
            # 선반을 그립니다.
            qp.drawRect(init_x-int(self.shelf_width/2),init_y-int(self.shelf_height/2),self.shelf_width,self.shelf_height)
            #선반이 oneside인지
            item_width = self.shelf_width/self.shelf_maxitem
            qp.setPen(QPen(QColor(189,189,189), 2))
            #선반위에 선을 그립니다.(각 아이템이 들어갈 칸입니다.
            for i in range(self.shelf_maxitem+1):
                start_x =init_x-int(self.shelf_width/2)+item_width*i
                qp.drawLine(start_x,init_y-int(self.shelf_height/2),start_x,init_y+int(self.shelf_height/2))

            #선반의 중심선을 그릴지 정합니다.(양면인지 단면인지)
            if not self.isoneside  :
                start_x = init_x - int(self.shelf_width / 2)
                qp.drawLine(start_x, init_y, start_x+int(self.shelf_width), init_y)

            else:
                start_x = init_x - int(self.shelf_width / 2)
                qp.drawLine(start_x, init_y+int(self.shelf_height/2), start_x + int(self.shelf_width), init_y+int(self.shelf_height/2))

        # qp.setPen(QPen(QColor(255, 0, 0), 3))

        #표시된 점들 그리기
        for ind, point in enumerate(self.saved_shelf_point):

            if point[2] == 0 or point[2] == 180:
                lefttop = [point[0] - int(point[3] / 2),
                           point[1] - int(point[4] / 2)]
                rightbottom = [point[0] + int(point[3]/ 2),
                               point[1] + int(point[4]/ 2)]
            else:
                lefttop = [point[0] - int(point[4] / 2),
                           point[1] - int(point[3] / 2)]
                rightbottom = [point[0] + int(point[4] / 2),
                               point[1] + int(point[3] / 2)]
            if ind+1 ==self.current_clicked_curser_ind:
                if self.mode =="edit Map":
                    qp.setBrush(QColor(243, 97, 220))
                    qp.setPen(QPen(QColor(189,189,189), 2))
            elif ind+1 ==self.current_upper_curser_ind:
                if self.mode =="edit Map":
                    qp.setBrush(QColor(100, 100, 0))
                    qp.setPen(QPen(QColor(189,189,189), 2))
            else:
                qp.setBrush(QColor(0, 100, 0))
                qp.setPen(QPen(QColor(189,189,189), 2))
            init_x = self.init_map_x
            init_y = self.init_map_y

            small_x_index = math.floor((lefttop[0] - init_x) / res_width)  # 맨왼쪽 포함
            big_x_index = math.ceil((rightbottom[0] - init_x) / res_width)
            small_y_index = math.floor((lefttop[1] - init_y) / res_heigth)
            big_y_index = math.ceil((rightbottom[1] - init_y) / res_heigth)
            for i in range(small_y_index, big_y_index):
                for j in range(small_x_index, big_x_index):
                    lefttop_x = init_x + res_width * j
                    lefttop_y = init_y + res_heigth * i
                    qp.drawRect(lefttop_x, lefttop_y, res_width, res_heigth)
        #벽그리기
        for ind, block_point in enumerate(self.saved_block_point):

            left = self.init_map_x
            right = self.init_map_x + self.map_width
            top = self.init_map_y
            bottom = self.init_map_y + self.map_height
            init_x = self.init_map_x
            init_y = self.init_map_y
            if -(ind + 1) == self.current_clicked_curser_ind_block:
                if self.mode == "edit block":
                    qp.setBrush(QColor(243, 97, 220))
                    qp.setPen(QPen(QColor(100, 0, 0), 3))
            elif -(ind + 1) == self.current_upper_curser_ind_block:
                if self.mode == "edit block":
                    qp.setBrush(QColor(100, 100, 0))
                    qp.setPen(QPen(QColor(100, 0, 0), 3))
            else:
                qp.setBrush(QColor(0, 0, 0))
                qp.setPen(QPen(QColor(189,189,189), 2))
            small_x_index = math.floor((block_point[0] - init_x) / res_width)  # 맨왼쪽 포함
            big_x_index = math.ceil((block_point[0] - init_x) / res_width)
            small_y_index = math.floor((block_point[1]- init_y) / res_heigth)
            big_y_index = math.ceil((block_point[1] - init_y) / res_heigth)
            small_x_index = init_x + res_width * small_x_index
            # big_x_index = init_x + res_width * big_x_index
            small_y_index = init_y + res_heigth * small_y_index
            # big_y_index = init_y + res_heigth * big_y_index
            qp.drawRect(small_x_index, small_y_index, res_width, res_heigth)

        # 시작지점그리기
        for ind, block_point in enumerate(self.saved_sp_point):
            left = self.init_map_x
            right = self.init_map_x + self.map_width
            top = self.init_map_y
            bottom = self.init_map_y + self.map_height
            init_x = self.init_map_x
            init_y = self.init_map_y
            if (ind + 1+10000) == self.current_clicked_curser_ind_block:
                if self.mode == "delete sp":
                    qp.setBrush(QColor(0, 255, 0))
                    qp.setPen(QPen(QColor(189,189,189), 3))
            elif (ind + 1+10000) == self.current_upper_curser_ind_block:
                if self.mode == "delete sp":
                    qp.setBrush(QColor(100, 100, 0))
                    qp.setPen(QPen(QColor(189,189,189), 2))
            else:
                qp.setBrush(QColor(255, 0, 127))
                qp.setPen(QPen(QColor(189,189,189), 2))
            small_x_index = math.floor((block_point[0] - init_x) / res_width)  # 맨왼쪽 포함
            big_x_index = math.ceil((block_point[0] - init_x) / res_width)
            small_y_index = math.floor((block_point[1] - init_y) / res_heigth)
            big_y_index = math.ceil((block_point[1] - init_y) / res_heigth)
            small_x_index = init_x + res_width * small_x_index
            big_x_index = init_x + res_width * big_x_index
            small_y_index = init_y + res_heigth * small_y_index
            big_y_index = init_y + res_heigth * big_y_index
            qp.drawRect(small_x_index, small_y_index, res_width, res_heigth)

        # 패킹지점그리기
        for ind, block_point in enumerate(self.saved_pk_point):
            left = self.init_map_x
            right = self.init_map_x + self.map_width
            top = self.init_map_y
            bottom = self.init_map_y + self.map_height
            init_x = self.init_map_x
            init_y = self.init_map_y
            if (ind + 1+20000) == self.current_clicked_curser_ind_block:
                if self.mode == "delete pk":
                    qp.setBrush(QColor(0, 255, 0))
                    qp.setPen(QPen(QColor(0, 255, 0), 3))
            elif (ind + 1+20000) == self.current_upper_curser_ind_block:
                if self.mode == "delete pk":
                    qp.setBrush(QColor(100, 100, 0))
                    qp.setPen(QPen(QColor(0, 100, 0), 2))
            else:
                qp.setBrush(QColor(0, 0, 255))
                qp.setPen(QPen(QColor(0, 0, 255), 2))
            small_x_index = math.floor((block_point[0] - init_x) / res_width)  # 맨왼쪽 포함
            big_x_index = math.ceil((block_point[0] - init_x) / res_width)
            small_y_index = math.floor((block_point[1] - init_y) / res_heigth)
            big_y_index = math.ceil((block_point[1] - init_y) / res_heigth)
            small_x_index = init_x + res_width * small_x_index
            big_x_index = init_x + res_width * big_x_index
            small_y_index = init_y + res_heigth * small_y_index
            big_y_index = init_y + res_heigth * big_y_index
            qp.drawRect(small_x_index, small_y_index, res_width, res_heigth)


        # 패킹지점 미리보기
        if self.mode == "make pk":
            left = self.init_map_x
            right = self.init_map_x + self.map_width
            top = self.init_map_y
            bottom = self.init_map_y + self.map_height

            if (self.current_mouse_x <= right and self.current_mouse_x >= left) and (
                    self.current_mouse_y <= bottom and self.current_mouse_y >= top):
                init_x = self.init_map_x
                init_y = self.init_map_y
                qp.setBrush(QColor(0, 0, 255))
                qp.setPen(QPen(QColor(0, 0, 255), 2))
                small_x_index = math.floor((self.current_mouse_x - init_x) / res_width)  # 맨왼쪽 포함
                big_x_index = math.ceil((self.current_mouse_x - init_x) / res_width)
                small_y_index = math.floor((self.current_mouse_y - init_y) / res_heigth)
                big_y_index = math.ceil((self.current_mouse_y - init_y) / res_heigth)
                small_x_index = init_x + res_width * small_x_index
                big_x_index = init_x + res_width * big_x_index
                small_y_index = init_y + res_heigth * small_y_index
                big_y_index = init_y + res_heigth * big_y_index
                qp.drawRect(small_x_index,small_y_index,res_width,res_heigth)

        #시작지점 미리보기기
        if self.mode == "make sp":
            left = self.init_map_x
            right = self.init_map_x + self.map_width
            top = self.init_map_y
            bottom = self.init_map_y + self.map_height

            if (self.current_mouse_x <= right and self.current_mouse_x >= left) and (
                    self.current_mouse_y <= bottom and self.current_mouse_y >= top):
                init_x = self.init_map_x
                init_y = self.init_map_y
                qp.setBrush(QColor(255, 0, 127))
                qp.setPen(QPen(QColor(255, 0, 127), 2))
                small_x_index = math.floor((self.current_mouse_x - init_x) / res_width)  # 맨왼쪽 포함
                big_x_index = math.ceil((self.current_mouse_x - init_x) / res_width)
                small_y_index = math.floor((self.current_mouse_y - init_y) / res_heigth)
                big_y_index = math.ceil((self.current_mouse_y - init_y) / res_heigth)
                small_x_index = init_x + res_width * small_x_index
                big_x_index = init_x + res_width * big_x_index
                small_y_index = init_y + res_heigth * small_y_index
                big_y_index = init_y + res_heigth * big_y_index
                qp.drawRect(small_x_index,small_y_index,res_width,res_heigth)

        #벽미리보기
        if self.mode =="set block":
            left = self.init_map_x
            right = self.init_map_x + self.map_width
            top = self.init_map_y
            bottom = self.init_map_y + self.map_height
            # lefttop = [self.current_mouse_x - int(self.shelf_width / 2),
            #            self.current_mouse_y - int(self.shelf_height / 2)]
            # rightbottom = [self.current_mouse_x + int(self.shelf_width / 2),
            #                self.current_mouse_y + int(self.shelf_height / 2)]

            if (self.current_mouse_x<= right and self.current_mouse_x >= left) and (self.current_mouse_y <= bottom and self.current_mouse_y >= top):

                init_x = self.init_map_x
                init_y = self.init_map_y
                qp.setBrush(QColor(100, 0, 0))
                qp.setPen(QPen(QColor(0, 0, 0), 2))
                small_x_index = math.floor((self.current_mouse_x - init_x) / res_width)  # 맨왼쪽 포함
                # big_x_index = math.ceil((self.current_mouse_x - init_x) / res_width)
                small_y_index = math.floor((self.current_mouse_y - init_y) / res_heigth)
                # big_y_index = math.ceil((self.current_mouse_y - init_y) / res_heigth)
                small_x_index = init_x + res_width*small_x_index
                # big_x_index = init_x + res_width * big_x_index
                small_y_index = init_y + res_heigth * small_y_index
                # big_y_index = init_y + res_heigth * big_y_index
                qp.drawRect(small_x_index,small_y_index,res_width,res_heigth)

        #선반미리보기
        if self.mode == "Set Shelf":
            left = self.init_map_x
            right = self.init_map_x+self.map_width
            top = self.init_map_y
            bottom = self.init_map_y+self.map_height
            lefttop = [0, 0]
            rightbottom = [0, 0]
            # 가능영역 표시하기
            if self.current_rotation_angle == 0 or self.current_rotation_angle == 180:
                lefttop = [self.current_mouse_x - int(self.shelf_width / 2),
                           self.current_mouse_y - int(self.shelf_height / 2)]
                rightbottom = [self.current_mouse_x + int(self.shelf_width / 2),
                               self.current_mouse_y + int(self.shelf_height / 2)]
            else:
                lefttop = [self.current_mouse_x - int(self.shelf_height / 2),
                           self.current_mouse_y - int(self.shelf_width / 2)]
                rightbottom = [self.current_mouse_x + int(self.shelf_height / 2),
                               self.current_mouse_y + int(self.shelf_width / 2)]
            if (rightbottom[0]<= right and lefttop[0] >= left) and (rightbottom[1] <= bottom and lefttop[1] >= top):

                init_x = self.init_map_x
                init_y = self.init_map_y
                qp.setBrush(QColor(100, 0, 0))
                qp.setPen(QPen(QColor(0, 0, 0), 2))
                small_x_index = math.floor((lefttop[0] - init_x) / res_width)  # 맨왼쪽 포함
                big_x_index = math.ceil((rightbottom[0] - init_x) / res_width)
                small_y_index = math.floor((lefttop[1] - init_y) / res_heigth)
                big_y_index = math.ceil((rightbottom[1] - init_y) / res_heigth)
                for i in range(small_y_index, big_y_index):
                    for j in range(small_x_index, big_x_index):
                        lefttop_x = init_x + res_width * j
                        lefttop_y = init_y + res_heigth * i
                        qp.drawRect(lefttop_x, lefttop_y, res_width, res_heigth)


                init_x =0
                init_y = 0
                qp.translate(self.current_mouse_x,self.current_mouse_y)
                qp.rotate(self.current_rotation_angle)
                item_width = self.shelf_width / self.shelf_maxitem
                # 선반 미리보기
                qp.setBrush(QColor(0, 100, 240))
                qp.setPen(QPen(QColor(0, 100, 240), 2))
                qp.drawRect(init_x - int(self.shelf_width / 2), init_y - int(self.shelf_height / 2), self.shelf_width,
                            self.shelf_height)
                qp.setPen(QPen(QColor(0, 0, 0), 2))
                for i in range(self.shelf_maxitem + 1):
                    start_x = init_x - int(self.shelf_width / 2) + item_width * i
                    qp.drawLine(start_x, init_y - int(self.shelf_height / 2), start_x, init_y + int(self.shelf_height / 2))

                if not self.isoneside:
                    start_x = init_x - int(self.shelf_width / 2)
                    qp.drawLine(start_x, init_y, start_x + int(self.shelf_width), init_y)

                else:
                    start_x = init_x - int(self.shelf_width / 2)
                    qp.drawLine(start_x, init_y + int(self.shelf_height / 2), start_x + int(self.shelf_width),
                                init_y + int(self.shelf_height / 2))

                qp.rotate(-self.current_rotation_angle)
                qp.translate(-self.current_mouse_x, -self.current_mouse_y)
                qp.drawPoint(self.current_mouse_x, self.current_mouse_y)
                #이제 resolution을 고려하여 차지하는 영역을 표시 해야한다. 뭐 빨간색이라든가
                #사각형의 네가지 꼭지점의 위치를 고려해서 현재 resolution에따라서 다르게 표시하게 해도 될거같다. 4번정도만 해당 resolution에 포함되는지만 확인하자
                #각 모서리 좌표

    def setupSignal(self):
        self.slider_wSize.valueChanged.connect(self.change_width_size)
        self.slider_hSize.valueChanged.connect(self.change_height_size)
        self.slider_resolution.valueChanged.connect(self.change_resolution)
        self.slider_resolution_2.valueChanged.connect(self.change_resolution_2)
        self.edit_wSize.returnPressed.connect(self.change_width_edit_size)
        self.edit_hSize.returnPressed.connect(self.change_height_edit_size)
        self.edit_resolution.returnPressed.connect(self.change_resolution_edit)
        self.edit_resolution_2.returnPressed.connect(self.change_resolution_edit_2)
        self.edit_shelfheight.returnPressed.connect(self.change_shelf_height)
        self.edit_shelfwidth.returnPressed.connect(self.change_shelf_width)
        self.edit_shelfmaxitem.returnPressed.connect(self.change_shelf_item)
        self.check_oneside.stateChanged.connect(self.change_oneside_checkbox)
        self.button_makeshelf.clicked.connect(self.make_shelf)
        self.button_resetshelf.clicked.connect(self.reset_shelf)
        self.setMouseTracking(True)
        self.groupBox_map.setMouseTracking(True)
        self.button_shelfeditor.clicked.connect(self.edit_shelf)
        self.button_makeblock.clicked.connect(self.make_block)
        self.button_deleteblock.clicked.connect(self.edit_block)
        self.pushMapsize.clicked.connect(self.saveResNSize)
        self.button_savemap.clicked.connect(self.saveMapInfo)
        self.button_loadmap.clicked.connect(self.loadMapInfo)
        self.button_makeSP.clicked.connect(self.make_sp)
        self.button_deleteSP.clicked.connect(self.delete_sp)
        self.button_makePK.clicked.connect(self.make_pk)
        self.button_deletePK.clicked.connect(self.delete_pk)
        self.button_close.clicked.connect(self.close_window)

    def close_window(self):
        self.close()


    def delete_pk(self):
        self.mode = "delete pk"
        self.edit_shelfheight.setDisabled(True)
        self.edit_shelfwidth.setDisabled(True)
        self.edit_shelfmaxitem.setDisabled(True)
        self.check_oneside.setDisabled(True)

        self.button_makeshelf.setDisabled(True)  # 선반만드는 버튼을 비활성화 합니다.
        self.button_shelfeditor.setDisabled(True)  # 선반수정하는 버튼을 비활성화합니다.

        # 벽생성버튼을 비활성화합니다.
        self.button_makeblock.setDisabled(True)
        self.button_deleteblock.setDisabled(True)

        # 패킹지점관련 버튼을 비활성화합니다.
        self.button_makePK.setDisabled(True)  # 선반만드는 버튼을 비활성화 합니다.
        self.button_deletePK.setDisabled(True)  # 선반수정하는 버튼을 비활성화합니다.

        # 시작지점관련 버튼을 비활성화합니다.
        self.button_makeSP.setDisabled(True)  # 선반만드는 버튼을 비활성화 합니다.
        self.button_deleteSP.setDisabled(True)  # 선반수정하는 버튼을 비활성화합니다.

    def make_pk(self):
        self.mode = "make pk"
        self.edit_shelfheight.setDisabled(True)
        self.edit_shelfwidth.setDisabled(True)
        self.edit_shelfmaxitem.setDisabled(True)
        self.check_oneside.setDisabled(True)

        self.button_makeshelf.setDisabled(True)  # 선반만드는 버튼을 비활성화 합니다.
        self.button_shelfeditor.setDisabled(True)  # 선반수정하는 버튼을 비활성화합니다.

        # 벽생성버튼을 비활성화합니다.
        self.button_makeblock.setDisabled(True)
        self.button_deleteblock.setDisabled(True)

        # 패킹지점관련 버튼을 비활성화합니다.
        self.button_makePK.setDisabled(True)  # 선반만드는 버튼을 비활성화 합니다.
        #self.button_deletePK.setDisabled(True)  # 선반수정하는 버튼을 비활성화합니다.

        # 시작지점관련 버튼을 비활성화합니다.
        self.button_makeSP.setDisabled(True)  # 선반만드는 버튼을 비활성화 합니다.
        self.button_deleteSP.setDisabled(True)  # 선반수정하는 버튼을 비활성화합니다.

    def delete_sp(self):
        self.mode = "delete sp"
        self.edit_shelfheight.setDisabled(True)
        self.edit_shelfwidth.setDisabled(True)
        self.edit_shelfmaxitem.setDisabled(True)
        self.check_oneside.setDisabled(True)

        self.button_makeshelf.setDisabled(True)  # 선반만드는 버튼을 비활성화 합니다.
        self.button_shelfeditor.setDisabled(True)  # 선반수정하는 버튼을 비활성화합니다.

        # 벽생성버튼을 비활성화합니다.
        self.button_makeblock.setDisabled(True)
        self.button_deleteblock.setDisabled(True)

        # 패킹지점관련 버튼을 비활성화합니다.
        self.button_makePK.setDisabled(True)  # 선반만드는 버튼을 비활성화 합니다.
        self.button_deletePK.setDisabled(True)  # 선반수정하는 버튼을 비활성화합니다.

        # 시작지점관련 버튼을 비활성화합니다.
        self.button_makeSP.setDisabled(True)  # 선반만드는 버튼을 비활성화 합니다.
        self.button_deleteSP.setDisabled(True)  # 선반수정하는 버튼을 비활성화합니다.

    def make_sp(self):
        self.mode = "make sp"
        self.edit_shelfheight.setDisabled(True)
        self.edit_shelfwidth.setDisabled(True)
        self.edit_shelfmaxitem.setDisabled(True)
        self.check_oneside.setDisabled(True)

        self.button_makeshelf.setDisabled(True)  # 선반만드는 버튼을 비활성화 합니다.
        self.button_shelfeditor.setDisabled(True)  # 선반수정하는 버튼을 비활성화합니다.

        # 벽생성버튼을 비활성화합니다.
        self.button_makeblock.setDisabled(True)
        self.button_deleteblock.setDisabled(True)

        # 패킹지점관련 버튼을 비활성화합니다.
        self.button_makePK.setDisabled(True)  # 선반만드는 버튼을 비활성화 합니다.
        self.button_deletePK.setDisabled(True)  # 선반수정하는 버튼을 비활성화합니다.

        # 시작지점관련 버튼을 비활성화합니다.
        self.button_makeSP.setDisabled(True)  # 선반만드는 버튼을 비활성화 합니다.
        #self.button_deleteSP.setDisabled(True)  # 선반수정하는 버튼을 비활성화합니다.

    def saveMapInfo(self):
        FileSave = QFileDialog.getSaveFileName(self,'맵 저장하기','./Map/',"Map File (*.json)")[0]
        if FileSave == "":
            pass

        else:
            with open(FileSave,'w') as fp:
                data = {}
                data['map_size'] = (self.map_width, self.map_height)
                data['map_resolution'] = (self.map_resolution,self.map_resolution_2)
                data['occupay_map'] = self.occupy_map
                data['shelf_point'] = self.saved_shelf_point #x좌표,y좌표, 선반 회전각[degree], 선반 너비, 선반 높이, 한 면의 아이템수, 단면여부
                data['block_point'] = self.saved_block_point #x좌표,y좌표,
                data['pack_point'] = self.saved_pk_point  # x좌표,y좌표,
                data['start_point'] = self.saved_sp_point  # x좌표,y좌표,

                json.dump(data,fp)

    def loadMapInfo(self):
        FileSave = QFileDialog.getOpenFileName(self,'맵 불러오기','./Map/',"Map File (*.json)")[0]
        if FileSave == "":
            pass

        else:
            with open(FileSave,'r') as fp:
                data = json.load(fp)
                self.map_width = data['map_size'][0]
                self.map_height = data['map_size'][1]
                self.map_resolution = data['map_resolution'][0]
                self.map_resolution_2 = data['map_resolution'][1]
                self.occupy_map = data['occupay_map']
                self.saved_shelf_point = data['shelf_point']
                self.saved_block_point = data['block_point']
                self.saved_pk_point = data['pack_point']
                self.saved_sp_point = data['start_point']


            #ui를 위에서 얻은 정보로 바꿉니다.
            self.update()
            self.edit_wSize.setText(str(self.map_width))
            self.edit_hSize.setText(str(self.map_height))


            self.slider_wSize.setValue(self.map_width)
            self.slider_hSize.setValue(self.map_height)

            self.edit_resolution.setText(str(self.map_resolution))
            self.edit_resolution_2.setText(str(self.map_resolution_2))
            self.slider_resolution.setValue(self.map_resolution)
            self.slider_resolution_2.setValue(self.map_resolution_2)
            self.hide_warehouse_setting()

            self.flag_hide_preview = False
            self.pushMapsize.hide()
            want_height = self.groupBox_map.geometry().top()
            want_width = self.groupBox_shelf.geometry().left()
            self.groupBox_shelf.move(want_width, want_height)
            self.groupBox_shelf.show()
            self.init_shelf_x = self.groupBox_shelf.geometry().left() + self.preview_shelf.geometry().center().x()
            self.init_shelf_y = self.groupBox_shelf.geometry().top() + self.preview_shelf.geometry().center().y()
            self.update()

    def mouseMoveEvent(self, e):
        self.current_mouse_x = e.x()
        self.current_mouse_y = e.y()
        if self.mode =="edit Map":

            left = self.init_map_x
            right = self.init_map_x + self.map_width
            top = self.init_map_y
            bottom = self.init_map_y + self.map_height
            lefttop = [0, 0]
            rightbottom = [0, 0]
            # 가능영역 표시하기
            if self.current_rotation_angle == 0 or self.current_rotation_angle == 180:
                lefttop = [self.current_mouse_x - int(self.shelf_width / 2),
                           self.current_mouse_y - int(self.shelf_height / 2)]
                rightbottom = [self.current_mouse_x + int(self.shelf_width / 2),
                               self.current_mouse_y + int(self.shelf_height / 2)]
            else:
                lefttop = [self.current_mouse_x - int(self.shelf_height / 2),
                           self.current_mouse_y - int(self.shelf_width / 2)]
                rightbottom = [self.current_mouse_x + int(self.shelf_height / 2),
                               self.current_mouse_y + int(self.shelf_width / 2)]
            if (rightbottom[0] <= right and lefttop[0] >= left) and (rightbottom[1] <= bottom and lefttop[1] >= top):

                self.setCursor(QCursor(Qt.PointingHandCursor))
                if (rightbottom[0] <= right and lefttop[0] >= left) and (
                        rightbottom[1] <= bottom and lefttop[1] >= top):
                    init_x = self.init_map_x
                    init_y = self.init_map_y
                    res_width = self.map_width / self.map_resolution
                    res_heigth = self.map_height / self.map_resolution_2
                    small_x_index = math.floor((lefttop[0] - init_x) / res_width)  # 맨왼쪽 포함
                    big_x_index = math.ceil((rightbottom[0] - init_x) / res_width)
                    small_y_index = math.floor((lefttop[1] - init_y) / res_heigth)
                    big_y_index = math.ceil((rightbottom[1] - init_y) / res_heigth)
                    is_not = True

                    for i in range(small_y_index, big_y_index):
                        for j in range(small_x_index, big_x_index):
                            if self.occupy_map[i][j] > 0 :
                                is_not = False

                                self.current_upper_curser_ind = self.occupy_map[i][j]
                    if is_not:
                        self.current_upper_curser_ind =0

            else:
                self.setCursor(QCursor(Qt.ArrowCursor))

        if (self.mode =="edit block" or self.mode == "delete pk") or self.mode == "delete sp":
            left = self.init_map_x
            right = self.init_map_x + self.map_width
            top = self.init_map_y
            bottom = self.init_map_y + self.map_height
            # 가능영역 표시하기
            if (self.current_mouse_x <= right and self.current_mouse_x >= left) and (self.current_mouse_y <= bottom and self.current_mouse_y >= top):
                self.setCursor(QCursor(Qt.PointingHandCursor))
                init_x = self.init_map_x
                init_y = self.init_map_y
                res_width = self.map_width / self.map_resolution
                res_heigth = self.map_height / self.map_resolution_2

                small_x_index = math.floor((self.current_mouse_x - init_x) / res_width)  # 맨왼쪽 포함
                big_x_index = math.ceil((self.current_mouse_x - init_x) / res_width)
                small_y_index = math.floor((self.current_mouse_y - init_y) / res_heigth)
                big_y_index = math.ceil((self.current_mouse_y - init_y) / res_heigth)
                is_not = True
                for i in range(small_y_index, big_y_index):
                    for j in range(small_x_index, big_x_index):
                        if self.mode =="edit block" :
                            if self.occupy_map[i][j] < 0:
                                is_not = False
                                self.current_upper_curser_ind_block = self.occupy_map[i][j]
                        elif self.mode =="delete pk":
                            if self.occupy_map[i][j] >20000:
                                is_not = False
                                self.current_upper_curser_ind_block = self.occupy_map[i][j]
                        elif self.mode =="delete sp":
                            if self.occupy_map[i][j] >10000:
                                is_not = False
                                self.current_upper_curser_ind_block = self.occupy_map[i][j]


                if is_not:
                    self.current_upper_curser_ind_block =0

            else:
                self.setCursor(QCursor(Qt.ArrowCursor))



        self.update()

    def mousePressEvent(self, e):
        if self.mode == "Set Shelf":
            self.current_mouse_x = e.x()
            self.current_mouse_y = e.y()
            print(self.current_mouse_y,self.current_mouse_x)
            left = self.init_map_x
            right = self.init_map_x + self.map_width
            top = self.init_map_y
            bottom = self.init_map_y + self.map_height
            lefttop = [0, 0]
            rightbottom = [0, 0]
            # 가능영역 표시하기
            if self.current_rotation_angle == 0 or self.current_rotation_angle == 180:
                lefttop = [self.current_mouse_x - int(self.shelf_width / 2),
                           self.current_mouse_y - int(self.shelf_height / 2)]
                rightbottom = [self.current_mouse_x + int(self.shelf_width / 2),
                               self.current_mouse_y + int(self.shelf_height / 2)]
            else:
                lefttop = [self.current_mouse_x - int(self.shelf_height / 2),
                           self.current_mouse_y - int(self.shelf_width / 2)]
                rightbottom = [self.current_mouse_x + int(self.shelf_height / 2),
                               self.current_mouse_y + int(self.shelf_width / 2)]
            if (rightbottom[0] <= right and lefttop[0] >= left) and (rightbottom[1] <= bottom and lefttop[1] >= top):
                init_x = self.init_map_x
                init_y = self.init_map_y
                res_width = self.map_width / self.map_resolution
                res_heigth = self.map_height / self.map_resolution_2
                small_x_index = math.floor((lefttop[0] - init_x) / res_width)  # 맨왼쪽 포함
                big_x_index = math.ceil((rightbottom[0] - init_x) / res_width)
                small_y_index = math.floor((lefttop[1] - init_y) / res_heigth)
                big_y_index = math.ceil((rightbottom[1] - init_y) / res_heigth)
                flag_false = False
                for i in range(small_y_index, big_y_index):
                    for j in range(small_x_index, big_x_index):
                        if self.occupy_map[i][j] !=0 :
                            flag_false =True
                if flag_false :
                    msgBox = QMessageBox()
                    msgBox.setWindowTitle("경고")
                    msgBox.setText("해당점은 이미 차지하고 있습니다.")
                    msgBox.exec_()
                else :
                    self.saved_shelf_point.append([self.current_mouse_x,self.current_mouse_y,self.current_rotation_angle,self.shelf_width,self.shelf_height,self.shelf_maxitem,self.isoneside])
                    self.occupancy_change()


        elif self.mode == "edit Map":
            self.current_clicked_curser_ind = self.current_upper_curser_ind
            self.click_target = True

        elif self.mode == "set block":
            left = self.init_map_x
            right = self.init_map_x + self.map_width
            top = self.init_map_y
            bottom = self.init_map_y + self.map_height
            if (self.current_mouse_x <= right and self.current_mouse_x >= left) and (
                    self.current_mouse_y <= bottom and self.current_mouse_y >= top):
                init_x = self.init_map_x
                init_y = self.init_map_y
                res_width = self.map_width / self.map_resolution
                res_heigth = self.map_height / self.map_resolution_2
                small_x_index = math.floor((self.current_mouse_x - init_x) / res_width)  # 맨왼쪽 포함
                big_x_index = math.ceil((self.current_mouse_x - init_x) / res_width)
                small_y_index = math.floor((self.current_mouse_y - init_y) / res_heigth)
                big_y_index = math.ceil((self.current_mouse_y - init_y) / res_heigth)

                flag_false = False
                if small_x_index == big_x_index or small_y_index == big_y_index:
                    msgBox = QMessageBox()
                    msgBox.setWindowTitle("경고")
                    msgBox.setText("resolution에 맞는점을 찍어주세요")
                    msgBox.exec_()
                else:
                    for i in range(small_y_index, big_y_index):
                        for j in range(small_x_index, big_x_index):
                            if self.occupy_map[i][j] != 0:
                                flag_false = True
                    if flag_false :
                        msgBox = QMessageBox()
                        msgBox.setWindowTitle("경고")
                        msgBox.setText("해당점은 이미 차지하고 있습니다.")
                        msgBox.exec_()
                    else :
                        self.saved_block_point.append([self.current_mouse_x,self.current_mouse_y])
                        self.occupancy_change()

        elif (self.mode =="edit block" or self.mode == "delete pk")or self.mode == "delete sp":
            self.current_clicked_curser_ind_block = self.current_upper_curser_ind_block
            self.click_target = True

        elif self.mode == "make pk":

            left = self.init_map_x
            right = self.init_map_x + self.map_width
            top = self.init_map_y
            bottom = self.init_map_y + self.map_height
            if (self.current_mouse_x <= right and self.current_mouse_x >= left) and (
                    self.current_mouse_y <= bottom and self.current_mouse_y >= top):
                init_x = self.init_map_x
                init_y = self.init_map_y
                res_width = self.map_width / self.map_resolution
                res_heigth = self.map_height / self.map_resolution_2
                small_x_index = math.floor((self.current_mouse_x - init_x) / res_width)  # 맨왼쪽 포함
                big_x_index = math.ceil((self.current_mouse_x - init_x) / res_width)
                small_y_index = math.floor((self.current_mouse_y - init_y) / res_heigth)
                big_y_index = math.ceil((self.current_mouse_y - init_y) / res_heigth)

                flag_false = False
                if small_x_index == big_x_index or small_y_index == big_y_index:
                    msgBox = QMessageBox()
                    msgBox.setWindowTitle("경고")
                    msgBox.setText("resolution에 맞는점을 찍어주세요")
                    msgBox.exec_()
                else:
                    for i in range(small_y_index, big_y_index):
                        for j in range(small_x_index, big_x_index):
                            if self.occupy_map[i][j] != 0:
                                flag_false = True
                    if flag_false :
                        msgBox = QMessageBox()
                        msgBox.setWindowTitle("경고")
                        msgBox.setText("해당점은 이미 차지하고 있습니다.")
                        msgBox.exec_()
                    else :
                        self.saved_pk_point.append([self.current_mouse_x,self.current_mouse_y])
                        self.occupancy_change()

        elif self.mode == "make sp":
            left = self.init_map_x
            right = self.init_map_x + self.map_width
            top = self.init_map_y
            bottom = self.init_map_y + self.map_height
            if (self.current_mouse_x <= right and self.current_mouse_x >= left) and (
                    self.current_mouse_y <= bottom and self.current_mouse_y >= top):
                init_x = self.init_map_x
                init_y = self.init_map_y
                res_width = self.map_width / self.map_resolution
                res_heigth = self.map_height / self.map_resolution_2
                small_x_index = math.floor((self.current_mouse_x - init_x) / res_width)  # 맨왼쪽 포함
                big_x_index = math.ceil((self.current_mouse_x - init_x) / res_width)
                small_y_index = math.floor((self.current_mouse_y - init_y) / res_heigth)
                big_y_index = math.ceil((self.current_mouse_y - init_y) / res_heigth)

                flag_false = False
                if small_x_index == big_x_index or small_y_index == big_y_index:
                    msgBox = QMessageBox()
                    msgBox.setWindowTitle("경고")
                    msgBox.setText("resolution에 맞는점을 찍어주세요")
                    msgBox.exec_()
                else:
                    for i in range(small_y_index, big_y_index):
                        for j in range(small_x_index, big_x_index):
                            if self.occupy_map[i][j] != 0:
                                flag_false = True
                    if flag_false :
                        msgBox = QMessageBox()
                        msgBox.setWindowTitle("경고")
                        msgBox.setText("해당점은 이미 차지하고 있습니다.")
                        msgBox.exec_()
                    else :
                        self.saved_sp_point.append([self.current_mouse_x,self.current_mouse_y])
                        self.occupancy_change()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        self.draw(qp)
        qp.end()

    def saveResNSize(self):
        msgBox = QMessageBox()
        msgBox.setWindowTitle("경고")
        msgBox.setText("한번 분해능과 맵크기를 정하면 못바꿉니다. \n 이 설정을 사용하시겠습니까?")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        retval = msgBox.exec_()
        if retval == QMessageBox.Yes:
            self.hide_warehouse_setting()

            self.flag_hide_preview = False
            self.pushMapsize.hide()
            want_height =  self.groupBox_map.geometry().top()
            want_width = self.groupBox_shelf.geometry().left()
            self.groupBox_shelf.move(want_width,want_height)
            self.groupBox_shelf.show()
            self.init_shelf_x = self.groupBox_shelf.geometry().left() + self.preview_shelf.geometry().center().x()
            self.init_shelf_y = self.groupBox_shelf.geometry().top() + self.preview_shelf.geometry().center().y()
            self.update()

    def keyReleaseEvent(self, e):
        if self.mode == "Set Shelf":
            if e.key() == Qt.Key_R:
                if self.current_rotation_angle != 270:
                    self.current_rotation_angle += 90
                else :
                    self.current_rotation_angle = 0

            self.update()
        if self.mode == "edit Map":
            if e.key() == Qt.Key_Delete:
                if self.current_clicked_curser_ind> 0 and self.current_clicked_curser_ind< 10000:
                    if len(self.saved_shelf_point) >0 and self.click_target:
                        del self.saved_shelf_point[self.current_clicked_curser_ind-1]
                        self.current_clicked_curser_ind = 0
                        self.current_upper_curser_ind = 0
                        self.click_target = False
                        self.occupancy_change()
                        self.update()

        if self.mode == "edit block":
            if e.key() == Qt.Key_Delete:
                if self.current_clicked_curser_ind_block < 0 :
                    if len(self.saved_block_point) >0 and self.click_target:
                        #print(self.current_clicked_curser_ind_block)
                        del self.saved_block_point[-self.current_clicked_curser_ind_block-1]
                        self.current_clicked_curser_ind_block = 0
                        self.click_target = False
                        self.occupancy_change()
                        self.update()
        #(self.mode =="edit block" or self.mode == "edit pk")or self.mode == "edit sp":

        if self.mode == "delete pk":
            if e.key() == Qt.Key_Delete:
                if len(self.saved_pk_point) >0 and self.click_target:
                    if self.current_clicked_curser_ind_block > 20000 :
                        del self.saved_pk_point[self.current_clicked_curser_ind_block-20001]
                        self.current_clicked_curser_ind_block = 0
                        self.click_target = False
                        self.occupancy_change()
                        self.update()

        if self.mode == "delete sp":
            if e.key() == Qt.Key_Delete:
                if len(self.saved_sp_point) >0 and self.click_target:
                    if self.current_clicked_curser_ind_block > 10000 and self.current_clicked_curser_ind_block < 20000:
                        del self.saved_sp_point[self.current_clicked_curser_ind_block-10001]
                        self.current_clicked_curser_ind_block = 0
                        self.click_target = False
                        self.occupancy_change()
                        self.update()

    def change_oneside_checkbox(self):
        if self.check_oneside.isChecked():
            self.isoneside = True
        else:
            self.isoneside = False

        self.update()

    def edit_shelf(self):
        self.mode = "edit Map"
        self.current_upper_curser_ind = 0
        self.current_clicked_curser_ind = 0

        self.button_makeshelf.setDisabled(True)  # 선반만드는 버튼을 비활성화 합니다.
        self.button_shelfeditor.setDisabled(True)  # 선반수정하는 버튼을 비활성화합니다.

        # 패킹지점관련 버튼을 비활성화합니다.
        self.button_makePK.setDisabled(True)  # 선반만드는 버튼을 비활성화 합니다.
        self.button_deletePK.setDisabled(True)  # 선반수정하는 버튼을 비활성화합니다.
        # 시작지점관련 버튼을 비활성화합니다.
        self.button_makeSP.setDisabled(True)  # 선반만드는 버튼을 비활성화 합니다.
        self.button_deleteSP.setDisabled(True)  # 선반수정하는 버튼을 비활성화합니다.

    def make_block(self):
        self.edit_shelfheight.setDisabled(True)
        self.edit_shelfwidth.setDisabled(True)
        self.edit_shelfmaxitem.setDisabled(True)
        self.check_oneside.setDisabled(True)

        self.button_makeshelf.setDisabled(True)#선반만드는 버튼을 비활성화 합니다.
        self.button_shelfeditor.setDisabled(True)#선반수정하는 버튼을 비활성화합니다.

        #벽생성버튼을 비활성화합니다.
        self.button_makeblock.setDisabled(True)

        #패킹지점관련 버튼을 비활성화합니다.
        self.button_makePK.setDisabled(True)  # 선반만드는 버튼을 비활성화 합니다.
        self.button_deletePK.setDisabled(True)  # 선반수정하는 버튼을 비활성화합니다.
        #시작지점관련 버튼을 비활성화합니다.
        self.button_makeSP.setDisabled(True)  # 선반만드는 버튼을 비활성화 합니다.
        self.button_deleteSP.setDisabled(True)  # 선반수정하는 버튼을 비활성화합니다.
        self.mode = "set block"

    def edit_block(self):
        self.edit_shelfheight.setDisabled(True)
        self.edit_shelfwidth.setDisabled(True)
        self.edit_shelfmaxitem.setDisabled(True)
        self.check_oneside.setDisabled(True)

        self.button_makeblock.setDisabled(True)
        self.button_deleteblock.setDisabled(True)

        self.button_makeshelf.setDisabled(True)#선반만드는 버튼을 비활성화 합니다.
        self.button_shelfeditor.setDisabled(True)#선반수정하는 버튼을 비활성화합니다.
        self.mode = "edit block"

        # 패킹지점관련 버튼을 비활성화합니다.
        self.button_makePK.setDisabled(True)
        self.button_deletePK.setDisabled(True)
        # 시작지점관련 버튼을 비활성화합니다.
        self.button_makeSP.setDisabled(True)
        self.button_deleteSP.setDisabled(True)

    def make_shelf(self):
        self.edit_shelfheight.setDisabled(True)
        self.edit_shelfwidth.setDisabled(True)
        self.edit_shelfmaxitem.setDisabled(True)
        self.check_oneside.setDisabled(True)

        self.button_makeshelf.setDisabled(True)
        self.button_makeblock.setDisabled(True)
        self.button_deleteblock.setDisabled(True)
        self.mode = "Set Shelf"
        self.current_rotation_angle = 0

        # 패킹지점관련 버튼을 비활성화합니다.
        self.button_makePK.setDisabled(True)  # 선반만드는 버튼을 비활성화 합니다.
        self.button_deletePK.setDisabled(True)  # 선반수정하는 버튼을 비활성화합니다.
        # 시작지점관련 버튼을 비활성화합니다.
        self.button_makeSP.setDisabled(True)  # 선반만드는 버튼을 비활성화 합니다.
        self.button_deleteSP.setDisabled(True)  # 선반수정하는 버튼을 비활성화합니다.

    def reset_shelf(self):
        self.edit_shelfheight.setEnabled(True)
        self.edit_shelfwidth.setEnabled(True)
        self.edit_shelfmaxitem.setEnabled(True)
        self.check_oneside.setEnabled(True)


        self.button_makeshelf.setEnabled(True)
        self.button_makeblock.setEnabled(True)
        self.button_deleteblock.setEnabled(True)
        self.button_shelfeditor.setEnabled(True)
        self.mode = "Make Map"

        # 패킹지점관련 버튼을 활성화합니다.
        self.button_makePK.setEnabled(True)
        self.button_deletePK.setEnabled(True)
        # 시작지점관련 버튼을 활성화합니다.
        self.button_makeSP.setEnabled(True)
        self.button_deleteSP.setEnabled(True)

    def change_shelf_item(self):
        shelf_max_item = self.edit_shelfmaxitem.text()
        if shelf_max_item.isdigit():
            if 0< int(shelf_max_item) and int(shelf_max_item) <= 6:
                self.shelf_maxitem = int(shelf_max_item)
            else:
                msgBox = QMessageBox()
                msgBox.setWindowTitle("경고")
                msgBox.setText("1~6사이의 숫자값을 입력해주세요.")
                msgBox.exec_()
        else:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("경고")
            msgBox.setText("숫자값을 입력해주세요.")
            msgBox.exec_()
        self.update()

    def change_shelf_width(self):
        shelf_width = self.edit_shelfwidth.text()
        if shelf_width.isdigit():
            if 0< int(shelf_width) and int(shelf_width) <= 30:
                self.shelf_width = int(shelf_width)
            else:
                msgBox = QMessageBox()
                msgBox.setWindowTitle("경고")
                msgBox.setText("0~30사이의 숫자값을 입력해주세요.")
                msgBox.exec_()
        else:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("경고")
            msgBox.setText("숫자값을 입력해주세요.")
            msgBox.exec_()
        self.update()

    def change_shelf_height(self):
        shelf_height = self.edit_shelfheight.text()
        if shelf_height.isdigit():
            if 0< int(shelf_height) and int(shelf_height) <= 30:
                self.shelf_height = int(shelf_height)
            else:
                msgBox = QMessageBox()
                msgBox.setWindowTitle("경고")
                msgBox.setText("0~30사이의 숫자값을 입력해주세요.")
                msgBox.exec_()
        else:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("경고")
            msgBox.setText("숫자값을 입력해주세요.")
            msgBox.exec_()
        self.update()

    def change_resolution(self):
        rValue = self.slider_resolution.value()
        self.edit_resolution.setText(str(rValue))
        self.map_resolution = rValue
        self.occupancy_change()
        self.update()

    def change_resolution_2(self):
        rValue = self.slider_resolution_2.value()
        self.edit_resolution_2.setText(str(rValue))
        self.map_resolution_2 = rValue
        self.occupancy_change()
        self.update()

    def isupresolution(self):
        self.occupy_map = [[0 for col in range(self.map_resolution)] for row in range(self.map_resolution_2)]
        res_width = self.map_width / self.map_resolution
        res_heigth = self.map_height / self.map_resolution_2
        false_flag = False
        for point in self.saved_shelf_point:

            if point[2] == 0 or point[2] == 180:
                lefttop = [point[0] - int(point[3] / 2),
                           point[1] - int(point[4] / 2)]
                rightbottom = [point[0] + int(point[3]/ 2),
                               point[1] + int(point[4]/ 2)]
            else:
                lefttop = [point[0] - int(point[4] / 2),
                           point[1] - int(point[3] / 2)]
                rightbottom = [point[0] + int(point[4] / 2),
                               point[1] + int(point[3] / 2)]

            init_x = self.init_map_x
            init_y = self.init_map_y
            small_x_index = math.floor((lefttop[0] - init_x) / res_width)  # 맨왼쪽 포함
            big_x_index = math.ceil((rightbottom[0] - init_x) / res_width)
            small_y_index = math.floor((lefttop[1] - init_y) / res_heigth)
            big_y_index = math.ceil((rightbottom[1] - init_y) / res_heigth)
            false_flag = False
            for i in range(small_y_index, big_y_index):
                for j in range(small_x_index, big_x_index):
                    if self.occupy_map[i][j] !=0:
                        false_flag = True
                    self.occupy_map[i][j] = 1
            if false_flag== True:
                break
        if false_flag:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("경고")
            msgBox.setText("resolution이 너무 작습니다.")
            msgBox.exec_()
            return False
        else:
            return True

    def occupancy_change(self):
        self.occupy_map = [[0 for col in range(self.map_resolution)] for row in range(self.map_resolution_2)]
        res_width = self.map_width / self.map_resolution
        res_heigth = self.map_height / self.map_resolution_2
        for ind, point in enumerate(self.saved_shelf_point):

            if point[2] == 0 or point[2] == 180:
                lefttop = [point[0] - int(point[3] / 2),
                           point[1] - int(point[4] / 2)]
                rightbottom = [point[0] + int(point[3]/ 2),
                               point[1] + int(point[4]/ 2)]
            else:
                lefttop = [point[0] - int(point[4] / 2),
                           point[1] - int(point[3] / 2)]
                rightbottom = [point[0] + int(point[4] / 2),
                               point[1] + int(point[3] / 2)]

            init_x = self.init_map_x
            init_y = self.init_map_y
            small_x_index = math.floor((lefttop[0] - init_x) / res_width)  # 맨왼쪽 포함
            big_x_index = math.ceil((rightbottom[0] - init_x) / res_width)
            small_y_index = math.floor((lefttop[1] - init_y) / res_heigth)
            big_y_index = math.ceil((rightbottom[1] - init_y) / res_heigth)
            for i in range(small_y_index, big_y_index):
                for j in range(small_x_index, big_x_index):
                    self.occupy_map[i][j] = ind+1

        for ind, block_point in enumerate(self.saved_block_point):
            init_x = self.init_map_x
            init_y = self.init_map_y
            small_x_index = math.floor((block_point[0] - init_x) / res_width)  # 맨왼쪽 포함
            big_x_index = math.ceil((block_point[0] - init_x) / res_width)
            small_y_index = math.floor((block_point[1]- init_y) / res_heigth)
            big_y_index = math.ceil((block_point[1] - init_y) / res_heigth)

            for i in range(small_y_index, big_y_index):
                for j in range(small_x_index, big_x_index):
                    self.occupy_map[i][j] = -(ind+1)

        for ind, block_point in enumerate(self.saved_sp_point):
            init_x = self.init_map_x
            init_y = self.init_map_y
            small_x_index = math.floor((block_point[0] - init_x) / res_width)  # 맨왼쪽 포함
            big_x_index = math.ceil((block_point[0] - init_x) / res_width)
            small_y_index = math.floor((block_point[1]- init_y) / res_heigth)
            big_y_index = math.ceil((block_point[1] - init_y) / res_heigth)

            for i in range(small_y_index, big_y_index):
                for j in range(small_x_index, big_x_index):
                    self.occupy_map[i][j] = ind+10001

        for ind, block_point in enumerate(self.saved_pk_point):
            init_x = self.init_map_x
            init_y = self.init_map_y
            small_x_index = math.floor((block_point[0] - init_x) / res_width)  # 맨왼쪽 포함
            big_x_index = math.ceil((block_point[0] - init_x) / res_width)
            small_y_index = math.floor((block_point[1]- init_y) / res_heigth)
            big_y_index = math.ceil((block_point[1] - init_y) / res_heigth)

            for i in range(small_y_index, big_y_index):
                for j in range(small_x_index, big_x_index):
                    self.occupy_map[i][j] = ind+20001


    def change_width_size(self):
        wValue = self.slider_wSize.value()
        self.edit_wSize.setText(str(wValue))
        self.map_width = wValue
        self.occupancy_change()
        self.update()

    def change_height_size(self):
        hValue = self.slider_hSize.value()
        self.edit_hSize.setText(str(hValue))
        self.map_height =hValue
        self.occupancy_change()
        self.update()

    def change_resolution_edit(self):
        rValue = self.edit_resolution.text()
        if rValue.isdigit():
            if 10 < int(rValue) and int(rValue) <= self.max_map_resolution:
                self.slider_resolution.setValue(int(rValue))
                self.map_resolution = int(rValue)
                self.occupancy_change()
            else:
                msgBox = QMessageBox()
                msgBox.setWindowTitle("경고")
                msgBox.setText("10~"+str(self.max_map_resolution)+"사이의 숫자값을 입력해주세요.")
                msgBox.exec_()
        else:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("경고")
            msgBox.setText("숫자값을 입력해주세요.")
            msgBox.exec_()
        self.update()

    def change_resolution_edit_2(self):
        rValue = self.edit_resolution_2.text()
        if rValue.isdigit():
            if 10 < int(rValue) and int(rValue) <= self.max_map_resolution_2:
                self.slider_resolution_2.setValue(int(rValue))
                self.map_resolution_2 = int(rValue)
                self.occupancy_change()
            else:
                msgBox = QMessageBox()
                msgBox.setWindowTitle("경고")
                msgBox.setText("10~"+str(self.max_map_resolution_2)+"사이의 숫자값을 입력해주세요.")
                msgBox.exec_()
        else:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("경고")
            msgBox.setText("숫자값을 입력해주세요.")
            msgBox.exec_()
        self.update()

    def change_width_edit_size(self):
        wValue = self.edit_wSize.text()
        if wValue.isdigit():
            if 0 < int(wValue) and int(wValue) <= self.max_map_width:
                self.slider_wSize.setValue(int(wValue))
                self.map_width = int(wValue)
                self.occupancy_change()
            else:
                msgBox = QMessageBox()
                msgBox.setWindowTitle("경고")
                msgBox.setText("0~"+str(self.max_map_width)+"사이의 숫자값을 입력해주세요.")
                msgBox.exec_()
        else:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("경고")
            msgBox.setText("숫자값을 입력해주세요.")
            msgBox.exec_()
        self.update()

    def change_height_edit_size(self):
        hValue = self.edit_hSize.text()
        if hValue.isdigit():
            if 0 < int(hValue) and int(hValue) <= self.max_map_height:
                self.slider_hSize.setValue(int(hValue))
                self.map_height = int(hValue)
                self.occupancy_change()
            else:
                msgBox = QMessageBox()
                msgBox.setWindowTitle("경고")
                msgBox.setText("0~"+str(self.max_map_height)+"사이의 숫자값을 입력해주세요.")
                msgBox.exec_()
        else:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("경고")
            msgBox.setText("숫자값을 입력해주세요.")
            msgBox.exec_()
        self.update()

