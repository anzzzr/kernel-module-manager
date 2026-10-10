---
title: Kernel Module Parameters and /sys/module
category: configuration
source_url: https://docs.kernel.org/admin-guide/kernel-parameters.html
---

# Kernel Module Parameters and /sys/module

## Inspecting and Modifying Parameters
Module parameters can be passed at load time via `modprobe <module> <param>=<value>` or permanently configured in `/etc/modprobe.d/*.conf`.
At runtime, active parameters are exposed in sysfs under:
`/sys/module/<module>/parameters/`

## Invalid Parameter Errors
Passing unrecognized parameter names to `modprobe` triggers:
`modprobe: ERROR: could not insert '<module>': Unknown symbol in module, or unknown parameter`
Verify valid module parameters and descriptions with:
`modinfo -p <module>`
