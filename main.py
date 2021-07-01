import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import *
import urllib.request
import json
form_class = uic.loadUiType("./main_window.ui")[0]
from PyQt5.QtCore import Qt
from Map import *
import os
# class Widget4(QWidget):
#
#     def __init__(self, parent=None):
#         QWidget.__init__(self, parent=parent)
#         self.setWindowTitle("TSP 시뮬레이터")
#         self.a = 0
#         self.move(500,300)
#         self.setFixedWidth(263)
#         self.setFixedHeight(399)
#         # self.show()
#     def paintEvent(self, e):
#         qp = QPainter()
#         qp.begin(self)
#         self.draw_line(qp)
#         qp.end()
#
#     def draw_line(self,qp):
#         qp.setPen(QPen(Qt.blue,8))
#         qp.drawLine(30,230, 200, 50)
#         qp.setPen(QPen(Qt.green, 12))
#         qp.drawLine(140,60, 320, 280)
#         qp.setPen(QPen(Qt.red,16))
#         qp.drawLine(330, 250, 40, 190)


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


if __name__ == "__main__":
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] ='1'
    app = QApplication(sys.argv)
    app.setAttribute(Qt.AA_EnableHighDpiScaling)
    myWindow = WindowClass()
    myWindow.show()
    app.exec_()