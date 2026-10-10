---
title: Linux Kernel Modules Overview
category: architecture
source_url: https://docs.kernel.org/kbuild/modules.html
---

# Linux Kernel Modules Overview

## What Are Kernel Modules
Loadable Kernel Modules (LKMs) are object files containing code that extends the running Linux kernel without requiring a complete system reboot. Modules are dynamically linked into the kernel address space.

## Module File Formats
Kernel modules are compiled ELF object files ending in `.ko` (Kernel Object) or compressed `.ko.zst` / `.ko.xz`. They reside in `/lib/modules/$(uname -r)/` and are organized by subsystem (`kernel/drivers/`, `kernel/net/`, `kernel/fs/`).

## Inspecting Active Modules with lsmod
The `lsmod` command formats `/proc/modules`, displaying:
- **Module Name**: Name of the loaded driver.
- **Size**: Memory footprint in bytes.
- **Used by**: Reference count and comma-separated list of dependent modules.

A module with a non-zero reference count cannot be unloaded with `rmmod` because active hardware handles or dependent modules hold open references.
