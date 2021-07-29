#!/usr/bin/env python

import asyncio
import kasa
import time

plug_alias = 'Dehumidifier'

async def toggle(plug):
    print("Toggling " + plug_alias + "...")
    await plug.turn_on()
    print("Turned on!")
    time.sleep(10)
    await plug.turn_off()
    print("Turned off!")

def discover_plug():
    devices = asyncio.run(kasa.Discover.discover())

    plug_dev = None
    for addr, dev in devices.items():
        asyncio.run(dev.update())

        if dev.alias == plug_alias:
            plug_dev = dev

    return plug_dev

if __name__ == "__main__":
    plug = discover_plug()

    # Make sure we found the plug first
    try: plug
    except NameError: print("Error: device with alias '" + plug_alias + "' not found.")

    asyncio.run(toggle(plug))

