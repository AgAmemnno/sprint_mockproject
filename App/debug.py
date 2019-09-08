import redis
import numpy as np
from jinja2 import Template, Environment, FileSystemLoader
import subprocess

from GLAux.log import *


Ini_Charts ={
    'Assign':False,
    'ProfileLast': "Default",
    'MaxBars': 100000,
    'PrintColor': 0,
    'SaveDeleted': 0,
    'TradeLevels': 1,
    'TradeLevelsDrag': 0,
    'ObsoleteLasttime': 1538575276
}
Ini_Common = {
    'Assign': False,
    'Login': 25376369,
    'ProxyEnable': 0,
    'ProxyType': 0,
    'ProxyAddress': "",
    'ProxyAuth': "",
    'CertInstall': 0,
    'NewsEnable': 1,
    'NewsLanguages': "",
}
Ini_Experts = {
    'Assign': False,
    'Exprt':'',
    'Script': '',
    'Symbol': '',
    'Period': '',
    'ExpertParameters':'',
}
Ini_Script = {
    'Assign': False,
    'Script': '',

}
Ini_Tester = {

    'Assign' : False,
    'Expert': "Ku3\ptn_t_entry_opt",
    'ExpertParameters':"\Ku3\entry_opt.set",
    'Symbol': "KUUSD",
    'Period': "H4",
    'Deposit': 100000,
    'Model': 2,
    'Optimization': 2,
    'OptimizationCriterion': 0,
    'FromDate': "2012.01.01",
    'ToDate': "2019.03.08",
    'Report': "\\Tester\\html\\Ku3\\entry_opt\\profile",
    'ReplaceReport': 1,
    'UseLocal': 1,
    'Port': 3000,
    'Visual': 0,
    'ShutdownTerminal': 0,
}
DotIni = {
    'Ch': Ini_Charts,
    'Co': Ini_Common,
    'Ex': Ini_Experts,
    'Te': Ini_Tester,
}

DIR_TESTER="C:\\Users\\kaz38\\AppData\\Roaming\\MetaQuotes\\Terminal\\81A5DD5647C1537B178355C19B95D5C5\\MQL5\\Profiles\\Tester\\"
TERMINAL="D:\\XMTrading MT5\\terminal64.exe"
CONFIG="D:\\Python\\sprint\\App\\Debug\\"

def write_set_all(tester_set,Params):
    _set = ""
    f = open(tester_set, mode='r')
    null = False
    for c, l in enumerate(f):
        if c == 0:
            if l.split(";")[0] == "":
                l = "\x00;" + l.split(";")[1]
                null = True
        if len(l) <= 1: continue
        if null:
            if l[1] != ";":
                name = l.split("=")
                # print(name)
                _name = name[0][1::2]
                if _name in Params:
                    # _set += name[0] + ''.join("\x00" +i for i in  Params[_name])
                    _set += _name + Params[_name]
                else:
                    _set += l[1::2]
            else:
                _set += l[1::2]
        else:
            if l[0] != ";":
                name = l.split("=")
                # print(name)
                _name = name[0]
                if _name in Params:
                    # _set += name[0] + ''.join("\x00" +i for i in  Params[_name])
                    _set += _name + Params[_name]
                else:
                    _set += l
            else:
                _set += l
    print(_set)
    f.close()
    with open(tester_set, mode='w') as f:
        f.write(_set)
def write_set(tester_set,Params):
    _set = ""
    f    = open(tester_set, mode='r')
    null = False
    for c, l in enumerate(f):
        if c == 0:
            if l.split(";")[0] == "":
                l = "\x00;" + l.split(";")[1]
                null = True
        if len(l) <= 1: continue
        if null:
            if l[1] != ";":
                name = l.split("=")
                # print(name)
                _name = name[0][1::2]
                if _name in Params:
                    _para    =  name[1][1::2]
                    _para    = _para.split("||")
                    _para[0] = Params[_name]
                    _set += _name + "=" + "||".join(_para)
                else:
                    _set += l[1::2]
            else:
                _set += l[1::2]
        else:
            if l[0] != ";":
                name = l.split("=")
                # print(name)
                _name = name[0]
                if _name in Params:
                    _para = name[1]
                    _para = _para.split("||")
                    _para[0] = Params[_name]
                    _set += _name + "=" + "||".join(_para)
                else:
                    _set += l
            else:
                _set += l
    print(_set)
    f.close()
    with open(tester_set, mode='w') as f:
        f.write(_set)
def read_set(tester_set):
    Params = {}
    f    = open(tester_set, mode='r')
    null = False
    for c, l in enumerate(f):
        if c == 0:
            if l.split(";")[0] == "":
                l = "\x00;" + l.split(";")[1]
                null = True
        if len(l) <= 1: continue
        if null:
            if l[1] != ";":
                name = l.split("=")
                # print(name)
                _name = name[0][1::2]
                _para    =  name[1][1::2]
                _para    = _para.split("||")
                Params[_name] = _para[0]
        else:
            if l[0] != ";":
                name = l.split("=")
                _name    = name[0]
                _para    = name[1]
                _para = _para.split("||")
                Params[_name] = _para[0]

    f.close()
    return Params


class Debug_MT():
    def __init__(self):
        pool = redis.ConnectionPool(host='localhost', port=6379, db=2)
        self.r = redis.StrictRedis(connection_pool=pool)

        self.path = "./Debug"
        self.env = Environment(loader=FileSystemLoader(self.path))

        self.TESTER_INI = '\\tester_onece.ini'


    def Range4(self, Params, st="2019.08.01", ed="2019.09.01", peri='M1', symbol="GBPAUD", sd=1, vs=0,dp =2):
        log.Log("Forward OverAll  %s ==>  %s  %s(%s)" % (st, ed, symbol, peri))

        Parameters = "range\\sample.set"

        Ini_Tester = {
            'Assign': False,
            'Expert': "KuPip\\Indicator\\Range4",
            'ExpertParameters': Parameters,
            'Symbol': symbol,
            'Period': peri,
            'Deposit': 1000000,
            'Model': 1,
            'Optimization': 0,
            'OptimizationCriterion': 0,
            'FromDate': st,
            'ToDate': ed,
            'Report': "",
            'ReplaceReport': 0,
            'UseLocal': 1,
            'Port': 3000,
            'Visual': vs,
            'ShutdownTerminal': sd,
        }

        DotIni['Te'] = Ini_Tester
        tpl = self.env.get_template('common_tpl')
        html = tpl.render(DotIni)
        with open(self.path + self.TESTER_INI, mode='w') as f:
            f.write(html)



        Params["DumpMfi"] = "=%d\n"%(dp)

        _tester_set = DIR_TESTER + Parameters
        write_set_all(_tester_set, Params)
        subprocess.run(TERMINAL + "  /config:" + CONFIG + self.TESTER_INI)

    def get_mfi(self):
        b = self.r.hget("Range4", "Buf1")
        self.buf1 = np.frombuffer(bytes.fromhex(b.decode()), dtype=np.float32)
        b = self.r.hget("Range4", "Buf2")
        self.buf2 = np.frombuffer(bytes.fromhex(b.decode()), dtype=np.float32)
        b = self.r.hget("Range4", "Buf3")
        self.buf3 = np.frombuffer(bytes.fromhex(b.decode()), dtype=np.float32)
        print(self.buf1)
        print(self.buf2)
        print(self.buf3)

def Set_Params(p):
    Params = {
        "MFIROLL"  : "=" + str(int(p[0])) + "\n",
        "MFIROLL2" : "=" + str(int(p[1])) + "\n",
        "MFI_EMA"   :  "=" + "%.1f"%(p[2])  + "\n",
        "BB_AM"    : "=" + "%d"%(p[3])  + "\n",
        "BB_EM1"   : "=" + "%d"%(p[4])  + "\n",
        "BB_EM2"   : "=" + "%d"%(p[5])  + "\n",
        "BB_FSSC"   : "=" + "%.6f" %(p[6]) + "\n",
        "bandTH"    : "=" + "%.2f" % (p[7]) + "\n"
    }
    return Params

if __name__ == "__main__":

    deb = Debug_MT()
    deb.Range4(Set_Params([50.0, 60.0, 13.399999618530273, 59.0, 57.0, 43.0, 0.008999999612569809, 0.44999998807907104]),sd =0,vs = 1)
    deb.get_mfi()
