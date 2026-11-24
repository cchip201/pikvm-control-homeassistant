# PiKVM Control Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![HA_Version](https://img.shields.io/badge/Home%20Assistant-2026.3+-blue.svg?style=for-the-badge)](https://github.com/home-assistant/core)
[![Release](https://img.shields.io/github/v/release/cchip201/pikvm-control-homeassistant?style=for-the-badge)](https://github.com/cchip201/pikvm-control-homeassistant/releases)

A Home Assistant integration to monitor and control **PiKVM V3/V4** hardware ATX states, running services, temperature, fan speed, and diagnostics.

---

## Features

### 🔌 Physical ATX Control & Buttons
Trigger physical ATX actions on your target computer:
*   **Power Click**: Simulates a momentary ATX power button press.
*   **Reset Click**: Simulates a momentary ATX reset button press.
*   **Power Long Press (Hard Off)**: Executes an immediate forced ATX power-off (`off_hard`).

### 📊 Diagnostics & Telemetry
Real-time telemetry and hardware monitoring from the PiKVM KVMD API:
*   **CPU Temperature**: Reports the PiKVM SoC temperature in degrees Celsius.
*   **Fan Speed**: Reports cooling fan rotation speed (RPM).
*   **Boot Time**: Calculates the host boot timestamp from KVMD uptime telemetry.
*   **KVMD Version**: Displays the running version of the PiKVM daemon.

### 🛡️ Services & Throttling Status
Track sub-services and physical server states:
*   **Under-voltage / Throttling Alert**: Alerts when the PiKVM hardware experiences throttling due to voltage drop or thermals.
*   **IPMI Service**: Checks whether the IPMI interface is active.
*   **Janus WebRTC Service**: Monitors the streaming gateway state.
*   **VNC Service**: Monitors target desktop remote session availability.
*   **Webterm Service**: Checks if the embedded terminal shell service is online.
*   **Power & HDD LEDs**: Mirrors the target system's physical front-panel Power and HDD LEDs.

---

## Installation

### Method 1: HACS (Recommended)
1. Open **HACS** (or **Marketplace** in Home Assistant 2026.11+) in your Home Assistant sidebar.
2. Search for **PiKVM Control Home Assistant**, click **Download**, and restart Home Assistant.
   * *Alternative (Custom Repository)*: Click the **three dots** in the top-right corner of HACS → **Custom repositories** → add `https://github.com/cchip201/pikvm-control-homeassistant` with category **Integration** → click **Add**, then download and restart Home Assistant.

### Method 2: Manual Installation
1. Download the latest release from the [Releases](https://github.com/cchip201/pikvm-control-homeassistant/releases) page.
2. Extract and copy the `custom_components/pikvm_custom/` directory into your Home Assistant `<config_dir>/custom_components/` folder.
3. Restart Home Assistant.

---

## Configuration

1. In Home Assistant, navigate to **Settings** > **Devices & Services**.
2. Click **+ Add Integration** in the bottom-right corner.
3. Search for and select **PiKVM Control Home Assistant**.
4. Fill in the connection form:
   *   **Host**: IP address or hostname of your PiKVM device (e.g., `192.168.1.150` or `pikvm.local`).
   *   **Username**: Your KVMD web interface username (default: `admin`).
   *   **Password**: Your KVMD web interface password.
5. Click **Submit** to finalize the setup.

---

## Exposed Entities

### Sensors (`sensor.py`)
| Entity Name | Device Class | State Class | Unit | Icon |
| :--- | :--- | :--- | :--- | :--- |
| **CPU Temperature** | `temperature` | `measurement` | °C | `mdi:thermometer` |
| **Fan Speed** | — | `measurement` | RPM | `mdi:fan` |
| **Boot Time** | `timestamp` | — | UTC | `mdi:clock-start` |
| **KVMD Version** | — | — | — | `mdi:information-outline` |

### Binary Sensors (`binary_sensor.py`)
| Entity Name | Device Class | Icon | Description |
| :--- | :--- | :--- | :--- |
| **Power LED** | `power` | — | Reflects target system Power LED state |
| **HDD LED** | `running` | — | Reflects target system Disk Activity LED state |
| **Throttling Alert** | `problem` | — | Turns ON if PiKVM hardware experiences under-voltage/throttling |
| **IPMI Service** | `running` | `mdi:server` | Monitors active IPMI service state |
| **Janus WebRTC Service** | `running` | `mdi:webrtc` | Monitors active WebRTC streams |
| **VNC Service** | `running` | `mdi:screencast` | Monitors active VNC server daemon |
| **Webterm Service** | `running` | `mdi:console-line` | Monitors web terminal interface |

### Buttons (`button.py`)
| Button Name | Action | Description |
| :--- | :--- | :--- |
| **Power Click** | Momentary Click (`power`) | Simulates pressing the physical ATX power button |
| **Reset Click** | Momentary Click (`reset`) | Simulates pressing the physical ATX reset button |
| **Power Long Press (Hard Off)** | ATX Power Action (`off_hard`) | Forces an immediate ATX power-off on the target computer |

---

## Diagnostics & Troubleshooting

This integration includes support for Home Assistant local brand asset rendering (introduced in **2026.3**). Brand assets are stored locally under `custom_components/pikvm_custom/brand/`.

If you encounter issues with device connections:
1. Ensure your PiKVM is reachable on the local network.
2. Confirm your KVMD HTTPS API configuration uses Basic Authentication.
3. Check the Home Assistant logs (`homeassistant.log`) for any debug output under the `custom_components.pikvm_custom` namespace.
