#!/usr/bin/env python
# -*- coding: utf-8 -*-
################################################################################
##
## Project: NextGIS Borsch build system
## Author: Dmitry Baryshnikov <dmitry.baryshnikov@nextgis.com>
##
## Copyright (c) 2017 NextGIS <info@nextgis.com>
## License: GPL v.2
##
## Purpose: Post processing script
################################################################################

import fileinput
import os
import sys
import shutil

cmake_src_path = os.path.join(sys.argv[1], 'CMakeLists.txt')

if not os.path.exists(cmake_src_path):
    exit('Parse path not exists')

utilfile = os.path.join(os.getcwd(), os.pardir, 'cmake', 'util.cmake')

# Get values
ft_major = "0"
ft_minor = "0"
ft_patch = "0"

major_get = False
minor_get = False
patch_get = False

def extract_value(text):
    val_text = text.split("\"")
    return val_text[1]

with open(cmake_src_path) as f:
    for line in f:
        if "set(VERSION_MAJOR" in line:
            ft_major = extract_value(line)
            major_get = True
        elif "set(VERSION_MINOR" in line:
            ft_minor = extract_value(line)
            minor_get = True
        elif "set(VERSION_PATCH" in line:
            ft_patch = extract_value(line)
            patch_get = True

        if major_get and minor_get and patch_get:
            break

for line in fileinput.input(utilfile, inplace = 1):
    if "set(FT_MAJOR_VERSION " in line:
        print "    set(FT_MAJOR_VERSION " + ft_major + ")"
    elif "set(FT_MINOR_VERSION " in line:
            print "    set(FT_MINOR_VERSION " + ft_minor + ")"
    elif "set(FT_PATCH_VERSION " in line:
            print "    set(FT_PATCH_VERSION " + ft_patch + ")"
    else:
        print line,
