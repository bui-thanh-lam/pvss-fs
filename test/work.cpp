#include <math.h>
#include <bits/stdc++.h>
#include "gmp.h"

// g++ -fPIC -shared -o work_libsample.so work.cpp  -lgmp

using namespace std;

void _printHello(){
    gmp_printf("Hello World \n");
}
int _gcd(int x, int y)
{
	int g = y;
	while (x > 0)
	{
		g = x;
		x = y % x;
		y = g;
	}
	return g;
}

int _divide(int a, int b, int * remainder)
{
	int quot = a / b;
	*remainder = a % b;
	return quot;
}

double _avg(double * a, int n)
{
	int i;
	double total = 0.0;
	for (i = 0; i < n; i++)
	{
		total += a[i];
	}
	return total / n;
}

typedef struct Point
{
	double x, y;
} Point;

double _distance(Point * p1, Point * p2)
{
	return hypot(p1->x - p2->x, p1->y - p2->y);
}

void _functionTestGmp()
{
    mpz_t n, a, a_pow2, x, p, q, check;

    //init
    mpz_init_set_str(n, "179769313486231590772930519078902473361797697894230657273430081157732675805505620686985379449212982959585501387537164015710139858647833778606925583497541085196591615128057575940752635007475935288710823649949940771895617054361149474865046711015101563940680527540071584560878577663743040086340742855278549092581", 10);
    mpz_init(a);
    mpz_init(x);
    mpz_init(a_pow2);
    mpz_init(p);
    mpz_init(q);
    mpz_init(check);

    //calculate
    mpz_sqrt(a, n); // a = can n
    int i = 0, cmp;
    do
    {
        mpz_add_ui(a, a, 1);      // a = a+1
        mpz_pow_ui(a_pow2, a, 2); // a = a^2
        mpz_sub(x, a_pow2, n);    // x = a^2-n
        mpz_sqrt(x, x);           // x = can x
        mpz_sub(p, a, x);         // p = a-x
        mpz_add(q, a, x);         // p = a+x
        mpz_mul(check, p, q);     // check = p*q
        cmp = mpz_cmp(n, check);
        i += 1;
    } while (cmp != 0);
    gmp_printf("%Zd\n", p);
    gmp_printf("%Zd\n", q);
    cout << "thoa man p*q = n sau " << i << " buoc lap" << endl;
}

void _printString(string s){
    cout<<"String: "<<s<<endl;
}

void _printStringArray(string array[], int n){
    for(int i = 0; i < n; i++){
        cout<<"string "<<i<<": "<<array[i]<<endl;
    }
}


extern "C"{
    void printHello(){
        _printHello();
    }
    int gcd(int x, int y){
        return _gcd(x, y);
    }
    int divide(int a, int b, int *remainder){
        return _divide(a,b,remainder);
    }
    double avg(double *a,int n){
        return _avg(a, n);
    }
    double distance(Point * p1, Point * p2){
        return _distance(p1, p2);
    }
    void functionTestGmp(){
        _functionTestGmp();
    }
    void printString(char *s){
        string str(s);
        _printString(str);
    }
    void printStringArray(char **s, int n){
        string *array = new string[n];
        for(int i = 0; i < n; i++){
            string str(s[i]);
            array[i] = str;
        }
        _printStringArray(array, n);
    }
}