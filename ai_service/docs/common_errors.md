# Common Kernel Module Errors

## "FATAL: Module <name> not found in directory /lib/modules/<version>"

The module file does not exist for the running kernel version. Causes and solutions:

- **Module not installed**: Install the appropriate package (e.g., `linux-modules-extra-$(uname -r)` on Ubuntu).
- **Wrong kernel version**: After a kernel upgrade, modules built for the old kernel won't be found. Reboot into the new kernel or install modules for the current kernel.
- **Typo in module name**: Verify the correct module name using `find /lib/modules/$(uname -r) -name "*.ko*"`.
- **depmod not run**: Run `sudo depmod -a` to rebuild the module database.
- **DKMS module not built**: Run `sudo dkms autoinstall` to build pending DKMS modules.

## "Invalid module format"

The module's vermagic string doesn't match the running kernel. This happens when:

- The module was compiled for a different kernel version.
- The kernel configuration differs (e.g., SMP vs non-SMP, different preemption model).
- The module binary is corrupted.

Solutions:
- Rebuild the module for the current kernel version.
- Install the correct version of the module package.
- Use DKMS to automatically rebuild on kernel updates.

## "Unknown symbol in module"

The module references a symbol that no loaded module exports. Causes:

- **Missing dependency**: Load the dependency module first, or use `modprobe` which handles this automatically.
- **Incompatible kernel version**: The symbol was removed or renamed in the running kernel.
- **Missing kernel config option**: The kernel wasn't compiled with the configuration that exports the needed symbol.

Check which module provides the symbol:
```
grep <symbol_name> /lib/modules/$(uname -r)/modules.symbols
```

## "Required key not available" / "Key was rejected by service"

Secure Boot signature verification failed. The module is not signed with a trusted key. Solutions:

- Sign the module with a Machine Owner Key (MOK) enrolled in the UEFI firmware.
- Use distribution-provided pre-signed modules.
- Disable Secure Boot (reduces security).

Steps to sign a module:
1. Generate a signing key pair: `openssl req -new -x509 -newkey rsa:2048 -keyout MOK.priv -outform DER -out MOK.der -nodes -days 36500 -subj "/CN=My Module Signing Key/"`
2. Enroll the key: `sudo mokutil --import MOK.der`
3. Reboot and confirm enrollment in the MOK manager.
4. Sign the module: `sudo /usr/src/linux-headers-$(uname -r)/scripts/sign-file sha256 MOK.priv MOK.der <module.ko>`

## "Operation not permitted" (EPERM)

Module loading requires root privileges or the CAP_SYS_MODULE capability. Unprivileged users cannot load or unload kernel modules.

In containerized environments (Docker, Kubernetes), module operations may be restricted even for root unless the container has the appropriate capabilities or runs in privileged mode.

## "Module is in use"

The module cannot be unloaded because:

- Another module depends on it (check with `lsmod`).
- A process is using the module's functionality.
- The module's reference count is greater than zero.

Solutions:
- Unload dependent modules first.
- Stop processes using the module.
- Use `modprobe -r <module>` to remove the module and its unused dependencies.
- Check what's using it: `lsof | grep <module>` or inspect `/sys/module/<module>/refcnt`.

## DKMS Build Failures

DKMS (Dynamic Kernel Module Support) automatically rebuilds modules when the kernel is updated. Common DKMS failures:

- **Missing kernel headers**: Install `linux-headers-$(uname -r)`.
- **Missing build tools**: Install `build-essential` (Debian/Ubuntu) or `kernel-devel` and `gcc` (RHEL/Fedora).
- **Source code incompatibility**: The module source may not compile against the new kernel. Check DKMS logs in `/var/lib/dkms/<module>/<version>/build/make.log`.
- **Disk space**: DKMS compilation requires adequate space in `/var/lib/dkms/`.

Check DKMS status:
```
dkms status
```
