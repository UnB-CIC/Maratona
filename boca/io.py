#  -*- coding: utf-8 -*-
#    @package: io.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Agrupar funções para criação de dados de entrada/saída para testes de um
# problema para realização de um Contest no BOCA.

# Gera os arquivos de saída a partir de um arquivo de código fonte e dos
# arquivos de teste de entrada. Assume que existe a seguinte estrutura:
#   - nível
#       `- problema
#            |- input               (diretório para os arquivos de teste)
#            |- output              (diretório para os arquivos de teste)


import os
from subprocess import check_call
import utils


def gen_input(src_file):
    base_dir = src_file.split('/')
    src_file = base_dir[-1]
    base_dir = '/'.join(base_dir[:-1])

    current_dir = os.getcwd()
    os.chdir(base_dir)

    setup, cmd, cleanup, time_limit = run_stages(src_file)

    if setup:
        check_call(setup, shell=True)

    check_call(cmd, shell=True)

    if cleanup:
        check_call(cleanup, shell=True)

    os.chdir(current_dir)


def gen_ouput(src_file, timeit, runs=0, set_time_limit=False):
    base_dir = src_file.split('/')
    base_dir = '/'.join(base_dir[:-1])

    setup, bash_cmd, cleanup, extra_time = run_stages(src_file)

    if setup:
        check_call(setup, shell=True)

    max_time = 0
    input_dir = base_dir + '/input'
    for (dirpath, dirnames, filenames) in os.walk(input_dir):
        for f in sorted(filenames):
            input_file = '{}/input/{}'.format(base_dir, f)
            output_file = '{}/output/{}'.format(base_dir, f)
            msg = '{} > {}'.format(input_file, output_file)
            cmd = '{} < {}'.format(bash_cmd, msg)

            if timeit:
                t = time_it(cmd, runs)
                msg += ' ({:0.3f}s)'.format(t)
                max_time = max(t, max_time)
            else:
                check_call(cmd, shell=True)

            utils.log(msg)

    if cleanup:
        check_call(cleanup, shell=True)

    if timeit:
        # time_limit = round_time(max_time) + extra_time

        # extra_time serve como parâmetro em relação a execução em C/C++,
        # mas esta medida de tempo já é realizada considerando a execução
        # da própria linguagem, portanto é viável ignorar.
        time_limit = round_time(max_time)
        utils.log('\nTempo máximo: {:0.3f} s (setup: {}).'
                  ''.format(max_time, time_limit))

        if set_time_limit:
            language = src_file.split('.')[-1]
            problem = base_dir.split('/')[-1]
            tex_file = base_dir + '/' + problem + '.tex'
            set_BOCA_time_limit(base_dir, language, time_limit)
            set_problem_description_time_limit(tex_file, time_limit)


def get_BOCA_time_limit(problem, language):
    file_name = '/'.join([problem.full_dir(), 'limits', language])

    if not os.path.isfile(file_name):
        file_name = './templates/limits/' + language

    with open(file_name, 'r') as f:
        from re import match
        for line in f:
            m = match('echo (\d+)', line)
            if m:
                return m.group(1)


def round_time(x):
    from math import ceil
    c = ceil(x)
    if (x / c) > 0.8:
        return c + 1
    return c


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


def set_problem_description_time_limit(tex_file, time_limit):
    pattern = 'LimiteDeTempo{\d+}%'
    repl = 'LimiteDeTempo{{{}}}%'.format(time_limit)
    utils.replace_first(pattern, repl, tex_file, tex_file)


def set_BOCA_time_limit(dir, language, time_limit):
    src = '/'.join([dir, 'limits', language])
    dest = src

    if not os.path.isfile(src):
        src = './templates/limits/' + language

    pattern = 'echo \d+'
    repl = 'echo {}'.format(time_limit)

    utils.replace_first(pattern, repl, src, dest)


def time_it(cmd, runs):
    setup = 'from subprocess import check_call'
    stmt = 'check_call(\'{}\', shell=True)'.format(cmd)

    from timeit import timeit
    return timeit(stmt, setup=setup, number=runs) / runs


if __name__ == '__main__':
    def check_runs(value):
        ivalue = int(value)
        if ivalue <= 0:
            raise ValueError('É preciso uma quantidade positiva '
                             'de execuções.')

        return ivalue

    def check_src(value):
        if not value:
            raise ValueError('É preciso especificar o arquivo com '
                             'a solução.')

        svalue = str(value)
        if not os.path.isfile(svalue):
            raise ValueError('Arquivo \'{}\' não encontrado.'
                             ''.format(svalue))

        return svalue

    def check_time(args):
        if args.time_limit and not args.timeit:
            raise ValueError('--time-limit requires --timeit.')

        if args.timeit:
            print('Cronometrando {} execuçõe(s) (por arquivo), isto '
                  'pode demorar um pouco...'.format(args.runs))

    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    parser = ArgumentParser(add_help=False,
                            description=' gerar arquivos de teste '
                                        '(entrada/saída) para um problema de '
                                        'um contest para a Maratona (BOCA).',
                            formatter_class=RawDescriptionHelpFormatter,
                            epilog='Exemplos de uso:\n'
                                   '\tpython %(prog)s in '
                                   'problems/0/facil/geninput.c\n'
                                   '\tpython %(prog)s out '
                                   'problems/0/facil/facil.c')

    parser.add_argument('-h', '--help', action='help',
                        help='mostrar esta mensagem e sair')

    subparsers = parser.add_subparsers(help='opções de uso', dest='command')

    sub_p = subparsers.add_parser('in', help='gerar arquivos de entrada',
                                  formatter_class=RawDescriptionHelpFormatter,
                                  add_help=False,
                                  epilog='Exemplo de uso:\n'
                                         '\tpython %(prog)s 2/led/geninput.c')

    sub_p.add_argument('-h', '--help', action='help',
                       help='mostrar esta mensagem e sair')
    sub_p.add_argument('src', type=check_src,
                       help='arquivo fonte com para gerar os casos de teste '
                            ' (deve estar no mesmo diretório do problema)')

    sub_p = subparsers.add_parser('out', help='gerar arquivos de saída',
                                  formatter_class=RawDescriptionHelpFormatter,
                                  add_help=False,
                                  epilog='Exemplo de uso:\n'
                                         '\tpython %(prog)s '
                                         'problems/9/ops/ops.c')

    sub_p.add_argument('src', type=check_src,
                       help='arquivo fonte com a solução a ser '
                       'aplicada (deve estar no mesmo diretório '
                       'do problema)')

    sub_p.add_argument('-h', '--help', action='help',
                       help='mostrar esta mensagem e sair')
    sub_p.add_argument('-l', dest='time_limit',
                       action='store_true',
                       help='incluir limite de tempo nas configurações e no '
                       'arquivo TeX da descrição')
    sub_p.add_argument('-q', '--quiet', dest='quiet',
                       action='store_true',
                       help='omitir os resultados do processo')
    sub_p.add_argument('-r', dest='runs',
                       type=check_runs, default=10,
                       help='quantidade de execuções a serem '
                       'cronometradas (default: %(default)s)')
    sub_p.add_argument('-t', dest='timeit',
                       action='store_true',
                       help='cronometrar execução da solução')

    args = parser.parse_args()

    if args.command == 'in':
        gen_input(args.src)
    elif args.command == 'out':
        check_time(args)
        gen_ouput(args.src, args.timeit, args.runs, args.time_limit)
