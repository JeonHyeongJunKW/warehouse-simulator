import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
import urllib.request
import json

form_class = uic.loadUiType("./main_window.ui")[0]
from PyQt5.QtCore import Qt
from Map import *
from SimSet import *
import os


class WindowClass(QMainWindow, form_class):
    def __init__(self):
        super(WindowClass,self).__init__()
        self.setupUi(self)
        self.setWindowTitle("TSP 시뮬레이터")
        self.a = 0
        self.move(500, 300)
        self.setFixedWidth(263)
        self.setFixedHeight(399)
        self.mapMaker = Widget_Warehouse()
        self.mapMaker.hide()
        self.simulation_maker =  Widget_SimSet()
        self.simulation_maker.hide()

        #시그널링 설정
        self.button_openmapmaker.clicked.connect(self.openMap)
        self.button_loadMap.clicked.connect(self.loadMap)
        self.button_paramset.clicked.connect(self.setSim)

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
                self.map_width = data['map_size'][0]
                self.map_height = data['map_size'][1]
                self.map_resolution = data['map_resolution'][0]
                self.map_resolution_2 = data['map_resolution'][1]
                self.occupy_map = data['occupay_map']
                self.saved_shelf_point = data['shelf_point']
                self.saved_block_point = data['block_point']
                self.saved_pk_point = data['pack_point']
                self.saved_sp_point = data['start_point']

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
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] ='1'
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()