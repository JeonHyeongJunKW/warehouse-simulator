import random
import time
from multiprocessing import Process

class procees_order_maker:
    def __init__(self):
        self.sub_process = None
        self.order_data = None


    def run(self, order_data):

        self.order_data = order_data
        self.order_data["reset"] = False #리셋플레그를 false로합니다.

        #이전에 살려뒀던 프로세스를 죽입니다.
        if self.sub_process != None:
            if self.sub_process.is_alive():
                self.sub_process.kill()

        #새로운 프로세스를 할당합니다.
        self.sub_process = Process(target=self.process, args=(self.order_data,1))
        self.sub_process.start()

    def reset(self):
        #while 탈출 및 sub process를 죽입니다.
        self.order_data["reset"] = True
        if self.sub_process.is_alive():
            self.sub_process.kill()

    def process(self,order_data, no_use):

        ## dynamic order make
        initOrder = order_data["simulation_order_set"][1]  # 초기 주문량
        order_rate = order_data["simulation_order_set"][2]  # 시간당 주문 증가량

        kind = order_data['order_kind'] # 주문의 종류
        order_data["orders"] = [list(set([random.choice(list(range(kind))) for _ in range(5)])) for __ in
                                range(initOrder)]
        while True:
            if order_data["reset"]:
                break

            time.sleep(1)
            new_order = [list(set([random.choice(list(range(kind))) for _ in range(5)])) for __ in
                         range(order_rate)]
            order_data["orders"] = order_data["orders"] + new_order