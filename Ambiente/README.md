# Ambiente

A __ferramenta__ utilizada para resolver os problemas de maratona deve ser __rápida__, pois uma solução deve respeitar os limites de tempo e memória, e deve ser de __fácil utilização__, para que o processo de transformação da sua ideia em um programa funcional seja simples.

A linguagem de programação [C++](https://pt.wikipedia.org/wiki/C%2B%2B) é muito utilizada no âmbito da programação competitiva, por ser uma linguagem rápida e com muitas ferramentas que auxiliam o competidor a resolver os problemas.

Apesar de ser muito utilizada, o __C++__ nem sempre é a melhor escolha na hora de resolver uma questão, visto que linguagens como __Python__ e __Java__ possuem ferramentas específicas que podem facilitar quem as usa a resolver as questões com maior facilidade. Para facilitar o processo de aprendizado é recomendado que por hora utilize o C++ como ferramenta principal para resolver os problemas.

## Template


```cpp
#include <bits/stdc++.h>
using namespace std;

int main(){
	// Insira seu código aqui.

	return 0;
}
```

Esse é o template de um programa escrito em C++, a primeira linha inclui uma [biblioteca](https://pt.wikipedia.org/wiki/Biblioteca_(computa%C3%A7%C3%A3o)) que possui diversas [ferramentas](https://pt.wikipedia.org/wiki/Standard_Template_Library) úteis, a segunda linha facilita a sintaxe da linguagem. A função main é o ponto de partida para a execução do seu programa.

## Compilação

Caso você não tenha o g++ instalado, basta digitar:
```bash
sudo apt-get install g++
```

Para compilar seu programa basta abrir o terminal no diretório onde seu programa se encontra e digitar:
```bash
g++ -std=c++11 arquivo.cpp
```
Com -std=c++11 estamos utilizando a versão 11 do C++, e lembre-se de mudar arquivo para o nome do arquivo do seu programa.


O g++ gerou um arquivo executável com o seu programa chamado a.out, para executa-lo basta digitar:
```bash
./a.out
```

## Importante

É importante lembrar que a linguagem C++ é uma extensão da __linguagem C__, isso significa que funções que são utilizadas no C como printf e scanf podem ser utilizadas em um programa escrito em C++.

# Iniciante

## Entrada e Saída

As funções de entrada e saída do c++ são o __cin__ e o __cout__.

```cpp
int x;
cin >> x;
```
A primeira linha declara uma variável chamada x que armazena um número inteiro.
A segunda linha espera até que o usuário digite um número inteiro na entrada padrão para ser coletado e armazenado na variável x.


```cpp
cout << "Hello World!\n"; 
cout << x << '\n';
```
A mensagem Hello World! seguido de uma quebra de linha será mostrado na tela.
Logo após a será mostrado na tela o valor da variável x coletada mais cedo.

__Importante:__ repare que a orientação das [setinhas](https://www.inf.pucrs.br/~pinho/PRGSWB/Streams/streams.html) é diferente nas duas funções.


# Intermediário


# Avançado

Adicionar mais coisas
