# Module Dependencies

## How Dependencies Work

Linux kernel modules can depend on symbols (functions and variables) exported by other modules. When module A uses a symbol from module B, module A depends on module B, and B must be loaded before A.

## depmod and modules.dep

The `depmod` command scans all modules in `/lib/modules/$(uname -r)/` and generates dependency information:

- `modules.dep` — text format listing each module and its dependencies
- `modules.dep.bin` — binary (optimized) format used by modprobe
- `modules.symbols` — maps symbols to the modules that export them
- `modules.alias` — maps device aliases to modules

`depmod` is run automatically during kernel and module installation. It must be re-run after manually copying module files.

Usage:
```
depmod -a                    # rebuild all dependency info
depmod -n <module>           # dry-run, show what would be generated
depmod -v                    # verbose output
```

## modules.dep Format

Each line in `modules.dep` lists a module and its dependencies:

```
kernel/drivers/net/wireless/intel/iwlwifi/iwlwifi.ko: kernel/net/wireless/cfg80211.ko
```

This means `iwlwifi.ko` depends on `cfg80211.ko`.

## Viewing Dependencies

```
modprobe --show-depends <module_name>
```

This shows all modules that would be loaded (in order) to satisfy the dependencies.

```
modinfo -F depends <module_name>
```

This shows the direct dependencies listed in the module's metadata.

## Missing Dependencies

When a module's dependency cannot be found:

- `modprobe` reports: "FATAL: Module <name> not found"
- Check if the dependency module exists: `find /lib/modules/$(uname -r) -name "*.ko" | grep <dep_name>`
- Run `depmod -a` to rebuild the dependency database
- The dependency module may need to be installed separately

## Circular Dependencies

Circular dependencies (A depends on B, B depends on A) are rare but can occur with incorrectly built modules. They cause `modprobe` to fail. Resolution typically requires rebuilding the modules correctly or loading them manually with `insmod` in the right order.

## Soft Dependencies

Soft dependencies (declared via `softdep` in modprobe configuration) are modules that enhance functionality but aren't strictly required. They're loaded if available but their absence doesn't prevent the main module from loading.

```
softdep moduleA pre: moduleB moduleC
softdep moduleA post: moduleD
```
