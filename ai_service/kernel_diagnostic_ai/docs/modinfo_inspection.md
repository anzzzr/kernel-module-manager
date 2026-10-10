---
title: Module Inspection with modinfo
category: tools
source_url: https://man7.org/linux/man-pages/man8/modinfo.8.html
---

# Module Inspection with modinfo

## Inspecting Module Metadata
The `modinfo` command extracts information from the `.modinfo` ELF section of a module file or currently loaded kernel driver:
- `filename`: Absolute path to the `.ko` binary on disk.
- `vermagic`: Target kernel release and build characteristics.
- `depends`: Comma-separated list of required dependency modules.
- `firmware`: Paths to firmware files required by the driver.
- `parm`: Tunable module parameters and their data types.
- `signer` / `sig_key`: Cryptographic signature details for Secure Boot validation.
