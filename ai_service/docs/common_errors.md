---
title: Common Kernel Module Errors Reference
category: troubleshooting
source_url: https://docs.kernel.org/admin-guide/bug-hunting.html
---

# Common Kernel Module Errors Reference

## "Module in use" (EBUSY / -16)
When `rmmod <module>` fails with `Resource temporarily unavailable` or `Module is in use`:
- The module has a non-zero refcount in `/proc/modules`.
- A mounted filesystem (e.g., ext4, xfs, overlay) is currently mounted.
- Dependent modules listed under `Used by` must be unloaded first.
- A user space daemon holds open device file descriptors under `/dev`.

## "Required key not available" (ENOKEY / -126)
Occurs on UEFI Secure Boot systems when kernel lockdown is active (`CONFIG_LOCKDOWN_LSM`).
The module binary is unsigned or signed with an un-enrolled certificate key.
Remediation:
- Sign the `.ko` binary with a private MOK key using `kmodsign` or `sign-file`.
- Enroll the public MOK key into the UEFI firmware via `mokutil --import MOK.der`.
