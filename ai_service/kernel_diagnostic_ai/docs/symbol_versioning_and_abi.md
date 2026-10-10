---
title: Kernel Symbol Versioning and Kernel ABI Breaks
category: abi
source_url: https://docs.kernel.org/kbuild/modules.html#module-versioning
---

# Kernel Symbol Versioning and Kernel ABI Breaks

## Symbol Exporting: EXPORT_SYMBOL
Kernel functions and global data structures are only accessible to loadable modules if explicitly declared with `EXPORT_SYMBOL()` or `EXPORT_SYMBOL_GPL()`.

## Symbol Version Mismatch
When a driver fails with:
`disagrees about version of symbol <symbol_name>`
`Unknown symbol <symbol_name> (err -22)`

The module was compiled against kernel headers whose symbol CRC differed from the currently running kernel.
Causes:
- Point releases modifying internal kernel subsystem data structures.
- Distribution security backports altering internal function prototypes.
- Loading out-of-tree modules without recompiling against the exact running kernel headers.

To fix: Always clean and recompile out-of-tree drivers against the exact headers of the target running kernel.
