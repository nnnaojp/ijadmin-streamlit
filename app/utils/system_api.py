import subprocess


def run_command(command, encoding="utf-8"):
    """Runs a system command and returns the result."""
    try:
        result = subprocess.run(
            command, capture_output=True, text=True, encoding=encoding
        )
        return result
    except Exception as e:
        return str(e)


def reboot_system():
    """Reboots the system (placeholder for demo)."""
    # subprocess.run(["shutdown", "/r", "/t", "0"])
    return "Reboot command executed (Demo)"


def get_ip_address():
    """Retrieves the server's IP address specific to Linux."""
    result = run_command(["hostname", "-I"])
    if isinstance(result, str):
        return "Unknown"
    
    if result.returncode == 0:
        # hostname -I returns space-separated IPs, take the first one
        ips = result.stdout.strip().split()
        if ips:
            return ips[0]
    return "Unknown"


def get_mistral_version():
    """Reads the Mistral version from the configuration file."""
    try:
        with open("/usr/mistral/conf/mistralversion", "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return "Unknown"


def get_pdc_versions():
    """Returns a list of PDC versions."""
    # Placeholder: return empty list or mock data
    return ['20251201', '20251202']


def get_hif_versions():
    """Returns a 2D list of HIF versions."""
    # Placeholder: return empty list or mock data
    return [['20251201', '20251202'], ['20251201', '20251202']]


def search_system_logs(query, password):
    """Searches system logs usinggrep with sudo."""
    if not query:
        return "Search query cannot be empty."
    
    # -S reads password from stdin
    # -r recursive
    # -n line number
    # -I ignore binary files
    command = ["sudo", "-S", "grep", "-I", query, "/var/mistral/log/mistlog.log"]
    
    try:
        result = subprocess.run(
            command,
            input=password + "\n",
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            return result.stdout
        elif result.returncode == 1:
            return "No matches found."
        else:
            return f"Error executing grep:\n{result.stderr}"
    except Exception as e:
        return f"An error occurred: {str(e)}"
