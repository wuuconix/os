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

def findProcess(processes, pid): #根据pid从列表中找到进程对象并返回
    for i in processes:
        if i.id == pid:
            return i
    return None

def chooseRun(readyQue): #选择当前就绪队列中优先级最高的且最先到的进程来运行
    index, que = 3, readyQue[3]
    while len(que) == 0:
        index -= 1
        que = readyQue[index]
    return que.pop(0)

resources = [Resource(i) for i in range(0, 5)] #resources表示所有的资源列表，一共5个资源，rid分别为0~4
processes = [] #存储现在所有的进程
readyQue = [[], [], [], []] #就绪队列组，按照优先级分出不同的优先级队列。下标为0的代表优先级为0的就绪队列。默认有0~3，一共4个优先级队列
blockQue = [] #记录当前哪些进程被阻塞了
initProcess = Process(0, "Init", 0) #按照实验指导要求生成一个0优先级的init进程
processes.append(initProcess)
runningProcess = initProcess
pid = 1
while(1):
    cmd = input(">")
    if cmd == "":
        continue
    cmd = cmd.split()
    if cmd[0] == "quit":
        break
    elif cmd[0] == "ls" and cmd[1] == "-q":
        print("running process:\n" + " " * 12 + f"pid: {runningProcess.id} name: {runningProcess.name}\n-------------")
        for i in range(len(readyQue) - 1, -1, -1):
            que = readyQue[i]
            if len(que) == 0:
                print(f"readyQue[{i}] is empty")
            else:    
                print(f"readyQue[{i}] has {len(que)} processes:")
                for process in que:
                    print(" " * 12 + f"pid: {process.id} name: {process.name}")
    elif cmd[0] == "ls" and cmd[1] == "-p":
        print(f"now existing {len(processes)} process")
        for i in processes:
            print(f"pid: {i.id}  name: {i.name}  priority: {i.priority}  status: {i.status}  resource: {i.resource}")
    elif cmd[0] == "ls" and cmd[1] == "-r":
        for i in resources:
            print(f"rid: {i.id}  status: {i.status}  blockQue: {i.blockQue}")
    elif cmd[0] == "cr": #创建进程的模拟命令
        if len(cmd) != 3:
            print("illegle input!")
            continue
        name, priority = cmd[-2], int(cmd[-1]) #priority需要为整型
        if priority > 3 or priority < 0:
            print("优先级输入有误， 请输入0~3作为优先级!")
            continue
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
    elif cmd[0] == "kill":
        if len(cmd) != 2:
            print("illegle input!")
            continue
        if not cmd[-1].isdigit():
            print("please kill a process using pid")
            continue
        pid = int(cmd[-1]) # 利用pid来删除进程
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
    elif cmd[0] == "req": #请求资源
        if not len(cmd) == 3:
            print("illegle input!")
            continue
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
    else:
        print("illegle input!")
        continue    



