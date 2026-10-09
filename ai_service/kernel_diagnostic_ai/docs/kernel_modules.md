# Linux Kernel Modules

## What Are Kernel Modules

Linux kernel modules are pieces of code that can be loaded into and unloaded from the running kernel on demand. They extend the functionality of the kernel without requiring a system reboot. Modules typically provide support for hardware devices, filesystems, network protocols, and other kernel-level features.

Kernel modules have the `.ko` (kernel object) file extension and are stored under `/lib/modules/$(uname -r)/`. Each module is compiled for a specific kernel version and must match the running kernel's version and configuration.

## Module Location

Modules are stored in `/lib/modules/<kernel-version>/`. The directory structure typically includes:

- `kernel/` — built-in kernel modules organized by subsystem
- `kernel/drivers/` — hardware device drivers
- `kernel/fs/` — filesystem modules
- `kernel/net/` — networking modules
- `kernel/sound/` — audio subsystem modules
- `extra/` or `updates/` — third-party or updated modules (e.g., DKMS-built modules)

## Listing Loaded Modules

The `lsmod` command displays all currently loaded kernel modules. It reads from `/proc/modules` and formats the output with columns:

- Module name
- Size in bytes
- Used-by count (number of other modules depending on this one)
- Used-by list (comma-separated names of dependent modules)

A module with a used-by count greater than 0 cannot be unloaded until its dependents are removed first.

## Module Information

The `modinfo` command displays detailed information about a kernel module file, including:

- `filename`: Path to the .ko file
- `description`: Human-readable description
- `author`: Module author
- `license`: License type (e.g., GPL)
- `depends`: Comma-separated list of module dependencies
- `vermagic`: Version magic string that must match the running kernel
- `parm`: Module parameters that can be set at load time
- `alias`: Alternative names for the module
- `srcversion`: Source version hash
- `sig_key`: Signing key identifier (for Secure Boot)

## /proc/modules

The `/proc/modules` virtual file provides raw information about loaded modules. Each line contains: module name, memory size, reference count, list of referring modules, state (Live, Loading, Unloading), and memory offset.

## Module Parameters

Many modules accept parameters that modify their behavior. Parameters can be set when loading a module:

```
modprobe module_name parameter=value
```

Current parameter values for a loaded module can be read from `/sys/module/<module_name>/parameters/`.
