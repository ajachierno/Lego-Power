# LEGO Power

Control **LEGO® Powered Up** motors directly over Bluetooth from Home Assistant.

Each hub becomes a device with:

- a **Motor** switch (on = run, off = stop),
- a **Speed** control (live 1–100%; default 50%),
- a **Connection** switch (connect / disconnect), and
- a **Connected** status sensor.

Supports multiple hubs, auto‑reconnect, and per‑device motor port / direction /
stop‑behaviour options. Works with a local Bluetooth adapter or an ESPHome
Bluetooth proxy.

> **Tested only on the LEGO Piano (21323).** Running the motor at full speed will
> skip the piano gears — keep the Speed near the default 50%.

See the [README](https://github.com/ajachierno/Lego-Power) for setup details.
