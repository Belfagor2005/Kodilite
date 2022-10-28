#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
from os import listdir as os_listdir

scripts = "/usr/lib/enigma2/python/Plugins/Extensions/KodiLite/scripts"


if os.path.exists(scripts):
    for name in os_listdir(scripts):
        if "script." in name:
            fold = scripts + "/" + name + "/lib"
            sys.path.append(fold)
            
