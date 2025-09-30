# File: main.py
# Final version with a Python class to control the checkbox color change.

import requests
import json
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.scrollview import ScrollView
from kivy.uix.checkbox import CheckBox  # <-- ADD THIS IMPORT
from kivy.properties import ColorProperty  # <-- ADD THIS IMPORT

# --- IMPORTANT: CONFIGURE THESE VALUES ---
# The base URL from your Azure App Service
BASE_URL = "https://iotoct2-c8g7gjbdhec2b6h9.northeurope-01.azurewebsites.net"
# The API key you set in your backend's environment variables
API_KEY = "987654321"
# The device ID to query telemetry data for (can be changed in the UI)
DEFAULT_TELEMETRY_DEVICE_ID = "Raspberry Pi Web Client"
# The device ID to send commands to (fixed for the POST request)
COMMAND_DEVICE_ID = "SimDevice01"
# -----------------------------------------


# 1. NEW PYTHON CLASS FOR THE CHECKBOX
# This class contains the logic to change the inner circle's color.
class DeviceCheckBox(CheckBox):
    # A Kivy property to store the color of the inner circle
    inner_circle_color = ColorProperty([0, 0, 0, 0])  # Default is transparent

    def on_active(self, instance, value):
        """This function is called automatically by Kivy when the 'active' state changes."""
        if value:
            # If the checkbox is now active, make the inner circle blue and opaque.
            self.inner_circle_color = [0.3, 0.6, 1, 1]
        else:
            # If the checkbox is now inactive, make it fully transparent.
            self.inner_circle_color = [0.3, 0.6, 1, 0]


class IotApp(App):
    def build(self):
        self.title = 'IoT Dashboard'
        self.telemetry_device_id = DEFAULT_TELEMETRY_DEVICE_ID
        return Builder.load_file('iotapp.kv')

    def on_start(self):
        pass

    def set_telemetry_device_id(self, device_id):
        if device_id and device_id.strip():
            self.telemetry_device_id = device_id.strip()
            self.root.ids.results_label.text = f"Telemetry Device ID set to:\n{self.telemetry_device_id}"
        else:
            self.root.ids.results_label.text = "[color=ff0000]Error: Device ID cannot be empty.[/color]"

    def _fetch_and_sort_telemetry(self):
        try:
            url = f"{BASE_URL}/telemetry"
            params = {'deviceId': self.telemetry_device_id}
            headers = {'x-api-key': API_KEY}
            response = requests.get(
                url, params=params, headers=headers, timeout=10)
            response.raise_for_status()
            entities = response.json()
            sorted_entities = sorted(
                entities, key=lambda e: e.get('timestamp', ''), reverse=True)
            return sorted_entities
        except requests.exceptions.RequestException as e:
            self.root.ids.results_label.text = f"[color=ff0000]Connection Error:\n{e}[/color]"
            return None
        except Exception as e:
            self.root.ids.results_label.text = f"[color=ff0000]An error occurred:\n{e}[/color]"
            return None

    def get_latest_reading(self):
        self.root.ids.results_label.text = "Fetching latest reading..."
        sorted_entities = self._fetch_and_sort_telemetry()
        if sorted_entities:
            latest = sorted_entities[0]
            display_text = "[color=00ff00]--- Latest Reading ---\n"
            for key, value in latest.items():
                if key not in ["PartitionKey", "RowKey", "etag"]:
                    display_text += f"{key.capitalize()}: {value}\n"
            display_text += "[/color]"
            self.root.ids.results_label.text = display_text
        elif sorted_entities is not None:
            self.root.ids.results_label.text = "No data found for this device."

    def get_last_3_readings(self):
        self.root.ids.results_label.text = "Fetching last 3 readings..."
        sorted_entities = self._fetch_and_sort_telemetry()
        if sorted_entities:
            last_three = sorted_entities[:3]
            display_text = "[color=00ff00]--- Last 3 Readings ---\n\n"
            for i, entity in enumerate(last_three):
                display_text += f"Reading #{i+1}\n"
                for key, value in entity.items():
                    if key not in ["PartitionKey", "RowKey", "etag"]:
                        display_text += f"  {key.capitalize()}: {value}\n"
                display_text += "---\n"
            display_text += "[/color]"
            self.root.ids.results_label.text = display_text
        elif sorted_entities is not None:
            self.root.ids.results_label.text = "No data found for this device."

    def send_command(self, state):
        self.root.ids.results_label.text = f"Sending '{state.upper()}' command..."
        try:
            url = f"{BASE_URL}/command/{COMMAND_DEVICE_ID}"
            headers = {'x-api-key': API_KEY,
                       'Content-Type': 'application/json'}
            body = {"commandName": "toggle", "payload": {
                "activatedBy": "KivyApp", "state": state}}
            response = requests.post(
                url, headers=headers, data=json.dumps(body), timeout=10)
            response.raise_for_status()

            response_data = response.json()
            display_text = "[color=00ff00]Command Sent Successfully!\n--- Response ---\n"
            for key, value in response_data.items():
                display_text += f"{key.capitalize()}: {value}\n"
            display_text += "[/color]"
            self.root.ids.results_label.text = display_text

        except requests.exceptions.RequestException as e:
            self.root.ids.results_label.text = f"[color=ff0000]Command Error:\n{e}[/color]"
        except Exception as e:
            self.root.ids.results_label.text = f"[color=ff0000]An error occurred:\n{e}[/color]"

if __name__ == '__main__':
    IotApp().run()
