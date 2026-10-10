---
title: UEFI Secure Boot, Kernel Lockdown, and MOK Keys
category: security
source_url: https://docs.kernel.org/security/secrets/kernel_lockdown.html
---

# UEFI Secure Boot, Kernel Lockdown, and MOK Keys

## Kernel Lockdown LSM
When UEFI Secure Boot is enabled in motherboard firmware, modern Linux kernels activate the Lockdown LSM in `confidentiality` or `integrity` mode.
In lockdown mode, loading unsigned kernel modules is completely prohibited to prevent ring-0 code tampering.

## Failure Signatures in dmesg
- `Lockdown: modprobe: unsigned module loading is restricted`
- `Loading of unsigned module is rejected`
- `PKCS#7 signature not found`
- `Key was rejected by service` (Error -129 / -ENOKEY)

## Enrolling Keys with mokutil
To allow third-party or out-of-tree modules (e.g., VirtualBox, custom PCIe drivers):
1. Generate an X.509 MOK key pair: `openssl req -new -x509 -newkey rsa:2048 -keyout MOK.priv -out MOK.der -nodes -days 36500 -subj "/CN=Custom Driver Key/"`
2. Enroll the key into the Machine Owner Key (MOK) database: `sudo mokutil --import MOK.der`
3. Reboot the machine and complete the "Enroll MOK" screen in UEFI Shim.
4. Sign the module: `/usr/src/linux-headers-$(uname -r)/scripts/sign-file sha256 MOK.priv MOK.der module.ko`
