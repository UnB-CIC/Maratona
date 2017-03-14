# -*- coding: utf-8 -*-
#   @package: users.py3
#    @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Gera os arquivos necessários para criação de usuários para o BOCA.


def config(user_id, usertype, fullname, description, multilogin=0):
    usertype = usertype.lower()
    number = 'usernumber={}'.format(user_id)
    sitenumber = 'usersitenumber={}'.format(1)
    name = 'username={}{}'.format(usertype, user_id)
    fullname = 'userfullname={}'.format(fullname)
    enabled = 'userenabled=1'
    usertype = 'userusertype={}'.format(usertype)
    desc = 'userdesc={}'.format(description)
    pwd = 'userpassword=' + password()
    multilogin = 'usermultilogin={}'.format(multilogin)

    return '\n'.join(['', number, sitenumber, name, fullname, enabled,
                      usertype, desc, pwd, multilogin, ''])


def create_staff(judges, staff, scores):
    with open('staff.txt', 'w') as f:
        f.write('[user]\n')
        for j in range(1001, 1001 + judges):
            cnf = config(j, 'judge', 'Judge ' + str(j), 'Juiz', 1)
            f.write(cnf)
        for s in range(2001, 2001 + staff):
            cnf = config(s, 'staff', 'Staff ' + str(s), 'Staff', 1)
            f.write(cnf)
        for s in range(3001, 3001 + scores):
            cnf = config(s, 'score', 'Score ' + str(s), 'Placar', 1)
            f.write(cnf)


def create_users(teams, desc):
    from random import shuffle
    shuffle(teams)
    with open('txt', 'w') as f:
        f.write('[user]\n')
        user_id = 1
        for school, team in teams:
            cnf = config(user_id, 'team',
                         '[{}] {}'.format(school, team), desc, 1)
            f.write(cnf)
            user_id += 1


def get_teams(csv_file):
    from csv import reader
    with open(csv_file, newline='') as f:
        teams = [(team[0].strip(), team[1].strip()) for team in reader(f)]
    return teams


def password(num_chars=6):
    from random import choice
    return ''.join([choice('0123456789') for x in range(num_chars)])


if __name__ == '__main__':
    def check_users(value):
        ivalue = int(value)
        if ivalue < 1:
            raise ValueError('É preciso ter pelo menos 1 usuário.')
        return ivalue

    from argparse import ArgumentParser, RawDescriptionHelpFormatter
    parser = ArgumentParser(add_help=False,
                            description='gerar arquivos de usuários para o '
                            'BOCA',
                            formatter_class=RawDescriptionHelpFormatter,
                            epilog='Exemplo de uso:\n'
                                   '\tpython %(prog)s users.csv')

    parser.add_argument('csv', type=str,
                        help='arquivo CSV com os instituições/times')
    parser.add_argument('-d', dest='description', required=True,
                        help='descrição do Contest')
    parser.add_argument('-h', '--help', action='help',
                        help='mostrar esta mensagem e sair')
    parser.add_argument('-j', dest='judges', type=check_users, default=2,
                        help='quantidade de juízes')
    parser.add_argument('-p', dest='scores', type=check_users, default=5,
                        help='quantidade de placares')
    parser.add_argument('-q', '--quiet', dest='quiet',
                        action='store_true',
                        help='omitir os resultados do processo')
    parser.add_argument('-s', dest='staff', type=check_users, default=5,
                        help='quantidade de staff')

    args = parser.parse_args()

    teams = get_teams(args.csv)
    create_staff(args.judges, args.staff, args.scores)
    create_users(teams, args.description)
