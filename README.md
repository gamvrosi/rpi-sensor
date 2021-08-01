# sensei-omnistat
Sensei is a Raspberry Pi program that collects BME680 sensor data and uses it to
control a Kasa plug. It can be used to build an omnistat, i.e., a thermostat,
humidistat, etc.

![sensei_sh-day](https://user-images.githubusercontent.com/6475334/127780819-21d7ce1e-bd1d-4cba-a4fe-9ee1b3e85308.png)

# Environment Setup

* Configure default Python version on your Pi
  ```bash
  sudo update-alternatives --install /usr/bin/python python /usr/bin/python2.7 1
  sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.7 2
  ```

* Install python-kasa
  ```bash
  pip3 install python-kasa --pre
  ```

* Add local bin folder to your path by editing .profile in the user home
  directory to append:
  ```bash
  export PATH="$HOME/.local/bin:$PATH"
  ```

* Power off RPi and connect BME680 sensor to GPIO pins. For STEMMA-QT follow
  this guide:
  * Red wire is VIN (3-5V) -> GPIO1
  * Blk wire is GND -> GPIO6
  * Ylw wire is SCK -> SCL or GPIO3
  * Blu wire is SDI -> SDA or GPIO5

* Enable the I2C interface through the `raspi-config` command
  Pro-tip: consider installing `i2c-tools` to test for detected devices

* Install CircuitPython BME680 library
  ```bash
  pip3 install adafruit-circuitpython-bme680
  ```
* Create `systemd` Sensei service
  ```bash
  sudo cp sensei.service /etc/systemd/system/sensei.service
  ```
  Make sure the path to `sensei.py` is correct.

* You can start the service with
  ```bash
  sudo systemctl start sensei
  ```
  And automatically get it to start on boot with
  ```bash
  sudo systemctl enable sensei
  ```

# Server-side Setup
The Pi is responsible for collecting sensor data and controlling the smart plug,
then periodically pushing the latest measurements to a remote server. The remote
server will be responsible for visualizing the sensor/plug state using Munin.

* Set up password-less access from Pi to your Server via `ssh`.

* Create a `/var/log/munin/sensei.out` file on the server owned by the user you
  will ssh as, and make it readable by everyone

* Install Munin plugin
  ```bash
  sudo cp sensei.sh .
  sudo ln -s /usr/share/munin/plugins/sensei.sh sensei.sh
  sudo service munin-node restart
  ```

