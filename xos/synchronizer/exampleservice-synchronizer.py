#!/usr/bin/env python

# Runs the standard XOS synchronizer

import importlib
import os
import sys
from xosconfig import Config

config_file = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) + '/exampleservice_config.yaml')
Config.init(config_file, 'synchronizer-config-schema.yaml')

synchronizer_path = os.path.join(os.path.dirname(
    os.path.realpath(__file__)), "../../synchronizers/new_base")
sys.path.append(synchronizer_path)
mod = importlib.import_module("xos-synchronizer")
mod.main()

