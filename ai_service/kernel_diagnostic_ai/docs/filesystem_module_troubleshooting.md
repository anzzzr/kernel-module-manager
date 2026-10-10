---
title: Filesystem Kernel Modules (ext4, zfs, btrfs, overlay)
category: filesystems
source_url: https://docs.kernel.org/filesystems/index.html
---

# Filesystem Kernel Modules (ext4, zfs, btrfs, overlay)

## Dynamic Filesystem Drivers
Filesystem drivers (`overlay`, `zfs`, `btrfs`, `cifs`, `nfs`) are frequently compiled as modules.
When mounting a filesystem (`mount -t overlay ...`), the `mount` command calls `mount()` system call, which requests module autoloading via `modprobe overlay`.

## Troubleshooting In-Use Filesystems
A filesystem module cannot be removed if any volume remains mounted.
To release the driver:
1. `umount -l /target/mountpoint`
2. Stop container runtimes holding overlay layers (Docker, containerd).
3. Confirm unmount before attempting `rmmod`.
