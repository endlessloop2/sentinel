import pytest
import sys
import os
import re
os.environ['SENTINEL_ENV'] = 'test'
os.environ['SENTINEL_CONFIG'] = os.path.normpath(os.path.join(os.path.dirname(__file__), '../test_sentinel.conf'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'lib'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
import config

from keplerd import KeplerDaemon
from kepler_config import KeplerConfig


def test_keplerd():
    config_text = KeplerConfig.slurp_config_file(config.kepler_conf)
    network = 'mainnet'
    is_testnet = False
    genesis_hash = u'da7cf0305dd1dd0c59ea0f2b5f0cd2a65ebe5ce4d70b01907e17b830b6dbdf23' # change later
    for line in config_text.split("\n"):
        if line.startswith('testnet=1'):
            network = 'testnet'
            is_testnet = True
            genesis_hash = u'00000bafbc94add76cb75e2ec92894837288a481e5c005f6563d91623bf8bc2c'

    creds = KeplerConfig.get_rpc_creds(config_text, network)
    keplerd = KeplerDaemon(**creds)
    assert keplerd.rpc_command is not None

    assert hasattr(keplerd, 'rpc_connection')

    # Kepler testnet block 0 hash == 00000bafbc94add76cb75e2ec92894837288a481e5c005f6563d91623bf8bc2c
    # test commands without arguments
    info = keplerd.rpc_command('getinfo')
    info_keys = [
        'blocks',
        'connections',
        'difficulty',
        'errors',
        'protocolversion',
        'proxy',
        'testnet',
        'timeoffset',
        'version',
    ]
    for key in info_keys:
        assert key in info
    assert info['testnet'] is is_testnet

    # test commands with args
    assert keplerd.rpc_command('getblockhash', 0) == genesis_hash
