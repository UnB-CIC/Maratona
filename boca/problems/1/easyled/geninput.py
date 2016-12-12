# -*- coding: utf-8 -*-
#    Arquivo: genio.py
#   Objetivo: Gerar dados de Entrada/Saída para o problema.


from os import walk
from subprocess import call


# Gerar casos de teste (input)
from random import randint

for test_num in range(1, 10):
    with open('input/{}'.format(test_num), 'w') as f:
        f.write('{}\n'.format(test_num))
    with open('input/{}'.format(test_num + 9), 'w') as f:
        num = randint(2, 2 * (10 ** 6))
        f.write('{}\n'.format(num))

with open('input/19', 'w') as f:
    f.write('0\n')
with open('input/20', 'w') as f:
    f.write('2000000\n')


# Gerar casos de teste (output)
def _check_src(value):
    if not value:
        raise(ValueError('É preciso especificar o arquivo com a solução.'))

    str_value = str(value)

    from os.path import isfile
    if not isfile(str_value):
        raise(ValueError('Arquivo \'{}\' não encontrado.'.format(str_value)))

    return str_value


def _check_runs(value):
    i_value = int(value)
    if i_value <= 0:
        raise(ValueError('É preciso uma quantidade positiva de execuções.'))

    return i_value


def _language_specs(src_file):
    def compile_C(src_file):
        return 'gcc -lm -O3 ' + src_file

    def compile_CPP(src_file):
        return 'g++ -lm -O3 -std=c++11 ' + src_file

    ext = src_file.split('.')[-1].lower()

    #  {ext:  (language, setup, bash_exec, cleanup)}
    SPECS = {'py': ('Python2', None, 'python2 ' + src_file, None),
             'py2': ('Python2', None, 'python2 ' + src_file, None),
             'py3': ('Python3', None, 'python3 ' + src_file, None),
             'c': ('C', compile_C(src_file), './a.out', 'rm a.out'),
             'cpp': ('C++', compile_CPP(src_file), './a.out', 'rm a.out')}

    if ext not in SPECS:
        raise(ValueError('Tipo de arquivo \'' + ext + '\' desconhecido.'))

    return SPECS[ext]


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser(description='Gerar arquivos de Entrada/Saída de '
                                        'dados de teste para um problema')

    parser.add_argument('src_file', type=_check_src)
    parser.add_argument('-t', dest='timeit', action='store_false')
    parser.add_argument('-r', dest='runs', type=_check_runs, default=100)
    parser.add_argument('-q', dest='quiet', action='store_true')

    args = parser.parse_args()
    lang, setup, executable, cleanup = _language_specs(args.src_file)

    if setup:
        call(setup, shell=True)

    max_time = 0
    for (dirpath, dirnames, filenames) in walk('input'):
        for f in sorted(filenames):
            in_file = 'input/' + f
            out_file = 'output/' + f

            cmd = '{} < {} > {}'.format(executable, in_file, out_file)
            if args.timeit:
                from timeit import timeit
                setup = 'from subprocess import call'
                stmt = 'call(\'{}\', shell=True)'.format(cmd)
                t = timeit(stmt, setup=setup, number=args.runs) / args.runs
                max_time = max(t, max_time)

                log = '{:<9} -> {:<10} ({:0.3f}s)'.format(in_file, out_file, t)
            else:
                call(cmd, shell=True)
                log = '{:<9} -> {:<10}'.format(in_file, out_file)

            if not args.quiet:
                print(log)

    if not args.quiet and args.timeit:
        print('\ntempo médio máximo: {:0.3f} s.'.format(max_time))
        from math import ceil
        time_limit = str(ceil(max_time))
        print('Setup para {}s'.format(time_limit))

        import re
        with open('description.tex', 'r') as f:
            lines = f.readlines()
        lines = ''.join(lines)
        matches = re.findall('LimiteDeTempo{(.*?)}', lines)
        if matches:
            tex_time_limit = 'LimiteDeTempo{{{}}}'.format(time_limit)
            lines = re.sub('LimiteDeTempo{(.*?)}', tex_time_limit, lines)
        else:
            matches = re.findall('\\NomeDoProblema(.*?)\n', lines)
            tex_time_limit = '\n\\LimiteDeTempo{{{}}}%'.format(time_limit)
            for line in matches:
                lines = re.sub(line, line + tex_time_limit, lines)
        with open('description.tex', 'w') as f:
            f.write(lines)

    if cleanup:
        call(cleanup, shell=True)
