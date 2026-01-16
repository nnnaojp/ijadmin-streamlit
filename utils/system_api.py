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


from utils.config_manager import get_sudo_password

def execute_sudo_command(command_args):
    """Executes a command with sudo using the configured password."""
    password = get_sudo_password()
    if not password:
        return "Error: sudo password not configured in config.toml"

    # Prepend sudo -S to the command
    sudo_cmd = ["sudo", "-S"] + command_args
    
    try:
        result = subprocess.run(
            sudo_cmd,
            input=password + "\n",
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            return "Success"
        else:
            return f"Error: {result.stderr}"
    except Exception as e:
        return f"Exception: {str(e)}"

def reboot_system():
    """Reboots the system."""
    return execute_sudo_command(["shutdown", "-r", "now"])

def shutdown_system():
    """Shuts down the system."""
    return execute_sudo_command(["shutdown", "-h", "now"])


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


def get_cpu_info():
    """Retrieves CPU information using lscpu with filtering."""
    cmd = "LC_ALL=C lscpu | egrep 'Model name|Socket\(s\)|Core\(s\) per socket|Thread\(s\) per core|CPU\(s\)'"
    result = run_command(["sh", "-c", cmd])
    if isinstance(result, str):
        return "Unknown"
    
    if result.returncode == 0:
        return result.stdout
    return "Unknown"


def get_memory_info():
    """Retrieves memory information using free -h and formats it."""
    result = run_command(["free", "-h"])
    if isinstance(result, str):
        return "Unknown"
    
    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')
        if len(lines) < 2:
            return result.stdout

        # Parse headers
        raw_headers = lines[0].split()
        headers = ["Type"] + raw_headers
        
        rows = []
        # Parse data lines
        for line in lines[1:]:
            parts = line.split()
            rows.append(parts)
        
        # Calculate column widths
        max_cols = len(headers)
        col_widths = [0] * max_cols
        
        # Update widths based on headers
        for i, h in enumerate(headers):
            col_widths[i] = max(col_widths[i], len(h))
            
        # Update widths based on data
        for row in rows:
            for i, val in enumerate(row):
                if i < max_cols:
                    col_widths[i] = max(col_widths[i], len(val))
        
        # Build formatted string
        output = []
        
        def format_row(row_data):
            parts = []
            for i in range(max_cols):
                val = row_data[i] if i < len(row_data) else ""
                width = col_widths[i]
                if i == 0:
                    # First column left aligned
                    parts.append(f"{val:<{width}}")
                else:
                    # Others right aligned
                    parts.append(f"{val:>{width}}")
            return "  ".join(parts)
        
        output.append(format_row(headers))
        for row in rows:
            output.append(format_row(row))
            
        return "\n".join(output)

    return "Unknown"


def get_disk_info():
    """Retrieves disk information using lsblk."""
    result = run_command(["lsblk", "-e", "7,11", "-o", "NAME,TYPE,SIZE,MOUNTPOINT"])
    if isinstance(result, str):
        return "Unknown"
    
    if result.returncode == 0:
        return result.stdout
    return "Unknown"

