Maratona UnB
============

Repositório de código. Para informações, visite o site oficial: [http://www.maratona.cic.unb.br](http://www.maratona.cic.unb.br).


Provas
======

As provas são feitos com o software [BOCA](http://www.ime.usp.br/~cassio/boca/), portanto os problemas devem ser estruturados de acordo com ele em 9 diretórios. Os valores padrões para as configurações do BOCA estão no diretório [BocaDefaults](BocaDefaults), mas cada problema tem pelo menos 4 arquivos específicos que o definem (não inclusos na estrutura de diretórios padrão).

Problemas
---------

Para usar o juíz automático, cada problema deve definir os seguintes arquivos:

    problema
       |- description
       |     |- problem.info
       |     `- prova.pdf
       |- input
       |     `- problema
       `- output
             `- problema

Conforme a [documentação](http://www.ime.usp.br/~cassio/boca/boca/doc/ADMIN.txt), o arquivo ```problem.info``` descreve os nomes relacionados ao problema, e indica o arquivo que contém a descrição mais detalhada deste (no exemplo, ```prova.pdf```, mas poderia ser outro tipo de arquivo ou mesmo nenhum). O arquivo ```input/problema``` deve conter as entradas a serem utilizadas para testar as soluções enviadas. O arquivo ```output/problema``` deve conter as saídas associadas às entradas (*na mesma ordem*), os arquivos necessariamente devem ter o mesmo nome. **Cuidado com a versão do BOCA sendo utilizada, a versão considerada aqui assume apenas um arquivo de entrada e um de saída, versões mais recentes utilizam diversos arquivos.**

Supondo que se queria avaliar a implementação de um _conceito_ específico com um _problema_, a forma mais simples de se incluir um problema é copiar os arquivos padrões e definir os diretórios/arquivos específicos. Por exemplo, considerando o problema [easyled](1/easyled) (baseado em [LED](https://www.urionlinejudge.com.br/judge/pt/problems/view/1168)), que lida com strings, bastaria definir:

    easyled
     |- description
     |     |- problem.info
     |     `- prova.pdf
     |- input
     |     `- easyled
     `- output
           `- easyled

Além destes, pode ser interessante analisar os arquivos do diretório ```compile``` para, por exemplo, verificar o comando utilizado para compilar a solução (e acrescentar/remover _flags_ de compilação), e os arquivos do diretório ```limits```, que definem as restrições de tempo/espaço associadas ao problema.

Uma vez que todos os 9 diretórios estão completos, basta utilizar uma ferramenta qualquer para gerar um arquivo ZIP deles e submetê-lo ao BOCA via interface web.

PDF de Prova
------------

A classe [MaratonaUnB](MaratonaUnB.cls) facilita a criação de provas, bastando apenas que os problemas sigam a simples estrutura descrita. Ela utiliza a classe [UnBExam](https://github.com/gnramos/UnBExam) como base. Assume-se que cada problema está organizado com a seguinte estrutura de arquivos (dentro de um diretório [opcional] que indica o conceito mais importante para resolução):

    - conceito
        `- problema
	         `- problema.tex

O arquivo ```problema.tex``` contém a descrição do problema e as definições de entrada/saída a serem utilizadas como exemplos.

Todo arquivo ```problema.tex``` deve ter a seguinte estrutura:

```TeX
\NomeDoProblema{O nome completo do problema}%
\LimiteDeTempo{1}% O limite de tempo para execução da solução.

% Texto introdutório, contextualizando o problema e explicitando o que se
% deseja que o programa faça.

\Entrada%
% Descrição precisa da quantidade de dados de entrada, e do formato destes.

\Saida%
% Descrição precisa dos dados de saída, e do formato destes.

\Exemplos{1} % Lista dos nomes dos arquivos de entrada/saída, separados
             % por vírgulas, a serem utilizados como exemplos.

% Neste ponto, *automaticamente* serão inclusos os exemplos de IO.

% Caso necessário, pode-se usar:
\aoFinalDoProblema{%
    % Conteúdo a ser inserido *após* os exemplos de IO.
}%
```

Exemplo de uso da classe CIC-Maratona:

```TeX
\documentclass{MaratonaUnB}%

\begin{document}%
    \problema[./problems/0]{parouimpar}%
    \problema[./problems/1]{fizzbuzz}%
\end{document}%
```

Scripts
-------

Para facilitar a configuração do BOCA, alguns __scripts__ podem ser utilizados (testado em ambiente GNU/Linux).

```Python
# Criar um problema
python problem.py -h

# Gerar arquivos de entrada/saída
python io.py -h

# Gerar um contest
python contest.py -h

# Gerar os arquivos de usuários do sistema
python users.py -h
```

Cores
-----

Os códigos das cores dos balões podem ser vistos [aqui](http://www.w3schools.com/colors/colors_hex.asp) (ou no [PDF](balloon_colors.pdf)).
