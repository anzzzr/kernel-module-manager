---
title: Kernel Module Reference Counting and Safe Unloading
category: lifecycle
source_url: https://docs.kernel.org/kbuild/modules.html
---

# Kernel Module Reference Counting and Safe Unloading

## Module Usage Counters
The kernel maintains an internal reference counter for every module. This counter increments when:
1. Another module calls an exported function of the module.
2. A filesystem provided by the module is mounted.
3. A character or block device exposed by the module is opened by a userspace process.
4. A network interface managed by the module is active (`UP`).

## Safe Removal Sequence
When `rmmod` returns `ERROR: Module <name> is in use`:
- Check dependencies: `lsmod | grep <name>`
- Identify holding processes: `lsof /dev/<device>` or `fuser -m /mountpoint`
- Take network interfaces down: `ip link set dev <interface> down`
- Stop associated system services: `systemctl stop <service>`
- Unload dependent child modules before attempting to unload the parent module.
