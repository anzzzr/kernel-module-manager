---
title: Kernel Module Memory Allocation and Resource Limits
category: resources
source_url: https://docs.kernel.org/core-api/memory-allocation.html
---

# Kernel Module Memory Allocation and Resource Limits

## vmalloc Area Allocation
Kernel modules are loaded into the module vmalloc virtual memory space rather than physical RAM directly.
On architectures with limited vmalloc space, module insertion may fail with `ENOMEM` (Cannot allocate memory) if the vmalloc zone is exhausted.

## Resource Conflicts (EBUSY)
When a driver's `init()` function attempts to claim IO ports, memory-mapped registers (MMIO), or IRQ lines already reserved by another driver, initialization fails with `Resource temporarily unavailable` or `Device or resource busy`.
Inspect `/proc/ioports` and `/proc/iomem` to identify conflicting hardware reservations.
