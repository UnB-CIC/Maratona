#  -*- coding: utf-8 -*-
#    @package: problem.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)


from os.path import join as os_path_join

import utils


class Problem():
    '''Define um problema.'''
    letter = 'A'

    def __init__(self, dir, name):
        self.dir = dir
        self.name = name
        self.__full_name = None
        self.__time_limits = {}
        self.letter = Problem.letter
        Problem.letter = chr(ord(Problem.letter) + 1)

    @property
    def full_dir(self):
        return os_path_join(self.dir, self.name)

    @property
    def full_name(self):
        if not self.__full_name:
            full_name = utils.first_occurrence(r'\NomeDoProblema{(.*?)}',
                                               self.tex_file)

            if not full_name:
                raise ValueError('Nome completo do problema não definido '
                                 'no arquivo \'' + self.tex_file + '\'.')

            self.__full_name = full_name

        return self.__full_name

    @property
    def tex_file(self):
        return '{}/{}.tex'.format(self.full_dir, self.name)

    def get_time_limit(self, language):
        if language not in self.__time_limits:
            file_name = os_path_join(self.full_dir, 'limits', language)

            from os.path import isfile
            if not isfile(file_name):
                file_name = utils.Templates.BOCA.limits(language)

            time_limit = utils.first_occurrence(r'echo (\d+)', file_name)
            if not time_limit:
                raise ValueError('Limite de tempo não definido no arquivo '
                                 '\'' + file_name + '\'.')

            self.__time_limits[language] = time_limit

        return self.__time_limits[language]

    def set_time_limit(self, time_limit, language):
        orig = dest = os_path_join(self.full_dir, 'limits', language)

        from os.path import isfile
        if not isfile(orig):
            orig = utils.Templates.BOCA.limits(language)
        if not isfile(orig):
            raise ValueError('Limite não definido para \'{}\'.'
                             ''.format(language))

        pattern = 'echo \d+'
        repl = 'echo {}'.format(time_limit)
        utils.replace_first(pattern, repl, orig, dest)


def make_dirs(problem):
    utils.makedir(problem.dir)
    utils.makedir(os_path_join(problem.dir, problem.name))
    utils.makedir(os_path_join(problem.dir, problem.name, 'input'))
    utils.makedir(os_path_join(problem.dir, problem.name, 'output'))


def create_description_tex_file(problem):
    utils.fill_template(utils.Templates.TeX.problem(), problem.tex_file)
    utils.warning('Não se esqueça de preencher a descrição do '
                  'problema:             *\n*     '
                  '{:<58}'.format(problem.tex_file))


def create_geninput_file(problem):
    utils.copy(utils.Templates.Source.geninput(), problem.full_dir)


def create_solution_src_file(problem, solution):
    from os import walk
    for dirpath, dirnames, filenames in walk(utils.Templates.Source.dir()):
        for file_name in filenames:
            file_ext = file_name.split('.')[-1]
            if file_ext in solution:
                src_file = problem.name + '.' + file_ext
                orig = os_path_join(utils.Templates.Source.dir(), file_name)
                dest = os_path_join(problem.full_dir, src_file)
                utils.copy(orig, dest)

    utils.warning('Não se esqueça de gerar as soluções do problema.'
                  '                ')


def create(problem, solution):
    make_dirs(problem)
    create_geninput_file(problem)
    create_description_tex_file(problem)
    if solution:
        create_solution_src_file(problem, solution)


if __name__ == '__main__':
    languages = [k for k in utils.PROGRAMMING_LANGUAGES.keys()]

    def check_lang(value):
        svalue = str(value)
        if not value or svalue == 'all':
            return languages
        return svalue

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
                        default='all',
                        choices=['all'] + languages,
                        help='criar um arquivo para implementação da '
                        'solução na linguagem especificada '
                        '(default: all).')

    args = parser.parse_args()
    create(Problem(args.dir, args.problem), check_lang(args.solution))
