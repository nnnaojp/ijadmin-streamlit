import json

class DcmConfig:
    def __init__(self,fpath='/tmp/dcm.json'):
        self.fpath = fpath
        self.adjpos = {"AdjustPosition": []}
        self.fcjet = {"ForceJet": {
            "JetDropID": [],
            "JetFreq": [],
            "JetList": [],
            "JetTimer": 1
        }}
        self.idljet = {"IdleJet": {
            "JetDropID": [],
            "JetFreq": [],
            "TickleEnable": False
        }}
        self.linehead = {"LineHead": []}
        self.printer = {"Printer": []}
        self.sptjet = {"SpitJet": {
            "SwSpitMaxWidth": [],
            "SwSpitBetaWidth": [],
            "SwSpitStartX": [],
            "SwSpitBetaLength": 40,
            "SwSpitBlankLength": 5,
            "SwSpitRepeat": 3,
            "SwSpitEnable": True,
            "TickleDropID": 6,
            "TickleEnable": False
        }}
        self.system = {"System": {
            "ConfigVersion": "setup",
            "DebugDump": False,
            "DebugRaster": False,
            "EncorderBaseDivK": 4673,
            "EncorderBaseMultiK": 6222,
            "EncorderBaseSampleNum": 8,
            "HeadTempGradient": 0,
            "NOHEAD": [
                False,
                False,
                False,
                False
            ],
            "NOHIF": [
                False,
                False,
                False,
                False
            ],
            "NOPDC": [
                False,
                False,
                False,
                False
            ]
        }}

    def adjustPositionEntry(self,nlhead):
        for i in range(nlhead):
            self.adjpos["AdjustPosition"].append({
                "X": 0,
                "Y": 0
            })

    def forceJetEntry(self,drpids,freqs,nlhead):
        for drpid in drpids:
            self.fcjet["ForceJet"]["JetDropID"].append(drpid)
        for freq in freqs:
            self.fcjet["ForceJet"]["JetFreq"].append(freq)
        for i in range(nlhead):
            self.fcjet["ForceJet"]["JetList"].append({
            "Enable": False,
            "JetMask": "0xffffff"
        })


    def idleJetEntry(self,drpids,freqs):
        ijet = {
           "JetDropID": [],
           "JetFreq": [],
           "TickleEnable": False
        }
        for drpid in drpids:
            self.idljet["IdleJet"]["JetDropID"].append(drpid)
        for freq in freqs:
            self.idljet["IdleJet"]["JetFreq"].append(freq)

    def lineHeadEntry(self,*args):
        lheads = []
        for arg in args:
            lhead = {}
            lhead["Enable"] = True
            lhead["Head"] = []
            for i in range(arg[0]):
                lhead["Head"].append({
                  "HeaterEnable": False,
                  "HeaterTemp": 30,
                  "YAdjust": 0,
                  "YOffset": arg[i%2+1]
                })
            lhead["XOffset"] = 0
            lhead["YOffset"] = 0
            self.linehead["LineHead"].append(lhead)

    def printerEntry(self,*args):
        support_heads = {
          "SambaG3": {
            "EncorderPulseEdge": 0,
            "EncorderRotateDir": 0,
            "LatClockBase": 0,
            "LatClockDivK": 1,
            "LatClockFreq": 11811024,
            "LatClockMultiK": 2,
            "LatClockSampleNum": 2,
            "TriggerMode": 0,
            "TriggerPulseEdge": 1
          },
          "RC1536": {
            "EncorderPulseEdge": 0,
            "EncorderRotateDir": 0,
            "LatClockBase": 0,
            "LatClockDivK": 33797,
            "LatClockFreq": 7086614,
            "LatClockMultiK": 4500,
            "LatClockSampleNum": 2,
            "TriggerMode": 0,
            "TriggerPulseEdge": 1
          }
        }
        for arg in args:
            self.printer["Printer"].append(support_heads[arg])

    def spitJetEntry(self,maxws,betaws,startxs):
        for maxw in maxws:
            self.sptjet["SpitJet"]["SwSpitMaxWidth"].append(maxw)
        for betaw in betaws:
            self.sptjet["SpitJet"]["SwSpitBetaWidth"].append(betaw)
        for startx in startxs:
            self.sptjet["SpitJet"]["SwSpitStartX"].append(startx)

    def getConfig(self):
        return {**self.adjpos, **self.fcjet, **self.idljet,
                **self.linehead,**self.printer,**self.sptjet,
                **self.system}

    def save(self):
        conf = self.getConfig()
        print(json.dumps(conf, indent=2))
        with open(self.fpath, 'w') as f:
            json.dump(conf, f, indent=2)
