---
title: Differences Between insmod and modprobe
category: tools
source_url: https://man7.org/linux/man-pages/man8/insmod.8.html
---

# Differences Between insmod and modprobe

## Low-Level insmod
`insmod` is a low-level utility that executes the `init_module` system call directly with an explicit file path (`insmod /path/to/driver.ko`).
It does not:
- Resolve dependent modules.
- Search `/lib/modules/`.
- Parse `/etc/modprobe.d/` configuration options.
- Honor blacklist directives.

If dependencies are missing, `insmod` immediately fails with `Unknown symbol in module`.

## High-Level modprobe
`modprobe` is the recommended standard tool for module management. It consults `modules.dep.bin`, automatically loads all required prerequisite modules in topological order, and applies runtime parameters from `/etc/modprobe.d/`.
