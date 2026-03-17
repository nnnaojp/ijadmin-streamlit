import sys
import json
sys.path.append("..")

import config_gens.mistral_json as mistral_json
import config_gens.dcm_json as dcm_json
import config_gens.tiff2lb_json as tiff2lb_json
import config_gens.dnc_json as dnc_json
import config_gens.fxijconfig as fxijconfig

def load_config_test(filepath):
    print(f"Reading {filepath}")
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    servers = data.get("Server", [])

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
                    # lb_entries is a list, e.g. [{"nHIF": 1, "nHead": 1}, ...]
                    # but l_idx points to the specific LB index
                    lb_entries = servers[s_idx]["PDC"][p_idx]["LB"]
                    nhead = lb_entries[l_idx].get("nHead", 0)
                    color_nhead += nhead
                except (IndexError, KeyError, TypeError) as e:
                    pass
        color_head_counts.append(str(color_nhead))

    color_str = " ".join(colors)
    head_count_str = " ".join(color_head_counts)

    print(f"Color:          {color_str}")
    print(f"nHead:          {head_count_str}")
    print("-" * 20)

print("\n--- Testing original mistral ---")
load_config_test("/usr/mistral/conf/mistral.json")

def simulate(setup_func):
    mc = mistral_json.MistralConfig(fpath='/tmp/mistral.json')
    dc = dcm_json.DcmConfig(fpath='/tmp/dcm.json')
    tc = tiff2lb_json.Tiff2lb(fpath='/tmp/tiff2lb.json')
    dnc = dnc_json.MistralConfig(fpath='/tmp/dnc.json')
    setup_func(mc, dc, tc, dnc, ('10.20.14.106', '10.20.14.105', '10.20.14.107'))
    load_config_test("/tmp/mistral.json")

print("\n--- Testing simulated Type500_RC1536_40mpm ---")
simulate(fxijconfig.setup1_Type500_RC1536_40mpm)
print("\n--- Testing simulated Type1000_RC1536_40mpm ---")
simulate(fxijconfig.setup4_Type1000_RC1536_40mpm)
print("\n--- Testing simulated Type1000_SambaG5Lx2_30mpm ---")
simulate(fxijconfig.setup6_Type1000_SambaG5Lx2_30mpm)
