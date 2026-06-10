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

> [!WARNING]
> **Tested only on the LEGO® Piano (21323).** Other Powered Up hubs and motors
> should work, but are unverified. **Do not run the piano motor at full speed —
> the gears will skip.** The default speed is a safe **50 %**; raise it carefully.

## Features

- 🎛️ **Motor switch** — turn on to run the motor, off to stop it.
- 🔌 **Connection switch** — connect or disconnect the hub from Home Assistant.
- 🏎️ **Speed control** — a live slider (1–100%); defaults to a gear-safe 50%.
- 📶 **Connected** binary sensor — shows the live Bluetooth connection status.
- ➕ **Multiple devices** — add as many hubs as you like, one config entry each.
- 🔁 **Auto‑reconnect** — re‑establishes the link when the hub comes back in range.
- 🎚️ **Live device controls** — motor port, direction (Reverse toggle) and
  stop behaviour (Brake toggle) are adjustable right on the device page, no
  reconfigure dialog needed.

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

That's the only setup question. Everything else is a **live control on the device page** (and remembers its value across restarts):

| Entity | What it does |
| --- | --- |
| **Motor** (switch) | Run / stop the motor. |
| **Speed** (number) | Run speed, 1–100 %. Defaults to a gear‑safe **50 %**. |
| **Reverse** (switch) | Off = forward, on = reverse direction. |
| **Brake on stop** (switch) | Off = float/coast, on = brake/hold when stopped. |
| **Motor port** (number) | Hub port the motor is on (**A=0, B=1, C=2, D=3**). |
| **Connection** (switch) | Connect / disconnect the hub. |
| **Connected** (binary sensor) | Live Bluetooth connection status. |

> [!CAUTION]
> Full speed (100 %) will skip the LEGO Piano (21323) gears. Keep the Speed at or near the default 50 % for that set.

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

## Submitting to HACS

The repo is structured for the
[HACS integration requirements](https://www.hacs.xyz/docs/publish/integration/):
`custom_components/lego_power/` with a `manifest.json` (incl. `version`,
`documentation`, `issue_tracker`, `codeowners`) and a config flow, a root
`hacs.json`, a README, and a `Validate` workflow running **hassfest** + the
**HACS action**.

To get listed in the **default HACS store**, in order:

1. **Repo settings** (GitHub → repo home): add a **Description**, add **Topics**
   (e.g. `home-assistant`, `hacs`, `homeassistant-integration`, `lego`,
   `bluetooth`, `esphome`), and make sure **Issues** are enabled and the repo is
   **public** and not archived.
2. **Publish a Release**: GitHub → Releases → *Draft a new release* → choose the
   existing tag **`v1.2.0`** → publish. HACS installs from the latest release.
3. **Brand assets** — open a PR to
   [home-assistant/brands](https://github.com/home-assistant/brands) adding the
   integration's `lego_power` domain. Copy the images from this repo's `brands/`
   folder to:
   `custom_integrations/lego_power/icon.png` (256×256),
   `custom_integrations/lego_power/icon@2x.png` (512×512),
   `custom_integrations/lego_power/logo.png`,
   `custom_integrations/lego_power/logo@2x.png`.
   This must be merged **before** the HACS default PR will pass.
4. **Check CI**: confirm the **Validate** workflow (Actions tab) is green. The
   HACS `brands` check only passes once step 3 is merged.
5. **Default-store PR**: fork [hacs/default](https://github.com/hacs/default),
   add `ajachierno/Lego-Power` to the `integration` list (alphabetical), and open
   a PR. A maintainer/bot reviews it.

Custom-repository installs work today without any of the above.

## License

[MIT](LICENSE)

## Buy me a coffee

Did you find this helpful? Consider buying me a coffee to support additional development: [buymeacoffee](https://buymeacoffee.com/ajachiernoo)
