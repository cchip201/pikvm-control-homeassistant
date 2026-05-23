# PiKVM Custom Controls for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)
[![HA_Version](https://img.shields.io/badge/Home%20Assistant-2026.3+-blue.svg?style=for-the-badge)](https://github.com/home-assistant/core)
[![Release](https://img.shields.io/github/v/release/cchip201/pikvm-control-homeassistant?style=for-the-badge)](https://github.com/cchip201/pikvm-control-homeassistant/releases)

A fully polished, advanced Home Assistant integration to monitor and control **PiKVM V3/V4** hardware ATX states, running services, temperature, fan speed, and diagnostics.

---

## Features

### 🔌 Physical ATX Control & Buttons
Trigger real-time physical button presses on your target computer:
*   **Power Button Click**: Performs a standard momentary power button press.
*   **Reset Button Click**: Performs a standard momentary reset button press.
*   **Advanced Power Actions**: Execute persistent states such as `On`, `Off` (Graceful), `Hard Off` (Force power-down), and `Hard Reset`.

### 📊 Advanced Diagnostics (New in v2.0.0)
Real-time telemetry and hardware monitoring from the PiKVM KVMD API:
*   **CPU Temperature**: Keep track of the PiKVM SOC thermal profile in degrees Celsius.
*   **Fan Speed**: Dynamic rotation speed monitoring (RPM) to maintain hardware health.
*   **System Uptime & Boot Time**: Calculate precise host boot timestamps and uptime duration.
*   **KVMD Version**: Display the current running version of the PiKVM daemon.

### 🛡️ Services & Throttling Status
Track sub-services and physical server states:
*   **Under-voltage / Throttling Alert**: Alert when the PiKVM hardware experiences throttling due to voltage drop or thermals.
*   **IPMI Service**: Check whether the IPMI interface is active.
*   **Janus WebRTC Service**: Monitor the streaming gateway state.
*   **VNC Service**: Monitor target desktop remote session availability.
*   **Webterm Service**: Check if the embedded terminal shell service is online.
*   **Power & HDD LEDs**: Visual indicators mirror the target system's physical front-panel LEDs.

---

## Installation

### Method 1: HACS (Recommended)
1. Go to **HACS** > **Integrations** in your Home Assistant sidebar.
2. Click the **three dots** in the top-right corner and select **Custom repositories**.
3. Add the repository URL:
   ```text
   https://github.com/cchip201/pikvm-control-homeassistant
   ```
4. Select Category **Integration** and click **Add**.
5. Find **PiKVM Custom Controls** in the store, click **Download**, and restart Home Assistant.

### Method 2: Manual Installation
1. Download the latest release from the [Releases](https://github.com/cchip201/pikvm-control-homeassistant/releases) page.
2. Extract and copy the `custom_components/pikvm_custom/` directory into your Home Assistant `<config_dir>/custom_components/` folder.
3. Restart Home Assistant.

---

## Configuration

1. In Home Assistant, navigate to **Settings** > **Devices & Services**.
2. Click **+ Add Integration** in the bottom-right corner.
3. Search for and select **PiKVM Custom Controls**.
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
| **Click Power Button** | Momentary Click | Simulates pressing the physical ATX power button |
| **Click Reset Button** | Momentary Click | Simulates pressing the physical ATX reset button |

---

## Diagnostics & Troubleshooting

This integration includes support for Home Assistant local brand asset rendering (introduced in **2026.3**). Brand assets like the integration logo and icon are stored locally under the `brand/` directory inside the custom component, prioritizing local asset loading over GitHub or standard brand API proxy calls.

If you encounter issues with device connections:
1. Ensure your PiKVM is reachable on the local network.
2. Confirm your KVMD HTTPS API configuration uses Basic Authentication.
3. Check the Home Assistant logs (`homeassistant.log`) for any debug output under the `custom_components.pikvm_custom` namespace.
