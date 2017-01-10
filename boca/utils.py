# -*- coding: utf-8 -*-
#   @package: utils.py
#    @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Arquivos necessários para funções utilitárias na criação de contests para o
# BOCA.


import os
from subprocess import check_call


class Templates():
    @staticmethod
    def dir():
        return './templates'

    class BOCA():
        @staticmethod
        def dir():
            return Templates.dir() + '/boca'

        @staticmethod
        def all_subdirs():
            return ['compare', 'compile', 'description', 'input',
                    'limits', 'output', 'run', 'tests']

        @staticmethod
        def compile(extension=None):
            if extension:
                return Templates.BOCA.dir() + '/compile/' + extension
            return Templates.BOCA.dir() + '/compile'

        @staticmethod
        def limits(language=None):
            if language:
                return Templates.BOCA.dir() + '/limits/' + language
            return Templates.BOCA.dir() + '/limits'

    class Source():
        @staticmethod
        def dir():
            return Templates.dir() + '/src'

        @staticmethod
        def geninput():
            return Templates.Source.dir() + '/geninput.py3'

    class TeX():
        @staticmethod
        def dir():
            return Templates.dir() + '/tex'

        @staticmethod
        def contest():
            return Templates.TeX.dir() + '/contest.tex'

        @staticmethod
        def info_sheet():
            return Templates.TeX.dir() + '/info_sheet.tex'

        @staticmethod
        def problem():
            return Templates.TeX.dir() + '/problem.tex'


VERBOSE = True


def log(msg):
    if VERBOSE:
        print(msg)


def copy(orig, dest):
    if os.path.isfile(orig):
        from shutil import copy2
        copy2(orig, dest)
    else:
        from shutil import copytree
        copytree(orig, dest)
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


def first_occurrence(regex, file_name):
    with open(file_name, 'r') as f:
        content = f.read()

    from re import search
    occurrence = search(regex, content)

    return None if not occurrence else occurrence.groups(0)[0]


def makedir(dir):
    if not os.path.isdir(dir):
        os.makedirs(dir)
        log('Created ' + dir)


def pdflatex(tex_file, output_dir):
    env = os.environ.copy()
    env['TEXINPUTS'] = '.:' + Templates.TeX.dir() + '//:'

    cmd = ['pdflatex', '-output-directory=' + output_dir,
           '-interaction=nonstopmode', '-halt-on-error', tex_file]
    with open(os.devnull, 'w') as DEVNULL:
        try:
            check_call(cmd, env=env, stdout=DEVNULL)
            check_call(cmd, env=env, stdout=DEVNULL)  # 2x para indexação
        except:
            check_call(cmd, env=env)  # Mostrar o erro

    # Remoção de arquivos auxiliares
    for dirpath, dirnames, filenames in os.walk(output_dir):
        for f in filenames:
            if not f.endswith('.pdf'):
                os.remove(os.path.join(dirpath, f))

    pdf_file = tex_file.replace('tex', 'pdf')
    log('Created ' + os.path.join(output_dir, pdf_file))
    return pdf_file


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
    log('Created ' + dest_file)


def warning(msg):
    LINE_LENGTH = 70
    separator = '*' * LINE_LENGTH
    print('\n' + separator)

    if isinstance(msg, str):
        msg = [msg]

    for line in msg:
        print('* {0:{1}} *'.format(line, LINE_LENGTH - 4))

    print(separator + '\n')


class Language():
    '''Define as configurações de uma linguagem de programação'''
    def __init__(self, name, extension):
        self.name = name
        self.extension = extension

    def run_stages(self, src_file):
        '''Os comandos para execução de um arquivo fonte.
        1. Preparação para execução (compilação)
        2. Execução
        3. Remoção de arquivos
        '''
        ## to-do Usar os (ou outra coisa independente do sistema operacional)
        return (self.setup(src_file),
                self.execute(src_file),
                self.cleanup(src_file))

    def setup(self, src_file):
        '''Comando de preparação para execução.'''
        raise NotImplementedError

    def execute(self, src_file):
        '''Comando de execução do arquivo.'''
        raise NotImplementedError

    def cleanup(self, src_file):
        '''Comando de remoção de arquivos.'''
        raise NotImplementedError

    def info_sheet(self, problems=None):
        '''Informações adicionais sobre a linguagem'''
        return ''


class BOCALanguage(Language):
    '''Busca as configurações de uma linguagem para ser usada na BOCA.'''
    def __init__(self, name, extension, compiler_regex,
                 compilation_flags_regex):
        super(BOCALanguage, self).__init__(name, extension)

        compiler = self.__search_compile__(extension, compiler_regex)
        compilation_flags = self.__search_compile__(extension,
                                                    compilation_flags_regex)

        self.boca_compile = compiler + ' ' + compilation_flags

    def __search_compile__(self, extension, regex):
        if not regex:
            raise NotImplementedError('É preciso definir como encontrar '
                                      'a configuração de compilação.')

        file_name = Templates.BOCA.compile(extension)

        return first_occurrence(regex, file_name)

    def setup(self, src_file):
        return self.boca_compile + ' ' + src_file


class CLang(BOCALanguage):
    def __init__(self, name='C', extension='c',
                 compiler_regex=r'cc=\\\`which (.*?)\\\`',
                 compilation_flags_regex=r'\"\\\$cc\" (.*?) -o'):
        super(CLang, self).__init__(name, extension, compiler_regex,
                                    compilation_flags_regex)

    def execute(self, src_file):
        return './a.out'

    def cleanup(self, src_file):
        return 'rm a.out'

    def info_sheet(self, problems):
        return ['Seu programa deve retornar 0 como último comando executado.']


class CPPLang(CLang):
    def __init__(self):
        super(CPPLang, self).__init__('C++', 'cpp')


class JavaLang(BOCALanguage):
    def __init__(self):
        super(JavaLang, self).__init__('Java', 'java',
                                       r'javac=\`which (javac)\`',
                                       r'\\\$javac (.*?)\"\$name\"')

    def execute(self, src_file):
        return 'java ' + ''.join(src_file.split('.')[:-1]) + '.jar'

    def cleanup(self, src_file):
        return 'rm ' + ''.join(src_file.split('.')[:-1]) + '.jar'

    def info_sheet(self, problems):
        if len(problems) == 1:
            letters = problems[0].letter
        elif len(problems) < 5:
            letters = ', '.join(p.letter for p in problems[:-1])
            letters += ' e ' + problems[-1].letter
        else:
            letters = problems[0].letter + ', ' + \
                problems[1].letter + ', $\dots$ e ' + \
                problems[-1].letter

        ## to-do ler as configurações de execução do arquivo
        return ['Não declare um pacote em seu programa.',
                'O nome do arquivo deve seguir a convenção, portanto o nome '
                'da sua classe pública deve ser uma letra maiúscula '
                '(' + letters + ').',
                'Comando para executar uma solução: '
                'java -Xms1024m -Xmx1024m -Xss20m']


class PythonLang(Language):
    def __init__(self, version):
        self.version = version
        super(PythonLang, self).__init__('Python' + str(version),
                                         'py' + str(version))

    def setup(self, src_file):
        return ''

    def execute(self, src_file):
        return 'python{} {} '.format(self.version, src_file)

    def cleanup(self, src_file):
        return ''

    def info_sheet(self, problems):
        return ['Cuidado ao informar a versão, use a extensão {} para a '
                'versão {}.'.format(self.extension, self.version)]


PROGRAMMING_LANGUAGES = {'c': CLang(), 'cpp': CPPLang(), 'java': JavaLang()}
# 'py2': PythonLang(2), 'py3': PythonLang(3)}


if __name__ == '__main__':
    pass
