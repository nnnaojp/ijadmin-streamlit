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

    for i in range(1, 3):
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
                    version = f"(PDC{i}) {parts[1]}"
                    versions.append(version)
                else:
                    # Fallback if format is unexpected
                    versions.append(output)
            else:
                break
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

    for pdc_i in range(1, 3):
        pdc_versions = [f"(PDC{pdc_i})"]
        for lb_i in range(1, 5):
            lb_versions = [f" (LB{lb_i})"]
            alive_lbs = 0
            init_command = ["sudo", "-S", "/usr/mistral/bin/pdc", "-i", str(pdc_i), str(lb_i), "--csinit-hif"]
            try:
                subprocess.run(
                    init_command,
                    input=password + "\n",
                    capture_output=True,
                    text=True,
                    check=False
                )
            except Exception:
                pass

            for hif_i in range(1, 5):
                command = ["sudo", "-S", "/usr/mistral/bin/pdc", "-i", str(pdc_i), str(lb_i), str(hif_i), "--hifr", "0xf008", "4"]
                try:
                    result = subprocess.run(
                        command,
                        input=password + "\n",
                        capture_output=True,
                        text=True,
                        check=False
                    )
                    print(f"hf_vers: {pdc_i}.{lb_i}.{hif_i} ret:",result.returncode)
                    if result.returncode == 0:
                        # Output example:
                        # f008: 09
                        # f009: 10
                        # f00a: 24
                        # f00b: 20
                        # We want to form "20241009" (f00b + f00a + f009 + f008)
                        lines = result.stdout.strip().split('\n')
                        print(f"hif_vers: {pdc_i}.{lb_i}.{hif_i} lines:", lines)
                        byte_values = []
                        for line in lines:
                            parts = line.split()
                            if len(parts) >= 2:
                                byte_values.append(parts[1])
                    
                        # Reverse join
                        version_str = "".join(reversed(byte_values))
                        lb_versions.append(version_str)
                        alive_lbs = alive_lbs+1
                    else:
                        break
                except Exception as e:
                    lb_versions.append(f"Exception: {str(e)}")
            if alive_lbs > 0:
                if lb_i == 1:
                    all_versions.append(pdc_versions)
                all_versions.append(lb_versions)
            
    return all_versions


import shlex

MAX_LOG_BYTES = 10 * 1024 * 1024  # 10 MB

def get_all_system_logs(password):
    """Returns the full content of the system log file.
    
    If the log file exceeds 10 MB, only the most recent 10 MB is returned.
    Returns a tuple of (content: str, truncated: bool).
    """
    log_file = "/var/mistral/log/mistlog.log"

    # Check file size first
    try:
        size_result = subprocess.run(
            ["sudo", "-S", "stat", "-c", "%s", log_file],
            input=password + "\n",
            capture_output=True,
            text=True,
            check=False
        )
        file_size = int(size_result.stdout.strip()) if size_result.returncode == 0 else 0
    except Exception:
        file_size = 0

    truncated = file_size > MAX_LOG_BYTES

    if truncated:
        # Read only the last 10 MB
        command = ["sudo", "-S", "tail", "-c", str(MAX_LOG_BYTES), log_file]
    else:
        command = ["sudo", "-S", "cat", log_file]

    try:
        result = subprocess.run(
            command,
            input=password + "\n",
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            return result.stdout, truncated
        else:
            return f"Error reading log file:\n{result.stderr}", False
    except Exception as e:
        return f"An error occurred: {str(e)}", False


def search_system_logs(query, password):
    """Searches system logs using grep with sudo. Supports AND (space) and OR (|) search."""
    if not query:
        return "Search query cannot be empty."
    
    log_file = "/var/mistral/log/mistlog.log"
    
    # Determine search mode
    if "|" in query:
        # OR Search
        parts = [p.strip() for p in query.split("|") if p.strip()]
        if not parts:
            return "Invalid query."
        regex = "|".join(parts)
        # grep -E for extended regex (OR)
        command = ["sudo", "-S", "grep", "-I", "-E", regex, log_file]
    else:
        # AND Search (space separated)
        parts = query.split()
        if not parts:
            return "Invalid query."
            
        if len(parts) == 1:
            # Simple single word search
            command = ["sudo", "-S", "grep", "-I", parts[0], log_file]
        else:
            # Multiple words: chain grep commands
            # grep -I "A" file | grep -I "B" | ...
            # We need to construct a shell command string
            
            # Quote parts for safety
            quoted_parts = [shlex.quote(p) for p in parts]
            
            # First grep reads the file
            shell_cmd = f"grep -I {quoted_parts[0]} {log_file}"
            
            # Subsequent greps filter the output
            for p in quoted_parts[1:]:
                shell_cmd += f" | grep -I {p}"
                
            # Execute via sudo sh -c
            command = ["sudo", "-S", "sh", "-c", shell_cmd]

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
    """Retrieves memory information using free without args and formats it by dividing values by 1000000."""
    result = run_command(["free"])
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
            new_parts = [parts[0]]
            for p in parts[1:]:
                try:
                    val = int(float(p) / 1000000.0)
                    new_parts.append(str(val))
                except ValueError:
                    new_parts.append(p)
            rows.append(new_parts)
        
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
        result = run_command(["free"])
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            if len(lines) >= 2:
                parts = lines[1].split()
                if len(parts) >= 2:
                    return int(float(parts[1]) / 1000000.0)
    except Exception:
        pass
    return 0


def get_gpu_info():
    """Retrieves GPU information using nvidia-smi."""
    result = run_command(["nvidia-smi", "--query-gpu=name,driver_version,memory.total", "--format=csv,noheader,nounits"])
    if isinstance(result, str):
        return "nvidia-smi not available or no GPU found."

    if result.returncode == 0:
        lines = result.stdout.strip().split('\n')
        headers = ["Name", "Driver", "Mem Total(MiB)"]
        rows = []
        for line in lines:
            if line.strip():
                rows.append([v.strip() for v in line.split(',')])

        # Calculate column widths
        col_widths = [len(h) for h in headers]
        for row in rows:
            for i, val in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(val))

        def format_row(row_data):
            parts = []
            for i, width in enumerate(col_widths):
                val = row_data[i] if i < len(row_data) else ""
                if i == 0:
                    parts.append(f"{val:<{width}}")
                else:
                    parts.append(f"{val:>{width}}")
            return "  ".join(parts)

        output = [format_row(headers)]
        for row in rows:
            output.append(format_row(row))
        return "\n".join(output)
    else:
        return "nvidia-smi not available or no GPU found."


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
            
        ignoring = False
        for line in lines[1:]:
            # lsblk outputs top-level devices starting with alphanumeric characters.
            # Child devices start with spaces or tree characters.
            if len(line) > 0 and line[0].isalnum():
                if any(pat in line for pat in exclude_patterns):
                    ignoring = True
                else:
                    ignoring = False
            
            if ignoring:
                continue
                
            # If the current line itself matches the pattern (for non-top-level exclusions)
            if any(pat in line for pat in exclude_patterns):
                continue
                
            filtered_lines.append(line)
        
        return "\n".join(filtered_lines)
    return "Unknown"


def get_raid_disk_info():
    """Returns lsblk output filtered to only show disks related to md127."""
    result = run_command(["lsblk", "-e", "7,11", "-o", "NAME,TYPE,SIZE,MOUNTPOINT"])
    if isinstance(result, str):
        return "Unknown"
    
    if result.returncode != 0:
        return "Unknown"

    lines = result.stdout.splitlines()
    if not lines:
        return "Unknown"

    header = lines[0]

    # Split into blocks per top-level disk
    blocks = []
    current_block = []
    for line in lines[1:]:
        if len(line) > 0 and line[0].isalnum():
            if current_block:
                blocks.append(current_block)
            current_block = [line]
        else:
            current_block.append(line)
    if current_block:
        blocks.append(current_block)

    # Keep only blocks that contain md127 anywhere in the subtree
    filtered_blocks = [block for block in blocks if any("md127" in l for l in block)]

    result_lines = [header]
    for block in filtered_blocks:
        result_lines.extend(block)

    return "\n".join(result_lines)


def get_os_disk_info():
    """Returns a tuple of (os_disk_name, display_text) for the OS disk (the disk mounted at /).

    Returns:
        tuple: (
            os_disk_name (str | None): e.g. "/dev/sdb", or None if not detected,
            display_text (str): lsblk output for the OS disk, for display purposes
        )
    """
    import re as _re
    # /proc/mounts からOSディスク名を特定
    os_disk_name = None
    try:
        with open("/proc/mounts", "r") as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 2 and parts[1] == "/":
                    m = _re.match(r'^/dev/(sd[a-z]+)', parts[0])
                    if m:
                        os_disk_name = m.group(1)
                        break
    except Exception:
        pass

    if not os_disk_name:
        return None, "OSディスクを特定できませんでした"

    result = run_command(["lsblk", "-e", "7,11", "-o", "NAME,TYPE,SIZE,MOUNTPOINT"])
    if isinstance(result, str):
        return os_disk_name, "Unknown"
    if result.returncode != 0:
        return os_disk_name, "Unknown"

    lines = result.stdout.splitlines()
    if not lines:
        return os_disk_name, "Unknown"

    header = lines[0]

    # Split into blocks per top-level disk
    blocks = []
    current_block = []
    for line in lines[1:]:
        if len(line) > 0 and line[0].isalnum():
            if current_block:
                blocks.append(current_block)
            current_block = [line]
        else:
            current_block.append(line)
    if current_block:
        blocks.append(current_block)

    # OSディスクのブロックのみ抽出 (例: os_disk_name="sdb" でblock[0]が"sdb"で始まるもの)
    filtered_blocks = [block for block in blocks if block and block[0].startswith(os_disk_name)]

    result_lines = [header]
    for block in filtered_blocks:
        result_lines.extend(block)

    display_text = "\n".join(result_lines)
    return f"/dev/{os_disk_name}", display_text


def init_raid_sequence(os_disk: str):
    """Executes the RAID initialization sequence.

    Args:
        os_disk: OSディスクのパス (例: "/dev/sdb")。get_os_disk_info()の戻り値①を渡すこと。

    1) アクティブなmdNを検出し、構成sdを把握してstop/zero-superblock
    2) パーティションテーブルの消去 (wipefs, sgdisk)
    3) RAID作成 (mdadm -C, mkfs.ext4, mount, update-initramfs)
    """
    import re, glob
    write_syslog(f"init_raid_sequence strated. os_disk={os_disk}")
    results = []
    sd_devices = []  # mdNから動的に取得、なければデフォルト

    # --- Step 1: アクティブなmdNを検出し停止 ---
    try:
        with open("/proc/mdstat", "r") as f:
            mdstat_lines = f.readlines()

        for line in mdstat_lines:
            # 例: "md127 : active raid0 sdb[0] sdc[1] sdd[2]"
            if not (line.startswith("md") and " : active" in line):
                continue

            parts = line.split()
            md_name = parts[0]                        # e.g. "md127"
            md_device = f"/dev/{md_name}"

            # sd構成要素を抽出 (例: sdb[0] -> /dev/sdb)
            members = []
            for part in parts:
                m = re.match(r'^([a-z]+(?:\d+)?)\[\d+\]', part)
                if m:
                    members.append(f"/dev/{m.group(1)}")

            results.append(f"Info: {md_device} is active, members: {', '.join(members)}")

            # mdを停止
            write_syslog(f"mdadm --stop...")
            res = execute_sudo_command(["mdadm", "--stop", md_device])
            if res == "Success":
                results.append(f"Success: mdadm --stop {md_device}")
            else:
                results.append(f"Warning: mdadm --stop {md_device} -> {res}")

            # zero-superblock (警告扱い)
            write_syslog(f"mdadm --zero-superblock...")
            for dev in members:
                res = execute_sudo_command(["mdadm", "--zero-superblock", dev])
                if res == "Success":
                    results.append(f"Success: mdadm --zero-superblock {dev}")
                else:
                    results.append(f"Warning: mdadm --zero-superblock {dev} -> {res}")

            if members:
                sd_devices = members

    except Exception as e:
        results.append(f"Warning: could not read /proc/mdstat -> {str(e)}")

    # sd要素が取得できなかった場合は、マウントされていない /dev/sdN を動的に取得
    if not sd_devices:
        try:
            # マウント済みデバイスを取得
            mounted = set()
            with open("/proc/mounts", "r") as f:
                for line in f:
                    parts = line.split()
                    if parts:
                        mounted.add(parts[0])

            results.append(f"Info: OS disk: {os_disk}")

            # /dev/sd? を列挙し、マウントされておらずOSディスクでないものを選択
            all_sd = sorted(glob.glob("/dev/sd[a-z]") + glob.glob("/dev/sd[a-z][a-z]"))
            sd_devices = [
                dev for dev in all_sd
                if dev not in mounted and dev != os_disk
            ]
            results.append(f"Info: no active md found, detected unmounted sd devices: {', '.join(sd_devices) if sd_devices else 'none'}")
        except Exception as e:
            results.append(f"Warning: could not detect unmounted sd devices -> {str(e)}")

    # --- sd_devices バリデーション ---
    if len(sd_devices) != 3:
        results.append(f"Error: RAID requires exactly 3 sd devices, but found {len(sd_devices)}: {', '.join(sd_devices) if sd_devices else 'none'}")
        return "\n".join(results)

    # --- Step 2: パーティションテーブルの消去 ---
    write_syslog(f"wipefs...")
    for dev in sd_devices:
        res = execute_sudo_command(["wipefs", "-a", dev])
        if res == "Success":
            results.append(f"Success: wipefs -a {dev}")
        else:
            results.append(f"Error: wipefs -a {dev} -> {res}")
            return "\n".join(results)

    write_syslog(f"sgdisk...")
    for dev in sd_devices:
        res = execute_sudo_command(["sgdisk", "--zap-all", dev])
        if res == "Success":
            results.append(f"Success: sgdisk --zap-all {dev}")
        else:
            results.append(f"Error: sgdisk --zap-all {dev} -> {res}")
            return "\n".join(results)

    # --- Step 3: RAID作成 ---
    write_syslog(f"mdadm -C...")
    n = len(sd_devices)
    create_cmd = ["mdadm", "-C", "/dev/md127", "-l", "0", "-n", str(n)] + sd_devices
    res = execute_sudo_command(create_cmd)
    cmd_str = " ".join(create_cmd)
    if res == "Success":
        results.append(f"Success: {cmd_str}")
    else:
        results.append(f"Error: {cmd_str} -> {res}")
        return "\n".join(results)

    write_syslog(f"mkfs...")
    for cmd in [
        ["mkfs.ext4", "/dev/md127"],
        ["mount", "-o", "rw,remount", "/boot"],
        ["update-initramfs", "-u"],
    ]:
        res = execute_sudo_command(cmd)
        cmd_str = " ".join(cmd)
        if res == "Success":
            results.append(f"Success: {cmd_str}")
        else:
            results.append(f"Error: {cmd_str} -> {res}")
            return "\n".join(results)

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
