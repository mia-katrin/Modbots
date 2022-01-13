import os
import re
import argparse

def get_local_config(pardir=False):
    if pardir:
        local_dir = os.path.abspath(os.pardir)
    else:
        local_dir = os.path.dirname(os.path.realpath(__file__))
    regex = re.compile(r"(.+)_config.cfg")

    try:
        local_config = [name for name in os.listdir(local_dir) if regex.match(name)][0]
    except IndexError:
        raise ValueError("No config file!")
    return local_config

def get_config(pardir=False):
    # Add arguments
    parser = argparse.ArgumentParser(description='Default config get parser')
    parser.add_argument(
        '--config_file',
        type = str,
        help='The config file to configure this evolution',
        default=get_local_config(pardir)
    )

    args = parser.parse_args()

    from localconfig import config
    if pardir:
        config.read(os.path.abspath(os.pardir) + "/" + args.config_file)
    else:
        config.read(args.config_file)

    return config
