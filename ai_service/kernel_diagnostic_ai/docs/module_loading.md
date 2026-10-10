---
title: Module Loading Mechanism and Vermagic
category: loading
source_url: https://docs.kernel.org/admin-guide/module-signing.html
---

# Module Loading Mechanism and Vermagic

## Kernel Version Magic (vermagic)
Every compiled Linux kernel module embeds a `vermagic` string in its `.modinfo` ELF section. It records:
- Exact kernel release version (e.g. `6.8.0-40-generic`).
- SMP (Symmetric Multiprocessing) support.
- Preemption model (`preempt`).
- Module unload capability.
- Modversions CRC checking state.

During module loading via `init_module()` or `finit_module()`, the kernel compares its own internal vermagic against the module. If they mismatch, insertion fails immediately with `Exec format error` (`ENOEXEC`) and logs `version magic mismatch` to `dmesg`.

## Modversions (Symbol CRCs)
When `CONFIG_MODVERSIONS=y` is active, the kernel computes a 32-bit CRC hash for every exported symbol signature. If an in-tree kernel update changes a structure layout or function parameter, the CRC differs and insertion fails with:
`disagrees about version of symbol <symbol_name>`
