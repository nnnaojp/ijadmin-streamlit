import config_gens.mistral_json as mistral_json
import config_gens.dcm_json as dcm_json
import config_gens.tiff2lb_json as tiff2lb_json
import config_gens.dnc_json as dnc_json

def setup1_Type500_RC1536_40mpm(mc, dc, tc, dnc, iparry):
    # setup mistral.json
    mc.setSystem(("SambaG3", 4), ("RC1536", 1), nserver=1)
    mc.setServer(
        [(4, 12), (4, 12), (4, 12), (4, 12)],  # PDC1(nHIF,nHEAD)
        [(3, 5)],  # PDC2(nHIF,nHEAD)
        svrid=1, ipaddr=iparry[0])
    mc.setLineHead(
        ("black", [111]),
        ("cyan", [112]),
        ("magenta", [113]),
        ("yellow", [114]),
        ("white", [121]),
    )
    mc.save()

    # setup dcm.json
    dc.adjustPositionEntry(nlhead=5)
    dc.forceJetEntry(drpids=(1, 1), freqs=(2000, 2000), nlhead=5)
    dc.idleJetEntry(drpids=(0, 0), freqs=(2000, 2000))
    dc.lineHeadEntry((12, 10660, 10660),
                     (12, 10660, 10660),
                     (12, 10660, 10660),
                     (12, 10660, 10660),
                     (5, 1500, 86500))
    dc.printerEntry("SambaG3", "RC1536")
    dc.spitJetEntry(maxws=(516, 516),
                    betaws=(516, 516),
                    startxs=(-1, -1))
    dc.save()

    # setup tiff2lb.json
    tc.setHeadType("Dimatix_SambaG3Lx12","SII_RC1536x5")
    tc.setLineHead(
        ("black", "K", 1,          # color,ab,htype,
         ((1, 1, -128, 24704),)),  # svno,lbno,offset,width
        ("cyan", "C", 1,
         ((1, 2, -128, 24704),)),
        ("magenta", "M", 1,
         ((1, 3, -128, 24704),)),
        ("yellow", "Y", 1,
         ((1, 4, -128, 24704),)),
        ("white", "W", 2,
         ((1, 5, 0, 7680),)),
    )
    tc.save()

def setup2_Type500_RC1536x2_40mpm(mc, dc, tc, dnc, iparry):
    # setup mistral.json
    mc.setSystem(("SambaG3", 4), ("RC1536", 2), nserver=1)
    mc.setServer(
        [(4, 12), (4, 12), (4, 12), (4, 12)],  # PDC1(nHIF,nHEAD)
        [(3, 5), (3, 5)],  # PDC2(nHIF,nHEAD)
        svrid=1, ipaddr=iparry[0])
    mc.setLineHead(
        ("black", [111]),
        ("cyan", [112]),
        ("magenta", [113]),
        ("yellow", [114]),
        ("white1", [121]),
        ("white2", [122]),
    )
    mc.save()

    # setup dcm.json
    dc.adjustPositionEntry(nlhead=6)
    dc.forceJetEntry(drpids=(1, 1), freqs=(2000, 2000), nlhead=6)
    dc.idleJetEntry(drpids=(0, 0), freqs=(2000, 2000))
    dc.lineHeadEntry((12, 10660, 10660),
                     (12, 10660, 10660),
                     (12, 10660, 10660),
                     (12, 10660, 10660),
                     (5, 1500, 86500),
                     (5, 1500, 86500),
                     )
    dc.printerEntry("SambaG3", "RC1536")
    dc.spitJetEntry(maxws=(516, 516),
                    betaws=(516, 516),
                    startxs=(-1, -1))
    dc.save()

    # setup tiff2lb.json
    tc.setHeadType("Dimatix_SambaG3Lx12","SII_RC1536x5")
    tc.setLineHead(
        ("black", "K", 1,          # color,ab,htype,
         ((1, 1, -128, 24704),)),  # svno,lbno,offset,width
        ("cyan", "C", 1,
         ((1, 2, -128, 24704),)),
        ("magenta", "M", 1,
         ((1, 3, -128, 24704),)),
        ("yellow", "Y", 1,
         ((1, 4, -128, 24704),)),
        ("white", "W1", 2,
         ((1, 5, 0, 7680),)),
        ("white", "W2", 2,
         ((1, 6, 0, 7680),)),
    )
    tc.save()

def setup3_Type500_SambaG5Lx2_40mpm(mc, dc, tc, dnc, iparry):
    # setup mistral.json
    mc.setSystem(("SambaG3", 6), nserver=1)
    mc.setServer(
        [(4, 12), (4, 12), (4, 12), (4, 12)],  # PDC1(nHIF,nHEAD)
        [(4, 12), (4, 12)],  # PDC2(nHIF,nHEAD)
        svrid=1, ipaddr=iparry[0])
    mc.setLineHead(
        ("black", [111]),
        ("cyan", [112]),
        ("magenta", [113]),
        ("yellow", [114]),
        ("white1", [121]),
        ("white2", [122]),
    )
    mc.save()

    # setup dcm.json
    dc.adjustPositionEntry(nlhead=6)
    dc.forceJetEntry(drpids=(1, 0), freqs=(2000, 0), nlhead=6)
    dc.idleJetEntry(drpids=(0, 0), freqs=(2000, 0))
    dc.lineHeadEntry((12, 10660, 10660),
                     (12, 10660, 10660),
                     (12, 10660, 10660),
                     (12, 10660, 10660),
                     (12, 10660, 10660),
                     (12, 10660, 10660),
                     )
    dc.printerEntry("SambaG3")
    dc.spitJetEntry(maxws=(516, 0),
                    betaws=(516, 0),
                    startxs=(-1, 0))
    dc.save()

    # setup tiff2lb.json
    tc.setHeadType("Dimatix_SambaG3Lx12")
    tc.setLineHead(
        ("black", "K", 1,          # color,ab,htype,
         ((1, 1, -128, 24704),)),  # svno,lbno,offset,width
        ("cyan", "C", 1,
         ((1, 2, -128, 24704),)),
        ("magenta", "M", 1,
         ((1, 3, -128, 24704),)),
        ("yellow", "Y", 1,
         ((1, 4, -128, 24704),)),
        ("white", "W1", 1,
         ((1, 5, -128, 24704),)),
        ("white", "W2", 1,
         ((1, 6, -128, 24704),)),
    )
    tc.save()

def setup4_Type1000_RC1536_40mpm(mc, dc, tc, dnc, iparry):
    # setup mistral.json
    mc.setSystem(("SambaG3", 4), ("RC1536", 1), nserver=2)
    mc.setServer(
        [(4, 12), (4, 12), (4, 12), (4, 12)],  # PDC1(nHIF,nHEAD)
        svrid=1, ipaddr=iparry[0])
    mc.setServer(
        [(4, 12), (4, 12), (4, 12), (4, 12)],  # PDC1(nHIF,nHEAD)
        [(5, 10)],  # PDC2(nHIF,nHEAD)
        svrid=2, ipaddr=iparry[1])
    mc.setLineHead(
        ("black", [111, 112]),
        ("cyan", [113, 114]),
        ("magenta", [211, 212]),
        ("yellow", [213, 214]),
        ("white", [221]),
    )
    mc.save()

    # setup dcm.json
    dc.adjustPositionEntry(nlhead=5)
    dc.forceJetEntry(drpids=(1, 1), freqs=(2000, 2000), nlhead=5)
    dc.idleJetEntry(drpids=(0, 0), freqs=(2000, 2000))
    dc.lineHeadEntry((24, 10660, 10660),
                     (24, 10660, 10660),
                     (24, 10660, 10660),
                     (24, 10660, 10660),
                     (10, 1500, 86500),
                     )
    dc.printerEntry("SambaG3", "RC1536")
    dc.spitJetEntry(maxws=(1032, 1080),
                    betaws=(1000, 1000),
                    startxs=(-1, -1))
    dc.save()

    # setup tiff2lb.json
    tc.setHeadType("Dimatix_SambaG3Lx24", "SII_RC1536x10")
    tc.setLineHead(
        ("black", "K", 1,          # color,ab,htype,
         ((1, 1, -128, 24704),     # svno,lbno,offset,width
          (1, 2, 24448, 24704),
          )),
        ("cyan", "C", 1,
         ((1, 3, -128, 24704),
          (1, 4, 24448, 24704),
          )),
        ("magenta", "M", 1,
         ((2, 1, -128, 24704),
          (2, 2, 24448, 24704),
          )),
        ("yellow", "Y", 1,
         ((2, 3, -128, 24704),
          (2, 4, 24448, 24704),
          )),
        ("white", "W", 2,
         ((2, 5, 0, 15360),)),
    )
    tc.save()

def setup5_Type1000_RC1536x2_40mpm(mc, dc, tc, dnc, iparry):
    # setup mistral.json
    mc.setSystem(("SambaG3", 4), ("RC1536", 2), nserver=2)
    mc.setServer(
        [(4, 12), (4, 12), (4, 12), (4, 12)],  # PDC1(nHIF,nHEAD)
        svrid=1, ipaddr=iparry[0])
    mc.setServer(
        [(4, 12), (4, 12), (4, 12), (4, 12)],  # PDC1(nHIF,nHEAD)
        [(5, 10), (5, 10)],  # PDC2(nHIF,nHEAD)
        svrid=2, ipaddr=iparry[1])
    mc.setLineHead(
        ("black", [111, 112]),
        ("cyan", [113, 114]),
        ("magenta", [211, 212]),
        ("yellow", [213, 214]),
        ("white1", [221]),
        ("white2", [222]),
    )
    mc.save()

    # setup dcm.json
    dc.adjustPositionEntry(nlhead=6)
    dc.forceJetEntry(drpids=(1, 1), freqs=(2000, 2000), nlhead=6)
    dc.idleJetEntry(drpids=(0, 0), freqs=(2000, 2000))
    dc.lineHeadEntry((24, 10660, 10660),
                     (24, 10660, 10660),
                     (24, 10660, 10660),
                     (24, 10660, 10660),
                     (10, 1500, 86500),
                     (10, 1500, 86500),
                     )
    dc.printerEntry("SambaG3", "RC1536")
    dc.spitJetEntry(maxws=(1032, 1080),
                    betaws=(1000, 1000),
                    startxs=(-1, -1))
    dc.save()

    # setup tiff2lb.json
    tc.setHeadType("Dimatix_SambaG3Lx24", "SII_RC1536x10")
    tc.setLineHead(
        ("black", "K", 1,          # color,ab,htype,
         ((1, 1, -128, 24704),     # svno,lbno,offset,width
          (1, 2, 24448, 24704),
          )),
        ("cyan", "C", 1,
         ((1, 3, -128, 24704),
          (1, 4, 24448, 24704),
          )),
        ("magenta", "M", 1,
         ((2, 1, -128, 24704),
          (2, 2, 24448, 24704),
          )),
        ("yellow", "Y", 1,
         ((2, 3, -128, 24704),
          (2, 4, 24448, 24704),
          )),
        ("white", "W1", 2,
         ((2, 5, 0, 15360),)),
        ("white", "W2", 2,
         ((2, 6, 0, 15360),)),
    )
    tc.save()

def setup6_Type1000_SambaG5Lx2_30mpm(mc, dc, tc, dnc, iparry):
    # setup mistral.json
    mc.setSystem(("SambaG3", 6), nserver=2)
    mc.setServer(
        [(4, 12), (4, 12), (4, 12), (4, 12)],  # PDC1(nHIF,nHEAD)
        svrid=1, ipaddr=iparry[0])
    mc.setServer(
        [(4, 12), (4, 12), (4, 12), (4, 12)],  # PDC1(nHIF,nHEAD)
        [(4, 12), (4, 12), (4, 12), (4, 12)],  # PDC2(nHIF,nHEAD)
        svrid=2, ipaddr=iparry[1])

    mc.setLineHead(
        ("black", [111,112]),
        ("cyan", [113,114]),
        ("magenta", [211,212]),
        ("yellow", [213,214]),
        ("white1", [221,222]),
        ("white2", [223,224]),
    )
    mc.save()

    # setup dcm.json
    dc.adjustPositionEntry(nlhead=6)
    dc.forceJetEntry(drpids=(1, 1), freqs=(2000, 2000), nlhead=6)
    dc.idleJetEntry(drpids=(0, 0), freqs=(2000, 2000))
    dc.lineHeadEntry((24, 10660, 10660),
                     (24, 10660, 10660),
                     (24, 10660, 10660),
                     (24, 10660, 10660),
                     (24, 10660, 10660),
                     (24, 10660, 10660),
                     )
    dc.printerEntry("SambaG3")
    dc.spitJetEntry(maxws=(1032, 0),
                    betaws=(1000, 0),
                    startxs=(-1, 0))
    dc.save()

    # setup tiff2lb.json
    tc.setHeadType("Dimatix_SambaG3Lx24")
    tc.setLineHead(
        ("black", "K", 1,          # color,ab,htype,
         ((1, 1, -128, 24704),     # svno,lbno,offset,width
          (1, 2, 24448, 24704),
          )),
        ("cyan", "C", 1,
         ((1, 3, -128, 24704),
          (1, 4, 24448, 24704),
          )),
        ("magenta", "M", 1,
         ((2, 1, -128, 24704),
          (2, 2, 24448, 24704),
          )),
        ("yellow", "Y", 1,
         ((2, 3, -128, 24704),
          (2, 4, 24448, 24704),
          )),
        ("white", "W1", 1,
         ((2, 5, -128, 24704),
          (2, 6, 24448, 24704),
          )),
        ("white", "W2", 1,
         ((2, 7, -128, 24704),
          (2, 8, 24448, 24704),
          )),
    )
    tc.save()

def setup7_Type1000_SambaG5Lx2_50mpm(mc, dc, tc, dnc, iparry):
    # setup mistral.json
    mc.setSystem(("SambaG3", 6), nserver=3)
    mc.setServer(
        [(4, 12), (4, 12), (4, 12), (4, 12)],  # PDC1(nHIF,nHEAD)
        svrid=1, ipaddr=iparry[0])
    mc.setServer(
        [(4, 12), (4, 12), (4, 12), (4, 12)],  # PDC1(nHIF,nHEAD)
        svrid=2, ipaddr=iparry[1])
    mc.setServer(
        [(4, 12), (4, 12), (4, 12), (4, 12)],  # PDC1(nHIF,nHEAD)
        svrid=3, ipaddr=iparry[2])

    mc.setLineHead(
        ("black", [111,112]),
        ("cyan", [113,114]),
        ("magenta", [211,212]),
        ("yellow", [213,214]),
        ("white1", [311,312]),
        ("white2", [313,314]),
    )
    mc.save()

    # setup dcm.json
    dc.adjustPositionEntry(nlhead=6)
    dc.forceJetEntry(drpids=(1, 1), freqs=(2000, 2000), nlhead=6)
    dc.idleJetEntry(drpids=(0, 0), freqs=(2000, 2000))
    dc.lineHeadEntry((24, 10660, 10660),
                     (24, 10660, 10660),
                     (24, 10660, 10660),
                     (24, 10660, 10660),
                     (24, 10660, 10660),
                     (24, 10660, 10660),
                     )
    dc.printerEntry("SambaG3")
    dc.spitJetEntry(maxws=(1032, 0),
                    betaws=(1000, 0),
                    startxs=(-1, 0))
    dc.save()

    # setup tiff2lb.json
    tc.setHeadType("Dimatix_SambaG3Lx24")
    tc.setLineHead(
        ("black", "K", 1,          # color,ab,htype,
         ((1, 1, -128, 24704),     # svno,lbno,offset,width
          (1, 2, 24448, 24704),
          )),
        ("cyan", "C", 1,
         ((1, 3, -128, 24704),
          (1, 4, 24448, 24704),
          )),
        ("magenta", "M", 1,
         ((2, 1, -128, 24704),
          (2, 2, 24448, 24704),
          )),
        ("yellow", "Y", 1,
         ((2, 3, -128, 24704),
          (2, 4, 24448, 24704),
          )),
        ("white", "W1", 1,
         ((3, 1, -128, 24704),
          (3, 2, 24448, 24704),
          )),
        ("white", "W2", 1,
         ((3, 3, -128, 24704),
          (3, 4, 24448, 24704),
          )),
    )
    tc.save()

if __name__ == '__main__':
    mc = mistral_json.MistralConfig()
    dc = dcm_json.DcmConfig()
    tc = tiff2lb_json.Tiff2lb()
    dnc = dnc_json.MistralConfig()
    # setup1_Type500_RC1536_40mpm(mc, dc, tc, ('10.20.14.106'))
    setup2_Type500_RC1536x2_40mpm(mc, dc, tc, dnc, ('10.20.14.106'))
    # setup3_Type500_SambaG5Lx2_40mpm(mc, dc, tc, ('10.20.14.106'))
    #setup4_Type1000_RC1536_40mpm(mc, dc, tc, ('10.20.14.106', '10.20.14.105'))
    # setup5_Type1000_RC1536x2_40mpm(mc, dc, tc,('10.20.14.106', '10.20.14.105'))
    # setup6_Type1000_SambaG5Lx2_30mpm(mc, dc, tc,('10.20.14.106', '10.20.14.105'))
    #setup7_Type1000_SambaG5Lx2_50mpm(mc, dc, tc,('10.20.14.106', '10.20.14.105','10.20.14.107'))
