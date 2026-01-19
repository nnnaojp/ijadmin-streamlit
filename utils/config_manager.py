import json
import os
import config_gens.mistral_json as mistral_json
import config_gens.dcm_json as dcm_json
import config_gens.tiff2lb_json as tiff2lb_json
import config_gens.fxijconfig as fxijconfig

def save_config(config_data):
    """Saves configuration data (placeholder)."""
    # In a real app, this would write to a file or database
    configFunc = [
        fxijconfig.setup1_Type500_RC1536_40mpm,
        fxijconfig.setup2_Type500_RC1536x2_40mpm,
        fxijconfig.setup3_Type500_SambaG5Lx2_40mpm,
        fxijconfig.setup4_Type1000_RC1536_40mpm,
        fxijconfig.setup5_Type1000_RC1536x2_40mpm,
        fxijconfig.setup6_Type1000_SambaG5Lx2_30mpm,
        fxijconfig.setup7_Type1000_SambaG5Lx2_50mpm,
    ]
    user = 'ijadmin'
    passwd = 'ijadmin'
    tmpdir = '/tmp/'
    confdir = '/usr/mistral/conf'
    etcdir = '/usr/mistral/etc'
    cfgfile = ['mistral.json','dcm.json']
    etcfile = ['tiff2lb.json']
    # mc = mistral_json.MistralConfig()
    # dc = dcm_json.DcmConfig()
    # tc = tiff2lb_json.Tiff2lb()
    # svrlst = [myapp.serverSet.svrlist[i].address
    #               for i in range(myapp.serverSet.numServers)]
    # configFunc[myapp.serverSet.systemId-1](mc,dc,tc,svrlst)

    
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
            
        # Extract Colors
        # LineHead[].Color mapped to B, C, M, Y, W
        color_map = {
            "black": "B",
            "cyan": "C",
            "magenta": "M",
            "yellow": "Y",
            "white": "W"
        }
        colors = []
        line_heads = data.get("LineHead", [])
        for lh in line_heads:
            color_name = lh.get("Color", "").lower()
            if color_name in color_map:
                colors.append(color_map[color_name])
        
        color_str = "".join(colors)
        
        # Build Output String
        lines = []
        lines.append(f"PrintWidth:     {print_width}")
        lines.append(f"PrintDirection: {print_direction}")
        
        for i, ip in enumerate(server_ips):
            lines.append(f"Server {i+1} IP:    {ip}")
            
        lines.append(f"Color:          {color_str}")
        
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
        print(f"Error reading sudo password: {e}")
        return ""
