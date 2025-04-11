import psutil

def get_battery_status():
    battery = psutil.sensors_battery()
    if battery is None:
        return "--", 0

    percentage = battery.percent
    plugged_in = battery.power_plugged  # True if charging or connected to power
    return f"{percentage}", 1 if plugged_in else 0

if __name__ == "__main__":
    print(get_battery_status())
