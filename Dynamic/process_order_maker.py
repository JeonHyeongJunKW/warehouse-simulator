import random
import time
from multiprocessing import Process

class procees_order_maker:
    def __init__(self):
        self.sub_process = None
        self.order_data = None

        self.init_ordernum = 0
        self.update_ordernum = 2
        self.max_itemnum =4
        self.max_ordercall = 50

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
        if self.sub_process ==None:
            return
        #while 탈출 및 sub process를 죽입니다.
        self.order_data["reset"] = True

        if self.sub_process.is_alive():
            self.sub_process.kill()

    def process(self,order_data, no_use):

        ## dynamic order make
        initOrder = self.init_ordernum  # 초기 주문량
        order_rate = self.update_ordernum  # 시간당 주문 증가량
        order_size =self.max_itemnum
        kind = order_data['order_kind'] # 주문의 종류
        random.seed(100)
        order_data["orders"] = [list(set([random.choice(list(range(kind))) for _ in range(order_size)])) for __ in
                                range(initOrder)]
        order_count =initOrder
        end_flag = False
        while True:
            if order_data["reset"]:
                break

            if order_count <self.max_ordercall:
                order_count += order_rate
            else:
                if not end_flag:
                    print("히히 이젠 못받아!")
                end_flag =True
                continue
            time.sleep(1)
            new_order = [list(set([random.choice(list(range(kind))) for _ in range(order_size)])) for __ in
                         range(order_rate)]
            order_data["orders"] = order_data["orders"] + new_order