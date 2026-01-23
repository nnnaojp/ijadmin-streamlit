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
    versions = []
    password = get_sudo_password()
    
    if not password:
        return ["Error: sudo password not configured"] * 4

    for i in range(1, 5):
        command = ["sudo", "-S", "/usr/mistral/bin/pdc", "-i", str(i), "--pdcr", "0xf4", "1"]
        try:
            result = subprocess.run(
                command,
                input=password + "\n",
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                # Output format example: "00f4: 20251029"
                # User wants only the second column (the version)
                output = result.stdout.strip()
                parts = output.split()
                if len(parts) >= 2:
                    versions.append(parts[1])
                else:
                    # Fallback if format is unexpected
                    versions.append(output)
        except Exception as e:
            versions.append(f"Exception: {str(e)}")
            
    return versions


def get_hif_versions():
    """Returns a 2D list of HIF versions."""
    all_versions = []
    password = get_sudo_password()
    
    if not password:
        # Return 4x4 error structure
        return [["Error: sudo password not configured"] * 4 for _ in range(4)]

    for pdc_i in range(1, 5):
        pdc_versions = []
        for hif_i in range(1, 5):
            command = ["sudo", "-S", "/usr/mistral/bin/pdc", "-i", str(pdc_i), str(hif_i), "--hifr", "0xf008", "4"]
            try:
                result = subprocess.run(
                    command,
                    input=password + "\n",
                    capture_output=True,
                    text=True,
                    check=False
                )
                
                if result.returncode == 0:
                    # Output example:
                    # f008: 09
                    # f009: 10
                    # f00a: 24
                    # f00b: 20
                    # We want to form "20241009" (f00b + f00a + f009 + f008)
                    lines = result.stdout.strip().split('\n')
                    byte_values = []
                    for line in lines:
                        parts = line.split()
                        if len(parts) >= 2:
                            byte_values.append(parts[1])
                    
                    # Reverse join
                    version_str = "".join(reversed(byte_values))
                    all_versions.append([f"(PDC{pdc_i})"])
                    pdc_versions.append(version_str)
            except Exception as e:
                pdc_versions.append(f"Exception: {str(e)}")
        all_versions.append(pdc_versions)
            
    return all_versions


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


def get_server_total_memory_gb():
    """Returns total server memory in GB."""
    # Use free -g or parse /proc/meminfo
    try:
        # free -g | awk '/^Mem:/{print $2}'
        result = run_command(["free", "-g"])
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                # Header: total used free ...
                # Mem:    123   ...
                parts = lines[1].split()
                if len(parts) >= 2:
                    return int(parts[1])
    except Exception:
        pass
    return 0


def get_disk_info(exclude_patterns=None):
    """Retrieves disk information using lsblk."""
    result = run_command(["lsblk", "-e", "7,11", "-o", "NAME,TYPE,SIZE,MOUNTPOINT"])
    if isinstance(result, str):
        return "Unknown"
    
    if result.returncode == 0:
        if not exclude_patterns:
            return result.stdout
            
        lines = result.stdout.splitlines()
        filtered_lines = []
        if lines:
            filtered_lines.append(lines[0]) # Header
            
        for line in lines[1:]:
            # Filter out lines containing any of the exclude patterns
            if not any(pat in line for pat in exclude_patterns):
                filtered_lines.append(line)
        
        return "\n".join(filtered_lines)
    return "Unknown"


def init_raid_sequence():
    """Executes the RAID initialization sequence."""
    commands = [
        ["mdadm", "--stop", "/dev/md127"],
        ["mdadm", "--stop", "/dev/md126"],
        ["mdadm", "--zero-superblock", "/dev/sdb1"],
        ["mdadm", "--zero-superblock", "/dev/sdc1"],
        ["mdadm", "--zero-superblock", "/dev/sdd1"],
        ["mdadm", "-C", "/dev/md127", "-l", "0", "-n", "3", "/dev/sdb1", "/dev/sdc1", "/dev/sdd1"],
        
        # mkfs.ext4 /dev/md127
        # -F to force if needed? User didn't specify. Assuming clean.
        ["mkfs.ext4", "/dev/md127"],
        
        ["mount", "-o", "rw,remount", "/boot"],
        ["update-initramfs", "-u"],
        # ["mount", "/dev/md127", "/mnt/ssd1"]
    ]
    
    results = []
    
    for cmd in commands:
        # Special handling for potentially non-critical commands?
        # mdadm --stop might fail if not running, that's fine.
        # zero-superblock might fail, fine.
        
        # We'll execute and log output.
        # We iterate and return the first failure? Or try to continue?
        # Usually RAID init should abort if Creation fails.
        
        res = execute_sudo_command(cmd)
        
        # If mdadm --stop fails, it might just be "not found", which is OK.
        # If initramfs fails, that's bad.
        
        cmd_str = " ".join(cmd)
        if res != "Success":
            # Allow some failures?
            if "mdadm --stop" in cmd_str or "zero-superblock" in cmd_str:
                results.append(f"Warning: {cmd_str} -> {res}")
            else:
                results.append(f"Error: {cmd_str} -> {res}")
                return "\n".join(results) # Abort on error for critical steps
        else:
            results.append(f"Success: {cmd_str}")
            
    return "Success"

def unmount_raid_volume():
    """Unmounts RAID volumes /dev/md127 and /dev/md126. Ignores errors."""
    # Try to unmount both
    execute_sudo_command(["umount", "/dev/md127"])
    execute_sudo_command(["umount", "/dev/md126"])
    # Always return success as requested
    return "Success"
    
def mount_raid_volume():
    """Mounts RAID volumes /dev/md127 to /mnt/ssd1."""
    # Command: mount /dev/md127 /mnt/ssd1
    # We should use execute_sudo_command because it likely requires root privileges
    cmd = ["mount", "/dev/md127", "/mnt/ssd1"]
    return execute_sudo_command(cmd)

def import_settings_package(tgz_path):
    """
    Imports settings from a tgz package.
    1. Creates a temp dir in /tmp.
    2. Extracts tgz there.
    3. Runs sudo ./import.sh in that dir.
    4. Cleans up temp dir and tgz file.
    """
    import os
    import time
    import shutil
    
    # Create unique work directory
    timestamp = int(time.time())
    work_dir = f"/tmp/import_settings_{timestamp}"
    
    try:
        os.makedirs(work_dir, exist_ok=True)
    except Exception as e:
        return f"Error creating work directory: {str(e)}"
        
    try:
        # Extract tgz
        # tar -xzvf <tgz_path> -C <work_dir>
        cmd_extract = ["tar", "-xzvf", tgz_path, "-C", work_dir]
        res_extract = run_command(cmd_extract)
        
        if res_extract.returncode != 0:
            # Cleanup and return error
            shutil.rmtree(work_dir, ignore_errors=True)
            return f"Error extracting tgz:\n{res_extract.stderr}"
            
        # Run import.sh
        # Expected path: <work_dir>/import.sh
        # import_script = os.path.join(work_dir, "/tmp/import.sh")
        
        # Check if script exists
        # Since we might need sudo to see files if extraction preserved permissions that block us?
        # But we extracted it, so we should own it or have read access usually.
        # Let's just try running it via sudo.
        
        # We need to execute it inside the work_dir because the script might refer to relative files (conf/, etc/)
        # execute_sudo_command doesn't natively support cwd change easily without chaining in shell.
        # So we construct a shell command: cd <work_dir> && ./import.sh
        
        # However, execute_sudo_command uses subprocess with password input.
        # We can pass the relative command but we need to ensure CWD.
        # Let's modify execute_sudo_command or just wrap it here.
        
        # Actually, execute_sudo_command is simple. Let's send a customized command list.
        # "sudo -S sh -c 'cd <dir> && ./import.sh'"
        
        cmd_import = ["sh", "-c", f"cd {work_dir} && chmod +x ./import.sh && ./import.sh"]
        res_import = execute_sudo_command(cmd_import)
        
        return res_import
        
    except Exception as e:
        return f"Exception during import: {str(e)}"
    finally:
        # Cleanup
        # 1. Remove work_dir
        # We might need sudo to remove if files inside were created by root?
        # But we extracted them. If import.sh created root files inside, standard rm might fail.
        # Safer to use sudo rm -rf
        cleanup_cmd = ["rm", "-rf", work_dir]
        execute_sudo_command(cleanup_cmd)
        
        # 2. Remove tgz_path
        if os.path.exists(tgz_path):
            try:
                os.remove(tgz_path)
            except:
                # If failed (maybe owner issue), try sudo
                execute_sudo_command(["rm", "-f", tgz_path])

# Global flag to track syslog initialization
_syslog_initialized = False

def write_syslog(message, priority=None):
    """Writes a message to syslog."""
    import syslog
    global _syslog_initialized
    
    if not _syslog_initialized:
        print("syslog initialized")
        syslog.openlog(ident="ijadmin-ui", logoption=syslog.LOG_PID, facility=syslog.LOG_LOCAL0)
        _syslog_initialized = True
        
    if priority is None:
        priority = syslog.LOG_INFO
    syslog.syslog(priority, message)
