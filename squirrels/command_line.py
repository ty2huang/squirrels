import sys, time
global_start = time.time()
sys.path.append('.')

from squirrels import constants as c, profile_manager as pm
from squirrels.renderer import Renderer
from argparse import ArgumentParser


def get_profiles():
    for key, value in pm.get_profiles().items():
        print(key + ": " + str(value))


def set_profile(args):
    profile = pm.Profile(args.name)
    if args.values:
        dialect, url, user, pw = args.values
    else:
        dialect = input("Enter sql dialect: ")
        url = input("Enter connection URL [host:port/database]: ")
        user = input("Enter username: ")
        pw = input("Enter password: ")
    
    profile.set(dialect, url, user, pw)
    
    print(f"\nProfile '{args.name}' has been set with following values:")
    print(profile.get())


def delete_profile(args):
    profile_existed = pm.Profile(args.name).delete()
    if profile_existed:
        print(f"Profile '{args.name}' was deleted")
    else:
        print(f"Profile '{args.name}' does not exist")


def run_project():
    raise NotImplementedError()


def load_modules():
    raise NotImplementedError()


def init_project():
    raise NotImplementedError()


def main():
    GET_PROFILES_CMD = 'get-all-profiles'
    SET_PROFILE_CMD = 'set-profile'
    DELETE_PROFILE_CMD = 'delete-profile'
    TEST_CMD = 'test'
    RUN_CMD = 'run'
    LOAD_MODULES_CMD = 'load-modules'
    INIT_CMD = 'init'

    start = time.time()
    parser = ArgumentParser(description="Command line utilities from the squirrels python package")
    parser.add_argument('-v', '--verbose', action='store_true', help='Show all log messages')
    subparsers = parser.add_subparsers(title='commands', dest='command', required=True)

    def _add_profile_argument(parser):
        parser.add_argument('name', type=str, help='Name of the database connection profile (as written in manifest.json)')

    subparsers.add_parser(INIT_CMD, help='Initialize a squirrels project')

    subparsers.add_parser(LOAD_MODULES_CMD, help='Load all the modules specified in manifest.json from git')

    subparsers.add_parser(GET_PROFILES_CMD, help='Get all database connection profile names and values')

    set_profile_parser = subparsers.add_parser(SET_PROFILE_CMD, help='Set a database connection profile')
    _add_profile_argument(set_profile_parser)
    set_profile_parser.add_argument('--values', type=str, nargs=4, help='The sql dialect, connection url, username, and password')

    delete_profile_parser = subparsers.add_parser(DELETE_PROFILE_CMD, help='Delete a database connection profile')
    _add_profile_argument(delete_profile_parser)

    test_parser = subparsers.add_parser(TEST_CMD, help='For a given dataset, create or compare expected results of parameters response and rendered sql queries')
    test_parser.add_argument('dataset', type=str, help='Name of dataset (as written in manifest.json) to test, and results are written in an "outputs" folder, or if this is not specified, unit testing on the "tests" folder is done instead')
    test_parser.add_argument('-c', '--cfg', type=str, help='Configuration file for parameter selections. Path is relative to a specific dataset folder')
    test_parser.add_argument('-d', '--data', type=str, help='Sample lookup data to avoid making a database connection. Path is relative to a specific dataset folder')
    test_parser.add_argument('-r', '--runquery', action='store_true', help='Runs all database queries and final view, and produce the results as csv files')

    subparsers.add_parser(RUN_CMD, help='Enable all APIs')
    c.timer.add_activity_time('creating argparser', start)

    start = time.time()
    args = parser.parse_args()
    if args.command == GET_PROFILES_CMD:
        get_profiles()
    elif args.command == SET_PROFILE_CMD:
        set_profile(args)
    elif args.command == DELETE_PROFILE_CMD:
        delete_profile(args)
    elif args.command == TEST_CMD:
        Renderer(args.dataset, args.cfg, args.data).write_outputs(args.runquery)
        c.timer.add_activity_time('rendering output', start)
    elif args.command == RUN_CMD:
        run_project()
    elif args.command == LOAD_MODULES_CMD:
        load_modules()
    elif args.command == INIT_CMD:
        init_project()
    else:
        raise RuntimeError(f'The squirrels CLI does not support "{args.command}"')
    
    c.timer.add_activity_time('everything', global_start)
    c.timer.report_times(args.verbose)


if __name__ == '__main__':
    main()
