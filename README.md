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

## Documentation

Please refer to the [docs](/docs) for more info.

---

<div align="center">
  <p>
    <img src="https://img.shields.io/badge/Developed_by-UWO--FAST--et--al-orange" alt="Developed by UWO-FAST et al.">
    <img src="https://img.shields.io/badge/Powered_by-Open_Source-blue" alt="Powered by Open Source">
  </p>
</div>