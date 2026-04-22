import json

class DncConfig:
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

    def setMaxNozzleNumber(self, num):
        self.max_nozzle_number["MaxNozzleNumber"] = num

    def getConfig(self):
        return {
            **self.nozzle_data,
            **self.defect_ratio,
            **self.lut,
            **self.mask_dark,
            **self.mask_light,
            **self.max_nozzle_number,
            **self.threshold,
            **self.tone_threshold
        }

    def save(self):
        conf = self.getConfig()
        print(json.dumps(conf, indent=2))
        with open(self.fpath[0], 'w') as f:
            json.dump(conf, f, indent=2)
        with open(self.fpath[1], 'w') as f:
            json.dump(conf, f, indent=2)
