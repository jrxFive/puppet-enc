import os
import yaml
import re
import optparse
import sys


class DB(object):

    def __init__(self, db_filepath):
        self.db = self._load_yaml_db(db_filepath)
        self.db_filepath = db_filepath

    def _load_yaml_db(self, filepath):
        try:
            with open(filepath, 'r') as fh:
                r = yaml.load(fh.read())
                if r:
                    return r
                else:
                    return {}
        except IOError as err:
            return {}
        except ValueError as err:
            raise
        except TypeError as err:
            return {}

    def _write_yaml_db(self):
        with open(self.db_filepath, 'w+') as fh:
            yaml.dump(self.db, fh, default_flow_style=False)


class Environments(DB):

    ROOT_KEY = "environments"
    NODES_KEY = "nodes"
    GROUPS_KEY = "groups"

    def __init__(self, db_filepath):
        super(Environments, self).__init__(db_filepath)
        self._check_create_empty()

    def _check_create_empty(self):
        """Check if ROOT_KEY has been created in the db file. If False add ROOT_KEY to db
        file with a value of an empty dict"""
        if not self._check():
            self.db[Environments.ROOT_KEY] = {}
            self._write_yaml_db()

    def _check(self, env_name=None):
        """Check for specified environment name within the ROOT_KEY object.
        If no environment name is specified check if the ROOT_KEY is in the db
        file

        Returns True or False
        """
        if env_name:
            if env_name in self.db[Environments.ROOT_KEY]:
                return True
            else:
                return False
        else:
            if Environments.ROOT_KEY in self.db:
                return True
            else:
                return False

    def _get_nested(self, env_name=None, nested_key=None):
        """Get nested information within each environment either (nodes,groups). Environments
        name must exist or set to None. If env_name is None and nested_key given"""
        if not self._check(env_name):  # if environment does not exist in db file
            return False
        if env_name:
            return self.db[Environments.ROOT_KEY][env_name][nested_key]
        if not env_name:
            tmp = {}

            if nested_key == Environments.NODES_KEY:
                f = self.get_nodes
            if nested_key == Environments.GROUPS_KEY:
                f = self.get_groups

            for e in self.get_environment():
                tmp[e] = f(e)

            return tmp

    def _add_nested(self, env_name=None, nested_key=None, put_key=None):
        """Add Key to Environment either node or group. Returns False if env_name does
        not exist or if key already exists in nested_key """
        if not self._check(env_name):
            return False

        if not env_name and not put_key:
            return False
        elif env_name and put_key:
            if put_key not in self.db[Environments.ROOT_KEY][env_name][nested_key]:
                self.db[Environments.ROOT_KEY][
                    env_name][nested_key][put_key] = ""
                self._write_yaml_db()
                return True
            else:
                return False
        else:
            return False

    def _delete_nested(self, env_name=None, nested_key=None, delete_key=None):
        """Delete nested key if the env_name exists. If no delete_key is given
        will remove entire nested_key and recreated nested_key with empty dict. If
        delete_key is given will delete only that key within the nested_key. Returns
        False if operations cannot be done or failed to lookup key"""
        try:
            if not self._check(env_name):
                return False
            if not env_name and delete_key:
                return False
            if env_name and not delete_key:
                del self.db[Environments.ROOT_KEY][env_name][nested_key]
                self.db[Environments.ROOT_KEY][env_name][nested_key] = {}
                self._write_yaml_db()
                return True
            if env_name and delete_key:
                del self.db[Environments.ROOT_KEY][
                    env_name][nested_key][delete_key]
                self._write_yaml_db()
                return True
        except KeyError:
            return False

    def add_environment(self, env_name=None, env_name_values=None):
        """Add environment, returns False if env_name already exists. If supplying preset
        nested values it must contain NODES_KEY and GROUPS_KEY and they must be dicts,
        otherwise will return False"""

        if env_name and env_name_values and env_name not in self.db[Environments.ROOT_KEY]:

            if Environments.NODES_KEY not in env_name_values:
                return False
            if not isinstance(env_name_values[Environments.NODES_KEY], dict):
                return False
            if Environments.GROUPS_KEY not in env_name_values:
                return False
            if not isinstance(env_name_values[Environments.GROUPS_KEY], dict):
                return False

            self.db[Environments.ROOT_KEY][env_name] = env_name_values
            self._write_yaml_db()
            return True

        elif env_name and env_name not in self.db[Environments.ROOT_KEY]:
            self.db[Environments.ROOT_KEY][
                env_name] = {"nodes": {}, "groups": {}}
            self._write_yaml_db()
            return True
        else:
            return False

    def get_environment(self, env_name=None):
        """Get environment if it exists. If no env_name specified return list of environments
        declared in the db file"""
        if not self._check(env_name):
            return False

        if env_name:
            return self.db[Environments.ROOT_KEY][env_name]
        else:
            return self.db[Environments.ROOT_KEY]

    def delete_environment(self, env_name=None):
        """Delete environment if it exists"""
        if not env_name:
            return False

        if not self._check(env_name):
            return False

        del self.db[Environments.ROOT_KEY][env_name]
        self._write_yaml_db()
        return True

    def get_nodes(self, env_name=None):
        return self._get_nested(env_name, Environments.NODES_KEY)

    def add_nodes(self, env_name=None, node_name=None):
        return self._add_nested(env_name, Environments.NODES_KEY, node_name)

    def delete_nodes(self, env_name=None, node_name=None):
        return self._delete_nested(env_name, Environments.NODES_KEY, node_name)

    def get_groups(self, env_name=None):
        return self._get_nested(env_name, Environments.GROUPS_KEY)

    def add_groups(self, env_name=None, groups_name=None):
        return self._add_nested(env_name, Environments.GROUPS_KEY, groups_name)

    def delete_groups(self, env_name=None, groups_name=None):
        return self._delete_nested(env_name, Environments.GROUPS_KEY, groups_name)

    def find_node(self, node_name=None):
        if not node_name:
            return False
        else:
            for env, nodes in self.get_nodes().items():
                if node_name in nodes:
                    return env

            for env, groups in self.get_groups().items():
                for group in groups:
                    if re.search(group, node_name):
                        return env

            return False


def print_find(enc, arg):
    result = enc.find_node(arg)
    if result:
        print(yaml.dump({"environment": result},
                        default_flow_style=False, line_break=None).replace('\n', ''))
    else:
        print(yaml.dump({"environment": "undef"},
                        default_flow_style=False, line_break=None).replace('\n', ''))

if __name__ == "__main__":
    parser = optparse.OptionParser()

    parser.add_option('-l',
                      '--ls',
                      action='store_true',
                      dest='list',
                      default=False)

    parser.add_option('-r',
                      '--rm',
                      action='store_true',
                      dest='remove',
                      default=False)

    parser.add_option('-a',
                      '--add',
                      action='store_true',
                      dest='add',
                      default=False)

    parser.add_option('-e',
                      '--env',
                      action='store',
                      dest='environment',
                      type='string',
                      default=None)

    parser.add_option('-c',
                      '--custom',
                      action='store',
                      dest='custom',
                      type='string',
                      default=None)

    parser.add_option('-n',
                      '--node',
                      action='store',
                      dest='node',
                      type='string',
                      default=None)

    parser.add_option('-g',
                      '--group',
                      action='store',
                      dest='group',
                      type='string',
                      default=None)

    parser.add_option('-f',
                      '--find',
                      action='store',
                      dest='find',
                      type='string',
                      default=None)

    options, args = parser.parse_args()

    e = Environments('db.yml')

    if options.find:
        print_find(e, options.find)

    elif options.list:
        if options.environment:
            result = e.get_environment(options.environment)
            print(yaml.dump(result, default_flow_style=False))
        else:
            result = e.get_environment()
            print(yaml.dump(result, default_flow_style=False))
    elif options.add:
        if options.environment and options.custom:
            result = e.add_environment(
                options.environment, yaml.load(options.custom))
            if not result:
                sys.stderr.write(
                    "Unable to add environment: {e} with custom yaml/json\n".format(e=options.environment))

        elif options.environment and options.node:
            result = e.add_nodes(options.environment, options.node)
            if not result:
                sys.stderr.write("Unable to add node: {n} to environment: {e}\n".format(n=options.node,
                                                                                        e=options.environment))
        elif options.environment and options.group:
            result = e.add_groups(options.environment, options.group)
            if not result:
                sys.stderr.write("Unable to add group: {g} to environment: {e}\n".format(g=options.group,
                                                                                         e=options.environment))
        elif options.environment:
            result = e.add_environment(options.environment)
            if not result:
                sys.stderr.write(
                    "Unable to add environment: {e}\n".format(e=options.environment))
    elif options.remove:
        if options.environment and options.node:
            result = e.delete_nodes(options.environment, options.node)
            if not result:
                sys.stderr.write("Unable to delete node: {n} to environment: {e}\n".format(n=options.node,
                                                                                           e=options.environment))
        elif options.environment and options.group:
            result = e.delete_groups(options.environment, options.group)
            if not result:
                sys.stderr.write("Unable to delete group: {g} to environment: {e}\n".format(g=options.group,
                                                                                            e=options.environment))
        elif options.environment:
            result = e.delete_environment(options.environment)
            if not result:
                sys.stderr.write(
                    "Unable to delete environment: {e}\n".format(e=options.environment))
    else:
        if len(sys.argv) == 2:
            print_find(e, sys.argv[1])
