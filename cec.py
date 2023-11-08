import json
import sys
import logging
logger = logging.getLogger(__name__)

class ParseError(Exception):
    pass

def parse_json_value(s: str, keep_int: bool = True) -> dict | list | int | str:
    # if s is a json parseable string?
    try:
        s = json.loads(s)
    except json.JSONDecodeError:
        pass
    if not keep_int and isinstance(s, int):
            s = str(s)
    return s

def parse_json(config_filepath: str = 'config.json') -> dict:
    try:
        with open(config_filepath, 'r') as f:
            return json.load(f)
    except:
        logger.warning(f"Can't parse {config_filepath}, maybe file not found or currupted?")
        return {}


def parse_env(env_prefix: str = 'nemo', keep_int: bool = True) -> dict:
    import os
    config = {}
    # environment variables
    # NEMO_DEMO_CONFIG -> demo_config
    # nemo_demo_config -> demo_config
    env_prefix = env_prefix.lower() + '_'
    env_prefix_len = len(env_prefix)
    for k, v in os.environ.items():
        k = k.lower()
        if k.startswith(env_prefix):
            # multi path:
            # NEMO_DEMO__CONFIG -> demo.config / demo['config']
            # NEMO_DEMO__CONFIG__KEY -> demo.config.key / demo['config']['key']
            k = k[env_prefix_len:].split('__')
            v = parse_json_value(v, keep_int=keep_int)
            # set config
            if len(k) == 1:
                config[k[0]] = v
            else:
                tmp = config
                for sub_key in k[:-1]:
                    tmp[sub_key] = tmp.get(sub_key, {})
                    tmp = tmp[sub_key]
                tmp[k[-1]] = v
    return config


def parse_cli(keep_int: bool = True) -> dict:
    from collections import defaultdict
    config = defaultdict(list)
    for k, v in ((k.lstrip('-'), v) for k, v in (a.split('=') for a in sys.argv[1:])):
        v = parse_json_value(v, keep_int=keep_int)
        config[k].append(v)
    config = {k: v[0] if len(v) == 1 else v for k, v in config.items()}
    return config


def parse(config_filepath: str = 'config.json', env_prefix: str = 'nemo', keep_int: bool = True) -> dict:
    config = {}
    if config_filepath:
        config = parse_json(config_filepath)
    config.update(parse_env(env_prefix, keep_int=keep_int))
    config.update(parse_cli(keep_int=keep_int))
    return config