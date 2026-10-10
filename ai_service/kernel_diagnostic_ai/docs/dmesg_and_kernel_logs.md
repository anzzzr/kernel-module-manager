---
title: Kernel Ring Buffer and dmesg Diagnostics
category: diagnostics
source_url: https://man7.org/linux/man-pages/man1/dmesg.1.html
---

# Kernel Ring Buffer and dmesg Diagnostics

## Reading the Ring Buffer
`dmesg` prints the kernel message buffer (managed by `printk`). When module insertion or device driver probing fails, the kernel outputs detailed diagnostic diagnostics to this buffer.

## Key Log Indicators for Module Failures
- `version magic '...' should be '...'`: Vermagic string mismatch.
- `Unknown symbol <sym> (err -2)`: Missing prerequisite module.
- `Direct firmware load for <file> failed with error -2`: Missing firmware blob in `/lib/firmware`.
- `Lockdown: unsigned module loading is restricted`: UEFI Secure Boot violation.
- `disagrees about version of symbol <sym>`: ABI CRC mismatch.
