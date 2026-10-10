---
title: ALSA Sound Card Drivers and snd Modules
category: multimedia
source_url: https://www.alsa-project.org/wiki/Main_Page
---

# ALSA Sound Card Drivers and snd Modules

## Audio Module Stack
The Advanced Linux Sound Architecture (ALSA) loads base drivers (`snd`, `snd_pcm`, `snd_timer`) alongside vendor drivers (`snd_hda_intel`, `snd_soc_core`).

## Sound Conflicts and Blacklisting
Internal PC beeper devices (`pcspkr`, `snd_pcsp`) are commonly blacklisted by distributions in `/etc/modprobe.d/alsa-base-blacklist.conf` to avoid console audio conflicts.
Attempting to load blacklisted audio modules will produce `Module is blacklisted`.
