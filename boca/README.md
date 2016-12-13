# Maratona UnB #

Repositório de código. Para informações, visite o site oficial: [http://www.maratona.cic.unb.br](http://www.maratona.cic.unb.br).


## BOCA ##

O [BOCA](http://www.ime.usp.br/~cassio/boca/) é um sistema de administração de competições de programação. A forma mais simples de instalá-lo é usando pacotes DEB: [https://github.com/maratona-linux](https://github.com/maratona-linux) (é uma boa ideia ver [esta discussão](https://groups.google.com/forum/#!msg/boca-users/W2x3lRivUWs/F-S9CIrjAQAJ)).

### _Contest_ ###

Uma competição (_contest_) envolve uma série de arquivos para, basicamente, 3 funcionalidades:

1. gerar a prova;
2. gerar os arquivos para execução dos testes das submissões no BOCA; e
3. gerar os arquivos de usuários.

Para agilizar este processo, utilize os arquivos descritos a seguir.

#### `problems.py` ####

```bash
# Criar um problema
python problem.py -h
```

Este programa gera o esqueleto para criação de um problema dentro de um diretório que agrupa problemas com características similares:

```
problems
    `- característica
           `- problema
                  |- input/                (para os casos de teste)
                  |- output/               (para os resultados esperados)
                  `- problema.tex          (arquivo com a contextualização do problema)
```
Uma vez criada a estrutura, é preciso preencher o arquivo `problema.tex` com a descrição do problema e definição do formato de entrada e saída de dados. Veja a classe [MaratonaUnB](templates/problems/tex/MaratonaUnB.cls) para mais detalhes. O passo seguinte é criar uma série de casos de testes para avaliar uma solução para este problema, conforme as definições. A melhor forma de fazer isto é com um programa que gere casos aleatórios (já no diretório `input`), tomando cuidado para forçar o teste das condições de contorno (ou casos especiais de interesse). A seguir, crie um programa que solucione o problema (conforme as especificações) e gerar a saída adequada para os casos de teste gerados; cada arquivo de saída (no diretório `output`) está associado a um arquivo de entrada (em `input`). Para agilizar este processo, utilize o programa [`io.py`](io.py).

```bash
# Criar entradas/saídas de um problema
python io.py -h
```

Por fim, é preciso verificar a questão de limites de tempo de execução e atualizar tanto os arquivos no diretório `limits` do problema (caso os limites sejam diferentes dos valores padrões do BOCA definidos em [templates/limits](templates/limits)) quanto o `problema.tex`. O `io.py` já lida com isso automaticamente.

#### `contest.py` ####

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

Caso deseje sobrepor alguma configuração para o seu problema, basta incluir o diretório adequado com a configuração específica no diretório do seu problema (como é feito com os diretórios `ìnput` e `output`). Este programa gera um arquivo TeX listando os problemas (veja [MaratonaUnB](templates/problems/tex/MaratonaUnB.cls)), gera um arquivo PDF para a prova, configura um diretório `description` para cada problema e cria um arquivo ZIP para ser utilizado no BOCA.

```bash
# Gerar um contest
python contest.py -h
```

Os códigos das cores dos balões podem ser encontrados no sítio da [W3Schools](http://www.w3schools.com/colors/colors_hex.asp) (ou no [PDF](doc/balloon_colors.pdf)).


#### `users.py` ####

Por fim, a criação de usuários pode ser agilizada criando-se arquivos `.txt` adequados:

```bash
# Gerar os arquivos de usuários do sistema
python users.py -h
```

Assume-se que há um arquivo CSV listando, em suas 2 primeiras colunas, o nome do time e a instituição que ele representa, nesta ordem.
