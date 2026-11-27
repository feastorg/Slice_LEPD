# Photometer Slice

Photometer using LED and photodiode slice for BREAD.

## Introduction

[Short introduction on the project.]

## Usage

[Explain how to use the project. Include examples and screenshots if applicable.]

### Photodiode connectors (J6, J7)

| Pin | Photodiode | Goes to |
| --- | --- | --- |
| 1 | anode (A) | TIA bias, 49 mV (R38 / R40) |
| 2 | cathode (K) | TIA summing node (R37 / R39) |

Wired this way, light raises the TIA output from 49 mV by 1.5 V per µA of
photocurrent; A0 (J6) and A1 (J7) reach 5 V at about 3.3 µA. A photodiode
fitted the other way round drives the output to the bottom rail (about 12 mV).

### LED outputs (J2-J5)

Each channel sinks up to 1.000 V / 12.4 Ω = 80.6 mA at 100 % duty (81.7 mA with R9's 13 mV of
comparator hysteresis). The INL-5AMIR15's absolute maximum is 100 mA DC at 25 °C (Pd 160 mW),
derated linearly above about 30 °C ambient: about 83 mA at 40 °C and 51 mA at 60 °C (datasheet
V1.0, page 3). Its typical forward-voltage curve gives about 2.15 V at 80 mA, so the sink keeps
about 1.8 V across Q2 at full scale.

## Documentation

Please refer to the [docs](/docs) for more info.

---

<div align="center">
  <p>
    <img src="https://img.shields.io/badge/Developed_by-UWO--FAST--et--al-orange" alt="Developed by UWO-FAST et al.">
    <img src="https://img.shields.io/badge/Powered_by-Open_Source-blue" alt="Powered by Open Source">
  </p>
</div>