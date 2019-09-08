import wx.glcanvas as glcanvas
import wx
from wxasync.wxasync import *
import wx.lib.sized_controls as sc

from OpenGL.GL import *
from OpenGL.GL.shaders import *

from GLAux.compile import *
from GLAux.query import *
from GLAux.parser import *
from GLAux.vao import *
from GLAux.log import *
from App.config import *
from App.ssbo import *
from App.debug import *

import numpy as np
import matplotlib.pyplot as plt
import time
import gc


class TestObserver:
    def __init__(self):
        self.t1 = False
        self.t2 = False
        self.t3 = False
        self.t4 = False
        self.t5 = False
        self.t6 = False
    def PassT1(self,tf):
        if tf:
            self.t1 = True
            log.Info("<<<<<<<<<<<<<Test1 Pass>>>>>>>>>>>>>>")
        else:
            raise("Error Test1 Failed.")

    def PassT2(self,tf):
        if tf:
            self.t2 = True
            log.Info("<<<<<<<<<<<<<Test2 Pass>>>>>>>>>>>>>>")
        else:
            raise("Error Test2 Failed.")

    def PassT3(self,tf):
        if tf:
            self.t3 = True
            log.Info("<<<<<<<<<<<<<Test3 Pass>>>>>>>>>>>>>>")
        else:
            raise("Error Test3 Failed.")

    def PassT4(self,tf):
        if tf:
            self.t4 = True
            log.Info("<<<<<<<<<<<<<Test4 Pass>>>>>>>>>>>>>>")
        else:
            raise("Error Test4 Failed.")
    def PassT5(self,tf):
        if tf:
            self.t5 = True
            log.Info("<<<<<<<<<<<<<Test5 Pass>>>>>>>>>>>>>>")
        else:
            raise("Error Test5 Failed.")

    def PassT6(self,tf):
        if tf:
            self.t6 = True
            log.Info("<<<<<<<<<<<<<Test6 Pass>>>>>>>>>>>>>>")
        else:
            raise("Error Test6 Failed.")

TO = TestObserver()

class Sampler:
    def __init__(self,seed,para_ra,sep=4):
        self.seed = seed
        self.para_range = para_ra
        self.vth        = len(para_ra)
        self.sep = 4
        np.random.seed(seed)
        self.fig = plt.figure(100)
        self.ax = self.fig.add_subplot(111)
        plt.show()
    def initSeed(self):
        np.random.seed(self.seed)
    def randint(self,n):
        for i, a in enumerate(self.para_range):
            p = a[0] + a[2] * np.random.randint(0, (a[1] - a[0]) / a[2], n)
            #print(i,"  range ",a,"  param  ",p)
            if i == 0:
                l = p
            else:
                l = np.vstack((l, p))
        return np.vstack((l, np.zeros(n))).T
    def roundmax(self,oarg,param,samp_ra,samp_num):
        pid = np.random.choice(np.arange(self.vth), samp_num,replace=False)
        mx = param[oarg[:self.sep], :8]
        for i in range(self.sep):
            log.Info("MaxParameter %s     result %.3f"%(mx[i].tolist(),param[oarg[i], 8]))

        n  = param.shape[0]
        N  = n//self.sep
        for i, a in enumerate(self.para_range):
            if i in pid:
                ra = int(samp_ra * (a[1] - a[0]) / a[2])
                p = []
                for j in range(self.sep):
                    mu = mx[j,i] - ra / 2
                    if mu < a[0]: mu = a[0]
                    log.Log("sampling mu %.4f  0-%d  %d "%(mu,ra,N))
                    p += (mu + a[2] * np.random.randint(0, ra, N)).tolist()
            else:
                p = []
                for j in range(self.sep):
                    p += (np.ones(N)*mx[j,i]).tolist()

            if i == 0:
                l = p
            else:
                l = np.vstack((l, p))

        return np.vstack((l, np.zeros(n))).T
    def result(self,asset):
        self.ax.cla()
        def onpick3(event):
            ind = event.ind
            log.Info('Output : path %s  result %s'%(ind, asset[ind]))
        col = self.ax.scatter(np.arange(len(asset)),asset,picker=True)
        # fig.savefig('pscoll.eps')
        self.fig.canvas.mpl_connect('pick_event', onpick3)

        #plt.plot(asset)
        # log.Log("x  %s"%asset[i, 0, 1:l].tolist())
        # log.Log("y  %s"%asset[i, 1, 1:l].tolist())


class Mock(glcanvas.GLCanvas):

    def __init__(self, *args, **kwargs):
        glcanvas.GLCanvas.__init__(self, *args, **kwargs)
        self.context  = glcanvas.GLContext(self)
        self.frame = args[0]
        self.comp = None
        self.ssbo = None
        self.pipe = None
        self.pipe_fatou = None
        self.active = None
        self.lastx    = self.x = 30
        self.lasty    = self.y = 30
        self.size     = None
        self.calcT8   = False
        self.redraw      = -1
        self.SetBackgroundStyle(wx.BG_STYLE_PAINT)
        self.Bind(wx.EVT_SIZE, self.OnSize)
        #self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_LEFT_DOWN, self.OnMouseDown)
        self.Bind(wx.EVT_LEFT_UP, self.OnMouseUp)
        self.Bind(wx.EVT_MOTION, self.OnMouseMotion)
        #self.Bind(wx.EVT_CLOSE, self.OnDestroy)
        self.Bind(wx.EVT_WINDOW_DESTROY, self.OnDestroy)
    def OnClose(self, event):
        print('In OnClose')
        event.Skip()
    def OnSize(self, event):
        self.DoSetViewport()
        #wx.CallAfter(self.DoSetViewport)
        if self.redraw != -1:
            if self.redraw==0:
                self.TestUV()
            elif self.redraw==1:
                self.Test_Draw1()
            elif self.redraw == 2:
                self.Test_Draw4()
            elif self.redraw == 3:
                self.Test_DrawAsset()
        event.Skip()
    def DoSetViewport(self):
        size = self.size = self.GetClientSize()
        self.SetCurrent(self.context)
        glViewport(0, 0, size.width, size.height)
    def Call(self,N):
        #dc = wx.PaintDC(self)
        #dc.DrawLine(0, 0, 100, 100)
        self.SetCurrent(self.context)
        if N == "Hist":
            self.gpHist()
        elif N == "Ratio":
            self.gpRatio()
        elif N == "bzGP":
            self.bzGP()
        self.after()
    def OnMouseDown(self, evt):
        self.CaptureMouse()
        self.x, self.y = self.lastx, self.lasty = evt.GetPosition()
        #print("Mouse ",self.x,self.y)
    def OnMouseUp(self, evt):
        self.ReleaseMouse()
    def OnMouseMotion(self, evt):
        if evt.Dragging() and evt.LeftIsDown():
            self.lastx, self.lasty = self.x, self.y
            self.x, self.y = evt.GetPosition()
            self.Refresh(False)
    def OnContext(self):
        self.SetCurrent(self.context)
    def after(self):
        if self.size is None:
            self.size = self.GetClientSize()
        self.SwapBuffers()
    def Link(self,cls,type =0):
        self.link = cls
        self.SetCurrent(self.context)
        self.InitGL()
    def OnDestroy(self, event):
        #glDeleteVertexArrays(1, [vao]);
        self.SetCurrent(self.context)
        if self.comp != None:
            self.comp.delete()
            self.comp = None
        if self.ssbo != None:
            self.ssbo.delete()
            self.ssbo = None
        if self.pipe != None:
            self.pipe.delete()
            self.pipe = None
        if self.pipe_fatou != None:
            self.pipe_fatou.delete()
            self.pipe_fatou = None
        #self.pipe.delete()
        #self.vao.delete()
        log.Info('Mock Destroy <====  ' + self.TYPE)
        if event != None:event.Skip()
    def uniform(self,n,val= None):

        self.SetCurrent(self.context)
        if n == "TOTAL":
            self.TOTAL = int(val)
            self.comp.bind(self.comp.name['T2'])
            glUniform1i(glGetUniformLocation(self.comp.PG[0],n),self.TOTAL)
        elif n == "beta":
            self.comp.bind(0)
            self.beta = float(val)
            glUniform1f(glGetUniformLocation(self.comp.PG[0], "beta"),self.beta);
            self.comp.bind(1)
            glUniform1f(glGetUniformLocation(self.comp.PG[1], "beta"), self.beta);
        elif n == "npoints":
            self.comp.bind(0)
            glUniform1i(glGetUniformLocation(self.comp.PG[0], "npoints"),int(val));
            print("Add Point   ",val)
            self.npoints = int(val)
            self.comp.bind(1)
            glUniform1i(glGetUniformLocation(self.comp.PG[1], "npoints"),int(val));
        elif n == "ipoints":
            self.comp.bind(0)
            glUniform1i(glGetUniformLocation(self.comp.PG[0], "ipoints"),int(val));
            #self.comp.bind(1)
            #glUniform1i(glGetUniformLocation(self.comp.PG[1], "ipoints"),int(val));
        elif n == "ADD":
            self.comp.bind(0)
            glUniform1i(glGetUniformLocation(self.comp.PG[0], "ADD"),int(val));
        elif n== "range":
            N = 300

            self.comp.bind(0)
            l = int(len(val)/4)
            if(l > N):
                val = val[-(N*4):]
            print("length   range   ", l)
            print("length   range   ", val)
            glUniform1i(glGetUniformLocation(self.comp.PG[0], "irange"), l);
            glUniform4iv(glGetUniformLocation(self.comp.PG[0], "range"), l, val);
            self.range = np.array(val).reshape((l,4)).astype(np.int32)
            #glUniform2iv(glGetUniformLocation(self.comp.PG[0], "range"), 5, np.arange(10).astype(np.int32).ctypes.data_as(ctypes.POINTER(ctypes.c_long)));
        elif n == "seed":
            self.comp.bind(0)
            glUniform2f(glGetUniformLocation(self.comp.PG[0], "seed"),*np.random.rand(2));
    def InitGL(self):
        #vert = "F:\MT5\Charm2019\Recognition\GLAux\\glsl\\bz\\vert.glsl"
        #frag = "F:\MT5\Charm2019\Recognition\GLAux\\glsl\\bz\\frag.glsl"
        #self.pipe = glau.Pipe([vert, frag], [GL_VERTEX_SHADER, GL_FRAGMENT_SHADER])
        #vao = create_vao2()
        #self.vao =  glau.Vao()
        #self.vao.pos2d()
        #node1 = "F:\MT5\Charm2019\Recognition\GLAux\\glsl\\bz\\node1.comp"
        #node2 = "F:\MT5\Charm2019\Recognition\GLAux\\glsl\\bz\\range.comp"
        #self.comp    = Compute([node1,node2])
        self.ssbo    = Ssbo()
        self.ssbo.initialize()

        #st = np.random.randint(0, 1000, 100)
        #ed = st+ 100
        #data = np.vstack((st, st + 100)).T.flatten().astype(np.int32)
        #self.comp.bind(0)
        #glUniform2iv(glGetUniformLocation(self.comp.PG[0], "range"), int(len(data)/2),data);
        #glUniform1iv(glGetUniformLocation(self.comp.PG[0], "range"), 5,np.arange(5).astype(np.int32));
        self.ini = True
    def Test1(self):
        # < 1000 billion times
        self.Shid = 1024
        self.TYPE = "Test1"
        log.Info("Start Test1 1000 billion AtomicAdd")
        self.SetCurrent(self.context)
        self.spec = Spec()
        #print(glGetIntegerv(GL_MAX_COMPUTE_SHADER_STORAGE_BLOCKS))
        self.spec.ComputeShader()

        T1 = "../GLAux/glsl/Mock/T1.glsl"
        self.comp      = Compute([T1])
        self.comp.name = {'T1': 0 }

        self.ssbo = Ssbo()
        self.ssbo.initialize()

        self.comp.bind(self.comp.name['T1'])

        csum = []
        disp = [128,1024,64]
        for i in range(10):
            start = time.time()
            self.ssbo.G2C(tag="clear_ac")
            glDispatchCompute(*disp)
            glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
            ac = self.ssbo.G2C(tag="np_ac")
            elapsed_time = time.time() - start
            cs = np.alltrue([disp[0] * 1024 == i for i in ac])
            log.Warning("Test1 Result  %d (atomicAdd)times  elapsed_time:%.4f[sec]  CheckSum %s  "%(self.Shid*disp[0]*disp[1]*disp[2],elapsed_time,cs))
            csum.append(cs)

        self.frame.Destroy()
        TO.PassT1(np.alltrue(csum))
        gc.collect()
    def Test2(self):
        self.TYPE = "Test2"
        if not TO.t1:
            log.Warning("Please Execute Test1 !!!")
            self.frame.Destroy()
            gc.collect()
            return
        # < One trillion operate
        self.Shid = 1024

        log.Info("Start Test2 trillion calculation(exponential)")
        self.SetCurrent(self.context)

        T2 = "../GLAux/glsl/Mock/T2.glsl"
        self.comp      = Compute([T2])
        self.comp.name = {'T2': 0 }

        disp = [1, 128, 16]

        self.ssbo = Ssbo()
        self.ssbo.Set_data()
        self.ssbo.Set_AC(size = self.Shid*disp[2])

        self.TOTAL = 50000
        self.comp.bind(self.comp.name['T2'])
        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['T2']], "TOTAL"),self.TOTAL)


        csum = []
        N = 100
        log.Warning("Testing.......")
        start = time.time()

        for i in range(N):

            self.ssbo.G2C(tag="clear_ac")
            glDispatchCompute(*disp)
            glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
            ac = self.ssbo.G2C(tag="np_ac").reshape(disp[2],self.Shid)[:,:disp[1]]
            cs = np.alltrue([disp[0]*1024 == i for i in ac])
            csum.append(cs)

        elapsed_time = time.time() - start
        log.Warning("Test2 Result dispatch %d * %d (expcalc)times elapsed_time:%.4f[sec]  CheckSum %s  " % (N,self.TOTAL * 100 * self.Shid * disp[0] * disp[1] * disp[2], elapsed_time, csum))
        self.frame.Destroy()
        gc.collect()

        TO.PassT2(np.alltrue(csum))
    def Test3(self):
        # Global Memory vs Shared Memory
        self.TYPE = "Test3"
        if not TO.t2:
            log.Warning("Please Execute Test2 !!!")
            self.frame.Destroy()
            gc.collect()
            return
        # < One trillion operate
        self.Shid = 1024

        log.Info("Start Test3  MemoryAccess(GlobalMemory vs SharedMemory (uint))")
        self.SetCurrent(self.context)

        T3 = "../GLAux/glsl/Mock/T3.glsl"
        self.comp      = Compute([T3])
        self.comp.name = {'T3': 0 }

        disp = [1, 128, 16]

        self.ssbo = Ssbo()
        self.ssbo.Set_data()
        self.ssbo.Set_AC(size = self.Shid*disp[2])

        self.TOTAL = 4096;#self.ssbo.Prop["data"][3][0]
        self.comp.bind(self.comp.name['T3'])
        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['T3']], "TOTAL"),self.TOTAL)
        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['T3']], "GLOBAL"), 1)


        csum = []
        N = 100
        log.Warning("Testing Global.......")
        start = time.time()

        for i in range(N):

            self.ssbo.G2C(tag="clear_ac")
            glDispatchCompute(*disp)
            glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
            ac = self.ssbo.G2C(tag="np_ac").reshape(disp[2],self.Shid)[:,:disp[1]]
            cs =  len(set(ac.flatten())) == 1
            csum.append(cs)

        elapsed_time = time.time() - start
        log.Warning("Test3 Result dispatch %d * %d (ssbo access)times elapsed_time:%.4f[sec]  Val %d CheckSum %s  " % (N,self.TOTAL  * self.Shid * disp[0] * disp[1] * disp[2], elapsed_time, ac[0,0],csum))

        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['T3']], "GLOBAL"), 0)

        csum = []
        N = 100
        log.Warning("Testing Shared.......")
        start = time.time()

        for i in range(N):
            self.ssbo.G2C(tag="clear_ac")
            glDispatchCompute(*disp)
            glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
            ac = self.ssbo.G2C(tag="np_ac").reshape(disp[2], self.Shid)[:, :disp[1]]
            cs = len(set(ac.flatten())) == 1
            csum.append(cs)

        elapsed_time = time.time() - start
        log.Warning("Test3 Result dispatch %d * %d (ssbo access)times elapsed_time:%.4f[sec]  Val %d CheckSum %s  " % (
        N, self.TOTAL * self.Shid * disp[0] * disp[1] * disp[2], elapsed_time, ac[0, 0], csum))

        #d = self.ssbo.G2C("np_data")[:int(self.TOTAL), :]


        d = self.ssbo.G2C("data")
        mod31 = np.uint32(2147483647)
        mod15 = np.uint32(32768)
        a = np.uint32(0)
        csum = []
        csum2 = []
        #print(type(ctypes.c_float(d[i].date)),type(self.ssbo.data[i, 2:]))
        for i in range(1,self.TOTAL):
            b  = np.uint32(d[i].date*np.uint(100000))
            #b1 = round(np.float32(d[i].open), 5)
            #b2 = np.uint(round( (round(self.ssbo.data[i, 2],5)  + round(self.ssbo.data[i, 3],5) + round(self.ssbo.data[i, 4],5))/ np.float32(3.),5)*100000)
            a = (a + b) % mod31
            #log.Log("%d Th NP_DATA  GLOBAL %.7f  Shared %.7f   %s"% (i,b,b2,round(b,5) == round(b2,5)))
            csum.append(round(np.float32(d[i].date),5) == round(np.float32(d[i].open),5))

        """
        for i in range(1,self.TOTAL):
            b   = d[i,0]
            a   = (a + np.uint(b * 100000)) % mod31
            b2  = np.sum(self.ssbo.data[i,2:])/np.float(3.)
            #log.Log(" %d Th NP_DATA  %.7f  %.7f  %s" % (i,d[i, 2],self.ssbo.data[i,2],round(d[i, 2],5) == round(self.ssbo.data[i,2],5)))
            log.Log("%d Th NP_DATA  GLOBAL %.7f  Shared %.7f   %s"% (i,b,b2,round(b,5) == round(b2,5)))
            #log.Log("%d Th NP_DATA  GLOBAL %d  Shared %d  CPU %d     Equal %s   "%(i,int(d[i,0]*10**5),int(d[i,1]*10**5),int(b2*10**5),str(round(d[i,0],5))==str(round(d[i,1],5))==str(round(b2,5))))
            csum2.append(int(d[i,0]*10**5)==int(d[i,1]*10**5)==int(b2*10**5))
            csum.append(round(d[i, 2],5) == round(self.ssbo.data[i,2],5))
            #csum.append(str(round(d[i, 0], 5)) == str(round(d[i, 1], 5)) == str(round(b2, 5)))
        """
        log.Log("NP_DATA ===> ANS  %u  CPU == GlobalMemrory == SharedMemory  %s  %s  where  %s" % ((a%mod15)*np.uint32(1024),np.alltrue(csum),np.alltrue(csum2),np.where(np.array(csum)==False)[0].tolist()))
        self.frame.Destroy()
        gc.collect()

        TO.PassT3(np.alltrue(csum))
    def Test4(self):
        # Global Memory vs Shared Memory
        self.TYPE = "Test4"
        if not TO.t3:
            log.Warning("Please Execute Test4 !!!")
            self.frame.Destroy()
            gc.collect()
            return
        # < One trillion operate
        self.Shid = 1024

        log.Info("Start Test4 MemoryAccess(GlobalMemory vs SharedMemory (float))")
        self.SetCurrent(self.context)

        T4 = "../GLAux/glsl/Mock/T4.glsl"
        self.comp      = Compute([T4])
        self.comp.name = {'T4': 0 }

        disp = [1, 128, 16]

        self.ssbo = Ssbo()
        self.ssbo.Set_data()
        self.ssbo.Set_AC(size = self.Shid*disp[2])

        self.TOTAL = 4096#self.ssbo.Prop["data"][3][0]
        self.comp.bind(self.comp.name['T4'])
        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['T4']], "TOTAL"),self.TOTAL)
        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['T4']], "GLOBAL"), 1)


        csum = []
        N = 100
        log.Warning("Testing Global.......")
        start = time.time()

        for i in range(N):

            self.ssbo.G2C(tag="clear_ac")
            glDispatchCompute(*disp)
            glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
            ac = self.ssbo.G2C(tag="np_ac").reshape(disp[2],self.Shid)[:,:disp[1]]
            cs =  len(set(ac.flatten())) == 1
            csum.append(cs)

        elapsed_time = time.time() - start
        log.Warning("Test4 Result dispatch %d * %d (ssbo access)times elapsed_time:%.4f[sec]  Val %d CheckSum %s  " % (N,self.TOTAL  * self.Shid * disp[0] * disp[1] * disp[2], elapsed_time, ac[0,0],csum))


        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['T4']], "GLOBAL"), 0)

        csum = []
        N = 100
        log.Warning("Testing Shared.......")
        start = time.time()

        for i in range(N):
            self.ssbo.G2C(tag="clear_ac")
            glDispatchCompute(*disp)
            glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
            ac = self.ssbo.G2C(tag="np_ac").reshape(disp[2], self.Shid)[:, :disp[1]]
            cs = len(set(ac.flatten())) == 1
            csum.append(cs)

        elapsed_time = time.time() - start
        log.Warning("Test4 Result dispatch %d * %d (ssbo access)times elapsed_time:%.4f[sec]  Val %d CheckSum %s  " % (
        N, self.TOTAL * self.Shid * disp[0] * disp[1] * disp[2], elapsed_time, ac[0, 0], csum))

        #d = self.ssbo.G2C("np_data")[:int(self.TOTAL), :]


        d = self.ssbo.G2C("data")

        v = np.float32(d[0].date)
        Y  = [v]
        v2 = np.float32(d[0].open)
        Y2 = [v2]
        ema = np.float32(2./(1. + 26.))
        for i in range(1,self.TOTAL):
            v2  = np.float32(v2 + ema *(np.float32(d[i].open) - v2))
            Y2.append(v2)
            Y.append(np.float32(d[i].date))
        log.Log("NP_DATA ===> last value  GPU%.6f<=>CPU%.6f " % (Y[-1],Y2[-1]))
        self.frame.gui.ax1.cla()
        self.frame.gui.ax1.plot(Y,label="GPU")
        self.frame.gui.ax1.plot(Y2,label="CPU")
        self.frame.gui.ax1.legend()


        self.frame.Destroy()
        gc.collect()

        TO.PassT4(np.alltrue(csum))
    def Test5(self):
        # Global Memory vs Shared Memory
        self.TYPE = "Test5"
        if not TO.t4:
            log.Warning("Please Execute Test4 !!!")
            #self.frame.Destroy()
            #gc.collect()
            #return
        # < One trillion operate


        log.Info("Start Test5 Block Size Design ")

        disp = [1, 2, 2]
        self.Shid  = self.frame.gui.shth
        self.TOTAL = 2048  # self.ssbo.Prop["data"][3][0]

        self.SetCurrent(self.context)
        cr = ConstRender()
        CONST = {
            "SHXTH": self.Shid,
            "SHYTH": 1,
            "SHZTH": 1,
            "SHRTH": self.TOTAL,
            "TOTAL": self.TOTAL
        }
        cr.render("Mock1/parameter.tpl", CONST)

        T5 = "../GLAux/glsl/Mock/T5.glsl"
        self.comp      = Compute([T5])
        self.comp.name = {'T5': 0 }



        self.ssbo = Ssbo()
        self.ssbo.Set_data()
        self.ssbo.Set_AC(size = self.Shid*mul(disp))


        self.comp.bind(self.comp.name['T5'])

        csum = []
        N = 10
        log.Warning("Testing BlockDesign.......\n%s"%(dictString(CONST)))
        start = time.time()

        for i in range(N):
            self.ssbo.G2C(tag="clear_ac")
            glDispatchCompute(*disp)
            glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
            ac = self.ssbo.G2C(tag="np_ac")
            cs = len(set(ac.flatten())) == 1
            csum.append(cs)

        elapsed_time = time.time() - start
        log.Warning("Test5 Result shared (%d) dispatch (%d , %d  , %d) %d times  Inner(%d times)  elapsed_time:%.4f[sec]  Val %d CheckSum %s  " % (
         self.Shid ,disp[0] , disp[1] ,disp[2],N,self.TOTAL,elapsed_time, ac[0], csum))

        #d = self.ssbo.G2C("np_data")[:int(self.TOTAL), :]


        d = self.ssbo.G2C("data")

        v = np.float32(d[0].date)
        Y  = [v]
        v2 = np.float32(d[0].open)
        Y2 = [v2]
        ema = np.float32(2./(1. + 26.))
        for i in range(1,self.TOTAL):
            v2  = np.float32(v2 + ema *(np.float32(d[i].open) - v2))
            Y2.append(v2)
            Y.append(np.float32(d[i].date))
        log.Log("NP_DATA ===> last value  GPU%.6f<=>CPU%.6f " % (Y[-1],Y2[-1]))
        self.frame.gui.ax1.cla()
        self.frame.gui.ax1.plot(Y,label="GPU")
        self.frame.gui.ax1.plot(Y2,label="CPU")
        self.frame.gui.ax1.legend()

        self.frame.Destroy()
        gc.collect()

        TO.PassT5(np.alltrue(csum))
    def Test6(self):
        # Global Memory vs Shared Memory
        self.TYPE = "Test6"
        if not TO.t5:
            log.Warning("Please Execute Test5 !!!")
            #self.frame.Destroy()
            #gc.collect()
            #return
        # < One trillion operate


        log.Info("Start Test6 Block Size Design ")

        disp = [1, 2, 2]
        self.Shid  = self.frame.gui.shth
        self.TOTAL = 2048  # self.ssbo.Prop["data"][3][0]

        self.SetCurrent(self.context)
        cr = ConstRender()
        CONST = {
            "SHXTH": self.Shid,
            "SHYTH": 1,
            "SHZTH": 1,
            "SHRTH": self.TOTAL,
            "TOTAL": self.TOTAL
        }
        cr.render("Mock1/parameter.tpl", CONST)

        T6 = "../GLAux/glsl/Mock/T6.glsl"
        self.comp      = Compute([T6])
        self.comp.name = {'T6': 0 }



        self.ssbo = Ssbo()
        self.ssbo.Set_data()
        self.ssbo.Set_AC(size = self.Shid*mul(disp))


        self.comp.bind(self.comp.name['T6'])

        csum = []
        N = 10
        log.Warning("Testing BlockDesign.......\n%s"%(dictString(CONST)))
        start = time.time()

        for i in range(N):
            self.ssbo.G2C(tag="clear_ac")
            glDispatchCompute(*disp)
            glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
            ac = self.ssbo.G2C(tag="np_ac")
            cs = len(set(ac.flatten())) == 1
            csum.append(cs)

        elapsed_time = time.time() - start
        log.Warning("Test6 Result shared (%d) dispatch (%d , %d  , %d) %d times  Inner(%d times)  elapsed_time:%.4f[sec]  Val %d CheckSum %s  " % (
         self.Shid ,disp[0] , disp[1] ,disp[2],N,self.TOTAL,elapsed_time, ac[0], csum))

        #d = self.ssbo.G2C("np_data")[:int(self.TOTAL), :]




        self.frame.Destroy()
        gc.collect()

        TO.PassT6(np.alltrue(csum))
    def Test7(self):
        # Global Memory vs Shared Memory
        if self.active == "T7":return
        if self.active != None:
            self.OnDestroy(None)
            self.active = None
        self.TYPE = "Test7"
        if not TO.t6:
            log.Warning("Please Execute Test6 !!!")
            #self.frame.Destroy()
            #gc.collect()
            #return
        # < One trillion operate


        log.Info("Start Test7 Block Size Design ")

        self.disp = disp = [1, 2, 2]
        self.Shid  = self.frame.gui.shth
        self.TOTAL = 2048  # self.ssbo.Prop["data"][3][0]

        self.SetCurrent(self.context)

        cr = ConstRender()
        CONST = {
            "SHXTH": self.Shid,
            "SHYTH": 1,
            "SHZTH": 1,
            "SHRTH": self.TOTAL,
            "TOTAL": self.TOTAL
        }
        cr.render("Mock1/parameter.tpl", CONST)


        CONST = {
            "SEPARATE": disp[1]*disp[2],
        }
        cr.render("Visual/mock1_buffer.tpl", CONST)

        T7       = "../GLAux/glsl/Mock/T7.glsl"
        prepro   = "../GLAux/glsl/Mock/VS/prepro_T0.glsl"
        self.comp      = Compute([T7,prepro])
        self.comp.name = {'T7': 0 ,"PP" : 1}

        vert     = "../GLAux/glsl\\Mock\\VS\\T0.glsl"
        fatou    = "../GLAux/glsl\\Mock\\FS\\fatou.glsl"
        frag     = "../GLAux/glsl\\Mock\\FS\\T0.glsl"
        self.pipe_fatou = Pipe([vert, fatou], [GL_VERTEX_SHADER, GL_FRAGMENT_SHADER])
        self.pipe = Pipe([vert, frag], [GL_VERTEX_SHADER, GL_FRAGMENT_SHADER])
        self.vao =  Vao()
        self.vao.pos2d()

        self.ssbo = Ssbo()
        self.ssbo.Set_data()
        self.ssbo.Set_Vis()
        self.ssbo.Set_Dprop()
        #self.ssbo.Set_AC(size = self.Shid*mul(disp))
        self.active = "T7"
        self.iniDraw = True
    def TestUV(self):

        #log.Log("Test Draw UV")

        self.SetCurrent(self.context)

        self.pipe_fatou.bind()
        self.vao.bind()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_COLOR, GL_SRC_ALPHA)
        glEnable(GL_VERTEX_PROGRAM_POINT_SIZE)
        glEnable(GL_POINT_SPRITE)

        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        #glProgramUniform2f(*self.pipe.vloc("res"),  float(self.size.width), float(self.size.height))
        glProgramUniform1i(*self.pipe.vloc("TYPE"), 1)
        #glProgramUniform1f(*self.pipe.vloc("Zoom"), float(0.))

        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

        self.after()
        self.redraw = 0
        log.Log("Test Draw UV")
    def Test_CalcT7(self):
        self.comp.bind(self.comp.name['T7'])

        csum = []
        N = 1
        #log.Warning("Testing BlockDesign.......\n%s"%(dictString(CONST)))

        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['T7']], "PID"), self.pid)
        start = time.time()
        for i in range(N):
            #self.ssbo.G2C(tag="clear_ac")
            glDispatchCompute(*self.disp)
            glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
            #ac = self.ssbo.G2C(tag="np_ac")
            #cs = len(set(ac.flatten())) == 1
            #csum.append(cs)

        elapsed_time = time.time() - start
        #log.Warning("Test7 Result PID %d shared (%d) dispatch (%d , %d  , %d) %d times  Inner(%d times)  elapsed_time:%.4f[sec]" % (
        # self.pid,self.Shid ,self.disp[0] , self.disp[1] ,self.disp[2],N,self.TOTAL,elapsed_time))
    def Test_Draw4(self):
        stid = self.stid
        wth = self.wth  # self.TOTAL
        #log.Log("TestDraw4  STID  %d  WTH   %d" % (stid, wth))
        self.Test_Draw3(stid, wth)
    def Test_Draw3(self,stid,lth):

        self.SetCurrent(self.context)

        self.comp.bind(self.comp.name['PP'])
        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['PP']], "PROG"),0)
        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['PP']], "LTH"),lth)
        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['PP']], "STID"), stid)


        glDispatchCompute(1, self.disp[1]*self.disp[2], 1)
        glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)

        dprop = self.ssbo.G2C(tag="dprop2")
        #log.Log("Entry Array  %s"%[dprop[0].entry[i + 1] for i in range(dprop[0].entry[0])])
        #log.Log("Exit Array  %s" % [dprop[0].exit[i + 1] for i in range(dprop[0].exit[0])])
        entry = []
        exit  = []

        for p in range(self.disp[1]*self.disp[2]):
            entry.append([])
            exit.append([])
            for i in range(dprop[p].entry[0]):
                e = dprop[p].entry[i + 1]
                if stid <= e and (stid+lth) > e:
                    entry[p].append(i+1)
            for i in range(dprop[p].exit[0]):
                e = dprop[p].exit[i + 1]
                if stid <= e and (stid + lth) > e:
                    exit[p].append(i+1)
        #log.Log("Entry Array  %s "%entry)

        self.pipe.bind()
        self.vao.bind()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_COLOR, GL_SRC_ALPHA)
        glEnable(GL_VERTEX_PROGRAM_POINT_SIZE)
        glEnable(GL_POINT_SPRITE)

        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glProgramUniform2f(*self.pipe.vloc("res"), float(self.size.width), float(self.size.height))
        glProgramUniform1i(*self.pipe.vloc("TYPE"), 0)

        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

        glProgramUniform1i(*self.pipe.vloc("FULL"), int(self.FULL))
        if self.FULL == 0:
            glProgramUniform1i(*self.pipe.vloc("TYPE"), 10)
            glDrawArraysInstanced(GL_LINES, 0, 2, 2)  # self.voxsize[1]);

        #log.Info("##################Draw Status  FULL %d SEPID %d  Total %d " % (self.FULL,self.sepid,self.TOTAL))

        for i in range(4):

            if self.FULL == 1 and self.sepid != i:continue
            glProgramUniform1i(*self.pipe.vloc("SEP"), int(i))
            glProgramUniform1i(*self.pipe.vloc("TYPE"), 2)
            glDrawArraysInstanced(GL_POINTS, 0, 1, int(lth))

            glProgramUniform1i(*self.pipe.vloc("TYPE"), 3)
            glDrawArraysInstanced(GL_LINES, 0, 2, int(lth - 1))

            glProgramUniform1i(*self.pipe.vloc("TYPE"), 4)
            glDrawArraysInstanced(GL_LINES, 0, 2, int(lth - 1))

            if len(entry[i]) >0:
                #log.Log("Entry Point %s "%entry[i])
                glProgramUniform1i(*self.pipe.vloc("Eofs"), entry[i][0])
                glProgramUniform1i(*self.pipe.vloc("TYPE"), 15)
                glDrawArraysInstanced(GL_POINTS, 0, 1, len(entry[i]))
            if len(exit[i])  >0:
                #log.Log("Exit Point %s " % exit[i])
                glProgramUniform1i(*self.pipe.vloc("Eofs"), exit[i][0])
                glProgramUniform1i(*self.pipe.vloc("TYPE"), 16)
                glDrawArraysInstanced(GL_POINTS, 0, 1, len(exit[i]))



        self.after()
        self.redraw = 2
    def Test_Draw1(self):

        self.Test_Draw0(0,self.TOTAL)
    def Test_Draw2(self):

        stid = self.stid
        wth  = self.wth#self.TOTAL

        log.Log("TestDraw2 STID  %d  WTH   %d"%(stid,wth))
        self.Test_Draw0(stid,wth)
        #self.Test_DrawNP()
    def Test_Draw0(self,stid,lth):

        self.SetCurrent(self.context)

        self.comp.bind(self.comp.name['PP'])
        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['PP']], "PROG"),0)
        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['PP']], "LTH"),lth)
        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['PP']], "STID"), stid)


        glDispatchCompute(1, self.disp[1]*self.disp[2], 1)
        glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)

        #prop = self.ssbo.G2C("dprop")
        #for i in range(4):
        #    log.Log("PROP    min %.6f  max　%.6f "%(prop[i].ry[0],prop[i].ry[1]))

        self.pipe.bind()
        self.vao.bind()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_COLOR, GL_SRC_ALPHA)
        glEnable(GL_VERTEX_PROGRAM_POINT_SIZE)
        glEnable(GL_POINT_SPRITE)

        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glProgramUniform2f(*self.pipe.vloc("res"), float(self.size.width), float(self.size.height))
        glProgramUniform1i(*self.pipe.vloc("TYPE"), 0)

        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

        glProgramUniform1i(*self.pipe.vloc("FULL"), int(self.FULL))
        if self.FULL == 0:
            glProgramUniform1i(*self.pipe.vloc("TYPE"), 10)
            glDrawArraysInstanced(GL_LINES, 0, 2, 2)  # self.voxsize[1]);

        #log.Info("##################Draw Status  FULL %d SEPID %d  Total %d " % (self.FULL,self.sepid,self.TOTAL))

        for i in range(4):

            if self.FULL == 1 and self.sepid != i:continue
            glProgramUniform1i(*self.pipe.vloc("SEP"), int(i))
            glProgramUniform1i(*self.pipe.vloc("TYPE"), 2)
            glDrawArraysInstanced(GL_POINTS, 0, 1, int(lth))

            glProgramUniform1i(*self.pipe.vloc("TYPE"), 3)
            glDrawArraysInstanced(GL_LINES, 0, 2, int(lth - 1))

            glProgramUniform1i(*self.pipe.vloc("TYPE"), 4)
            glDrawArraysInstanced(GL_LINES, 0, 2, int(lth - 1))



        self.after()
        self.redraw = 1
    def Test8(self):
        # Global Memory vs Shared Memory
        if self.active == "T8":return
        self.TYPE = "Test8"
        if self.active == "T7":
            self.OnDestroy(None)
            self.active = None

        log.Info("Start Test8 Shader Shared Loop ")

        self.disp = disp = [1, 2, 2]
        self.Shid  = self.frame.gui.shth


        self.SetCurrent(self.context)
        self.ssbo = Ssbo()
        self.ssbo.Set_data()
        self.ssbo.Set_Vis()
        self.ssbo.Set_Dprop()
        self.ssbo.Set_AC(size=self.Shid * mul(disp))


        self.SHRTH = 2048
        self.TOTAL = self.ssbo.Prop["data"][3][0]



        cr = ConstRender()
        CONST = {
            "SHXTH": self.Shid,
            "SHYTH": 1,
            "SHZTH": 1,
            "SHRTH": self.SHRTH,
            "TOTAL": self.TOTAL
        }
        cr.render("Mock1/parameter.tpl", CONST)


        CONST = {
            "SEPARATE": disp[1]*disp[2],
        }

        cr.render("Visual/mock1_buffer.tpl", CONST)

        T8       = "../GLAux/glsl/Mock/T8.glsl"
        prepro   = "../GLAux/glsl/Mock/VS/prepro_T0.glsl"
        self.comp      = Compute([T8,prepro])
        self.comp.name = {'T8': 0 ,"PP" : 1}

        vert     = "../GLAux/glsl\\Mock\\VS\\T0.glsl"
        fatou    = "../GLAux/glsl\\Mock\\FS\\fatou.glsl"
        frag     = "../GLAux/glsl\\Mock\\FS\\T0.glsl"
        self.pipe_fatou = Pipe([vert, fatou], [GL_VERTEX_SHADER, GL_FRAGMENT_SHADER])
        self.pipe = Pipe([vert, frag], [GL_VERTEX_SHADER, GL_FRAGMENT_SHADER])
        self.vao =  Vao()
        self.vao.pos2d()


        #self.ssbo.Set_AC(size = self.Shid*mul(disp))
        self.active = "T8"
        self.iniDraw = True
    def Test_CalcT8(self):

        self.comp.bind(self.comp.name['T8'])

        csum = []
        N = 10
        #log.Warning("Testing BlockDesign.......\n%s"%(dictString(CONST)))

        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['T8']], "PID"), self.pid)
        start = time.time()
        for i in range(N):
            #self.ssbo.G2C(tag="clear_ac")
            glDispatchCompute(*self.disp)
            glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
            ac = self.ssbo.G2C(tag="np_ac")
            cs = len(set(ac.flatten())) == 1
            csum.append(cs)

        elapsed_time = time.time() - start
        log.Warning(
            "Test6 Result shared (%d) dispatch (%d , %d  , %d) %d times  Inner(%d times)  elapsed_time:%.4f[sec]  Val %d CheckSum %s  " % (
                self.Shid, self.disp[0], self.disp[1], self.disp[2], N, self.TOTAL, elapsed_time, ac[0], csum))
        self.calcT8  = True
    def Test_DrawNP(self):
        data = self.ssbo.G2C("np_vis")
        self.frame.gui.ax1.cla()
        self.frame.gui.ax1.plot(data[:,0,0],label="mu")
        self.frame.gui.ax1.plot( data[:,0,1],label="mu2")
        self.frame.gui.ax1.legend()
    def Test9(self):
        # Global Memory vs Shared Memory
        if self.active == "T9":return
        self.TYPE = "Test9"
        if self.active != None:
            self.OnDestroy(None)
            self.active = None

        log.Info("Start Test9 Shader Dealing ")

        self.disp = disp = [1, 2, 2]
        self.Shid  = self.frame.gui.shth


        self.SetCurrent(self.context)
        self.ssbo = Ssbo()
        self.ssbo.Set_data(mt = True)
        self.ssbo.Set_Vis()
        self.ssbo.Set_Dprop2()
        self.ssbo.Set_AC(size=self.Shid * mul(disp))


        self.SHRTH = 2048
        self.TOTAL = self.ssbo.Prop["data"][3][0]


        cr = ConstRender()
        CONST = {
            "SHXTH": self.Shid,
            "SHYTH": 1,
            "SHZTH": 1,
            "SHRTH": self.SHRTH,
            "TOTAL": self.TOTAL
        }
        cr.render("Mock1/parameter.tpl", CONST)


        CONST = {
            "SEPARATE": disp[1]*disp[2],
        }

        cr.render("Visual/mock1_buffer.tpl", CONST)

        T9       = "../GLAux/glsl/Mock/T9.glsl"
        prepro   = "../GLAux/glsl/Mock/VS/prepro_T1.glsl"
        self.comp      = Compute([T9,prepro])
        self.comp.name = {'T9': 0 ,"PP" : 1}

        vert     = "../GLAux/glsl\\Mock\\VS\\T1.glsl"
        fatou    = "../GLAux/glsl\\Mock\\FS\\fatou.glsl"
        frag     = "../GLAux/glsl\\Mock\\FS\\T0.glsl"
        self.pipe_fatou = Pipe([vert, fatou], [GL_VERTEX_SHADER, GL_FRAGMENT_SHADER])
        self.pipe = Pipe([vert, frag], [GL_VERTEX_SHADER, GL_FRAGMENT_SHADER])
        self.vao =  Vao()
        self.vao.pos2d()


        #self.ssbo.Set_AC(size = self.Shid*mul(disp))
        self.active = "T9"
        self.iniDraw = True
    def Test_CalcT9(self):

        self.comp.bind(self.comp.name['T9'])

        csum = []
        N = 10
        #log.Warning("Testing BlockDesign.......\n%s"%(dictString(CONST)))

        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['T9']], "PID"), self.pid)
        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['T9']], "VIS_MODE"), self.vis)
        if self.vis == 1:
            N = 1
        start = time.time()
        for i in range(N):
            self.ssbo.G2C(tag="clear_ac")
            self.ssbo.G2C(tag="clear_dprop")
            glDispatchCompute(*self.disp)
            glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
            ac = self.ssbo.G2C(tag="np_ac").reshape(self.disp[1]*self.disp[2],self.Shid)
            if self.vis == 0:
                for i in range(self.disp[1]*self.disp[2]):
                    log.Log("Test9  Dealing  blocksize %d  dispatch %s  init 10**6  YZID %d  result %s  "%(self.Shid,self.disp,i,ac[i,:]))

        if self.vis != 0:
            log.Log("Test9  Dealing Draw blocksize %d  dispatch %s  init 10**6  YZID %d  result %s  Pid %d " % (
                self.Shid, self.disp, i, ac[:, self.pid],self.pid))


            #cs = len(set(ac.flatten())) == 1
            #csum.append(cs)

        elapsed_time = time.time() - start
        log.Warning(
            "Test9 Result shared (%d) dispatch (%d , %d  , %d) %d times  Inner(%d times)  elapsed_time:%.4f[sec]  CheckSum %s  " % (
                self.Shid, self.disp[0], self.disp[1], self.disp[2], N, self.TOTAL, elapsed_time,  csum))
        self.calcT9  = True
    def Test10(self):
        # Global Memory vs Shared Memory
        if self.active == "T10":return
        self.TYPE = "Test10"
        if self.active != None:
            self.OnDestroy(None)
            self.active = None

        log.Info("Start Test10 Shader Dealing ")

        self.disp = disp = [1, 2, 2]
        self.Shid  = self.frame.gui.shth
        self.deal_size = 200
        self.batch = self.frame.gui.batch

        self.SetCurrent(self.context)
        self.ssbo = Ssbo()
        self.ssbo.Set_data(mt = True)
        self.ssbo.Set_Vis()
        self.ssbo.Set_Dprop2()
        self.ssbo.Set_AC(size=self.Shid * mul(disp))
        self.ssbo.Set_Asset(sep = mul(disp),shid = self.Shid,batch = self.batch)

        self.SHRTH = 2048
        self.TOTAL = self.ssbo.Prop["data"][3][0]

        cr = ConstRender()

        CONST = {
            "SHXTH": self.Shid,
            "SHYTH": 1,
            "SHZTH": 1,
            "SHRTH": self.SHRTH,
            "TOTAL": self.TOTAL
        }

        cr.render("Mock1/parameter.tpl", CONST)


        CONST = {
            "SEPARATE"   : disp[1]*disp[2],
            "ASSETTH": int(self.deal_size * 1.5),
            "DEALTH"  : self.deal_size,
            "BATCHTH" : self.batch,
        }

        cr.render("Visual/mock2_buffer.tpl", CONST)

        T10            = "../GLAux/glsl/Mock/T10.glsl"
        prepro         = "../GLAux/glsl/Mock/VS/prepro_T2.glsl"
        self.comp      = Compute([T10,prepro])
        self.comp.name = {'T10': 0 ,"PP" : 1}

        vert     = "../GLAux/glsl\\Mock\\VS\\T2.glsl"
        frag     = "../GLAux/glsl\\Mock\\FS\\T0.glsl"


        self.pipe = Pipe([vert, frag], [GL_VERTEX_SHADER, GL_FRAGMENT_SHADER])
        self.vao =  Vao()
        self.vao.pos2d()



        self.comp.bind(self.comp.name['T10'])

        csum = []
        N    = self.batch
        #log.Warning("Testing BlockDesign.......\n%s"%(dictString(CONST)))

        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['T10']], "PID"), -1)
        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['T10']], "VIS_MODE"), 0)

        start = time.time()
        for i in range(N):
            self.ssbo.G2C(tag="clear_ac")
            self.ssbo.G2C(tag="clear_dprop")
            glDispatchCompute(*self.disp)
            glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
            ac = self.ssbo.G2C(tag="np_ac").reshape(self.disp[1]*self.disp[2],self.Shid)
            if True:
                for i in range(self.disp[1]*self.disp[2]):
                    log.Log("Test10  Dealing  blocksize %d  dispatch %s  init 10**6  YZID %d  result %s  "%(self.Shid,self.disp,i,ac[i,:]))



        elapsed_time = time.time() - start
        log.Warning(
            "Test10 Result shared (%d) dispatch (%d , %d  , %d) %d times  Inner(%d times)  elapsed_time:%.4f[sec]  CheckSum %s  " % (
                self.Shid, self.disp[0], self.disp[1], self.disp[2], N, self.TOTAL, elapsed_time,  csum))



        #self.ssbo.Set_AC(size = self.Shid*mul(disp))
        self.frame.Destroy()
        gc.collect()
        self.iniDraw = True

    def TestAsset(self):
        # Global Memory vs Shared Memory
        if self.active == "Tasset":return
        self.TYPE = "Tasset"
        if self.active != None:
            self.OnDestroy(None)
            self.active = None

        log.Info("Start Tasset Shader Dealing ")

        self.disp = disp = [1, 2, 2]
        self.Shid  = self.frame.gui.shth
        self.deal_size = 200
        self.batch = self.frame.gui.batch
        self.vth   = 8


        self.SetCurrent(self.context)
        self.ssbo = Ssbo()
        self.ssbo.Set_data(mt = True)
        self.ssbo.Set_Vis()
        self.ssbo.Set_Dprop2()
        self.ssbo.Set_AC(size=self.Shid * mul(disp))
        self.ssbo.Set_Asset(sep = mul(disp),shid = self.Shid,batch = self.batch)
        self.ssbo.Set_InOut(sep = mul(disp),shid = self.Shid,batch = self.batch, vth=self.vth)

        self.SHRTH = 2048
        self.TOTAL = self.ssbo.Prop["data"][3][0]

        cr = ConstRender()

        CONST = {
            "SHXTH": self.Shid,
            "SHYTH": 1,
            "SHZTH": 1,
            "SHRTH": self.SHRTH,
            "TOTAL": self.TOTAL
        }

        cr.render("Mock1/parameter.tpl", CONST)

        CONST = {
            "SHXTH": self.Shid,
            "SHYTH": 1,
            "SHZTH": 1,
            "SHRTH": self.SHRTH,
            "TOTAL": self.TOTAL
        }

        cr.render("Mock1/parameter_vf.tpl", CONST)


        CONST = {
            "SEPARATE"   : disp[1]*disp[2],
            "DEALTH"  : self.deal_size,
            "ASSETTH":  int(self.deal_size*1.5),
            "BATCHTH" : self.batch,
        }

        cr.render("Visual/mock2_buffer.tpl", CONST)


        CONST = {
            "VTH"   : self.vth,
        }

        cr.render("Mock1/inout.tpl", CONST)

        Tasset            = "../GLAux/glsl/Mock/Tasset.glsl"
        prepro         = "../GLAux/glsl/Mock/VS/prepro_T2.glsl"
        self.comp      = Compute([Tasset,prepro])
        self.comp.name = {'Tasset': 0 ,"PP" : 1}

        vert     = "../GLAux/glsl\\Mock\\VS\\T2.glsl"
        frag     = "../GLAux/glsl\\Mock\\FS\\T0.glsl"

        self.pipe = Pipe([vert, frag], [GL_VERTEX_SHADER, GL_FRAGMENT_SHADER])
        self.vao =  Vao()
        self.vao.pos2d()

        self.Samp = Sampler(12345,param_range)

        #self.ssbo.Set_AC(size = self.Shid*mul(disp))

        gc.collect()
        self.iniDraw = True
    def Test_CalcTasset(self,para_mode =0,mode = None):

        self.SetCurrent(self.context)

        self.comp.bind(self.comp.name['Tasset'])

        csum = []
        N = self.batch
        # log.Warning("Testing BlockDesign.......\n%s"%(dictString(CONST)))

        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['Tasset']], "PID"), -1)
        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['Tasset']], "VIS_MODE"), 2)

        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['Tasset']], "PARA_MODE"), para_mode)
        if para_mode == 1:
            self.Test_Input(mode)
        #self.Test_Input()

        start = time.time()
        self.ssbo.G2C(tag="clear_asset")
        for i in range(N):
            glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['Tasset']], "BID"), int(i))
            self.ssbo.G2C(tag="clear_ac")
            self.ssbo.G2C(tag="clear_dprop")
            glDispatchCompute(*self.disp)
            glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
            ac = self.ssbo.G2C(tag="np_ac").reshape(self.disp[1] * self.disp[2], self.Shid)
            if True:
                for i in range(self.disp[1] * self.disp[2]):
                    log.Log("Test asset  Dealing  blocksize %d batchsize %d dispatch %s  init 10**6  YZID %d  result %s  " % (
                    self.Shid, self.batch,self.disp, i, ac[i, :]))

        elapsed_time = time.time() - start
        log.Warning(
            "Test asset Result shared (%d) dispatch (%d , %d  , %d) %d times  Inner(%d times)  elapsed_time:%.4f[sec]  CheckSum %s  " % (
                self.Shid, self.disp[0], self.disp[1], self.disp[2], N, self.TOTAL, elapsed_time, csum))

        #self.Test_Input("out")
    def Test_DrawAsset(self):

        stid = 0
        lth  = self.TOTAL
        self.SetCurrent(self.context)

        self.comp.bind(self.comp.name['PP'])
        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['PP']], "PROG"),1)
        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['PP']], "LTH"),lth)
        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['PP']], "STID"), stid)


        glDispatchCompute(1, self.disp[1]*self.disp[2], 1)
        glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)

        dprop = self.ssbo.G2C(tag="dprop2")
        for i in range(4):
            log.Log("Entry Array  %s"%[dprop[i].ry[j] for j in range(2)])
        #log.Log("Exit Array  %s" % [dprop[0].exit[i + 1] for i in range(dprop[0].exit[0])])
        asset = self.ssbo.G2C(tag="np_asset")
        """
        import matplotlib.pyplot as plt
        plt.figure()
        for i in range(len(asset)):
            l = int(asset[i, 0, 0])
            #print(i," lth  ",l)
            if l > 300:l = 300
            plt.plot(asset[i, 0, 1:l],asset[i, 1, 1:l])
            #log.Log("x  %s"%asset[i, 0, 1:l].tolist())
            #log.Log("y  %s"%asset[i, 1, 1:l].tolist())
        plt.show()
        """
        self.pipe.bind()
        self.vao.bind()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_COLOR, GL_SRC_ALPHA)
        glEnable(GL_VERTEX_PROGRAM_POINT_SIZE)
        glEnable(GL_POINT_SPRITE)

        glClearColor(0, 0, 0, 1)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glProgramUniform2f(*self.pipe.vloc("res"), float(self.size.width), float(self.size.height))
        glProgramUniform1i(*self.pipe.vloc("TYPE"), 0)

        glDrawArrays(GL_TRIANGLE_STRIP, 0, 4)

        glProgramUniform1i(*self.pipe.vloc("FULL"), int(self.FULL))
        if self.FULL == 0:
            glProgramUniform1i(*self.pipe.vloc("TYPE"), 10)
            glDrawArraysInstanced(GL_LINES, 0, 2, 2)  # self.voxsize[1]);

        #log.Info("##################Draw Status  FULL %d SEPID %d  Total %d " % (self.FULL,self.sepid,self.TOTAL))

        for i in range(4):

            if self.FULL == 1 and self.sepid != i:continue
            glProgramUniform1i(*self.pipe.vloc("SEP"), int(i))
            glProgramUniform1i(*self.pipe.vloc("TYPE"), 20)

            for j in range(self.batch * self.Shid):
                lth = asset[self.batch * self.Shid * i + j, 0, 0]
                glProgramUniform1i(*self.pipe.vloc("Eofs"), j)
                if lth > 2:
                    glDrawArraysInstanced(GL_LINES, 0, 2, int(lth - 2))
                #glDrawArraysInstanced(GL_POINTS, 0, 1, int(lth))



        self.Test_Input("out")

        self.after()
        self.redraw = 3
    def Test_Input(self,mode = None):
        """
        input  :  8
        output :  1
        :return:
        """

        param_range =[
            [5,60,1],[5,100,1],[5,50,1.2],[12,120,1],[12,120,1],[21,210,1],[0.005,0.01,0.001],[0.1,0.5,0.05]
        ]
        N = self.Shid * self.batch

        if mode == "ini":

            param = self.Samp.randint(N*mul(self.disp))
            #param = np.arange(N*mul(self.disp)*9).reshape(N*mul(self.disp),9).astype(np.float)
            #param = np.ones(N * mul(self.disp) * 9).reshape(N * mul(self.disp), 9).astype(np.float32)
            self.ssbo.G2C("set_io", param)
            #for i in range(len(param)):
        elif mode == "max" :
            self.SetCurrent(self.context)
            param = self.ssbo.G2C("np_io")

            o    = param[:, 8].flatten()
            log.Log("param output  %s" %o.tolist())
            oarg = np.argsort(o)[::-1]
            param = self.Samp.roundmax(oarg,param,self.samp_ra,self.samp_num)
            self.ssbo.G2C("set_io", param)

        elif mode == "out":
            param = self.ssbo.G2C("np_io")
            o = param[:, 8].flatten() #.reshape(mul(self.disp),N)
            self.Samp.result(o)
            #for i in range(mul(self.disp)):
            #    self.Samp.result(o[i,:])
        else:
            param = self.ssbo.G2C("np_io")

        i = 0
        log.Warning("%d th  output %.3f input %s"%(i, param[i, 8], param[i, :8]))
        i = N*mul(self.disp)-1
        log.Warning("%d th  output %.3f input %s"%(i, param[i, 8], param[i, :8]))
    def TestVisual(self):
        # Global Memory vs Shared Memory
        if self.active == "TVisual":return
        self.TYPE = "TestVisual"
        if self.active != None:
            self.OnDestroy(None)
            self.active = None

        log.Info("Start TestVisual Shader Dealing ")

        self.disp = disp = [1, 2, 2]
        self.Shid  = self.frame.gui.shth
        self.batch = self.frame.gui.batch
        self.sep   = mul(self.disp)
        self.vth = 8

        self.SetCurrent(self.context)
        self.ssbo = Ssbo()
        self.ssbo.Set_data(mt = True)
        self.ssbo.Set_Vis()
        self.ssbo.Set_Dprop2()
        self.ssbo.Set_AC(size=self.Shid * mul(disp))
        self.ssbo.Set_InOut(sep=mul(disp), shid=self.Shid, batch=self.batch, vth=self.vth)

        self.SHRTH = 2048
        self.TOTAL = self.ssbo.Prop["data"][3][0]


        cr = ConstRender()
        CONST = {
            "SHXTH": self.Shid,
            "SHYTH": 1,
            "SHZTH": 1,
            "SHRTH": self.SHRTH,
            "TOTAL": self.TOTAL
        }
        cr.render("Mock1/parameter.tpl", CONST)


        CONST = {
            "SEPARATE": disp[1]*disp[2],
        }

        cr.render("Visual/mock1_buffer.tpl", CONST)

        TVis       = "../GLAux/glsl/Mock/Tvisual.glsl"
        prepro   = "../GLAux/glsl/Mock/VS/prepro_T1.glsl"
        self.comp      = Compute([TVis,prepro])
        self.comp.name = {'TVisual': 0 ,"PP" : 1}

        vert     = "../GLAux/glsl\\Mock\\VS\\T1.glsl"
        fatou    = "../GLAux/glsl\\Mock\\FS\\fatou.glsl"
        frag     = "../GLAux/glsl\\Mock\\FS\\T0.glsl"
        self.pipe_fatou = Pipe([vert, fatou], [GL_VERTEX_SHADER, GL_FRAGMENT_SHADER])
        self.pipe = Pipe([vert, frag], [GL_VERTEX_SHADER, GL_FRAGMENT_SHADER])
        self.vao =  Vao()
        self.vao.pos2d()


        #self.ssbo.Set_AC(size = self.Shid*mul(disp))
        self.active = "TVisual"
        self.iniDraw = True
    def Test_CalcTVisual(self,vmode =5):

        self.SetCurrent(self.context)
        self.comp.bind(self.comp.name['TVisual'])
        self.vis = vmode

        csum = []
        N = 1
        #log.Warning("Testing BlockDesign.......\n%s"%(dictString(CONST)))

        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['TVisual']], "PID"), self.pid)
        glUniform1i(glGetUniformLocation(self.comp.PG[self.comp.name['TVisual']], "VIS_MODE"), self.vis)

        start = time.time()
        for i in range(N):
            self.ssbo.G2C(tag="clear_ac")
            self.ssbo.G2C(tag="clear_dprop")
            glDispatchCompute(*self.disp)
            glMemoryBarrier(GL_SHADER_STORAGE_BARRIER_BIT)
            ac = self.ssbo.G2C(tag="np_ac").reshape(self.disp[1]*self.disp[2],self.Shid)


        log.Log("TestVisual  Dealing Draw blocksize %d  dispatch %s  init 10**6  result %s  Pid %d " % (
            self.Shid, self.disp,ac[:, int(self.pid % self.Shid)],self.pid))


            #cs = len(set(ac.flatten())) == 1
            #csum.append(cs)

        elapsed_time = time.time() - start
        log.Warning(
            "TestVisual Result shared (%d) dispatch (%d , %d  , %d) %d times  Inner(%d times)  elapsed_time:%.4f[sec]  CheckSum %s  " % (
                self.Shid, self.disp[0], self.disp[1], self.disp[2], N, self.TOTAL, elapsed_time,  csum))
        self.calcTVisual  = True
    def Debug_MFI(self):

        dp = self.vis
        self.SetCurrent(self.context)
        gpu = self.ssbo.G2C("np_vis")
        gpu = gpu[:,:,0].T
        deb = Debug_MT()
        deb.Range4(
            Set_Params(self.para[self.pid,:8]),
            sd=0, vs=1,dp = dp)
        deb.get_mfi()


        gpu_c = '#FF4500'
        cpu_c = '#0045FF'
        if dp ==2:
            plt.figure(102)
            plt.plot(gpu[0,:],label= "gpu_mu",c=gpu_c)
            plt.plot(gpu[1, :],label="gpu_mu2" ,c=gpu_c)
            plt.plot(gpu[4, :], label="gpu_tval",c=gpu_c)

            plt.plot(deb.buf1, label="mt_mu",c=cpu_c)
            plt.plot(deb.buf2, label="mt_mu2",c=cpu_c)
            plt.plot(deb.buf3, label="mt_tval",c=cpu_c)

            plt.legend()
            plt.show()

        elif dp ==5:

            plt.figure(102)
            plt.plot(gpu[2, :], label="gpu_balance", c=gpu_c)
            plt.plot(deb.buf1, label="mt_balance", c=cpu_c)
            plt.legend()

            plt.figure(103)
            plt.plot(gpu[3, :], label="gpu_profit", c=gpu_c)
            plt.plot(deb.buf2, label="mt_profit", c=cpu_c)
            plt.legend()

            plt.figure(104)
            plt.plot(gpu[4, :], label="gpu_npm", c=gpu_c)
            plt.plot(deb.buf3, label="mt_npm", c=cpu_c)
            plt.legend()

            plt.show()



smi = Smi()

class MockSetting7(sc.SizedDialog):
    def __init__(self, parent, id):
        sc.SizedDialog.__init__(self, None, -1, "Setting",
                                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self._ = parent.mock

        bg  = wx.Colour(23, 23, 23, alpha=200)
        fg  = wx.Colour(123, 123, 123, alpha=200)

        self.SetBackgroundColour(bg)
        self.SetForegroundColour(fg)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.CTRL = {}

        grid1 = wx.FlexGridSizer(cols=2)
        b_testuv = wx.Button(self, label="TestUV")
        self.Color(b_testuv,bg,fg)
        b_testuv.Bind(wx.EVT_BUTTON, self.OnTestUV, b_testuv)
        grid1.Add(b_testuv)

        b_test7 = wx.Button(self, label="Test7")
        self.Color(b_test7, bg, fg)
        b_test7.Bind(wx.EVT_BUTTON, self.OnTest7, b_test7)
        grid1.Add(b_test7)


        self.sizer.Add(grid1, flag=wx.BOTTOM, border=15)

        grid2 = wx.FlexGridSizer(cols=3)

        self._.pid = 25
        slider = wx.Slider(
            self, 100, self._.pid, 0, 256, size=(250, -1),
            style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS
        )
        self.Color(slider, bg, fg)
        slider.SetTickFreq(1)
        slider.Bind(wx.EVT_SLIDER, self.OnPidSlider)
        self.CTRL["pid"] = slider

        grid2.Add(slider)
        b_sl1 = wx.Button(self, label="<", size=(20, 20))
        self.Color(b_sl1, bg, fg)
        b_sl1.Bind(wx.EVT_BUTTON, self.OnSLLeft)
        grid2.Add(b_sl1)
        b_sl2 = wx.Button(self, label=">", size=(20, 20))
        self.Color(b_sl2, bg, fg)
        b_sl2.Bind(wx.EVT_BUTTON, self.OnSLRight)
        grid2.Add(b_sl2)

        self.sizer.Add(grid2, flag=wx.BOTTOM, border=5)


        grid3 = wx.FlexGridSizer(cols=3)

        self._.FULL = 0
        b_sf = wx.Button(self, label="sep/full", size=(60, 40))
        self.Color(b_sf, bg, fg)
        b_sf.Bind(wx.EVT_BUTTON, self.OnSEPFULL)
        grid3.Add(b_sf)
        grid3.Add(size=(20, 20))

        self.SEP = ["0","1","2","3"]
        self._.sepid = 0
        rb = wx.RadioBox(self, wx.ID_ANY, 'separateID',
                                choices=self.SEP, style=wx.RA_HORIZONTAL)
        self.Color(rb, bg, fg)
        rb.SetToolTip(wx.ToolTip("SEPARATE_ID"))
        rb.Select(self._.sepid)
        self.Bind(wx.EVT_RADIOBOX, self.EvtSEP, rb)
        grid3.Add(rb)

        self.sizer.Add(grid3, flag=wx.BOTTOM, border=5)

        #b = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        #self.Color(b,bg,fg)
        #self.sizer.Add(b, border=5)

        self.border = wx.BoxSizer()
        self.border.Add(self.sizer, flag=wx.ALL, border=20)
        self.SetSizerAndFit(self.border)

        self.radio1 = 0

        self.SetMinSize(self.GetSize())

        self.para_ini = True
    def Color(self,w,bg,fg):
        w.SetBackgroundColour(bg)
        w.SetForegroundColour(fg)
    def EvtSEP(self,event):
        self._.sepid = event.GetInt()
        self.OnTest()
        #print(self._.sepid)
    def OnSLLeft(self, event):
        v = self.CTRL["pid"].GetValue()
        if v > 0:
            self.CTRL["pid"].SetValue(v - 1)
            self.OnPidSlider(None)
    def OnSLRight(self, event):
        v = self.CTRL["pid"].GetValue()
        if v < self.CTRL["pid"].GetMax():
            self.CTRL["pid"].SetValue(v + 1)
            self.OnPidSlider(None)
    def OnTestUV(self, ev):
        self._.TestUV()
        gc.collect()
    def OnSEPFULL(self, ev):
        self._.FULL = 1 if self._.FULL == 0 else 0
        self.OnTest()
    def OnTest(self):
        if self._.active == "T7":
            self.OnTest7(None)
        elif self._.active == "T8":
            self.OnTest8(None)
    def OnTest7(self,ev):
        ut = smi.utilization()
        if ut > 80:
            log.Warning("<< GPU busy use rate %.3f ％ >>"%ut)
            return
        self._.Test7()
        self._.Test_CalcT7()
        self._.Test_Draw1()
    def OnPidSlider(self, ev):
        self._.pid = self.CTRL["pid"].GetValue()
        self.OnTest()
    def GetValue(self):
        return

class MockSetting8(sc.SizedDialog):
    def __init__(self, parent, id):
        sc.SizedDialog.__init__(self, None, -1, "Setting",
                                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self._ = parent.mock

        self._.Test8()

        bg  = wx.Colour(23, 23, 23, alpha=200)
        fg  = wx.Colour(123, 123, 123, alpha=200)

        self.SetBackgroundColour(bg)
        self.SetForegroundColour(fg)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.CTRL = {}

        grid1 = wx.FlexGridSizer(cols=3)
        b_testuv = wx.Button(self, label="TestUV")
        self.Color(b_testuv,bg,fg)
        b_testuv.Bind(wx.EVT_BUTTON, self.OnTestUV, b_testuv)
        grid1.Add(b_testuv)


        b_test8 = wx.Button(self, label="Test8")
        self.Color(b_test8, bg, fg)
        b_test8.Bind(wx.EVT_BUTTON, self.OnTest8, b_test8)
        grid1.Add(b_test8)

        self.sizer.Add(grid1, flag=wx.BOTTOM, border=15)

        grid2 = wx.FlexGridSizer(cols=3)

        self._.pid = 25
        slider = wx.Slider(
            self, 100, self._.pid, 0, 64, size=(250, -1),
            style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS
        )
        self.Color(slider, bg, fg)
        slider.SetTickFreq(1)
        slider.Bind(wx.EVT_SLIDER, self.OnPidSlider)
        self.CTRL["pid"] = slider

        grid2.Add(slider)
        b_sl1 = wx.Button(self, label="<", size=(20, 20))
        self.Color(b_sl1, bg, fg)
        b_sl1.Bind(wx.EVT_BUTTON, self.OnSLIDER)
        b_sl1.name = "pid"
        b_sl1.left = True
        grid2.Add(b_sl1)
        b_sl2 = wx.Button(self, label=">", size=(20, 20))
        self.Color(b_sl2, bg, fg)
        b_sl2.name = "pid"
        b_sl2.left = False
        b_sl2.Bind(wx.EVT_BUTTON, self.OnSLIDER)
        grid2.Add(b_sl2)

        self.sizer.Add(grid2, flag=wx.BOTTOM, border=5)


        grid3 = wx.FlexGridSizer(cols=5)

        self._.FULL = 0
        b_sf = wx.Button(self, label="sep/full", size=(60, 40))
        self.Color(b_sf, bg, fg)
        b_sf.Bind(wx.EVT_BUTTON, self.OnSEPFULL)
        grid3.Add(b_sf)
        grid3.Add(size=(20, 20))

        self.SEP = ["0","1","2","3"]
        self._.sepid = 0
        rb = wx.RadioBox(self, wx.ID_ANY, 'separateID',
                                choices=self.SEP, style=wx.RA_HORIZONTAL)
        self.Color(rb, bg, fg)
        rb.SetToolTip(wx.ToolTip("SEPARATE_ID"))
        rb.Select(self._.sepid)
        self.Bind(wx.EVT_RADIOBOX, self.EvtSEP, rb)
        grid3.Add(rb)

        self.sizer.Add(grid3, flag=wx.BOTTOM, border=5)

        grid3.Add(size=(20, 20))

        self.WTH = ["256", "512", "4096", "8192"]
        self._.wth = 256
        rb = wx.RadioBox(self, wx.ID_ANY, 'window',
                         choices=self.SEP, style=wx.RA_HORIZONTAL)
        self.Color(rb, bg, fg)
        rb.SetToolTip(wx.ToolTip("WindowLength"))
        rb.Select(0)
        self.Bind(wx.EVT_RADIOBOX, self.EvtWTH, rb)
        grid3.Add(rb)

        self.sizer.Add(grid3, flag=wx.BOTTOM, border=5)

        grid4 = wx.FlexGridSizer(cols=3)

        self._.stid = 25
        slider = wx.Slider(
            self, 100, self._.stid, 0, self._.TOTAL - int(self.WTH[-1]) , size=(250, -1),
            style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS
        )
        self.Color(slider, bg, fg)
        slider.SetTickFreq(1)
        slider.Bind(wx.EVT_SLIDER, self.OnStidSlider)
        self.CTRL["stid"] = slider

        grid4.Add(slider)
        b_sl1 = wx.Button(self, label="<", size=(20, 20))
        self.Color(b_sl1, bg, fg)
        b_sl1.name = "stid"
        b_sl1.left = True
        b_sl1.Bind(wx.EVT_BUTTON, self.OnSLIDER)
        grid4.Add(b_sl1)
        b_sl2 = wx.Button(self, label=">", size=(20, 20))
        self.Color(b_sl2, bg, fg)
        b_sl2.Bind(wx.EVT_BUTTON, self.OnSLIDER)
        b_sl2.name = "stid"
        b_sl2.left = False
        grid4.Add(b_sl2)

        self.sizer.Add(grid4 , flag=wx.BOTTOM, border=5)

        #b = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        #self.Color(b,bg,fg)
        #self.sizer.Add(b, border=5)

        self.border = wx.BoxSizer()
        self.border.Add(self.sizer, flag=wx.ALL, border=20)
        self.SetSizerAndFit(self.border)

        self.radio1 = 0

        self.SetMinSize(self.GetSize())

        self.para_ini = True
    def Color(self,w,bg,fg):
        w.SetBackgroundColour(bg)
        w.SetForegroundColour(fg)
    def EvtSEP(self,event):
        self._.sepid = event.GetInt()
        self.OnTest8(None)
        #print(self._.sepid)
    def EvtWTH(self,event):
        self._.wth = int(self.WTH[event.GetInt()])
        if self._.calcT8:
            self._.Test_Draw2()
        else:
            self.OnTest8(None)
        #print(self._.sepid)
    def OnSLIDER(self, event):
        name = event.EventObject.name
        left = event.EventObject.left
        v = self.CTRL[name].GetValue()
        if event.EventObject.left:
            if v > 0:
                self.CTRL[name].SetValue(v - 1)
        else:
            if v < self.CTRL[name].GetMax():
                self.CTRL[name].SetValue(v + 1)

        if name == "stid":
            self.OnStidSlider(None)
        elif name == "pid":
            self.OnPidSlider(None)
    def OnTestUV(self, ev):
        self._.TestUV()
        gc.collect()
    def OnSEPFULL(self, ev):
        self._.FULL = 1 if self._.FULL == 0 else 0
        self.OnTest8(None)
    def OnTest8(self,ev):
        ut = smi.utilization()
        if ut > 80:
            log.Warning("<< GPU busy use rate %.3f ％ >>"%ut)
            return
        #self._.Test8()
        self._.Test_CalcT8()
        self._.Test_Draw1()
    def OnPidSlider(self, ev):
        self._.pid = self.CTRL["pid"].GetValue()
        self.OnTest8(None)
    def OnStidSlider(self, ev):
        self._.stid = self.CTRL["stid"].GetValue()
        if not self._.calcT8:
            self._.Test_CalcT8()
        self._.Test_Draw2()
    def GetValue(self):
        return

class MockSetting9(sc.SizedDialog):
    def __init__(self, parent, id):
        sc.SizedDialog.__init__(self, None, -1, "Setting",
                                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self._ = parent.mock

        self._.Test9()

        bg  = wx.Colour(23, 23, 23, alpha=200)
        fg  = wx.Colour(123, 123, 123, alpha=200)

        self.SetBackgroundColour(bg)
        self.SetForegroundColour(fg)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.CTRL = {}

        grid1 = wx.FlexGridSizer(cols=3)
        b_testuv = wx.Button(self, label="TestUV")
        self.Color(b_testuv,bg,fg)
        b_testuv.Bind(wx.EVT_BUTTON, self.OnTestUV, b_testuv)
        grid1.Add(b_testuv)


        b_test9 = wx.Button(self, label="Test9")
        self.Color(b_test9, bg, fg)
        b_test9.Bind(wx.EVT_BUTTON, self.OnTest9, b_test9)
        grid1.Add(b_test9)

        self.DrawMode = ["draw","overall"]
        self._.vis = 1
        rb = wx.RadioBox(self, wx.ID_ANY, 'draw mode',
                                choices=self.DrawMode, style=wx.RA_HORIZONTAL)
        self.Color(rb, bg, fg)
        rb.SetToolTip(wx.ToolTip("DrawMode"))
        rb.Select(0)
        self.Bind(wx.EVT_RADIOBOX, self.EvtDrawMode, rb)
        grid1.Add(rb)

        self.sizer.Add(grid1, flag=wx.BOTTOM, border=15)


        grid2 = wx.FlexGridSizer(cols=3)

        self._.pid = 0
        slider = wx.Slider(
            self, 100, self._.pid, 0, self._.Shid, size=(250, -1),
            style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS
        )
        self.Color(slider, bg, fg)
        slider.SetTickFreq(1)
        slider.Bind(wx.EVT_SLIDER, self.OnPidSlider)
        self.CTRL["pid"] = slider

        grid2.Add(slider)
        b_sl1 = wx.Button(self, label="<", size=(20, 20))
        self.Color(b_sl1, bg, fg)
        b_sl1.Bind(wx.EVT_BUTTON, self.OnSLIDER)
        b_sl1.name = "pid"
        b_sl1.left = True
        grid2.Add(b_sl1)
        b_sl2 = wx.Button(self, label=">", size=(20, 20))
        self.Color(b_sl2, bg, fg)
        b_sl2.name = "pid"
        b_sl2.left = False
        b_sl2.Bind(wx.EVT_BUTTON, self.OnSLIDER)
        grid2.Add(b_sl2)

        self.sizer.Add(grid2, flag=wx.BOTTOM, border=5)


        grid3 = wx.FlexGridSizer(cols=5)

        self._.FULL = 0
        b_sf = wx.Button(self, label="sep/full", size=(60, 40))
        self.Color(b_sf, bg, fg)
        b_sf.Bind(wx.EVT_BUTTON, self.OnSEPFULL)
        grid3.Add(b_sf)
        grid3.Add(size=(20, 20))

        self.SEP = ["0","1","2","3"]
        self._.sepid = 0
        rb = wx.RadioBox(self, wx.ID_ANY, 'separateID',
                                choices=self.SEP, style=wx.RA_HORIZONTAL)
        self.Color(rb, bg, fg)
        rb.SetToolTip(wx.ToolTip("SEPARATE_ID"))
        rb.Select(self._.sepid)
        self.Bind(wx.EVT_RADIOBOX, self.EvtSEP, rb)
        grid3.Add(rb)

        self.sizer.Add(grid3, flag=wx.BOTTOM, border=5)

        grid3.Add(size=(20, 20))

        self.WTH = ["256", "512", "4096", "8192"]
        self._.wth = 256
        rb = wx.RadioBox(self, wx.ID_ANY, 'window',
                         choices=self.SEP, style=wx.RA_HORIZONTAL)
        self.Color(rb, bg, fg)
        rb.SetToolTip(wx.ToolTip("WindowLength"))
        rb.Select(0)
        self.Bind(wx.EVT_RADIOBOX, self.EvtWTH, rb)
        grid3.Add(rb)

        self.sizer.Add(grid3, flag=wx.BOTTOM, border=5)

        grid4 = wx.FlexGridSizer(cols=3)

        self._.stid = 25
        slider = wx.Slider(
            self, 100, self._.stid, 0, self._.TOTAL - int(self.WTH[-1]) , size=(250, -1),
            style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS
        )
        self.Color(slider, bg, fg)
        slider.SetTickFreq(1)
        slider.Bind(wx.EVT_SLIDER, self.OnStidSlider)
        self.CTRL["stid"] = slider

        grid4.Add(slider)
        b_sl1 = wx.Button(self, label="<", size=(20, 20))
        self.Color(b_sl1, bg, fg)
        b_sl1.name = "stid"
        b_sl1.left = True
        b_sl1.Bind(wx.EVT_BUTTON, self.OnSLIDER)
        grid4.Add(b_sl1)
        b_sl2 = wx.Button(self, label=">", size=(20, 20))
        self.Color(b_sl2, bg, fg)
        b_sl2.Bind(wx.EVT_BUTTON, self.OnSLIDER)
        b_sl2.name = "stid"
        b_sl2.left = False
        grid4.Add(b_sl2)

        self.sizer.Add(grid4 , flag=wx.BOTTOM, border=5)

        #b = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        #self.Color(b,bg,fg)
        #self.sizer.Add(b, border=5)

        self.border = wx.BoxSizer()
        self.border.Add(self.sizer, flag=wx.ALL, border=20)
        self.SetSizerAndFit(self.border)

        self.radio1 = 0

        self.SetMinSize(self.GetSize())
        self.para_ini = True
    def Color(self,w,bg,fg):
        w.SetBackgroundColour(bg)
        w.SetForegroundColour(fg)
    def EvtSEP(self,event):
        self._.sepid = event.GetInt()
        if self._.vis == 1:
            if self._.calcT9:self._.Test_Draw4()
        #print(self._.sepid)
    def EvtDrawMode(self, event):
        if event.GetInt() == 0:
            self._.vis = 1
            self._.pid = self.CTRL["pid"].GetValue()
        else:
            self._.vis = 0
            self._.pid = -1
        self.OnTest9(None)
        # print(self._.sepid)
    def EvtWTH(self,event):
        self._.wth = int(self.WTH[event.GetInt()])
        if self._.vis == 1:
            if self._.calcT9:self._.Test_Draw4()
    def OnSLIDER(self, event):
        name = event.EventObject.name
        left = event.EventObject.left
        v = self.CTRL[name].GetValue()
        if event.EventObject.left:
            if v > 0:
                self.CTRL[name].SetValue(v - 1)
        else:
            if v < self.CTRL[name].GetMax():
                self.CTRL[name].SetValue(v + 1)

        if name == "stid":
            self.OnStidSlider(None)
        elif name == "pid":
            self.OnPidSlider(None)
    def OnTestUV(self, ev):
        self._.TestUV()
        gc.collect()
    def OnSEPFULL(self, ev):
        if self._.vis == 1:
            self._.FULL = 1 if self._.FULL == 0 else 0
            if self._.calcT9:self._.Test_Draw4()
    def OnTest9(self,ev):
        ut = smi.utilization()
        if ut > 80:
            log.Warning("<< GPU busy use rate %.3f ％ >>"%ut)
            return
        #self._.Test8()
        self._.Test_CalcT9()
        self._.Test_Draw4()
    def OnPidSlider(self, ev):

        if self._.vis == 1:
            self._.pid = self.CTRL["pid"].GetValue()
            #print(" vis  ", self._.vis, "  pid ", self._.pid)
            self.OnTest9(None)
    def OnStidSlider(self, ev):
        if self._.vis == 1:
            self._.stid = self.CTRL["stid"].GetValue()
            if not self._.calcT9:
                self._.Test_CalcT9()
            self._.Test_Draw4()
    def GetValue(self):
        return

class MockSettingVisualizer(sc.SizedDialog):
    def __init__(self, parent, id):
        sc.SizedDialog.__init__(self, None, -1, "Setting",
                                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self._ = parent.mock

        self._.TestVisual()

        bg  = wx.Colour(23, 23, 23, alpha=200)
        fg  = wx.Colour(123, 123, 123, alpha=200)

        self.SetBackgroundColour(bg)
        self.SetForegroundColour(fg)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.CTRL = {}

        grid1 = wx.FlexGridSizer(cols=3)
        b_testuv = wx.Button(self, label="TestUV")
        self.Color(b_testuv,bg,fg)
        b_testuv.Bind(wx.EVT_BUTTON, self.OnTestUV, b_testuv)
        grid1.Add(b_testuv)


        b_test9 = wx.Button(self, label="TestRun")
        self.Color(b_test9, bg, fg)
        b_test9.Bind(wx.EVT_BUTTON, self.OnTestRun, b_test9)
        grid1.Add(b_test9)

        self.DrawMode = ["draw","overall"]
        self._.vis = 1
        rb = wx.RadioBox(self, wx.ID_ANY, 'draw mode',
                                choices=self.DrawMode, style=wx.RA_HORIZONTAL)
        self.Color(rb, bg, fg)
        rb.SetToolTip(wx.ToolTip("DrawMode"))
        rb.Select(0)
        self.Bind(wx.EVT_RADIOBOX, self.EvtDrawMode, rb)
        grid1.Add(rb)

        self.sizer.Add(grid1, flag=wx.BOTTOM, border=15)


        grid2 = wx.FlexGridSizer(cols=3)

        self._.pid = 0
        slider = wx.Slider(
            self, 100, self._.pid, 0, self._.Shid*self._.batch*self._.sep, size=(250, -1),
            style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS
        )
        self.Color(slider, bg, fg)
        slider.SetTickFreq(1)
        slider.Bind(wx.EVT_SLIDER, self.OnPidSlider)
        self.CTRL["pid"] = slider

        grid2.Add(slider)
        b_sl1 = wx.Button(self, label="<", size=(20, 20))
        self.Color(b_sl1, bg, fg)
        b_sl1.Bind(wx.EVT_BUTTON, self.OnSLIDER)
        b_sl1.name = "pid"
        b_sl1.left = True
        grid2.Add(b_sl1)
        b_sl2 = wx.Button(self, label=">", size=(20, 20))
        self.Color(b_sl2, bg, fg)
        b_sl2.name = "pid"
        b_sl2.left = False
        b_sl2.Bind(wx.EVT_BUTTON, self.OnSLIDER)
        grid2.Add(b_sl2)

        self.sizer.Add(grid2, flag=wx.BOTTOM, border=5)


        grid3 = wx.FlexGridSizer(cols=5)

        self._.FULL = 0
        b_sf = wx.Button(self, label="sep/full", size=(60, 40))
        self.Color(b_sf, bg, fg)
        b_sf.Bind(wx.EVT_BUTTON, self.OnSEPFULL)
        grid3.Add(b_sf)
        grid3.Add(size=(20, 20))

        self.SEP = ["0","1","2","3"]
        self._.sepid = 0
        rb = wx.RadioBox(self, wx.ID_ANY, 'separateID',
                                choices=self.SEP, style=wx.RA_HORIZONTAL)
        self.Color(rb, bg, fg)
        rb.SetToolTip(wx.ToolTip("SEPARATE_ID"))
        rb.Select(self._.sepid)
        self.Bind(wx.EVT_RADIOBOX, self.EvtSEP, rb)
        grid3.Add(rb)

        self.sizer.Add(grid3, flag=wx.BOTTOM, border=5)

        grid3.Add(size=(20, 20))

        self.WTH = ["256", "512", "4096", "8192"]
        self._.wth = 256
        rb = wx.RadioBox(self, wx.ID_ANY, 'window',
                         choices=self.SEP, style=wx.RA_HORIZONTAL)
        self.Color(rb, bg, fg)
        rb.SetToolTip(wx.ToolTip("WindowLength"))
        rb.Select(0)
        self.Bind(wx.EVT_RADIOBOX, self.EvtWTH, rb)
        grid3.Add(rb)

        self.sizer.Add(grid3, flag=wx.BOTTOM, border=5)

        grid4 = wx.FlexGridSizer(cols=3)

        self._.stid = 25
        slider = wx.Slider(
            self, 100, self._.stid, 0, self._.TOTAL - int(self.WTH[-1]) , size=(250, -1),
            style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS
        )
        self.Color(slider, bg, fg)
        slider.SetTickFreq(1)
        slider.Bind(wx.EVT_SLIDER, self.OnStidSlider)
        self.CTRL["stid"] = slider

        grid4.Add(slider)
        b_sl1 = wx.Button(self, label="<", size=(20, 20))
        self.Color(b_sl1, bg, fg)
        b_sl1.name = "stid"
        b_sl1.left = True
        b_sl1.Bind(wx.EVT_BUTTON, self.OnSLIDER)
        grid4.Add(b_sl1)
        b_sl2 = wx.Button(self, label=">", size=(20, 20))
        self.Color(b_sl2, bg, fg)
        b_sl2.Bind(wx.EVT_BUTTON, self.OnSLIDER)
        b_sl2.name = "stid"
        b_sl2.left = False
        grid4.Add(b_sl2)

        self.sizer.Add(grid4 , flag=wx.BOTTOM, border=5)

        #b = self.CreateStdDialogButtonSizer(wx.OK | wx.CANCEL)
        #self.Color(b,bg,fg)
        #self.sizer.Add(b, border=5)

        self.border = wx.BoxSizer()
        self.border.Add(self.sizer, flag=wx.ALL, border=20)
        self.SetSizerAndFit(self.border)

        self.radio1 = 0

        self.SetMinSize(self.GetSize())
        self.para_ini = True
    def Color(self,w,bg,fg):
        w.SetBackgroundColour(bg)
        w.SetForegroundColour(fg)
    def EvtSEP(self,event):
        self._.sepid = event.GetInt()
        if self._.vis == 1:
            if self._.calcTVisual:self._.Test_Draw4()
        #print(self._.sepid)
    def EvtDrawMode(self, event):
        if event.GetInt() == 0:
            self._.vis = 1
            self._.pid = self.CTRL["pid"].GetValue()
        else:
            self._.vis = 0
            self._.pid = -1
        self.OnTestVisual(None)
        # print(self._.sepid)
    def EvtWTH(self,event):
        self._.wth = int(self.WTH[event.GetInt()])
        if self._.vis == 1:
            if self._.calcTVisual:self._.Test_Draw4()
    def OnSLIDER(self, event):
        name = event.EventObject.name
        left = event.EventObject.left
        v = self.CTRL[name].GetValue()
        if event.EventObject.left:
            if v > 0:
                self.CTRL[name].SetValue(v - 1)
        else:
            if v < self.CTRL[name].GetMax():
                self.CTRL[name].SetValue(v + 1)


        if name == "pid":
            self.OnPidSlider(None)

    def OnTestUV(self, ev):
        self._.TestUV()
        gc.collect()
    def OnSEPFULL(self, ev):
        if self._.vis == 1:
            self._.FULL = 1 if self._.FULL == 0 else 0
            if self._.calcTVisual:self._.Test_Draw4()
    def OnTestRun(self,ev):
        ut = smi.utilization()
        if ut > 80:
            log.Warning("<< GPU busy use rate %.3f ％ >>"%ut)
            return
        #self._.Test8()
        self._.Test_CalcTVisual()
        self._.Test_Draw4()
        log.Info("parameters   %s  "%self._.para[self._.pid,:].tolist())
        self._.Debug_MFI()
    def OnPidSlider(self, ev):
        self._.pid = self.CTRL["pid"].GetValue()
            #log.Log(" Set PID   %d "%self._.pid)
            #self.OnTestVisual(None)
    def OnStidSlider(self, ev):
        if self._.vis == 1:
            self._.stid = self.CTRL["stid"].GetValue()
            if not self._.calcTVisual:
                self._.Test_CalcTVisual()
            self._.Test_Draw4()
    def GetValue(self):
        return



class MockSettingAsset(sc.SizedDialog):
    def __init__(self, parent, id):
        sc.SizedDialog.__init__(self, None, -1, "Setting",
                                style=wx.DEFAULT_DIALOG_STYLE | wx.RESIZE_BORDER)

        self._   = parent.mock
        self.gui = parent.gui
        self.visual = None

        self._.TestAsset()


        bg  = wx.Colour(23, 23, 23, alpha=200)
        fg  = wx.Colour(123, 123, 123, alpha=200)

        self.SetBackgroundColour(bg)
        self.SetForegroundColour(fg)

        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.CTRL = {}

        grid1 = wx.FlexGridSizer(cols=1)

        b_testOut = wx.Button(self, label="TestOut")
        self.Color(b_testOut, bg, fg)
        b_testOut.Bind(wx.EVT_BUTTON, self.OnTestOut, b_testOut)
        grid1.Add(b_testOut)

        self.sizer.Add(grid1, flag=wx.BOTTOM, border=15)

        grid12 = wx.FlexGridSizer(cols=3)

        st = wx.StaticText(self, wx.ID_ANY, "TestSampling")
        font = wx.Font(10, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        st.SetFont(font)
        grid12.Add(st)

        b_testRandom = wx.Button(self, label="Random")
        self.Color(b_testRandom, bg, fg)
        b_testRandom.Bind(wx.EVT_BUTTON, self.OnTestRandom, b_testRandom)
        grid12.Add(b_testRandom)

        b_testMax = wx.Button(self, label="Max")
        self.Color(b_testMax, bg, fg)
        b_testMax.Bind(wx.EVT_BUTTON, self.OnTestMax, b_testMax)
        grid12.Add(b_testMax)

        self.sizer.Add(grid12, flag=wx.BOTTOM, border=15)


        grid20 = wx.FlexGridSizer(cols=1)

        st = wx.StaticText(self, wx.ID_ANY, "SampleRange")
        font = wx.Font(10, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        st.SetFont(font)
        grid20.Add(st)
        self.sizer.Add(grid20, flag=wx.BOTTOM, border=15)

        grid2 = wx.FlexGridSizer(cols=3)

        self._.samp_ra = 0.5
        slider = wx.Slider(
            self, 100, self._.samp_ra, 0, 100, size=(250, -1),
            style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS
        )
        self.Color(slider, bg, fg)

        slider.SetTickFreq(25)
        slider.Bind(wx.EVT_SLIDER, self.OnSampRaSlider)
        self.CTRL["samp_ra"] = slider

        grid2.Add(slider)
        b_sl1 = wx.Button(self, label="<", size=(20, 20))
        self.Color(b_sl1, bg, fg)
        b_sl1.Bind(wx.EVT_BUTTON, self.OnSLIDER)
        b_sl1.name = "samp_ra"
        b_sl1.left = True
        grid2.Add(b_sl1)
        b_sl2 = wx.Button(self, label=">", size=(20, 20))
        self.Color(b_sl2, bg, fg)
        b_sl2.name = "samp_ra"
        b_sl2.left = False
        b_sl2.Bind(wx.EVT_BUTTON, self.OnSLIDER)
        grid2.Add(b_sl2)

        self.sizer.Add(grid2, flag=wx.BOTTOM, border=5)



        grid40 = wx.FlexGridSizer(cols=1)

        st = wx.StaticText(self, wx.ID_ANY, "SampleNum")
        font = wx.Font(10, wx.FONTFAMILY_MODERN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
        st.SetFont(font)
        grid40.Add(st)
        self.sizer.Add(grid40, flag=wx.BOTTOM, border=15)

        grid4 = wx.FlexGridSizer(cols=3)

        self._.samp_num = self._.vth
        slider = wx.Slider(
            self, 100, self._.samp_num, 1, self._.vth, size=(250, -1),
            style=wx.SL_HORIZONTAL | wx.SL_AUTOTICKS | wx.SL_LABELS
        )
        self.Color(slider, bg, fg)

        slider.SetTickFreq(1)
        slider.Bind(wx.EVT_SLIDER, self.OnSampNumSlider)
        self.CTRL["samp_num"] = slider

        grid4.Add(slider)
        b_sl1 = wx.Button(self, label="<", size=(20, 20))
        self.Color(b_sl1, bg, fg)
        b_sl1.Bind(wx.EVT_BUTTON, self.OnSLIDER)
        b_sl1.name = "samp_num"
        b_sl1.left = True
        grid4.Add(b_sl1)
        b_sl2 = wx.Button(self, label=">", size=(20, 20))
        self.Color(b_sl2, bg, fg)
        b_sl2.name = "samp_num"
        b_sl2.left = False
        b_sl2.Bind(wx.EVT_BUTTON, self.OnSLIDER)
        grid4.Add(b_sl2)

        self.sizer.Add(grid4, flag=wx.BOTTOM, border=5)




        grid3 = wx.FlexGridSizer(cols=5)

        self._.FULL = 0
        b_sf = wx.Button(self, label="sep/full", size=(60, 40))
        self.Color(b_sf, bg, fg)
        b_sf.Bind(wx.EVT_BUTTON, self.OnSEPFULL)
        grid3.Add(b_sf)
        grid3.Add(size=(20, 20))

        self.SEP = ["0","1","2","3"]
        self._.sepid = 0
        rb = wx.RadioBox(self, wx.ID_ANY, 'separateID',
                                choices=self.SEP, style=wx.RA_HORIZONTAL)
        self.Color(rb, bg, fg)
        rb.SetToolTip(wx.ToolTip("SEPARATE_ID"))
        rb.Select(self._.sepid)
        self.Bind(wx.EVT_RADIOBOX, self.EvtSEP, rb)
        grid3.Add(rb)

        self.sizer.Add(grid3, flag=wx.BOTTOM, border=5)


        self.border = wx.BoxSizer()
        self.border.Add(self.sizer, flag=wx.ALL, border=20)
        self.SetSizerAndFit(self.border)

        self.radio1 = 0

        self.SetMinSize(self.GetSize())

        self.OnTestVisual(None)

        self.para_ini = True
    def Color(self,w,bg,fg):
        w.SetBackgroundColour(bg)
        w.SetForegroundColour(fg)
    def EvtSEP(self,event):
        self._.sepid = event.GetInt()
        if self._.vis == 1:
            if self._.calcT9:self._.Test_Draw4()
        #print(self._.sepid)
    def EvtDrawMode(self, event):
        pass
        # print(self._.sepid)
    def OnSLIDER(self, event):
        name = event.EventObject.name
        left = event.EventObject.left
        v = self.CTRL[name].GetValue()
        if event.EventObject.left:
            if v > 0:
                self.CTRL[name].SetValue(v - 1)
        else:
            if v < self.CTRL[name].GetMax():
                self.CTRL[name].SetValue(v + 1)

        if name == "samp_ra":
            self.OnSampRaSlider(None)
        if name == "samp_num":
            self.OnSampNumSlider(None)
    def OnSEPFULL(self, ev):
        if self._.vis == 1:
            self._.FULL = 1 if self._.FULL == 0 else 0
            self._.Test_DrawAsset()
    def OnTestOut(self,ev):
        ut = smi.utilization()
        if ut > 80:
            log.Warning("<< GPU busy use rate %.3f ％ >>"%ut)
            return
        #self._.Test8()
        self._.Test_CalcTasset(para_mode=0)
        self._.Test_DrawAsset()
    def OnTestRandom(self,ev):
        ut = smi.utilization()
        if ut > 80:
            log.Warning("<< GPU busy use rate %.3f ％ >>"%ut)
            return

        self._.Test_CalcTasset(para_mode=1,mode ="ini")

        self._.Test_DrawAsset()

        self.SetParameter()

    def SetParameter(self):
        if self.visual != None:
            self._.OnContext()
            self.para = self._.ssbo.G2C("np_io")
            self.visual._.OnContext()
            self.visual._.ssbo.G2C("set_io",self.para)
            self.visual._.para = self.visual._.ssbo.G2C("np_io")
            log.Log("Set parameter  validate %s "%np.alltrue(self.para == self.visual._.para))
    def OnTestMax(self,ev):
        ut = smi.utilization()
        if ut > 80:
            log.Warning("<< GPU busy use rate %.3f ％ >>"%ut)
            return
        self._.Test_CalcTasset(para_mode=1,mode ="max")
        self._.Test_DrawAsset()
        self.SetParameter()
    def OnSampRaSlider(self, ev):
        self._.samp_ra = self.CTRL["samp_ra"].GetValue()/100
        print(" sample range  ", self._.samp_ra)
        #self.OnTest9(None)
    def OnSampNumSlider(self, ev):
        self._.samp_num = self.CTRL["samp_num"].GetValue()
        print(" sample num  ", self._.samp_num)
        #self.OnTest9(None)
    async def mock1dlg(self,n):
        if n ==0:
            frame = wx.Frame(None, -1, "Visualizer", size=(500, 500),
                             style=wx.DEFAULT_FRAME_STYLE, name="run a sample")
            frame.mock = Mock(frame, size=(500, 500))
            frame.gui  = self.gui
            self.visual = MockSettingVisualizer(frame, 0)
            frame.Show()
        return_code = await AsyncShowDialog(self.visual)
        log.Info("  Visualizer Delete !!!")
        self.visual = None
    def OnTestVisual(self, event):
        loop = get_event_loop()
        ta = []
        ta.append(self.mock1dlg(0))
        for i in ta:
            loop.create_task(i)
        if event != None:event.Skip()
    def GetValue(self):
        return


if __name__ == "__main__":
    from GLAux.parser import *
    cr = ConstRender()
    CONST = {
        "SHXTH": 256,
        "SHYTH": 1,
        "SHZTH": 1,
        "TOTAL": 2048
    }
    cr.render("Mock1/parameter.tpl",CONST)
