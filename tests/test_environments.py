import unittest
from enc.enc import Environments

custom_env_no_node_key = {"groups": "^saiyan"}

custom_env_no_group_key = {"nodes": "dbz-goku.earth.univ"}

custom_env_no_groups_key = {"group": "dbz-goku.earth.univ"}

custom_env_groups_no_dict = {"groups": []}

custom_env = {"groups": {"^saiyan": "", "^dbz": ""},
              "nodes": {"dbz-gohan.earth.univ": ""}}


class EnvironmentsTestCase(unittest.TestCase):

    def setUp(self):
        self.enc = Environments('tests/db.yml')
        self.enc.db = {}
        self.enc._check_create_empty()

    def test_add_nodes(self):
        env_name = "earth"
        t1 = self.enc.add_nodes(
            env_name, "dbz-goku.earth.univ")

        self.assertFalse(t1)

        self.enc.add_environment(env_name)

        t2 = self.enc.add_nodes(
            env_name, "dbz-goku.earth.univ")

        self.assertTrue(t2)

        t3 = self.enc.add_nodes(
            env_name, "dbz-goku.earth.univ")

        self.assertFalse(t3)

    def test_add_nodes_no_put_envname(self):
        env_name = "earth"
        t1 = self.enc.add_nodes()

        self.assertFalse(t1)

        self.enc.add_environment(env_name)

        t2 = self.enc.add_nodes()

        self.assertFalse(t2)

    def test_add_multiple_nodes(self):
        env_name = "earth"

        self.enc.add_environment(env_name)

        t1 = self.enc.add_nodes(
            env_name, "dbz-goku.earth.univ")

        self.assertTrue(t1)

        t2 = self.enc.add_nodes(
            env_name, "dbz-gohan.earth.univ")

        self.assertTrue(t2)

        env_name = "vegeta"

        self.enc.add_environment(env_name)

        t3 = self.enc.add_nodes(
            env_name, "dbz-vegeta.vegeta.univ")

        self.assertTrue(t3)

        self.assertEqual(
            len(self.enc.db["environments"]["earth"][Environments.NODES_KEY]), 2)

        self.assertEqual(
            len(self.enc.db["environments"]["vegeta"][Environments.NODES_KEY]), 1)

    def test_add_remove_nodes(self):
        env_name = "earth"

        self.enc.add_environment(env_name)

        t1 = self.enc.add_nodes(
            env_name, "dbz-goku.earth.univ")

        self.assertTrue(t1)

        t2 = self.enc.delete_nodes(
            env_name, "dbz-goku.earth.univ")

        self.assertTrue(t2)

        self.assertEqual(
            len(self.enc.db["environments"][env_name][Environments.NODES_KEY]), 0)

        t3 = self.enc.delete_nodes(env_name)

        self.assertTrue(t3)

        self.assertEqual(
            len(self.enc.db["environments"][env_name][Environments.NODES_KEY]), 0)

        t4 = self.enc.delete_nodes("namek")

        self.assertFalse(t4)

    def test_get_nodes(self):
        env_name = "earth"

        self.enc.add_environment(env_name)

        t1 = self.enc.add_nodes(
            env_name, "dbz-goku.earth.univ")

        self.assertTrue(t1)

        t2 = self.enc.add_nodes(
            env_name, "dbz-gohan.earth.univ")

        self.assertTrue(t2)

        t3 = self.enc.get_nodes("earth")

        self.assertEqual(len(t3.keys()), 2)

        self.assertFalse(self.enc.get_nodes("vegeta"))

    def test_add_groups(self):
        env_name = "earth"
        t1 = self.enc.add_groups(
            env_name, "^saiyan")

        self.assertFalse(t1)

        self.enc.add_environment(env_name)

        t2 = self.enc.add_nodes(
            env_name, "^saiyan")

        self.assertTrue(t2)

        t3 = self.enc.add_nodes(
            env_name, "^saiyan")

        self.assertFalse(t3)

    def test_add_remove_groups(self):
        env_name = "earth"

        self.enc.add_environment(env_name)

        t1 = self.enc.add_groups(
            env_name, "^saiyan")

        self.assertTrue(t1)

        t2 = self.enc.delete_groups(
            env_name, "^saiyan")

        self.assertTrue(t2)

        t3 = self.enc.delete_groups(None, "^saiyan")

        self.assertFalse(t3)

        self.assertEqual(
            len(self.enc.db["environments"][env_name][Environments.GROUPS_KEY]), 0)

    def test_add_delete_environment(self):
        env_name = "earth"

        t1 = self.enc.add_environment(env_name)

        self.assertTrue(t1)

        t2 = self.enc.delete_environment(env_name)

        self.assertTrue(t2)

        t3 = self.enc.delete_environment(env_name)

        self.assertFalse(t3)

    def test_get_environment(self):
        env_name = "earth"

        t1 = self.enc.add_environment(env_name)

        self.assertTrue(t1)

        t2 = self.enc.get_environment(env_name)

        self.assertTrue(t2)

        t3 = self.enc.delete_environment(env_name)

        self.assertTrue(t3)

        t4 = self.enc.delete_environment(env_name)

        self.assertFalse(t4)

    def test_add_provided_environment(self):
        env_name = "earth"

        t1 = self.enc.add_environment(env_name, custom_env_no_node_key)

        self.assertFalse(t1)

        t2 = self.enc.add_environment(env_name, custom_env_no_group_key)

        self.assertFalse(t2)

        t3 = self.enc.add_environment(env_name, custom_env)

        self.assertTrue(t3)

        t4 = self.enc.add_environment(env_name, custom_env_no_groups_key)

        self.assertFalse(t4)

        t5 = self.enc.add_environment(env_name, custom_env_groups_no_dict)

        self.assertFalse(t5)

    def test_find_node(self):
        t1 = self.enc.find_node()

        self.assertFalse(t1)

        t2 = self.enc.find_node("dbz-goku.earth.univ")

        self.assertFalse(t2)

        env_name = "earth"

        self.enc.add_environment(env_name, custom_env)

        t3 = self.enc.find_node("dbz-goku.earth.univ")

        self.assertEqual(t3, env_name)

        t4 = self.enc.find_node("dbz-gohan.earth.univ")

        self.assertEqual(t3, env_name)
