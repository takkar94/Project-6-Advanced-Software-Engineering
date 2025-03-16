import psutil

def get_battery_status():
    battery = psutil.sensors_battery()
    if battery is None:
        return "Battery information not available"

    percentage = battery.percent
    plugged_in = battery.power_plugged  # True if charging or connected to power
    status = "Plugged in" if plugged_in else "Not plugged in"
    notification_stat = 1 if plugged_in else 0

    return f"Battery Percentage: {percentage}% | Power Status: {status}", notification_stat

if __name__ == "__main__":
    print(get_battery_status())  # This only runs if executed directly, not on import
