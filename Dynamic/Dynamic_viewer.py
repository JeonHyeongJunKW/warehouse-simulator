from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import math
import json
import time
from Dynamic.Map_drawer import map_maker
from Dynamic.simulation_main_drawer import main_drawer
from Dynamic.DEBUG_tool import DEBUG_log

class online_simulator(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        DEBUG_log("입력확인")
        uic.loadUi("Dynamic/online_simulator.ui", self)
        self.main_drawer = main_drawer(self)


        #체크박스 설정
        self.cb_lo_route.stateChanged.connect(self.viewLongRoute)
        self.cb_sh_route.stateChanged.connect(self.viewShortRoute)
        self.cb_target.stateChanged.connect(self.viewTarget)
        self.cb_solo_target.stateChanged.connect(self.viewSoloTarget)
        DEBUG_log("초기화 완료")
    def viewLongRoute(self):
        if self.cb_lo_route.isChecked():
            self.main_drawer.is_view_full_route = True
        else:
            self.main_drawer.is_view_full_route = False

    def viewSoloTarget(self):
        if self.cb_solo_target.isChecked():
            self.main_drawer.is_view_solo_target = True
        else:
            self.main_drawer.is_view_solo_target = False

    def viewShortRoute(self):
        if self.cb_sh_route.isChecked():
            self.main_drawer.is_view_route = True
        else:
            self.main_drawer.is_view_route = False

    def viewTarget(self):

        if self.cb_target.isChecked():
            self.main_drawer.is_view_target = True
        else:
            self.main_drawer.is_view_target = False

    def run(self,gui_data):
        self.gui_data = gui_data
        map_data = self.gui_data["map_data"]
        ui_info = self.gui_data["ui_data"]
        #기본 데이터를 등록합니다.
        self.setMapInfo(map_data,ui_info)
        self.start_draw()



    def setMapInfo(self, map_data, ui_info):
        self.map_maker = map_maker(self)
        self.map_name = 'map.jpg'
        self.map_maker.draw_and_save(map_data, self.map_name, ui_info)
        self.map_maker.hide()
        ## 기본 설정
        sim_width,sim_height = self.main_drawer.default_set(map_data,self.map_name,ui_info)
        self.setFixedWidth(sim_width)
        self.setFixedHeight(sim_height)
        ##제어기 위치 조절
        self.gb_sim_control.move(sim_width - 190, 20)
        self.show()
        self.main_drawer.show()
        self.main_drawer.update()

    def start_draw(self):
        self.main_drawer.start_draw(self.gui_data)


