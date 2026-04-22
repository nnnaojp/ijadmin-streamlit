import json

class Tiff2lbConfig:
    def __init__(self,fpath='/tmp/tiff2lb.json'):
        self.fpath = fpath
        self.params = {
            "Threads": 4,
            "Mirror": False,
            "Compress": False,
            "UseLastLine": True,
        }
        self.headtype = {"LineHeadType": []}
        self.linehead = {"LineHead": []}

    def _headTypeEntry(self,arg):
        head_type = {
            "Dimatix_SambaG3Lx12": {
                "ID": 1,
                "Name": "Dimatix_SambaG3Lx12",
                "Margin": 100,
                "MaxWidth": 24448,
                "BPS": [
                    1,
                    2
                ],
                "DPI": {
                    "X": [
                        1200
                    ],
                    "Y": [
                        1200
                     ]
                }
            },
            "Dimatix_SambaG3Lx24": {
                "ID": 1,
                "Name": "Dimatix_SambaG3Lx24",
                "Margin": 100,
                "MaxWidth": 49024,
                "BPS": [
                    1,
                    2
                ],
                "DPI": {
                    "X": [
                        1200
                    ],
                    "Y": [
                        1200
                    ]
                }
            },
            "SII_RC1536x5" : {
                "ID": 2,
                "Name": "SII_RC1536x5",
                "Margin": 0,
                "MaxWidth": 7680,
                "BPS": [
                    1,
                    2
                ],
                "DPI": {
                    "X": [
                        360
                    ],
                    "Y": [
                        360
                    ]
                }
            },
            "SII_RC1536x10" : {
                "ID": 2,
                "Name": "SII_RC1536x10",
                "Margin": 0,
                "MaxWidth": 15360,
                "BPS": [
                    1,
                    2
                ],
                "DPI": {
                    "X": [
                        360
                    ],
                    "Y": [
                        360
                    ]
                }
            }
        }
        return head_type[arg]

    def setHeadType(self,*args):
        for arg in args:
            self.headtype["LineHeadType"].append(self._headTypeEntry(arg))

    def setLineHead(self,*entries):
        for entry in entries:
            lhead = {}
            lhead["Color"] = entry[0]
            lhead["ColorAbbr"] = entry[1]
            lhead["Type"] = entry[2]
            lhead["LB"] = []
            for arg in entry[3]:
                lhead["LB"].append({
                    "ServerNo": arg[0],
                    "LBNo": arg[1],
                    "Offset": arg[2],
                    "Width": arg[3]
                })
            self.linehead["LineHead"].append(lhead)

    def getConfig(self):
        return {**self.params, **self.headtype, **self.linehead}

    def save(self):
        conf = self.getConfig()
        print(json.dumps(conf, indent=2))
        with open(self.fpath, 'w') as f:
            json.dump(conf, f, indent=2)
