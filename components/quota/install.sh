#!/usr/bin/env bash

if [[ $(id -u) != 0 ]]; then
   echo "This script should be run using sudo"
   exit 1
fi

if [[ ! -f /home/pi/RPi-Jukebox-RFID/settings/quota.ini ]]; then
    cp /home/pi/RPi-Jukebox-RFID/misc/sampleconfigs/quota.ini.sample /home/pi/RPi-Jukebox-RFID/settings/quota.ini
    chmod a+rw /home/pi/RPi-Jukebox-RFID/settings/quota.ini
fi

echo 'Installing quota service'
read -p "Press enter to continue " -n 1 -r
SERVICE_FILE=/etc/systemd/system/phoniebox-quota.service
if [[ -f "$SERVICE_FILE" ]]; then
   echo "$SERVICE_FILE exists.";
   echo 'systemctl daemon-reload'
   systemctl daemon-reload
   echo 'restarting service'
   systemctl restart phoniebox-quota.service
   read -p "Press enter to continue " -n 1 -r;
else
    cp -v ../../misc/sampleconfigs/phoniebox-quota.service.sample /etc/systemd/system/phoniebox-quota.service
    echo "systemctl start phoniebox-quota.service"
    systemctl start phoniebox-quota.service
    echo "systemctl enable phoniebox-quota.service"
    systemctl enable phoniebox-quota.service
fi
SERVICE_STATUS="$(systemctl is-active phoniebox-quota.service)"
if [[ "${SERVICE_STATUS}" = "active" ]]; then
    echo "Phoniebox Quota Service started correctly ....."
    echo "For further configuration of Phoniebox Quota consult components/quota/README.MD."
else
    echo ""
    FRED="\033[31m"
    FBOLD='\033[1;31m'
    RS="\033[0m"
    echo -e "$FRED"$FBOLD"Problem during installation occured $RS"
    echo "   Service not running, please check functionallity by running service.py "
    echo "   in the directory ~/RPi-Jukebox-RFID/components/quota: "
    echo "      $ cd ~/RPi-Jukebox-RFID/components/quota"
    echo "      $ python3 service.py"
    echo "   or check output of journaclctl by:"
    echo "      $ journalctl -u phoniebox-quota.service -f"
    exit 1
fi
