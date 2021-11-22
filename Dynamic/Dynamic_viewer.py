from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import math
import json
import time
from Dynamic.Map_drawer import map_maker
from Dynamic.simulation_main_drawer import main_drawer

class online_simulator(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("./Dynamic/online_simulator.ui", self)
        self.gui_data = None
        self.is_view_shelf = False
        self.is_view_route = False
        self.is_view_full_route = False
        self.checkBox_viewAllShelf.stateChanged.connect(self.viewShelf)
        self.timer = QTimer(self)

        self.checkBox_viewRoute.stateChanged.connect(self.viewRoute)
        self.checkBox_viewFullRoute.stateChanged.connect(self.viewFullRoute)

        self.main_drawer = main_drawer(self)

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


    def run(self,gui_data):
        self.gui_data = gui_data

        map_data = self.gui_data["map_data"]
        ui_info = self.gui_data["ui_info"]
        self.setMapInfo(self,map_data,ui_info)


    def setMapInfo(self, map_data, ui_info):
        self.map_maker = map_maker(self)
        self.map_name = 'map.jpg'

        self.map_maker.draw_and_save(map_data, self.map_name, ui_info)
        self.map_maker.hide()

        ## 기본 설정
        sim_width,sim_height = self.main_drawer.default_set(map_data,self.map_name)
        self.setFixedWidth(sim_width)
        self.setFixedHeight(sim_height)
        self.map_drawer.show()
        self.map_drawer.update()


