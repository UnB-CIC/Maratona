# -*- coding: utf-8 -*-
#   @package: utils.py
#    @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Arquivos necessários para funções utilitárias na criação de contests para o
# BOCA.


import os
from subprocess import check_call


VERBOSE = True


def log(msg):
    if VERBOSE:
        print(msg)


def copy(src, dest, flags=''):
    cmd = 'cp {} {} {}'.format(flags, src, dest)
    check_call(cmd, shell=True)
    log('Created ' + dest)


def fill_template_file(input_file, output_file, rpl_dict=None):
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
    from subprocess import Popen
    from os import environ
    maratona_env = environ.copy()
    maratona_env['TEXINPUTS'] = '.:templates/problems//:'

    cmd = ['pdflatex', '-output-directory=' + output_dir,
           '-interaction=nonstopmode', '-halt-on-error', tex_file]
    DEVNULL = open(os.devnull, 'w')

    with Popen(cmd, stdout=DEVNULL, env=maratona_env) as proc:
        output, error = proc.communicate()
        if proc.returncode != 0:
            with Popen(cmd, env=maratona_env) as proc:
                # output, error = proc.communicate()
                raise RuntimeError('Erro ao gerar o PDF.')  # Mostrar o erro
        else:
            with Popen(cmd, stdout=DEVNULL, env=maratona_env) as proc:
                pass  # 2x para indexação correta

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
