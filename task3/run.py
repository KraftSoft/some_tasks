from task3.fs_prototype.utils import FileSystemStore, FileSystemManager
import sys


def data_parse(line):
    arguments = None
    if len(line) > 0:
        command = line[0]
    if len(line) > 1:
        arguments = line[1:]
    return command, arguments


if __name__ == '__main__':
    try:
        input = raw_input
    except NameError:
        pass

    store = FileSystemStore()
    fs_manager = FileSystemManager(store.get_cursor(), sys.stdout)
    session = fs_manager.get_session()

    while True:
        try:
            user_input = input('{0}@{1}:{2}$ '.format(session.user.login,
                                                      session.computer,
                                                      session.current_directory.path))
            separate_data = user_input.split(' ')
            command, args = data_parse(separate_data)

            fs_manager.command_executor(command, args)

        except EOFError:
            print('Bye!')
            exit(0)
