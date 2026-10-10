---
title: Hardware Detection, udev, and Module Autoloading
category: hardware
source_url: https://wiki.archlinux.org/title/Udev
---

# Hardware Detection, udev, and Module Autoloading

## How Hardware Triggers Drivers
When a PCI, USB, or ACPI device is plugged into the system, the Linux kernel detects the device and generates a uevent containing the hardware device identifier (`MODALIAS`).
The `systemd-udevd` daemon receives the uevent and invokes `modprobe $MODALIAS`.

## Diagnosing Autoload Failures
If a device is connected but no driver loads:
1. Find device ID: `lspci -nn` or `lsusb`.
2. Check alias mapping: `modprobe -c | grep -i <device_id>`.
3. Check if the module is blacklisted in `/etc/modprobe.d/`.
4. Inspect `dmesg` to see if the driver loaded but failed to attach to the device due to missing firmware or hardware timeout.
