# Module Loading Process

## Loading Sequence

When a kernel module is loaded, the following sequence occurs:

1. **Dependency Resolution**: `modprobe` reads `modules.dep` to identify required dependencies.
2. **Dependency Loading**: All dependencies are loaded recursively, depth-first.
3. **File Reading**: The `.ko` file is read into memory.
4. **ELF Verification**: The kernel verifies the module is a valid ELF object.
5. **Version Check (vermagic)**: The kernel checks the module's `vermagic` string against the running kernel. If it doesn't match, loading fails with "invalid module format".
6. **Signature Verification**: On systems with Secure Boot or module signing enforcement, the kernel verifies the module's cryptographic signature.
7. **Symbol Resolution**: The kernel resolves all symbols (functions and variables) the module references. Unresolved symbols cause loading to fail with "Unknown symbol".
8. **Memory Allocation**: Kernel memory is allocated for the module's code and data sections.
9. **Relocation**: Code and data addresses are adjusted for the allocated memory region.
10. **Initialization**: The module's `init` function is called. If it returns non-zero, loading fails.

## vermagic String

The vermagic string encodes the kernel version and configuration the module was built against. Example:

```
5.15.0-91-generic SMP preempt mod_unload modversions
```

It includes:
- Kernel version (e.g., 5.15.0-91-generic)
- SMP (Symmetric Multi-Processing) support
- Preemption model
- Module unload support
- Module versioning (modversions)

A vermagic mismatch means the module was compiled for a different kernel version or configuration. Solutions:

1. Install the correct module version for the running kernel.
2. Rebuild the module for the current kernel using DKMS or manual compilation.
3. As a last resort, use `modprobe --force` (dangerous, may cause kernel instability).

## Signature Verification

With Secure Boot enabled, the kernel may enforce module signature verification. Unsigned or incorrectly signed modules will fail to load with errors like:

- "Required key not available"
- "Key was rejected by service"
- "Module verification failed"

Solutions:
- Sign the module with an enrolled Machine Owner Key (MOK)
- Disable Secure Boot (reduces system security)
- Use distribution-provided signed modules

## Common Loading Errors

### "module not found"
The module file doesn't exist in `/lib/modules/$(uname -r)/`. Causes:
- Module not installed
- Module name misspelled
- Module built for different kernel version
- `depmod` not run after module installation

### "invalid module format"
vermagic mismatch between module and running kernel. The module was compiled for a different kernel version.

### "Unknown symbol in module"
The module references a kernel symbol that doesn't exist. Causes:
- Missing dependency module
- Module incompatible with kernel version
- Kernel configuration doesn't export required symbols

### "Operation not permitted"
Loading modules requires CAP_SYS_MODULE capability or root access.
