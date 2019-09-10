import numpy as np
import os
from OpenGL.GL import *
from OpenGL.GL.shaders import *

from p2popt.GLAux.log import *
from p2popt.App.config import *
import json


class Sampler:
    def __init__(self,seed):
        self.seed      = seed
        home           = os.path.expanduser("~")
        home           = "%s\%s"%(home[:2],home[2:])
        self.name      =  config["ID_json"]
        self.num       = 0

        self.choiceNum = -1
        self.fix       = -1
        self.path   = "%s/%s/"%(home,config["dir_json"])
        log.Info("DownLoads Directory %s"%self.path)
        self.para_range = param_range
        self.vth        = len(param_range)
        self.sep        = 4
        np.random.seed(seed)
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
                if i == self.choiceNum:
                    p  = self.choice[np.random.randint(0, len(self.choice), n)]
                else:
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
    def resultplot(self,asset):

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
    def readIni(self,n):
        fn = "%sinit.json" % (self.path)
        if not os.path.isfile(fn):
            log.Error("inifile Not exist!!  %s"%fn)
            return False
        else:
            with open(fn, mode='r') as f:
                r0  = f.read()
                r  = json.loads(r0)
                #print(r0)
                self.choice    = np.array(r["choice"]).astype(np.float)
                self.choiceNum = r["choiceNum"]
                self.fix       = r["fix"]

            os.remove(fn)

            for i, a in enumerate(self.para_range):
                if i == self.choiceNum:
                    p = self.choice[np.random.randint(0, len(self.choice), n)]
                else:
                    p = a[0] + a[2] * np.random.randint(0, (a[1] - a[0]) / a[2], n)
                #print(i,"  range ",a,"  param  ",p)
                if i == 0:
                    l = p
                else:
                    l = np.vstack((l, p))

            return np.vstack((l, np.zeros(n))).T
    def writeJson(self,p):
        Result = {
            "Name" : "A",
            "Prop" : {"Fix": self.fix, "Choice": self.choiceNum},
            "ID"   : "%s-%d"%(self.name,self.num),
            "Data" : p.tolist()
        }

        J = json.dumps(Result)
        with open("%s%s_%d.json"%(self.path,self.name,self.num), mode='w') as f:
            f.write(J)
        self.num += 1

#with open("tester.json", mode='r') as f:
#    r = f.read()
#    r  = json.loads(r)
#    print(r)
#    print(np.array(r["Data"]))self.path




class Ssbo:
    def __init__(self):
        """
        Property["Name"]  = [ssbo_pointer,bufferbaseID,byteSize,DataShape]
        """
        self.Prop    = {}
        self.Ammount = 0
    def initialize(self):
        self.Set_data()
        self.Set_AC()
    def delete(self):
        keys = []
        for k in self.Prop:
            if self.Prop[k][0] != None:
                glDeleteBuffers(1, [self.Prop[k][0]])
                self.Ammount    -= self.Prop[k][2]
                keys.append(k)
        for i in keys:
            del self.Prop[i]
        log.Info("Ssbo Destroy %s"%keys)
    def load_mt(self):
        dir = os.path.dirname(os.path.abspath(__file__))
        path = "%s/Data/GBPAUD_M1_201908.csv"%dir
        data = np.loadtxt(path, delimiter="\t", skiprows=1, usecols=(2, 3, 4, 5))
        return np.hstack((np.arange(len(data)).reshape(len(data), 1), data))
    def Set_data(self,name="data",bbid= 3,mt = False):
        dir = os.path.dirname(os.path.abspath(__file__))
        if mt:
            data = self.load_mt()
        else:
            data = np.loadtxt("%s/Data/%s"%(dir,config[name]),delimiter=",",skiprows=0,usecols=(1, 2, 3, 4, 5))
        log.Log("DATA   min %.6f max %.6f"%(data[:,4].min(),data[:,4].max()))
        self.data  = data.astype(np.float)
        nbyte = data.data.nbytes
        if not name in self.Prop:
            if not bool(glGenBuffers):
                log.Error("Error Generate SSBO")
                return False
            ssbo  = glGenBuffers(1)
        else:
            ssbo =  self.Prop[name][0]
            self.Ammount -= self.Prop[name][2]
        glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssbo)
        glBufferData(GL_SHADER_STORAGE_BUFFER, data.flatten().astype(np.float32), GL_STATIC_DRAW)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, bbid, ssbo)
        self.Ammount      += nbyte
        self.Prop["data"] = [ ssbo,bbid,nbyte,data.shape]
        log.Info("Ssbo Generate %s bbid(%d) nbyte(%d) shape(%s)  Ammount(%d)"%(name,bbid,nbyte,data.shape,self.Ammount))
        #ToDo  Validate SSBO
        return True
    def Set_AC(self,name = "ac",bbid =1,size = 1024*64):
        nbyte = size*4
        if not name  in self.Prop:
            if not bool(glGenBuffers):
                log.Error("Error Generate SSBO")
                return False
            ssbo  = glGenBuffers(1)
        else:
            ssbo =  self.Prop[name][0]
            self.Ammount -= self.Prop[name][2]

        glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssbo)
        glBufferData(GL_SHADER_STORAGE_BUFFER,np.zeros(size).astype(np.uint), GL_DYNAMIC_DRAW)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, bbid, ssbo)
        self.Ammount += nbyte
        self.Prop[name] = [ssbo, bbid, nbyte, (size,)]
        log.Info("Ssbo Generate %s bbid(%d) nbyte(%d) shape(%s)  Ammount(%d)" % (name, bbid, nbyte, size, self.Ammount))
    def Set_Vis(self,sep = 4):
        if not "data" in self.Prop:
            log.Error("No Data Found.")
            return
        lth   = self.Prop["data"][3][0]
        d     = np.zeros(lth*5*sep)
        nbyte = d.nbytes
        bbid  = 0
        if not "vis" in self.Prop:
            if not bool(glGenBuffers):
                log.Error("Error Generate SSBO")
                return False
            ssbo  = glGenBuffers(1)
        else:
            ssbo =  self.Prop[name][0]
            self.Ammount -= self.Prop[name][2]

        glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssbo)
        glBufferData(GL_SHADER_STORAGE_BUFFER, d.flatten().astype(np.float32), GL_STATIC_DRAW)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, bbid, ssbo)
        self.Ammount      += nbyte
        self.Prop["vis"]  = [ssbo,bbid,nbyte, (lth,5,sep)]

        log.Info("Ssbo Generate %s bbid(%d) nbyte(%d) shape(%s)  Ammount(%d)"%("vis",bbid,nbyte,self.Prop["vis"][3],self.Ammount))


        #ToDo  Validate SSBO
        return True
    def Set_Dprop(self):
        if not "vis" in self.Prop:
            log.Error("No DrawClass Found.")
            return
        sep = self.Prop["vis"][3][2]
        d     = np.zeros(6 * sep)
        nbyte = d.nbytes
        bbid  = 2
        if not "dprop" in self.Prop:
            if not bool(glGenBuffers):
                log.Error("Error Generate SSBO")
                return False
            ssbo = glGenBuffers(1)
        else:
            ssbo = self.Prop[name][0]
            self.Ammount -= self.Prop[name][2]

        glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssbo)
        glBufferData(GL_SHADER_STORAGE_BUFFER, d.flatten().astype(np.float32), GL_STATIC_DRAW)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, bbid, ssbo)
        self.Ammount += nbyte
        self.Prop["dprop"] = [ssbo, bbid, nbyte, (sep, 6)]

        log.Info("Ssbo Generate %s bbid(%d) nbyte(%d) shape(%s)  Ammount(%d)" % (
        "dprop", bbid, nbyte, self.Prop["dprop"][3], self.Ammount))

        # ToDo  Validate SSBO
        return True
    def Set_Dprop2(self):
        if not "vis" in self.Prop:
            log.Error("No DrawClass Found.")
            return
        sep = self.Prop["vis"][3][2]
        size_st = 6+400
        d     = np.zeros( size_st * sep)
        nbyte = d.nbytes
        bbid  = 2
        if not "dprop" in self.Prop:
            if not bool(glGenBuffers):
                log.Error("Error Generate SSBO")
                return False
            ssbo = glGenBuffers(1)
        else:
            ssbo = self.Prop[name][0]
            self.Ammount -= self.Prop[name][2]

        glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssbo)
        glBufferData(GL_SHADER_STORAGE_BUFFER, d.flatten().astype(np.float32), GL_STATIC_DRAW)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, bbid, ssbo)
        self.Ammount += nbyte
        self.Prop["dprop"] = [ssbo, bbid, nbyte, (sep, size_st)]

        log.Info("Ssbo Generate %s bbid(%d) nbyte(%d) shape(%s)  Ammount(%d)" % (
        "dprop", bbid, nbyte, self.Prop["dprop"][3], self.Ammount))

        # ToDo  Validate SSBO
        return True
    def Set_Asset(self,batch= 10,sep = 4,shid = 32,deal = 300):
        if not "data" in self.Prop:
            log.Error("No Data Found.")
            return
        lth   = sep *  shid * batch
        d     = np.zeros(lth*deal*2)
        nbyte = d.nbytes
        bbid  = 4
        if not "asset" in self.Prop:
            if not bool(glGenBuffers):
                log.Error("Error Generate SSBO")
                return False
            ssbo  = glGenBuffers(1)
        else:
            ssbo =  self.Prop[name][0]
            self.Ammount -= self.Prop[name][2]

        glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssbo)
        glBufferData(GL_SHADER_STORAGE_BUFFER, d.flatten().astype(np.float32), GL_STATIC_DRAW)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, bbid, ssbo)
        self.Ammount      += nbyte
        self.Prop["asset"]  = [ssbo,bbid,nbyte, (lth,2,deal)]  # (sep,shid*batch,2,deal)

        log.Info("Ssbo Generate %s bbid(%d) nbyte(%d) shape(%s)  Ammount(%d)"%("asset",bbid,nbyte,self.Prop["asset"][3],self.Ammount))

        #ToDo  Validate SSBO
        return True
    def Set_InOut(self,batch= 10,sep = 4,shid = 32,vth = 6):
        if not "data" in self.Prop:
            log.Error("No Data Found.")
            return
        name = "io"
        lth   = sep *  shid * batch
        d     = np.zeros(lth*(vth + 1))
        nbyte = d.nbytes
        bbid  = ssbo_location[name]
        if not name in self.Prop:
            if not bool(glGenBuffers):
                log.Error("Error Generate SSBO")
                return False
            ssbo  = glGenBuffers(1)
        else:
            ssbo =  self.Prop[name][0]
            self.Ammount -= self.Prop[name][2]

        glBindBuffer(GL_SHADER_STORAGE_BUFFER, ssbo)
        glBufferData(GL_SHADER_STORAGE_BUFFER, d.flatten().astype(np.float32), GL_DYNAMIC_DRAW)
        glBindBufferBase(GL_SHADER_STORAGE_BUFFER, bbid, ssbo)
        self.Ammount      += nbyte
        self.Prop[name]  = [ssbo,bbid,nbyte, (lth,vth+1)]

        log.Info("Ssbo Generate %s bbid(%d) nbyte(%d) shape(%s)  Ammount(%d)"%(name,bbid,nbyte,self.Prop[name][3],self.Ammount))

        #ToDo  Validate SSBO
        return True
    def G2C(self,tag,data = None):
        if   tag    == "np_ac":
            glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.Prop["ac"][0])
            data = glMapBuffer(GL_SHADER_STORAGE_BUFFER, GL_READ_ONLY)
            ptr  = ctypes.c_uint * self.Prop["ac"][3][0]
            data = np.ctypeslib.as_array(ptr.from_address(data))
            glUnmapBuffer(GL_SHADER_STORAGE_BUFFER)
            return data
        elif tag    == "clear_ac":
            glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.Prop["ac"][0])
            glBufferData(GL_SHADER_STORAGE_BUFFER, np.zeros(self.Prop["ac"][3][0]).astype(np.uint), GL_DYNAMIC_DRAW)
        elif tag    == "np_data":
            ptr = ctypes.c_float * mul(self.Prop["data"][3])
            glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.Prop["data"][0])
            data = glMapBuffer(GL_SHADER_STORAGE_BUFFER, GL_READ_ONLY)
            data = np.ctypeslib.as_array(ptr.from_address(data)).astype(np.float)
            glUnmapBuffer(GL_SHADER_STORAGE_BUFFER)
            return data.reshape(*self.Prop["data"][3])
        elif tag    == "data":
            class cRates(ctypes.Structure):
                _fields_ = [
                    ("date", (ctypes.c_float)),
                    ("open",  (ctypes.c_float) ),
                    ("high",  (ctypes.c_float) ),
                    ("low",   (ctypes.c_float) ),
                    ("close", (ctypes.c_float) ),
                   # ("vol",   (ctypes.c_float) ),
                ]
            glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.Prop["data"][0])
            data = ctypes.cast(glMapBuffer(GL_SHADER_STORAGE_BUFFER, GL_READ_ONLY), ctypes.POINTER(cRates))
            glUnmapBuffer(GL_SHADER_STORAGE_BUFFER)
            return data
        elif tag    == "dprop":

            class cDprop(ctypes.Structure):
                _fields_ = [
                    ("stid", (ctypes.c_int)),
                    ("std",  (ctypes.c_float) ),
                    ("ry",  (ctypes.c_float)*2 ),
                    ("rx",   (ctypes.c_float)*2 ),
                ]

            glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.Prop["dprop"][0])
            data = ctypes.cast(glMapBuffer(GL_SHADER_STORAGE_BUFFER, GL_READ_ONLY), ctypes.POINTER(cDprop))
            glUnmapBuffer(GL_SHADER_STORAGE_BUFFER)
            return data
        elif tag    == "dprop2":

            class cDprop(ctypes.Structure):
                _fields_ = [
                    ("stid",  (ctypes.c_int)),
                    ("std",   (ctypes.c_float) ),
                    ("ry",    (ctypes.c_float)*2 ),
                    ("rx",    (ctypes.c_float)*2 ),
                    ("entry", (ctypes.c_int) * 200),
                    ("exit",  (ctypes.c_int) * 200),
                ]

            glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.Prop["dprop"][0])
            data = ctypes.cast(glMapBuffer(GL_SHADER_STORAGE_BUFFER, GL_READ_ONLY), ctypes.POINTER(cDprop))
            glUnmapBuffer(GL_SHADER_STORAGE_BUFFER)
            return data
        elif tag    == "clear_dprop2":

            glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.Prop["dprop"][0])
            glBufferData(GL_SHADER_STORAGE_BUFFER, np.zeros(mul(self.Prop["dprop"][3])).astype(np.int), GL_DYNAMIC_DRAW)
        elif tag    == "clear_asset":

            name = "asset"
            glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.Prop["asset"][0])
            glBufferData(GL_SHADER_STORAGE_BUFFER, np.zeros(mul(self.Prop["asset"][3])).astype(np.float32), GL_DYNAMIC_DRAW)
        elif tag    == "np_vis":

            ptr  = ctypes.c_float * mul(self.Prop["vis"][3])
            glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.Prop["vis"][0])
            data = glMapBuffer(GL_SHADER_STORAGE_BUFFER, GL_READ_ONLY)
            data = np.ctypeslib.as_array(ptr.from_address(data)).astype(np.float)
            glUnmapBuffer(GL_SHADER_STORAGE_BUFFER)
            return data.reshape(*self.Prop["vis"][3])
        elif tag    == "np_asset":

            ptr = ctypes.c_float * mul(self.Prop["asset"][3])
            glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.Prop["asset"][0])
            data = glMapBuffer(GL_SHADER_STORAGE_BUFFER, GL_READ_ONLY)
            data = np.ctypeslib.as_array(ptr.from_address(data)).astype(np.float)
            glUnmapBuffer(GL_SHADER_STORAGE_BUFFER)
            return data.reshape(*self.Prop["asset"][3])
        elif tag    == "set_io":

            name = "io"
            glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.Prop[name][0])
            glBufferData(GL_SHADER_STORAGE_BUFFER, data.flatten().astype(np.float32), GL_DYNAMIC_DRAW)
            #glBindBufferBase(GL_SHADER_STORAGE_BUFFER,self.Prop[name][1], self.Prop[name][0])
            log.Info("Ssbo Set io %s bbid(%d)  shape(%s)  data_shape(%s)" % (
            name,self.Prop[name][1], self.Prop[name][3],data.shape))
        elif tag    == "np_io":
            name = "io"
            ptr = ctypes.c_float * mul(self.Prop[name][3])
            glBindBuffer(GL_SHADER_STORAGE_BUFFER, self.Prop[name][0])
            data = glMapBuffer(GL_SHADER_STORAGE_BUFFER, GL_READ_ONLY)
            data = np.ctypeslib.as_array(ptr.from_address(data)).astype(np.float)
            glUnmapBuffer(GL_SHADER_STORAGE_BUFFER)
            return data.reshape(*self.Prop[name][3])


if __name__ == "__main__":
   #ssbo = Ssbo()
   # ssbo.dataSet()
    p = Sampler(12345,"name")
    p.readIni(1000)