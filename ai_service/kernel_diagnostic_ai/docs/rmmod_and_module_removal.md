---
title: Kernel Module Removal: rmmod and modprobe -r
category: tools
source_url: https://man7.org/linux/man-pages/man8/rmmod.8.html
---

# Kernel Module Removal: rmmod and modprobe -r

## rmmod Mechanism
`rmmod` invokes the `delete_module()` system call to remove an unloaded module from the kernel.
It will fail with `Resource temporarily unavailable` (EBUSY) if:
- Any other module depends on it.
- Its refcount is greater than 0.

## Recursive Removal with modprobe -r
`modprobe -r <module>` removes the specified module AND recursively attempts to unload any unused dependent modules that were pulled in with it, provided their reference count is zero.
