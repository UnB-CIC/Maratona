#  -*- coding: utf-8 -*-
#    @package: problem.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)


import utils


class Problem():
    letter = 'A'

    def __init__(self, dir, name):
        self.dir = dir
        self.name = name
        self._full_name_ = None
        self._limits_ = {}
        self.letter = Problem.letter
        Problem.letter = chr(ord(Problem.letter) + 1)

    def full_dir(self):
        return self.dir + '/' + self.name

    def full_name(self):
        if not self._full_name_:
            with open(self.tex_file(), 'r') as f:
                content = f.read()

            from re import search
            full_name = search(r'\NomeDoProblema{(.*?)}', content)

            if not full_name:
                raise ValueError('Nome completo do problema não definido '
                                 'no arquivo \'' + self.tex_file() + '\'.')

            self._full_name_ = full_name.groups(0)[0]

        return self._full_name_

    def tex_file(self):
        return '{}/{}.tex'.format(self.full_dir(), self.name)

    def get_time_limit(self, language):
        if language not in self._limits_:
            file_name = '/'.join([self.full_dir(), 'limits', language])

            from os.path import isfile
            if not isfile(file_name):
                file_name = './templates/limits/' + language
            if not isfile(file_name):
                raise ValueError('Limite não definido para \'{}\'.'
                                 ''.format(language))

            with open(file_name, 'r') as f:
                content = f.read()

            from re import search
            time_limit = search(r'echo (\d+)', content)

            if not time_limit:
                raise ValueError('Limite de tempo não definido no arquivo '
                                 '\'' + file_name + '\'.')

            self._limits_[language] = time_limit.groups(0)[0]

        return self._limits_[language]

    def set_time_limit(self, time_limit, language):
        src = '/'.join([self.full_dir(), 'limits', language])
        dest = src

        from os.path import isfile
        if not isfile(src):
            src = './templates/limits/' + language
        if not isfile(src):
            raise ValueError('Limite não definido para \'{}\'.'
                             ''.format(language))

        pattern = 'echo \d+'
        repl = 'echo {}'.format(time_limit)

        from utils import replace_first
        replace_first(pattern, repl, src, dest)


def make_dirs(problem):
    utils.makedir(problem.dir)
    utils.makedir(problem.dir + '/' + problem.name)
    utils.makedir(problem.dir + '/' + problem.name + '/input')
    utils.makedir(problem.dir + '/' + problem.name + '/output')


def create_description_tex_file(problem):
    file_name = '{}/{}.tex'.format(problem.full_dir(), problem.name)
    utils.fill_template(utils.TMPL['PROBLEM_TEX'], file_name)
    utils.warning('Não se esqueça de preencher a descrição do '
                  'problema:             *\n*     '
                  '{:<58}'.format(file_name))


def create_geninput_file(problem):
    utils.copy(utils.TMPL['GENINPUT'], problem.full_dir())


def create_solution_src_file(problem, solution):
    from os import walk
    for dirpath, dirnames, filenames in walk('./templates/problems/src'):
        for f in filenames:
            file_ext = f.split('.')[-1]
            if file_ext in solution:
                src = './templates/src/' + f
                dest = '{}/{}.{}'.format(problem.full_dir(),
                                         problem.name, file_ext)
                utils.copy(src, dest)

    utils.warning('Não se esqueça de gerar as soluções do problema.'
                  '                ')


def create(problem, solution):
    make_dirs(problem)
    create_geninput_file(problem)
    create_description_tex_file(problem)
    if solution:
        create_solution_src_file(problem, solution)


if __name__ == '__main__':
    languages = [k for k in utils.PROGRAMMING_LANGUAGES]

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
                        choices=['all'] + languages,
                        help='criar um arquivo para implementação da '
                        'solução na linguagem especificada '
                        '(default: all).')

    args = parser.parse_args()
    if args.solution == 'NoneGiven':
        args.solution = None
    elif not args.solution or args.solution == 'all':
        args.solution = languages

    create(Problem(args.dir, args.problem), args.solution)
