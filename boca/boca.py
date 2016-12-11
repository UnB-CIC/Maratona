# -*- coding: utf-8 -*-
#   @package: boca.py
#    @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Gera os arquivos necessários para criação de um Contest com o BOCA.


from argparse import (ArgumentParser,
                      RawDescriptionHelpFormatter as DescriptionFormatter)
import os
from subprocess import check_call
from time import strftime


class Utils():
    VERBOSE = True

    @staticmethod
    def log(msg):
        if Utils.VERBOSE:
            print(msg)

    @staticmethod
    def copy(src, dest, flags=''):
        cmd = 'cp {} {} {}'.format(flags, src, dest)
        check_call(cmd, shell=True)
        Utils.log('Created ' + dest)

    @staticmethod
    def makedir(dir):
        if not os.path.isdir(dir):
            os.makedirs(dir)
            Utils.log('Created ' + dir)

    @staticmethod
    def pdflatex(tex_file, output_dir):
        cmd = ['pdflatex', '-output-directory=' + output_dir,
               '-interaction=nonstopmode', '-halt-on-error', tex_file]
        DEVNULL = open(os.devnull, 'w')
        try:
            check_call(cmd, stdout=DEVNULL)
            check_call(cmd, stdout=DEVNULL)  # 2x para indexação correta
        except:
            check_call(cmd)  # Mostrar o erro

        # Remoção de arquivos auxiliares
        for dirpath, dirnames, filenames in os.walk(output_dir):
            for f in filenames:
                if not f.endswith('.pdf'):
                    os.remove(os.path.join(dirpath, f))

        pdf_file = tex_file.replace('tex', 'pdf')
        Utils.log('Created {}/{}'.format(output_dir, pdf_file))
        return pdf_file

    @staticmethod
    def remove_subdirs(base_dir):
        cmd = 'rm -rf {}/*/'.format(base_dir)
        check_call(cmd, shell=True)
        Utils.log('Removed ' + base_dir + '/*/')

    @staticmethod
    def replace_first(pattern, repl, src_file, dest_file):
        print('read ' + src_file)
        with open(src_file, 'r') as f:
            from re import sub
            content = sub(pattern, repl, f.read(), 1)

        dest = os.path.dirname(dest_file)
        if not dest:
            dest = '.'
        if not os.path.isdir(dest):
            Utils.makedir(dest)

        print('write ' + dest_file)
        with open(dest_file, 'w') as f:
            f.write(content)

    @staticmethod
    def round_time(x):
        from math import ceil
        c = ceil(x)
        if x/c > 0.8:
            return c + 1
        return c

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
    def zip_dir(src_dir, file_name):
        current_dir = os.getcwd()
        os.chdir(src_dir)
        cmd = 'zip ' + file_name + ' -q -r *'
        check_call(cmd, shell=True)
        os.chdir(current_dir)

        file_name = os.path.join(src_dir, file_name)
        Utils.log('Created ' + os.path.realpath(file_name))


class Contest():
    '''Agrupar funções para criação de uma prova e arquivos ZIP relacionados
    para realização de um Contest no BOCA.
    '''
    class Dirs():
        @staticmethod
        def default():
            for d in ['compare', 'compile', 'description', 'input',
                      'limits', 'output', 'run', 'tests']:
                yield d

        @staticmethod
        def copy(src, dest):
            for dirpath, dirnames, filenames in os.walk(src):
                for dir in dirnames:
                    if dir in Contest.Dirs.default():
                        Utils.copy(dirpath + '/' + dir,
                                   dest + '/' + dir,
                                   '-Tr')

        @staticmethod
        def dir_problem_tuple(problem, base_dir='.'):
            for dirpath, dirnames, filenames in os.walk(base_dir):
                if problem in dirnames:
                    return Problem('./' + dirpath, problem)
            raise ValueError('Problema \'' + problem + '\'não encontrado.')

    class Files():
        @staticmethod
        def create_info(target_dir, problem, pdf_file, basename):
            tex_file = '{}/{}.tex'.format(problem.full_dir(), problem.name)

            with open(tex_file, 'r') as f:
                content = f.read()

            from re import search
            full_name = search(r'\NomeDoProblema{(.*?)}', content)
            if not full_name:
                raise ValueError('Nome completo do problema não definido '
                                 'no arquivo \'' + tex_file + '\'.')

            desc_dir = target_dir + '/description'
            desc_file = desc_dir + '/problem.info'
            rpl_dict = {'BASE_NAME': basename,
                        'FULL_NAME': full_name.groups(0)[0],
                        'DESCRIPTION_FILE': pdf_file}

            Utils.makedir(desc_dir)
            Contest.Files.fill_template('problem.info', desc_file, rpl_dict)

            src = '{}/../{}'.format(target_dir, pdf_file)
            Utils.copy(src, desc_dir)

        @staticmethod
        def create_zip(letter, problem, target_dir, pdf):
            Utils.makedir(target_dir)
            Contest.Dirs.copy('./BocaDefaults', target_dir)  # Padrão
            Contest.Dirs.copy(problem.full_dir(), target_dir)       # Específicos
            Contest.Files.create_info(target_dir, problem, pdf, letter)
            Utils.zip_dir(target_dir, '../{}.zip'.format(letter))

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
                Utils.log('Created ' + output_file)

    class TestSheet():
        @staticmethod
        def create_pdf(tex_file, base_dir):
            return Utils.pdflatex(tex_file, base_dir)

        @staticmethod
        def create_tex(contest, problems, date):
            def tex_format(problem):
                return '\t\\Problema[{}]{{{}}}%\n'.format(problem.dir,
                                                          problem.name)

            tex_file = contest + '.tex'
            rpl_dict = {'FILE_NAME': tex_file,
                        'FILE_DATE': strftime('%d/%m/%Y')}

            if date:
                rpl_dict['CONTEST_DATE'] = '\data{{{}}}%'.format(date)
            else:
                rpl_dict['\nCONTEST_DATE'] = ''

            tex_problems = ''.join(tex_format(p) for p in problems)
            rpl_dict['INDENTED_PROBLEMS\n'] = tex_problems

            Contest.Files.fill_template('contest.tex', tex_file, rpl_dict)

    @staticmethod
    def random_problems(dirs):
        def at_least(n, dir):
            for dirpath, dirnames, filenames in os.walk(dir):
                if len(dirnames) < n:
                    raise ValueError('Não há {} problemas em \'{}\'.'
                                     ''.format(n, dir))
                return dirnames

        problems = {}
        for dir in dirs:
            n = dirs.count(dir)
            problems[dir] = {'n': n, 'problems': at_least(n, dir)}

        from random import sample
        return [p for dir in problems for p in sample(problems[dir]['problems'], problems[dir]['n'])]

    @staticmethod
    def create(problems, contest_tex_file, base_dir='.', date=None):
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
        problems = [Contest.Dirs.dir_problem_tuple(p) for p in problems]

        base_dir += '/' + contest

        Utils.makedir(base_dir)
        Contest.TestSheet.create_tex(contest, problems, date)
        pdf_file = Contest.TestSheet.create_pdf(contest + '.tex', base_dir)

        letter = 'A'
        for p in problems:
            Utils.log('=== {} - {} ==='.format(letter, p.name))
            target_dir = base_dir + '/' + p.name
            Contest.Files.create_zip(letter, p, target_dir, pdf_file)

            # Ajuste
            letter = chr(ord(letter) + 1)

        Utils.remove_subdirs(base_dir)

    @staticmethod
    def add_subparser(parser):
        def check_tex(value):
            svalue = str(value)
            if not svalue or not svalue.lower().endswith('.tex'):
                raise ValueError('Arquivo \'' + svalue + '\' não é TeX.')

            if os.path.isfile(svalue):
                Utils.warning('O arquivo \'' + svalue + '\' será sobrescrito.')
            return svalue

        epilog = ('Exemplos de uso:\n'
                 '\tpython %(prog)s fizzbuzz easyled\n'
                 '\tpython %(prog)s -r 0 0 1 2\n\n')

        sub_p = parser.add_parser('contest', help='gerar arquivos para '
                                  'realização de um Contest',
                                  formatter_class=DescriptionFormatter,
                                  add_help=False,
                                  epilog=epilog)

        sub_p.add_argument('-d', dest='base_dir',
                           type=str, default='/tmp',
                           help='diretório onde criar os arquivos '
                           '(default: %(default)s)')
        sub_p.add_argument('-date', dest='date', type=str,
                           default=None,
                           help='data do contest')
        sub_p.add_argument('-h', '--help', action='help',
                           help='mostrar esta mensagem e sair')
        sub_p.add_argument('ids', nargs='+', type=str,
                           help='identificador(es) de problema(s) ou '
                           'diretório(s)')
        sub_p.add_argument('-q', '--quiet', dest='quiet',
                           action='store_true',
                           help='omitir os resultados do processo')
        sub_p.add_argument('-r', '--random', dest='random',
                           action='store_true',
                           help='criar uma prova aleatória')
        sub_p.add_argument('-t', dest='tex_file', type=check_tex,
                           default=strftime('%Y-%m-%d.tex'),
                           help='nome do arquivo TeX '
                           '(default: %(default)s)')

    @staticmethod
    def process_args(args):
        if args.random:
            problems = Contest.random_problems(args.ids)
        else:
            from collections import OrderedDict
            problems = list(OrderedDict.fromkeys(p for p in args.ids))

        Contest.create(problems, args.tex_file, args.base_dir, args.date)


class Problem():
    def __init__(self, dir, name):
        self.dir = dir
        self.name = name

    def full_dir(self):
        return self.dir + '/' + self.name

    class Dirs():
        @staticmethod
        def make(problem):
            Utils.makedir(problem.dir)
            Utils.makedir(problem.dir + '/' + problem.name)
            Utils.makedir(problem.dir + '/' + problem.name + '/input')
            Utils.makedir(problem.dir + '/' + problem.name + '/output')

    class Files():
        KNOWN_EXTENSIONS = ['c', 'cpp', 'py', 'py2', 'py3']

        @staticmethod
        def create_geninput(problem):
            file_name = '{}/geninput.py3'.format(problem.full_dir())
            Contest.Files.fill_template('geninput.py3', file_name)
            Utils.warning('Não se esqueça de gerar as Entradas/Saídas de '
                            'teste do problema.')

        @staticmethod
        def create_description_tex(problem):
            file_name = '{}/{}.tex'.format(problem.full_dir(), problem.name)
            Contest.Files.fill_template('problem.tex', file_name)
            Utils.warning('Não se esqueça de preencher a descrição do '
                            'problema:             *\n*     '
                            './{:<58}'.format(file_name))

        @staticmethod
        def create_solution(problem, solution):
            for dirpath, dirnames, filenames in os.walk('templates'):
                for f in filenames:
                    file_ext = f.split('.')[-1]
                    if file_ext in solution:
                        src = 'templates/' + f
                        dest = '{}/{}.{}'.format(problem.full_dir(),
                                                 problem.name, file_ext)
                        Utils.copy(src, dest)

            Utils.warning('Não se esqueça de gerar as soluções do problema.'
                            '                ')

    @staticmethod
    def create(problem, solution):
        '''
        Gera uma estrutura de arquivos inicial (dentro de um diretório que
        agrupa problemas com características similares), para criação de um
        problema no formato BOCA. Há uma opção de gerar um arquivo inicial (ou
        vários) para a solução na linguagem especificada. A estrutura é:
          - característica
              `- problema
                   |- input/          (diretório para os arquivos de teste)
                   |- output/         (diretório para os arquivos de teste)
                   |- geninput.py3    (programa para gerar a os dados de teste)
                   |- problema.tex    (arquivo com a descrição do problema)
                   `- problema.py2    ([opcional] arquivo para solução Python)
        '''
        Problem.Dirs.make(problem)
        Problem.Files.create_description_tex(problem)
        Problem.Files.create_geninput(problem)
        if solution:
            Problem.Files.create_solution(problem, solution)

    @staticmethod
    def add_subparser(parser):
        def check_str(value):
            svalue = str(value)

            from re import match
            if not match(r'^\w+$', svalue):
                raise ValueError('\'' + svalue + '\' não é um '
                                 'identificador válido.')

            return svalue

        epilog = ('Exemplo de uso:\n'
                  '\tpython %(prog)s 1 fizzbuzz')

        sub_p = parser.add_parser('problem', help='gerar a estrutura '
                                  'básica de um problema',
                                  formatter_class=DescriptionFormatter,
                                  add_help=False,
                                  epilog=epilog)

        sub_p.add_argument('dir', type=check_str,
                           help='diretório onde criar o problema')
        sub_p.add_argument('-h', '--help', action='help',
                           help='mostrar esta mensagem e sair')
        sub_p.add_argument('problem', type=check_str,
                           help='identificador do problema')
        sub_p.add_argument('-q', '--quiet', dest='quiet',
                           action='store_true',
                           help='omitir os resultados do processo')
        sub_p.add_argument('-s', nargs='?', dest='solution',
                           default='NoneGiven',
                           choices=['all'] + Problem.Files.KNOWN_EXTENSIONS,
                           help='criar um arquivo para implementação da '
                           'solução na linguagem especificada '
                           '(default: all).')

    @staticmethod
    def process_args(args):
        if args.solution == 'NoneGiven':
            args.solution = None
        elif not args.solution or args.solution == 'all':
            args.solution = Problem.Files.KNOWN_EXTENSIONS

        Problem.create(Problem(args.dir, args.problem), args.solution)


class Timer():
    '''Agrupar funções para lidar com medidas de tempo de um problema.'''
    @staticmethod
    def check_runs(value):
        ivalue = int(value)
        if ivalue <= 0:
            raise ValueError('É preciso uma quantidade positiva '
                             'de execuções.')

        return ivalue

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
    def check_time(args):
        if args.time_limit and not args.timeit:
            raise ValueError('--time-limit requires --timeit.')

        if args.timeit:
            print('Cronometrando {} execuçõe(s) (por arquivo), isto '
                  'pode demorar um pouco...'.format(args.runs))

    @staticmethod
    def get_time_limit(problem, language):
        file_name = '/'.join([problem.full_dir(), 'limits', language])

        if not os.path.isfile(file_name):
            file_name = 'BocaDefaults/limits/' + language

        with open(file_name, 'r') as f:
            from re import match
            for line in f:
                m = match('echo (\d+)', line)
                if m:
                    return m.group(1)

    @staticmethod
    def run_stages(src_file):
        def C(src_file):
            setup = 'gcc -static -O2 ' + src_file + ' -lm'
            cmd = './a.out'
            cleanup = 'rm a.out'
            extra_time = 0
            return (setup, cmd, cleanup, extra_time)

        def CPP(src_file):
            setup = 'g++ -static -O2 -std=c++11 ' + src_file + ' -lm'
            cmd = './a.out'
            cleanup = 'rm a.out'
            extra_time = 0
            return (setup, cmd, cleanup, extra_time)

        def Python2(src_file):
            setup = None
            cmd = 'python2 ' + src_file
            cleanup = None
            extra_time = 1
            return (setup, cmd, cleanup, extra_time)

        def Python3(src_file):
            setup = None
            cmd = 'python3 ' + src_file
            cleanup = None
            extra_time = 1
            return (setup, cmd, cleanup, extra_time)

        def Java(src_file):
            # setup = None
            # cmd = 'javac ' + src_file
            # cleanup = None
            # extra_time = 2
            # return (setup, cmd, cleanup, extra_time)
            raise NotImplementedError

        ext = src_file.split('.')[-1].lower()

        if ext in ['py', 'py2']:
            return Python2(src_file)
        if ext == 'py3':
            return Python3(src_file)
        if ext == 'c':
            return C(src_file)
        if ext == 'cpp':
            return CPP(src_file)
        if ext == 'java':
            return Java(src_file)

        raise ValueError('Tipo de arquivo \'' + ext + '\' desconhecido.')

    @staticmethod
    def set_LimiteDeTempo(tex_file, time_limit):
        pattern = 'LimiteDeTempo{\d+}%'
        repl = 'LimiteDeTempo{{{}}}%'.format(time_limit)
        Utils.replace_first(pattern, repl, tex_file, tex_file)

    @staticmethod
    def set_time_limit(dir, language, time_limit):
        src = '/'.join([dir, 'limits', language])
        dest = src

        if not os.path.isfile(src):
            src = './BocaDefaults/limits/' + language

        pattern = 'echo \d+'
        repl = 'echo {}'.format(time_limit)

        Utils.replace_first(pattern, repl, src, dest)

    @staticmethod
    def time_it(cmd, runs):
        setup = 'from subprocess import check_call'
        stmt = 'check_call(\'{}\', shell=True)'.format(cmd)

        from timeit import timeit
        return timeit(stmt, setup=setup, number=runs) / runs

    @staticmethod
    def add_arguments(sub_p):
        sub_p.add_argument('-h', '--help', action='help',
                           help='mostrar esta mensagem e sair')
        sub_p.add_argument('-l', '--time-limit', dest='time_limit',
                           action='store_true',
                           help='incluir limite de tempo no '
                           'arquivo TeX da descrição')
        sub_p.add_argument('src', type=Timer.check_src,
                           help='arquivo fonte com a solução a ser '
                           'aplicada (deve estar no mesmo diretório '
                           'do problema)')
        sub_p.add_argument('-q', '--quiet', dest='quiet',
                           action='store_true',
                           help='omitir os resultados do processo')
        sub_p.add_argument('-r', '--runs', dest='runs',
                           type=Timer.check_runs, default=10,
                           help='quantidade de execuções a serem '
                           'cronometradas')
        sub_p.add_argument('-t', '--timeit', dest='timeit',
                           action='store_true',
                           help='cronometrar execução da solução')

    @staticmethod
    def process_args(args):
        Timer.check_time(args)


class Output():
    '''Agrupar funções para criação de dados de saída para testes de um
    problema para realização de um Contest no BOCA.

    Gera os arquivos de saída a partir de um arquivo de código fonte e dos
    arquivos de teste de entrada. Assume que existe a seguinte estrutura:
      - nível
          `- problema
               |- input               (diretório para os arquivos de teste)
               |- output              (diretório para os arquivos de teste)
               `- problema.???        (código com a solução do problema)
    '''
    @staticmethod
    def add_subparser(parser):
        epilog = ('Exemplo de uso:\n'
                  '\tpython %(prog)s 1/fizzbuzz/solution.py3')

        sub_p = parser.add_parser('output', help='gerar arquivos de '
                                  'saída de dados de teste para um '
                                  'problema',
                                  formatter_class=DescriptionFormatter,
                                  add_help=False,
                                  epilog=epilog)

        Timer.add_arguments(sub_p)

    @staticmethod
    def process_args(args):
        Timer.process_args(args)

        base_dir = args.src.split('/')
        base_dir = '/'.join(base_dir[:-1])

        setup, bash_cmd, cleanup, extra_time = Timer.run_stages(args.src)

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
                    t = Timer.time_it(cmd, args.runs)
                    log_msg += ' ({:0.3f}s)'.format(t)
                    max_time = max(t, max_time)
                else:
                    check_call(cmd, shell=True)

                Utils.log(log_msg)

        if cleanup:
            check_call(cleanup, shell=True)

        if args.timeit:
            # time_limit = Utils.round_time(max_time) + extra_time

            # extra_time serve como parâmetro em relação a execução em C/C++,
            # mas esta medida de tempo já é realizada considerando a execução
            # da própria linguagem, portanto é viável ignorar.
            time_limit = Utils.round_time(max_time)
            Utils.log('\nTempo máximo: {:0.3f} s (setup: {}).'
                      ''.format(max_time, time_limit))

            if args.time_limit:
                language = args.src.split('.')[-1]
                problem = base_dir.split('/')[-1]
                tex_file = base_dir + '/' + problem + '.tex'
                Timer.set_time_limit(base_dir, language, time_limit)
                Timer.set_LimiteDeTempo(tex_file, time_limit)


class Input():
    '''Agrupar funções para criação de dados de entrada para testes de um
    problema para realização de um Contest no BOCA.
    '''
    @staticmethod
    def add_subparser(parser):
        epilog = ('Exemplo de uso:\n'
                  '\tpython %(prog)s 1/fizzbuzz/geninput.c')

        sub_p = parser.add_parser('input', help='gerar arquivos de '
                                  'entrada de dados de teste para um '
                                  'problema',
                                  formatter_class=DescriptionFormatter,
                                  add_help=False,
                                  epilog=epilog)

        Timer.add_arguments(sub_p)

    @staticmethod
    def process_args(args):
        Timer.process_args(args)

        base_dir = args.src.split('/')
        src_file = base_dir[-1]
        base_dir = '/'.join(base_dir[:-1])

        current_dir = os.getcwd()
        os.chdir(base_dir)

        setup, cmd, cleanup, time_limit = Timer.run_stages(src_file)

        if setup:
            check_call(setup, shell=True)

        log_msg = cmd
        if args.timeit:
            t = Timer.time_it(cmd, args.runs)
            log_msg += ' ({:0.3f}s)'.format(t)
        else:
            check_call(cmd, shell=True)

        Utils.log(log_msg)

        if cleanup:
            check_call(cleanup, shell=True)

        os.chdir(current_dir)


if __name__ == '__main__':
    classes = {'contest': Contest,
               'input': Input,
               'output': Output,
               'problem': Problem}

    parser = ArgumentParser(add_help=False,
                            description='Geração/manipulação automática de '
                                        'arquivos para a Maratona (BOCA).')

    parser.add_argument('-h', '--help', action='help',
                        help='mostrar esta mensagem e sair')
    subparsers = parser.add_subparsers(help='opções de uso', dest='command')

    for class_ in classes.values():
        class_.add_subparser(subparsers)

    args = parser.parse_args()
    Utils.VERBOSE = (not args.quiet)

    class_ = classes[args.command]
    class_.process_args(args)
