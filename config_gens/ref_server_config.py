#!/usr/bin/python3
# -*- coding: utf-8 -*-

from PySide2.QtWidgets import *
from PySide2.QtCore import Qt, QTimer
import sys,os
import shutil
import ipaddress
import threading
from concurrent.futures import ThreadPoolExecutor
from messages import UiStrings

from dcm import dcm_api
from mpsapi import mistral_api
from mistral.thrift.ttypes import *
import pings
from myapp import ProductType,PingStatus
import myapp
from remote import remote
from myconfig import MistralConfig
import mistral_json
import dcm_json
import tiff2lb_json
import fxijconfig

sys.path.append('/usr/mistral/python3.6/site-packages')

from mylogger import logger


def isIpV4(str):
    try:
        ip = ipaddress.IPv4Address(str)
        return True
    except Exception as e:
        return False

class AlignDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super(AlignDelegate,self).initStyleOption(option,index)
        option.displayAlignment = Qt.AlignCenter

class ServerConfigWidget(QWidget):
    def __init__(self):
        super().__init__()

        vbox = QVBoxLayout()
        self.count = 0;
        self.systemCombo = QComboBox()
        for i in range(len(myapp.serverSet.systemList)):
            self.systemCombo.addItem(myapp.serverSet.systemList[i])
        self.systemCombo.currentIndexChanged.connect(self.updateServerTable)

        hbox1 = QHBoxLayout()
        hbox1.addWidget(QLabel("ヘッド構成："))
        hbox1.addWidget(self.systemCombo)

        self.serverTable = QTableWidget();
        self.serverTable.setColumnCount(3);
        self.serverTable.setRowCount(myapp.MAX_SERVERS);
        delegate = AlignDelegate(self.serverTable)
        for i in range(3):
            self.serverTable.setItemDelegateForColumn(i,delegate)

        hlbl = ['サーバー','IPアドレス','通信状態']
        self.serverTable.setHorizontalHeaderLabels(hlbl)
        hdr = self.serverTable.horizontalHeader()
        self.serverTable.setColumnWidth(0,100)
        self.serverTable.setColumnWidth(1,300)
        hdr.setSectionResizeMode(2,QHeaderView.Stretch)

        for i in range(myapp.MAX_SERVERS):
            self.serverTable.setItem(i, 0, QTableWidgetItem(' '))
            self.serverTable.setItem(i, 1, QTableWidgetItem(' '))
            self.serverTable.setItem(i, 2, QTableWidgetItem(' '))

        self.serverTable.setSelectionMode(QAbstractItemView.SingleSelection)
        self.serverTable.itemChanged.connect(self.itemChanged)

        vbox1 = QVBoxLayout()
        hbox2 = QHBoxLayout()
        hbox2.addWidget(QLabel("システム状態："))
        self.statusEdit = QLineEdit("")
        self.statusEdit.setReadOnly(True)
        hbox2.addWidget(self.statusEdit)
        self.versionText = QPlainTextEdit(self)
        self.versionText.setReadOnly(True)

        vbox1.addLayout(hbox2)
        vbox1.addWidget(self.versionText)

        btn = QPushButton("通信確認")
        btn.clicked.connect(self.updateDisplay)
        self.pbtnExec = QPushButton("コンフィグ実行")
        self.pbtnExec.clicked.connect(self.askExecConfig)
        self.pbtnExec.setEnabled(False)
        hbox3 = QHBoxLayout()
        hbox3.addWidget(QLabel())
        hbox3.addWidget(btn)
        hbox3.addWidget(self.pbtnExec)

        self.pbar = QProgressBar()
        self.pbar.setMaximum(100)
        self.pbar.setFixedHeight(10)
        self.progress = 0

        vbox.addLayout(hbox1)
        vbox.addWidget(self.serverTable)
        vbox.addLayout(vbox1)
        vbox.addLayout(hbox3)
        vbox.addWidget(self.pbar)

        self.systemCombo.setCurrentIndex(myapp.serverSet.systemId-1)
        self.updateServerTable(myapp.serverSet.systemId-1)
        self.setLayout(vbox)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateProgress)

    def itemChanged(self,item):
        row = item.row()
        col = item.column()
        if col == 1:
            if isIpV4(self.serverTable.item(row,1).text()):
                myapp.serverSet.svrlist[row].address = self.serverTable.item(row, 1).text()
            else:
                myapp.serverSet.svrlist[row].address = ''
                self.serverTable.item(row,1).setText('-')
            myapp.serverSet.svrlist[row].pingStatus = PingStatus.YET
            #logger.info(f'IP: {myapp.serverSet.svrlist[row].address}')

    def updateServerTable(self,idx):
        myapp.serverSet.setProduct(ProductType(idx+1).value)
        for i in range(myapp.MAX_SERVERS):
            if i < myapp.serverSet.numServers:
                self.serverTable.item(i, 0).setText(myapp.serverSet.svrlist[i].colors)
                self.serverTable.item(i, 1).setText(myapp.serverSet.svrlist[i].address)
                self.serverTable.item(i, 2).setText(myapp.serverSet.getPingStatus(i))
                self.serverTable.item(i, 2).setBackground(Qt.white)
            else:
                self.serverTable.item(i,0).setText('-')
                self.serverTable.item(i,1).setText('-')
                self.serverTable.item(i,2).setText('-')
                self.serverTable.item(i, 2).setBackground(Qt.white)

    def updateDisplay(self):
        svlst = []
        for i in range(myapp.serverSet.numServers):
            svlst.append(myapp.serverSet.svrlist[i].address)
        if len(svlst) != len(set(svlst)):
            QMessageBox.information(self,UiStrings.DlgCritical,
                                    UiStrings.ErrIPAddress,QMessageBox.Yes)
            return
        self.checkServersAlive()
        self.showSystemStatus()
        # for i in range(myapp.serverSet.numServers):
        #     if myapp.serverSet.svrlist[i].pingStatus != PingStatus.OK:
        #         QMessageBox.information(self,UiStrings.DlgInfo,
        #                                 UiStrings.InfoPingServers,
        #                                 QMessageBox.Yes)
        #         break

    def checkServersAlive(self):
        self.pbar.setValue(30)
        self.timer.start(1000)
        with ThreadPoolExecutor(1) as tpe:
            future = tpe.submit(self.pingServers)
        self.progress = 100
        print(future.result())
        for i in range(myapp.serverSet.numServers):
            self.serverTable.item(i, 2).setText(myapp.serverSet.getPingStatus(i))
            if myapp.serverSet.svrlist[i].pingStatus == PingStatus.OK:
                self.serverTable.item(i, 2).setBackground(Qt.green)
            else:
                self.serverTable.item(i, 2).setBackground(Qt.red)

    def pingServers(self):
        print('ping servers...')
        p = pings.Ping(quiet=False)
        for i in range(myapp.serverSet.numServers):
            sv = myapp.serverSet.svrlist[i].address
            if len(sv):
                res = p.ping(sv)
                if res.is_reached():
                    myapp.serverSet.svrlist[i].pingStatus = PingStatus.OK
                else:
                    myapp.serverSet.svrlist[i].pingStatus = PingStatus.NG
            else:
                myapp.serverSet.svrlist[i].pingStatus = PingStatus.NG
        print('ping servers done')
        return True

    def updateProgress(self):
        #print('zzz')
        if self.progress >= 0:
            self.pbar.setValue(self.progress)
            if self.progress == 100:
                self.progress = 0
            elif self.progress == 0:
                self.pbar.reset()
                self.timer.stop()

    def showSystemStatus(self):
        # if myapp.serverSet.svrlist[0].pingStatus != PingStatus.OK:
        #     logger.error(f'master not responding!,{myapp.serverSet.svrlist[0].address}')
        #     self.statusEdit.setText('サーバー応答エラー')
        #     self.versionText.clea        #     return
        if not(myapp.serverSet.isMasetr()):
            self.statusEdit.setText("マスターサーバーではありません。")
            self.versionText.clear()
            self.pbtnExec.setEnabled(False)
        else:
            try:
                m = mistral_api()
                m._client_setup(myapp.serverSet.svrlist[0].address)
                sinfo = m._command_sysinfo()

                d = dcm_api(myapp.serverSet.svrlist[0].address)
                sts = d.getPrinterStatus()
                vers = d.getDeviceVersion()

                self.statusEdit.setText(self.to_status_str(sts))
                vers_str = ''
                svrid = 1
                for sv in sinfo.server:
                    vers_str += f'●Server{svrid} - {sv.address}\n'
                    vers_str += f'・Mistral Version: {sv.version}\n'
                    pdcid = 1
                    for pdc in vers.server[svrid-1].pdc:
                        vers_str += f'・PDC{pdcid} Version: {pdc.pdc}\n'
                        lbid = 1
                        for lb in pdc.lb:
                            vers_str += f'・(LB{lbid})HIF Version: '
                            for hif in lb.hif:
                                vers_str += f'{hif} '
                            vers_str += '\n'
                            lbid = lbid+1
                        pdcid = pdcid+1
                    vers_str += '\n'
                    svrid = svrid+1
                self.versionText.setPlainText(vers_str)

            except APIException as ex:
                self.versionText.clear()
                self.statusEdit.setText('APIエラーが発生しました。')
                logger.error(ex.args)
            except TException as ex:
                self.versionText.clear()
                self.statusEdit.setText('DCMが起動されていません。')
                logger.error(ex.args)
            except Exception as ex:
                self.versionText.clear()
                self.statusEdit.setText('例外エラーが発生しました。')
                logger.error(ex.args)
            finally:
                if m.transport.isOpen():
                    m.transport.close()
                self.pbtnExec.setEnabled(True)

    def to_status_str(self, sts, d={0: '利用可能',
                                    1: '応答待ち',
                                    2: '初期化中',
                                    3: '初期化中',
                                    4: 'データ転送中',
                                    5: 'トリガ待ち',
                                    6: '印刷中',
                                    7: 'エラー',
                                    8: 'オフライン',
                                    9: '強制吐出中'}):
        status_str = d
        if sts.status in status_str:
            rets = status_str[sts.status]
            if sts.status == 7:
                rets = self.to_error_str(sts.error.errcode)
                rets += '  (SERVER['+str(sts.error.svrid)+ \
                        '],PDC['+str(sts.error.pdcid)+ \
                        '],HIF['+str(sts.error.hifid)+ \
                        '],HEAD['+str(sts.error.headid)+'])'
            return rets
        else:
            return "-"

    def to_error_str(self,ecode):
        error_str = {0:'利用可能',
                     1:'応答無し',
                     2:'PDCIFエラー',
                     3:'HIFエラー',
                     4:'リンクエラー',
                     5:'HIFデータエラー',
                     6:'ヘッドエラー',
                     7:'ヘッド温度エラー',
                     8:'ヘッドヒーター制御中',
                     9:'PLC電源オフ',
                     10:'電源ユニットエラー',
                     11:'UPSエラー',
                     12:'シャットダウン信号検知',
                     13:'インク無し',
                     14:'トリガーロス',
                     15:'HIF基盤温度エラー',
                     16:'HIF基盤温度ワーニング',
                     17:'PDCライン番号異常',
                     18:'HIFメモリテストエラー',
                     19:'PDC光通信エラー',
                     20:'HIF光通信エラー',
                     21:'カスケード接続初期化エラー',
                     22:'高速シリアルトランシーバー受信エラー',
                     23:'高速シリアルトランシーバーエラー',
                     24:'光トランシーバーデバイスエラー',
                     25:'PDC-HIF通信CRCエラー',
                     26:'PDC-HIF通信印刷バッファオーバーフロー',
                     27:'PDC-HIF通信レジスタアクセスコマンドエラー',
                     28:'ヘッド1接続エラー',
                     29:'ヘッド2接続エラー',
                     30:'ヘッド3接続エラー',
                     31:'ヘッド温度ワーニング',
                     32:'ヘッドCUK光通信エラー',
                     33:'ヘッドアンプDC光通信エラー',
                     34:'ヘッドアンプAC光通信エラー',
                     35:'ヘッド3.3V Float光通信エラー',
                     100:'キャンセル',
                     101:'印刷処理中のため変更できません',
                     102:'コンフィグエラー',
                     103:'メモリコンフィグエラー',
                     104:'ソケット通信エラー',
                     105:'波形データ内容エラー(印字波形)',
                     106:'波形データ内容エラー(ティックル波形)',
                     107:'波形データメモリエラー',
                     108:'波形データ設定エラー',
                     109:'ヘッド駆動オペアンプ異常',
                     110:'ヘッド駆動電圧制御エラー',
                     111:'印刷準備エラー',
                     112:'印刷データ転送エラー',
                     119:'システムエラー',
                     200:'連続印刷条件エラー(画像ビット数不一致)',
                     201:'連続印刷条件エラー(画像解像度不一致)',
                     202:'連続印刷条件エラー(トリガーモード不一致)',
                     203:'連続印刷条件エラー(波形データ不一致)',
        }
        if ecode in error_str:
            return error_str[ecode]
        else:
            return "unknown error"


    def askExecConfig(self):
            rc = QMessageBox.question(self,UiStrings.DlgQuestion,
                                      UiStrings.AskServerConfig,
                                      QMessageBox.Ok,QMessageBox.Cancel)
            if rc == QMessageBox.Ok:
                self.execConfig()

    def execConfig(self):
        print(self.systemCombo.currentText())
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

        print(myapp.serverSet.systemId)
        mc = mistral_json.MistralConfig()
        dc = dcm_json.DcmConfig()
        tc = tiff2lb_json.Tiff2lb()
        svrlst = [myapp.serverSet.svrlist[i].address
                  for i in range(myapp.serverSet.numServers)]
        configFunc[myapp.serverSet.systemId-1](mc,dc,tc,svrlst)

        # copy config files
        for i in range(myapp.serverSet.numServers):
            try:
                if i == 0:
                    for f in cfgfile:
                        shutil.copy(tmpdir+f,confdir)
                    for f in etcfile:
                        shutil.copy(tmpdir+f,etcdir)
                else:
                    # master server copies config to slave servers
                    #if myapp.serverSet.myip == myapp.serverSet.svrlist[0].address:
                    if myapp.serverSet.isMasetr():
                        r = remote(myapp.serverSet.svrlist[i].address,user,passwd)
                        for f in cfgfile:
                            r.rootcopy(confdir,tmpdir+f)
                        for f in etcfile:
                            r.rootcopy(etcdir,tmpdir+f)

            except Exception as e:
                logger.error('copy failed!');
                QMessageBox.critical(self,UiStrings.DlgCritical,
                                     UiStrings.ErrException,
                                     QMessageBox.Yes)
                return

        QMessageBox.information(self, UiStrings.DlgInfo,
                                UiStrings.InfoConfigDone, QMessageBox.Yes)

    def execConfigOLDVERS(self):
        print(self.systemCombo.currentText())
        user = 'ijadmin'
        passwd = 'ijadmin'
        tmpdir = '/tmp/'
        confdir = '/usr/mistral/conf'
        etcdir = '/usr/mistral/etc'
        srcCfgDir = f'/boot/archive/config/{myapp.serverSet.systemId}/conf/'
        srcEtcDir = f'/boot/archive/config/{myapp.serverSet.systemId}/etc/'
        cfgfile = ['mistral.json','dcm.json']
        etcfile = ['tiff2lb.json','mpsd.json','spooler.json']
        print(srcCfgDir,srcEtcDir)

        # overwrite the server ip in the /tmp/mistral.json
        for f in cfgfile:
            sf = f'{srcCfgDir}{f}'
            df = f'{tmpdir}{f}'
            try:
                shutil.copyfile(sf,df)
                if f == 'mistral.json':
                    wkconf = MistralConfig(df)
                    for i in range(myapp.serverSet.numServers):
                        wkconf.setIPAddress(i,myapp.serverSet.svrlist[i].address)
                    wkconf.save()
            except Exception as e:
                logger.error('overwrite ip failed!');
                QMessageBox.critical(self,UiStrings.DlgCritical,
                                     UiStrings.ErrException,
                                     QMessageBox.Yes)
                return

        # copy config files
        for i in range(myapp.serverSet.numServers):
            try:
                if i == 0:
                    for f in cfgfile:
                        shutil.copy(tmpdir+f,confdir)
                    for f in etcfile:
                        shutil.copy(srcEtcDir+f,etcdir)
                else:
                    # only master server can copy files to other ones
                    #if myapp.serverSet.myip == myapp.serverSet.svrlist[0].address:
                    if myapp.serverSet.isMasetr():
                        r = remote(myapp.serverSet.svrlist[i].address,user,passwd)
                        for f in cfgfile:
                            r.rootcopy(confdir,tmpdir+f)
                        for f in etcfile:
                            r.rootcopy(etcdir,srcEtcDir+f)
                    else:
                        logger.info('update only master config...')

            except Exception as e:
                logger.error('copy failed!');
                QMessageBox.critical(self,UiStrings.DlgCritical,
                                     UiStrings.ErrException,
                                     QMessageBox.Yes)
                return

        QMessageBox.information(self,UiStrings.DlgInfo,
                             UiStrings.InfoDone,QMessageBox.Yes)
