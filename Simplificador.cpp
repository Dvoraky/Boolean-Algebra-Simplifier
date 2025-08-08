#include <iostream>
#include <string>
#include <algorithm>
#include <vector>
#include <cctype>

class Simplificador
{
    public:
        Simplificador() // Construtor
        {
            ler_expressão();
            this -> tamanho = this -> expressão.length();
            ler_variáveis();
        }

    private:
        std::string expressão;
        int tamanho;
        int num_variável = 0;
        std::vector<char> variáveis;

        void ler_expressão() // Lê a expressão e remove os espaços
        {   
            std::string expressão;
            std::cin >> expressão;
            expressão.erase(std::remove(expressão.begin(), expressão.end(), ' '), expressão.end());

            this -> expressão = expressão;
        }

        void ler_variáveis() // Lê a quantidade de variáveis na expressão e salva elas em um vetor
        {
            for(int i = 0; i < this -> tamanho; i++)
            {
                if(std::isalpha(this -> expressão[i]))
                {
                    auto it = std::find(this -> variáveis.begin(), this -> variáveis.end(), this -> expressão[i]);
                    if(it == this -> variáveis.end())
                    {
                        this -> variáveis.push_back(this -> expressão[i]);
                        this -> num_variável++;
                    }
                }
            }
        }

        void Anulação()
        {
            // A0 = 0
            // A + 1 = 1

        }

        void Identidade()
        {
            // A + 0 = A
            // A1 = A

        }

        void idempotência()
        {
            // A + A = A
            // AA = A

        }

        void Complemento()
        {
            // A'A = 0
            // A + 'A = 1

        }

        void DuplaNegação()
        {
            // ''A = A

        }

        void Distributiva()
        {
            // A(B + C) = AB + AC
            // A + (BC) = (A + B)(A + C)

        }

        void Associativa()
        {
            // A + (B + C) = (A + B) + C
            // A(BC) = (AB)C

        }
        
        void Comutativa()
        {
            // A + B = B + A
            // AB = BA
        }

        void Absorção()
        {
            // B + (BA) = B
            // B(B + A) = B
            // A + 'AB = A + B
            // A('A + B) = AB

        }

        void DeMorgan()
        {
            // '(A + B) = 'A'B
            // '(AB) = 'A + 'B
        }

        void Postulados()
        {
            // 0.0 = 0
            // 1.1 = 1
            // 1.0 = 0
            // 0 + 0 = 0
            // 1 + 1 = 1
            // 1 + 0 = 0
            // '1 = 0
            // '0 = 1
        }
}; 

