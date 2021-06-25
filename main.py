import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
import urllib.request
import json
form_class = uic.loadUiType("./main_window.ui")[0]
from PyQt5.QtCore import Qt
from Map import *



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
        # self.setCentralWidget(self.test_widget)
        self.button_openmapmaker.clicked.connect(self.openMap)
        self.button_loadMap.clicked.connect(self.loadMap)

    def openMap(self):

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


if __name__ == "__main__":

    app = QApplication(sys.argv)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()