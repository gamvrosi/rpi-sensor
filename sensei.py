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

# Sensor-specific libs
import adafruit_bme680
import board

# Plug-specific libs
import asyncio
import kasa

def signal_handler(signal, frame):
	sys.exit(0)

def parse_config():
	global SenseiHighRH
	global SenseiLowRH
	global SenseiInterval
	global SenseiPlugAlias
	global SenseiServerAddr

	try:
		cfg = configparser.ConfigParser()
		cfg.read(SenseiDir + "sensei.config")
		SenseiHighRH = int(cfg.get('Humidistat','HighThreshold'))
		SenseiLowRH = int(cfg.get('Humidistat','LowThreshold'))
		SenseiInterval = int(cfg.get('General','IntervalSecs'))
		SenseiPlugAlias = cfg.get('Plugs','HumidifierAlias')
		SenseiServerAddr = cfg.get('General','ServerAddr')
	except:
		print("Error: unable to initialize configuration values\n")
		system.exit(1)

def discover_plug():
	global SenseiPlugAlias

	devices = asyncio.run(kasa.Discover.discover())

	plug_dev = None
	for addr, dev in devices.items():
		asyncio.run(dev.update())

		if dev.alias == SenseiPlugAlias:
			plug_dev = dev

	return plug_dev

async def get_status(plug):
	await plug.update()
	return int(plug.is_on == True)

async def toggle_on(plug):
	await plug.turn_on()

async def toggle_off(plug):
	await plug.turn_off()

def check_trigger(plug, reading, high, low):
	global SenseiLogDir
	global SenseiRHLastOn

	plug_state = asyncio.run(get_status(plug))

	now = datetime.datetime.now()
	logname = SenseiLogDir + "plug_events_" + now.strftime('%y%m') + ".log"

	if (reading > high) and (not plug_state):
		asyncio.run(toggle_on(plug))
		SenseiRHLastOn = now
		with open(logname, "a") as f:
			f.write(now.strftime('%H:%M:%S') + " ON\n")
	elif (reading < low) and (plug_state):
		asyncio.run(toggle_off(plug))
		with open(logname, "a") as f:
			f.write(now.strftime('%H:%M:%S') + " OFF -- Duration = " +
					str(now-SenseiRHLastOn) + "\n")

def poll_sensor():
	global SenseiLogDir
	global SenseiHighRH
	global SenseiLowRH
	global RHplug
	global SenseiLatestReading

	# Create sensor object, communicating over the board's default I2C bus
	i2c = board.I2C()   # Uses board.SCL and board.SCA
	bme680 = adafruit_bme680.Adafruit_BME680_I2C(i2c, refresh_rate=1)

	# XXX: Change this to match the location's pressure (hPa) at sea level
	bme680.sea_level_pressure = 1013.25

	now = datetime.datetime.now()
	logname = SenseiLogDir + "sensor_data_" + now.strftime('%y%m%d') + ".log"

	SenseiLatestReading = "%s %s %s %s %s %s %s\n" % (now.strftime('%H:%M:%S '),
		format(bme680.temperature, '4.1f'),
		format(bme680.relative_humidity, '4.1f'),
		format(bme680.gas, '6d'),
		format(bme680.pressure, '9.3f'),
		format(bme680.altitude, '7.2f'),
		format(asyncio.run(get_status(RHplug)), '1d'))

	with open(logname, "a") as f:
		f.write(SenseiLatestReading)

	check_trigger(RHplug, bme680.relative_humidity, SenseiHighRH, SenseiLowRH)

def push_server_update():
	global SenseiLatestReading
	global SenseiServerAddr

	cmd = "ssh %s 'printf \"%s\" > /tmp/sensei.out'" % (SenseiServerAddr, SenseiLatestReading)
	stream = os.popen(cmd)

# Initialize global variables
SenseiDir = os.environ.get('HOME') + "/.sensei/"
SenseiLogDir = SenseiDir + "logs/"
SenseiRHLastOn = datetime.datetime.now()

SenseiServerAddr = ""
SenseiPlugAlias = 'Dehumidifier'
SenseiHighRH = 100
SenseiLowRH = 0
SenseiInterval = 30

# Latest logged reading
SenseiLatestReading = ""

parse_config()

# Create log dirs if they do not exist already
if not os.path.exists(SenseiLogDir):
	try:
		os.makedirs(SenseiLogDir)
	except OSError as exc:
		# Guard against race condition
		if exc.errno != errno.EEXIST:
			raise

signal.signal(signal.SIGINT, signal_handler)

# Find the plug first
RHplug = discover_plug()

# Make sure we found the plug first
try: RHplug
except NameError: print("Error: device with alias '" + SenseiPlugAlias + "' not found.")

while True:
	poll_sensor()
	push_server_update()
	time.sleep(SenseiInterval)

