# BOCA #

O [BOCA](http://www.ime.usp.br/~cassio/boca/) é um sistema de administração de competições de programação. A forma mais simples de instalá-lo é usando pacotes DEB: [https://github.com/maratona-linux](https://github.com/maratona-linux) (é uma boa ideia ver [esta discussão](https://groups.google.com/forum/#!msg/boca-users/W2x3lRivUWs/F-S9CIrjAQAJ)).

## _Contest_ ##

Uma competição (_contest_) envolve uma série de arquivos para, basicamente, 3 funcionalidades:

1. gerar a prova;
2. gerar os arquivos para execução dos testes das submissões no BOCA; e
3. gerar os arquivos de usuários.

Para agilizar este processo, utilize os arquivos descritos a seguir.

### `problems.py3` ###

```bash
# Ver a documentação
python problem.py3 -h

# Criar um problema
python problem.py3 0 parouimpar -s py3
```

Este programa gera o esqueleto para criação de um problema dentro de um diretório que agrupa problemas com características similares:

```
problems
    `- característica
           `- problema
                  |- input/                (para os casos de teste)
                  |- output/               (para os resultados esperados)
                  |- geninput.py3          (programa para gerar a os dados de teste)
                  |- problema.py3          ([opcional] arquivo para solução Python)
                  `- problema.tex          (arquivo com a contextualização do problema)
```
Uma vez criada a estrutura, é preciso preencher o arquivo `problema.tex` com a descrição do problema e definição do formato de entrada e saída de dados. Veja a classe [`MaratonaUnB`](templates/tex/MaratonaUnB.cls) para mais detalhes. O passo seguinte é criar uma série de casos de testes para avaliar uma solução para este problema, conforme as definições. A melhor forma de fazer isto é com um programa que gere casos aleatórios (já no diretório `input`), tomando cuidado para forçar o teste das condições de contorno (ou casos especiais de interesse). A seguir, crie um programa que solucione o problema (conforme as especificações) e gerar a saída adequada para os casos de teste gerados; cada arquivo de saída (no diretório `output`) está associado a um arquivo de entrada (em `input`). Para agilizar este processo, utilize o programa [`io.py3`](io.py3).

```bash
# Ver a documentação
python io.py3 -h

# Criar entradas de um problema
python io.py3 in problems/1/parouimpar/geninput.py3

# Criar saídas de um problema
python io.py3 out problems/1/parouimpar/parouimpar.py3
```

A classe [`MaratonaUnB.cls`](templates/tex/MaratonaUnB.cls) define o comando `\Exemplo`, que carrega (verbatim) o conteúdo de um arquivo de exemplo (entrada e saída), portanto atenção para criar exemplos significativos (e utilizá-los na descrição do problema).

Por fim, é preciso verificar a questão de limites de tempo de execução e atualizar tanto os arquivos no diretório `limits` do problema (caso os limites sejam diferentes dos valores padrões do BOCA definidos em [`templates/boca/limits`](templates/boca/limits)) quanto o `problema.tex`. O `io.py3` já lida com isso automaticamente.

Caso deseje sobrepor alguma configuração para o seu problema, basta incluir o diretório adequado com a configuração específica no diretório do seu problema (como é feito com os diretórios `ìnput` e `output`). Por exemplo, substituir os limites de tempo para Java:

```
problems
    `- característica
           `- problema
                  |- input/
                  |- limits/
                  |    `- java             (limite de tempo específicos para java)
                  `- output/
```

### `contest.py3` ###

Um _contest_ é feito para o BOCA, portanto os problemas devem ser estruturados em 8 diretórios:

```
- problema
      |- compare
      |- compile
      |- description
      |- input
      |- limits
      |- output
      |- run
      `- test
```

Este programa gera um arquivo TeX listando os problemas (veja [`MaratonaUnB`](templates/tex/MaratonaUnB.cls)), gera um arquivo PDF para a prova, configura um diretório `description` para cada problema e cria um arquivo ZIP para ser utilizado no BOCA.

```bash
# Ver a documentação
python contest.py3 -h

# Gerar um contest com problemas
python contest.py3 parouimpar fizzbuzz
```

É possível que se deseje criar um _contest_ com problemas aleatórios, o que é feito com a opção `-r`. Neste caso, o programa escolhe um problema aleatório dentro de cada diretório (dentro de [`problems`](problems)) dado como argumento. Espera-se que um diretório represente uma característica marcante de cada problema dentro dele. No caso, cada diretório representa o nível de dificuldade do problema, e o comando a seguir gera os arquivos considerando dois problemas de nível `0`, um de nível `1` e um de nível `2`. A ordem em que são apresentados no _contest_ também é aleatória.

```bash
# Gerar um contest com problemas aleatórios
python contest.py3 -r 2 0 1 0
```

Para obter os códigos RBG das cores dos balões, veja o sítio [W3Schools](http://www.w3schools.com/colors/colors_hex.asp) (ou o [PDF](doc/balloon_colors.pdf)).


### `users.py3` ###

Por fim, a criação de usuários pode ser agilizada criando-se arquivos `.txt` adequados:

```bash
# Ver a documentação
python users.py3 -h

# Gerar os arquivos de usuários do sistema
python users.py3 teams.csv -j 2
```

Assume-se que há um arquivo CSV listando, em suas 2 primeiras colunas, o nome do time e a instituição que ele representa, nesta ordem.
