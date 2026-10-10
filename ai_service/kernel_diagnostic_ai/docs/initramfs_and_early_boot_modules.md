---
title: Initial RAM Filesystem (initramfs) and Early Boot Drivers
category: boot
source_url: https://wiki.debian.org/Initramfs
---

# Initial RAM Filesystem (initramfs) and Early Boot Drivers

## Early Boot Driver Loading
Storage controller drivers (NVMe, AHCI, SAS) and root filesystem drivers must be loaded before the root disk is mounted. These drivers are packaged into the `initramfs` image.

## Stale initramfs After Driver Updates
When updating out-of-tree drivers (e.g. DKMS, GPU drivers), the changes must be synced into the initramfs ramdisk:
```bash
sudo update-initramfs -u -k $(uname -r)
# Or on Fedora/RHEL:
sudo dracut --regenerate-all --force
```
Failure to update initramfs can cause early boot boot-loops or driver version mismatches.
