#  -*- coding: utf-8 -*-
#    @package: problem.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
#
# Gera uma estrutura de arquivos inicial (dentro de um diretório que
# agrupa problemas com características similares), para criação de um
# problema no formato BOCA. Há uma opção de gerar um arquivo inicial (ou
# vários) para a solução na linguagem especificada. A estrutura é:
#   - característica
#       `- problema
#            |- input/          (diretório para os arquivos de teste)
#            |- output/         (diretório para os arquivos de teste)
#            |- geninput.py3    (programa para gerar a os dados de teste)
#            |- problema.tex    (arquivo com a descrição do problema)
#            `- problema.py2    ([opcional] arquivo para solução Python)


import utils


KNOWN_EXTENSIONS = ['c', 'cpp', 'py2', 'py3']


class Problem():
    def __init__(self, dir, name):
        self.dir = dir
        self.name = name

    def full_dir(self):
        return self.dir + '/' + self.name


def make_dirs(problem):
    utils.makedir(problem.dir)
    utils.makedir(problem.dir + '/' + problem.name)
    utils.makedir(problem.dir + '/' + problem.name + '/input')
    utils.makedir(problem.dir + '/' + problem.name + '/output')


def create_geninput_file(problem):
    file_name = '{}/geninput.py3'.format(problem.full_dir())
    utils.fill_template_file('geninput.py3', file_name)
    utils.warning('Não se esqueça de gerar as Entradas/Saídas de '
                  'teste do problema.')


def create_description_tex_file(problem):
    file_name = '{}/{}.tex'.format(problem.full_dir(), problem.name)
    utils.fill_template_file('problem.tex', file_name)
    utils.warning('Não se esqueça de preencher a descrição do '
                  'problema:             *\n*     '
                  './{:<58}'.format(file_name))


def create_solution_src_file(problem, solution):
    from os import walk
    for dirpath, dirnames, filenames in walk('./templates'):
        for f in filenames:
            file_ext = f.split('.')[-1]
            if file_ext in solution:
                src = 'templates/' + f
                dest = '{}/{}.{}'.format(problem.full_dir(),
                                         problem.name, file_ext)
                utils.copy(src, dest)

    utils.warning('Não se esqueça de gerar as soluções do problema.'
                  '                ')


def create(problem, solution):
    make_dirs(problem)
    create_description_tex_file(problem)
    create_geninput_file(problem)
    if solution:
        create_solution_src_file(problem, solution)


if __name__ == '__main__':
    def check_str(value):
        svalue = str(value)

        from re import match
        if not match(r'^\w+$', svalue):
            raise ValueError('\'' + svalue + '\' não é um '
                             'identificador válido.')
        return svalue

    def check_dir(value):
        svalue = check_str(value)

        if not svalue.startswith('./problems/'):
            return './problems/' + svalue
        return svalue

    from argparse import ArgumentParser, RawDescriptionHelpFormatter
    parser = ArgumentParser(add_help=False,
                            description='Geração/manipulação automática de '
                                        'arquivos de um problema para a '
                                        'Maratona (BOCA).',
                            formatter_class=RawDescriptionHelpFormatter,
                            epilog='Exemplo de uso:\n'
                                   '\tpython %(prog)s 2 led')

    parser.add_argument('dir', type=check_dir,
                        help='diretório onde criar o problema')
    parser.add_argument('-h', '--help', action='help',
                        help='mostrar esta mensagem e sair')
    parser.add_argument('problem', type=check_str,
                        help='identificador do problema')
    parser.add_argument('-q', '--quiet', dest='quiet',
                        action='store_true',
                        help='omitir os resultados do processo')
    parser.add_argument('-s', nargs='?', dest='solution',
                        default='NoneGiven',
                        choices=['all'] + KNOWN_EXTENSIONS,
                        help='criar um arquivo para implementação da '
                        'solução na linguagem especificada '
                        '(default: all).')

    args = parser.parse_args()
    if args.solution == 'NoneGiven':
        args.solution = None
    elif not args.solution or args.solution == 'all':
        args.solution = KNOWN_EXTENSIONS

    create(Problem(args.dir, args.problem), args.solution)
