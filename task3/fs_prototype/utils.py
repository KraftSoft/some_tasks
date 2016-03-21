from collections import OrderedDict

import pymysql
from getpass import fallback_getpass
import hashlib
import sys
import os
import warnings
from datetime import datetime
import configparser


class FileSystemStore(object):
    def __init__(self):
        conf = configparser.ConfigParser()
        conf.read('conf/default.conf')
        database = conf['DATABASE']
        self.conn = pymysql.connect(host=database['host'], user=database['user'], passwd=database['password'],
                                    db=database['database'], charset='utf8')

    def get_cursor(self):
        return self.conn.cursor()

    def commit(self):
        self.conn.commit()


class FileSystemManager(object):
    def __init__(self, store, stream):
        self.stream = stream
        self.root_directory = '/'
        self.__store = store
        self.cursor = store.get_cursor()

        self.permissions = {
            'execute': 1,
            'write': 2,
            'write-execute': 3,
            'read': 4,
            'read-execute': 5,
            'read-write': 6,
            'all': 7
        }

        self.default_permissions = '755'

        self.ACTION_EXECUTE = 'execute'
        self.ACTION_READ = 'read'
        self.ACTION_WRITE = 'write'

        self.directory__actions = {
            self.ACTION_EXECUTE: (1, 3, 5, 7),
            self.ACTION_READ: (4, 5, 6, 7),
            self.ACTION_WRITE: (3, 6, 7)
        }

        self.file__actions = {
            self.ACTION_EXECUTE: (1, 3, 5, 7),
            self.ACTION_READ: (4, 5, 6, 7),
            self.ACTION_WRITE: (2, 3, 6, 7)
        }

        self.node_types = {
            'file': 0,
            'directory': 1
        }

        self.node_types_map = {
            0: 'f',
            1: 'd'
        }

        self.colors = {
            'blue': '\033[94m',
            'default': '\033[0m'
        }

        self.TYPE_OWNER = 'owner'
        self.TYPE_GROUP = 'group'
        self.TYPE_OTHERS = 'others'

        self.user_types_columns = {
            self.TYPE_OWNER: 'owner_permission',
            self.TYPE_GROUP: 'group_permission',
            self.TYPE_OTHERS: 'others_permission'
        }

        self.__entry_to_fs()

    def command_executor(self, command, args):
        command_dict = {
            'cd': self.change_dir,
            'mkdir': self.make_dir,
            'mkfile': self.make_file,
            'ls': self.list_directory
        }

        if command in command_dict:
            try:
                if args:
                    return command_dict[command](*args)
                else:
                    return command_dict[command]()
            except Exception as e:
                self.write_out(e)
        else:
            self.write_out("Command '{0}' not found".format(command))

    def write_out(self, string, color=None):
        if color:
            return self.stream.write(color + '{0}{1}'.format(string, '\n') + self.colors['default'])
        else:
            return self.stream.write('{0}{1}'.format(string, '\n'))

    def __fetch_multi(self, request, params):
        results_count = self.cursor.execute(request, params)
        results_values = self.cursor.fetchall()
        return results_count, results_values

    def __fetch_single(self, request, params):
        self.cursor.execute(request, params)
        results_value = self.cursor.fetchone()
        return results_value

    def __execute_single(self, request, params):
        self.cursor.execute(request, params)
        self.__store.commit()
        return self.cursor.lastrowid

    def __login(self, username, password):
        value = self.__fetch_single(
            "SELECT id, login, group_id, is_superuser FROM user WHERE login=%s AND password=%s ",
            (username, password))
        if value:
            return True, FileSystemUser(*value)
        else:
            return False, None

    def __entry_to_fs(self):
        is_exists = False

        while not is_exists:

            login = None
            password = None

            try:
                login = input('Login: ')
                with warnings.catch_warnings():
                    warnings.filterwarnings("ignore")
                    password = fallback_getpass('Password: ', sys.stdout)
            except EOFError:
                print('Bye!')
                exit(0)

            hash_pass = hashlib.md5(password.encode('utf-8')).hexdigest()
            is_exists, user = self.__login(login, hash_pass)

            if not is_exists:
                self.write_out('Not valid pair login,password, please try again')

        current_dir = self.__set_default_directory(user)
        self.__session = Session(user, current_dir)

    def get_session(self):
        return self.__session

    def __check_access(self, node_id, action, user_type):

        if user_type not in self.user_types_columns:
            return False

        db_column = self.user_types_columns[user_type]
        row = self.__fetch_single("SELECT {0}, N.type "
                                  "FROM permissions P INNER JOIN node N ON N.id=P.node_id "
                                  "WHERE node_id=%s ".format(db_column), (node_id,), )
        if row:
            permission = int(row[0])
            node_type = row[1]
            return self.__check_action(action, permission, node_type)

    def __check_action(self, action, permission, node_type):
        if node_type == self.node_types['file']:
            return permission in self.file__actions[action]
        if node_type == self.node_types['directory']:
            return permission in self.directory__actions[action]

    def __has_access(self, user, node_id, action):
        if user.is_superuser:
            return True

        if user.id == self.__get_owner_id(node_id):
            return self.__check_access(node_id, action, self.TYPE_OWNER)
        if user.group_id == self.__get_owner_group_id(node_id) and user.group_id is not None:
            return self.__check_access(node_id, action, self.TYPE_GROUP)
        else:
            return self.__check_access(node_id, action, self.TYPE_OTHERS)

    def __get_owner_id(self, node_id):
        row = self.__fetch_single("SELECT M.owner_id "
                                  "FROM node N INNER JOIN meta M ON N.meta_id=M.id "
                                  "WHERE N.id=%s", (node_id,))
        if row:
            return int(row[0])

    def __get_owner_group_id(self, node_id):
        row = self.__fetch_single("SELECT U.group_id "
                                  "FROM node N INNER JOIN meta M ON N.meta_id=M.id "
                                  "INNER JOIN user U ON U.id=M.owner_id "
                                  "WHERE N.id=%s", (node_id,))
        if row:
            if row[0]:
                return int(row[0])

    def __set_default_directory(self, user):
        dir_name = self.root_directory
        node_id = self.__get_node_by_path(dir_name, self.node_types['directory'])
        if node_id:
            if self.__has_access(user, node_id, self.ACTION_EXECUTE):
                return Directory(*self.__get_directory_meta(node_id))
            else:
                self.write_out('Access denied')
        else:
            self.write_out('Directory not found')

    def __get_node_by_name(self, dir_name, parent_id, node_type):
        row = self.__fetch_single("SELECT N.id "
                                  "FROM meta M INNER JOIN node N ON N.meta_id=M.id "
                                  "WHERE N.name=%s AND N.parent_id=%s AND N.type=%s ",
                                  (dir_name, parent_id, node_type))

        if row:
            return int(row[0])

    def __get_node_by_path(self, path, node_type):
        row = self.__fetch_single("SELECT N.id "
                                  "FROM meta M INNER JOIN node N ON N.meta_id=M.id "
                                  "WHERE M.path=%s and N.type=%s", (path, node_type))

        if row:
            return int(row[0])

    def __get_directory_meta(self, dir_id):
        row = self.__fetch_single("SELECT N.id, N.name, M.path "
                                  "FROM meta M INNER JOIN node N ON N.meta_id=M.id "
                                  "WHERE N.id=%s AND N.type=%s ", (dir_id, self.node_types['directory']))

        if row:
            return row

    def __create(self, node_type, name, parent_id, permissions):

        perms = permissions if permissions and self.__check__permissions_symbols(
            permissions) else self.default_permissions

        if node_type == self.node_types['file']:
            return self.__create_file(name, parent_id, perms)
        elif node_type == self.node_types['directory']:
            return self.__create_directory(name, parent_id, perms)

    def __create_directory(self, dir_name, parent_id, permissions):
        user = self.__session.user
        if self.__session.current_directory.path != self.root_directory:
            dir_path = '{0}/{1}'.format(self.__session.current_directory.path, dir_name)
        else:
            dir_path = '{0}{1}'.format(self.__session.current_directory.path, dir_name)

        meta_id = self.__execute_single("INSERT INTO meta (date_create, last_modify, owner_id, last_changer_id, path) "
                                        "VALUES (%s, %s, %s, %s, %s)",
                                        (datetime.now(), datetime.now(), user.id, user.id, dir_path))

        node_type = self.node_types['directory']
        node_id = self.__execute_single("INSERT INTO node (name, type, meta_id, parent_id) "
                                        "VALUES (%s, %s, %s, %s)", (dir_name, node_type, meta_id, parent_id))

        permission_name = '{0} directory permissions'.format(dir_path)

        owner_p = permissions[0]
        group_p = permissions[1]
        others_p = permissions[2]

        permission_id = self.__execute_single(
            "INSERT INTO permissions (name, owner_permission, group_permission, others_permission, node_id) "
            "VALUES (%s, %s, %s, %s, %s)", (permission_name, owner_p, group_p, others_p, node_id))
        if permission_id:
            return True

    def __create_file(self, file_name, parent_id, permissions):
        user = self.__session.user
        if self.__session.current_directory.path != self.root_directory:
            file_path = '{0}/{1}'.format(self.__session.current_directory.path, file_name)
        else:
            file_path = '{0}{1}'.format(self.__session.current_directory.path, file_name)

        meta_id = self.__execute_single("INSERT INTO meta (date_create, last_modify, owner_id, last_changer_id, path) "
                                        "VALUES (%s, %s, %s, %s, %s)",
                                        (datetime.now(), datetime.now(), user.id, user.id, file_path))

        node_type = self.node_types['file']
        node_id = self.__execute_single("INSERT INTO node (name, type, meta_id, parent_id) "
                                        "VALUES (%s, %s, %s, %s)", (file_name, node_type, meta_id, parent_id))

        permission_name = '{0} file permissions'.format(file_path)

        owner_p = permissions[0]
        group_p = permissions[1]
        others_p = permissions[2]

        permission_id = self.__execute_single(
            "INSERT INTO permissions (name, owner_permission, group_permission, others_permission, node_id) "
            "VALUES (%s, %s, %s, %s, %s)", (permission_name, owner_p, group_p, others_p, node_id))
        if permission_id:
            return True

    def __check__permissions_symbols(self, perm):
        if isinstance(perm, str) and len(perm) == 3:
            perm_available_symbols = set(('1', '2', '3', '4', '5', '6', '7'))
            perm_set = set(list(perm))
            return perm_set.issubset(perm_available_symbols)

    def __get_directory_list(self, directory_id):
        results = []
        _, rows = self.__fetch_multi("SELECT name, type FROM node WHERE parent_id=%s", (directory_id,))
        for row in rows:
            results.append({'name': row[0], 'type': row[1]})
        return results

    def __get_extended_directory_list(self, directory_id):
        header = OrderedDict((
            ('name', 'file name'),
            ('type', 'type'),
            ('permissions', 'perm'),
            ('owner', 'owner'),
            ('changer', 'changer'),
            ('date_create', 'creation date'),
            ('last_modify', 'last modify')
        ))

        results = [header]
        count, rows = self.__fetch_multi("SELECT N.name, N.type, P.owner_permission, P.group_permission, "
                                         "P.others_permission, Owner.login, Changer.login, "
                                         "M.date_create, M.last_modify FROM node N "
                                         "INNER JOIN meta M ON N.meta_id=M.id "
                                         "INNER JOIN permissions P ON P.node_id=N.id "
                                         "INNER JOIN user Owner ON M.owner_id=Owner.id AND N.meta_id=M.id "
                                         "INNER JOIN user Changer ON M.last_changer_id=Changer.id AND N.meta_id=M.id "
                                         "WHERE N.parent_id=%s", (directory_id,))
        for row in rows:
            results.append(OrderedDict((
                ('name', row[0]),
                ('type', row[1]),
                ('permissions', '{0}{1}{2}'.format(row[2], row[3], row[4])),
                ('owner', row[5]),
                ('changer', row[6]),
                ('date_create', row[7]),
                ('last_modify', row[8])
            )))
        return count, results

    def change_dir(self, dir_name=None):
        if not dir_name:
            self.write_out('Directory name is required')
            return

        if len(dir_name) > 0:

            if dir_name[0] == self.root_directory:
                node_id = self.__get_node_by_path(dir_name, self.node_types['directory'])
            else:
                current_node = self.__session.current_directory.node_id
                node_id = self.__get_node_by_name(dir_name, current_node, self.node_types['directory'])

            if not node_id:
                self.write_out('Directory not found')
                return self.get_session()
            else:
                if self.__has_access(self.__session.user, node_id, self.ACTION_EXECUTE):
                    new_dir = Directory(*self.__get_directory_meta(node_id))
                    self.__session.change_dir(new_dir)
                    return self.get_session()
                else:
                    self.write_out('Access denied')
        else:
            self.write_out('Directory name is required')

    def make_dir(self, dir_name=None, perm=None):
        if not dir_name:
            self.write_out('Directory name is required')
            return
        if len(dir_name) > 0:

            current_node = self.__session.current_directory.node_id

            if self.__has_access(self.__session.user, current_node, self.ACTION_WRITE):
                is_created = self.__create(self.node_types['directory'], dir_name, current_node, perm)
                if not is_created:
                    self.write_out('Can not create a directory')
            else:
                self.write_out('Access denied')
        else:
            self.write_out('Directory name is required')

    def make_file(self, file_name=None, perm=None):
        if not file_name:
            self.write_out('File name is required')
            return
        if len(file_name) > 0:

            current_node = self.__session.current_directory.node_id

            if self.__has_access(self.__session.user, current_node, self.ACTION_WRITE):
                is_created = self.__create(self.node_types['file'], file_name, current_node, perm)
                if not is_created:
                    self.write_out('Can not create a file')
            else:
                self.write_out('Access denied')
        else:
            self.write_out('File name is required')

    def __format_dir_list(self, directory):

        name = directory['name']
        node_type = directory['type']
        permissions = directory['permissions']
        owner = directory['owner']
        changer = directory['changer']
        date_create = directory['date_create']
        last_modify = directory['last_modify']

        return '%-6s %-5s %-10s %-10s %-25s %-25s %s' % (
            permissions, node_type, owner, changer, date_create, last_modify, name)

    def list_directory(self, params=None):
        current_node_id = self.__session.current_directory.node_id
        if self.__has_access(self.__session.user, current_node_id, self.ACTION_READ):
            if not params:
                directories = self.__get_directory_list(current_node_id)
                for dir in directories:
                    if dir['type'] == self.node_types['file']:
                        self.write_out(dir['name'])
                    elif dir['type'] == self.node_types['directory']:
                        self.write_out(dir['name'], self.colors['blue'])

            elif params == '-l':
                count, directories = self.__get_extended_directory_list(current_node_id)
                self.write_out('total: {0}'.format(count))
                header = directories.pop(0)
                self.write_out(self.__format_dir_list(header))
                for dir in directories:
                    line = self.__format_dir_list(dir)
                    if dir['type'] == self.node_types['file']:
                        self.write_out(line)
                    elif dir['type'] == self.node_types['directory']:
                        self.write_out(line, self.colors['blue'])
            else:
                self.write_out("ls command can use with flag '-l' ")
        else:
            self.write_out('Access denied')


class FileSystemUser(object):
    def __init__(self, user_id, login, group_id, is_superuser):
        self.id = int(user_id)
        self.login = login
        self.is_superuser = is_superuser

        if group_id:
            self.group_id = int(group_id)
        else:
            self.group_id = None


class Directory(object):
    def __init__(self, node_id, name, path):
        self.node_id = node_id
        self.name = name
        self.path = path


class Session(object):
    def __init__(self, user, directory):
        self.user = user
        self.current_directory = directory
        self.computer = os.uname().nodename

    def change_dir(self, new_dir):
        self.current_directory = new_dir
