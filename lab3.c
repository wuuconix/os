#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#define BUF 2048
#define TESTNUM 1

struct freeMem
{
    int start; //分区始址， 即下标
    int length; //分区大小
    struct freeMem *last;
    struct freeMem *next;
};

int nodeIndex(struct freeMem *head, struct freeMem *node) //计算某节点在链表中的位置，不算头节点 ，认为第一个节点的下标为0
{
    struct freeMem *next = head->next;
    int index = 0;
    while (next->start != node->start)
    {
        next = next->next;
        index++;
    }
    return index;        
}

void displayNode(struct freeMem *head, struct freeMem *node) //可视化输出节点
{
    if (node == NULL)
        printf("it is NULL\n");
    else
    {
        printf("id         start       length\n");
        printf("%2d          %4d          %2d\n", nodeIndex(head, node), node->start, node->length);
    }
}

void displayLinks(struct freeMem *head) //可视化输出链表
{
    printf("id         start       length\n");
    struct freeMem *next = head->next;
    while (next != NULL)
    {
        printf("%2d          %4d          %3d\n", nodeIndex(head, next), next->start, next->length);
        next = next->next;
    }
}

struct freeMem *getNodeN(struct freeMem *begin, int n)  //返回链表中第N个节点，不算头节点 ，认为第一个节点的下标为0
{
    struct freeMem *next = begin->next;
    int index = 0;
    while (index < n)
    {
        next = next->next;
        index++;         
    }
    return next;
}

int linkLength(struct freeMem *head) //统计链表一共有几个节点
{
    int n = 0;
    struct freeMem *next = head->next;
    while (next != NULL)
    {
        n++;
        next = next->next;
    }
    return n;
}

int mem_release(struct freeMem *head) //随机挑选一片占用区域释放 返回值0表示失败，1表示成功
{
    int choice = rand() % 4;
    int randomOrder = rand() % linkLength(head);
    int lastOrder = 0; //代表不是最后一个节点
    if (randomOrder == linkLength(head) - 1) //最后一个节点，无后继节点
    {
        lastOrder = 1;
        choice = rand() % 2; //若是最后一个节点则 只能开一个新或者与最后的节点合并
    }
    printf("现在要在%d 节点前后开启 %d号计划\n", randomOrder, choice);
    struct freeMem *node =  getNodeN(head, randomOrder);
    struct freeMem *new = NULL;
    int start, end, dec; //switch里要用，而switch里不能定义变量，只能对变量进行修改。
    switch (choice)
    {
    case 0: //单独开一个空闲分区
        new = (struct freeMem*)malloc(sizeof(struct freeMem));
        start = 2, end = 1;
        while (start > end)
        {
            if (lastOrder == 1)
            {
                if ((node->start + node->length + 1) >= 2047) //说明已经不能再开新空间了
                    return 0;
                else
                {   
                    start = (node->start + node->length + 1) + rand() % (BUF - 1  - (node->start + node->length + 1));
                    end = (node->start + node->length + 1) + rand() % (BUF - 1 - (node->start + node->length + 1));
                }

            }
            else
            {
                start = (node->start + node->length + 1) + rand() % (node->next->start - 1 - (node->start + node->length + 1));
                end = (node->start + node->length + 1) + rand() % (node->next->start - 1 - (node->start + node->length + 1));
            }
        }
        new->start = start;
        new->length = end - start + 1;
        new->last = node;
        new->next = node->next;
        node->next = new;
        if (lastOrder == 0)
            new->next->last = new;
        break;
    case 1:  //与上一个空闲区与合并
        if (lastOrder == 1)
            node->length = node->length + (rand() % (BUF - 1 - node->start - node->length));
        else
            node->length = node->length + (rand() % (node->next->start - node->start - node->length));
        break;
    case 2: //与下一个空闲分区合并
        dec = rand() % (node->next->start - (node->start + node->length));         //1  2,   6  2
        node->next->start -= dec;
        node->next->length += dec;
        break;
    case 3: //将前后两个空闲区域合并
        node->length = (node->next->start - node->start) + node->next->length;
        node->next = node->next->next;
        break;
    }
    return 1;
}

double memUsage(struct freeMem *head) //计算内存占用率
{
    struct freeMem *next = head->next;
    int freeBlock = 0;
    while (next != NULL)
    {
        freeBlock += next->length;
        next = next->next;
    }
    return (1.0 - (double)freeBlock / BUF);
}

struct freeMem *mem_request(struct freeMem *begin, int n)  //返回第一个可以装下n的空闲分区对应的节点指针，NULL表示找不到
{
    struct freeMem *next = begin->next;
    while (next != NULL)
    {
        if (next->length >= n)
            return next;
        else
            next = next->next;            
    }
    return NULL;
}

struct freeMem *genLinkBF(struct freeMem *head)  //生成按照空闲块数递增的链表
{
    struct freeMem *headL = (struct freeMem*)malloc(sizeof(struct freeMem));
    headL->last = NULL;

    int *a = (int *)malloc(sizeof(int) * linkLength(head));
    for (int i = 0; i < linkLength(head); i++)
        a[i] = i; //初始化
    for (int i = 0; i < linkLength(head); i++)
    {
        int min = i;
        for (int j = i + 1; j < linkLength(head); j++)
        {
            if (getNodeN(head, a[j])->length < getNodeN(head, a[min])->length)
                min = j;
        }
        int temp;
        temp = a[i];
        a[i] = a[min];
        a[min] = temp;
    }

    struct freeMem *last = headL;
    for (int i = 0; i < linkLength(head); i++)
    {
        struct freeMem *new = (struct freeMem*)malloc(sizeof(struct freeMem));
        new->start = getNodeN(head, a[i])->start;
        new->length = getNodeN(head, a[i])->length;
        new->last = last;
        new->next = NULL;
        last->next = new;
        last = new;
    }
    return headL;
}

int main()
{
    int strategy;
    printf("请选择内存分配策略： (0) FF  (1) BF:  ");
    scanf("%d", &strategy);

    srand(time(0));
    int index = 0;
    struct freeMem *headFF = (struct freeMem*)malloc(sizeof(struct freeMem)); //开始节点，不写数据 根据地址递增的链表 FF所用链表
    headFF->last = NULL;
    struct freeMem *last = headFF; //用来定位上一个节点
    
    while (index < BUF) //随机生成空闲表的表项
    {
        int length = rand() % 200 + 1; //空闲表
        if (index + length >= BUF) //直到直接被选择为占用或者length 小于剩余 空间
            continue;
        struct freeMem *tmp = (struct freeMem*)malloc(sizeof(struct freeMem));
        tmp->start = index;
        tmp->length = length;
        tmp->last = last;
        tmp->next = NULL;
        last->next = tmp;
        last = tmp;
        index += length;

        length = rand() % 200 + 1; //随机占用
        index += length;
    }

    struct freeMem *headBF = genLinkBF(headFF); //根据空闲块数递增的链表，用以BF策略
    struct freeMem * head = (strategy == 0) ? headFF : headBF;

    printf("初始空闲分区\n");
    displayLinks(head);
    printf("---------------\n");
    for (int i = 0; i < TESTNUM; i++)
    {
        printf("round%d\n", i);
        while(1)
        {
            int requestBlock = rand() % 200 + 1;
            printf("现在开始寻找大于%d的分区\n", requestBlock);
            struct freeMem *target = mem_request(head, requestBlock);
            if (target != NULL)
            {
                printf("找到分区%d\n", nodeIndex(head, target));
                target->length -= requestBlock;
                if (strategy == 1)
                {
                    getNodeN(headFF, nodeIndex(headFF, target))->length = target->length; //同步FF链表
                    head = genLinkBF(head); //重新排序
                }
                displayLinks(head); //每次
            }
            else
            {
                printf("找不到了\n");
                break;
            }
        }
        displayLinks(head);
        printf("内存占用率：%.4lf\n", memUsage(head));
        while(1)
        {
            if (mem_release(headFF))
            {
                headBF = genLinkBF(headFF);
                break;
            }
            sleep(1);
        }
        printf("----------------------------\n");
    }

    return 0;
}