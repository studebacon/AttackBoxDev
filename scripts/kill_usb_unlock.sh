#!/bin/sh

if [ "$EUID" -ne 0 ]
  then echo "Please run as root"
  exit
fi

lsblk

echo "Enter USB Device (/dev/sda):"
read USB_DEVICE

echo "Enter Encrypted Partition (/dev/nvme0n1p3):"
read LUKS_DEVICE

if [ ! -b $USB_DEVICE ]; then
    echo "USB device does not exist."
    exit
fi


if [ ! -b $LUKS_DEVICE ]; then
    echo "LUKS device does not exist." 
    exit
fi


#remove old key if exists on slot 1
echo ""
echo "If LUKS Slot 1 key exists, delete (requires Slot 0 passphrase)"
echo ""
cryptsetup luksKillSlot ${LUKS_DEVICE} 1


rmdir /root/usbkey
mkdir /root/usbkey
mount ${USB_DEVICE}1 /root/usbkey
shred -u /root/usbkey/key.bin
umount /root/usbkey
