# -*- coding: utf-8 -*-
#   @package: utils.py
#    @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Arquivos necessários para funções utilitárias na criação de contests para o
# BOCA.


import os
from subprocess import check_call


TMPL = {'BOCA_DIRS': ['compare', 'compile', 'description', 'input',
                      'limits', 'output', 'run', 'tests'],
        'CONTEST_TEX': './templates/tex/contest.tex',
        'CONTEST_INFO_TEX': './templates/tex/contest_info.tex',
        'PROBLEM_TEX': './templates/tex/problem.tex',
        'GENINPUT': './templates/src/geninput.py3'}
VERBOSE = True


def log(msg):
    if VERBOSE:
        print(msg)


def copy(src, dest, flags=''):
    cmd = 'cp {} {} {}'.format(flags, src, dest)
    check_call(cmd, shell=True)
    log('Created ' + dest)


def fill_template(input_file, output_file, rpl_dict=None):
    with open(input_file, 'r') as f:
        content = f.read()

    if rpl_dict:
        from re import compile
        rx = compile('|'.join(rpl_dict.keys()))
        content = rx.sub(lambda m: rpl_dict[m.group(0)], content)

    with open(output_file, 'w') as f:
        f.write(content)
        log('Created ' + output_file)


def makedir(dir):
    if not os.path.isdir(dir):
        os.makedirs(dir)
        log('Created ' + dir)


def pdflatex(tex_file, output_dir):
    env = os.environ.copy()
    env['TEXINPUTS'] = '.:templates/tex//:'

    cmd = ['pdflatex', '-output-directory=' + output_dir,
           '-interaction=nonstopmode', '-halt-on-error', tex_file]
    DEVNULL = open(os.devnull, 'w')

    try:
        check_call(cmd, env=env, stdout=DEVNULL)
        check_call(cmd, env=env, stdout=DEVNULL)  # 2x para indexação correta
    except:
        check_call(cmd, env=env)  # Mostrar o erro

    # Remoção de arquivos auxiliares
    for dirpath, dirnames, filenames in os.walk(output_dir):
        for f in filenames:
            if not f.endswith('.pdf'):
                os.remove(os.path.join(dirpath, f))

    pdf_file = tex_file.replace('tex', 'pdf')
    log('Created {}/{}'.format(output_dir, pdf_file))
    return pdf_file


def remove_subdirs(base_dir):
    cmd = 'rm -rf {}/*/'.format(base_dir)
    check_call(cmd, shell=True)
    log('Removed ' + base_dir + '/*/')


def replace_first(pattern, repl, src_file, dest_file):
    with open(src_file, 'r') as f:
        from re import sub
        content = sub(pattern, repl, f.read(), 1)

    dest = os.path.dirname(dest_file)
    if not dest:
        dest = '.'
    if not os.path.isdir(dest):
        makedir(dest)

    with open(dest_file, 'w') as f:
        f.write(content)


def warning(msg):
    # 68 caracteres '*'
    print('\n'
          '**********************************'
          '**********************************\n'
          '* {:64s} *\n'
          '**********************************'
          '**********************************\n'.format(msg))


def zip_dir(src_dir, file_name):
    current_dir = os.getcwd()
    os.chdir(src_dir)
    cmd = 'zip ' + file_name + ' -q -r *'
    check_call(cmd, shell=True)
    os.chdir(current_dir)

    file_name = os.path.join(src_dir, file_name)
    log('Created ' + os.path.realpath(file_name))


class Language():
    def __init__(self, name, extension, setup, cmd, cleanup, extra_time):
        self.name = name
        self.extension = extension
        self.setup = setup
        self.cmd = cmd
        self.cleanup = cleanup
        self.extra_time = extra_time

    def run_stages(self, src_file):
        raise NotImplementedError


class CLang(Language):
    def __init__(self):
        setup = 'gcc -static -O2 -lm'
        cmd = './a.out'
        cleanup = 'rm a.out'
        extra_time = 0
        super(CLang, self).__init__('C', 'c', setup, cmd, cleanup, extra_time)

    def run_stages(self, src_file):
        return (self.setup + ' ' + src_file, self.cmd, self.cleanup,
                self.extra_time)


class CPPLang(CLang):
    def __init__(self):
        super(CPPLang, self).__init__()
        self.name = 'C++'
        self.extension = 'cpp'
        self.setup = 'g++ -static -O2 -lm'


class JavaLang(Language):
    def __init__(self):
        setup = 'javac'
        cmd = 'java'
        cleanup = 'rm a.out'
        extra_time = 2
        super(JavaLang, self).__init__('Java', 'java', setup, cmd, cleanup,
                                       extra_time)

    def run_stages(self, src_file):
        return (self.setup + ' ' + src_file, self.cmd, self.cleanup,
                self.extra_time)


PROGRAMMING_LANGUAGES = {'c': CLang(), 'cpp': CPPLang(), 'java': JavaLang()}
