import copy

def getTable(target:str)->list: #从输入中分析出对应的Max表，allocation表等
    global Pnum, Rnum, infos
    tables = []
    if target == "available": #一维数组
        line = infos[infos.index(target) + 1]
        eachs = line.split(" ")
        for i in range(0, Rnum):
            tables.append(int(eachs[i]))
    else: #二维数组
        for i in range(0, Pnum):
            tables.append([]) #确定行数
        for i in range(0, Pnum): #填充列
            line = infos[infos.index(target) + 1 + i]
            eachs = line.split(" ")
            for j in range(0, Rnum):
                tables[i].append(int(eachs[j]))
    return tables

def getNeed()->list: #return a need
    global Pnum, Rnum, Max, Allocation
    Need = []
    for i in range(0, Pnum):
        Need.append([])
    for i in range(0, Pnum):
        for j in range(0, Rnum):
            Need[i].append(Max[i][j] - Allocation[i][j])
    return Need

with open("inputC.txt", "r") as f: #inputA 代表报告中的A状态, inputC代表报告中的C状态
    infos = f.read().split('\n')
    Pnum = int(infos[infos.index('p') + 1])
    Rnum = int(infos[infos.index('r') + 1])
    Available = getTable('available')
    Allocation = getTable('allocation')
    Max = getTable('max')
    Need = getNeed()

def printTable(name:str):
    global Pnum, Rnum, Available, Allocation, Max, Need
    if name == "ava":
        print("当前资源剩余情况:")
        for i in range(0, Rnum):
            print(f"{i}号资源剩余{Available[i]}个")
    elif name == "allo":
        print("当前资源占用情况:")
        for i in range(0, Pnum):
            print(f"{i}号进程: {Allocation[i]}")
    elif name == "max":
        print("各进程最大占用资源情况:")
        for i in range(0, Pnum):
            print(f"{i}号进程: {Max[i]}")
    elif name == "need":
        print("各进程尚需资源情况:")
        for i in range(0, Pnum):
            print(f"{i}号进程: {Need[i]}")

def checkCMD(cmd:str)->bool:
    global Pnum, Rnum
    cmd = cmd.split(" ")
    if not cmd[0] in ['req', 'rel', 'p']: #遇到了不认识的命令
        print(f"Error! no cmd named {cmd[0]}")
        return False
    elif cmd[0] == "p": #print命令
        if len(cmd) != 2:
            print(f"Error! try like print ava")
            return False
        elif not cmd[1] in ['ava', 'max', 'allo', 'need', 'all']:
            print(f"Error! no cmd named p {cmd[1]}")
            return False
    elif cmd[0] in ['req', 'rel']:
        if len(cmd) != 4 or not cmd[1].isdigit() or not cmd[2].isdigit() or not cmd[3].isdigit(): #个数不对或者不是整数
            print(f"Error! try like {cmd[0]} 1, 2")
            return False
        elif int(cmd[1]) >= Pnum:
            print(f'Error! there is no process{cmd[1]}')
            return False
        elif int(cmd[2]) >= Rnum:
            print(f'Error! there is no resource{cmd[2]}')
            return False
    return True

def addWork(Work:list, Allocation:list, pid:int)->list: #从Allocation释放pid进程占有的资源，加入给Work。返回新Work
    global Rnum
    newWork = copy.deepcopy(Work)
    for i in range(0, Rnum):
        newWork[i] = Work[i] + Allocation[pid][i]
    return newWork
    
def security()->bool: #安全性算法，如果安全则返回Ture，反之False
    global Pnum, Rnum, Available, Allocation, Max, Need
    Work = copy.deepcopy(Available) #初始和Available一样，一维数组，代表每种资源剩余个数
    Finish = [False for i in range(0, Pnum)] #默认全部为False
    SafeQue = [] #安全队列
    while(1):
        if False not in Finish: #没有False了说明成功了
            print(f"安全队列: {SafeQue}")
            return True
        flag_outer = False #用来标志是否找不到一个进程可以去释放资源的
        for i in range(0, Pnum): #遍历进程
            if Finish[i]: #说明已经为True了，直接跳过
                continue
            flag_inner = False #标志有无分配成功
            for j in range(0, Rnum): #遍历资源
                if not Need[i][j] <= Work[j]: #发现不满足的地方
                    break
                if j == Rnum - 1: #满足条件且到达了最后一个，即全部满足
                    Work = addWork(Work, Allocation, i) #将i进程的资源释放
                    Finish[i] = True
                    flag_inner = True
                    SafeQue.append(i)
                    # print(f"进程{i}分配成功\n现在的Work:{Work}")
                else: #满足则继续看下一个资源情况是否满足
                    continue
            if flag_inner:
                flag_outer = True
                break #在该进程出成功分配了某资源，重新开始从头开始找进程
            else:
                if i == Pnum - 1: #已经到了最后一个进程了，仍然失败
                    break
                else: 
                    continue #继续尝试下一个进程
        if flag_outer == False:
            print("不安全状态!不予分配!")
            return False #当前状态为不安全状态

while(1):
    cmd = input('>')
    if not checkCMD(cmd):
        continue
    cmd = cmd.split(" ")
    if cmd[0] == "quit": #退出
        break
    elif cmd[0] == "p": #print 输出相关信息
        printTable(cmd[1])
        if (cmd[1] == "all"):
            printTable('allo')
            printTable('need')
            printTable('ava')
    elif cmd[0] == "req": #申请资源 req 0 0 1，表示0号进程申请1个0号资源 
        pid, rid, num = int(cmd[1]), int(cmd[2]), int(cmd[3])
        if num > Need[pid][rid]: #大于所需
            print(f"申请资源数 {num} 大于所需 Need[{pid}][{rid}] {Need[pid][rid]}!")
        elif num > Available[rid]: #大于可用
            print(f"申请资源数 {num} 大于剩余 Available[{rid}] {Available[rid]}!")
        else: #能够分配，预分配，查看是否为安全状态，否则回溯
            Allocation[pid][rid] += num
            Available[rid] -= num
            Need = getNeed()
            if not security(): #如果不是安全序列回溯
                Allocation[pid][rid] -= num
                Available[rid] += num
                Need = getNeed()
            else:
                print("分配成功!")
    elif cmd[0] == "rel": #释放资源 rel 0 0 1 表示0号进程释放1个0号资源
        pid, rid, num = int(cmd[1]), int(cmd[2]), int(cmd[3])
        Allocation[pid][rid] -= num
        Available[rid] += num
        Need = getNeed()
        print(f"进程{pid}成功释放{num}个资源{rid}!")

