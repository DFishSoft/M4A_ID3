def getID3(filename):
    
    def b2int(mbytes):
      return int.from_bytes(mbytes,byteorder="big" ,signed=False)

    def _readAtom(offset):
        fp.seek(offset)
        size = b2int(fp.read(4))
        name = fp.read(4)
        return (name, size - 8)
        
    def readAtom(offset,ending = 0):
        #这是一个递归函数，获取ID3信息位置
        atomInfo = {}
        cursor = 0
    
        #这些ATOM之后紧跟着是所属子层次的ATOM 
        atomList  = [b"moov",b"trak",b"mdia",b"minf",b"stbl",b"udta",b"ilst"]

        while True:

            #如果设置的结束位置，且游标超出则退出循环

            if ending > 0 and ending <= offset:break

            tag = _readAtom(offset)

            if tag[0] in (atomList):
                #记录当前游标位置
                #ATOM结束位置等于当前游标加ATOM大小
                cursor = fp.tell()
                Ending = cursor + tag[1]
                #查找子ATOM
                subatomInfo = readAtom(fp.tell(), Ending)
                atomInfo[tag[0].decode("ascii")] = subatomInfo
                offset = Ending
            elif tag[0] == b"meta":
                #记录当前游标位置
                #ATOM结束位置等于当前游标加ATOM大小
                cursor = fp.tell()
                Ending = cursor + tag[1]
                #查找子ATOM
                subatomInfo = readAtom(fp.tell() + 4, Ending)
                atomInfo[tag[0].decode("ascii")] = subatomInfo
                offset = Ending
            elif tag[0] == b"":
                break
            else:
                #记录当前游标位置
                cursor = fp.tell()
                key = tag[0]
                if tag[0][0] == 0xa9:
                    key = bytearray([tag[0][1],tag[0][2],tag[0][3]])
                key = key.decode("ascii")
                index = 0
                while True:
                    index += 1
                    if not key in atomInfo.keys():
                        break
                    key += str(index)
                atomInfo[key] = [cursor, tag[1]]
                offset = cursor + tag[1]
        return atomInfo



    def myDecode(mBytes):
        #自动尝试各种编码
        codes = ["","utf-8","unicode","gb18030","gbk","gb2312","ascii"]

        while True:

            for code in codes:
                try:
                    return mBytes.decode(code)
                except:
                    pass
                
            return False

    def id3info(tree):
        #获取ID3信息
        info = {}
        tags = [["nam","标题","str"],
                ["ART","艺术家","str"],
                ["alb","专辑","str"],
                ["too","编码器","str"],
                ["cmt","评论","str"],
                ["wrt","作曲家","str"],
                ["tmpo","BPM","uint"],
                ["trkn","跟踪号码","uint"],
                ["day","年","str"],
                ["cpil","编译","uint"],
                ["aART","专辑的艺术家","str"],
                ["gen","类型","str"]]

        for tag in tags:
            try:
                cursor, size = tree["moov"]["udta"]["meta"]["ilst"][tag[0]]
                fp.seek(cursor + 16)
                mBytes = fp.read(size - 16)

                if tag[2] == "str":
                    info[tag[1]] = myDecode(mBytes)
                else:
                    info[tag[1]] = b2int(mBytes)
                    
            except KeyError:
                    info[tag[1]] = None

        return info
                    
    fp = open(filename, 'rb')

    atomInfo = readAtom(0)

    content = id3info(atomInfo)

    fp.close()

    return  {"position": atomInfo, "content":content}


##################################################
# 这是一个例子
##################################################

def print_tree(tree,root):
    buff = [root]
    _print_tree(tree, buff, '')
    print('\n'.join(buff))
 

def _print_tree(tree, buff, prefix):
    count = len(tree)
    for k, v in tree.items():
        count -= 1
        if type(v) == dict:
            buff.append('%s +- %s/' % (prefix, k))
            if count > 0:
                _print_tree(v, buff, prefix + ' |  ')
            else:
                _print_tree(v, buff, prefix + '    ')
        else:
            buff.append('%s +- %s: %s' % (prefix, k,str(v)))


    
if __name__ == '__main__':

    filePath = r"F:\Python\AudioSpider\AudioSpider\[123]人类的解放\[01]序言.m4a"

    tree = getID3(filePath)

    print("-"*50)

    print_tree(tree["position"],"M4A-ID3")

    print("-"*50)

    print_tree(tree["content"],"M4A-ID3")

    print("-"*50+"\n")

    input("")

"""
这是运行结果
--------------------------------------------------
M4A-ID3
 +- ftyp: [8, 16]
 +- moov/
 |   +- mvhd: [40, 100]
 |   +- trak/
 |   |   +- tkhd: [156, 84]
 |   |   +- edts: [248, 28]
 |   |   +- mdia/
 |   |       +- mdhd: [292, 24]
 |   |       +- hdlr: [324, 37]
 |   |       +- minf/
 |   |           +- smhd: [377, 8]
 |   |           +- dinf: [393, 28]
 |   |           +- stbl/
 |   |               +- stsd: [437, 97]
 |   |               +- stts: [542, 24]
 |   |               +- stsc: [574, 44]
 |   |               +- stsz: [626, 24600]
 |   |               +- stco: [25234, 20]
 |   +- udta/
 |       +- meta/
 |       |   +- hdlr: [25282, 25]
 |       |   +- ilst/
 |       |       +- nam: [25323, 39]
 |       |       +- ART: [25370, 39]
 |       |       +- alb: [25417, 39]
 |       |       +- too: [25464, 29]
 |       |       +- cmt: [25501, 39]
 |       |       +- wrt: [25548, 39]
 |       |       +- tmpo: [25595, 17]
 |       |       +- trkn: [25620, 24]
 |       |       +- day: [25652, 20]
 |       |       +- cpil: [25680, 17]
 |       |       +- aART: [25705, 39]
 |       |       +- gen: [25752, 39]
 |       +- Xtra: [25799, 986]
 +- free: [26793, 0]
 +- mdat: [26801, 2283729]
--------------------------------------------------
M4A-ID3
 +- 标题: 爱听书 aitingshu.com
 +- 艺术家: 爱听书 aitingshu.com
 +- 专辑: 爱听书 aitingshu.com
 +- 编码器: Lavf56.18.101
 +- 评论: 爱听书 aitingshu.com
 +- 作曲家: 爱听书 aitingshu.com
 +- BPM: 0
 +- 跟踪号码: 8667244003328
 +- 年: 2018
 +- 编译: 0
 +- 专辑的艺术家: 爱听书 aitingshu.com
 +- 类型: 爱听书 aitingshu.com
--------------------------------------------------
"""
