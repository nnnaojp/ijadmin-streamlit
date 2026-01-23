import json

class MistralConfig:
    def __init__(self,reverse=False,fpath='/tmp'):
        self.reverse = reverse
        self.fpath = [f"{fpath}/dnc_fwd.json", f"{fpath}/dnc_rev.json"]
        self.nozzle_data = {"DefectNozzleData": {
            "Date": "",
            "File": "",
        }}
        self.defect_ratio = {"DefectRatio": {
            "Both": [
                15,34,8,22,100
            ],
            "Left": [
                42,13,0,0,100
            ],
            "Right": [
                0,0,42,13,100
            ],
        }}
        self.lut = {"Lut": {
            "Both": [
                36,880,99998,9999
            ],
            "Left": [
                356,2554,99998,99999
            ],
            "Right": [
                358,2554,99998,99999
            ],
        }}
        self.mask_dark = {"MaskPatternDark": {
            "Both": [
                "0xffffffff",
                "0xffffffff",
            ],
            "Left": [
                "0xffffffff",
                "0xffffffff",
            ],
            "Right": [
                "0xffffffff",
                "0xffffffff",
            ],
        }}
        self.mask_light = {"MaskPatternLight": {
            "Both": [
                "0xa5a5a5a5",
                "0xa5a5a5a5",
            ],
            "Left": [
                "0xa5a5a5a5",
                "0x00000000",
            ],
            "Right": [
                "0x00000000",                
                "0xa5a5a5a5",
            ],
        }}
        self.max_nozzle_number = {"MaxNozzleNumber": 24448}
        self.threshold = {"Threshold": {
            "Both": [
                271, 929, 99999
            ],
            "Left": [
                1007, 2703, 99999
            ],
            "Right": [
                1009, 2704, 99999
            ],
        }}
        self.tone_threshold = {"ToneThreshold": 7}

    def _inkJetHeadEntry(self,arg) :
        support_heads = {
            "SambaG3": {
                "HeadType": "SambaG3",
                "DPI": 1200,
                "PrintDirection": 0,
                "nLineHead": 0,
                "ErrorHeadTemp": [
                    60,
                    50,
                    1,
                    0
                ],
                "ErrorHIFTemp": [
                    60,
                    50,
                    10,
                    0
                ],
                "OverlapMargin": 100,
                "MaxHeadPerHIF": 3
            },
            "RC1536": {
                "HeadType": "RC1536",
                "DPI": 360,
                "PrintDirection": 0,
                "nLineHead": 1,
                "ErrorHeadTemp": [
                    60,
                    50,
                    10,
                    0
                ],
                "ErrorHIFTemp": [
                    60,
                    50,
                    10,
                    0
                ],
                "OverlapMargin": 0,
                "MaxHeadPerHIF": 2
            }
        }
        support_heads[arg[0]]["nLineHead"] = arg[1]
        return support_heads[arg[0]]

    def setSystem(self, *args, nserver):
        lhead = 0
        for arg in args:
            self.system["System"]["InkjetHead"].append(self._inkJetHeadEntry(arg))
            lhead = lhead + arg[1]
        self.system["System"]["nServer"] = nserver
        self.system["System"]["nLineHead"] = lhead

    def setServer(self, *args, svrid, ipaddr):
        nPDC = len(args)
        sve = {}
        sve["//"] = f"## Server{svrid} ##"
        sve["Master"] = True if svrid == 1 else False
        sve["IPAddress"] = ipaddr
        sve["nPDC"] = nPDC
        sve["PDC"] = []

        for pidx in range(nPDC):
            pdce = {}
            pdce["//"] = f"## PDC{pidx + 1} ##"
            pdce["nLB"] = len(args[pidx])
            pdce["LB"] = []
            pdce["IOFilterLow"] = 127
            pdce["IOFilter"] = {
                "PIO_IN": [
                    {
                        "//": "## PIO_IN1 ##",
                        "FPOL": "0xffffff",
                        "FPRSCLR": "0xffffff",
                        "HOLD": "0x000000",
                        "tFS1": "0x00000000",
                        "tFS2": "0x00000000",
                        "tFS3": "0x00000000",
                        "tFS4": "0x00000000",
                        "tFS5": "0x00000000",
                        "tFS6": "0x00000000",
                        "tFH1": "0x00000000",
                        "tFH2": "0x00000000",
                        "tFH3": "0x00000000",
                        "tFH4": "0x00000000",
                        "tFH5": "0x00000000",
                        "tFH6": "0x00000000"
                    },
                    {
                        "//": "## PIO_IN2 ##",
                        "FPOL": "0xffffff",
                        "FPRSCLR": "0xffffff",
                        "HOLD": "0x000000",
                        "tFS1": "0x00ffffff",
                        "tFS2": "0xffff0000",
                        "tFS3": "0x00000000",
                        "tFS4": "0x00000000",
                        "tFS5": "0x00000000",
                        "tFS6": "0x00000000",
                        "tFH1": "0x00000000",
                        "tFH2": "0x00000000",
                        "tFH3": "0x00000000",
                        "tFH4": "0x00000000",
                        "tFH5": "0x00000000",
                        "tFH6": "0x00000000"
                    }
                ]
            }

            for lidx in range(len(args[pidx])):
                lbe = {}
                lbe["//"] = f"## LB{lidx + 1} ##"
                lbe["nHIF"] = args[pidx][lidx][0]
                lbe["nHead"] = args[pidx][lidx][1]
                pdce["LB"].append(lbe)
            sve["PDC"].append(pdce)
        self.server["Server"].append(sve)

    def setLineHead(self,*args):
        for arg in args:
            self.linehead["LineHead"].append(
                {
                    "Color": arg[0],
                    "LBID": arg[1]
                }
            )

    def getConfig(self):
        return {**self.system, **self.server, **self.linehead}

    def save(self):
        conf = self.getConfig()
        print(json.dumps(conf, indent=2))
        with open(self.fpath, 'w') as f:
            json.dump(conf, f, indent=2)
