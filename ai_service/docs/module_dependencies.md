---
title: Module Dependencies and depmod
category: dependencies
source_url: https://man7.org/linux/man-pages/man8/depmod.8.html
---

# Module Dependencies and depmod

## The depmod Indexer
The `depmod` command scans `/lib/modules/$(uname -r)` and generates lookup maps:
- `modules.dep` / `modules.dep.bin`: Direct and transitive dependency paths.
- `modules.symbols.bin`: Reverse mapping of symbol names to provider modules.
- `modules.alias.bin`: Hardware PCI/USB IDs mapped to kernel drivers.

## Resolving Missing Dependency Failures
When inserting a module returns `Unknown symbol in module, or unknown parameter`, it indicates a prerequisite module exporting that symbol is absent from memory.
To inspect dependencies prior to loading:
```bash
modprobe --show-depends <module_name>
```
If dependencies exist on disk but modprobe fails to identify them, run `sudo depmod -a` to regenerate the dependency cache.
