---
title: Ethernet NIC Driver Management
category: networking
source_url: https://wiki.linuxfoundation.org/networking/start
---

# Ethernet NIC Driver Management

## Intel and Realtek Drivers
Common Ethernet network interface controllers rely on drivers like `e1000e`, `igb`, `ixgbe`, and `r8169`.

## Interface Binding and Reference Counts
When an Ethernet interface is managed by `systemd-networkd`, `NetworkManager`, or has carrier link `UP`, the kernel module reference counter is locked.
To reload or replace network drivers:
```bash
sudo ip link set dev eth0 down
sudo modprobe -r e1000e
sudo modprobe e1000e
sudo ip link set dev eth0 up
```
