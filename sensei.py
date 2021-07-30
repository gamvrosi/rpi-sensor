#!/usr/bin/python
# This file is part of Sensei.
#
# Sensei is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sensei is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sensei.  If not, see <https://www.gnu.org/licenses/>.
#
# Sensei, Copyright (C) 2021 George Amvrosiadis

import os
import errno
import datetime
import sys, signal
import time
import configparser

def signal_handler(signal, frame):
	sys.exit(0)

SenseiDir = os.environ.get('HOME') + "/.sensei/"
SenseiLogDir = SenseiDir + "logs/"

# Initialize configuration values
SenseiHighRH = 100
SenseiLowRH = 0
SenseiInterval = 30

try:
	cfg = configparser.ConfigParser()
	cfg.read(SenseiDir + "sensei.config")
	SenseiHighRH = int(cfg.get('Humidistat','HighThreshold'))
	SenseiLowRH = int(cfg.get('Humidistat','LowThreshold'))
	SenseiInterval = int(cfg.get('General','IntervalSecs'))
except:
	print("Error: unable to initialize configuration values\n")
	system.exit(1)

# Create log dirs if they do not exist already
if not os.path.exists(SenseiLogDir):
    try:
        os.makedirs(SenseiLogDir)
    except OSError as exc:
        # Guard against race condition
        if exc.errno != errno.EEXIST:
            raise

signal.signal(signal.SIGINT, signal_handler)

while True:
	with open(SenseiLogDir + "test.txt", "a") as f:
		now = datetime.datetime.now()
		f.write(now.strftime('%Y-%m-%d %H:%M:%S :: ') + "Sensei up -- HighRH:" +
			str(SenseiHighRH) + "%, LowRH:" + str(SenseiLowRH) + "%, Interval=" +
			str(SenseiInterval) + "sec\n")
	time.sleep(SenseiInterval)

