"""Script to generate 42 benchmark evaluation test cases across 10 categories."""

import json
import os

CASES = [
    # 1. vermagic/kernel version mismatch (5 cases)
    {
        "id": "case_01_vermagic_nvidia",
        "module": "nvidia",
        "category": "vermagic/kernel version mismatch",
        "evidence": {
            "module": "nvidia",
            "commands": {
                "uname": "6.8.0-40-generic",
                "lsmod": "Module                  Size  Used by\nnvme                   61440  4\n",
                "modinfo": "filename:       /lib/modules/6.5.0-28-generic/updates/dkms/nvidia.ko\nversion:        535.183.01\nvermagic:       6.5.0-28-generic SMP preempt mod_unload modversions\ndepends:        nvidia-modeset\n",
                "dmesg": "[  124.512014] nvidia: version magic '6.5.0-28-generic SMP preempt mod_unload modversions' should be '6.8.0-40-generic SMP preempt mod_unload modversions'\n[  124.512028] nvidia: disagrees about version of symbol module_layout",
                "journalctl": "systemd-modules-load[412]: Failed to insert module 'nvidia': Exec format error",
                "modprobe_deps": "insmod /lib/modules/6.5.0-28-generic/updates/dkms/nvidia.ko",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: ERROR: could not insert 'nvidia': Exec format error"
            }
        },
        "gold_root_cause_category": "vermagic/kernel version mismatch",
        "gold_keywords": ["vermagic", "version mismatch", "module_layout", "rebuild", "dkms", "kernel headers"],
        "gold_doc_sources": ["module_loading.md", "nvidia_troubleshooting.md"],
        "source_type": "adapted_public_bug",
        "source_reference": "https://bugs.launchpad.net/ubuntu/+source/nvidia-graphics-drivers/+bug/1951493"
    },
    {
        "id": "case_02_vermagic_vboxguest",
        "module": "vboxguest",
        "category": "vermagic/kernel version mismatch",
        "evidence": {
            "module": "vboxguest",
            "commands": {
                "uname": "5.15.0-101-generic",
                "lsmod": "Module                  Size  Used by\next4                  983040  1\n",
                "modinfo": "filename:       /lib/modules/5.15.0-88-generic/misc/vboxguest.ko\nvermagic:       5.15.0-88-generic SMP mod_unload \ndepends:        \n",
                "dmesg": "[   34.120911] vboxguest: version magic '5.15.0-88-generic SMP mod_unload' should be '5.15.0-101-generic SMP mod_unload'\n[   34.120920] vboxguest: disagrees about version of symbol module_layout",
                "journalctl": "kernel: vboxguest: version magic mismatch on kernel update",
                "modprobe_deps": "insmod /lib/modules/5.15.0-88-generic/misc/vboxguest.ko",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: ERROR: could not insert 'vboxguest': Exec format error"
            }
        },
        "gold_root_cause_category": "vermagic/kernel version mismatch",
        "gold_keywords": ["vermagic", "kernel version", "disagrees about version", "exec format error"],
        "gold_doc_sources": ["module_loading.md", "common_errors.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_03_vermagic_zfs",
        "module": "zfs",
        "category": "vermagic/kernel version mismatch",
        "evidence": {
            "module": "zfs",
            "commands": {
                "uname": "6.2.0-39-generic",
                "lsmod": "Module                  Size  Used by\nspl                   188416  0\n",
                "modinfo": "filename:       /lib/modules/6.2.0-37-generic/extra/zfs.ko\nvermagic:       6.2.0-37-generic SMP preempt mod_unload \ndepends:        spl,znvpair,zcommon,zunicode,zlua,icp\n",
                "dmesg": "[   12.890112] zfs: version magic '6.2.0-37-generic' should be '6.2.0-39-generic'",
                "journalctl": "zfs-import-cache[601]: Failed to load ZFS module stack: version magic mismatch",
                "modprobe_deps": "insmod /lib/modules/6.2.0-37-generic/extra/spl.ko\ninsmod /lib/modules/6.2.0-37-generic/extra/zfs.ko",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: ERROR: could not insert 'zfs': Exec format error"
            }
        },
        "gold_root_cause_category": "vermagic/kernel version mismatch",
        "gold_keywords": ["version magic", "vermagic", "kernel update", "module_layout", "recompile"],
        "gold_doc_sources": ["module_loading.md", "common_errors.md"],
        "source_type": "adapted_public_bug",
        "source_reference": "https://github.com/openzfs/zfs/issues/13101"
    },
    {
        "id": "case_04_vermagic_wireguard",
        "module": "wireguard",
        "category": "vermagic/kernel version mismatch",
        "evidence": {
            "module": "wireguard",
            "commands": {
                "uname": "5.4.0-150-generic",
                "lsmod": "Module                  Size  Used by\nip6_udp_tunnel         16384  0\nudp_tunnel             20480  0\n",
                "modinfo": "filename:       /lib/modules/5.4.0-144-generic/kernel/net/wireguard/wireguard.ko\nvermagic:       5.4.0-144-generic SMP mod_unload \ndepends:        ip6_udp_tunnel,udp_tunnel\n",
                "dmesg": "[   88.192011] wireguard: version magic '5.4.0-144-generic SMP mod_unload' should be '5.4.0-150-generic SMP mod_unload'",
                "journalctl": "systemd[1]: Failed to start WireGuard interface wg0: Exec format error",
                "modprobe_deps": "insmod /lib/modules/5.4.0-144-generic/kernel/net/wireguard/wireguard.ko",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: ERROR: could not insert 'wireguard': Exec format error"
            }
        },
        "gold_root_cause_category": "vermagic/kernel version mismatch",
        "gold_keywords": ["vermagic", "5.4.0-144", "5.4.0-150", "version magic mismatch"],
        "gold_doc_sources": ["module_loading.md", "common_errors.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_05_vermagic_r8168",
        "module": "r8168",
        "category": "vermagic/kernel version mismatch",
        "evidence": {
            "module": "r8168",
            "commands": {
                "uname": "6.5.0-41-generic",
                "lsmod": "Module                  Size  Used by\n",
                "modinfo": "filename:       /lib/modules/6.5.0-35-generic/updates/dkms/r8168.ko\nvermagic:       6.5.0-35-generic SMP preempt mod_unload modversions\ndepends:        \n",
                "dmesg": "[    4.201991] r8168: version magic '6.5.0-35-generic SMP preempt mod_unload' should be '6.5.0-41-generic SMP preempt mod_unload'",
                "journalctl": "network-manager[702]: r8168 ethernet driver failed to load due to vermagic check",
                "modprobe_deps": "insmod /lib/modules/6.5.0-35-generic/updates/dkms/r8168.ko",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: ERROR: could not insert 'r8168': Exec format error"
            }
        },
        "gold_root_cause_category": "vermagic/kernel version mismatch",
        "gold_keywords": ["vermagic", "dkms", "r8168", "rebuild", "exec format error"],
        "gold_doc_sources": ["module_loading.md", "common_errors.md"],
        "source_type": "synthetic"
    },

    # 2. missing dependency (5 cases)
    {
        "id": "case_06_missing_dep_nftables",
        "module": "nft_compat",
        "category": "missing dependency",
        "evidence": {
            "module": "nft_compat",
            "commands": {
                "uname": "6.1.0-21-amd64",
                "lsmod": "Module                  Size  Used by\nx_tables               53248  0\n",
                "modinfo": "filename:       /lib/modules/6.1.0-21-amd64/kernel/net/netfilter/nft_compat.ko\ndepends:        nf_tables,x_tables\n",
                "dmesg": "[   45.102391] nft_compat: Unknown symbol nf_tables_valid_genid (err -2)\n[   45.102401] nft_compat: Unknown symbol nft_register_expr (err -2)",
                "journalctl": "modprobe[1082]: modprobe: ERROR: could not insert 'nft_compat': Unknown symbol in module, or unknown parameter (see dmesg)",
                "modprobe_deps": "insmod /lib/modules/6.1.0-21-amd64/kernel/net/netfilter/nf_tables.ko\ninsmod /lib/modules/6.1.0-21-amd64/kernel/net/netfilter/nft_compat.ko",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: ERROR: could not insert 'nft_compat': Unknown symbol in module",
                "dependency_check": "dependency nf_tables is not loaded"
            }
        },
        "gold_root_cause_category": "missing dependency",
        "gold_keywords": ["dependency", "depends", "nf_tables", "module_dependencies", "modprobe"],
        "gold_doc_sources": ["module_dependencies.md", "modprobe.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_07_missing_dep_overlay",
        "module": "overlay",
        "category": "missing dependency",
        "evidence": {
            "module": "overlay",
            "commands": {
                "uname": "5.10.0-8-amd64",
                "lsmod": "Module                  Size  Used by\n",
                "modinfo": "filename:       /lib/modules/5.10.0-8-amd64/kernel/fs/overlayfs/overlay.ko\ndepends:        \n",
                "dmesg": "",
                "journalctl": "dockerd[1204]: failed to start daemon: error initializing graphdriver: overlay2: failed to mount overlay: no such device",
                "modprobe_deps": "/lib/modules/5.10.0-8-amd64/modules.dep: No such file or directory",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: FATAL: Module overlay not found in directory /lib/modules/5.10.0-8-amd64"
            }
        },
        "gold_root_cause_category": "missing dependency",
        "gold_keywords": ["modules.dep", "depmod", "module not found", "dependency list"],
        "gold_doc_sources": ["modprobe.md", "module_dependencies.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_08_missing_dep_crypto",
        "module": "aesni_intel",
        "category": "missing dependency",
        "evidence": {
            "module": "aesni_intel",
            "commands": {
                "uname": "5.15.0-72-generic",
                "lsmod": "Module                  Size  Used by\n",
                "modinfo": "filename:       /lib/modules/5.15.0-72-generic/kernel/arch/x86/crypto/aesni-intel.ko\ndepends:        crypto_simd,cryptd\n",
                "dmesg": "[   19.001923] aesni_intel: Unknown symbol crypto_simd_usable (err -2)",
                "journalctl": "systemd[1]: cryptsetup failed because aesni_intel missing crypto_simd dependency",
                "modprobe_deps": "insmod /lib/modules/5.15.0-72-generic/kernel/crypto/cryptd.ko\ninsmod /lib/modules/5.15.0-72-generic/kernel/crypto/crypto_simd.ko\ninsmod /lib/modules/5.15.0-72-generic/kernel/arch/x86/crypto/aesni-intel.ko",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: ERROR: could not insert 'aesni_intel': Unknown symbol in module"
            }
        },
        "gold_root_cause_category": "missing dependency",
        "gold_keywords": ["dependency", "crypto_simd", "cryptd", "depends", "modprobe"],
        "gold_doc_sources": ["module_dependencies.md", "modprobe.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_09_missing_dep_nvidia_uvm",
        "module": "nvidia_uvm",
        "category": "missing dependency",
        "evidence": {
            "module": "nvidia_uvm",
            "commands": {
                "uname": "5.19.0-46-generic",
                "lsmod": "Module                  Size  Used by\n",
                "modinfo": "filename:       /lib/modules/5.19.0-46-generic/updates/dkms/nvidia-uvm.ko\ndepends:        nvidia\n",
                "dmesg": "[   72.102391] nvidia_uvm: Unknown symbol nvUvmInterfaceSessionDestroy (err -2)",
                "journalctl": "cuda-driver: failed to initialize unified memory because nvidia base module is absent",
                "modprobe_deps": "insmod /lib/modules/5.19.0-46-generic/updates/dkms/nvidia.ko\ninsmod /lib/modules/5.19.0-46-generic/updates/dkms/nvidia-uvm.ko",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: ERROR: could not insert 'nvidia_uvm': Unknown symbol in module"
            }
        },
        "gold_root_cause_category": "missing dependency",
        "gold_keywords": ["nvidia", "dependency", "depends: nvidia", "missing dependency", "nvidia-uvm"],
        "gold_doc_sources": ["nvidia_troubleshooting.md", "module_dependencies.md"],
        "source_type": "adapted_public_bug",
        "source_reference": "https://forums.developer.nvidia.com/t/nvidia-uvm-unknown-symbol/42111"
    },
    {
        "id": "case_10_missing_dep_cifs",
        "module": "cifs",
        "category": "missing dependency",
        "evidence": {
            "module": "cifs",
            "commands": {
                "uname": "6.1.0-18-amd64",
                "lsmod": "Module                  Size  Used by\n",
                "modinfo": "filename:       /lib/modules/6.1.0-18-amd64/kernel/fs/smb/client/cifs.ko\ndepends:        dns_resolver,cifs_arc4,fscache\n",
                "dmesg": "[   91.192014] cifs: Unknown symbol fscache_acquire_volume (err -2)",
                "journalctl": "mount.cifs: mount error: cifs filesystem not supported by the system",
                "modprobe_deps": "insmod /lib/modules/6.1.0-18-amd64/kernel/net/dns_resolver/dns_resolver.ko\ninsmod /lib/modules/6.1.0-18-amd64/kernel/fs/netfs/fscache.ko\ninsmod /lib/modules/6.1.0-18-amd64/kernel/fs/smb/client/cifs.ko",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: ERROR: could not insert 'cifs': Unknown symbol in module"
            }
        },
        "gold_root_cause_category": "missing dependency",
        "gold_keywords": ["fscache", "dns_resolver", "dependency", "depends", "symbol"],
        "gold_doc_sources": ["module_dependencies.md", "common_errors.md"],
        "source_type": "synthetic"
    },

    # 3. Secure Boot signature rejection (5 cases)
    {
        "id": "case_11_secureboot_nvidia",
        "module": "nvidia",
        "category": "Secure Boot signature rejection",
        "evidence": {
            "module": "nvidia",
            "commands": {
                "uname": "5.15.0-84-generic",
                "lsmod": "Module                  Size  Used by\n",
                "modinfo": "filename:       /lib/modules/5.15.0-84-generic/updates/dkms/nvidia.ko\nsigner:         \nsig_key:        \nsig_hashalgo:   \n",
                "dmesg": "[    8.412091] Lockdown: modprobe: unsigned module loading is restricted; see man kernel_lockdown.7\n[    8.412104] Loading of unsigned module is rejected\n[    8.412110] PKCS#7 signature not found",
                "journalctl": "systemd-modules-load[450]: Failed to insert module 'nvidia': Key was rejected by service",
                "modprobe_deps": "insmod /lib/modules/5.15.0-84-generic/updates/dkms/nvidia.ko",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: ERROR: could not insert 'nvidia': Key was rejected by service"
            }
        },
        "gold_root_cause_category": "Secure Boot signature rejection",
        "gold_keywords": ["Secure Boot", "unsigned module", "Key was rejected by service", "MOK", "mokutil", "lockdown"],
        "gold_doc_sources": ["module_loading.md", "nvidia_troubleshooting.md"],
        "source_type": "adapted_public_bug",
        "source_reference": "https://askubuntu.com/questions/1023036/key-was-rejected-by-service-when-trying-to-load-nvidia-driver"
    },
    {
        "id": "case_12_secureboot_vboxdrv",
        "module": "vboxdrv",
        "category": "Secure Boot signature rejection",
        "evidence": {
            "module": "vboxdrv",
            "commands": {
                "uname": "6.2.0-26-generic",
                "lsmod": "Module                  Size  Used by\n",
                "modinfo": "filename:       /lib/modules/6.2.0-26-generic/misc/vboxdrv.ko\nsigner:         \nsig_key:        \n",
                "dmesg": "[   14.020192] Lockdown: modprobe: unsigned module loading is restricted; see man kernel_lockdown.7\n[   14.020205] Loading of unsigned module is rejected",
                "journalctl": "kernel: Lockdown: modprobe: unsigned module loading is restricted; see man kernel_lockdown.7",
                "modprobe_deps": "insmod /lib/modules/6.2.0-26-generic/misc/vboxdrv.ko",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: ERROR: could not insert 'vboxdrv': Operation not permitted"
            }
        },
        "gold_root_cause_category": "Secure Boot signature rejection",
        "gold_keywords": ["Secure Boot", "lockdown", "unsigned module", "sign", "MOK"],
        "gold_doc_sources": ["module_loading.md", "common_errors.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_13_secureboot_broadcom",
        "module": "wl",
        "category": "Secure Boot signature rejection",
        "evidence": {
            "module": "wl",
            "commands": {
                "uname": "5.15.0-60-generic",
                "lsmod": "Module                  Size  Used by\ncfg80211              970752  0\n",
                "modinfo": "filename:       /lib/modules/5.15.0-60-generic/updates/dkms/wl.ko\nsigner:         \n",
                "dmesg": "[   18.231901] PKCS#7 signature not found\n[   18.231910] Loading of unsigned module is rejected\n[   18.231915] Lockdown: modprobe: unsigned module loading is restricted",
                "journalctl": "modprobe[612]: Failed to insert 'wl': Key was rejected by service",
                "modprobe_deps": "insmod /lib/modules/5.15.0-60-generic/updates/dkms/wl.ko",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: ERROR: could not insert 'wl': Key was rejected by service"
            }
        },
        "gold_root_cause_category": "Secure Boot signature rejection",
        "gold_keywords": ["Secure Boot", "Key was rejected", "PKCS#7", "unsigned", "mokutil"],
        "gold_doc_sources": ["module_loading.md", "common_errors.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_14_secureboot_evdi",
        "module": "evdi",
        "category": "Secure Boot signature rejection",
        "evidence": {
            "module": "evdi",
            "commands": {
                "uname": "6.5.0-28-generic",
                "lsmod": "Module                  Size  Used by\ndrm_kms_helper        249856  0\n",
                "modinfo": "filename:       /lib/modules/6.5.0-28-generic/updates/dkms/evdi.ko\nsigner:         Build time autogenerated kernel key\nsig_key:        74:81:92:...\nsig_hashalgo:   sha512\n",
                "dmesg": "[   22.102391] Loading of module with untrusted key is rejected\n[   22.102401] Certificate is not in the system trusted keyring",
                "journalctl": "systemd-modules-load: Failed to load evdi: Key was rejected by service",
                "modprobe_deps": "insmod /lib/modules/6.5.0-28-generic/updates/dkms/evdi.ko",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: ERROR: could not insert 'evdi': Key was rejected by service"
            }
        },
        "gold_root_cause_category": "Secure Boot signature rejection",
        "gold_keywords": ["untrusted key", "keyring", "Secure Boot", "enroll", "MOK"],
        "gold_doc_sources": ["module_loading.md", "common_errors.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_15_secureboot_custom_driver",
        "module": "my_pci_driver",
        "category": "Secure Boot signature rejection",
        "evidence": {
            "module": "my_pci_driver",
            "commands": {
                "uname": "6.8.0-31-generic",
                "lsmod": "Module                  Size  Used by\n",
                "modinfo": "filename:       /lib/modules/6.8.0-31-generic/extra/my_pci_driver.ko\n",
                "dmesg": "[    9.192014] Lockdown: modprobe: unsigned module loading is restricted; see man kernel_lockdown.7",
                "journalctl": "kernel: Loading of unsigned module is rejected",
                "modprobe_deps": "insmod /lib/modules/6.8.0-31-generic/extra/my_pci_driver.ko",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: ERROR: could not insert 'my_pci_driver': Operation not permitted"
            }
        },
        "gold_root_cause_category": "Secure Boot signature rejection",
        "gold_keywords": ["Lockdown", "kernel_lockdown", "unsigned module", "Secure Boot"],
        "gold_doc_sources": ["module_loading.md", "common_errors.md"],
        "source_type": "synthetic"
    },

    # 4. missing firmware (5 cases)
    {
        "id": "case_16_missing_fw_iwlwifi",
        "module": "iwlwifi",
        "category": "missing firmware",
        "evidence": {
            "module": "iwlwifi",
            "commands": {
                "uname": "6.1.0-9-amd64",
                "lsmod": "Module                  Size  Used by\ncfg80211              970752  0\n",
                "modinfo": "filename:       /lib/modules/6.1.0-9-amd64/kernel/drivers/net/wireless/intel/iwlwifi/iwlwifi.ko\nfirmware:       iwlwifi-ty-a0-gf-a0-59.ucode\nfirmware:       iwlwifi-so-a0-gf-a0.ucode\n",
                "dmesg": "[    3.412091] iwlwifi 0000:00:14.3: Direct firmware load for iwlwifi-so-a0-gf-a0.ucode failed with error -2\n[    3.412104] iwlwifi 0000:00:14.3: minimum version required: iwlwifi-so-a0-gf-a0-39\n[    3.412110] iwlwifi 0000:00:14.3: Failed to start RT ucode: -2",
                "journalctl": "kernel: iwlwifi: Direct firmware load failed with error -2",
                "modprobe_deps": "insmod /lib/modules/6.1.0-9-amd64/kernel/drivers/net/wireless/intel/iwlwifi/iwlwifi.ko",
                "loaded_check": "iwlwifi               458752  0"
            },
            "errors": {
                "dmesg": "Direct firmware load for iwlwifi-so-a0-gf-a0.ucode failed with error -2"
            }
        },
        "gold_root_cause_category": "missing firmware",
        "gold_keywords": ["firmware", "failed with error -2", "linux-firmware", "/lib/firmware", "iwlwifi"],
        "gold_doc_sources": ["common_errors.md", "kernel_modules.md"],
        "source_type": "adapted_public_bug",
        "source_reference": "https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=987114"
    },
    {
        "id": "case_17_missing_fw_amdgpu",
        "module": "amdgpu",
        "category": "missing firmware",
        "evidence": {
            "module": "amdgpu",
            "commands": {
                "uname": "6.5.0-18-generic",
                "lsmod": "Module                  Size  Used by\ndrm_suballoc_helper    16384  0\n",
                "modinfo": "filename:       /lib/modules/6.5.0-18-generic/kernel/drivers/gpu/drm/amd/amdgpu/amdgpu.ko\nfirmware:       amdgpu/navi10_sos.bin\nfirmware:       amdgpu/navi10_asd.bin\n",
                "dmesg": "[    2.102391] amdgpu 0000:03:00.0: Direct firmware load for amdgpu/navi10_sos.bin failed with error -2\n[    2.102401] [drm:amdgpu_device_init] *ERROR* Early init failed\n[    2.102410] amdgpu: Fatal error during GPU init",
                "journalctl": "kernel: amdgpu: Direct firmware load for amdgpu/navi10_sos.bin failed with error -2",
                "modprobe_deps": "insmod /lib/modules/6.5.0-18-generic/kernel/drivers/gpu/drm/amd/amdgpu/amdgpu.ko",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: ERROR: could not insert 'amdgpu': No such device"
            }
        },
        "gold_root_cause_category": "missing firmware",
        "gold_keywords": ["firmware", "error -2", "linux-firmware", "/lib/firmware/amdgpu", "navi10_sos.bin"],
        "gold_doc_sources": ["common_errors.md", "kernel_modules.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_18_missing_fw_ath10k",
        "module": "ath10k_pci",
        "category": "missing firmware",
        "evidence": {
            "module": "ath10k_pci",
            "commands": {
                "uname": "5.15.0-48-generic",
                "lsmod": "Module                  Size  Used by\nath10k_core           483328  0\n",
                "modinfo": "filename:       /lib/modules/5.15.0-48-generic/kernel/drivers/net/wireless/ath/ath10k/ath10k_pci.ko\ndepends:        ath10k_core\n",
                "dmesg": "[    5.981023] ath10k_pci 0000:02:00.0: Direct firmware load for ath10k/QCA6174/hw3.0/firmware-6.bin failed with error -2\n[    5.981035] ath10k_pci 0000:02:00.0: could not fetch firmware files (-2)",
                "journalctl": "kernel: ath10k_pci: could not fetch firmware files (-2)",
                "modprobe_deps": "insmod /lib/modules/5.15.0-48-generic/kernel/drivers/net/wireless/ath/ath10k/ath10k_pci.ko",
                "loaded_check": "ath10k_pci             49152  0"
            },
            "errors": {
                "dmesg": "Direct firmware load for ath10k/QCA6174/hw3.0/firmware-6.bin failed with error -2"
            }
        },
        "gold_root_cause_category": "missing firmware",
        "gold_keywords": ["firmware", "failed with error -2", "/lib/firmware", "ath10k", "package linux-firmware"],
        "gold_doc_sources": ["common_errors.md", "kernel_modules.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_19_missing_fw_r8169",
        "module": "r8169",
        "category": "missing firmware",
        "evidence": {
            "module": "r8169",
            "commands": {
                "uname": "6.1.0-22-amd64",
                "lsmod": "Module                  Size  Used by\nrealtek                32768  0\n",
                "modinfo": "filename:       /lib/modules/6.1.0-22-amd64/kernel/drivers/net/ethernet/realtek/r8169.ko\nfirmware:       rtl_nic/rtl8168h-2.fw\n",
                "dmesg": "[    1.821092] r8169 0000:01:00.0: Direct firmware load for rtl_nic/rtl8168h-2.fw failed with error -2\n[    1.821102] r8169 0000:01:00.0: Unable to load firmware rtl_nic/rtl8168h-2.fw (-2)",
                "journalctl": "kernel: r8169: Direct firmware load for rtl_nic/rtl8168h-2.fw failed with error -2",
                "modprobe_deps": "insmod /lib/modules/6.1.0-22-amd64/kernel/drivers/net/ethernet/realtek/r8169.ko",
                "loaded_check": "r8169                  98304  0"
            },
            "errors": {
                "dmesg": "Unable to load firmware rtl_nic/rtl8168h-2.fw (-2)"
            }
        },
        "gold_root_cause_category": "missing firmware",
        "gold_keywords": ["firmware", "rtl_nic", "error -2", "/lib/firmware", "non-free-firmware"],
        "gold_doc_sources": ["common_errors.md", "kernel_modules.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_20_missing_fw_btusb",
        "module": "btusb",
        "category": "missing firmware",
        "evidence": {
            "module": "btusb",
            "commands": {
                "uname": "6.2.0-37-generic",
                "lsmod": "Module                  Size  Used by\nbluetooth             679936  0\n",
                "modinfo": "filename:       /lib/modules/6.2.0-37-generic/kernel/drivers/bluetooth/btusb.ko\ndepends:        bluetooth\n",
                "dmesg": "[   11.412091] Bluetooth: hci0: Direct firmware load for intel/ibt-19-0-4.sfi failed with error -2\n[   11.412104] Bluetooth: hci0: Failed to load firmware file (-2)",
                "journalctl": "bluetoothd[820]: Failed to start bluetooth controller firmware load",
                "modprobe_deps": "insmod /lib/modules/6.2.0-37-generic/kernel/drivers/bluetooth/btusb.ko",
                "loaded_check": "btusb                  65536  0"
            },
            "errors": {
                "dmesg": "Bluetooth: hci0: Failed to load firmware file (-2)"
            }
        },
        "gold_root_cause_category": "missing firmware",
        "gold_keywords": ["firmware", "failed with error -2", "/lib/firmware/intel", "btusb", "linux-firmware"],
        "gold_doc_sources": ["common_errors.md", "kernel_modules.md"],
        "source_type": "synthetic"
    },

    # 5. blacklisted module (5 cases)
    {
        "id": "case_21_blacklist_nouveau",
        "module": "nouveau",
        "category": "blacklisted module",
        "evidence": {
            "module": "nouveau",
            "commands": {
                "uname": "6.5.0-28-generic",
                "lsmod": "Module                  Size  Used by\nnvidia_drm             77824  0\n",
                "modinfo": "filename:       /lib/modules/6.5.0-28-generic/kernel/drivers/gpu/drm/nouveau/nouveau.ko\n",
                "dmesg": "",
                "journalctl": "systemd-modules-load: Module 'nouveau' is blacklisted in /etc/modprobe.d/blacklist-nvidia.conf",
                "modprobe_deps": "",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: FATAL: Module nouveau is blacklisted"
            }
        },
        "gold_root_cause_category": "blacklisted module",
        "gold_keywords": ["blacklisted", "/etc/modprobe.d", "blacklist nouveau", "modprobe.d"],
        "gold_doc_sources": ["modprobe.md", "nvidia_troubleshooting.md"],
        "source_type": "adapted_public_bug",
        "source_reference": "https://wiki.debian.org/NvidiaGraphicsDrivers#Disabling_nouveau"
    },
    {
        "id": "case_22_blacklist_pcspkr",
        "module": "pcspkr",
        "category": "blacklisted module",
        "evidence": {
            "module": "pcspkr",
            "commands": {
                "uname": "5.15.0-91-generic",
                "lsmod": "Module                  Size  Used by\n",
                "modinfo": "filename:       /lib/modules/5.15.0-91-generic/kernel/drivers/input/misc/pcspkr.ko\n",
                "dmesg": "",
                "journalctl": "modprobe: Module pcspkr is blacklisted in /etc/modprobe.d/nobeep.conf",
                "modprobe_deps": "",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: FATAL: Module pcspkr is blacklisted"
            }
        },
        "gold_root_cause_category": "blacklisted module",
        "gold_keywords": ["blacklisted", "blacklist", "/etc/modprobe.d", "modprobe.d"],
        "gold_doc_sources": ["modprobe.md", "common_errors.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_23_blacklist_floppy",
        "module": "floppy",
        "category": "blacklisted module",
        "evidence": {
            "module": "floppy",
            "commands": {
                "uname": "6.1.0-15-amd64",
                "lsmod": "Module                  Size  Used by\n",
                "modinfo": "filename:       /lib/modules/6.1.0-15-amd64/kernel/drivers/block/floppy.ko\n",
                "dmesg": "",
                "journalctl": "kernel: modprobe: Module floppy is blacklisted",
                "modprobe_deps": "",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: FATAL: Module floppy is blacklisted"
            }
        },
        "gold_root_cause_category": "blacklisted module",
        "gold_keywords": ["blacklisted", "blacklist floppy", "/etc/modprobe.d", "modprobe.d"],
        "gold_doc_sources": ["modprobe.md", "common_errors.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_24_blacklist_usb_storage",
        "module": "usb_storage",
        "category": "blacklisted module",
        "evidence": {
            "module": "usb_storage",
            "commands": {
                "uname": "5.10.0-23-amd64",
                "lsmod": "Module                  Size  Used by\n",
                "modinfo": "filename:       /lib/modules/5.10.0-23-amd64/kernel/drivers/usb/storage/usb-storage.ko\n",
                "dmesg": "",
                "journalctl": "systemd[1]: Security policy: module usb_storage blacklisted in /etc/modprobe.d/security-hardening.conf",
                "modprobe_deps": "",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: FATAL: Module usb_storage is blacklisted"
            }
        },
        "gold_root_cause_category": "blacklisted module",
        "gold_keywords": ["blacklisted", "security", "/etc/modprobe.d", "blacklist"],
        "gold_doc_sources": ["modprobe.md", "common_errors.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_25_blacklist_snd_pcsp",
        "module": "snd_pcsp",
        "category": "blacklisted module",
        "evidence": {
            "module": "snd_pcsp",
            "commands": {
                "uname": "6.8.0-38-generic",
                "lsmod": "Module                  Size  Used by\nsnd_pcm               159744  0\n",
                "modinfo": "filename:       /lib/modules/6.8.0-38-generic/kernel/sound/drivers/pcsp/snd-pcsp.ko\n",
                "dmesg": "",
                "journalctl": "alsa-init: snd_pcsp is blacklisted in /etc/modprobe.d/alsa-base-blacklist.conf",
                "modprobe_deps": "",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: FATAL: Module snd_pcsp is blacklisted"
            }
        },
        "gold_root_cause_category": "blacklisted module",
        "gold_keywords": ["blacklisted", "/etc/modprobe.d", "alsa-base-blacklist", "blacklist"],
        "gold_doc_sources": ["modprobe.md", "common_errors.md"],
        "source_type": "synthetic"
    },

    # 6. module already loaded/in use (cannot unload) (5 cases)
    {
        "id": "case_26_in_use_overlay",
        "module": "overlay",
        "category": "module already loaded/in use",
        "evidence": {
            "module": "overlay",
            "commands": {
                "uname": "6.2.0-39-generic",
                "lsmod": "Module                  Size  Used by\noverlay               151552  24\n",
                "modinfo": "filename:       /lib/modules/6.2.0-39-generic/kernel/fs/overlayfs/overlay.ko\n",
                "dmesg": "",
                "journalctl": "systemd[1]: Failed to unload kernel module 'overlay': Resource temporarily unavailable",
                "modprobe_deps": "insmod /lib/modules/6.2.0-39-generic/kernel/fs/overlayfs/overlay.ko",
                "loaded_check": "overlay               151552  24"
            },
            "errors": {
                "rmmod": "rmmod: ERROR: Module overlay is in use"
            }
        },
        "gold_root_cause_category": "module already loaded/in use",
        "gold_keywords": ["in use", "Module is in use", "refcount", "used by", "rmmod", "unmount"],
        "gold_doc_sources": ["kernel_modules.md", "module_loading.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_27_in_use_nvidia",
        "module": "nvidia",
        "category": "module already loaded/in use",
        "evidence": {
            "module": "nvidia",
            "commands": {
                "uname": "6.5.0-35-generic",
                "lsmod": "Module                  Size  Used by\nnvidia_modeset        1556480  1\nnvidia_uvm            3489792  2\nnvidia               56623104  45 nvidia_modeset,nvidia_uvm\n",
                "modinfo": "filename:       /lib/modules/6.5.0-35-generic/updates/dkms/nvidia.ko\n",
                "dmesg": "",
                "journalctl": "systemd[1]: nvidia-persistenced[911]: holding open /dev/nvidia0",
                "modprobe_deps": "insmod /lib/modules/6.5.0-35-generic/updates/dkms/nvidia.ko",
                "loaded_check": "nvidia               56623104  45"
            },
            "errors": {
                "rmmod": "rmmod: ERROR: Module nvidia is in use by: nvidia_modeset nvidia_uvm"
            }
        },
        "gold_root_cause_category": "module already loaded/in use",
        "gold_keywords": ["in use", "used by", "dependent modules", "nvidia_modeset", "nvidia_uvm", "stop services"],
        "gold_doc_sources": ["nvidia_troubleshooting.md", "module_dependencies.md"],
        "source_type": "adapted_public_bug",
        "source_reference": "https://forums.developer.nvidia.com/t/rmmod-error-module-nvidia-is-in-use/61054"
    },
    {
        "id": "case_28_in_use_ext4",
        "module": "ext4",
        "category": "module already loaded/in use",
        "evidence": {
            "module": "ext4",
            "commands": {
                "uname": "5.15.0-89-generic",
                "lsmod": "Module                  Size  Used by\next4                  983040  2\n",
                "modinfo": "filename:       /lib/modules/5.15.0-89-generic/kernel/fs/ext4/ext4.ko\n",
                "dmesg": "",
                "journalctl": "root filesystem mounted as ext4",
                "modprobe_deps": "insmod /lib/modules/5.15.0-89-generic/kernel/fs/ext4/ext4.ko",
                "loaded_check": "ext4                  983040  2"
            },
            "errors": {
                "rmmod": "rmmod: ERROR: Module ext4 is in use"
            }
        },
        "gold_root_cause_category": "module already loaded/in use",
        "gold_keywords": ["in use", "used by", "mounted filesystem", "cannot unload", "rmmod"],
        "gold_doc_sources": ["kernel_modules.md", "module_loading.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_29_in_use_e1000e",
        "module": "e1000e",
        "category": "module already loaded/in use",
        "evidence": {
            "module": "e1000e",
            "commands": {
                "uname": "6.1.0-21-amd64",
                "lsmod": "Module                  Size  Used by\ne1000e                327680  0\n",
                "modinfo": "filename:       /lib/modules/6.1.0-21-amd64/kernel/drivers/net/ethernet/intel/e1000e/e1000e.ko\n",
                "dmesg": "[   14.001923] e1000e: eth0 NIC Link is Up 1000 Mbps Full Duplex",
                "journalctl": "systemd-networkd[420]: eth0 interface is active",
                "modprobe_deps": "insmod /lib/modules/6.1.0-21-amd64/kernel/drivers/net/ethernet/intel/e1000e/e1000e.ko",
                "loaded_check": "e1000e                327680  0"
            },
            "errors": {
                "rmmod": "rmmod: ERROR: Module e1000e is in use"
            }
        },
        "gold_root_cause_category": "module already loaded/in use",
        "gold_keywords": ["in use", "interface is active", "device in use", "ip link set down"],
        "gold_doc_sources": ["kernel_modules.md", "common_errors.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_30_in_use_drm",
        "module": "drm",
        "category": "module already loaded/in use",
        "evidence": {
            "module": "drm",
            "commands": {
                "uname": "6.8.0-40-generic",
                "lsmod": "Module                  Size  Used by\ndrm_kms_helper        249856  1 i915\ndrm                   614400  4 i915,drm_kms_helper\n",
                "modinfo": "filename:       /lib/modules/6.8.0-40-generic/kernel/drivers/gpu/drm/drm.ko\n",
                "dmesg": "",
                "journalctl": "gdm3[900]: Wayland display server active",
                "modprobe_deps": "insmod /lib/modules/6.8.0-40-generic/kernel/drivers/gpu/drm/drm.ko",
                "loaded_check": "drm                   614400  4"
            },
            "errors": {
                "rmmod": "rmmod: ERROR: Module drm is in use by: i915 drm_kms_helper"
            }
        },
        "gold_root_cause_category": "module already loaded/in use",
        "gold_keywords": ["in use by", "dependent modules", "i915", "drm_kms_helper", "unload dependent modules"],
        "gold_doc_sources": ["module_dependencies.md", "kernel_modules.md"],
        "source_type": "synthetic"
    },

    # 7. unknown symbol / ABI mismatch (5 cases)
    {
        "id": "case_31_abi_mismatch_vbox",
        "module": "vboxdrv",
        "category": "unknown symbol / ABI mismatch",
        "evidence": {
            "module": "vboxdrv",
            "commands": {
                "uname": "6.5.0-28-generic",
                "lsmod": "Module                  Size  Used by\n",
                "modinfo": "filename:       /lib/modules/6.5.0-28-generic/misc/vboxdrv.ko\nvermagic:       6.5.0-28-generic SMP preempt mod_unload \n",
                "dmesg": "[   41.102391] vboxdrv: Unknown symbol RTSpinlockCreate (err -2)\n[   41.102401] vboxdrv: Unknown symbol RTMemContAlloc (err -2)\n[   41.102410] vboxdrv: disagrees about version of symbol alloc_netdev_mqs",
                "journalctl": "systemd[1]: VirtualBox Linux kernel driver failed to load: Unknown symbol in module",
                "modprobe_deps": "insmod /lib/modules/6.5.0-28-generic/misc/vboxdrv.ko",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: ERROR: could not insert 'vboxdrv': Unknown symbol in module, or unknown parameter"
            }
        },
        "gold_root_cause_category": "unknown symbol / ABI mismatch",
        "gold_keywords": ["unknown symbol", "disagrees about version of symbol", "ABI mismatch", "recompile", "kernel headers"],
        "gold_doc_sources": ["module_loading.md", "common_errors.md"],
        "source_type": "adapted_public_bug",
        "source_reference": "https://www.virtualbox.org/ticket/21491"
    },
    {
        "id": "case_32_abi_mismatch_openafs",
        "module": "openafs",
        "category": "unknown symbol / ABI mismatch",
        "evidence": {
            "module": "openafs",
            "commands": {
                "uname": "5.15.0-105-generic",
                "lsmod": "Module                  Size  Used by\n",
                "modinfo": "filename:       /lib/modules/5.15.0-105-generic/updates/openafs.ko\n",
                "dmesg": "[   55.912014] openafs: disagrees about version of symbol vfs_read\n[   55.912025] openafs: Unknown symbol vfs_read (err -22)",
                "journalctl": "openafs-client: modprobe openafs failed with code 1",
                "modprobe_deps": "insmod /lib/modules/5.15.0-105-generic/updates/openafs.ko",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: ERROR: could not insert 'openafs': Unknown symbol in module"
            }
        },
        "gold_root_cause_category": "unknown symbol / ABI mismatch",
        "gold_keywords": ["unknown symbol", "disagrees about version", "ABI", "kernel version change"],
        "gold_doc_sources": ["module_loading.md", "common_errors.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_33_abi_mismatch_drbd",
        "module": "drbd",
        "category": "unknown symbol / ABI mismatch",
        "evidence": {
            "module": "drbd",
            "commands": {
                "uname": "6.1.0-18-amd64",
                "lsmod": "Module                  Size  Used by\n",
                "modinfo": "filename:       /lib/modules/6.1.0-18-amd64/extra/drbd.ko\n",
                "dmesg": "[   19.231901] drbd: Unknown symbol blk_cleanup_queue (err -2)\n[   19.231910] drbd: Unknown symbol bio_alloc_bioset (err -2)",
                "journalctl": "drbd.service: Job for drbd.service failed because of unknown kernel symbol",
                "modprobe_deps": "insmod /lib/modules/6.1.0-18-amd64/extra/drbd.ko",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: ERROR: could not insert 'drbd': Unknown symbol in module"
            }
        },
        "gold_root_cause_category": "unknown symbol / ABI mismatch",
        "gold_keywords": ["Unknown symbol", "ABI", "kernel API changed", "module_layout", "rebuild"],
        "gold_doc_sources": ["module_loading.md", "common_errors.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_34_abi_mismatch_tp_smapi",
        "module": "tp_smapi",
        "category": "unknown symbol / ABI mismatch",
        "evidence": {
            "module": "tp_smapi",
            "commands": {
                "uname": "6.6.0-14-generic",
                "lsmod": "Module                  Size  Used by\nthinkpad_ec            16384  0\n",
                "modinfo": "filename:       /lib/modules/6.6.0-14-generic/updates/dkms/tp_smapi.ko\n",
                "dmesg": "[   12.102391] tp_smapi: disagrees about version of symbol thinkpad_ec_try_lock",
                "journalctl": "tp-smapi: module insertion failed with symbol version mismatch",
                "modprobe_deps": "insmod /lib/modules/6.6.0-14-generic/updates/dkms/tp_smapi.ko",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: ERROR: could not insert 'tp_smapi': Exec format error"
            }
        },
        "gold_root_cause_category": "unknown symbol / ABI mismatch",
        "gold_keywords": ["symbol version mismatch", "disagrees about version of symbol", "ABI", "rebuild dkms"],
        "gold_doc_sources": ["module_loading.md", "common_errors.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_35_abi_mismatch_kheaders",
        "module": "kheaders",
        "category": "unknown symbol / ABI mismatch",
        "evidence": {
            "module": "kheaders",
            "commands": {
                "uname": "5.15.0-91-generic",
                "lsmod": "Module                  Size  Used by\n",
                "modinfo": "filename:       /lib/modules/5.15.0-91-generic/kernel/kernel/kheaders.ko\n",
                "dmesg": "[    4.412091] kheaders: disagrees about version of symbol sysfs_create_bin_file",
                "journalctl": "systemd[1]: Failed to insert kheaders: Exec format error",
                "modprobe_deps": "insmod /lib/modules/5.15.0-91-generic/kernel/kernel/kheaders.ko",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: ERROR: could not insert 'kheaders': Exec format error"
            }
        },
        "gold_root_cause_category": "unknown symbol / ABI mismatch",
        "gold_keywords": ["disagrees about version", "symbol", "ABI mismatch", "vermagic", "kernel"],
        "gold_doc_sources": ["module_loading.md", "common_errors.md"],
        "source_type": "synthetic"
    },

    # 8. DKMS build failure (4 cases)
    {
        "id": "case_36_dkms_nvidia_gcc_mismatch",
        "module": "nvidia",
        "category": "DKMS build failure",
        "evidence": {
            "module": "nvidia",
            "commands": {
                "uname": "6.8.0-40-generic",
                "lsmod": "Module                  Size  Used by\n",
                "modinfo": "modinfo: ERROR: Module nvidia not found.",
                "dmesg": "",
                "journalctl": "dkms[1420]: Error! The /var/lib/dkms/nvidia/535.183.01/build/make.log shows compilation failed.\ncompiler version check failed: kernel built with gcc-13, current CC is gcc-12",
                "modprobe_deps": "",
                "loaded_check": ""
            },
            "errors": {
                "dkms": "The /var/lib/dkms/nvidia/535.183.01/build/make.log shows build failure",
                "modprobe": "modprobe: FATAL: Module nvidia not found in directory /lib/modules/6.8.0-40-generic"
            }
        },
        "gold_root_cause_category": "DKMS build failure",
        "gold_keywords": ["DKMS", "make.log", "compiler version", "gcc", "build failed", "dkms autoinstall"],
        "gold_doc_sources": ["nvidia_troubleshooting.md", "module_loading.md"],
        "source_type": "adapted_public_bug",
        "source_reference": "https://bugs.launchpad.net/ubuntu/+source/nvidia-graphics-drivers/+bug/1968840"
    },
    {
        "id": "case_37_dkms_missing_kernel_headers",
        "module": "vboxguest",
        "category": "DKMS build failure",
        "evidence": {
            "module": "vboxguest",
            "commands": {
                "uname": "6.5.0-28-generic",
                "lsmod": "Module                  Size  Used by\n",
                "modinfo": "modinfo: ERROR: Module vboxguest not found.",
                "dmesg": "",
                "journalctl": "dkms[1105]: Error! Your kernel headers for kernel 6.5.0-28-generic cannot be found at /lib/modules/6.5.0-28-generic/build or /lib/modules/6.5.0-28-generic/source.",
                "modprobe_deps": "",
                "loaded_check": ""
            },
            "errors": {
                "dkms": "kernel headers not found",
                "modprobe": "modprobe: FATAL: Module vboxguest not found"
            }
        },
        "gold_root_cause_category": "DKMS build failure",
        "gold_keywords": ["kernel headers", "linux-headers", "dkms", "build", "/lib/modules", "source"],
        "gold_doc_sources": ["module_loading.md", "nvidia_troubleshooting.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_38_dkms_anbox_ashmem",
        "module": "ashmem_linux",
        "category": "DKMS build failure",
        "evidence": {
            "module": "ashmem_linux",
            "commands": {
                "uname": "5.19.0-38-generic",
                "lsmod": "Module                  Size  Used by\n",
                "modinfo": "modinfo: ERROR: Module ashmem_linux not found.",
                "dmesg": "",
                "journalctl": "dkms: ashmem-linux build failed with error: implicit declaration of function 'kmem_cache_create_usercopy'",
                "modprobe_deps": "",
                "loaded_check": ""
            },
            "errors": {
                "dkms": "dkms build failed: compilation error",
                "modprobe": "modprobe: FATAL: Module ashmem_linux not found"
            }
        },
        "gold_root_cause_category": "DKMS build failure",
        "gold_keywords": ["dkms", "build failed", "compilation error", "kernel headers", "patch"],
        "gold_doc_sources": ["module_loading.md", "common_errors.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_39_dkms_zfs_make_fail",
        "module": "zfs",
        "category": "DKMS build failure",
        "evidence": {
            "module": "zfs",
            "commands": {
                "uname": "6.8.0-31-generic",
                "lsmod": "Module                  Size  Used by\n",
                "modinfo": "modinfo: ERROR: Module zfs not found.",
                "dmesg": "",
                "journalctl": "dkms[1902]: Error! Bad return status for module build on kernel: 6.8.0-31-generic (x86_64)\nConsult /var/lib/dkms/zfs/2.1.5/build/make.log for more information.",
                "modprobe_deps": "",
                "loaded_check": ""
            },
            "errors": {
                "dkms": "Bad return status for module build on kernel: 6.8.0-31-generic",
                "modprobe": "modprobe: FATAL: Module zfs not found"
            }
        },
        "gold_root_cause_category": "DKMS build failure",
        "gold_keywords": ["dkms", "bad return status", "make.log", "module build", "kernel headers"],
        "gold_doc_sources": ["module_loading.md", "common_errors.md"],
        "source_type": "synthetic"
    },

    # 9. healthy module cases (4 cases) -> false positive check
    {
        "id": "case_40_healthy_loop",
        "module": "loop",
        "category": "healthy module",
        "evidence": {
            "module": "loop",
            "commands": {
                "uname": "6.8.0-40-generic",
                "lsmod": "Module                  Size  Used by\nloop                   36864  8\n",
                "modinfo": "filename:       /lib/modules/6.8.0-40-generic/kernel/drivers/block/loop.ko\nalias:          block-major-7-*\nlicense:        GPL\nvermagic:       6.8.0-40-generic SMP preempt mod_unload \n",
                "dmesg": "[    1.120911] loop: module loaded\n[    1.120920] loop0: detected 104857600 bytes",
                "journalctl": "kernel: loop: module loaded successfully",
                "modprobe_deps": "insmod /lib/modules/6.8.0-40-generic/kernel/drivers/block/loop.ko",
                "loaded_check": "loop                   36864  8"
            },
            "errors": {}
        },
        "gold_root_cause_category": "healthy module",
        "gold_keywords": ["healthy", "normal", "no fault found", "loaded and operating", "no action required"],
        "gold_doc_sources": ["kernel_modules.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_41_healthy_e1000e",
        "module": "e1000e",
        "category": "healthy module",
        "evidence": {
            "module": "e1000e",
            "commands": {
                "uname": "5.15.0-91-generic",
                "lsmod": "Module                  Size  Used by\ne1000e                327680  0\nptp                    32768  1 e1000e\n",
                "modinfo": "filename:       /lib/modules/5.15.0-91-generic/kernel/drivers/net/ethernet/intel/e1000e/e1000e.ko\nvermagic:       5.15.0-91-generic SMP mod_unload \ndepends:        ptp\n",
                "dmesg": "[    3.102391] e1000e: Intel(R) PRO/1000 Network Driver\n[    3.102401] e1000e 0000:00:1f.6 eth0: (PCI Express:2.5GT/s:Width x1) 00:15:5d:01:02:03",
                "journalctl": "systemd-networkd: eth0: Link UP",
                "modprobe_deps": "insmod /lib/modules/5.15.0-91-generic/kernel/drivers/ptp/ptp.ko\ninsmod /lib/modules/5.15.0-91-generic/kernel/drivers/net/ethernet/intel/e1000e/e1000e.ko",
                "loaded_check": "e1000e                327680  0"
            },
            "errors": {}
        },
        "gold_root_cause_category": "healthy module",
        "gold_keywords": ["healthy", "normal", "no error", "operating normally", "no fault found"],
        "gold_doc_sources": ["kernel_modules.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_42_healthy_nvidia",
        "module": "nvidia",
        "category": "healthy module",
        "evidence": {
            "module": "nvidia",
            "commands": {
                "uname": "6.5.0-28-generic",
                "lsmod": "Module                  Size  Used by\nnvidia_uvm            3489792  0\nnvidia_modeset        1556480  0\nnvidia               56623104  2 nvidia_modeset,nvidia_uvm\n",
                "modinfo": "filename:       /lib/modules/6.5.0-28-generic/updates/dkms/nvidia.ko\nversion:        550.54.14\nvermagic:       6.5.0-28-generic SMP preempt mod_unload \ndepends:        \n",
                "dmesg": "[   14.412091] nvidia: loading out-of-tree module taints kernel.\n[   14.412104] nvidia: module license 'NVIDIA' taints kernel.\n[   14.500112] NVRM: loading NVIDIA UNIX x86_64 Kernel Module  550.54.14",
                "journalctl": "systemd[1]: Started NVIDIA Persistence Daemon.",
                "modprobe_deps": "insmod /lib/modules/6.5.0-28-generic/updates/dkms/nvidia.ko",
                "loaded_check": "nvidia               56623104  2"
            },
            "errors": {}
        },
        "gold_root_cause_category": "healthy module",
        "gold_keywords": ["healthy", "loaded", "functioning", "no fault found", "normal"],
        "gold_doc_sources": ["nvidia_troubleshooting.md", "kernel_modules.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_43_healthy_wireguard",
        "module": "wireguard",
        "category": "healthy module",
        "evidence": {
            "module": "wireguard",
            "commands": {
                "uname": "6.8.0-40-generic",
                "lsmod": "Module                  Size  Used by\nwireguard             114688  0\nip6_udp_tunnel         16384  1 wireguard\nudp_tunnel             24576  1 wireguard\n",
                "modinfo": "filename:       /lib/modules/6.8.0-40-generic/kernel/net/wireguard/wireguard.ko\nvermagic:       6.8.0-40-generic SMP preempt mod_unload \ndepends:        ip6_udp_tunnel,udp_tunnel\n",
                "dmesg": "[    8.981023] wireguard: WireGuard 1.0.0 loaded. See www.wireguard.com for information.",
                "journalctl": "systemd[1]: Started WireGuard Tunnel.",
                "modprobe_deps": "insmod /lib/modules/6.8.0-40-generic/kernel/net/wireguard/wireguard.ko",
                "loaded_check": "wireguard             114688  0"
            },
            "errors": {}
        },
        "gold_root_cause_category": "healthy module",
        "gold_keywords": ["healthy", "normal", "operating properly", "no fault found"],
        "gold_doc_sources": ["kernel_modules.md"],
        "source_type": "synthetic"
    },

    # 10. noisy/irrelevant logs (3 cases)
    {
        "id": "case_44_noisy_audio_log_during_network_probe",
        "module": "r8169",
        "category": "missing firmware",
        "evidence": {
            "module": "r8169",
            "commands": {
                "uname": "6.1.0-21-amd64",
                "lsmod": "Module                  Size  Used by\nrealtek                32768  0\n",
                "modinfo": "filename:       /lib/modules/6.1.0-21-amd64/kernel/drivers/net/ethernet/realtek/r8169.ko\nfirmware:       rtl_nic/rtl8168h-2.fw\n",
                "dmesg": "[   12.001923] snd_hda_intel 0000:00:1f.3: CORB reset timeout#1, CORBRP = 0\n[   12.001930] usb 1-1: reset high-speed USB device number 2 using xhci_hcd\n[   12.002010] EXT4-fs (sda1): re-mounted. Opts: errors=remount-ro\n[   12.102391] r8169 0000:02:00.0: Direct firmware load for rtl_nic/rtl8168h-2.fw failed with error -2\n[   12.102401] thermal thermal_zone0: critical temperature reaching 98C",
                "journalctl": "pulseaudio: sink input dropped\nkernel: r8169: Direct firmware load for rtl_nic/rtl8168h-2.fw failed with error -2",
                "modprobe_deps": "insmod /lib/modules/6.1.0-21-amd64/kernel/drivers/net/ethernet/realtek/r8169.ko",
                "loaded_check": "r8169                  98304  0"
            },
            "errors": {
                "dmesg": "Direct firmware load for rtl_nic/rtl8168h-2.fw failed with error -2"
            }
        },
        "gold_root_cause_category": "missing firmware",
        "gold_keywords": ["firmware", "rtl_nic/rtl8168h-2.fw", "error -2", "linux-firmware"],
        "gold_doc_sources": ["common_errors.md", "kernel_modules.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_45_noisy_disk_warning_during_vermagic_fail",
        "module": "nvidia",
        "category": "vermagic/kernel version mismatch",
        "evidence": {
            "module": "nvidia",
            "commands": {
                "uname": "6.8.0-40-generic",
                "lsmod": "Module                  Size  Used by\n",
                "modinfo": "filename:       /lib/modules/6.5.0-28-generic/updates/dkms/nvidia.ko\nvermagic:       6.5.0-28-generic SMP preempt mod_unload \n",
                "dmesg": "[  100.120911] ata1.00: exception Emask 0x0 SAct 0x0 SErr 0x0 action 0x0\n[  100.120920] ata1.00: failed command: READ DMA\n[  100.201991] nvidia: version magic '6.5.0-28-generic' should be '6.8.0-40-generic'\n[  100.202010] systemd[1]: cron.service: Succeeded.",
                "journalctl": "smartd[412]: Device /dev/sda is experiencing high read retry rate",
                "modprobe_deps": "insmod /lib/modules/6.5.0-28-generic/updates/dkms/nvidia.ko",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: ERROR: could not insert 'nvidia': Exec format error"
            }
        },
        "gold_root_cause_category": "vermagic/kernel version mismatch",
        "gold_keywords": ["vermagic", "version magic", "6.5.0-28-generic", "6.8.0-40-generic", "rebuild dkms"],
        "gold_doc_sources": ["module_loading.md", "nvidia_troubleshooting.md"],
        "source_type": "synthetic"
    },
    {
        "id": "case_46_noisy_bluetooth_spam_during_missing_dep",
        "module": "nft_compat",
        "category": "missing dependency",
        "evidence": {
            "module": "nft_compat",
            "commands": {
                "uname": "6.1.0-21-amd64",
                "lsmod": "Module                  Size  Used by\n",
                "modinfo": "filename:       /lib/modules/6.1.0-21-amd64/kernel/net/netfilter/nft_compat.ko\ndepends:        nf_tables,x_tables\n",
                "dmesg": "[   50.102391] Bluetooth: hci0: unexpected event 0x3e\n[   50.102401] nft_compat: Unknown symbol nf_tables_valid_genid (err -2)\n[   50.102410] Bluetooth: hci0: link disconnected with status 19",
                "journalctl": "bluetoothd[501]: Endpoint registered: /org/bluez/hci0/A2DP/SBC/Source",
                "modprobe_deps": "insmod /lib/modules/6.1.0-21-amd64/kernel/net/netfilter/nft_compat.ko",
                "loaded_check": ""
            },
            "errors": {
                "modprobe": "modprobe: ERROR: could not insert 'nft_compat': Unknown symbol in module"
            }
        },
        "gold_root_cause_category": "missing dependency",
        "gold_keywords": ["dependency", "nf_tables", "unknown symbol", "depends"],
        "gold_doc_sources": ["module_dependencies.md", "modprobe.md"],
        "source_type": "synthetic"
    }
]

def main():
    target_dir = os.path.join(os.path.dirname(__file__), "cases")
    os.makedirs(target_dir, exist_ok=True)
    for c in CASES:
        path = os.path.join(target_dir, f"{c['id']}.json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(c, f, indent=2)
    print(f"Generated {len(CASES)} benchmark cases in {target_dir}")

if __name__ == "__main__":
    main()
