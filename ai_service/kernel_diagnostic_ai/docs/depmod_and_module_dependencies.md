---
title: The depmod Indexing Architecture and modules.dep
category: tools
source_url: https://man7.org/linux/man-pages/man8/depmod.8.html
---

# The depmod Indexing Architecture and modules.dep

## Generation of Module Maps
When the kernel boots or packages update, `depmod` parses the symbol tables of every `.ko` file under `/lib/modules/$(uname -r)`.
It outputs:
- `modules.dep`: Colon-separated list of dependencies for each module path.
- `modules.symbols`: Map of symbol names to module filenames.
- `modules.alias`: Hardware device ID alias strings.

## Stale Dependency Cache Symptoms
If new modules are copied into `/lib/modules/` manually or via driver installers without running `depmod`:
`modprobe: FATAL: Module <name> not found in directory /lib/modules/<version>`
Running `sudo depmod -a` refreshes all binary cache indexes (`modules.dep.bin`) and resolves the lookup failure.
