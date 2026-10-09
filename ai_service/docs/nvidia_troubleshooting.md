# NVIDIA Kernel Module Troubleshooting

## Overview

NVIDIA GPU drivers on Linux use kernel modules (`nvidia`, `nvidia_modeset`, `nvidia_uvm`, `nvidia_drm`) that must match both the driver version and the running kernel. NVIDIA module issues are among the most common kernel module problems due to the proprietary nature of the driver and frequent kernel updates.

## Module Hierarchy

The NVIDIA driver installs several kernel modules:

- `nvidia` — Core GPU driver module
- `nvidia_modeset` — Kernel Mode Setting (KMS) support
- `nvidia_uvm` — Unified Virtual Memory for CUDA
- `nvidia_drm` — Direct Rendering Manager integration
- `nvidia_peermem` — GPU Direct RDMA (optional)

Dependencies: `nvidia_drm` → `nvidia_modeset` → `nvidia` and `nvidia_uvm` → `nvidia`.

## Common Issues

### nouveau Conflict

The open-source `nouveau` driver conflicts with the proprietary NVIDIA driver. Both cannot be loaded simultaneously.

Symptoms:
- NVIDIA module fails to load
- Error message: "NVIDIA kernel module has a version mismatch"
- Xorg/Wayland uses nouveau instead of nvidia

Solution:
1. Blacklist nouveau: create `/etc/modprobe.d/blacklist-nouveau.conf`:
   ```
   blacklist nouveau
   options nouveau modeset=0
   ```
2. Regenerate initramfs:
   - Ubuntu/Debian: `sudo update-initramfs -u`
   - RHEL/Fedora: `sudo dracut -f`
3. Reboot

### Kernel Version Mismatch

After a kernel update, the NVIDIA module compiled for the previous kernel won't load.

Symptoms:
- `modprobe nvidia` fails
- dmesg shows: "NVRM: API mismatch" or "version magic" errors
- `nvidia-smi` reports "NVIDIA-SMI has failed"

Solutions:
1. **DKMS**: If installed via DKMS, run `sudo dkms autoinstall`
2. **Package reinstall**: `sudo apt install --reinstall nvidia-driver-<version>` (Ubuntu) or `sudo dnf reinstall akmod-nvidia` (Fedora)
3. **Manual rebuild**: Download the `.run` installer from NVIDIA and run it with `--kernel-source-path=/usr/src/linux-headers-$(uname -r)`

### Secure Boot

NVIDIA proprietary modules are not signed by distribution keys. With Secure Boot enabled:

- Module loading fails with "Required key not available"
- `dmesg` shows signature verification failure

Solutions:
1. Sign modules with a MOK key (see distribution-specific instructions)
2. Use `sudo mokutil --disable-validation` (temporary)
3. Ubuntu's `nvidia-driver` packages attempt automatic MOK enrollment

### Missing Kernel Headers

DKMS and manual compilation require kernel headers matching the running kernel.

Check:
```
ls /usr/src/linux-headers-$(uname -r)
```

Install:
- Ubuntu/Debian: `sudo apt install linux-headers-$(uname -r)`
- RHEL/Fedora: `sudo dnf install kernel-devel-$(uname -r)`

### GPU Not Detected

If the NVIDIA module loads but the GPU isn't detected:

1. Check PCI bus: `lspci | grep -i nvidia`
2. Check module parameters: `cat /sys/module/nvidia/parameters/*`
3. Check dmesg for GPU errors: `dmesg | grep -i nvidia`
4. Verify IOMMU settings for passthrough: check `intel_iommu=on` or `amd_iommu=on` in boot parameters

## Diagnostic Commands

```bash
# Check loaded NVIDIA modules
lsmod | grep nvidia

# Check driver version
cat /proc/driver/nvidia/version

# Check GPU status
nvidia-smi

# Check module info
modinfo nvidia

# Check for errors
dmesg | grep -i nvidia
journalctl -k | grep -i nvidia

# Check Secure Boot status
mokutil --sb-state
```
