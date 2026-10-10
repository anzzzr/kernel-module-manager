# Documentation Corpus Sources & Attribution

All documentation files located in `ai_service/docs/` and packaged under `kernel_diagnostic_ai/docs/` are original, concise technical summaries created for this project to ground LLM reasoning in Linux kernel driver troubleshooting. No long passages or copyrighted manuals were copied verbatim.

Below is the authoritative list of upstream sources, standards, and references used for each file:

| File | Category | Upstream Reference & URL |
|:---|:---|:---|
| `kernel_modules.html` / `kernel_modules.md` | Architecture | [Linux Kernel Documentation: Building External Modules](https://docs.kernel.org/kbuild/modules.html) |
| `modprobe.md` | Tools | [Linux man-pages: modprobe(8)](https://man7.org/linux/man-pages/man8/modprobe.8.html) |
| `module_loading.md` | Loading & Vermagic | [Linux Kernel Documentation: Module Signing and Vermagic](https://docs.kernel.org/admin-guide/module-signing.html) |
| `module_dependencies.md` | Dependencies | [Linux man-pages: depmod(8)](https://man7.org/linux/man-pages/man8/depmod.8.html) |
| `common_errors.md` | Troubleshooting | [Linux Kernel Documentation: Bug Hunting](https://docs.kernel.org/admin-guide/bug-hunting.html) |
| `nvidia_troubleshooting.md` | Hardware & DKMS | [Debian Wiki: NVIDIA Graphics Drivers](https://wiki.debian.org/NvidiaGraphicsDrivers) |
| `secure_boot_lockdown.md` | Security | [Linux Kernel Documentation: Kernel Lockdown LSM](https://docs.kernel.org/security/secrets/kernel_lockdown.html) |
| `firmware_loading.md` | Hardware Subsystems | [Linux Kernel Documentation: Firmware Loading API](https://docs.kernel.org/driver-api/firmware/index.html) |
| `dkms_build_failures.md` | Build Framework | [Dell Dynamic Kernel Module Support (DKMS) Upstream](https://github.com/dell/dkms) |
| `symbol_versioning_and_abi.md` | Kernel ABI | [Linux Kernel Documentation: Module Versioning & CRC](https://docs.kernel.org/kbuild/modules.html#module-versioning) |
| `module_refcounts_and_unloading.md` | Lifecycle | [Linux Kernel Documentation: Module Refcounts](https://docs.kernel.org/kbuild/modules.html) |
| `blacklisting_and_modprobe_d.md` | Configuration | [Linux man-pages: modprobe.d(5)](https://man7.org/linux/man-pages/man5/modprobe.d.5.html) |
| `depmod_and_module_dependencies.md` | Tools | [Linux man-pages: depmod.d(5)](https://man7.org/linux/man-pages/man5/depmod.d.5.html) |
| `insmod_vs_modprobe.md` | Tools | [Linux man-pages: insmod(8)](https://man7.org/linux/man-pages/man8/insmod.8.html) |
| `rmmod_and_module_removal.md` | Tools | [Linux man-pages: rmmod(8)](https://man7.org/linux/man-pages/man8/rmmod.8.html) |
| `modinfo_inspection.md` | Inspection | [Linux man-pages: modinfo(8)](https://man7.org/linux/man-pages/man8/modinfo.8.html) |
| `dmesg_and_kernel_logs.md` | Diagnostics | [Linux man-pages: dmesg(1)](https://man7.org/linux/man-pages/man1/dmesg.1.html) |
| `signing_kernel_modules.md` | Security | [Linux Kernel Documentation: Admin Guide Module Signing](https://docs.kernel.org/admin-guide/module-signing.html) |
| `udev_and_module_autoloading.md` | Hardware Probing | [Arch Linux Wiki: udev and Hardware Probing](https://wiki.archlinux.org/title/Udev) |
| `module_memory_and_resources.md` | Core Memory | [Linux Kernel Documentation: Memory Allocation Subsystems](https://docs.kernel.org/core-api/memory-allocation.html) |
| `wireless_module_troubleshooting.md` | Networking | [Linux Wireless Wiki: Subsystem Documentation](https://wireless.wiki.kernel.org/) |
| `filesystem_module_troubleshooting.md` | Filesystems | [Linux Kernel Documentation: Filesystems](https://docs.kernel.org/filesystems/index.html) |
| `alsa_sound_modules.md` | Multimedia | [ALSA Project Wiki: Sound Card Drivers](https://www.alsa-project.org/wiki/Main_Page) |
| `ethernet_driver_modules.md` | Networking | [Linux Foundation: Networking Drivers](https://wiki.linuxfoundation.org/networking/start) |
| `module_parameters_and_sysfs.md` | Configuration | [Linux Kernel Documentation: Kernel Parameters and sysfs](https://docs.kernel.org/admin-guide/kernel-parameters.html) |
| `initramfs_and_early_boot_modules.md` | Early Boot | [Debian Wiki: Initramfs Architecture](https://wiki.debian.org/Initramfs) |
