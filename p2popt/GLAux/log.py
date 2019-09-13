import logging.config
from logging import getLogger, StreamHandler, Formatter,FileHandler
from inspect import getframeinfo, stack
import os
import shutil
from functools import reduce

__all__ = ['Logg','log','LoggUtil',"dictString","mul"]
LOGDIR  = "%s/logging"%os.path.dirname(os.path.abspath(__file__))
LOGNAME = {"Log1": '%s\\file0.log'%LOGDIR}

class LoggUtil:

    def Clean(dir = LOGDIR):
        if os.path.exists(dir):
            shutil.rmtree(dir)
        os.mkdir(dir)

class CLogg:
    LEVEL  = {"Log":5,"Deb":10,"Inf":20,"War":30,"Err":40,"Cri":50}
    colors = {'pink': '\033[95m', 'blue': '\033[94m', 'green': '\033[92m', 'yellow': '\033[93m', 'red': '\033[91m',
              'ENDC': '\033[0m', 'bold': '\033[1m', 'underline': '\033[4m','rev':'\x1b[7m'}
    def __init__(self,cons= True,file= True,name = "Log1"):
        global LOGDIR
        self.C = False
        self.F = False
        if file:
            if name not in LOGNAME:
                LOGNAME[name] = "%s/%s.log"%(LOGDIR,name)
            self.flg = logging.getLogger(name)
            stream_handler2 = FileHandler(filename= LOGNAME[name])
            #stream_handler2.setLevel(logging.DEBUG)
            handler_format = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            stream_handler2.setFormatter(handler_format)
            self.flg.setLevel(logging.DEBUG)
            self.flg.addHandler(stream_handler2)
            self.F = True
        if cons:
            self.clg = getLogger("LogTest")
            stream_handler = StreamHandler()
            #stream_handler.setLevel(1)
            handler_format = Formatter('\033[92m %(asctime)s\x1b[0m:  \x1b[31m %(levelname)s  \x1b[0m  %(message)s')
            stream_handler.setFormatter(handler_format)
            self.clg.addHandler(stream_handler)
            #self.clg.setLevel(1)
            self.C = True
    def _color(self,color, data):
        return self.colors[color] + str(data) + self.colors['ENDC']
    def Set(self,L):
        if L in self.LEVEL:
            if self.C:self.clg.setLevel(self.LEVEL[L])
            if self.F:self.flg.setLevel(self.LEVEL[L])
        else:
            if self.C:self.clg.setLevel(L)
            if self.F:self.flg.setLevel(self.LEVEL[L])
    def GetInfo(self):
        caller = getframeinfo(stack()[2][0])
        #print("%s:%d - %s" % (caller.filename, caller.lineno, message))
        return  self._color('yellow',caller.lineno) + ":"
    def Log(self, s):
        if self.C:self.clg.log(5,self._color('green', s))
        if self.F:self.flg.log(5,s)
    def Debug(self, s):
        if self.C:self.clg.debug(self.GetInfo() + self._color('rev', s))
        if self.F: self.flg.debug(s)
    def Info(self,s):
        if self.C:self.clg.info(self._color('blue', s))
        if self.F: self.flg.info(s)
    def Warning(self,s):
        if self.C:self.clg.warning(self._color('red', s))
        if self.F: self.flg.warning(s)
    def Error(self,s):
        if self.C:self.clg.error(self._color('red', s))
        if self.F: self.flg.error(s)
    def Critical(self,s):
        if self.C:self.clg.critical(self._color('pink', s))
        if self.F: self.flg.critical(s)


class Logg:

    LEVEL  = {"Log":5,"Deb":10,"Inf":20,"War":30,"Err":40,"Cri":50}
    def __init__(self,cons= True,file= True,name = "Log1"):
        global LOGDIR
        self.C = False
        self.F = False
        if file:
            if name not in LOGNAME:
                LOGNAME[name] = "%s/%s.log"%(LOGDIR,name)
            self.flg = logging.getLogger(name)
            stream_handler2 = FileHandler(filename= LOGNAME[name])
            #stream_handler2.setLevel(logging.DEBUG)
            handler_format = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            stream_handler2.setFormatter(handler_format)
            self.flg.setLevel(logging.DEBUG)
            self.flg.addHandler(stream_handler2)
            self.F = True
        if cons:
            self.clg = getLogger("LogTest")
            stream_handler = StreamHandler()
            #stream_handler.setLevel(1)
            handler_format = Formatter('%(asctime)s  %(levelname)s  %(message)s')
            stream_handler.setFormatter(handler_format)
            self.clg.addHandler(stream_handler)
            #self.clg.setLevel(1)
            self.C = True
    def Set(self,L):
        if L in self.LEVEL:
            if self.C:self.clg.setLevel(self.LEVEL[L])
            if self.F:self.flg.setLevel(self.LEVEL[L])
        else:
            if self.C:self.clg.setLevel(L)
            if self.F:self.flg.setLevel(self.LEVEL[L])
    def GetInfo(self):
        caller = getframeinfo(stack()[2][0])
        #print("%s:%d - %s" % (caller.filename, caller.lineno, message))
        return  str(caller.lineno) + ":"
    def Log(self, s):
        if self.C:self.clg.log(5,s)
        if self.F:self.flg.log(5,s)
    def Debug(self, s):
        if self.C:self.clg.debug(self.GetInfo() +  s)
        if self.F: self.flg.debug(s)
    def Info(self,s):
        if self.C:self.clg.info(s)
        if self.F: self.flg.info(s)
    def Warning(self,s):
        if self.C:self.clg.warning( s)
        if self.F: self.flg.warning(s)
    def Error(self,s):
        if self.C:self.clg.error( s)
        if self.F: self.flg.error(s)
    def Critical(self,s):
        if self.C:self.clg.critical(s)
        if self.F: self.flg.critical(s)


def dictString(dict):
  return "\n".join("{}\t{}".format(k, v) for k, v in dict.items())

def mul(a):
    return reduce(lambda a,b:a*b,a)


LoggUtil.Clean()
log = CLogg()
log.Set("Log")
"""
logging.Log("Log Color")
logging.Info("Info Color")
logging.Debug("Debug Color")
logging.Warning("Warninig Color")
"""