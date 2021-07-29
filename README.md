# rpi-sensor
Raspberry Pi program that collects BME680 sensor data and uses it to control a Kasa plug

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

* Add local bin folder to your path by editing .profile in the user home directory to append:
  ```bash
  export PATH="$HOME/.local/bin:$PATH"
  ```

