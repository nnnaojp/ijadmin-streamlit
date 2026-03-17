import sys
import syslog

# Mock function for testing output format logic
def mock_write_syslog(message, priority=None):
    if priority is None:
        priority = syslog.LOG_INFO
    # Translate syslog priority to name
    prio_map = {syslog.LOG_INFO: "INFO", syslog.LOG_WARNING: "WARN", syslog.LOG_ERR: "ERROR", syslog.LOG_DEBUG: "DEBUG"}
    prio_str = prio_map.get(priority, str(priority))
    print(f"syslog: [{prio_str}] {message}")

mock_write_syslog("Starting operation XYZ")
