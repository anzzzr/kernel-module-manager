# modprobe — Module Loading Utility

## Overview

`modprobe` is the standard utility for loading and removing kernel modules in Linux. Unlike `insmod`, which requires a full path to the module file, `modprobe` searches the module directory for the correct file and automatically handles dependencies.

## Basic Usage

Load a module:
```
modprobe <module_name>
```

Remove a module:
```
modprobe -r <module_name>
```

List module dependencies without loading:
```
modprobe --show-depends <module_name>
```

Dry-run (show what would be done):
```
modprobe -n -v <module_name>
```

## How modprobe Works

1. Reads `/lib/modules/$(uname -r)/modules.dep` to determine dependencies.
2. Loads all required dependency modules first, in order.
3. Loads the requested module using the `init_module()` or `finit_module()` system call.
4. Module initialization code runs in kernel space.

## modprobe vs insmod

`insmod` loads a single module from a specified file path without dependency resolution. `modprobe` is the preferred tool because it:

- Resolves and loads dependencies automatically
- Searches standard module directories
- Supports module aliases and configuration
- Can remove modules and their unused dependencies

## Configuration

modprobe reads configuration from:

- `/etc/modprobe.d/*.conf` — distribution and system configuration
- `/etc/modprobe.conf` (deprecated)
- `/lib/modprobe.d/*.conf` — distribution defaults

Configuration options include:

- `alias <name> <module>` — create an alias for a module
- `options <module> <param>=<value>` — set default parameters
- `blacklist <module>` — prevent automatic loading
- `install <module> <command>` — run a command instead of loading normally
- `softdep <module> pre: <deps> post: <deps>` — soft dependencies

## Blacklisting Modules

To prevent a module from loading automatically:

1. Create a file in `/etc/modprobe.d/` (e.g., `/etc/modprobe.d/blacklist-custom.conf`)
2. Add: `blacklist <module_name>`
3. Optionally add: `install <module_name> /bin/false` to prevent manual loading too
4. Run `update-initramfs -u` (Debian/Ubuntu) or `dracut -f` (RHEL/Fedora)

## rmmod

`rmmod` removes a loaded module. It will fail if:

- The module is in use by another module (reference count > 0)
- The module is in use by a process
- The module does not support removal (no exit function)

Use `modprobe -r` instead of `rmmod` to also remove unused dependencies.
