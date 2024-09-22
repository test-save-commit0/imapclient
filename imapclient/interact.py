import argparse
from getpass import getpass
from . import imapclient
from .config import create_client_from_config, get_config_defaults, parse_config_file
if __name__ == '__main__':
    main()
