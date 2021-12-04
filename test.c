#include <stdio.h>
#include <stdlib.h>
#include <time.h>

int main()
{

    srand(time(0));
    int n = 0;
    while (n < 100)
    {
        printf("%d\n", rand() % 2);
    }
    return 0;
}