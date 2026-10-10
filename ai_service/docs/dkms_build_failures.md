---
title: Dynamic Kernel Module Support (DKMS) Troubleshooting
category: dkms
source_url: https://github.com/dell/dkms
---

# Dynamic Kernel Module Support (DKMS) Troubleshooting

## How DKMS Operates
DKMS is a framework designed to build and install dynamic kernel modules automatically whenever a new Linux kernel package is installed on the host. Source trees reside in `/usr/src/<module>-<version>/`.

## Compiler & GCC Mismatch
The Linux kernel is sensitive to compiler ABI differences. DKMS builds check the compiler version used to compile the running kernel (`cat /proc/version`):
If the system `gcc` binary is newer or older than the kernel build toolchain, compilation halts:
`compiler version check failed: kernel built with gcc-13, current CC is gcc-12`
Set `export CC=gcc-13` or update the default compiler via `update-alternatives`.

## Missing Kernel Headers
DKMS builds require the kernel C header files and build infrastructure at `/lib/modules/$(uname -r)/build`:
`Error! Your kernel headers for kernel <version> cannot be found at /lib/modules/<version>/build`
Resolution:
`sudo apt-get install linux-headers-$(uname -r)`
