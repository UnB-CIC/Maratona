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
            'CONTEST_DATE\n': '' if not date else '\\data{' + date + '}%\n'}


def copy_BOCA_dirs(orig, dest, boca_dirs=utils.Templates.BOCA.all_subdirs()):
    for dirpath, dirnames, filenames in os.walk(orig):
        for dir in dirnames:
            if dir in boca_dirs:
                utils.copy(os.path.join(dirpath, dir), os.path.join(dest, dir))


def create(problems, tex_file, root='.', date=None):
    problems = [find_problem(p) for p in problems]

    contest_name = os.path.splitext(tex_file)[0]
    root = os.path.join(root, contest_name)
    info_sheet = contest_name + '_info_sheet.tex'

    utils.log('=== Setup ===')
    utils.makedir(root)
    create_contest_tex(tex_file, problems, date)
    pdf_file = create_pdf_file(tex_file, root)
    create_contest_info_sheet_tex(info_sheet, problems, date)
    create_pdf_file(info_sheet, root)

    for problem in problems:
        utils.log('=== ' + problem.letter + ' - ' + problem.name + ' ===')
        create_zip_file(problem, os.path.join(root, problem.name), pdf_file)

    utils.log('=== Cleanup ===')
    remove_subdirs(root)


def create_contest_tex(tex_file, problems, date):
    def as_tex(problem):
        return '\t\\Problema[' + problem.dir + ']{' + problem.name + '}'

    rpl_dict = contest_rpl_dict(tex_file, date)
    rpl_dict['INDENTED_PROBLEMS'] = '\n'.join(as_tex(p) for p in problems)

    utils.fill_template(utils.Templates.TeX.contest(), tex_file, rpl_dict)


def create_contest_info_sheet_tex(tex_file, problems, date):
    def cmd(name, setup):
        return item(tt(name) + ': ' + tt(setup))

    def infos(lang_name, info):
        return (r'\makesection{' + tt(lang_name) + '}%\n'
                '\t{%' + ''.join('\n\t\t' + item(i) for i in info) +
                '\n\t}%')

    def item(content):
        return r'\item ' + content + '%'

    def tt(content):
        return '\\texttt{' + content + '}'

    def row(problem_info):
        return problem_info + r'\\\hline%'

    langs = sorted((lang.name, lang)
                   for lang in utils.PROGRAMMING_LANGUAGES.values())
    row_info = []
    for problem in problems:
        language_limits = ' & '.join(problem.get_time_limit(lang.extension)
                                     for _, lang in langs)
        row_info.append(' & '.join([problem.letter, problem.full_name,
                                    language_limits]))

    rpl_dict = contest_rpl_dict(tex_file, date)

    # time limits
    rpl_dict['LANGUAGE_COLUMNS'] = ' c' * len(langs)
    rpl_dict['LANGUAGE_NAMES'] = ' & '.join(tt(n) for n, _ in langs)
    rpl_dict['PROBLEM_INFO'] = '\n\t\t\t'.join(row(p) for p in row_info)

    rpl_dict['COMPILATION_COMMANDS'] = '\n\t\t'.join(cmd(name, lang.setup(''))
                                                     for name, lang in langs
                                                     if lang.setup(''))

    rpl_dict['LANGUAGE_INFO'] = '\n\t'.join(infos(name,
                                                  lang.info_sheet(problems))
                                            for name, lang in langs
                                            if lang.info_sheet(problems))

    utils.fill_template(utils.Templates.TeX.info_sheet(), tex_file, rpl_dict)


def create_info_file(dest_dir, problem, pdf_file):
    desc_dir = dest_dir + '/description'
    desc_file = desc_dir + '/problem.info'
    rpl_dict = {'BASE_NAME': problem.letter,
                'FULL_NAME': problem.full_name,
                'DESCRIPTION_FILE': pdf_file}

    utils.fill_template(desc_file, desc_file, rpl_dict)


def create_zip_file(problem, dest_dir, pdf):
        utils.makedir(dest_dir)
        copy_BOCA_dirs(utils.Templates.BOCA.dir(), dest_dir)  # Padrão
        boca_dirs = ['input', 'output', 'limits']  # Específicos
        copy_BOCA_dirs(problem.full_dir, dest_dir, boca_dirs)
        create_info_file(dest_dir, problem, pdf)
        zip_dir(dest_dir, '../{}'.format(problem.letter))


def create_pdf_file(tex_file, root):
    return utils.pdflatex(tex_file, root)


def find_problem(problem):
    for dirpath, dirnames, filenames in os.walk('.'):
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


def remove_subdirs(root):
    for dirpath, dirnames, filenames in os.walk(root):
        for dir in dirnames:
            from shutil import rmtree
            dir = os.path.join(dirpath, dir)
            rmtree(dir)
            utils.log('Removed ' + dir)


def zip_dir(file_dir, file_name):
    from shutil import make_archive
    file_name = os.path.join(file_dir, file_name)
    file_name = make_archive(file_name, 'zip', file_dir)

    utils.log('Created ' + file_name)


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
    parser.add_argument('-d', dest='root',
                        type=str, default='/tmp',
                        help='diretório onde criar os arquivos '
                        '(default: %(default)s)')
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
    parser.add_argument('--date', dest='date', type=str,
                        help='data da prova')

    args = parser.parse_args()
    if args.random:
        problems = random_problems(args.ids)
    else:
        from collections import OrderedDict
        problems = list(OrderedDict.fromkeys(p for p in args.ids))

    create(problems, args.tex_file, args.root, args.date)
