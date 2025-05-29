
void main()
{
    int a = 42;
    if (a < 6)
        a *= 4;
    else
        a += 28;

    int b = 4;
    if (a + b > a * 2)
        b -= 50;
    a = a + b;
}
