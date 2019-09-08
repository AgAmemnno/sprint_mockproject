import numpy as np
from OpenGL.GL import *
from OpenGL.GL.shaders import *

from GLAux.log import *
from App.config import *



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
        path = "D:\Python\sprint\Data\GBPAUD_M1_201908.csv"
        data = np.loadtxt(path, delimiter="\t", skiprows=1, usecols=(2, 3, 4, 5))
        return np.hstack((np.arange(len(data)).reshape(len(data), 1), data))
    def Set_data(self,name="data",bbid= 3,mt = False):
        if mt:
            data = self.load_mt()
        else:
            data = np.loadtxt(config[name],delimiter=",",skiprows=0,usecols=(1, 2, 3, 4, 5))
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
    ssbo = Ssbo()
    ssbo.dataSet()