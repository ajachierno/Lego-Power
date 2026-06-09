# LEGO Power

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Validate](https://github.com/ajachierno/Lego-Power/actions/workflows/validate.yml/badge.svg)](https://github.com/ajachierno/Lego-Power/actions/workflows/validate.yml)

A Home Assistant integration that controls **LEGO® Powered Up** motors directly
over Bluetooth Low Energy, using the
[LEGO Wireless Protocol v3](https://lego.github.io/lego-ble-wireless-protocol-docs/).

Each LEGO hub becomes a proper Home Assistant **device** with controllable
entities, so you can run and stop motors from the UI, dashboards, scripts and
automations — no helper scripts or button presses required. The integration
supports **multiple hubs**, each added as its own device.

> LEGO® is a trademark of the LEGO Group, which does not sponsor, authorise or
> endorse this project.

## Features

- 🎛️ **Motor switch** — turn on to run the motor, off to stop it.
- 🔌 **Connection switch** — connect or disconnect the hub from Home Assistant.
- 📶 **Connected** binary sensor — shows the live Bluetooth connection status.
- ➕ **Multiple devices** — add as many hubs as you like, one config entry each.
- 🔁 **Auto‑reconnect** — re‑establishes the link when the hub comes back in range.
- ⚙️ **Per‑device options** — motor port, run power, direction and stop behaviour.

## How it works

LEGO Powered Up hubs (City Hub 88009, Technic Hub 88012, Boost Move Hub 88006,
etc.) expose a single BLE service (`00001623-…`) with one characteristic
(`00001624-…`). This integration sends *Port Output Commands*
(`WriteDirectModeData`, direct power mode) to start and stop the motor on the
configured port.

Home Assistant's Bluetooth stack provides the radio. If your Home Assistant host
has no Bluetooth, or the hub is out of range, an
[ESPHome Bluetooth Proxy](https://esphome.io/projects/?type=bluetooth) (such as
an ESP32) will transparently relay the connection — no extra configuration in
this integration is needed.

## Requirements

- Home Assistant **2024.12.0** or newer.
- The [Bluetooth integration](https://www.home-assistant.io/integrations/bluetooth/)
  configured (a local adapter or an ESPHome Bluetooth proxy in range of the hub).

## Installation

### HACS (recommended)

1. In HACS, open the three‑dot menu → **Custom repositories**.
2. Add `https://github.com/ajachierno/Lego-Power` with category **Integration**.
3. Search for **LEGO Power**, install it, and restart Home Assistant.

### Manual

Copy `custom_components/lego_power` into your Home Assistant `config/custom_components`
directory and restart.

## Setup

A powered‑on hub in range is usually **discovered automatically** — look for a
"LEGO Power" notification under *Settings → Devices & Services*.

To add one manually: **Settings → Devices & Services → Add Integration →
LEGO Power**, pick the hub, then set:

| Option | Description |
| --- | --- |
| **Name** | Friendly name for the device (e.g. `Piano`). |
| **Motor port** | Hub port the motor is plugged into. External ports are **A=0, B=1, C=2, D=3**. |
| **Run power** | Power (1–100 %) applied when the motor switch is turned on. |
| **Direction** | Forward or reverse. |
| **Stop behaviour** | *Float* (coast) or *Brake* (actively hold). |

These can be changed later via the device's **Configure** button.

> **Note:** A LEGO hub only allows one Bluetooth connection at a time. If you
> were previously controlling the hub from custom ESPHome firmware, disable that
> connection first so this integration can connect.

## Replacing the old play/stop automations

If you came here from automations that pressed `button.*_play` / `button.*_stop`,
replace those actions with the motor switch, e.g.:

```yaml
# Old
- action: button.press
  target:
    entity_id: button.lego_piano_controller_play

# New
- action: switch.turn_on
  target:
    entity_id: switch.piano_motor
```

## Submitting to HACS (for the maintainer)

This repo is already structured for the
[HACS integration requirements](https://www.hacs.xyz/docs/publish/integration/):

- `custom_components/lego_power/` with `manifest.json` (incl. `version`) and a
  config flow.
- `hacs.json` in the repo root.
- A `validate.yml` workflow running **hassfest** and the **HACS action**.

Remaining steps before requesting inclusion in the default HACS store:

1. **Publish a GitHub release** (e.g. `v1.0.0`) — HACS installs the latest tag.
2. **Add brand assets** to [home-assistant/brands](https://github.com/home-assistant/brands):
   create `custom_integrations/lego_power/icon.png` (256×256) and `logo.png`.
   Ready‑to‑use images are provided in the `brands/` folder of this repo.
3. Make the repository **public** and not archived, with a description and topics.
4. Open an inclusion PR at
   [hacs/default](https://github.com/hacs/default) (optional — custom
   repositories work without this).

## License

[MIT](LICENSE)

## Buy me a coffee

Did you find this helpful? Consider buying me a coffee to support additional development: [buymeacoffee](https://buymeacoffee.com/ajachiernoo)
