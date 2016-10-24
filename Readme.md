`apt install libbluetooth-dev
 pip install pybluez`


SAP error fixes from [here](http://raspberrypi.stackexchange.com/questions/40839/sap-error-on-bluetooth-service-status) and [here](https://www.raspberrypi.org/forums/viewtopic.php?f=63&t=133263)

Edit the bluetooth service: `sudo nano /etc/systemd/system/bluetooth.target.wants/bluetooth.service`

change to `ExecStart=/usr/lib/bluetooth/bluetoothd --noplugin=sap -C`

do `sudo sdptool add SAP`

Drink a lot.

Consider life choices.

Figure out that `sudo hciconfig hci0 piscan` actually turns discovery mode on.

Realize that you can set a name with `sudo hciconfig hci0 name <name>`

On the pi:

`sudo rfcomm -r watch 0 1 /sbin/agetty -L rfcomm0 115200 linux`

On the access comp:

`sdptool add SAP
hcitool scan for MAC
sudo rfcomm bind /dev/rfcomm0 <MAC> 1
sudo screen /dev/rfcomm0 115200`
