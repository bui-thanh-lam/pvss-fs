
// g++ -g server.cpp -o server.exe -lgmp

#include <bits/stdc++.h>
#include "gmp.h"

using namespace std;

gmp_randstate_t rand_state;
int first400Prime[400];

struct document{
    char *G, *H; //  base
    // string A[20], B[20]; // coefficients for polynomial function A or B. size = T
    int N; // amount of shareHolder
    int T; // amount of required shareHolders to open Document
    char *P; // prime for modulo
    // string K; // key for document
    char *k[20], *v[20]; // component key for shareHolder. size = N
    char *C[20]; // validate array
};


void generate_random(mpz_t X, mpz_t P){    
    mpz_init(X);
    mpz_urandomm(X, rand_state, P);
}

void generate_random_bits(mpz_t randomNumber, int bits){
    mpz_init(randomNumber);
    mpz_urandomb(randomNumber, rand_state, bits);
}

int check_fermat(mpz_t n){
    mpz_t n_1, powNumber;
    mpz_init(n_1);
    mpz_init_set_ui(powNumber, 2);
    mpz_sub_ui(n_1, n, 1);
    mpz_powm(powNumber, powNumber, n_1, n);
    if (mpz_cmp_ui(powNumber, 1) == 0)
        return 0;
    return 1;
}

int witness(mpz_t a, mpz_t n){
    mpz_t n_1;
    mpz_init(n_1);
    mpz_sub_ui(n_1, n, 1);

    mpz_t u;
    mpz_init(u);
    unsigned long t = 0;
    do{
        t += 1;
        while (mpz_divisible_ui_p(n_1, pow(2, t)) == 0)
            t++;
        mpz_div_ui(u, n_1, pow(2, t));
    } while (mpz_odd_p(u) == 0);
    mpz_t xi, xi_1;
    mpz_init(xi_1);
    mpz_init(xi);
    mpz_powm(xi_1, a, u, n);
    for (int i = 1; i <= t; i++){
        mpz_powm_ui(xi, xi_1, 2, n);
        if ((mpz_cmp_ui(xi, 1) == 0) && (mpz_cmp_ui(xi_1, 1) != 0) && (mpz_cmp(xi_1, n_1) != 0))
            return 1;
        mpz_set(xi_1, xi);
    }
    if (mpz_cmp_ui(xi, 1) != 0)
        return 1;
    return 0;
}

int rabin_Miller(mpz_t n, int s){
    for (int i = 1; i <= s; i++){
        mpz_t a;
        generate_random_bits(a, 16);
        if (witness(a, n) == 1)
            return 1;
    }
    return 0;
}

int check_prime(mpz_t n){
    for (int i = 0; i < 400; i++){
        if (mpz_divisible_ui_p(n, first400Prime[i]) != 0)
            return 1;
    }

    if (check_fermat(n) == 1)
        return 1;

    if (rabin_Miller(n, 64) == 1)
        return 1;
    return 0;
}

void generate_random_prime(mpz_t n, int bits){
    generate_random_bits(n, bits);
    mpz_setbit(n, 0);
    mpz_setbit(n, bits - 1);
    while (check_prime(n) == 1)
        mpz_add_ui(n, n, 2);
}

void generate_P_and_G(mpz_t P, mpz_t G, int bits){
    mpz_t p1, p2;
    generate_random_prime(p1, bits);
    generate_random_prime(p2, bits);
    mpz_mul_ui(p2, p2, 2);
    mpz_mul(P, p1, p2);
    mpz_add_ui(P, P, 1);
    while(true){
        mpz_t g, tmp, tmp1;
        generate_random(g, P);
        mpz_sub_ui(tmp, P, 1);
        if ()
    }

}

void generate_first_400_prime(){
    first400Prime[0] = 2;
    int index = 1;
    while (index < 400){
        int number = first400Prime[index - 1];
        bool isPrime;
        do{
            isPrime = true;
            number += 1;
            for (int i = 2; i < number; i++){
                if (number % i == 0){
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


void generate_function(mpz_t R[], bool is_function_a, mpz_t &K, mpz_t &P, int T){
    /*
    Generate coefficients for polynomial function A or B

    Args:
        is_function_a: boolean. if is_function_a = True -> generate function A
                                else -> generate function B
        K: mpz_t. Key for document. K will be used if is_function_a = True
        P: mpz_t. Prime for modulo
        T: int. T-1 is The degree of function

        R: Array coefficients of the polynomial
    */

    mpz_t tmp;

    gmp_printf("%Zd\n", P);
    gmp_printf("%Zd\n", K);

    if (!is_function_a) mpz_set(R[0], K);
    else {
        generate_random(tmp, P);
        mpz_set(R[0], tmp);
        gmp_printf("%Zd\n", R[0]);
    }

    for(int i = 1; i < T; i++){
        generate_random(tmp, P);
        mpz_set(R[i], tmp);
        gmp_printf("%Zd\n", R[i]);
    }
    mpz_clear(tmp);
}

void calculate_polynomial_value(mpz_t Res, mpz_t Q[], mpz_t P, long int x, int T){

    /*
    calculate value of polynomial Q with x

    Args:
        Q: mpz_t array. Array coefficients of the polynomial
        P: mpz_t. Prime for modulo
        x: long int. Variable value
        T: int. Size of Q

        Res: mpz_t. Value of polynomial at x
        Res = sum(Q[i]*x^i)
    */
    mpz_t X;

    mpz_init(Res);
    mpz_add(Res, Res, Q[0]);
    mpz_mod(Res, Res, P);

    mpz_set_si(X, x);
    for(int i = 1; i < T; i++){
        mpz_t tmp;
        mpz_mul(tmp, Q[i], X);
        mpz_mod(tmp, tmp, P);

        mpz_add(Res, Res, tmp);
        mpz_mod(Res, Res, P);

        mpz_mul_si(X, X, x);
        mpz_mod(X, X, P);
    }
    mpz_clear(X);
}

void calculate_C(mpz_t C[], mpz_t A[], mpz_t B[], mpz_t G, mpz_t H, mpz_t P, int T){
    /*
    calculate Ci to verify key

        ci = g^Ai * h^Bi mod P

    Args:
        A, B: mpz_t array. Array coefficients of polynomial A, B
        G, H: mpz_t. base
        T: int. size of A, B

    Returns:
        C: mpz_t array. array Ci

    */
    mpz_t tmp1;
    mpz_t tmp2;
    for (int i = 0; i < T; i++){

        mpz_powm(tmp1, G, A[i], P);
        mpz_powm(tmp2, H, B[i], P);

        mpz_mul(C[i], tmp1, tmp2);
        mpz_mod(C[i], C[i], P);
    }

    mpz_clear(tmp1);
    mpz_clear(tmp2);
}

document PVSS1(char* key,  int N, int T){

    /*
    Generate key for each shareHolder

    Args:
        key: string. Key for document
        N: int. Amount of shareHolders
        T: int. Amount of required shareHolders to open Document

    Returns:
        D: document. Information for the document
    */

    document D;
    D.N = N; D.T = T;
    mpz_t K;
    mpz_init_set_str(K, key, 16);


    // gen P
    mpz_t P;
    generate_random_prime(P, 1024);
    D.P =  mpz_get_str(D.P, 16, P);

    // gen G

    // gen H

    // D.H = H;

    mpz_t A[T], B[T];

    generate_function(A, true, P, K, T);

    mpz_t tmp;
    mpz_init(tmp);
    generate_function(B, false, tmp, prime, T);
    mpz_clear(tmp);


    mpz_t k[N+2], v[N+2];
    for(int i = 1; i <= N; i++){
        calculate_polynomial_value(k[i], A, prime, (long int)i, T);
        calculate_polynomial_value(v[i], B, prime, (long int)i, T);
        D.k[i] = mpz_get_str(D.k[i], 16, k[i]);
        D.v[i] = mpz_get_str(D.v[i], 16, v[i]);
    }

    mpz_t h, g;
    // mpz_init_set_str(h, H, 16);
    generate_random(g, prime);
    D.G = mpz_get_str(D.G, 16, g);

    mpz_t C[T];
    calculate_C(C, A, B, g, h, prime, T);

    mpz_clear(h);
    mpz_clear(g);
    mpz_clear(prime);
    mpz_clear(key);
    for(int i = 0; i <= N; i++){
        if (i < T){
            mpz_clear(A[i]);
            mpz_clear(B[i]);
            D.C[i] = mpz_get_str(D.C[i], 16, C[i]);
            mpz_clear(C[i]);
        }
        mpz_clear(k[i]);
        mpz_clear(v[i]);
    }

    return D;
}

bool verification(mpz_t key[], mpz_t verify[], int x[], int T){
    /*
    verify T key is correct

    Args:
        key, verify: mpz_t. Array component key of T shareHolder
        x: int. Array index corresponding each shareHolder
        T: int. amount of shareHolders who want to open the Document

    Returns:
        True if all component keys are correct
        False for otherwise

        g^k[i]  * h^t[i] =  sum(c[j]^(x[i]^j))

    */
    return false;

}

char* PVSS2(document D, char* K[], char* V[], int x[], int T){

    /*
    Recreate Key from T component Key

    Args:
        D: document. Information for the document
        K,V: string array. shareHolders's Key
        x: int array. array index corresponding each shareHolder
        T: int. amount of shareHolders who want to open the Document

    Returns:
        KEY: string. Key of Document
    */
   
    mpz_t key[T];
    mpz_t verify[T];
    for(int i = 0; i < T; i++){
        mpz_init_set_str(key[i], K[i], 16);
        mpz_init_set_str(verify[i], V[i], 16);
    }

    if (!verification(key, verify, x, T)){
        char *tmp;
        tmp = (char*)"Incorrect component keys!";
        return tmp;
    }

    mpz_t prime;
    mpz_init_set_str(prime, D.P, 16);
    mpz_t Key;

    // do something

    char* KEY;
    KEY = mpz_get_str(KEY, 16, Key);

    for(int i = 0; i < T; i++){
        mpz_clear(key[i]);
        mpz_clear(verify[i]);
    }
    mpz_clear(prime);
    mpz_clear(Key);

    return KEY;
}

main(){
    freopen("server.txt", "w", stdout);
    document D;

    init();

    char* K;    
    K = (char*)"1247981537862551155466699485222265446644533355665481";

    int N = 15;
    int T = 5;
    D = PVSS1(K, N, T);
    // for(int i=0; i < T; i++)
    //     cout << D.C[i] <<"\n";
}
