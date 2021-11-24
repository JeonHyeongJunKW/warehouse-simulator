from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import  *
from PyQt5.QtCore import Qt
import math
import json


class Widget_SimSet(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        uic.loadUi("simulation_parameter_editor.ui",self)

        #각 파라미터 변수 저장용
        self.is_randomItem = True#랜덤으로 아이템을 배치합니다.
        self.is_randomOrder = True#임의로 정한방식으로 주문이 들어옵니다.
        self.default_initorder = 0#초기 주문량
        self.default_orderrate = 10#주문의 증가율
        self.robot_cap = 1 #로봇의 아이템 저장용량
        self.robot_number = 1#로봇의 대수
        self.is_safe_close = True


        #GUI설정용
        self.radioButton_random.setChecked(True)#랜덤으로 아이템을 배치하는 의미로 라디오버튼을 킵니다.
        self.radioButton_orderdirect.clicked.connect(self.SetDirectOrder)
        self.radioButton_orderrandom.clicked.connect(self.SetRandomOrder)
        self.radioButton_random.clicked.connect(self.SetRandomItem)
        self.radioButton_handmake.clicked.connect(self.SetDirectItem)
        self.pushButton_openinveditor.clicked.connect(self.openinveditor)
        self.pushButton_save_set.clicked.connect(self.save_set)
        self.pushButton_load_set.clicked.connect(self.load_set)
        self.pushButton_close.clicked.connect(self.close_n_save)

        self.radioButton_handmake.hide()
        self.pushButton_openinveditor.hide()
        self.sim_data = [self.is_randomOrder, int(self.lineEdit_initorder.text()), int(self.lineEdit_orderrate.text()),
                         self.robot_cap, self.robot_number]

    def close_n_save(self):
        if self.is_randomOrder:
            pass
        else:
            init_order = self.lineEdit_initorder.text()
            order_rate = self.lineEdit_orderrate.text()

            if not self.is_goodAnswer(init_order):
                msgBox = QMessageBox()
                msgBox.setWindowTitle("경고")
                msgBox.setText("초기 주문량 값이 이상합니다.")
                msgBox.exec_()
                return False
            if not self.is_goodAnswer(order_rate):
                msgBox = QMessageBox()
                msgBox.setWindowTitle("경고")
                msgBox.setText("주문 증가율 값이 이상합니다.")
                msgBox.exec_()
                return False

        robotcap = self.lineEdit_robotcap.text()
        robotnumber = self.lineEdit_robotnumber.text()


        if not self.is_goodAnswer(robotcap):
            msgBox = QMessageBox()
            msgBox.setWindowTitle("경고")
            msgBox.setText("로봇의 용량이 이상합니다.")
            msgBox.exec_()
            return False

        if not self.is_goodAnswer(robotnumber):
            msgBox = QMessageBox()
            msgBox.setWindowTitle("경고")
            msgBox.setText("로봇의 수가 이상합니다.")
            msgBox.exec_()
            return False
        robotcap = int(robotcap)
        robotnumber =int(robotnumber)
        self.is_safe_close = True
        self.sim_data = [self.is_randomOrder, int(self.lineEdit_initorder.text()), int(self.lineEdit_orderrate.text()), robotcap,robotnumber]
        self.close()


    def SetDirectOrder(self):
        self.is_randomOrder = False
        self.lineEdit_initorder.setEnabled(True)
        self.lineEdit_orderrate.setEnabled(True)

    def SetRandomOrder(self):
        self.is_randomOrder = True
        self.lineEdit_initorder.setDisabled(True)
        self.lineEdit_orderrate.setDisabled(True)

    def SetRandomItem(self):
        self.is_randomItem = True
        self.pushbutton_openinveditor.setDisabled(True)

    def SetDirectItem(self):
        self.is_randomItem = False
        self.pushbutton_openinveditor.setEnabled(True)

    def openinveditor(self):
        print("making~")

    def is_goodAnswer(self, value):
        if not value.isdigit():
            return False
        if int(value) < 0:
            return False
        return True

    def load_set(self):
        FileSave = QFileDialog.getOpenFileName(self, '시물레이션 셋팅 불러오기', './sim_setting/', "Map File (*.json)")[0]
        if FileSave == "":
            pass

        else:
            with open(FileSave, 'r') as fp:
                data = json.load(fp)
                self.is_randomOrder = data['random_order']
                if self.is_randomOrder :
                    self.radioButton_orderrandom.setChecked(True)  # 랜덤으로 아이템을 배치하는 의미로 라디오버튼을 킵니다.
                    self.lineEdit_initorder.setDisabled(True)
                    self.lineEdit_orderrate.setDisabled(True)
                else :
                    self.radioButton_orderdirect.setChecked(True)  # 랜덤으로 아이템을 배치하는 의미로 라디오버튼을 킵니다.
                    self.lineEdit_initorder.setEnabled(True)
                    self.lineEdit_orderrate.setEnabled(True)
                self.lineEdit_initorder.setText(str(data['init_order']))
                self.lineEdit_orderrate.setText(str(data['order_rate']))
                self.lineEdit_robotcap.setText(str(data['robot_cap']))
                self.lineEdit_robotnumber.setText(str(data['robot_number']))

    def save_set(self):
        data = {}
        if self.is_randomOrder:
            data['random_order'] = True
            data['init_order'] = self.default_initorder
            data['order_rate'] = self.default_orderrate
        else:
            data['random_order'] = False
            init_order = self.lineEdit_initorder.text()
            order_rate = self.lineEdit_orderrate.text()

            if self.is_goodAnswer(init_order):
                data['init_order'] = int(init_order)
            else:
                msgBox = QMessageBox()
                msgBox.setWindowTitle("경고")
                msgBox.setText("초기 주문량 값이 이상합니다.")
                msgBox.exec_()
                return False
            if self.is_goodAnswer(order_rate):
                data['order_rate'] = int(order_rate)
            else:
                msgBox = QMessageBox()
                msgBox.setWindowTitle("경고")
                msgBox.setText("주문 증가율 값이 이상합니다.")
                msgBox.exec_()
                return False
        robotcap = self.lineEdit_robotcap.text()
        robotnumber = self.lineEdit_robotnumber.text()

        if self.is_goodAnswer(robotcap):

            data['robot_cap'] = int(robotcap)
        else:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("경고")
            msgBox.setText("로봇의 용량이 이상합니다.")
            msgBox.exec_()
            return False
        if self.is_goodAnswer(robotnumber):
            data['robot_number'] = int(robotnumber)
        else:
            msgBox = QMessageBox()
            msgBox.setWindowTitle("경고")
            msgBox.setText("로봇의 수가 이상합니다.")
            msgBox.exec_()
            return False

        FileSave = QFileDialog.getSaveFileName(self, '시물레이션 셋팅 저장하기', './sim_setting/', "sim_set File (*.json)")[0]
        if FileSave == "":
            pass

        else:
            with open(FileSave, 'w') as fp:
                json.dump(data, fp)
