import json
import os
import config_gens.mistral_json as mistral_json
import config_gens.dcm_json as dcm_json
import config_gens.tiff2lb_json as tiff2lb_json
import config_gens.fxijconfig as fxijconfig
import config_gens.dnc_json as dnc_json

def save_config(config_data, config_index):
    """Saves configuration data (placeholder)."""
    # In a real app, this would write to a file or database
    generator = [
        fxijconfig.setup1_Type500_RC1536_40mpm,
        fxijconfig.setup2_Type500_RC1536x2_40mpm,
        fxijconfig.setup3_Type500_SambaG5Lx2_40mpm,
        fxijconfig.setup4_Type1000_RC1536_40mpm,
        fxijconfig.setup5_Type1000_RC1536x2_40mpm,
        fxijconfig.setup6_Type1000_SambaG5Lx2_30mpm,
        fxijconfig.setup7_Type1000_SambaG5Lx2_50mpm,
    ]
    mc = mistral_json.MistralConfig()
    dc = dcm_json.DcmConfig()
    tc = tiff2lb_json.Tiff2lbConfig()
    dnc = dnc_json.DncConfig()
    generator[config_index](mc,dc,tc,dnc,config_data['ips'],
        0 if config_data.get("print_direction") == "正方向" else 1)
    
    # Needs subprocess to run sudo cp
    import subprocess
    
    password = get_sudo_password()
    if not password:
        # If no password, we can't sudo. In a real scenario this might raise error or return False.
        # For now, we return False to indicate failure in 'setting update'.
        print("Error: No sudo password available for file copy.")
        return False

    def copy_file(src, dest):
        command = ["sudo", "-S", "cp", src, dest]
        try:
            result = subprocess.run(
                command,
                input=password + "\n",
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                print(f"Error copying {src} to {dest}: {result.stderr}")
                return False
            return True
        except Exception as e:
            print(f"Exception copying {src} to {dest}: {e}")
            return False

    # Copy files
    tmpdir = '/tmp/'
    confdir = '/usr/mistral/conf'
    etcdir = '/usr/mistral/etc'

    # # mistral.json -> /usr/mistral/conf
    # if not copy_file(os.path.join(tmpdir, 'mistral.json'), confdir): return False
    # # dcm.json -> /usr/mistral/conf
    # if not copy_file(os.path.join(tmpdir, 'dcm.json'), confdir): return False
    # # tiff2lb.json -> /usr/mistral/etc
    # if not copy_file(os.path.join(tmpdir, 'tiff2lb.json'), etcdir): return False

    return True


def load_config():
    """Loads configuration data from /usr/mistral/conf/mistral.json."""
    config_path = "/usr/mistral/conf/mistral.json"
    
    if not os.path.exists(config_path):
        return "Configuration file not found."
        
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            
        # Extract PrintWidth (Fixed: 516mm)
        print_width = "516mm"
        
        # Extract PrintDirection
        # System.InkjetHead[0].PrintDirection: 0->normal, 1->reverse
        try:
            pd_val = data.get("System", {}).get("InkjetHead", [])[0].get("PrintDirection", 0)
            print_direction = "reverse" if pd_val == 1 else "normal"
        except (IndexError, AttributeError):
            print_direction = "Unknown"
            
        # Extract Server IPs
        # Server[].IPAddress
        server_ips = []
        servers = data.get("Server", [])
        for i, server in enumerate(servers):
            # Limit to 4 servers
            if i >= 4: break
            ip = server.get("IPAddress", "Unknown")
            server_ips.append(ip)
            
        # Extract Colors and total_nhead per color
        # LineHead[].Color mapped to B, C, M, Y, W
        color_map = {
            "black": "B",
            "cyan": "C",
            "magenta": "M",
            "yellow": "Y",
            "white": "W"
        }
        colors = []
        color_head_counts = []
        line_heads = data.get("LineHead", [])
        
        for lh in line_heads:
            color_name = lh.get("Color", "").lower()
            
            # Map the color to single letter if possible, otherwise use original
            mapped_color = color_name
            for key, val in color_map.items():
                if color_name.startswith(key):
                    mapped_color = val
                    break
                    
            colors.append(mapped_color)
            
            # Extract nHead from LBID for this specific color
            color_nhead = 0
            lbid_list = lh.get("LBID", [])
            for lbid in lbid_list:
                lbid_str = str(lbid)
                if len(lbid_str) == 3:
                    s_idx = int(lbid_str[0]) - 1
                    p_idx = int(lbid_str[1]) - 1
                    l_idx = int(lbid_str[2]) - 1
                    try:
                        lb_entries = servers[s_idx]["PDC"][p_idx]["LB"]
                        # The l_idx is the index into the LB array. We want the nHead property of this specific LB.
                        nhead = lb_entries[l_idx].get("nHead", 0)
                        color_nhead += nhead
                    except (IndexError, KeyError, TypeError):
                        pass
            color_head_counts.append(str(color_nhead))
        
        color_str = " ".join(colors)
        head_count_str = " ".join(color_head_counts)
        print_width = f"{int(color_head_counts[0]) * 43}mm" if color_head_counts else "Unknown"
        
        # Build Output String
        lines = []
        lines.append(f"PrintWidth:     {print_width}")
        lines.append(f"PrintDirection: {print_direction}")
        
        for i, ip in enumerate(server_ips):
            lines.append(f"Server {i+1} IP:    {ip}")
            
        lines.append(f"Color:          {color_str}")
        lines.append(f"HeadCount:      {head_count_str}")
        
        return "\n".join(lines)
        
    except Exception as e:
        return f"Error loading config: {str(e)}"

def get_sudo_password():
    """Reads sudo password from .streamlit/config.toml"""
    import toml
    try:
        config_path = ".streamlit/config.toml"
        if not os.path.exists(config_path):
            # Fallback for dev environment or if running from different cwd
            config_path = os.path.join(os.path.dirname(__file__), "../.streamlit/config.toml")
        
        with open(config_path, "r", encoding="utf-8") as f:
            data = toml.load(f)
            return data.get("system", {}).get("sudo_password", "")
    except Exception as e:
        return f"Error reading sudo password: {e}"
        return ""

def get_admin_password():
    """Reads admin password from .streamlit/config.toml"""
    import toml
    try:
        config_path = ".streamlit/config.toml"
        if not os.path.exists(config_path):
            config_path = os.path.join(os.path.dirname(__file__), "../.streamlit/config.toml")
        
        with open(config_path, "r", encoding="utf-8") as f:
            data = toml.load(f)
            return data.get("system", {}).get("admin_password", "ijadmin")
    except Exception as e:
        print(f"Error reading admin password: {e}")
        return "ijadmin"

def get_mistral_cma_size():
    """Returns Mistral page memory size in GB from /etc/default/grub (cma=XXG)."""
    import re
    try:
        with open("/etc/default/grub", "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("#"):
                    continue
                
                match = re.search(r'cma=([0-9]+)[Gg]', line)
                if match:
                    return int(match.group(1))
            
    except Exception as e:
        print(f"Error reading /etc/default/grub: {e}")
        
    return 0

def update_mistral_cma_config(server_mem_gb):
    """Updates cma=XXXG in /etc/default/grub based on server memory."""
    from utils.system_api import execute_sudo_command
    
    target_cma = 9 if server_mem_gb <= 16 else 20
    
    # Use sed to replace cma=...G with target_cma
    # We target lines starting with GRUB_CMDLINE_LINUX (allowing for whitespace), ignoring comments
    # Regex: 's/cma=[0-9]\+[Gg]/cma={target_cma}G/'
    
    sed_expr = f"/^\\s*GRUB_CMDLINE_LINUX/ s/cma=[0-9]\\+[Gg]/cma={target_cma}G/"
    
    command = ["sed", "-i", sed_expr, "/etc/default/grub"]
    
    return execute_sudo_command(command)
