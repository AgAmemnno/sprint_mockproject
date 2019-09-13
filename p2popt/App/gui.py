import wx.lib.inspection
import wx.lib.mixins.inspection
import matplotlib

matplotlib.interactive(True)
matplotlib.use('WXAgg')
from matplotlib.widgets import Button, RadioButtons
from matplotlib.font_manager import FontProperties

from p2popt.GLAux.log import log
from p2popt.App.mock import *

from p2popt.App.wxasync import *


class MockFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, None, -1, args[1], **kwargs)
        # print(args,kwargs)

        self.mock = Mock(self, size=kwargs["size"])
        if args[0] == 1:
            self.mock.Test1()
        if args[0] == 2:
            self.mock.Test2()
        if args[0] == 3:
            self.mock.Test3()
        if args[0] >= 4:
            self.gui = args[2]
        if args[0] == 4:
            self.mock.Test4()
        if args[0] == 5:
            self.mock.Test5()
        if args[0] == 6:
            self.mock.Test6()
        if args[0] == 10:
            self.mock.Test10()

        self.sizer = wx.BoxSizer()
        self.sizer.Add(self.mock, 1, wx.EXPAND)


class MockControlFrame(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, None, -1, args[1], **kwargs)
        # print(args,kwargs)

        self.mock = Mock(self, size=(512, 512))  # kwargs["size"])
        self.gui = args[2]
        if args[0] == 7:
            self.mock.Test7()

        self.sizer = wx.BoxSizer()
        self.sizer.Add(self.mock, 1, wx.EXPAND)
        # self.SetSizerAndFit(self.sizer)

        mb = wx.MenuBar()
        menu1 = wx.Menu()

        item = wx.MenuItem(menu1, wx.ID_ANY, "&Test7")
        menu1.Append(item)
        self.Bind(wx.EVT_MENU, self.OnTest7, item)

        item = wx.MenuItem(menu1, wx.ID_ANY, "&Test8")
        menu1.Append(item)
        self.Bind(wx.EVT_MENU, self.OnTest8, item)

        item = wx.MenuItem(menu1, wx.ID_ANY, "&Test9")
        menu1.Append(item)
        self.Bind(wx.EVT_MENU, self.OnTest9, item)

        mb.Append(menu1, "&Menu")
        self.SetMenuBar(mb)
        self.Show()

        self.exe_dlg = None

    async def mock1dlg(self, n):
        if n == 7:
            self.mock1_dlg = MockSetting7(self, 0)
        elif n == 8:
            self.mock1_dlg = MockSetting8(self, 0)
        elif n == 9:
            self.mock1_dlg = MockSetting9(self, 0)
        elif n == 10:
            self.mock1_dlg = MockSettingAsset(self, 0)
        return_code = await AsyncShowDialog(self.mock1_dlg)
        Date = self.mock1_dlg.GetValue()

    def OnTest7(self, event):
        loop = get_event_loop()
        ta = []
        ta.append(self.mock1dlg(7))
        for i in ta:
            loop.create_task(i)
        event.Skip()

    def OnTest8(self, event):
        loop = get_event_loop()
        ta = []
        ta.append(self.mock1dlg(8))
        for i in ta:
            loop.create_task(i)
        event.Skip()

    def OnTest9(self, event):
        loop = get_event_loop()
        ta = []
        ta.append(self.mock1dlg(9))
        for i in ta:
            loop.create_task(i)
        event.Skip()


class MockControlFrame2(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, None, -1, args[1], **kwargs)
        # print(args,kwargs)
        self.mock = Mock(self, size=kwargs["size"])
        self.gui = args[2]

        self.sizer = wx.BoxSizer()
        self.sizer.Add(self.mock, 1, wx.EXPAND)
        # self.SetSizerAndFit(self.sizer)

        mb = wx.MenuBar()
        menu1 = wx.Menu()

        item = wx.MenuItem(menu1, wx.ID_ANY, "&TestAsset")
        menu1.Append(item)
        self.Bind(wx.EVT_MENU, self.OnTestAsset, item)

        mb.Append(menu1, "&Menu")
        self.SetMenuBar(mb)
        self.Show()

        self.exe_dlg = None

    async def mock1dlg(self, n):
        if n == 0:
            self.mock1_dlg = MockSettingAsset(self, 0)
        return_code = await AsyncShowDialog(self.mock1_dlg)
        Date = self.mock1_dlg.GetValue()

    def OnTestAsset(self, event):
        loop = get_event_loop()
        ta = []
        ta.append(self.mock1dlg(0))
        for i in ta:
            loop.create_task(i)
        event.Skip()


class Gui(wx.Frame):
    def __init__(self, *args, **kwargs):
        wx.Frame.__init__(self, None, -1, args[1], **kwargs["option"])
        # print(args,kwargs)
        # self.shid  = kwargs["shid"]
        # self.batch = kwargs["batch"]

        self.shth  = 16
        self.batch = 10
        self.mock1_dlg = None

        self.SetBackgroundColour(wx.Colour(12, 12, 12))
        self.statusbar = self.CreateStatusBar(2)
        self.statusbar.SetStatusWidths([-4, -3])
        self.statusbar.SetStatusText("AgAmemnno   2019/09/13", 0)
        self.statusbar.SetStatusText("Welcome to SprintPython!", 1)

        self.mock = Mock(self, size=(2000, 1000), name="mock")
        self.vis = Mock(self, size=(2000, 1000), name="vis")

        self.sizerMock = wx.GridSizer(rows=1, cols=1, vgap=1, hgap=1)
        self.sizerMock.Add(self.mock, 1, wx.EXPAND)

        self.sizerVis = wx.GridSizer(rows=1, cols=1, vgap=1, hgap=1)
        self.sizerVis.Add(self.vis, 0, wx.EXPAND)

        self.bsizer = wx.BoxSizer()
        self.bsizer.Add(self.sizerMock)
        self.screen = "mock"

        self.SetSizer(self.bsizer)

        mb = wx.MenuBar()
        menu1 = wx.Menu()

        item = wx.MenuItem(menu1, wx.ID_ANY, "&controller")
        menu1.Append(item)
        self.Bind(wx.EVT_MENU, self.OnTestAsset, item)
        mb.Append(menu1, "&Main")

        menu2 = wx.Menu()

        item = wx.MenuItem(menu1, wx.ID_ANY, "&mockclass")
        menu2.Append(item)
        self.Bind(wx.EVT_MENU, self.OnCompile_Mock, item, id=1)

        item = wx.MenuItem(menu1, wx.ID_ANY, "&visualizer")
        menu2.Append(item)
        self.Bind(wx.EVT_MENU, self.OnCompile_Vis, item)

        item = wx.MenuItem(menu1, wx.ID_ANY, "&all")
        menu2.Append(item)
        self.Bind(wx.EVT_MENU, self.OnCompile, item)

        mb.Append(menu2, "&Compile")

        menu2 = wx.Menu()
        item = wx.MenuItem(menu1, wx.ID_ANY, "&mock")
        menu2.Append(item)
        self.Bind(wx.EVT_MENU, self.OnSwitchMock, item)
        item = wx.MenuItem(menu1, wx.ID_ANY, "&vis")
        menu2.Append(item)
        self.Bind(wx.EVT_MENU, self.OnSwitchVis, item)
        mb.Append(menu2, "&Screen")

        menu3 = wx.Menu()
        item = wx.MenuItem(menu3, wx.ID_ANY, "&test1")
        menu3.Append(item)
        self.Bind(wx.EVT_MENU, self.OnTestDouble1, item)

        item = wx.MenuItem(menu3, wx.ID_ANY, "&blockdesign")
        menu3.Append(item)
        self.Bind(wx.EVT_MENU, self.OnTestDouble2, item)

        mb.Append(menu3, "&TestDouble")

        self.SetMenuBar(mb)
        self.Show()

        self.Compile = {"mock":False,"vis":False}
        self.exe_dlg = None

    def OnCompile_Mock(self, event):
        if self.Compile["mock"]:
            self.mock.OnDestroy(None)
        self.mock.TestApp(self.shth, self.batch)
        self.Compile["mock"] = True
        if self.mock1_dlg != None:
            self.mock1_dlg.pidslider.SetMax(self.shth*4*self.batch)

    def OnCompile_Vis(self, event):
        if self.Compile["vis"]:
            self.mock.OnDestroy(None)
        self.vis.TestAppVisual(self.shth, self.batch)
        self.Compile["vis"] = True

    def OnCompile(self, event):
        self.OnCompile_Vis(None)
        self.OnCompile_Mock(None)

    def OnSwitch(self, n):
        if n == "mock":
            self.OnSwitchMock(None)
        elif n == "vis":
            self.OnSwitchVis(None)

    def OnSwitchMock(self, event):
        self.bsizer.Remove(0)
        sizer = wx.GridSizer(rows=1, cols=1, vgap=1, hgap=1)
        sizer.Add(self.mock, 1, wx.EXPAND)
        self.bsizer.Add(sizer)
        self.SetSizer(self.bsizer)
        self.vis.Off()
        self.mock.On()
        self.screen = "mock"

        # self.Fit()

    def OnSwitchVis(self, event):
        self.bsizer.Remove(0)
        sizer = wx.GridSizer(rows=1, cols=1, vgap=1, hgap=1)
        sizer.Add(self.vis, 1, wx.EXPAND)
        self.bsizer.Add(sizer)
        self.SetSizer(self.bsizer)
        self.mock.Off()
        self.vis.On()
        self.screen = "vis"
        # self.Fit()

    async def mock1dlg(self, n):
        if n == 0:
            self.mock1_dlg = Controller(self, 0)
        return_code = await AsyncShowDialog(self.mock1_dlg)
        self.mock1_dlg = None

    def OnTestAsset(self, event):
        loop = get_event_loop()
        ta = []
        ta.append(self.mock1dlg(0))
        for i in ta:
            loop.create_task(i)
        event.Skip()

    def OnTestVisual(self, event):
        loop = get_event_loop()
        ta = []
        ta.append(self.mock1dlg(1))
        for i in ta:
            loop.create_task(i)
        event.Skip()

    def OnTestDouble1(self, evt):

        font = FontProperties()
        font.set_family('serif')  # ['serif', 'sans-serif', 'cursive', 'fantasy', 'monospace']
        font.set_weight('semibold')  # ['light', 'normal', 'medium', 'semibold', 'bold', 'heavy', 'black']
        font.set_size('xx-large')  # ['xx-small', 'x-small', 'small', 'medium', 'large','x-large', 'xx-large']

        self.bbox = {'facecolor': [0.2, 0.4, 0.4], 'alpha': 0.2, 'pad': 2}
        self.font = font
        self.figure = plt.figure(0)
        self.figure.canvas.set_window_title(config["name"])
        self.figure.set_facecolor((0.5, 0.5, 0.6))
        axcolor = (0.3, 0.3, 0.4)  # 'lightgoldenrodyellow'

        x = 0.2
        w = 0.1
        y = 0.6
        h = 0.1
        resetax = plt.axes([x, y, w, h])
        resetax.set_title("Test Double\n\n       Mock Test", fontproperties=font)
        self.bTest1 = Button(resetax, 'Test1', color=axcolor, hovercolor='0.575')
        x += w
        resetax = plt.axes([x, y, w, h])
        self.bTest2 = Button(resetax, 'Test2', color=axcolor, hovercolor='0.575')
        x += w
        resetax = plt.axes([x, y, w, h])
        self.bTest3 = Button(resetax, 'Test3', color=axcolor, hovercolor='0.575')

        x += w
        resetax = plt.axes([x, y, w, h])
        self.bTest4 = Button(resetax, 'Test4', color=axcolor, hovercolor='0.575')

        x += w
        resetax = plt.axes([x, y, w, h])
        self.bNext = Button(resetax, 'Next', color=axcolor, hovercolor='0.575')

        self.bTest1.on_clicked(self.OnTest1)
        self.bTest2.on_clicked(self.OnTest2)
        self.bTest3.on_clicked(self.OnTest3)
        self.bTest4.on_clicked(self.OnTest4)

        def next(label):
            if not TO.t4:
                log.Warning("Please Execute Test4 !!!")
            else:
                gc.collect()
                plt.close(0)

        self.bNext.on_clicked(next)

        self.ax1 = self.figure.add_subplot(212)
        plt.subplots_adjust(left=0.25, bottom=0.15)

        def handle_close(evt):
            # self.timer.Stop()
            log.Log('Closed TestSuits!')

        self.figure.canvas.mpl_connect('close_event', handle_close)

    def OnTest1(self, evt):
        # frame = Gui(None, -1, "Mock: ", size=(500, 500),style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame = MockFrame(1, "Test1", size=(500, 500), style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame.Show()

    def OnTest2(self, evt):
        # frame = Gui(None, -1, "Mock: ", size=(500, 500),style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame = MockFrame(2, "Test2", size=(500, 500), style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame.Show()

    def OnTest3(self, evt):
        # frame = Gui(None, -1, "Mock: ", size=(500, 500),style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame = MockFrame(3, "Test3", size=(500, 500), style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame.Show()

    def OnTest4(self, evt):
        # frame = Gui(None, -1, "Mock: ", size=(500, 500),style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame = MockFrame(4, "Test4", self, size=(500, 500), style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame.Show()

    def OnTestDouble2(self, evt):

        font = FontProperties()
        font.set_family('serif')  # ['serif', 'sans-serif', 'cursive', 'fantasy', 'monospace']
        font.set_weight('semibold')  # ['light', 'normal', 'medium', 'semibold', 'bold', 'heavy', 'black']
        font.set_size('xx-large')  # ['xx-small', 'x-small', 'small', 'medium', 'large','x-large', 'xx-large']

        self.bbox = {'facecolor': [0.18, 0.18, 0.18], 'alpha': 0.2, 'pad': 2}
        self.font = font
        self.figure = plt.figure(0, figsize=(4, 4), dpi=80)
        self.figure.canvas.set_window_title(config["name"])
        self.figure.set_facecolor((0.188, 0.18, 0.18))
        axcolor = (0.175, 0.18, 0.18)

        x = 0.2
        w = 0.1
        y = 0.6
        h = 0.05
        resetax = plt.axes([x, y, w * 2, h * 2])
        resetax.set_title("Test Double\n\n       Block Design\n", fontproperties=font)
        self.bTest5 = Button(resetax, 'Test5', color=axcolor, hovercolor='0.575')
        self.bTest5.on_clicked(self.OnTest5)

        resetax = plt.axes([x + 2 * w, y, w * 2, h * 2])
        self.bTest6 = Button(resetax, 'Test6', color=axcolor, hovercolor='0.575')
        self.bTest6.on_clicked(self.OnTest6)

        def shspec(label):
            log.Info("Shared Memory Change %s" % (label))
            self.shth = int(label)

        y = 0.25
        resetax = plt.axes([x, y, w * 1.5, h * 4], facecolor=axcolor)
        font.set_size('large')
        resetax.set_title("SharedMemory", fontproperties=font)
        self.shspec = RadioButtons(resetax, ('8', '16', '24', '32'), active=1)
        self.shspec.on_clicked(shspec)


        def batchsize(label):
            log.Info("BatchSize Change %s" % (label))
            self.batch = int(label)

        resetax = plt.axes([x + 0.4, 0.25, w * 1.5, h * 4], facecolor=axcolor)
        font.set_size('large')
        resetax.set_title("BatchSize", fontproperties=font)
        self.batchsize = RadioButtons(resetax, ('5', '10', '25', '50'), active=1)
        self.batchsize.on_clicked(batchsize)

        def handle_close(evt):
            # self.timer.Stop()
            # plt.close(0)
            log.Log('Closed Test BlockDesign!')

        self.figure.canvas.mpl_connect('close_event', handle_close)

    def OnTest5(self, evt):
        # frame = Gui(None, -1, "Mock: ", size=(500, 500),style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame = MockFrame(5, "Test5", self, size=(500, 500), style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame.Show()

    def OnTest6(self, evt):
        # frame = Gui(None, -1, "Mock: ", size=(500, 500),style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame = MockFrame(6, "Test6", self, size=(500, 500), style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame.Show()


class _Gui(wx.Panel):
    def __init__(self, parent):
        self.parent = parent
        wx.Panel.__init__(self, parent, -1)
        self.TestDouble2()

    def TestDouble1(self):

        font = FontProperties()
        font.set_family('serif')  # ['serif', 'sans-serif', 'cursive', 'fantasy', 'monospace']
        font.set_weight('semibold')  # ['light', 'normal', 'medium', 'semibold', 'bold', 'heavy', 'black']
        font.set_size('xx-large')  # ['xx-small', 'x-small', 'small', 'medium', 'large','x-large', 'xx-large']

        self.bbox = {'facecolor': [0.2, 0.4, 0.4], 'alpha': 0.2, 'pad': 2}
        self.font = font
        self.figure = plt.figure(0)
        self.figure.canvas.set_window_title(config["name"])
        self.figure.set_facecolor((0.5, 0.5, 0.6))
        axcolor = (0.3, 0.3, 0.4)  # 'lightgoldenrodyellow'

        x = 0.2
        w = 0.1
        y = 0.6
        h = 0.1
        resetax = plt.axes([x, y, w, h])
        resetax.set_title("Test Double\n\n       Mock Test", fontproperties=font)
        self.bTest1 = Button(resetax, 'Test1', color=axcolor, hovercolor='0.575')
        x += w
        resetax = plt.axes([x, y, w, h])
        self.bTest2 = Button(resetax, 'Test2', color=axcolor, hovercolor='0.575')
        x += w
        resetax = plt.axes([x, y, w, h])
        self.bTest3 = Button(resetax, 'Test3', color=axcolor, hovercolor='0.575')

        x += w
        resetax = plt.axes([x, y, w, h])
        self.bTest4 = Button(resetax, 'Test4', color=axcolor, hovercolor='0.575')

        x += w
        resetax = plt.axes([x, y, w, h])
        self.bNext = Button(resetax, 'Next', color=axcolor, hovercolor='0.575')

        self.bTest1.on_clicked(self.OnTest1)
        self.bTest2.on_clicked(self.OnTest2)
        self.bTest3.on_clicked(self.OnTest3)
        self.bTest4.on_clicked(self.OnTest4)

        def next(label):
            if not TO.t4:
                log.Warning("Please Execute Test4 !!!")
                # self.frame.Destroy()
                # gc.collect()
                # return
            else:
                plt.close(0)
                self.TestDouble2()

        self.bNext.on_clicked(next)

        self.ax1 = self.figure.add_subplot(212)
        plt.subplots_adjust(left=0.25, bottom=0.15)

        def handle_close(evt):
            # self.timer.Stop()
            self.parent.Destroy()
            print('Closed Figure!')

        self.figure.canvas.mpl_connect('close_event', handle_close)

    def TestDouble2(self):

        font = FontProperties()
        font.set_family('serif')  # ['serif', 'sans-serif', 'cursive', 'fantasy', 'monospace']
        font.set_weight('semibold')  # ['light', 'normal', 'medium', 'semibold', 'bold', 'heavy', 'black']
        font.set_size('xx-large')  # ['xx-small', 'x-small', 'small', 'medium', 'large','x-large', 'xx-large']

        self.bbox = {'facecolor': [0.18, 0.18, 0.18], 'alpha': 0.2, 'pad': 2}
        self.font = font
        self.figure = plt.figure(0)
        self.figure.canvas.set_window_title(config["name"])
        self.figure.set_facecolor((0.188, 0.18, 0.18))
        axcolor = (0.175, 0.18, 0.18)

        x = 0.4
        w = 0.1
        y = 0.82
        h = 0.05

        resetax = plt.axes([x, y, w, h])
        self.bSet = Button(resetax, 'Settings', color=axcolor, hovercolor='0.575')
        self.bSet.on_clicked(self.OnFile)

        x = 0.2
        w = 0.1
        y = 0.6
        h = 0.05
        resetax = plt.axes([x, y, w, h])
        resetax.set_title("Test Double\n\n       Block Design\n", fontproperties=font)
        self.bTest5 = Button(resetax, 'Test5', color=axcolor, hovercolor='0.575')
        self.shth = 256
        self.bTest5.on_clicked(self.OnTest5)

        y -= h
        resetax = plt.axes([x, y, w, h])
        self.bTest6 = Button(resetax, 'Test6', color=axcolor, hovercolor='0.575')
        self.bTest6.on_clicked(self.OnTest6)

        def shspec(label):
            log.Info("Shared Memory Change %s" % (label))
            self.shth = int(label)

        y -= 2 * h
        resetax = plt.axes([x, y - 0.1, w, h + 0.1], facecolor=axcolor)
        font.set_size('small')
        resetax.set_title("SharedMemory", fontproperties=font)
        self.shspec = RadioButtons(resetax, ('16', '32', '64', '128', '256'), active=1)
        self.shspec.on_clicked(shspec)
        self.shth = 32

        x = 0.35
        w = 0.1
        y = 0.6
        h = 0.05
        resetax = plt.axes([x, y, w, h])
        self.bTest10 = Button(resetax, 'Test10', color=axcolor, hovercolor='0.575')
        self.bTest10.on_clicked(self.OnTest10)
        self.batch = 10

        def batchsize(label):
            log.Info("BatchSize Change %s" % (label))
            self.batch = int(label)

        y -= 2 * h
        resetax = plt.axes([x, y - 0.1, w, h + 0.1], facecolor=axcolor)
        font.set_size('small')
        resetax.set_title("BatchSize", fontproperties=font)
        self.batchsize = RadioButtons(resetax, ('5', '10', '50', '100'), active=1)
        self.batchsize.on_clicked(batchsize)

        x = 0.2
        w = 0.1
        y = 0.1
        h = 0.05
        resetax = plt.axes([x, y, w + 0.1, h])
        font.set_size('x-large')
        resetax.set_title("Test Visualize\n", fontproperties=font)
        self.bTest7 = Button(resetax, 'TestFrame', color=axcolor, hovercolor='0.575')
        self.bTest7.on_clicked(self.OnTest7)

        x = 0.6
        w = 0.1
        y = 0.3
        h = 0.05
        resetax = plt.axes([x, y, w + 0.1, h])
        font.set_size('x-large')
        resetax.set_title("Test InOut\n", fontproperties=font)
        self.bTestinout = Button(resetax, 'TestFrame', color=axcolor, hovercolor='0.575')
        self.bTestinout.on_clicked(self.OnTestInout)

        x = 0.6
        w = 0.1
        y = 0.1
        h = 0.05
        resetax = plt.axes([x, y, w + 0.1, h])
        font.set_size('x-large')
        resetax.set_title("Test App\n", fontproperties=font)
        self.bStartUp = Button(resetax, 'StartUp', color=axcolor, hovercolor='0.575')
        self.bStartUp.on_clicked(self.OnStartUp)

        self.ax1 = self.figure.add_subplot(222)
        plt.subplots_adjust(left=0.25, bottom=0.15)

        def handle_close(evt):
            # self.timer.Stop()
            self.parent.Destroy()
            print('Closed Figure!')

        self.figure.canvas.mpl_connect('close_event', handle_close)

    def OnFile(self, event):
        wildcard = "CSV (*.csv)" \
                   "All files (*.*)|*.*"

        dlg = wx.FileDialog(
            self, message="Choose a SampleData",
            defaultDir=os.getcwd(),
            defaultFile="",
            wildcard=wildcard,
            style=wx.FD_OPEN | wx.FD_MULTIPLE |
                  wx.FD_CHANGE_DIR | wx.FD_FILE_MUST_EXIST |
                  wx.FD_PREVIEW
        )

        if dlg.ShowModal() == wx.ID_OK:
            # This returns a Python list of files that were selected.
            paths = dlg.GetPaths()[0]
            log.Info('You selected SampleData %s:' % paths)
            config["dataDir"] = os.path.dirname(paths)
            config["data"] = os.path.basename(paths)
            os.chdir(os.path.dirname(os.path.abspath(__file__)))

        dlg.Destroy()

    def OnTest1(self, evt):
        # frame = Gui(None, -1, "Mock: ", size=(500, 500),style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame = MockFrame(1, "Test1", size=(500, 500), style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame.Show()

    def OnTest2(self, evt):
        # frame = Gui(None, -1, "Mock: ", size=(500, 500),style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame = MockFrame(2, "Test2", size=(500, 500), style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame.Show()

    def OnTest3(self, evt):
        # frame = Gui(None, -1, "Mock: ", size=(500, 500),style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame = MockFrame(3, "Test3", size=(500, 500), style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame.Show()

    def OnTest4(self, evt):
        # frame = Gui(None, -1, "Mock: ", size=(500, 500),style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame = MockFrame(4, "Test4", self, size=(500, 500), style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame.Show()

    def OnTest5(self, evt):
        # frame = Gui(None, -1, "Mock: ", size=(500, 500),style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame = MockFrame(5, "Test5", self, size=(500, 500), style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame.Show()

    def OnTest6(self, evt):
        # frame = Gui(None, -1, "Mock: ", size=(500, 500),style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame = MockFrame(6, "Test6", self, size=(500, 500), style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame.Show()

    def OnTest7(self, evt):
        # frame = Gui(None, -1, "Mock: ", size=(500, 500),style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame = MockControlFrame(7, "TestVisualize", self, size=(512, 512), style=wx.DEFAULT_FRAME_STYLE,
                                 name="run a sample")
        frame.Show()

    def OnTest10(self, evt):
        # frame = Gui(None, -1, "Mock: ", size=(500, 500),style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame = MockFrame(10, "Test10", self, size=(500, 500), style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame.Show()

    def OnTestInout(self, evt):
        # frame = Gui(None, -1, "Mock: ", size=(500, 500),style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        frame = MockControlFrame2(0, "TestInout", self, size=(400, 400), style=wx.DEFAULT_FRAME_STYLE,
                                  name="run a sample")
        frame.Show()

    def OnStartUp(self, evt):
        frameobj = {
            "size": (800, 400),
            "style": wx.DEFAULT_FRAME_STYLE
        }
        log.Info("StartUP BlockSize %d  BatchSize %d " % (self.shth, self.batch))
        frame = MockControlFrame3(0, "TestApp", option=frameobj, shid=self.shth, batch=self.batch)
        frame.Show()
        plt.close(0)


class App(WxAsyncApp, wx.lib.mixins.inspection.InspectionMixin):
    def __init__(self, name):
        self.name = name
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        WxAsyncApp.__init__(self)

    def OnInit(self):
        wx.Log.SetActiveTarget(wx.LogStderr())
        # self.SetAssertMode(assertMode)
        self.InitInspection()  # for the InspectionMixin base class
        # frame = wx.Frame(None, -1, "Mock: " + self.name, size=(500, 100),
        #                style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
        # win = Gui(frame)
        # frame.SetSize((640, 480))

        frameobj = {
            "size": (800, 400),
            "style": wx.DEFAULT_FRAME_STYLE
        }
        frame = Gui(0, "p2pOpt", option=frameobj)
        frame.Show()

        # win.SetFocus()
        frame.Bind(wx.EVT_CLOSE, self.OnCloseFrame)
        # self.SetTopWindow(frame)
        self.frame = frame
        # frame.Show(True)
        return True

    def OnExitApp(self, evt):
        self.frame.Close(True)

    def OnCloseFrame(self, evt):
        if hasattr(self, "window") and hasattr(self.window, "ShutdownDemo"):
            self.window.ShutdownDemo()
        evt.Skip()

    def OnWidgetInspector(self, evt):
        wx.lib.inspection.InspectionTool().Show()


def run():
    app = App("")
    loop = get_event_loop()
    loop.run_until_complete(app.MainLoop())


if __name__ == "__main__":
    # app  = App("")
    # loop = get_event_loop()
    # loop.run_until_complete(app.MainLoop())

    # from p2popt.App.gui import *
    run()
