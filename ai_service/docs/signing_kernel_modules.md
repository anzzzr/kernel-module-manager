---
title: Cryptographic Signing of Linux Kernel Modules
category: security
source_url: https://docs.kernel.org/admin-guide/module-signing.html
---

# Cryptographic Signing of Linux Kernel Modules

## Kernel Module Signing Architecture
Linux kernels built with `CONFIG_MODULE_SIG=y` verify the cryptographic signature appended to the end of a `.ko` file against keys stored in the system trusted keyring.
The signature format uses PKCS#7 / CMS standards.

## Signing Out-of-Tree Modules
To manually sign a kernel module:
```bash
/usr/src/linux-headers-$(uname -r)/scripts/sign-file   sha256   /path/to/MOK.priv   /path/to/MOK.der   /lib/modules/$(uname -r)/updates/dkms/driver.ko
```
Once signed with an enrolled MOK certificate, the module will load under UEFI Secure Boot without triggering `Key was rejected by service`.
