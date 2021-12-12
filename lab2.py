class Process:
   def __init__(self, Id, Name, Priority):
       self.id = int(Id)
       self.name = Name
       self.priority = int(Priority)
       self.status = "ready" #默认为ready状态
       self.resource = [] #表示该进程正在使用的资源标号，默认不需要资源
       self.wantRe = [] #表示进程需要但还未被满足的资源，默认为空

class Resource:
   def __init__(self, Id):
       self.id = int(Id)
       self.status = "free" #默认资源的状态为free
       self.usingPid = -1 #表示正在使用该资源的进程的pid
       self.blockQue = [] #表示当前资源阻塞了那些进程，记录进程的id

def getProcessById(pid:int)->Process: #根据pid从列表中找到进程对象并返回
    global processes
    for i in processes:
        if i.id == pid:
            return i
    return None

def InitProcess()->list: #实验报告要求的初始化进程函数，它会返回一个包含init进程的一个进程列表
    processes = []
    initProcess = Process(0, "Init", 0) #按照实验指导要求生成一个0优先级的init进程
    initProcess.status = "running"
    processes.append(initProcess)
    return processes

def InitResources()->list: #初始化资源，一共有4个资源，id分别为0~3，默认状态都是free
    resources = []
    for i in range(0, 4):
        resources.append(Resource(i)) #利用构造函数给资源一个id号
    return resources
    
def printReadyQue(): #可视化输出各个优先级的就绪队列
    global readyQue
    for i in range(len(readyQue) - 1, -1, -1):
        que = readyQue[i]
        if len(que) == 0:
            print(f"readyQue[{i}] is empty")
        else:    
            print(f"readyQue[{i}] has {len(que)} processes:")
            for process in que:
                print(" " * 12 + f"pid: {process.id} name: {process.name}")

def printRunProcess(): #可视化输出当前运行的进程
    global processes
    runningProcess = getRunProcess()
    print("running process:\n" + f"pid: {runningProcess.id} name: {runningProcess.name}")

def printProcesses(): #可视化输出所有的进程
    global processes
    print(f"now existing {len(processes)} process")
    for i in processes:
        print(f"pid: {i.id}  name: {i.name}  priority: {i.priority}  status: {i.status}  resource: {i.resource}  wantRe: {i.wantRe}")

def printResources(): #可视化输出所有的资源
    global resources
    for i in resources:
        print(f"rid: {i.id}  status: {i.status}  usingPid: {i.usingPid}  blockQue: {i.blockQue}")

def checkCMD(cmd:str)->bool: #检测命令是否合法，合法则True，非法则False
    if cmd == "":
        return False
    cmd = cmd.split()
    if cmd[0] not in ["ls", "cr", "kill", "req", "rel", "quit"]: #不在已有命令中
        print(f"Error! No cmd named {cmd[0]}")
    elif cmd[0] == "ls" and cmd[1] not in ["-q", "--run", "-p", "-r"]:
        print(f"Error in ls, No ls cmd named ls {cmd[1]}")
        return False
    elif cmd[0] == "cr" and (len(cmd) != 3 or not cmd[2]): #参数个数不对或者优先级不是数字
        print("Error in cr, please use like 'cr A 2'")
        return False
    elif cmd[0] == "cr" and (int(cmd[2]) > 3 or int(cmd[2]) < 0): #优先级不在0~3之间
        print("Error in cr, please make sure your priority from 0 to 3")
        return False
    elif cmd[0] == "kill":
        if not cmd[1].isdigit():
            print("Error in kill, please use like 'kill 1'")
            return False
        elif int(cmd[1]) == 0: #不能杀掉 pid为0的init进程
            print("Error in kill, init process could not be killed!")
            return False
        elif not getProcessById(int(cmd[1])): #找不到用户输入对应的pid
            print(f"Error in kill, cant't find process {int(cmd[1])}")
            return False
    elif cmd[0] == "req": #参数个数不对或着pid和rid不是数字
        if len(cmd) != 3 or not cmd[1].isdigit() or not cmd[2].isdigit():
            print("Error in req, please use like 'req 1 3'")
            return False
        elif not getProcessById(int(cmd[1])): #找不到pid
            print(f"Error in req, cant't find process {int(cmd[1])}")
            return False
        elif not int(cmd[2]) in range(0, 4): #rid 不在0~3之间
            print(f"Error in req, please input a rid from 0 to 3")
            return False
    elif cmd[0] == "rel":
        if len(cmd) != 3 or not cmd[1].isdigit() or not cmd[2].isdigit():
            print("Error in req, please use like 'rel 1 3'")
            return False
        elif int(cmd[2]) not in getProcessById(int(cmd[1])).resource: #需要释放的资源不在进程占用的资源列表里
            print(f"Error in req, resource{int(cmd[2])} not in process{int(cmd[1])}.resource")
            return False
    return True

def getRunProcess()->Process: #返回正在运行的进程
    global processes
    for i in processes:
        if i.status == "running":
            return i

def getPID()->int: #返回一个pid，供创建的进程初始化
    global pid
    pid = pid + 1
    return pid

def scheduler(): #最终要的调度程序
    global processes, readyQue
    runningProcess = getRunProcess()
    for i in range(3, -1, -1): #从最高优先级的就绪队列开始遍历
        if runningProcess.priority < i and readyQue[i]: #说明比它高优先级的就绪队列非空
            runningProcess.status = "ready"
            readyQue[runningProcess.priority].append(runningProcess)
            runningProcess = readyQue[i].pop(0) #新的runningProcess
            runningProcess.status = "running"
            break
    print(f"* process {runningProcess.name} is running!")
    return

def request(pid:int, rid:int): #为pid进程申请rid资源
    global processes, resources, blockQue, readyQue
    targetProcess = getProcessById(pid)
    if resources[rid].status == "free": #若资源空闲
        resources[rid].usingPid = pid
        resources[rid].status = "allocated"
        if rid in targetProcess.wantRe:
            targetProcess.wantRe.remove(rid) #从愿望清单上删除
        targetProcess.resource.append(rid)
        print(f"* process {targetProcess.name} get resouce{rid} successfully")
    elif resources[rid].status == "allocated": #若资源已被占用
        resources[rid].blockQue.append(pid)
        targetProcess.wantRe.append(rid)
        if targetProcess.status == "running": #若请求资源的进程为正在运行的，则需要加入阻塞队列然后重新调度选出新的运行进程
            targetProcess.status = "block"
            blockQue.append(targetProcess)
            print(f"* process {targetProcess.name} is blocked!   (from running to block)")
            delFromRQById(0) #将init进程从就绪队列中删除，转而成为运行态
            processes[0].status = "running"
            scheduler()
        elif targetProcess.status == "ready": #若请求资源的进程为就绪态，则从就绪队列中删除，加入到阻塞队列中
            targetProcess.status = "block"
            delFromRQById(pid)
            blockQue.append(targetProcess)
            print(f"* process {targetProcess.name} is blocked!   (from ready to block)")
        elif targetProcess.status == "block":
            print(f"* process {targetProcess.name} is blocked!   (from block to block)")

def release(pid:int, rid:int): #为pid进程释放rid资源
    global resources, readyQue
    targetProcess = getProcessById(pid)
    targetProcess.resource.remove(rid) #删除进程中的占用
    resources[rid].usingPid = -1 #删除资源中usingPid
    resources[rid].status = "free"
    print(f"* process {targetProcess.name} releases resource{rid} successfully")
    if resources[rid].blockQue: #如果该资源阻塞了其他的进程
        wakeProcess = getProcessById(resources[rid].blockQue.pop(0))  #由于资源被释放从而唤醒的一个进程
        request(wakeProcess.id, rid) #自动为阻塞队列中的第一个进程申请资源
        if not wakeProcess.wantRe: #如果被唤醒的进程所需要的资源都获得了满足，则加入就绪队列
            wakeProcess.status = "ready"
            delFromBQById(wakeProcess.id)
            readyQue[wakeProcess.priority].append(wakeProcess) #当就绪队列发生改变就需要执行调度程序，因为可能会导致runningprocess发生改变。
            scheduler()
    else: #如果该资源没有阻塞其他进程
        return 
            
def delFromRQById(pid:int): #在就绪队列中删除pid的进程
    global readyQue
    targetProcess = getProcessById(pid)
    readyQue[targetProcess.priority].remove(targetProcess)

def delFromBQById(pid:int): #在阻塞队列中删除pid的进程
    global blockQue
    blockQue.remove(getProcessById(pid))

processes = InitProcess()
resources = InitResources()
blockQue = [] #记录当前哪些进程被阻塞了
readyQue = [[], [], [], []] #就绪队列组，按照优先级分出不同的优先级队列。下标为0的代表优先级为0的就绪队列。默认有0~3，一共4个优先级队列

pid = 0 #不断递增的pid

while(1):
    cmd = input(">")
    if not checkCMD(cmd): #如果格式错误，则让用户重新输入
        continue
    cmd = cmd.split() #根据空格区分
    if cmd[0] == "quit": #quit退出
        print("byebye~")
        break
    elif cmd[0] == "ls": #ls命令包含一系列查看操作 例子ls -p查看所有进程
        if cmd[1] == "-q": #查看就绪队列
            printReadyQue()
        elif cmd[1] == "--run": #查看正在运行的进程
            printRunProcess()
        elif cmd[1] == "-p": #查看所有进程
            printProcesses()
        elif cmd[1] == "-r": #查看所有资源
            printResources()
    elif cmd[0] == "cr": #创建进程  例如 cr A 3 将创建一个优先级为3，名字为A的进程。
        name, priority = cmd[1], int(cmd[2])
        newProcess = Process(getPID(), name, priority) #新的进程直接加入就绪队列即可，然后调用调度程序
        processes.append(newProcess)
        readyQue[priority].append(newProcess)
        print(f"* process {newProcess.name} has been created successfully")
        scheduler() #调用调度程序
    elif cmd[0] == "kill": #杀死进程 例如 kill 1 将杀死pid为1的进程
        pid = int(cmd[1])
        targetProcess = getProcessById(pid)
        for re in targetProcess.resource: #杀死进程时自动释放它占用的资源
            release(pid, re)
        processes.remove(targetProcess)
        print(f"* process {targetProcess.name} has been killed!")
        if targetProcess.status == "running": #如果kill的进程是running的，从processes中删除
            delFromRQById(0)
            processes[0].status = "running" #让init进程来临时当running
            scheduler()
        elif targetProcess.status == "ready": #要kill的进程在就绪队列中
            delFromRQById(pid)
        elif targetProcess.status == "block": #要kill的进程在阻塞队列中
            delFromBQById(pid)
    elif cmd[0] == "req": #请求资源 例如 req 1 3 表示1号进程去申请3号资源
        pid, rid = int(cmd[1]), int(cmd[2]) #re pid, rid的格式，表示pid的进程去请求rid的资源
        request(pid, rid)
    elif cmd[0] == "rel": #释放资源 例如 rel 1 3 表示1号进程将释放其占用的3号资源
        pid, rid = int(cmd[1]), int(cmd[2])
        release(pid, rid)
