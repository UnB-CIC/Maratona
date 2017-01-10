#  -*- coding: utf-8 -*-
#    @package: io.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)


from copy import deepcopy
import os
from subprocess import check_call

import utils


programming_languages = deepcopy(utils.PROGRAMMING_LANGUAGES)
programming_languages['py2'] = utils.PythonLang(2)
programming_languages['py3'] = utils.PythonLang(3)


def natural_sort(l):
    # http://stackoverflow.com/questions/4836710/does-python-have-a-built-in-function-for-string-natural-sort#4836734
    def convert(text):
        return int(text) if text.isdigit() else text.lower()

    def alphanum(key):
        from re import split
        return [convert(c) for c in split('([0-9]+)', key)]

    return sorted(l, key=alphanum)


def gen_input(src_file):
    current_dir = os.getcwd()
    root = os.path.dirname(src_file)
    src_file = os.path.basename(src_file)
    ext = src_file.split('.')[-1].lower()

    language = programming_languages[ext]
    setup, cmd, cleanup = language.run_stages(src_file)

    os.chdir(root)

    if setup:
        check_call(setup, shell=True)

    check_call(cmd, shell=True)

    if cleanup:
        check_call(cleanup, shell=True)

    os.chdir(current_dir)


def gen_ouput(src_file, timeit, runs=0, set_time_limit=False):
    root = os.path.dirname(src_file)
    ext = src_file.split('.')[-1].lower()

    language = programming_languages[ext]
    setup, bash_cmd, cleanup = language.run_stages(src_file)

    if setup:
        check_call(setup, shell=True)

    max_time = 0
    input_dir = root + '/input'
    for (dirpath, dirnames, filenames) in os.walk(input_dir):
        for f in natural_sort(filenames):
            input_file = '{}/input/{}'.format(root, f)
            output_file = '{}/output/{}'.format(root, f)
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
        utils.log('\nTempo máximo medido: {:0.3f}s.'.format(max_time))

        from problem import Problem
        dir, name = os.path.split(root)
        problem = Problem(dir, name)

        time_limit = round_time(max_time)
        if set_time_limit:
            problem.set_time_limit(time_limit, ext)
        else:
            current_time_limit = int(problem.get_time_limit(ext))
            if current_time_limit != time_limit:
                utils.warning('O tempo medido foi de {}s, mas a configuração '
                              'atual é de {}s.     '
                              ''.format(time_limit, current_time_limit))

        utils.warning('Atenção aos tempos de linguagens diferentes!')


def round_time(x):
    from math import ceil
    c = ceil(x)
    return c if (x / c) <= 0.8 else  c + 1


def time_it(cmd, runs):
    from timeit import timeit
    setup = 'from subprocess import check_call'
    stmt = 'check_call(\'{}\', shell=True)'.format(cmd)

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
            print('Cronometrando {} execuções (por arquivo), isto '
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
