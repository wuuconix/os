class Process:
   def __init__(self, Id, Name, Priority):
       self.id = int(Id)
       self.name = Name
       self.priority = int(Priority)
       self.status = "ready" #默认为ready状态
       self.resource = None #表示该进程正在使用的资源标号，默认不需要资源,

class Resource:
   def __init__(self, Id):
       self.id = int(Id)
       self.status = "free" #默认资源的状态为free
       self.blockQue = None #表示当前资源阻塞了那些进程，记录进程的id

def findProcess(processes:list, pid:int)->Process: #根据pid从列表中找到进程对象并返回
    for i in processes:
        if i.id == pid:
            return i
    return None

def chooseRun(readyQue:list)->Process: #选择当前就绪队列中优先级最高的且最先到的进程来运行
    index, que = 3, readyQue[3]
    while len(que) == 0:
        index -= 1
        que = readyQue[index]
    return que.pop(0)

def InitProcess()->list: #实验报告要求的初始化进程函数，它会返回一个包含init进程的一个进程列表
    processes = []
    initProcess = Process(0, "Init", 0) #按照实验指导要求生成一个0优先级的init进程
    processes.append(initProcess)
    return processes

def InitResources()->list: #初始化资源，一共有4个资源，id分别为0~4，默认状态都是free
    resources = []
    for i in range(0, 5):
        resources.append(Resource(i)) #利用构造函数给资源一个id号
    return resources
    
def printReadyQue(readyQue): #可视化输出各个优先级的就绪队列
    for i in range(len(readyQue) - 1, -1, -1):
        que = readyQue[i]
        if len(que) == 0:
            print(f"readyQue[{i}] is empty")
        else:    
            print(f"readyQue[{i}] has {len(que)} processes:")
            for process in que:
                print(" " * 12 + f"pid: {process.id} name: {process.name}")

def printRunProcess(runningProcess): #可视化输出当前运行的进程
    print("running process:\n" + f"pid: {runningProcess.id} name: {runningProcess.name}")

def printProcesses(processes): #可视化输出所有的进程
    print(f"now existing {len(processes)} process")
    for i in processes:
        print(f"pid: {i.id}  name: {i.name}  priority: {i.priority}  status: {i.status}  resource: {i.resource}")

def printResouces(resources): #可视化输出所有的资源
    for i in resources:
        print(f"rid: {i.id}  status: {i.status}  blockQue: {i.blockQue}")

def checkCMD(cmd:str)->bool: #检测命令是否合法，合法则True，非法则False
    if cmd == "":
        return False
    cmd = cmd.split()
    if cmd[0] not in ["ls", "cr", "kill", "req"]: #不在已有命令中
        print(f"Error! No cmd named {cmd[0]}")
    elif cmd[0] == "ls" and cmd[1] not in ["-q", "--run", "-p", "-r"]:
        print(f"Error in ls, No ls cmd named ls {cmd[1]}")
        return False
    elif cmd[0] == "cr" and (len(cmd) != 3 or not cmd[2].isdigit()): #参数个数不对或者优先级不是数字
        print("Error in cr, please use like 'cr A 2'")
        return False
    elif cmd[0] == "cr" and (int(cmd[2]) > 3 or int(cmd[2]) < 0): #优先级不在0~3之间
        print("Error in cr, please make sure your priority from 0 to 3")
        return False
    elif cmd[0] == "kill" and not cmd[1].isdigit(): #第一个参数若不是数字
        print("Error in kill, please use like 'kill 1'")
        return False
    elif cmd[0] == "req" and (len(cmd) != 3 or not cmd[1].isdigit() or not cmd[2].isdigit()): #参数个数不对或着pid和rid不是数字
        print("Error in req, please use like 'req 1 3'")
        return False
    return True

processes = InitProcess()
resources = InitResources()
blockQue = [] #记录当前哪些进程被阻塞了
readyQue = [[], [], [], []] #就绪队列组，按照优先级分出不同的优先级队列。下标为0的代表优先级为0的就绪队列。默认有0~3，一共4个优先级队列

runningProcess = processes[0] #一开始running的就是init进程
pid = 1 #不断递增的pid

while(1):
    cmd = input(">")
    if not checkCMD(cmd): #如果格式错误，则让用户重新输入
        continue
    cmd = cmd.split() #根据空格区分
    if cmd[0] == "quit": #quit退出
        break
    elif cmd[0] == "ls": #ls命令包含一系列查看操作 例子ls -p查看所有进程
        if cmd[1] == "-q": #查看就绪队列
            printReadyQue(readyQue)
        elif cmd[1] == "--run": #查看正在运行的进程
            printRunProcess(runningProcess)
        elif cmd[1] == "-p": #查看所有进程
            printProcesses(processes)
        elif cmd[1] == "-r": #查看所有资源
            printResouces(resources)
    elif cmd[0] == "cr": #创建进程  例如 cr A 3 将创建一个优先级为3，名字为A的进程。
        name, priority = cmd[1], int(cmd[2]) #priority需要为整型
        newProcess = Process(pid, name, priority)
        processes.append(newProcess)
        pid += 1
        if newProcess.priority <= runningProcess.priority: #如果没有超过正在运行的进程的优先级，则加入就绪队列
            readyQue[priority].append(newProcess)
        else: #否则剥夺当前进程
            runningProcess.status = "ready"
            readyQue[runningProcess.priority].append(runningProcess)
            newProcess.status = "running"
            runningProcess = newProcess
        print(f"* process {runningProcess.name} is running!")
    elif cmd[0] == "kill": #杀死进程 例如 kill 1 将杀死pid为1的进程
        pid = int(cmd[1]) # 利用pid来删除进程
        if pid == 0:
            print("init process could not be killed!")
            continue
        targetProcess = findProcess(processes, pid)
        if not targetProcess:
            print(f"cant't find process {pid}")
            continue
        if targetProcess.status == "running": #如果kill的进程是当前执行的，需要从就绪队列中上一个来执行
            processes.remove(runningProcess)
            print(f"* process {runningProcess.name} has been killed!")
            runningProcess = chooseRun(readyQue)
            print(f"* process {runningProcess.name} is running!")
        elif targetProcess.status == "ready": #要kill的进程在就绪队列中
            for i in readyQue:
                if targetProcess in i:
                    i.remove(targetProcess)
                    break
            processes.remove(targetProcess)
            print(f"* process {targetProcess.name} has been killed!")
        elif targetProcess.status == "block": #要kill的进程在阻塞队列中
            blockQue.remove(targetProcess)
            for i in resources: #资源的阻塞队列中如果有它，也需要进行清楚
                if pid in i.blockQue:
                    i.blockQue.remove(pid) 
    elif cmd[0] == "req": #请求资源 例如 req 1 3 表示1号进程去申请3号资源
        pid, rid = int(cmd[1]), int(cmd[2]) #re pid, rid的格式，表示pid的进程去请求rid的资源
        if resources[rid].status == "free": #若资源空闲
            resources[rid].status = "allocated"
            targetProcess = findProcess(processes, pid)
            if targetProcess:
                targetProcess.resource = rid
                print(f"* process {runningProcess.name} is running!")
            else:
                print(f"cant't find process {pid}")
                continue
        elif resources[rid].status == "allocated": #若资源已被占用
            targetProcess = findProcess(processes, pid)
            if not targetProcess:
                print(f"cant't find process {pid}")
                continue
            else:
                status = targetProcess.status
                if status == "running":
                    print(f"* process {targetProcess.name} is blocked!   (from running to block)")
                    targetProcess.status = "block"
                    blockQue.append(targetProcess)
                    nextRunProcess = chooseRun(readyQue)
                    runningProcess = nextRunProcess
                    runningProcess.status = "running" #新晋运行进程
                    print(f"* process {runningProcess.name} is running!")
                elif status == "ready":
                    print(f"* process {targetProcess.name} is blocked!   (from ready to block)")
                    targetProcess.status = "block"
                    blockQue.append(targetProcess)        
                    print(f"* process {runningProcess.name} is running!")
                elif status == "block":
                    print(f"* process {targetProcess.name} is blocked!   (from block to block)")
                    print(f"* process {runningProcess.name} is running!")