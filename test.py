import contextlib
import unittest
import sys
import os

from cec import parse


CONFIG_FILEPATH = 'config.json'
SCRIPT_PATH = sys.argv[0]
sys.argv = [SCRIPT_PATH]

def clean():
    sys.argv = [SCRIPT_PATH]
    os.environ = {}
    with contextlib.suppress(FileNotFoundError):
        os.remove(CONFIG_FILEPATH)


class TestCEC(unittest.TestCase):
    
    def setUp(self) -> None:
        clean()
        return super().setUp()

    def test_simple_config(self):
        # config
        with open(CONFIG_FILEPATH, 'w') as f:
            f.write('''{
            "a": "1"
        }''')
        self.assertDictEqual(parse(), {'a': '1'})

    def test_simple_env(self):
        # env
        os.environ['NEMO_A'] = '2'
        os.environ['nemo_enV'] = 'yes'
        os.environ['nemo_demo_config'] = '{"key": "value"}'
        self.assertDictEqual(parse(), {'a': 2, 'env': 'yes', 'demo_config': {'key': 'value'}})

    def test_multipath_env(self):
        # env
        os.environ['nemo_demo__config'] = '{"key": "value"}'
        self.assertDictEqual(parse(), {'demo': {'config': {'key': 'value'}}})
    
    def test_simple_cli(self):
        sys.argv = [SCRIPT_PATH, '--a=3', '--cli=yes']
        self.assertDictEqual(parse(), {'a': 3, 'cli': 'yes'})

    def test_multi_cli(self):
        sys.argv = [SCRIPT_PATH, '--a=3', '--cli=yes']
        sys.argv.append('--a=4')
        self.assertDictEqual(parse(), {'a': [3, 4], 'cli': 'yes'})

    def test_overwrite(self):
        # config
        with open(CONFIG_FILEPATH, 'w') as f:
            f.write('''{
            "a": "1"
        }''')
        self.assertDictEqual(parse(), {'a': '1'})

        # env
        os.environ['NEMO_A'] = '2'
        os.environ['nemo_enV'] = 'yes'
        os.environ['nemo_demo_config'] = '{"key": "value"}'
        os.environ['nemo_demo__config'] = '{"key": "value"}'
        self.assertDictEqual(parse(), {'a': 2, 'env': 'yes', 'demo_config': {'key': 'value'}, 'demo': {'config': {'key': 'value'}}})

        # cli
        sys.argv = [SCRIPT_PATH, '--a=3', '--cli=yes']
        self.assertDictEqual(parse(), {'a': 3, 'cli': 'yes', 'env': 'yes', 'demo_config': {'key': 'value'}, 'demo': {'config': {'key': 'value'}}})

    def test_keep_int(self):
        # env
        os.environ['NEMO_A'] = '2'
        os.environ['nemo_enV'] = 'yes'
        os.environ['nemo_demo_config'] = '{"key": "value"}'
        os.environ['nemo_demo__config'] = '{"key": "value"}'
        self.assertDictEqual(parse(keep_int=False), {'a': '2', 'env': 'yes', 'demo_config': {'key': 'value'}, 'demo': {'config': {'key': 'value'}}})

        # cli
        sys.argv = [SCRIPT_PATH, '--a=3', '--cli=yes']
        self.assertDictEqual(parse(keep_int=False), {'a': '3', 'cli': 'yes', 'env': 'yes', 'demo_config': {'key': 'value'}, 'demo': {'config': {'key': 'value'}}})
        sys.argv.append('--a=4')
        self.assertDictEqual(parse(keep_int=False), {'a': ['3', '4'], 'cli': 'yes', 'env': 'yes', 'demo_config': {'key': 'value'}, 'demo': {'config': {'key': 'value'}}})

if __name__ == '__main__':
    unittest.main()