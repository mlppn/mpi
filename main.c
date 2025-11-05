#include <stdio.h>
#include "add.h"

int main(void) {
    int x = 17;
    int y = 25;
    printf("%d + %d = %d\n", x, y, add(x, y));
    return 0;
    }