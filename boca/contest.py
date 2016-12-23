#  -*- coding: utf-8 -*-
#    @package: contest.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)


import os
from time import strftime

import utils
from problem import Problem


def contest_rpl_dict(file_name, date):
    return {'FILE_NAME': file_name,
            'FILE_DATE': strftime('%d/%m/%Y'),
            'CONTEST_DATE\n': '\data{{{}}}\n%'.format(date) if date else ''}


def copy_BOCA_dirs(src, dest):
    for dirpath, dirnames, filenames in os.walk(src):
        for dir in dirnames:
            if dir in utils.TMPL['BOCA_DIRS']:
                    utils.copy(dirpath + '/' + dir,
                               dest + '/' + dir,
                               '-Tr')


def create_contest_tex(tex_file, problems, date):
    def as_tex(problem):
        return '\t\\Problema[{}]{{{}}}%'.format(problem.dir, problem.name)

    rpl_dict = contest_rpl_dict(tex_file, date)
    rpl_dict['INDENTED_PROBLEMS'] = '\n'.join(as_tex(p) for p in problems)

    utils.fill_template(utils.TMPL['CONTEST_TEX'], tex_file, rpl_dict)


def create_contest_info_tex(tex_file, problems, date):
    def as_tex(lang):
        return '\\texttt{{{}}}'.format(lang)

    def as_row(problem_info):
        return '{} \\\\\\hline%'.format(problem_info)

    languages = sorted((lang.name, lang.extension)
                       for lang in utils.PROGRAMMING_LANGUAGES.values())
    problem_row = []
    for problem in problems:
        language_limits = ' & '.join(problem.get_time_limit(ext)
                                     for _, ext in languages)
        problem_row.append(' & '.join([problem.letter, problem.full_name(),
                                       language_limits]))

    rpl_dict = contest_rpl_dict(tex_file, date)
    rpl_dict['LANGUAGE_COLUMNS'] = ' c' * len(utils.PROGRAMMING_LANGUAGES)
    rpl_dict['LANGUAGE_NAMES'] = ' & '.join(as_tex(n) for n, _ in languages)
    rpl_dict['PROBLEM_INFO'] = '\n\t\t\t'.join(as_row(p) for p in problem_row)

    utils.fill_template(utils.TMPL['CONTEST_INFO_TEX'], tex_file, rpl_dict)


def create_info_file(target_dir, problem, pdf_file):
    desc_dir = target_dir + '/description'
    desc_file = desc_dir + '/problem.info'
    rpl_dict = {'BASE_NAME': problem.letter,
                'FULL_NAME': problem.full_name(),
                'DESCRIPTION_FILE': pdf_file}

    utils.fill_template(desc_file, desc_file, rpl_dict)


def create_zip_file(problem, target_dir, pdf):
        utils.makedir(target_dir)
        copy_BOCA_dirs('./templates', target_dir)       # Padrão
        copy_BOCA_dirs(problem.full_dir(), target_dir)  # Específicos
        create_info_file(target_dir, problem, pdf)
        utils.zip_dir(target_dir, '../{}.zip'.format(problem.letter))


def create_pdf_file(tex_file, base_dir):
    return utils.pdflatex(tex_file, base_dir)


def dir_problem_tuple(problem, base_dir='.'):
    for dirpath, dirnames, filenames in os.walk(base_dir):
        if problem in dirnames:
            return Problem(dirpath, problem)
    raise ValueError('Problema \'' + problem + '\'não encontrado.')


def random_problems(dirs):
    def prefix(dirs):
        d = []
        for dir in dirs:
            if not dir.startswith('./problems/'):
                dir = './problems/' + dir
            d.append(dir)
        return d

    def at_least(n, dir):
        for dirpath, dirnames, filenames in os.walk(dir):
            if len(dirnames) < n:
                raise ValueError('Não há {} problemas em \'{}\'.'
                                 ''.format(n, dir))
            return dirnames

    dirs = prefix(dirs)
    all_problems = {}
    for dir in dirs:
        n = dirs.count(dir)
        all_problems[dir] = {'n': n, 'problems': at_least(n, dir)}

    from random import sample, shuffle
    random_problems = []
    for dir_list in all_problems.values():
        random_problems.extend(sample(dir_list['problems'], dir_list['n']))
    shuffle(random_problems)
    return random_problems


def create(problems, tex_file, base_dir='.', date=None):
    contest_name = tex_file[:-4]
    problems = [dir_problem_tuple(p) for p in problems]

    base_dir += '/' + contest_name

    utils.makedir(base_dir)
    create_contest_tex(tex_file, problems, date)
    pdf_file = create_pdf_file(tex_file, base_dir)
    create_contest_info_tex(contest_name + '_info.tex', problems, date)
    create_pdf_file(contest_name + '_info.tex', base_dir)

    for problem in problems:
        utils.log('=== {} - {} ==='.format(problem.letter, problem.name))
        target_dir = base_dir + '/' + problem.name
        create_zip_file(problem, target_dir, pdf_file)

    utils.remove_subdirs(base_dir)


if __name__ == '__main__':
    def check_tex(value):
        svalue = str(value)
        if not svalue or not svalue.lower().endswith('.tex'):
            raise ValueError('Arquivo \'' + svalue + '\' não é TeX.')

        if os.path.isfile(svalue):
            utils.warning('O arquivo \'' + svalue + '\' será sobrescrito.')
        return svalue

    from argparse import ArgumentParser, RawDescriptionHelpFormatter
    parser = ArgumentParser(add_help=False,
                            description='Geração/manipulação automática de '
                                        'arquivos de um contest para a '
                                        'Maratona (BOCA).',
                            formatter_class=RawDescriptionHelpFormatter,
                            epilog='Exemplos de uso:\n'
                                   '\tpython %(prog)s fizzbuzz easyled\n'
                                   '\tpython %(prog)s -r 0 0 1 2\n\n')

    parser.add_argument('ids', nargs='+', type=str,
                        help='identificador(es) de problema(s) ou '
                        'diretório(s)')
    parser.add_argument('-d', dest='base_dir',
                        type=str, default='/tmp',
                        help='diretório onde criar os arquivos '
                        '(default: %(default)s)')
    parser.add_argument('--data', dest='date', type=str,
                        help='data da prova')
    parser.add_argument('-h', '--help', action='help',
                        help='mostrar esta mensagem e sair')
    parser.add_argument('-q', '--quiet', dest='quiet',
                        action='store_true',
                        help='omitir os resultados do processo')
    parser.add_argument('-r', '--random', dest='random',
                        action='store_true',
                        help='criar uma prova aleatória')
    parser.add_argument('-t', dest='tex_file', type=check_tex,
                        default=strftime('%Y-%m-%d.tex'),
                        help='nome do arquivo TeX '
                        '(default: %(default)s)')

    args = parser.parse_args()
    if args.random:
        problems = random_problems(args.ids)
    else:
        from collections import OrderedDict
        problems = list(OrderedDict.fromkeys(p for p in args.ids))

    create(problems, args.tex_file, args.base_dir, args.date)
