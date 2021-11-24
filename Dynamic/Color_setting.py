import random

def getColorSet(color_num):
    color_list = []
    color_base =0
    for i in range(color_num):
        if color_base == 0:
            r = random.randrange(200,255)
            g = random.randrange(0, 100)
            b = random.randrange(0, 100)
        elif color_base == 1:
            r = random.randrange(0, 100)
            g = random.randrange(200, 255)
            b = random.randrange(0, 100)
        elif color_base ==2:
            r = random.randrange(0, 100)
            g = random.randrange(0, 100)
            b = random.randrange(200, 255)
        color_list.append([r,g,b])
        color_base =(color_base+1)%3
    return color_list
def getbrightColorSet(color_num):
    color_list = []
    color_base =0
    for i in range(color_num):
        if color_base == 0:
            r = random.randrange(254,255)
            g = random.randrange(240, 255)
            b = random.randrange(180, 230)
        elif color_base == 1:
            r = random.randrange(180, 230)
            g = random.randrange(254, 255)
            b = random.randrange(240, 255)
        elif color_base ==2:
            r = random.randrange(240, 255)
            g = random.randrange(180, 230)
            b = random.randrange(254, 255)
        elif color_base ==3:
            r = random.randrange(254, 255)
            g = random.randrange(180, 230)
            b = random.randrange(240, 255)
        color_list.append([r,g,b])
        color_base =(color_base+1)%4
    return color_list