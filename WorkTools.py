# -*- coding: utf-8 -*-
import wx
import re
import os
import ImageGrab
import time
import urllib
import json
import base64
import socket
import struct
import threading

'''
<Introduction>
——————————————————————————————————————————
为工作之便开发的常用工具
1.StatFilter(日志过滤)：通过正则匹配获取大量日志中自己需要的部分
2.ScreenShot(定时截图)：定时自动截取储存屏幕截图
3.Request(解析获取数据)：专门解析有关退弹后台返回的一段Json数据
4.GetPacket(数据包截取分析): 获取登陆器有关的数据包，然后根据自定义Json配置文件解析截取到的数据包，更精确定位登陆器各处问题


<Installation>
——————————————————————————————————————————
Python 2.7.4
PIL 1.1.7                    （图形库）
wxPython2.8-win32/64-unicode （界面库）


<Undo>
——————————————————————————————————————————
*自动化部署更新包
*压力测试框架

'''
class PageOne(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, pos=(0, 0))

        self.regf = ''  # 储存外部输入正则表达式
        self.Before_Data = ''  # 储存外部输入待处理数据
        self.After_Data = []  # 分割后的数据 (元组)
        self.Result = []  # 储存最后的结果
        self.flag = 0
        self.InitUI()

    def InitUI(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(self, label=u'正则表达式：')
        hbox1.Add(st1, flag=wx.RIGHT, border=8)

        tc = wx.TextCtrl(self)
        hbox1.Add(tc, proportion=1)
        vbox.Add(hbox1, flag=wx.EXPAND |
                 wx.LEFT | wx.RIGHT | wx.TOP, border=10)
        vbox.Add((-1, 10))

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(self, label=u'待处理数据：')
        hbox3.Add(st2, flag=wx.RIGHT, border=8)

        tc2 = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        hbox3.Add(tc2, proportion=1, flag=wx.EXPAND)
        vbox.Add(hbox3, proportion=1, flag=wx.LEFT | wx.RIGHT | wx.EXPAND,
                 border=10)
        vbox.Add((-1, 25))

        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        cb1 = wx.CheckBox(self, label=u'逆序输出')
        hbox4.Add(cb1, flag=wx.RIGHT | wx.EXPAND, border=8)
        btn = wx.Button(self, label=u'提交数据', size=(90, 30))
        hbox4.Add(btn)
        vbox.Add(hbox4, flag=wx.ALIGN_RIGHT | wx.RIGHT, border=8)
        vbox.Add((-1, 25))

        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.aft_str = wx.StaticText(self, label=u'已处理数据：')
        hbox5.Add(self.aft_str, flag=wx.RIGHT, border=8)

        self.tc3 = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        hbox5.Add(self.tc3, proportion=1, flag=wx.EXPAND)
        vbox.Add(hbox5, proportion=1, flag=wx.LEFT | wx.RIGHT | wx.EXPAND,
                 border=10)
        vbox.Add((-1, 25))
        self.SetSizer(vbox)

        # bind the events to handlers
        self.Bind(wx.EVT_TEXT, self.regformat, tc)
        #    self.Bind(wx.EVT_CHAR,self.onkeypress,tc)
        self.Bind(wx.EVT_TEXT, self.beforedata, tc2)
        #    self.Bind(wx.EVT_CHAR,self.onkeypress,tc)
        self.Bind(wx.EVT_CHECKBOX, self.reverse, cb1)
        self.Bind(wx.EVT_BUTTON, self.submit, btn)

    def regformat(self, event):
        self.regf = event.GetString()
        #       self.tc3.AppendText(u'正则表达式:%s \n' % self.regf)

    def beforedata(self, event):
        self.Before_Data = event.GetString()
    #        self.tc3.AppendText('Before Data:%s \n' % self.Before_Data)

    def reverse(self, event):
        self.flag = event.Checked()

    def submit(self, event):
        # 初始化变量，以免覆盖追加
        del self.After_Data[:]
        del self.Result[:]
        self.tc3.Clear()

        self.After_Data = self.Before_Data.split('\n')
        p = re.compile(self.regf)

        for x in self.After_Data:
            m = p.match(x)
            if m:
                self.Result.append(m.group())
        size = len(self.Result)
        if self.flag == 0:
            for element in self.Result:
                self.tc3.AppendText(element)
                self.tc3.AppendText('\n')
        else:
            for element in range(size-1, -1, -1):
                self.tc3.AppendText(self.Result[element])
                self.tc3.AppendText('\n')


class PageTwo(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.time_Itv = ''  # 时间间隔
        self.name_pre = u'防沉迷'  # 储存文件前缀名
        self.InitUI()

    def InitUI(self):
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.filepath_tc = wx.TextCtrl(self)
        choosepath_button = wx.Button(self, label=u'选择保存路径')
        hbox1.Add(self.filepath_tc, 2, flag=wx.RIGHT, border=8)
        hbox1.Add(choosepath_button, 0, flag=wx.LEFT, border=8)

        vbox.Add(hbox1, flag=wx.EXPAND |
                 wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        st1 = wx.StaticText(self, label=u'间隔时间(秒)')
        Time_tc = wx.TextCtrl(self)
        start_button = wx.Button(self, label=u' 开始 ')
        stop_button = wx.Button(self, label=u'结束')
        hbox2.Add(st1)
        hbox2.Add(Time_tc, flag=wx.LEFT | wx.BOTTOM, border=7)
        hbox2.Add(start_button, flag=wx.LEFT, border=31)
        hbox2.Add(stop_button, flag=wx.LEFT, border=7)
        vbox.Add(hbox2, flag=wx.ALIGN_RIGHT | wx.RIGHT | wx.TOP, border=10)

        self.Process_tc = wx.TextCtrl(
            self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        hbox3.Add(self.Process_tc, proportion=1, flag=wx.EXPAND)
        vbox.Add(hbox3, proportion=1, flag=wx.EXPAND |
                 wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        self.SetSizer(vbox)

        #   定时器
        self.timer = wx.Timer(self)
        #   绑定start事件
        self.Bind(wx.EVT_TIMER, self.start, self.timer)
        # bind the events to handlers

        self.Bind(wx.EVT_BUTTON, self.outputpath, choosepath_button)
        self.Bind(wx.EVT_BUTTON, self.OnStart, start_button)
        self.Bind(wx.EVT_TEXT, self.Time_Interval, Time_tc)
        self.Bind(wx.EVT_BUTTON, self.StopProgram, stop_button)

    def outputpath(self, event):
        self.filepath_tc.Clear()
        dir_dlg = wx.DirDialog(
            self, message='Choose Results Directory', defaultPath=os.getcwd(), style=wx.DD_DIR_MUST_EXIST)
        if dir_dlg.ShowModal() == wx.ID_OK:
            self.filepath_tc.AppendText(dir_dlg.GetPath())
            self.output_path = dir_dlg.GetPath()

    def OnStart(self, event):
        self.timer.Start((int(self.time_Itv))*1000)

    def start(self, event):
        im = ImageGrab.grab()
        t = time.strftime("%m-%d-%H-%M-%S", time.localtime())
        path = self.output_path+os.path.sep+self.name_pre+t+'.bmp'
        im.save(path)
        self.Process_tc.AppendText(u'......已储存在'+path+'\n')

    def Time_Interval(self, event):
        self.time_Itv = event.GetString()

    def StopProgram(self, event):
        self.timer.Stop()


class PageThree(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent, pos=(0, 0))

        self.url = ''
        self.InitUI()

    def InitUI(self):
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.tc = wx.TextCtrl(
            self, value="http://svr.servers.xm.youxi.gigaget.com:8991/poptip?gameid=000047&pid=8C89A57230FBVJRU&tids=")
        submit_button = wx.Button(self, label=u'提    交')
        hbox1.Add(self.tc, 2, flag=wx.RIGHT, border=8)
        hbox1.Add(submit_button, 0, flag=wx.LEFT, border=8)

        vbox.Add(hbox1, flag=wx.EXPAND |
                 wx.LEFT | wx.RIGHT | wx.TOP, border=10)

        self.P_tc = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        hbox3.Add(self.P_tc, proportion=1, flag=wx.EXPAND)
        vbox.Add(hbox3, proportion=1, flag=wx.EXPAND |
                 wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        self.SetSizer(vbox)

        self.Bind(wx.EVT_TEXT, self.geturl, self.tc)
        self.Bind(wx.EVT_BUTTON, self.submit, submit_button)

    def geturl(self, event):
        self.url = event.GetString()

    def submit(self, event):
        u = urllib.urlopen(self.url).read()
        contents = json.loads(u)
        if len(contents) > 0:
            temp = contents[0]['head']
            str_temp = str(temp)
            self.P_tc.AppendText("Head:"+base64.decodestring(
                str_temp).decode('utf-8')+'\n')
            self.P_tc.AppendText("Body:"+base64.decodestring(
                str(contents[0]['body'])).decode('utf-8')+'\n')
            self.P_tc.AppendText("Tail:"+base64.decodestring(
                str(contents[0]['tail'])).decode('utf-8')+'\n')
            self.P_tc.AppendText("Gameid:"+contents[0]['gameid']+'\n')
            self.P_tc.AppendText("Tid:"+str(contents[0]['tid'])+'\n')
            self.P_tc.AppendText("imageurl:"+contents[0]['imageUrl']+'\n')
            self.P_tc.AppendText(
                "----------------------------------------------"+'\n')
        else:
            # 好像Appendtext里的默认编码非utf-8，需要再指定
            self.P_tc.AppendText(u"没有获取到配置"+'\n')
            self.P_tc.AppendText(
                "----------------------------------------------"+'\n')


class WorkerThread(threading.Thread):

    """后台运行  socket 线程"""
    def __init__(self, threadNum, window):
        threading.Thread.__init__(self)
        self.threadNum = threadNum
        self.window = window
        self.IP_ADDRESS = '221.238.24.104'
        self.timeToQuit = threading.Event()
        self.timeToQuit.clear()

    def stop(self):
        self.timeToQuit.set()

    def run(self):  # RUN 行为在此
        HOST = socket.gethostbyname(socket.gethostname())
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
        s.bind((HOST, 0))
        s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        s.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
        wx.CallAfter(self.window.LogMessage,
                     u'-----------------------------监控开始-------------------------------\n')
        while True:
            buf = s.recvfrom(65565)
            if len(buf) == 0:
                s.close
            else:
                mapIpTmp = self.decodeIpHeader(buf)
                if mapIpTmp['totalLen'] < 40:
                    pass
                    # print '非TCP的数据包就不抓了'
                else:
                    mapTcpTmp = self.decodeTcpHeader(mapIpTmp['data'])
                    if mapIpTmp['dstaddr'] == self.IP_ADDRESS and mapTcpTmp['headerLen'] + mapIpTmp['headerLen'] != mapIpTmp['totalLen']:
                        wx.CallAfter(self.window.LogMessage, self.inputdata(
                            mapTcpTmp['data']))

                    if mapIpTmp['srcaddr'] == self.IP_ADDRESS and mapTcpTmp['headerLen'] + mapIpTmp['headerLen'] != mapIpTmp['totalLen']:
                        mapHttpTmp = self.decoderevHttpdata(mapTcpTmp['data'])
                        wx.CallAfter(self.window.LogMessage, u'\n服务器返回:\n')
                        wx.CallAfter(
                            self.window.LogMessage, mapHttpTmp + '\n\n\n')

        s.ioctl(socket.SIO_RCVALL, socket.RCVALL_OFF)

    def decodeIpHeader(self, packet):
        """ 解抓raw socket抓到的packet数据包IP层头部放置到mapRet字典中
        数据有如下:

        version
        headerLen
        serviceType
        totalLen
        id
        fragOff
        ttl
        protocol
        checksum
        srcAddr
        dstAddr
        data
        """
        mapRet = {}
        mapRet["version"] = (int(ord(packet[0][0])) & 0xF0) >> 4  # 去除高4位
        mapRet["headerLen"] = (int(ord(packet[0][0])) & 0x0F) << 2  # 乘4
        mapRet["serviceType"] = hex(int(ord(packet[0][1])))  # 十六进制打出来
        mapRet["totalLen"] = socket.ntohs(
            struct.unpack('H', packet[0][2:4])[0])
        mapRet["identification"] = "0x%02x%02x" % ((int(
            ord(packet[0][4]))), (int(ord(packet[0][5]))))
        mapRet["id"] = int(ord(packet[0][6]) & 0xE0) >> 5  # 去除高5位
        mapRet["fragOff"] = (int(ord(packet[0][
                             6]) & 0x1F) + int(ord(packet[0][7])))
        mapRet["ttl"] = int(ord(packet[0][8]))
        mapRet["protocol"] = int(ord(packet[0][9]))
        mapRet["checkSum"] = "0x%02x%02x" % (int(ord(packet[
                                             0][10])), int(ord(packet[0][11])))  # 十六进制打出来
        mapRet["srcaddr"] = "%d.%d.%d.%d" % (int(ord(packet[0][12])), int(ord(
            packet[0][13])), int(ord(packet[0][14])), int(ord(packet[0][15])))
        mapRet["dstaddr"] = "%d.%d.%d.%d" % (int(ord(packet[0][16])), int(
            ord(packet[0][17])), int(ord(packet[0][18])), int(ord(packet[0][19])))
        mapRet["data"] = packet[0][mapRet["headerLen"]:mapRet["totalLen"]]
        return mapRet

    def decodeTcpHeader(self, packet):
        """解抓raw socket抓到的packet数据包TCP层头部放置到mapRet字典中
        数据有如下:

        srcPort
        dstPort
        sequenceNum
        ackNum
        headerLen
        flags
        WinSize
        checksum
        Urgentpoint
        data
        """
        mapRet = {}
        mapRet['srcport'] = int(ord(packet[0])) + int(ord(packet[1]))
        mapRet['dstport'] = int(ord(packet[2])) + int(ord(packet[3]))
        mapRet['sequenceNum'] = struct.unpack(">I", packet[4:8])[0]
        mapRet['ackNum'] = struct.unpack(">I", packet[8:12])[0]
        mapRet['headerLen'] = (int(ord(packet[
                               12])) & 0xF0) >> 2  # 右移4位左移2位→右移2位
        mapRet['flags'] = struct.unpack("B", packet[13])[0] & 0x3F
      # mapRet['URG'] = int(ord(packet[0][33])) & 0x20
      # mapRet['ACK'] = int(ord(packet[0][33])) & 0x10
      # mapRet['RST'] = int(ord(packet[0][33])) & 0x04
      # mapRet['SYN'] = int(ord(packet[0][33])) & 0x02
      # mapRet['FIN'] = int(ord(packet[0][33])) & 0x01
        mapRet['WinSize'] = struct.unpack(">H", packet[14:16])[0]
        mapRet['checkSum'] = struct.unpack(">H", packet[16:18])[0]
        mapRet['Urgentpoint'] = struct.unpack(">H", packet[18:20])[0]
        mapRet['data'] = packet[mapRet['headerLen']:]
        return mapRet

    def decodesendHttpdata(self, data):
        '''自定义过滤规则获得需要处理的数据
        返回一组字典收集各项对应的数据
        目标的处理数据是:发包数据
        '''
        mapRet = {}
        Tempdata = data.split('\r\n')
        start_pos = Tempdata[0].index('?')
        end_pos = Tempdata[0].index('HTTP')
        Tempdata1 = Tempdata[0][start_pos + 1:end_pos - 1].split('&')
        for element in Tempdata1:
            key = element.split('=')[0]
            value = element.split('=')[1]
            mapRet[key] = value

        return mapRet

    def decoderevHttpdata(self, data):
        '''自定义过滤规则获得需要处理的数据
        返回一串String
        目标的处理数据:收包数据
        '''
        return data.split('\r\n')[5]

    def inputdata(self, data):
        '''格式化顺序输出欲输出的数据
        返回一个字符串
        '''
        result = u"客户端发送日志：\n"
        f = file("data.json")
        mapRet = json.load(f)
        mapHttpTmp = self.decodesendHttpdata(data)
        if mapHttpTmp['gs'] in mapRet:
            result += mapHttpTmp['gs'] + '->'
            for (k, v) in mapHttpTmp.items():
                for (key, value) in mapRet[mapHttpTmp['gs']].items():
                    if key == k:  # 对比
                        result += "%s: %s " % (k, v)
                        if type(mapRet[mapHttpTmp['gs']][key]) == dict:  # 若mapRet[mapHttpTmp['gs']][key] 的值不再是字典就直接输出了
                            if mapRet[mapHttpTmp['gs']][key].has_key(v):
                                result += "(%s) \t" % mapRet[
                                    mapHttpTmp['gs']][key][v]
                            else:
                                result += '(Undefined)' + '\t'
                        else:
                            result += "(%s) \t" % mapRet[mapHttpTmp['gs']][key]
        else:
            result += u'未在json文件中定义此类文件'
        result += '\n'
        return result
        f.close()


class PageFour(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.name_pre = u'登陆器操作日志'  # 储存文件前缀名
        self.threads = []
        self.count = 0
        self.daily_data = ''
        self.InitUI()

    def InitUI(self):
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        vbox = wx.BoxSizer(wx.VERTICAL)

        start_button = wx.Button(self, label=u' 开始持续监控 ')
        export_button = wx.Button(self, label=u'导出日志')
        hbox1.Add(start_button, flag=wx.LEFT, border=31)
        hbox1.Add(export_button, flag=wx.LEFT, border=7)
        vbox.Add(hbox1, flag=wx.ALIGN_RIGHT |
                 wx.RIGHT | wx.TOP | wx.BOTTOM, border=10)

        self.Process_tc = wx.TextCtrl(
            self, style=wx.TE_MULTILINE | wx.TE_READONLY)
        hbox2.Add(self.Process_tc, proportion=1, flag=wx.EXPAND)
        vbox.Add(hbox2, proportion=1, flag=wx.EXPAND |
                 wx.LEFT | wx.RIGHT | wx.BOTTOM, border=10)

        self.SetSizer(vbox)

        # bind the events to handlers

        self.Bind(wx.EVT_BUTTON, self.OnExport, export_button)
        self.Bind(wx.EVT_BUTTON, self.OnStart, start_button)
        self.Bind(wx.EVT_TEXT, self.Data, self.Process_tc)
        self.Bind(wx.EVT_CLOSE, self.OnCloseWindow)

    def Data(self,event):
        self.daily_data = event.GetString()

    def OnExport(self, event):
        t = time.strftime("%m-%d-%H-%M-%S", time.localtime())
        path = self.name_pre+t+'.txt'
        f = open(path,'w')
        f.write(self.daily_data.encode('gb2312'))
        f.close()

    def OnStart(self, event):
        self.count += 1
        thread = WorkerThread(self.count, self)  # 创建一个线程
        self.threads.append(thread)
        thread.start()  # 启动线程

    def LogMessage(self, msg):  # regiester a message
        self.Process_tc.AppendText(msg)

    def StopThreads(self):  # 从池中删除线程 线程池：threads、线程：thread
        while self.threads:
            thread = self.threads[0]
            thread.stop()
            self.threads.remove(thread)

    def OnCloseWindow(self, event):
        self.StopThreads()
        self.Destroy()


class MainFrame(wx.Frame):

    def __init__(self):
        wx.Frame.__init__(self, None, title="Work Tools", size=(600, 700))

        # Here we create a panel and a notebook on the panel
        p = wx.Panel(self)
        nb = wx.Notebook(p)

        # create the page windows as children of the notebook
        page1 = PageOne(nb)
        page2 = PageTwo(nb)
        page3 = PageThree(nb)
        page4 = PageFour(nb)

        # add the pages to the notebook with the label to show on the tab
        nb.AddPage(page1, "StatFilter")
        nb.AddPage(page2, "ScreenShot")
        nb.AddPage(page3, "Request")
        nb.AddPage(page4, "GetPacket")

        # finally, put the notebook in a sizer for the panel to manage
        # the layout
        sizer = wx.BoxSizer()
        sizer.Add(nb, 1, wx.EXPAND)
        p.SetSizer(sizer)
        self.Center()

if __name__ == "__main__":
    app = wx.App()
    MainFrame().Show()
    app.MainLoop()
