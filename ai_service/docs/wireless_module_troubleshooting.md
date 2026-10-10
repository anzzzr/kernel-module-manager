---
title: Wireless Network Driver Troubleshooting
category: networking
source_url: https://wireless.wiki.kernel.org/
---

# Wireless Network Driver Troubleshooting

## Common Wireless Driver Modules
Linux Wi-Fi drivers (e.g. `iwlwifi`, `ath10k_pci`, `mt7921e`, `rtw88`) depend on the core `cfg80211` and `mac80211` subsystems.

## Frequent Causes of Failure
1. **Missing Firmware**: Modern Wi-Fi chips require `.ucode` or `.bin` files from `linux-firmware`. Look for `Direct firmware load failed with error -2` in `dmesg`.
2. **RF-Kill Soft/Hard Blocking**: Radio transmitters disabled by hardware switch. Check with `rfkill list`.
3. **Regulatory Domain**: Incompatible wireless domain settings in `cfg80211`.
