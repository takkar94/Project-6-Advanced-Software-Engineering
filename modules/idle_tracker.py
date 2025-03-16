import ctypes

class LASTINPUTINFO(ctypes.Structure):
    _fields_ = [("cbSize", ctypes.c_uint), ("dwTime", ctypes.c_ulong)]

def get_idle_time():
    """Returns the idle time in seconds."""
    lii = LASTINPUTINFO()
    lii.cbSize = ctypes.sizeof(LASTINPUTINFO)
    
    if ctypes.windll.user32.GetLastInputInfo(ctypes.byref(lii)):
        milliseconds_since_last_input = ctypes.windll.kernel32.GetTickCount() - lii.dwTime
        return milliseconds_since_last_input / 1000.0  # Convert to seconds

    return 0  # Return 0 if function fails

if __name__ == "__main__":
    print(f"Idle Time: {get_idle_time()} seconds")
