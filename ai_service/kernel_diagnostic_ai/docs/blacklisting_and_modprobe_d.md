---
title: Modprobe Configuration Directives and Blacklisting
category: configuration
source_url: https://man7.org/linux/man-pages/man5/modprobe.d.5.html
---

# Modprobe Configuration Directives and Blacklisting

## Configuration Directives in modprobe.d
The modprobe utility parses configuration files ending in `.conf` located in `/etc/modprobe.d/` and `/usr/lib/modprobe.d/`:
- `blacklist <module>`: Prevents internal module aliases from being loaded automatically. Note: manual `modprobe <module>` can still load a blacklisted module unless an install directive is used.
- `install <module> /bin/false`: Guarantees the module will fail to load even if explicitly requested.
- `options <module> <param>=<val>`: Specifies fixed runtime module parameters passed to `init_module()`.
- `alias <wildcard> <module>`: Associates device identifiers with drivers.

## Diagnosing Blacklisted Failures
If `modprobe` reports `FATAL: Module <name> is blacklisted`:
Inspect files in `/etc/modprobe.d/` using `grep -rnw '/etc/modprobe.d/' -e '<module>'`.
Remove or comment out the blacklist line, then reload the configuration.
