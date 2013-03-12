# -*- coding: utf-8 -*-
import wx
import re
import os
import ImageGrab
import time
import urllib
import json
import base64

class PageOne(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent,pos=(0,0))

        self.regf = ''   #储存外部输入正则表达式
        self.Before_Data = ''  #储存外部输入待处理数据
        self.After_Data = [] #分割后的数据 (元组)
        self.Result = [] #储存最后的结果
        self.flag = 0

        self.InitUI()
    def InitUI(self):
        vbox = wx.BoxSizer(wx.VERTICAL)

        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        st1 = wx.StaticText(self,label=u'正则表达式：')
        hbox1.Add(st1,flag=wx.RIGHT,border=8)

        tc = wx.TextCtrl(self)
        hbox1.Add(tc,proportion=1)
        vbox.Add(hbox1,flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,border=10)
        vbox.Add((-1,10))

        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        st2 = wx.StaticText(self,label=u'待处理数据：')
        hbox3.Add(st2,flag=wx.RIGHT,border=8)

        tc2 = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        hbox3.Add(tc2, proportion=1, flag=wx.EXPAND)
        vbox.Add(hbox3, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND,
            border=10)
        vbox.Add((-1, 25))

        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        cb1 = wx.CheckBox(self, label=u'逆序输出')
        hbox4.Add(cb1,flag=wx.RIGHT|wx.EXPAND,border=8)
        btn = wx.Button(self, label=u'提交数据', size=(90, 30))
        hbox4.Add(btn)
        vbox.Add(hbox4, flag=wx.ALIGN_RIGHT|wx.RIGHT,border=8)
        vbox.Add((-1, 25))

        hbox5 = wx.BoxSizer(wx.HORIZONTAL)
        self.aft_str = wx.StaticText(self,label=u'已处理数据：')
        hbox5.Add(self.aft_str,flag=wx.RIGHT,border=8)

        self.tc3 = wx.TextCtrl(self, style=wx.TE_MULTILINE|wx.TE_READONLY)
        hbox5.Add(self.tc3, proportion=1, flag=wx.EXPAND)
        vbox.Add(hbox5, proportion=1, flag=wx.LEFT|wx.RIGHT|wx.EXPAND,
            border=10)
        vbox.Add((-1, 25))
        self.SetSizer(vbox)

        # bind the events to handlers
        self.Bind(wx.EVT_TEXT,self.regformat,tc)
        #    self.Bind(wx.EVT_CHAR,self.onkeypress,tc)
        self.Bind(wx.EVT_TEXT,self.beforedata,tc2)
        #    self.Bind(wx.EVT_CHAR,self.onkeypress,tc)
        self.Bind(wx.EVT_CHECKBOX,self.reverse,cb1)
        self.Bind(wx.EVT_BUTTON,self.submit,btn)

    def regformat(self,event):
        self.regf = event.GetString()
        #       self.tc3.AppendText(u'正则表达式:%s \n' % self.regf)

    def beforedata(self,event):
        self.Before_Data = event.GetString()
    #        self.tc3.AppendText('Before Data:%s \n' % self.Before_Data)

    def reverse(self,event):
        self.flag = event.Checked()

    def submit(self,event):
        #初始化变量，以免覆盖追加
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
            for element in range(size-1,-1,-1):
                self.tc3.AppendText(self.Result[element])
                self.tc3.AppendText('\n')

class PageTwo(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.time_Itv = '' #时间间隔
        self.name_pre = u'防沉迷'  #储存文件前缀名
        self.InitUI()

    def InitUI(self):
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.filepath_tc = wx.TextCtrl(self)
        choosepath_button = wx.Button(self,label=u'选择保存路径')
        hbox1.Add(self.filepath_tc,2,flag=wx.RIGHT,border=8)
        hbox1.Add(choosepath_button,0,flag=wx.LEFT,border=8)

        vbox.Add(hbox1,flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,border=10)

        st1 = wx.StaticText(self,label=u'间隔时间(秒)')
        Time_tc = wx.TextCtrl(self)
        start_button = wx.Button(self,label=u' 开始 ')
        stop_button = wx.Button(self,label=u'结束')
        hbox2.Add(st1)
        hbox2.Add(Time_tc,flag=wx.LEFT|wx.BOTTOM,border=7)
        hbox2.Add(start_button,flag=wx.LEFT,border=31)
        hbox2.Add(stop_button,flag=wx.LEFT,border=7)
        vbox.Add(hbox2,flag=wx.ALIGN_RIGHT|wx.RIGHT|wx.TOP,border=10)

        self.Process_tc = wx.TextCtrl(self,style=wx.TE_MULTILINE|wx.TE_READONLY)
        hbox3.Add(self.Process_tc,proportion=1, flag=wx.EXPAND)
        vbox.Add(hbox3,proportion=1,flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,border=10)

        self.SetSizer(vbox)

        #   定时器
        self.timer = wx.Timer(self)
        #   绑定start事件
        self.Bind(wx.EVT_TIMER,self.start,self.timer)
        # bind the events to handlers

        self.Bind(wx.EVT_BUTTON,self.outputpath,choosepath_button)
        self.Bind(wx.EVT_BUTTON,self.OnStart,start_button)
        self.Bind(wx.EVT_TEXT,self.Time_Interval,Time_tc)
        self.Bind(wx.EVT_BUTTON,self.StopProgram,stop_button)

    def outputpath(self,event):
        self.filepath_tc.Clear()
        dir_dlg = wx.DirDialog(self, message='Choose Results Directory', defaultPath=os.getcwd(), style=wx.DD_DIR_MUST_EXIST)
        if dir_dlg.ShowModal() == wx.ID_OK:
            self.filepath_tc.AppendText(dir_dlg.GetPath())
            self.output_path = dir_dlg.GetPath()

    def OnStart(self,event):
        self.timer.Start((int(self.time_Itv))*1000)

    def start(self,event):
        im = ImageGrab.grab()
        t = time.strftime("%m-%d-%H-%M-%S",time.localtime())
        path = self.output_path+os.path.sep+self.name_pre+t+'.bmp'
        im.save(path)
        self.Process_tc.AppendText(u'......已储存在'+path+'\n')

    def Time_Interval(self,event):
        self.time_Itv = event.GetString()

    def StopProgram(self,event):
        self.timer.Stop()

class PageThree(wx.Panel):
    def __init__(self, parent):
        wx.Panel.__init__(self, parent,pos=(0,0))

        self.url = ''
        self.InitUI()

    def InitUI(self):
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self.tc = wx.TextCtrl(self,value="http://svr.servers.xm.youxi.gigaget.com:8991/poptip?gameid=000047&pid=8C89A57230E488S1&tids=")
        submit_button = wx.Button(self,label=u'提    交')
        hbox1.Add(self.tc,2,flag=wx.RIGHT,border=8)
        hbox1.Add(submit_button,0,flag=wx.LEFT,border=8)

        vbox.Add(hbox1,flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.TOP,border=10)

        self.P_tc = wx.TextCtrl(self,style=wx.TE_MULTILINE|wx.TE_READONLY)
        hbox3.Add(self.P_tc,proportion=1, flag=wx.EXPAND)
        vbox.Add(hbox3,proportion=1,flag=wx.EXPAND|wx.LEFT|wx.RIGHT|wx.BOTTOM,border=10)

        self.SetSizer(vbox)

        self.Bind(wx.EVT_TEXT,self.geturl,self.tc)
        self.Bind(wx.EVT_BUTTON,self.submit,submit_button)

    def geturl(self,event):
        self.url = event.GetString()

    def submit(self,event):
         u = urllib.urlopen(self.url).read()
         contents = json.loads(u)
         temp = contents[0]['head']
         str_temp = str(temp)
         self.P_tc.AppendText("Head:"+base64.decodestring(str_temp).decode('utf-8').encode('gbk')+'\n')
         self.P_tc.AppendText("Body:"+base64.decodestring(str(contents[0]['body'])).decode('utf-8').encode('gbk')+'\n')
         self.P_tc.AppendText("Tail:"+base64.decodestring(str(contents[0]['tail'])).decode('utf-8').encode('gbk')+'\n')
         self.P_tc.AppendText("Gameid:"+contents[0]['gameid']+'\n')
         self.P_tc.AppendText("Tid:"+str(contents[0]['tid'])+'\n')
         self.P_tc.AppendText("imageurl:"+contents[0]['imageUrl']+'\n')
         self.P_tc.AppendText("----------------------------------------------"+'\n')
class MainFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, title="Job tools",size=(600,700))

        # Here we create a panel and a notebook on the panel
        p = wx.Panel(self)
        nb = wx.Notebook(p)

        # create the page windows as children of the notebook
        page1 = PageOne(nb)
        page2 = PageTwo(nb)
        page3 = PageThree(nb)

        # add the pages to the notebook with the label to show on the tab
        nb.AddPage(page1, "StatFilter")
        nb.AddPage(page2, "ScreenShot")
        nb.AddPage(page3, "Request")

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