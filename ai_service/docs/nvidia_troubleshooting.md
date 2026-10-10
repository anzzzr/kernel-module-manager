---
title: NVIDIA Driver Kernel Troubleshooting
category: hardware
source_url: https://wiki.debian.org/NvidiaGraphicsDrivers
---

# NVIDIA Driver Kernel Troubleshooting

## Version Mismatch and DKMS
The proprietary NVIDIA graphics driver comprises userspace libraries and kernel modules (`nvidia`, `nvidia_modeset`, `nvidia_uvm`, `nvidia_drm`).
After automated kernel package updates, the existing `.ko` modules fail vermagic checks.
Remediation:
```bash
sudo dkms autoinstall
sudo update-initramfs -u
```

## Conflict with nouveau
The open-source `nouveau` driver binds to the GPU PCI device at boot. If `nouveau` is loaded, `nvidia.ko` fails with `No such device`.
`nouveau` must be disabled in `/etc/modprobe.d/blacklist-nvidia.conf`:
```
blacklist nouveau
options nouveau modeset=0
```

## Driver In Use During Unload
Attempting to reload the NVIDIA driver while Xorg, Wayland, or `nvidia-persistenced` is running fails with `rmmod: ERROR: Module nvidia is in use`. Stop graphics display managers before unloading.
