import argparse
import toml
import sys

_config_path = "./config.toml"

""" TODO redo in main
import __main__ as main
if hasattr(main, '__file__'):
    _parser = argparse.ArgumentParser()
    _parser.add_argument('--config', default='./config.toml', type=str)
    args = _parser.parse_args(sys.argv[1:])
    _config_path = args.config
"""
    
def reload():
    # To use in an interractive environment to relead config object when file is changed.
    global _CONFIG
    _CONFIG = toml.load(_config_path)

def config(keys=[]):
    obj = _CONFIG
    for key in keys:
        obj = obj[key]
    return obj

reload()