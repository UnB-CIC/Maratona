%%
%% Arquivo MaratonaUnB.cls
%%
%% Copyright (C) 2016 by Guilherme N. Ramos (gnramos@unb.br)
%%
%%
%% Exemplo de uso:
%%
%%%%%%%%%% Documento TeX %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%    \documentclass{MaratonaUnB}%
%%
%%    \documento{Prova Exemplo - 2016}%
%%    \data{29 de novembro de 2016}%
%%
%%    \begin{document}%
%%        \Problema[./problems/1]\Problema[1]{fizzbuzz}%
%%        \Problema[./problems/3]{led}%
%%    \end{document}%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%
%%%%%%%%%% Modelo de Problema %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%
%% \NomeDoProblema{Nome Completo do Problema}%
%% \Conceitos{Conceitos/técnicas abordadas}
%%
%% Texto introdutório, contextualizando o problema e explicitando o que se
%% deseja que o programa faça.
%%
%% \Entrada%
%% Descrição precisa da quantidade de dados de entrada, e do formato destes.
%%
%% \Saida%
%% Descrição precisa dos dados de saída, e do formato destes.
%%
%% \Exemplos{Lista dos nomes dos arquivos de entrada/saída, separados por
%% vírgulas, a serem utilizados como exemplos.}%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\NeedsTeXFormat{LaTeX2e}[1999/12/01]%

\ProvidesClass{MaratonaUnB}[2016/11/29 Classe para gerar simulados para MaratonaUnB de Programação da UnB.]%

\ProcessOptions\relax%
\LoadClass{UnBExam}%
\extraheadheight[0cm]{0mm}%
\documento{MaratonaUnB de Programação UnB}%
\data{\today}%

\RequirePackage{hyperref}% Links internos
\RequirePackage{pgffor}% laço foreach
\RequirePackage{totcount}% Contagem de problemas.
\RequirePackage{verbatim}% Inclusão de exemplos de I/O para problemas.

% Contadores
\newcounter{exemplo}%
\newcounter{problem}%
\regtotcounter{problem}%

% Margens da tabela de exemplos.
\newlength{\@inputWidth}%
\newlength{\@outputWidth}%

% Primeira página
\newcommand{\@capa}{%
	\thispagestyle{empty}%

	\begin{center}%
		\includegraphics[width=.25\textwidth]{MaratonaUnB}%
	\end{center}%

	\vfill%

	\begin{center}%
		{\Huge\bf\documento@UnBExam}%
		\\\vspace{2em}
		{\small\emph{\data@UnBExam}}%
		\\\vfill%
		Este caderno contém \total{problem} problemas; as páginas estão numeradas
		de 1 a \hyperlink{page.\numpages}{\numpages}.
	\end{center}%
	\vfill%
	\begin{center}\small v0.2\end{center}%
}%

% Segunda página.
\newcommand{\@contracapa}{%
	\thispagestyle{empty}%
	\paragraph{Informações Gerais}\ \\\vspace{-.75em}%

	Estas condições são válidas para todos os problemas, exceto quando
	explicitamente dito.%

	\paragraph{Nome do programa}\ \\\vspace{-1em}%
	\begin{enumerate}\setlength{\itemsep}{0pt}%
		\item Sua solução deve ser chamada
		\emph{problema}\texttt{.c}, \emph{problema}\texttt{.cpp} ou
		\emph{problema}\texttt{.java}; onde \emph{problema} é a letra maiúscula
		que identifica o problema.% Lembre que em Java o nome da classe principal deve ser igual ao nome do arquivo.%
	\end{enumerate}%

	\paragraph{Entrada}\ \\\vspace{-1em}%%
	\begin{enumerate}\setlength{\itemsep}{0pt}%
		\item A entrada de seu programa deve ser lida da entrada padrão.%
		\item A entrada consiste de um único caso de teste, que é descrito com
		uma quantidade de linhas definida no problema. Não há outras informações na entrada.
		\item Quando uma linha contém diversos valores, eles são separados por
		\emph{um único espaço}. Não há outros espaços na entrada. Não há linhas vazias.
		\item Apenas o alfabeto em Inglês é utilizado. Não há caracteres com til,
		acento, trema ou outros símbolos (ñ, Ã, é, Ì, ô, Ü, ç, etcetera).
		\item Todas as linhas, incluindo a última, contém o tradicional caractere
		de quebra-de-linha.
	\end{enumerate}%

	\paragraph{Saída}\ \\\vspace{-.75em}%
	\begin{enumerate}\setlength{\itemsep}{0pt}%
		\item A saída de seu programa deve ser escrita na saída padrão.%
		\item O resultado de um caso de teste deve ser escrito com uma quantidade
		de linhas definida no problema. Não deve haver outras informações na saída.
		\item Quando uma linha contém diversos valores, eles devem ser separados
		por \emph{um único espaço}. Não deve haver outros espaços na entrada. Não
		deve haver linhas vazias.
		\item Apenas o alfabeto em Inglês deve ser utilizado. Não deve haver
		caracteres com til, acento, trema ou outros símbolos (ñ, Ã, é, Ì, ô, Ü,
		ç, etcetera).
		\item Todas as linhas, incluindo a última, devem conter o tradicional
		caractere de quebra-de-linha.
		\item Para resultados de números reais, arredonde para o número racional
		mais próximo com a quantidade equivalente de dígitos de precisão. O caso
		de teste é feito de modo que não haja ambiguidade neste tipo de arredondamento.
	\end{enumerate}%
}%

% Verificação de arquivos.
\newcommand{\@stopIfNotExists}[1]{%
	\IfFileExists{#1}%
		{}%
		{%
			\ClassError{MaratonaUnB}%
			{Arquivo '#1' nao encontrado}%
			{O arquivo '#1' deveria estar junto ao demais arquivos do problema}%
		}%
}%

% Inclui (verbatim) o arquivo, ajustando os espaços verticais.
\newcommand{\@exampleCell}[1]{%
	\vspace{-1.2\baselineskip}%
	\verbatiminput{#1}%
	\vspace*{-2\baselineskip}%
}%

% Para cada exemplo, gera uma tabela.
\newcommand{\@tabelasDeExemplos}{%
	\ifx\@exemplosCSV\@empty%
		\ClassError{MaratonaUnB}%
			{Problema  '\@baseFile.tex' nao define exemplos de teste}%
			{O arquivo '\@baseFile.tex' deveria definir exemplos para o problema}%
	\fi%

	\setcounter{exemplo}{0}%
    \foreach \ex in \@exemplosCSV {
    	\stepcounter{exemplo}%

    	% Seleciona o próximo item.
    	\def\lastitem{\ex}%
    	\expandafter\gdef\expandafter\glastitem\expandafter{\ex}%

    	% Define os arquivos de exemplos de I/O.
    	\def\@exampleInputFile{\@baseFileDir/input/\ex}%
    	\def\@exampleOutputFile{\@baseFileDir/output/\ex}%

    	\@stopIfNotExists{\@exampleInputFile}%
    	\@stopIfNotExists{\@exampleOutputFile}%

    	% Gera a tabela com os exemplos.
    	\noindent%
    	\vspace{-.75em}%
    	\begin{tabular}[t]{|p{.95\@inputWidth}|p{.95\@outputWidth}|}%
			\hline%
			\textbf{Entrada \arabic{exemplo}} & \textbf{Saída \arabic{exemplo}}    \\%
			\@exampleCell{\@exampleInputFile} & \@exampleCell{\@exampleOutputFile} \\\hline%
		\end{tabular}\\%
    }
}%

% Define o formato inicial do documento.
\AtBeginDocument{%
	% Valores iniciais.
	\aoFinalDoProblema{}%
	\setInputWidth{.5\textwidth}%
	% Documento
	\@capa%
	\newpage%
	\@contracapa%
	% Reformatação para inclusão de problemas
	\pagestyle{headings}%
	\setcounter{page}{0}%
	\markboth{}{\documento@UnBExam}%
}%


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%                     Funções que o usuário "pode" acessar                     %
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%


% Define a lista (CSV) de conceitos e técnicas a serem abordados no problema.
%   #1 - lista de nomes dos arquivos, separados por vírgulas
\newcommand{\Conceitos}[1]{\gdef\@conceitosCSV{#1}}%
% Exemplo de uso:
%    \Conceitos{string,counting sort}%

% Define a lista (CSV) de exemplos a serem inclusos.
%   #1 - lista de nomes dos arquivos, separados por vírgulas
\newcommand{\Exemplos}[1]{\gdef\@exemplosCSV{#1}}%
% Exemplo de uso:
%    \Exemplos{1,2,5}%

% Define o limite de tempo disponível para execução do  problema.
\newcommand{\LimiteDeTempo}[1]{%
	\begin{center}%
		\emph{Limite de tempo: #1s}%
	\end{center}%
}%

% Define o título do problema.
%   #1 - nome completo do problema
\newcommand{\NomeDoProblema}[1]{
	\ifx&#1&%
		\ClassError{MaratonaUnB}%
			{Problema  '\@baseFile.tex' sem nome}%
			{O arquivo '\@baseFile.tex' deveria definir o nome do problema}%
	\fi%
	\begin{center}%
		{\LARGE{\bf Problema\ \Alph{problem} - #1}}%
	\end{center}
}%

% Define a formatação da seção que descreve a entrada de dados.
\newcommand{\Entrada}{\subsection*{Entrada}}%

% Define a formatação da seção que descreve a saída de dados.
\newcommand{\Saida}{\subsection*{Saída}}%

% Define @atEndProblem, que é incluído ao final de cada problema. O conteúdo de
% @atEndProblem é liberado ao final de cada problema, de modo que cada "sufixo"
% só seja considerado uma vez por problema.
\newcommand{\aoFinalDoProblema}[1]{\def\@atEndProblem{#1}}%

% Insere um problema.
%   #1 - diretório dos arquivos
%   #2 - nome base dos arquivos
\newcommand{\Problema}[2][]{%
	\ifx&#1&\@empty\def\@baseFileDir{\detokenize{#2}}%
	\else\def\@baseFileDir{\detokenize{#1/#2}}%
	\fi%

	\def\@fileName{\detokenize{#2}}%

	\graphicspath{{\@baseFileDir/}}%
	\def\@baseFile{\@baseFileDir/#2}%

	\@stopIfNotExists{\@baseFile}%

	\newpage%
	\stepcounter{problem}%

	{% garantir o escopo local de inputWidth, caso seja alterada
		\Exemplos{}% força o erro caso não definidos
		\input{\@baseFile}%
		\@tabelasDeExemplos%

		\@atEndProblem%
		\aoFinalDoProblema{}% Limpando as cofigurações
	}%
}%
% Exemplo de uso:
%    \Problema[./problems/1]{fizzbuzz}%

% Largura da coluna de exemplos de entrada (na tabela de exemplos de IO de um
% problema). A largura da coluna com exemplos de saída é ajustada
% automaticamente em função da de entrada.
\newcommand{\setInputWidth}[1]{%
	\setlength{\@inputWidth}{#1}%
	\setlength{\@outputWidth}{\textwidth}%
	\addtolength{\@outputWidth}{-#1}%
}%
% Exemplo de uso:
%    \setInputWidth{.25\textwidth}%

\endinput
%%
%% End of file `MaratonaUnB.cls'.
