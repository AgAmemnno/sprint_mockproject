from p2popt.GLAux.log import *
from jinja2 import Template, Environment, FileSystemLoader
import re

INCLUDE = "../GLAux/glsl/include/"
pattern = '.*#include +<(.*)>.*'
class ParseProgram:
    inc     = {}
    ofs     = []


def parse(filename,i=0):
    global inc,ofs
    sha = ""
    log.Info("parse "+filename)
    if i ==0:
        ParseProgram.inc = {}
        ParseProgram.ofs = []
        sha = "#version 460 core\n"
        ParseProgram.ofs.append([sha,1])
    with open(filename) as fp:
        for l in fp.readlines():
            result = re.match(pattern,l)
            if result != None:
                f = result.group(1)
                if not f in ParseProgram.inc:
                    ParseProgram.inc[f] = 1
                    l = parse(INCLUDE + f,1)
                    ofth  = len(ParseProgram.ofs) - 1
                    ParseProgram.ofs.append([INCLUDE+f, ParseProgram.ofs[ofth][1]+len(l.split("\n"))-1])
                else:
                    l = ""
            sha += l
    return sha + "\n"


class ConstRender:
    def __init__(self,dir= "../GLAux/glsl/include/"):
        self.dir = dir
        self.env = Environment(loader=FileSystemLoader(dir))
    def render(self,path,const = {}):

        OBJ = {}
        OBJ['CONST'] = const
        import os
        #print(self.dir,"   ",path,"   ",__file__,"  ",os.getcwd())
        tpl = self.env.get_template(path)
        shader = tpl.render(OBJ)
        path = path.replace(".tpl", ".glsl")
        with open(self.dir + path , mode='w') as f:
            f.write(shader)

if __name__ == "__main__":

    #pattern = '.*\<(.)\>.*'
    #result = re.match(pattern, "adfa <adfad> ")

    pattern = '.*"(.*)".*'
    result = re.match(pattern, 'adfjkl "adfja" ')
    print(result.group(1))

    result = re.match(pattern, 'adfjkl ')
    print(result == None)

    pattern = '.*#include +<(.*)>.*'
    result = re.match(pattern, '  #include    <a.glsl>')
    print(result.group(1))

    vert = parse("F:\MT5\Charm2019\Recognition\GLAux\glsl\\test\\test3.vert", 0)
    print(vert)