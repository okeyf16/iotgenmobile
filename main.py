# File: main.py
# Updated logic to interact with your specific Flask API on Azure.

import requests
import json
from kivy.app import App
from kivy.uix.scrollview import ScrollView  # Needed for the .kv file

# --- IMPORTANT: CONFIGURE THESE VALUES ---
# The base URL from your Azure App Service
BASE_URL = "https://iotoct2-c8g7gjbdhec2b6h9.northeurope-01.azurewebsites.net"
# The API key you set in your backend's environment variables
API_KEY = "987654321"
# The device ID you want to query data for
DEVICE_ID = "Raspberry Pi Web Client"
# -----------------------------------------


class IotApp(App):
    def build(self):
        self.title = 'IoT Dashboard'
        # The .kv file is loaded automatically
        return super().build()

    def _fetch_and_sort_telemetry(self):
        """Helper function to get all data for a device and sort it by timestamp."""
        try:
            url = f"{BASE_URL}/telemetry"
            params = {'deviceId': DEVICE_ID}
            headers = {'x-api-key': API_KEY}

            response = requests.get(
                url, params=params, headers=headers, timeout=10)
            response.raise_for_status()  # Raise an exception for HTTP errors

            entities = response.json()

            # Sort the results. We assume each record has a 'timestamp' field.
            # Sorting is newest first.
            sorted_entities = sorted(
                entities,
                key=lambda e: e.get('timestamp', ''),
                reverse=True
            )
            return sorted_entities

        except requests.exceptions.RequestException as e:
            self.root.ids.results_label.text = f"Connection Error:\n{e}"
            return None
        except Exception as e:
            self.root.ids.results_label.text = f"An error occurred:\n{e}"
            return None

    def get_latest_reading(self):
        """Button callback to get and display the single latest reading."""
        self.root.ids.results_label.text = "Fetching latest reading..."
        sorted_entities = self._fetch_and_sort_telemetry()

        if sorted_entities:
            latest = sorted_entities[0]
            # Format the output string nicely
            display_text = "--- Latest Reading ---\n"
            for key, value in latest.items():
                if key not in ["PartitionKey", "RowKey", "etag"]:  # Exclude metadata
                    display_text += f"{key.capitalize()}: {value}\n"
            self.root.ids.results_label.text = display_text
        elif sorted_entities is not None:  # It was an empty list, not an error
            self.root.ids.results_label.text = "No data found for this device."

    def get_last_3_readings(self):
        """Button callback to get and display the last three readings."""
        self.root.ids.results_label.text = "Fetching last 3 readings..."
        sorted_entities = self._fetch_and_sort_telemetry()

        if sorted_entities:
            # Get the first 3 items from the sorted list
            last_three = sorted_entities[:3]
            display_text = "--- Last 3 Readings ---\n\n"
            for i, entity in enumerate(last_three):
                display_text += f"Reading #{i+1}\n"
                for key, value in entity.items():
                    if key not in ["PartitionKey", "RowKey", "etag"]:
                        display_text += f"  {key.capitalize()}: {value}\n"
                display_text += "---\n"
            self.root.ids.results_label.text = display_text
        elif sorted_entities is not None:
            self.root.ids.results_label.text = "No data found for this device."

    def send_command(self, command):
        """
        Placeholder for sending commands. Your provided backend code does not
        include an endpoint for this, but the UI button is here for future use.
        """
        self.root.ids.results_label.text = f"Command '{command.upper()}' functionality is not yet implemented in the backend."
        print(f"UI Triggered command: {command}")


if __name__ == '__main__':
    IotApp().run()
