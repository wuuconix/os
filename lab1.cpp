// proccreate项目
#include <windows.h>
#include <iostream>
#include <stdio.h>
#include <stdlib.h>

// 创建一个进程，运行的是本程序，唯一的变化是nClone
void StartClone(int nCloneID)
{
    // 得到该文件的绝对路径 C:\Users\wuuconix\source\repos\OS1\Debug\OS1.exe
    // 因为控制台为unicode环境。直接用cout只会输出该变量的地址。
    // 利用wcout可以输出
    TCHAR szFilename[MAX_PATH];
    ::GetModuleFileName(NULL, szFilename, MAX_PATH);
    // std::wcout << szFilename << std::endl;
    
    // 得到cmd命令 "C:\Users\wuuconix\source\repos\OS1\Debug\OS1.exe" 2
    // 直接在cmd中输入以上命令即可执行
    // TCHAR 变量使用 sprintf 会在VS中会报错[g++ 手动编译则没有问题]， 这里修改为swprintf
    TCHAR szCmdLine[MAX_PATH];
    ::swprintf(szCmdLine, L"\"%s\" %d", szFilename, nCloneID);
     //::sprintf(szCmdLine, "\"%s\" %d", szFilename, nCloneID);
    //std::wcout << szCmdLine << std::endl;

    // 一个结构体
    // 微软文档： https://docs.microsoft.com/en-us/windows/win32/api/processthreadsapi/ns-processthreadsapi-startupinfoa
    // ZeroMemory() 为 memset((Destination),0,(Length)) 的别名
    STARTUPINFO si;
    ::ZeroMemory(reinterpret_cast <void*> (&si), sizeof(si));
    si.cb = sizeof(si);				// 必须是本结构的大小

    // 返回的用于子进程的进程信息
    PROCESS_INFORMATION pi;

    // 利用同样的可执行文件和命令行创建进程，并赋于其子进程的性质
    BOOL bCreateOK = ::CreateProcess(
        szFilename,					// 产生这个EXE的应用程序的名称
        szCmdLine,					// 告诉其行为像一个子进程的标志
        NULL,						// 缺省的进程安全性
        NULL,						// 缺省的线程安全性
        FALSE,						// 不继承句柄
        CREATE_NEW_CONSOLE,			// 使用新的控制台
        //CREATE_NEW_PROCESS_GROUP,   //不开新窗口
        NULL,						// 新的环境
        NULL,						// 当前目录
        &si,						// 启动信息
        &pi);						// 返回的进程信息

    // 释放进程的句柄
    if (bCreateOK)
    {
        ::CloseHandle(pi.hProcess);
        ::CloseHandle(pi.hThread);
    }
}

int main(int argc, char* argv[])
{
    // int nClone(0) 和 int nClone = 0 效果一致
    // 默认nClone 的值为0
    int nClone(0);
    if (argc > 1)
    {
        // 如果用户通过命令行传参了，则设置为用户设置的值
        // 如 "C:\Users\wuuconix\source\repos\OS1\Debug\OS1.exe" 2
        // 这时 argv[1]为2。nClone将被设置为2
        ::sscanf(argv[1], "%d", &nClone);
    }

    // 显示进程位置
    std::cout << "Process ID:" << ::GetCurrentProcessId()
        << ", Clone ID:" << nClone
        << std::endl;


    // 最大nClone号
    const int c_nCloneMax = 25;
    if (nClone < c_nCloneMax)
    {
        // 将nClone 自增 后调用创建进程函数
        StartClone(++nClone);
    }

    // 在终止之前暂停一下 (l/2秒)

    return 0;
}
