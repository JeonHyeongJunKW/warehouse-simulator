import matplotlib.pyplot as plt
import numpy as np
from fpdf import FPDF
# from matplotlib.backends.ba
def makePDF(al_time,al_step,al_full_time):
    algorithm_name = ['Default',"GA","PSO","ACO","Div. & Conq. ","Greedy"]
    algorithm_color = ['black', 'red','darkorange','lawngreen','deepskyblue','darkviolet']
    # print(al_time)
    # print(al_step)

    #각 알고리즘별 총 이동거리를 구합니다.
    algorithm_each_length =[]
    for i, step_by_al in enumerate(al_step):
        algorithm_each_length.append(sum(step_by_al)*0.1)
    al_length = len(algorithm_each_length)
    x = np.arange(al_length)
    robot_index = algorithm_name
    robot_value = algorithm_each_length
    plt.figure(figsize=(8, 4))
    plt.title("Total travel distance", fontsize=25)
    plt.bar(x, robot_value, width=0.8, color=algorithm_color)
    plt.xticks(x, robot_index)
    plt.savefig("result/" + "알고리즘별 총 이동시간.png")
    plt.clf()


    for i, time_by_al in enumerate(al_time):
        plt.figure(figsize=(8,4))
        len_robot =len(time_by_al)
        x =np.arange(len_robot)
        robot_index =list(range(len_robot))
        robot_value =time_by_al
        bar_color = [algorithm_color[i] for _ in range(len_robot)]
        plt.title(algorithm_name[i]+" Algorithm time", fontsize=25)
        plt.bar(x,robot_value,width=0.4, color=bar_color,)
        plt.xticks(x,robot_index)
        plt.savefig("result/"+algorithm_name[i]+" 로봇별 시간.png")
        plt.clf()

    for i, time_by_al in enumerate(al_step):
        plt.figure(figsize=(8, 4))
        len_robot =len(time_by_al)
        x =np.arange(len_robot)
        robot_index =list(range(len_robot))
        robot_value =time_by_al
        bar_color = [algorithm_color[i] for _ in range(len_robot)]
        plt.title(algorithm_name[i]+" Travel distance", fontsize=25)
        plt.bar(x,robot_value,width=0.4, color=bar_color)
        plt.xticks(x,robot_index)
        plt.savefig("result/"+algorithm_name[i]+" 로봇별 이동거리.png")
        plt.clf()

    al_length = len(al_full_time)
    x = np.arange(al_length)
    robot_index = algorithm_name
    robot_value = al_full_time
    plt.figure(figsize=(8, 4))
    plt.title("Algorithm time", fontsize=25)
    plt.bar(x, robot_value, width=0.8, color =algorithm_color)
    plt.xticks(x, robot_index)
    plt.savefig("result/" + "알고리즘별 소요시간.png")
    plt.clf()

    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Helvetica",size=15)
    pdf.cell(200,30, txt="Total travel distance for each algorithm", ln=1, align='L')
    pdf.image("result/" + "알고리즘별 총 이동시간.png",w= pdf.w/1.2)
    pdf.ln(30)
    pdf.cell(200, 30, txt="Total hours of operation for each algorithm", ln=1, align='L')
    pdf.image("result/" + "알고리즘별 소요시간.png", w=pdf.w / 1.2)

    for i, time_by_al in enumerate(al_step):
        if i%2==0:
            pdf.add_page()
        pdf.cell(200, 30, txt=algorithm_name[i]+" :  Travel distance for each robot", ln=1, align='L')
        pdf.image("result/"+algorithm_name[i]+" 로봇별 이동거리.png", w=pdf.w / 1.2)
        pdf.ln(30)
    '''
    Total travel distance for each algorithm
    Total hours of operation for each algorithm
    알고리즘 이름 (크게)
    --한칸띄고--
    --Distance of each robot--
    --그림 가로로 한장--
    --
    '''

    pdf.output("result/"+"simulation_result.pdf")
    # pages = convert_from_path("result/"+"simulation_result.pdf", dpi=500)
    # for i, page in enumerate(pages):
    #     page.save("result/"+"simulation_img_"+str(i)+".jpg","JPEG")