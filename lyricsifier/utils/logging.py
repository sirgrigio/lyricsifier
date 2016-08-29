import os
import json
import logging.config


def loadcfg(default_path='logging.json',
            default_level=logging.INFO,
            env_key='LOG_CFG'):
    env = os.getenv(env_key, None)
    path = default_path if not env else env
    if os.path.exists(path):
        with open(path, 'r', encoding='utf8') as f:
            config = json.load(f)
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
