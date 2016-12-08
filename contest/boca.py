# -*- coding: utf-8 -*-
#   @package: contest.py
#    @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Gera os arquivos necessários para criação de um Contest com o BOCA.


from argparse import (ArgumentParser,
                      RawDescriptionHelpFormatter as DescriptionFormatter)
import os
from shutil import rmtree
from subprocess import check_call
from time import strftime

VERBOSE = True


def log(msg):
    if VERBOSE:
        print(msg)


class Contest():
    '''Agrupar funções para criação de uma prova e arquivos ZIP relacionados
    para realização de um Contest no BOCA.
    '''
    class Dirs():
        @staticmethod
        def copy(src, dest):
            for dirpath, dirnames, filenames in os.walk(src):
                for subdir in ['compare', 'compile', 'description', 'input',
                               'limits', 'output', 'run', 'tests']:
                    if subdir in dirnames:
                        src = dirpath + '/' + subdir
                        dst = dest + '/' + subdir
                        cmd = 'cp -r {} {}'.format(src, dst)
                        check_call(cmd, shell=True)
                        log('Created ' + dst)

        @staticmethod
        def find_problem(problem, base_dir='.'):
            for dirpath, dirnames, filenames in os.walk(base_dir):
                if problem in dirnames:
                    return (problem, dirpath)
            raise ValueError('Problema \'' + problem + '\'não encontrado.')

        @staticmethod
        def make(dir):
            if not os.path.isdir(dir):
                os.makedirs(dir)
                log('Created ' + dir)

        @staticmethod
        def remove_subdirs(base_dir):
            for dirpath, dirnames, filenames in os.walk(base_dir):
                for dir in dirnames:
                    rmtree(os.path.join(dirpath, dir))

    class Files():
        @staticmethod
        def create_info(target_dir, problem_dir, pdf_file, basename):
            def get_full_name(problem_dir):
                problem = problem_dir.split('/')[-1]
                tex_file = '{}/{}.tex'.format(problem_dir, problem)

                with open(tex_file, 'r') as f:
                    content = f.read()

                from re import search
                full_name = search(r'\NomeDoProblema{(.*?)}', content)
                if not full_name:
                    raise ValueError('Nome completo do problema não definido '
                                     'no arquivo \'' + tex_file + '\'.')

                return full_name.groups(0)[0]

            desc_dir = target_dir + '/description'
            desc_file = desc_dir + '/problem.info'
            rpl_dict = {'BASE_NAME': basename,
                        'FULL_NAME': get_full_name(problem_dir),
                        'DESCRIPTION_FILE': pdf_file}

            Contest.Dirs.make(desc_dir)
            Contest.Files.fill_template('problem.info', desc_file, rpl_dict)

            cmd = 'cp {}/../{} {}/'.format(target_dir, pdf_file, desc_dir)
            check_call(cmd, shell=True)
            log('Created {}/{}'.format(desc_dir, pdf_file))

        @staticmethod
        def create_pdf(contest, dest_dir):
            cmd = ['pdflatex', '-output-directory=' + dest_dir,
                   '-interaction=nonstopmode', '-halt-on-error',
                   contest + '.tex']
            DEVNULL = open(os.devnull, 'w')
            try:
                check_call(cmd, stdout=DEVNULL)
                check_call(cmd, stdout=DEVNULL)  # 2x para indexação correta
            except:
                check_call(cmd)  # Mostrar o erro

            # Remoção de arquivos auxiliares
            for dirpath, dirnames, filenames in os.walk(dest_dir):
                for f in filenames:
                    if not f.endswith('.pdf'):
                        os.remove(os.path.join(dirpath, f))

            pdf_file = contest + '.pdf'
            log('Created {}/{}'.format(dest_dir, pdf_file))
            return pdf_file

        @staticmethod
        def create_tex(contest, problems):
            def tex_format(dir, problem):
                return '\t\\Problema[{}]{{{}}}%\n'.format(dir, problem)

            tex_file = contest + '.tex'
            rpl_dict = {'FILE_NAME': tex_file,
                        'FILE_DATE': strftime('%d/%m/%Y')}

            tex_problems = ''.join(tex_format(d, p) for p, d in problems)
            rpl_dict['INDENTED_PROBLEMS\n'] = tex_problems

            Contest.Files.fill_template('contest.tex', tex_file, rpl_dict)

        @staticmethod
        def create_zip(letter, problem_dir, target_dir, pdf):
            Contest.Dirs.make(target_dir)
            Contest.Dirs.copy('./BocaDefaults', target_dir)  # Padrão
            Contest.Dirs.copy(problem_dir, target_dir)       # Específicos
            Contest.Files.create_info(target_dir, problem_dir, pdf, letter)
            Contest.Files.zip(target_dir, letter)

        @staticmethod
        def fill_template(input_file, output_file, rpl_dict=None):
            with open('templates/' + input_file, 'r') as f:
                content = f.read()

            if rpl_dict:
                from re import compile
                rx = compile('|'.join(rpl_dict.keys()))
                content = rx.sub(lambda m: rpl_dict[m.group(0)], content)

            with open(output_file, 'w') as f:
                f.write(content)
                log('Created ' + output_file)

        @staticmethod
        def zip(target_dir, letter):
            zip_file = '../' + letter + '.zip'
            current_dir = os.getcwd()
            os.chdir(target_dir)
            cmd = 'zip ' + zip_file + ' -q -r *'
            check_call(cmd, shell=True)
            os.chdir(current_dir)

            target_dir = target_dir.split('/')
            target_dir = '/'.join(target_dir[:-1])
            log('Created {}/{}.zip'.format(target_dir, letter))

    @staticmethod
    def create(problems, contest_tex_file, base_dir='.'):
        '''
        Assume-se cada problema está organizado com a seguinte estrutura mínima
        de arquivos (dentro de um diretório que agrupa problemas com
        características similares):
          - característica
              `- problema
                   |- input/                (para os casos de teste)
                   `- output/               (para os resultados esperados)

        Caso se deseje sobrescrever alguma configuração específica, basta
        acrescentar o(s) diretório(s) e arquivo(s) relacionados ao diretório do
        problema. Ex:
          - característica
              `- problema
                   |- input/
                   |- limits/
                   |    `- java         limites de tempo específicos para java)
                   `- output/
        '''
        contest = contest_tex_file[:-4]
        problems = [Contest.Dirs.find_problem(p) for p in problems]

        base_dir += '/' + contest

        Contest.Dirs.make(base_dir)
        Contest.Files.create_tex(contest, problems)
        pdf_file = Contest.Files.create_pdf(contest, base_dir)

        letter = 'A'
        for problem, dir in problems:
            log('=== {} - {} ==='.format(letter, problem))
            problem_dir = dir + '/' + problem
            target_dir = base_dir + '/' + problem
            Contest.Files.create_zip(letter, problem_dir, target_dir, pdf_file)

            # Ajuste
            letter = chr(ord(letter) + 1)

        Contest.Dirs.remove_subdirs(base_dir)

    @staticmethod
    def add_subparser(p):
        def check_tex(value):
            svalue = str(value)
            if not svalue or not svalue.lower().endswith('.tex'):
                raise ValueError('Arquivo \'' + svalue + '\' não é TeX.')

            if os.path.isfile(svalue):
                print('O arquivo \'' + svalue + '\' será sobrescrito.')
            return svalue

        epilog = 'Exemplo de uso:\n\tpython %(prog)s fizzbuzz easyled\n'

        sub_p = p.add_parser('contest', help='Gerar arquivos para '
                             'realização de um Contest com o Contest.',
                             formatter_class=DescriptionFormatter,
                             epilog=epilog)

        sub_p.add_argument('problems', nargs='+', type=str,
                           help='Identificador(es) de problema(s).')

        sub_p.add_argument('-t', dest='tex_file', type=check_tex,
                           default=strftime('%Y-%m-%d.tex'),
                           help='Nome do arquivo TeX '
                           '(default: %(default)s).')
        sub_p.add_argument('-d', dest='base_dir',
                           type=str, default='/tmp',
                           help='Diretório onde criar os arquivos '
                           '(default: %(default)s).')
        sub_p.add_argument('-q', '--quiet', dest='quiet',
                           action='store_true',
                           help='Omitir os resultados do processo.')

    @staticmethod
    def process_args(args):
        from collections import OrderedDict
        problems = list(OrderedDict.fromkeys(p for p in args.problems))

        Contest.create(problems, args.tex_file, args.base_dir)


class Problem():
    '''Agrupar funções para criação de um problema para realização de um
    Contest no BOCA.
    '''

    class Dirs():
        @staticmethod
        def make(dir, problem):
            Contest.Dirs.make(dir)
            Contest.Dirs.make(dir + '/' + problem)
            Contest.Dirs.make(dir + '/' + problem + '/input')
            Contest.Dirs.make(dir + '/' + problem + '/output')

    class Files():
        KNOWN_EXTENSIONS = ['c', 'cpp', 'py', 'py3']

        @staticmethod
        def create_geninput(dir, problem):
            file_name = '{}/{}/geninput.py'.format(dir, problem)
            Contest.Files.fill_template('geninput.py', file_name)
            Problem.warning('Não se esqueça de gerar as Entradas/Saídas de '
                            'teste do problema.')

        @staticmethod
        def create_tex(dir, problem):
            file_name = '{}/{}.tex'.format(dir, problem)
            Contest.Files.fill_template('problem.tex', file_name)
            Problem.warning('Não se esqueça de preencher a descrição do '
                            'problema:             *\n*     '
                            './{:<58}'.format(file_name))

        @staticmethod
        def create_solution(dir, problem, solution):
            for dirpath, dirnames, filenames in os.walk('templates'):
                for f in filenames:
                    file_ext = f.split('.')[-1]
                    if file_ext in solution:
                        src = 'templates/' + f
                        dest = '{}/{}/{}.{}'.format(dir, problem, problem,
                                                    file_ext)
                        cmd = 'cp {} {}'.format(src, dest)
                        check_call(cmd, shell=True)
                        log('Created ' + dest)

            Problem.warning('Não se esqueça de gerar as soluções do problema.'
                            '                ')

    @staticmethod
    def create(dir, problem, solution):
        '''
        Gera uma estrutura de arquivos inicial (dentro de um diretório que
        agrupa problemas com características similares), para criação de um
        problema no formato BOCA. Há uma opção de gerar um arquivo inicial (ou
        vários) para a solução na linguagem especificada. A estrutura é:
          - característica
              `- problema
                   |- input/          (diretório para os arquivos de teste)
                   |- output/         (diretório para os arquivos de teste)
                   |- geninput.py     (programa para gerar a os dados de teste)
                   |- problema.tex    (arquivo com a descrição do problema)
                   `- problema.py     ([opcional] arquivo para solução Python)
        '''
        Problem.Dirs.make(dir, problem)
        Problem.Files.create_tex(dir, problem)
        Problem.Files.create_geninput(dir, problem)
        if solution:
            Problem.Files.create_solution(dir, problem, solution)

    @staticmethod
    def warning(msg):
        # 68 caracteres '*'
        print('\n'
              '**********************************'
              '**********************************\n'
              '* {:64s} *\n'
              '**********************************'
              '**********************************\n'.format(msg))

    @staticmethod
    def add_subparser(p):
        def check_str(value):
            svalue = str(value)

            from re import match
            if not match(r'^\w+$', svalue):
                raise ValueError('\'' + svalue + '\' não é um '
                                 'identificador válido.')

            return svalue

        epilog = ('Exemplo de uso:\n'
                  '\tpython %(prog)s 1_getting_started fizzbuzz')

        sub_p = p.add_parser('problem', help='Gerar a estrutura '
                             'básica de um problema para o um '
                             'Contest com o BOCA.',
                             formatter_class=DescriptionFormatter,
                             epilog=epilog)

        sub_p.add_argument('dir', type=check_str,
                           help='Diretório onde criar o problema')
        sub_p.add_argument('problem', type=check_str,
                           help='Identificador do problema')
        sub_p.add_argument('-s', nargs='?', dest='solution',
                           default='NoneGiven',
                           choices=['all'] + Problem.Files.KNOWN_EXTENSIONS,
                           help='Criar um arquivo para implementação da '
                           'solução na linguagem especificada.')
        sub_p.add_argument('-q', '--quiet', dest='quiet',
                           action='store_true',
                           help='Omitir os resultados do processo.')

    @staticmethod
    def process_args(args):
        if args.solution == 'NoneGiven':
            args.solution = None
        elif not args.solution or args.solution == 'all':
            args.solution = Problem.Files.KNOWN_EXTENSIONS

        Problem.create(args.dir, args.problem, args.solution)


class IO():
    '''Agrupar funções para criação dos casos de teste (Entrada/Saída) para
    realização de um Contest no BOCA.
    '''
    @staticmethod
    def execution(src_file):
        def C(src_file):
            setup = 'gcc -lm -O2 ' + src_file
            cmd = './a.out'
            cleanup = 'rm a.out'
            return (setup, cmd, cleanup)

        def CPP(src_file):
            setup = 'g++ -lm -O2 -std=c++11 ' + src_file
            cmd = './a.out'
            cleanup = 'rm a.out'
            return (setup, cmd, cleanup)

        def Python2(src_file):
            setup = None
            cmd = 'python2 ' + src_file
            cleanup = None
            return (setup, cmd, cleanup)

        def Python3(src_file):
            setup = None
            cmd = 'python3 ' + src_file
            cleanup = None
            return (setup, cmd, cleanup)

        ext = src_file.split('.')[-1].lower()

        if ext in ['py', 'py2']:
            return Python2(src_file)
        if ext == 'py3':
            return Python3(src_file)
        if ext == 'c':
            return C(src_file)
        if ext == 'cpp':
            return CPP(src_file)

        raise ValueError('Tipo de arquivo \'' + ext + '\' '
                         'desconhecido.')

    @staticmethod
    def time_it(cmd, runs):
        setup = 'from subprocess import check_call'
        stmt = 'check_call(\'{}\', shell=True)'.format(cmd)

        from timeit import timeit
        return timeit(stmt, setup=setup, number=runs)

    @staticmethod
    def check_src(value):
        if not value:
            raise ValueError('É preciso especificar o arquivo com '
                             'a solução.')

        svalue = str(value)
        if not os.path.isfile(svalue):
            raise ValueError('Arquivo \'{}\' não encontrado.'
                             ''.format(svalue))

        return svalue

    @staticmethod
    def check_runs(value):
        ivalue = int(value)
        if ivalue <= 0:
            raise ValueError('É preciso uma quantidade positiva '
                             'de execuções.')

        return ivalue

    @staticmethod
    def add_arguments(sub_p):
        sub_p.add_argument('src', type=IO.check_src,
                           help='Arquivo fonte com a solução a ser '
                           'aplicada (deve estar no mesmo diretório '
                           'do problema).')
        sub_p.add_argument('-t', '--timeit', dest='timeit',
                           action='store_true',
                           help='Cronometrar execução da solução.')
        sub_p.add_argument('-r', '--runs', dest='runs',
                           type=IO.check_runs, default=100,
                           help='Quantidade de execuções a serem '
                           'cronometradas ')
        sub_p.add_argument('-l', '--time-limit', dest='time_limit',
                           action='store_true',
                           help='Incluir limite de tempo no '
                           'arquivo TeX da descrição.')
        sub_p.add_argument('-q', '--quiet', dest='quiet',
                           action='store_true',
                           help='Omitir os resultados do processo.')

    @staticmethod
    def check_time_args(args):
        if args.time_limit and not args.timeit:
            raise ValueError('--time-limit requires --timeit.')

        if args.timeit:
            print('Cronometrando {} execuçõe(s) (por arquivo), isto '
                  'pode demorar um pouco...'.format(args.runs))


class Output():
    '''Agrupar funções para criação de dados de saída para testes de um
    problema para realização de um Contest no BOCA.

    Gera os arquivos de saída a partir de um arquivo de código fonte e dos
    arquivos de teste de entrada. Assume que existe a seguinte estrutura:
      - nível
          `- problema
               |- input               (diretório para os arquivos de teste)
               |- output              (diretório para os arquivos de teste)
               `- src_file.??         (programa com a solução do problema)
    '''
    @staticmethod
    def add_subparser(p):
        epilog = ('Exemplo de uso:\n'
                  '\tpython %(prog)s 1/fizzbuzz/solution.py')

        sub_p = p.add_parser('output', help='Gerar arquivos de '
                             'Saída de dados de teste para um '
                             'problema.',
                             formatter_class=DescriptionFormatter,
                             epilog=epilog)

        IO.add_arguments(sub_p)

    @staticmethod
    def process_args(args):
        IO.check_time_args(args)

        base_dir = args.src.split('/')
        base_dir = '/'.join(base_dir[:-1])

        setup, bash_cmd, cleanup = IO.execution(args.src)

        if setup:
            check_call(setup, shell=True)

        max_time = 0
        input_dir = base_dir + '/input'
        for (dirpath, dirnames, filenames) in os.walk(input_dir):
            for f in sorted(filenames):
                input_file = '{}/input/{}'.format(base_dir, f)
                output_file = '{}/output/{}'.format(base_dir, f)
                log_msg = '{} > {}'.format(input_file, output_file)
                cmd = '{} < {}'.format(bash_cmd, log_msg)

                if args.timeit:
                    t = IO.time_it(cmd, args.runs)
                    t /= args.runs

                    max_time = max(t, max_time)
                    log_msg += ' ({:0.3f}s)'.format(t)
                else:
                    check_call(cmd, shell=True)

                log(log_msg)

        if cleanup:
            check_call(cleanup, shell=True)

        if args.timeit:
            log('\ntempo médio máximo: {:0.3f} s.'.format(max_time))
            from math import ceil
            time_limit = str(ceil(max_time))
            log('Setup para {}s'.format(time_limit))

            if args.time_limit:
                raise NotImplementedError('AJuste do arquivo ainda '
                                          'não implementado')
                # desc_file = problem + '.tex'
                # with open(desc_file, 'r') as f:
                #     lines = f.readlines()
                # lines = ''.join(lines)
                # matches = findall('LimiteDeTempo{(.*?)}', lines)
                # if matches:
                #     tex_time_limit = 'LimiteDeTempo{{{}}}'
                #                      ''.format(time_limit)
                #     lines = sub('LimiteDeTempo{(.*?)}',
                #                 tex_time_limit, lines)
                # else:
                #     matches = findall('\\NomeDoProblema(.*?)\n',
                #                       lines)
                #     tex_time_limit = '\n\\LimiteDeTempo{{{}}}%' \
                #                      ''.format(time_limit)
                #     for line in matches:
                #         lines = sub(line, line + tex_time_limit,
                #                     lines)
                # with open(desc_file, 'w') as f:
                #     f.write(lines)


class Input():
    @staticmethod
    def add_subparser(p):
        epilog = ('Exemplo de uso:\n'
                  '\tpython %(prog)s 1/fizzbuzz/geninput.py')

        sub_p = p.add_parser('input', help='Gerar arquivos de '
                             'Entrada de dados de teste para um '
                             'problema.',
                             formatter_class=DescriptionFormatter,
                             epilog=epilog)

        IO.add_arguments(sub_p)

    @staticmethod
    def process_args(args):
        IO.check_time_args(args)

        base_dir = args.src.split('/')
        src_file = base_dir[-1]
        base_dir = '/'.join(base_dir[:-1])

        current_dir = os.getcwd()
        os.chdir(base_dir)

        setup, bash_cmd, cleanup = IO.execution(src_file)

        if setup:
            check_call(setup, shell=True)

        log_msg = bash_cmd
        if args.timeit:
            t = IO.time_it(bash_cmd, args.runs)
            t /= args.runs
            log_msg += ' ({:0.3f}s)'.format(t)
        else:
            check_call(bash_cmd, shell=True)

        log(log_msg)

        if cleanup:
            check_call(cleanup, shell=True)

        os.chdir(current_dir)


if __name__ == '__main__':
    parser = ArgumentParser(description='Geração/manipulação automática de '
                                        'arquivos para a Maratona.')

    subparsers = parser.add_subparsers(help='Sub-comandos', dest='command')

    Contest.add_subparser(subparsers)
    Problem.add_subparser(subparsers)
    Input.add_subparser(subparsers)
    Output.add_subparser(subparsers)

    args, unknown = parser.parse_known_args()
    VERBOSE = (not args.quiet)

    if args.command == 'contest':
        Contest.process_args(args)
    if args.command == 'problem':
        Problem.process_args(args)
    if args.command == 'input':
        Input.process_args(args)
    if args.command == 'output':
        Output.process_args(args)
