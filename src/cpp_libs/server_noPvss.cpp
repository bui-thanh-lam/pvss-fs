#include <bits/stdc++.h>
#include "gmp.h"

using namespace std;

gmp_randstate_t rand_state;
int first400Prime[400];

struct KeyComponent
{
    char *k;
    int x;
};

struct KeyComponent_mpz
{
    mpz_t k;
    int x;
};

struct KeySharing
{
    // string A[20], B[20]; // coefficients for polynomial function A or B. size = T
    int N;   // amount of shareHolder
    int T;   // amount of required shareHolders to open Document
    char *p; // prime for modulo
    // string K; // key for document
    KeyComponent *key_component; // component key for shareHolder. 1 -> N
};

void generate_random(mpz_t X, mpz_t P)
{
    mpz_init(X);
    mpz_urandomm(X, rand_state, P);
}

void generate_random_bits(mpz_t randomNumber, int bits)
{
    mpz_init(randomNumber);
    mpz_urandomb(randomNumber, rand_state, bits);
}

int check_fermat(mpz_t n)
{
    mpz_t n_1, powNumber;
    mpz_init(n_1);
    mpz_init_set_ui(powNumber, 2);
    mpz_sub_ui(n_1, n, 1);
    mpz_powm(powNumber, powNumber, n_1, n);
    if (mpz_cmp_ui(powNumber, 1) == 0)
        return 0;
    return 1;
}

int witness(mpz_t a, mpz_t n)
{
    mpz_t n_1;
    mpz_init(n_1);
    mpz_sub_ui(n_1, n, 1);

    mpz_t u;
    mpz_init(u);
    unsigned long t = 0;
    do
    {
        t += 1;
        while (mpz_divisible_ui_p(n_1, pow(2, t)) == 0)
            t++;
        mpz_div_ui(u, n_1, pow(2, t));
    } while (mpz_odd_p(u) == 0);
    mpz_t xi, xi_1;
    mpz_init(xi_1);
    mpz_init(xi);
    mpz_powm(xi_1, a, u, n);
    for (int i = 1; i <= t; i++)
    {
        mpz_powm_ui(xi, xi_1, 2, n);
        if ((mpz_cmp_ui(xi, 1) == 0) && (mpz_cmp_ui(xi_1, 1) != 0) && (mpz_cmp(xi_1, n_1) != 0))
            return 1;
        mpz_set(xi_1, xi);
    }
    if (mpz_cmp_ui(xi, 1) != 0)
        return 1;
    return 0;
}

int rabin_Miller(mpz_t n, int s)
{
    for (int i = 1; i <= s; i++)
    {
        mpz_t a;
        generate_random_bits(a, 16);
        if (witness(a, n) == 1)
            return 1;
    }
    return 0;
}

int check_prime(mpz_t n)
{
    for (int i = 0; i < 400; i++)
    {
        if (mpz_divisible_ui_p(n, first400Prime[i]) != 0)
            return 1;
    }

    if (check_fermat(n) == 1)
        return 1;

    if (rabin_Miller(n, 64) == 1)
        return 1;
    return 0;
}

void generate_random_prime(mpz_t n, int bits)
{
    generate_random_bits(n, bits);
    mpz_setbit(n, 0);
    mpz_setbit(n, bits - 1);
    while (check_prime(n) == 1)
        mpz_add_ui(n, n, 2);
}

void generate_first_400_prime()
{
    first400Prime[0] = 2;
    int index = 1;
    while (index < 400)
    {
        int number = first400Prime[index - 1];
        bool isPrime;
        do
        {
            isPrime = true;
            number += 1;
            for (int i = 2; i < number; i++)
            {
                if (number % i == 0)
                {
                    isPrime = false;
                    break;
                }
            }
        } while (!isPrime);
        first400Prime[index] = number;
        index += 1;
    }
}

void init()
{
    gmp_randinit_mt(rand_state);
    gmp_randseed_ui(rand_state, (unsigned long)time(0));
    generate_first_400_prime();
}

void generate_function_K(mpz_t a[], mpz_t p, int T)
{
    /*
    Generate coefficients for polynomial function K(x) = a0 + a1.x^1 + .... at-1.x^t-1

    Args:
        P: mpz_t. Prime for modulo
        T: int. T-1 is The degree of function

        a[]: Array coefficients of the polynomial
    */
    for (int i = 1; i < T; i++)
    {
        generate_random(a[i], p);
    }
}
void calculate_value_of_function(mpz_t res, mpz_t a[], mpz_t p, int T, int x)
{
    mpz_add(res, res, a[0]);
    mpz_mod(res, res, p);
    for (int i = 1; i < T; i++)
    {
        mpz_t temp;
        mpz_init(temp);
        mpz_ui_pow_ui(temp, x, i);
        mpz_mul(temp, a[i], temp);
        mpz_add(res, res, temp);
        mpz_mod(res, res, p);
        mpz_clear(temp);
    }
}
void calculate_Ki(mpz_t k[], mpz_t a[], mpz_t p, int N, int T)
{
    /*
    Calculate the value of ki = K(xi) with xi = i, i = 1...n

    Args:
        P: mpz_t. Prime for modulo
        N: the number of shareholder

        a[]: Array value of Ki
    */

    for (int i = 0; i < N; i++)
    {
        mpz_init(k[i]);
        calculate_value_of_function(k[i], a, p, T, i + 1);
    }
}

KeySharing create_key_sharing(mpz_t k[], mpz_t p, int N, int T)
{
    KeySharing keySharing;
    keySharing.key_component = new KeyComponent[N];
    for (int i = 0; i < N; i++)
    {
        KeyComponent KeyComponent;
        KeyComponent.x = i + 1;
        KeyComponent.k = mpz_get_str(NULL, 16, k[i]);
        keySharing.key_component[i] = KeyComponent;
    }
    keySharing.N = N;
    keySharing.T = T;
    keySharing.p = mpz_get_str(NULL, 16, p);
    return keySharing;
}
KeySharing _key_sharing_phase(char *S, int N, int T)
{
    init();
    mpz_t p;
    generate_random_prime(p, 256);
    mpz_t a[T];
    mpz_t k[N];

    mpz_init_set_str(a[0], S, 16);
    gmp_printf("S = %Zd\n", a[0]);
    generate_function_K(a, p, T);
    calculate_Ki(k, a, p, N, T);
    // for (int i = 0; i < N; i++)
    // {
    //     gmp_printf("xi = %d ki = %Zd\n", i+1, k[i]);
    // }
    return create_key_sharing(k, p, N, T);
}

char* _key_reconstruction_phase(KeySharing keySharing)
{
    int T = keySharing.T;
    mpz_t p;
    mpz_init_set_str(p, keySharing.p, 16);
    KeyComponent_mpz k_mpz[T];
    for (int i = 0; i < T; i++)
    {
        mpz_init_set_str(k_mpz[i].k, keySharing.key_component[i].k, 16);
        k_mpz[i].x = keySharing.key_component[i].x;
        // gmp_printf("xi = %d ki = %Zd\n", k_mpz[i].xi, k_mpz[i].ki);
    }

    mpz_t S;
    mpz_init(S);
    for (int j = 0; j < T; j++)
    {
        mpz_t vj;
        mpz_init(vj);

        int xj;
        xj = k_mpz[j].x;

        mpz_t sj;
        mpz_init_set(sj, k_mpz[j].k);

        // gmp_printf("xj = %d Sj = %Zd\n", xj, sj);
        mpz_t numerator;
        mpz_init_set_ui(numerator, 1);
        mpz_t denominator;
        mpz_init_set_ui(denominator, 1);
        for (int k = 0; k < T; k++)
        {
            if (k != j)
            {
                int xk;
                xk = k_mpz[k].x;
                mpz_mul_ui(numerator, numerator, xk);
                mpz_t tmp;
                mpz_init(tmp);
                int sub = xk - xj;
                if (sub < 0)
                {
                    sub = -sub;
                    mpz_sub_ui(tmp, p, sub);
                }
                else
                {
                    mpz_set_ui(tmp, sub);
                }
                // gmp_printf("pre tmp = %Zd\n",tmp);
                mpz_invert(tmp, tmp, p);
                // gmp_printf("after tmp = %Zd\n",tmp);
                mpz_mul(denominator, denominator, tmp);
                mpz_clear(tmp);
            }
        }
        mpz_mul(vj, numerator, denominator);
        mpz_mul(vj, sj, vj);
        mpz_add(S, S, vj);
        mpz_mod(S, S, p);

        mpz_clear(sj);
        mpz_clear(vj);
        mpz_clear(numerator);
        mpz_clear(denominator);
    }
    mpz_clear(p);
    for (int i = 0; i < T; i++)
    {
        mpz_clear(k_mpz[i].k);
    }
    gmp_printf("S = %Zd\n", S);
    return mpz_get_str(NULL, 16, S);
}
// g++ -fPIC -shared -o Server_Lib.so server_noPvss.cpp - lgmp
extern "C"{
    KeySharing key_sharing_phase(char* S, int N, int T){
        return _key_sharing_phase(S, N, T);
    }
    char* key_reconstruction_phase(KeySharing keySharing){
        return _key_reconstruction_phase(keySharing);
    }
}
// main()
// {
//     // g++ -g server_noPvss.cpp -o server_noPvss.exe -lgmp
//     char *S = (char *)"7DC7F1D3377048287B1C1C69C846A8DF";
//     // char *S = (char *)"A";
//     int N = 300;
//     int T = 150;
//     KeySharing key = key_sharing_phase(S, N, T);
//     cout << key.p << endl;
//     cout << key_reconstruction_phase(key) << endl;
// }
