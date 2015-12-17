

import python_toolkit
from python_toolkit.arrayQuery import single, where
from python_toolkit.stringUtils import matchIgnorecase
from vivado_toolkit.ip_packager.helpers import appendSpiElem, \
         mkSpiElm, spi_ns_prefix
from vivado_toolkit.ip_packager.others import Parameter
from vhdl_toolkit.types import DIRECTION


DEFAULT_CLOCK = 100000000
         
D = DIRECTION
         
class InterfaceIncompatibilityExc(Exception):
    pass         
         
class IfConfig():
    ifMaster, ifSlave = ("master", "slave")
    
    def findPort(self, logName):
        logName = logName.lower()
        p = single(self.port, lambda x : x.logName.lower() == logName)
        return p

    @classmethod
    def getPortWidth(cls, component, thisIf, name):
        name = thisIf._ifObj.findPort(name).phyName
        dim = single(component.model.ports, lambda p : p.name.lower() == (thisIf.name + name).lower()).vector
        return abs(dim[0] - dim[1]) + 1

    @classmethod
    def opositDir(cls, _dir_):
        if _dir_ == D.OUT:
            return D.IN
        elif _dir_ == D.IN:
            return D.OUT
        else:
            raise Exception()
    @classmethod
    def master(cls):
        self = cls()
        if len(self.port) == 0:
            raise Exception
        return self
    
    @classmethod
    def slave(cls):
        self = cls()
        for p in self.port:
            p.masterDir = cls.opositDir(p.masterDir)
        return self

    def addSimpleParam(self, thisIf, name, value):
        p_aw = Parameter()
        p_aw.name = name
        p_aw.value.resolve = "immediate"
        p_aw.value.id = "BUSIFPARAM_VALUE." + thisIf.name.upper() + "." + name.upper()
        p_aw.value.text = value
        thisIf.parameters.append(p_aw)
    
    
    def postProcess(self, component, entity, allInterfaces, thisIfPrefix):
        pass 



class IfConfMap():
    def __init__(self, logName, phyName=None, masterDir=DIRECTION.IN, width=None):
        self.logName = logName
        self.width = width
        if phyName is None:
            self.phyName = "_" + logName.lower()
        else:
            self.phyName = phyName
        self.masterDir = masterDir
    def __repr__(self):
        return "<IfConfMap {%s:%s}>" % (self.logName, self.phyName)

class BlockRamPort_withMissing_clk(IfConfig):
    """
    This interface is used only for check, it does not exists in vivado
    """
    def __init__(self):
        self.name = "BlockRamPort_withMissing_clk"
        self.version = None
        self.vendor = None 
        self.library = None
        c = IfConfMap
        self.port = [c("addr_V", masterDir=D.OUT),
                     c("din_V", masterDir=D.OUT),
                     c("dout_V", masterDir=D.IN),
                     c("en", masterDir=D.OUT),
                     c("we", masterDir=D.OUT)                     
                     ]

class BlockRamPort_withMissing_clk2(IfConfig):
    """
    This interface is used only for check, it does not exists in vivado
    """
    def __init__(self):
        self.name = "BlockRamPort_withMissing_clk"
        self.version = None
        self.vendor = None 
        self.library = None
        c = IfConfMap
        self.port = [c("addr_V", masterDir=D.OUT),
                     c("din", masterDir=D.OUT),
                     c("dout", masterDir=D.IN),
                     c("en", masterDir=D.OUT),
                     c("we", masterDir=D.OUT)                     
                     ]

class BlockRamPort(IfConfig):
    def __init__(self, A_WIDTH=None, D_WIDTH=None):
        self.name = "bram"
        self.version = "1.0"
        self.vendor = "xilinx.com"  
        self.library = "interface" 
        c = IfConfMap
        self.port = [c("ADDR", "_addr_V", masterDir=D.OUT, width=A_WIDTH),
                     c("CLK", "_clk", masterDir=D.OUT, width=1),
                     c("DIN", "_din_V", masterDir=D.OUT, width=D_WIDTH),
                     c("DOUT", "_dout_V", masterDir=D.IN, width=D_WIDTH),
                     c("EN", "_en", masterDir=D.OUT, width=1),
                     c("WE", "_we", masterDir=D.OUT, width=1)                     
                     ]

class BlockRamPort2(IfConfig):
    def __init__(self):
        self.name = "bram"
        self.version = "1.0"
        self.vendor = "xilinx.com"  
        self.library = "interface" 
        c = IfConfMap
        self.port = [c("ADDR", "_addr_V", masterDir=D.OUT),
                     c("CLK", "_clk", masterDir=D.OUT),
                     c("DIN", "_din", masterDir=D.OUT),
                     c("DOUT", "_dout", masterDir=D.IN),
                     c("EN", "_en", masterDir=D.OUT),
                     c("WE", "_we", masterDir=D.OUT)                     
                     ]

class Handshake(IfConfig):
    def __init__(self):
        self.name = "handshake"
        self.version = "1.0"
        self.vendor = "nic" 
        self.library = "user"
        c = IfConfMap
        self.port = [c("ap_vld", masterDir=D.OUT),
                     c("ap_ack", masterDir=D.IN),
                     c("data", masterDir=D.OUT)
                     ]
        
class Handshake2(Handshake):
    def __init__(self):
        super().__init__()
        c = IfConfMap
        self.port = [c("ap_vld", masterDir=D.OUT),
                     c("ap_ack", masterDir=D.IN),
                     c("data", "", masterDir=D.OUT)
                     ]
        
class HS_config_d(Handshake):
    def __init__(self):
        super().__init__()
        c = IfConfMap
        self.port = [c("ap_vld", masterDir=D.OUT),
                     c("ap_ack", masterDir=D.IN),
                     c("data", "_d", masterDir=D.OUT)
                     ]
class HS_config_d_V(Handshake):
    def __init__(self, D_WIDTH=0):
        super().__init__()
        c = IfConfMap
        self.port = [c("ap_vld", masterDir=D.OUT, width=1),
                     c("ap_ack", masterDir=D.IN, width=1),
                     c("data", "_d_V", masterDir=D.OUT, width=D_WIDTH)
                     ]

class Ap_clk(IfConfig):
    def __init__(self):
        self.name = "clock"
        self.version = "1.0"
        self.vendor = "xilinx.com" 
        self.library = "signal"
        c = IfConfMap
        self.port = [c("CLK", "ap_clk", masterDir=D.OUT, width=1)
                     ]
            
    def postProcess(self, component, entity, allInterfaces, thisIf):
            rst = list(where(allInterfaces, lambda intf: intf._ifCls  in [Ap_rst, Ap_rst_n]))
            if len(rst) > 0:
                self.addSimpleParam(thisIf, "ASSOCIATED_RESET", rst[0]._portMaps['rst'])  # getResetPortName
            elif len(rst) > 1:
                raise Exception("Dont know how to work with multiple resets")
            
            intfs = where(allInterfaces, lambda intf: intf._ifCls not  in  [Ap_clk, Ap_rst, Ap_rst_n])
            self.addSimpleParam(thisIf, "ASSOCIATED_BUSIF", ":".join(map(lambda intf: intf.name, intfs)))
            self.addSimpleParam(thisIf, "FREQ_HZ", str(DEFAULT_CLOCK))

class Ap_rst(IfConfig):
    def __init__(self):
        self.name = "reset"
        self.version = "1.0"
        self.vendor = "xilinx.com" 
        self.library = "signal"
        c = IfConfMap
        self.port = [c("rst", "ap_rst", masterDir=D.OUT, width=1)]
        
    def postProcess(self, component, entity, allInterfaces, thisIf):
        self.addSimpleParam(thisIf, "POLARITY", "ACTIVE_HIGH")

class Ap_rst_n(IfConfig):
    def __init__(self):
        self.name = "reset"
        self.version = "1.0"
        self.vendor = "xilinx.com" 
        self.library = "signal"
        c = IfConfMap
        self.port = [c("rst", "ap_rst_n", masterDir=D.OUT, width=1)]
        
    def postProcess(self, component, entity, allInterfaces, thisIf):
        self.addSimpleParam(thisIf, "POLARITY", "ACTIVE_LOW")
        
class AXIStream(IfConfig):
    def __init__(self):
        self.name = "axis"
        self.version = "1.0"
        self.vendor = "xilinx.com" 
        self.library = "interface"
        c = IfConfMap
        self.port = [c("TDATA", masterDir=D.OUT),
                     c("TLAST", masterDir=D.OUT),
                     c("TVALID", masterDir=D.OUT),
                     c("TSTRB", masterDir=D.OUT),
                     c("TREADY", masterDir=D.IN)
                     ]
class HsAXIStream(IfConfig):
    def __init__(self, D_WIDTH=0):
        self.name = "axis"
        self.version = "1.0"
        self.vendor = "xilinx.com" 
        self.library = "interface"
        c = IfConfMap
        self.port = [c("TDATA", "_d_DATA_V", masterDir=D.OUT, width=D_WIDTH),
                     c("TLAST", "_d_LAST", masterDir=D.OUT, width=1),
                     c("TVALID", "_ap_vld" , masterDir=D.OUT, width=1),
                     c("TSTRB", "_d_STRB_V" , masterDir=D.OUT, width=D_WIDTH // 8),
                     c("TREADY", "_ap_ack", masterDir=D.IN, width=1)
                     ]
        
class AXILite(IfConfig):
    def __init__(self, A_WIDTH=0, D_WIDTH=0):
        self.name = "aximm"
        self.version = "1.0"
        self.vendor = "xilinx.com" 
        self.library = "interface"
        self.A_WIDTH = A_WIDTH
        self.D_WIDTH = D_WIDTH
        c = IfConfMap
        self.port = [c("AWADDR", masterDir=D.OUT, width=A_WIDTH),
                     c("AWVALID", masterDir=D.OUT, width=1),
                     c("AWREADY", masterDir=D.IN, width=1),
                     
                     c("WDATA", masterDir=D.OUT, width=D_WIDTH),
                     c("WSTRB", masterDir=D.OUT, width=D_WIDTH // 8),
                     c("WVALID", masterDir=D.OUT, width=1),
                     c("WREADY", masterDir=D.IN, width=1),
                     
                     c("ARADDR", masterDir=D.OUT, width=A_WIDTH),
                     c("ARVALID", masterDir=D.OUT, width=1),
                     c("ARREADY", masterDir=D.IN, width=1),
                     
                     c("RDATA", masterDir=D.IN, width=D_WIDTH),
                     c("RRESP", masterDir=D.IN, width=2),
                     c("RVALID", masterDir=D.IN, width=1),
                     c("RREADY", masterDir=D.OUT, width=1),

                     c("BVALID", masterDir=D.IN, width=1),
                     c("BREADY", masterDir=D.OUT, width=1),
                     c("BRESP", masterDir=D.IN, width=2) 

                     ]

        
    def postProcess(self, component, entity, allInterfaces, thisIf):
        thisIf.endianness = "little"
        self.addSimpleParam(thisIf, "ADDR_WIDTH", self.getPortWidth(component, thisIf , "AWADDR"))
        self.addSimpleParam(thisIf, "DATA_WIDTH", self.getPortWidth(component, thisIf , "WDATA"))
        self.addSimpleParam(thisIf, "PROTOCOL", "AXI4LITE")
        self.addSimpleParam(thisIf, "READ_WRITE_MODE", "READ_WRITE")

class AXILite_with_V(AXILite):
    def __init__(self):
        super().__init__()
        c = IfConfMap
        self.port = [c("AWADDR", "AW_ADDR_V", masterDir=D.OUT),
                     c("AWVALID", "AW_VALID", masterDir=D.OUT),
                     c("AWREADY", "AW_READY", masterDir=D.IN),
                     
                     c("WDATA", "W_DATA_V", masterDir=D.OUT),
                     c("WSTRB", "W_STRB_V", masterDir=D.OUT),
                     c("WVALID", "W_VALID", masterDir=D.OUT),
                     c("WREADY", "W_READY", masterDir=D.IN),
                     
                     c("ARADDR", "AR_ADDR_V", masterDir=D.OUT),
                     c("ARVALID", "AR_VALID", masterDir=D.OUT),
                     c("ARREADY", "AR_READY", masterDir=D.IN),
                     
                     c("RDATA", "R_DATA_V", masterDir=D.IN),
                     c("RRESP", "R_RESP_V", masterDir=D.IN),
                     c("RVALID", "R_VALID", masterDir=D.IN),
                     c("RREADY", "R_READY", masterDir=D.OUT),

                     c("BVALID", "B_VALID", masterDir=D.IN),
                     c("BREADY", "B_READY", masterDir=D.OUT),
                     c("BRESP", "B_RESP_V", masterDir=D.IN) 

                     ]

class Axi(AXILite):
    def __init__(self, ID_WIDTH=0, A_WIDTH=0, D_WIDTH=0):
        super().__init__(A_WIDTH, D_WIDTH)
        c = IfConfMap
        self.ID_WIDTH = ID_WIDTH
        self.port += [
                      c("ARID", masterDir=D.OUT, width=ID_WIDTH),
                      c("ARBURST", masterDir=D.OUT, width=2),
                      c("ARCACHE", masterDir=D.OUT, width=4),
                      c("ARLEN", masterDir=D.OUT, width=8),
                      c("ARLOCK", masterDir=D.OUT, width=2),
                      c("ARPROT", masterDir=D.OUT, width=3),
                      c("ARSIZE", masterDir=D.OUT, width=3),
                      c("ARQOS", masterDir=D.OUT, width=4),
                      
                      c("BID", masterDir=D.IN, width=ID_WIDTH),
                      
                      c("AWID", masterDir=D.OUT, width=ID_WIDTH),
                      c("AWBURST", masterDir=D.OUT, width=2),
                      c("AWCACHE", masterDir=D.OUT, width=4),
                      c("AWLEN", masterDir=D.OUT, width=8),
                      c("AWLOCK", masterDir=D.OUT, width=2),
                      c("AWPROT", masterDir=D.OUT, width=3),
                      c("AWSIZE", masterDir=D.OUT, width=3),
                      c("AWQOS", masterDir=D.OUT, width=4),
                      
                      
                      c("RID", masterDir=D.IN, width=ID_WIDTH),
                      c("RLAST", masterDir=D.IN, width=1),
                      
                      c("WID", masterDir=D.OUT, width=ID_WIDTH),
                      c("WLAST", masterDir=D.OUT, width=1),
                      ]
                     
    def postProcess(self, component, entity, allInterfaces, thisIf):
        thisIf.endianness = "little"
        pw_param = lambda name, portLogName : self.addSimpleParam(thisIf, name, self.getPortWidth(component, thisIf , portLogName))
        param = lambda name, val :  self.addSimpleParam(thisIf, name, val)
        pw_param("ADDR_WIDTH", "AWADDR")
        param("MAX_BURST_LENGTH", str(256))
        param("NUM_READ_OUTSTANDING", str(5))
        param("NUM_WRITE_OUTSTANDING", str(5))
        param("PROTOCOL", "AXI4")
        param("READ_WRITE_MODE", "READ_WRITE")
        param("SUPPORTS_NARROW_BURST", str(0))
        
class Axi_channeled(Axi):
    def __init__(self, ID_WIDTH=0, A_WIDTH=0, D_WIDTH=0):
        super().__init__(ID_WIDTH, A_WIDTH, D_WIDTH)
        def splitPortName(name):
            if name.startswith("A"):
                return (name[:2], name[2:])
            if name[0] in ["B", "W", "R"]:
                return (name[0], name[1:])
            else:
                raise Exception()
        for p in self.port:
            ch, n = splitPortName(p.logName)
            p.phyName = "_" + ch + "_" + n
            if  n not in ["VALID", "READY" , "LAST"]:
                p.phyName += "_V" 

        
defaultBusResolve = [ Ap_clk, Ap_rst_n, Ap_rst, Axi, Axi_channeled, AXILite, AXILite_with_V, \
                      Handshake, Handshake2, HS_config_d, HS_config_d_V, AXIStream,
                      HsAXIStream, BlockRamPort, BlockRamPort2]


class Type():
    __slots__ = ['name', 'version', 'vendor', 'library']
     
    @classmethod 
    def fromElem(cls, elm):
        self = cls()
        for s in ['name', 'version', 'vendor', 'library']:
            setattr(self, s, elm.attrib[spi_ns_prefix + s])
        return self
    
    def asElem(self, elmName):
        e = mkSpiElm(elmName)
        for s in ['name', 'version', 'vendor', 'library']:
            e.attrib[spi_ns_prefix + s] = getattr(self, s)
        return e    
    
class BusInterface():
    def __init__(self):
        self.name = None
        self.busType = Type()
        self.abstractionType = Type()
        self.isMaster = None
        # logical : physical
        self._portMaps = {}
        self.parameters = [] 
        self._ifCls = None
        self.endianness = None
    # @classmethod
    # def fromElem(cls, elm):
    #    self = cls()
    #    self.name = elm.find('spirit:name', ns).text
    #    self.busType = Type.fromElem(elm.find('spirit:busType', ns))
    #    self.abstractionType = Type.fromElem(elm.find('spirit:abstractionType', ns))
    #    if elm.find('spirit:master', ns) is not None:
    #        self.isMaster = True
    #    elif elm.find('spirit:slave', ns) is not None:
    #        self.isMaster = False
    #    else:
    #        raise Exception("buss missing master/slave specification")
    #    self._portMaps = []
    #    for m in elm.find('spirit:_portMaps', ns):
    #        pm = PortMap.fromElem(m)
    #        self._portMaps.append(pm)
    #    
    #    self.parameters = []
    #    for p in elm.find('spirit:parameters', ns):
    #        p_obj = Parameter.fromElem(p)
    #        self.parameters.append(p_obj)
    #        
    #    return self
    
    def asElem(self):
        def mkPortMap(logicalName, physicalName):
            pm = mkSpiElm("portMap")
            appendSpiElem(appendSpiElem(pm, "logicalPort"), "name").text = logicalName
            appendSpiElem(appendSpiElem(pm, "physicalPort"), "name").text = physicalName
            return pm
        
        e = mkSpiElm("busInterface")
        
        
        appendSpiElem(e, 'name').text = self.name
        e.append(self.busType.asElem('busType'))
        e.append(self.abstractionType.asElem('abstractionType'))
        if self.isMaster:
            appendSpiElem(e, "master")
        else:
            appendSpiElem(e, "slave")
       
        pm = appendSpiElem(e, "portMaps")

        for lName, pName in sorted(self._portMaps.items(), key=lambda pm: pm[0]):
            pm.append(mkPortMap(lName, pName))
        if self.endianness is not None:
            appendSpiElem(e, "endianness").text = self.endianness
        if len(self.parameters) > 0:
            pm = appendSpiElem(e, "parameters")
            for p in self.parameters:
                pm.append(p.asElem())
        return e
    

def extractBusInterface(entity, interface, excOnIncompatibilytiy=False):
        """
        @return: yields busInterfce objects for interface in unit 
        """
        m = interface.master()
        firstIntfPort = m.port[0]

        def firstPortInstances():
            """
            @return: unit ports witch probably matches with this interface
            """
            for x in entity.port:
                if not hasattr(x, "ifCls") and x.name.lower().endswith(firstIntfPort.phyName.lower()):
                    yield x
                    
        def getIfPrefix(entPort, interfaceConf):
            pName = entPort.name.lower()
            iName = firstIntfPort.phyName.lower()
            if pName == iName:
                return interfaceConf.name
            else:
                return  pName[:-len(iName)]
            
        def getMap(ifprefix, intfCls, ent):
            """
            @return:None if intf. can't be mapped otherwise returns (master/slave, {logical : physical})
            """
            allMatch = True
            noneMatch = True
            ifMap = {}
            for bi in m.port:
                try:
                    ep = single(ent.port, lambda p : matchIgnorecase(p.name, ifprefix + bi.phyName))
                except python_toolkit.arrayQuery.NoValueExc:
                    raise InterfaceIncompatibilityExc("Missing " + ifprefix + bi.phyName.lower())
                dirMatches = ep.direction.lower() == bi.masterDir
                allMatch = allMatch and dirMatches
                noneMatch = noneMatch  and not dirMatches     
                ifMap[bi.logName] = ifprefix + bi.phyName
                
            if allMatch:
                ifT = IfConfig.ifMaster
            elif noneMatch:
                ifT = IfConfig.ifSlave
            else:
                raise InterfaceIncompatibilityExc("Direction mismatch")

            return (ifT, ifMap)
        
        def getBusTypeFromConf(IfConfigObj):
            t = Type()
            for s in t.__slots__:
                setattr(t, s, getattr(IfConfigObj, s))
            return t
        if excOnIncompatibilytiy and len(list(firstPortInstances())) == 0:
            raise InterfaceIncompatibilityExc("Cant find " + firstIntfPort.phyName)
        for fpi in firstPortInstances():
            ifName = getIfPrefix(fpi, m)
            if fpi.name == firstIntfPort.phyName:
                ifPrefix = ""
            else:
                ifPrefix = ifName
            try:
                ifMap = getMap(ifPrefix, interface, entity)
                bi = BusInterface()
            
                if ifPrefix == "":
                    bi.name = m.name
                else:
                    bi.name = ifName
                isMaster = ifMap[0] == IfConfig.ifMaster
                bi.busType = getBusTypeFromConf(m)
                bi.abstractionType = getBusTypeFromConf(m)
                bi.abstractionType.name += "_rtl"
                bi.isMaster = isMaster
                bi._portMaps = ifMap[1]
                # bi._ifCls = interface
                if isMaster:
                    bi._ifObj = m
                else:
                    bi._ifObj = interface.slave()
                for intfPort in m.port: 
                    single(entity.port, lambda p : p.name.lower() == ifPrefix + intfPort.phyName.lower()).ifCls = interface
                yield bi
            except InterfaceIncompatibilityExc as e:
                if excOnIncompatibilytiy:
                    raise e
                else:
                    pass
