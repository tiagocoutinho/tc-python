from sardana.macroserver.macro import Macro, Type, Hookable
import time
import PyTango
FEAUTO_ATTR = "BL04/ct/eps-plc-01/FE_AUTO"
FE_PSS_PERMIT = "alba03:10000/expchan/id04scw_machine_attributes/8/value"
FE_CTRL_DISABLE = "BL04/ct/eps-plc-01/FE_CONTROL_DISABLED"
FE_BL_READY = "BL04/ct/eps-plc-01/bl_ready"
TEMPNAME = ['filt','vwin','wbat','mir','mma','mono']
CCGNAME = ['tru','filt','wbat','mir','blvs','mono','coll','pshu']
IPNAME =  ['filt','wbat','mir','blvs','fs','mono','coll','pshu']
VALVE_STATE = ["CLOSED","OPEN"]
FLOWSW =['filter','cvd','Wbatt','mirr_front','mirr_side1','mirr_side2','wfsm','monoBS','JulaboCool','JulaboCirc','Wbatt_Front','MMA']
#FLOWSW =['filter','cvd','Wbatt_Front','Wbatt','mirr_front','mirr_side1','mirr_side2','MMA','wfsm','monoBS','JulaboCool','JulaboCirc']


class BLstate(Macro):
    """Check status of VACUUM and fluids parameters  """

    def run(self, *args, **kwargs):
        self.output("Valves")
        self.execMacro("PNVstate")
        self.output("Cold cathode gauges")
        self.execMacro("CCGstate")
        self.output("Ionic pump controllers")
        self.execMacro("IPstate")
        self.output("Water flow")
        self.execMacro("WFLOWstate")
        self.output("Air flow")
        self.execMacro("AIRstate")
        self.execMacro("TEMPstate")
        self.output("Mono Cryocooler")
        self.execMacro("_CRYOstat")


class _CRYOstat(Macro):

    param_def = [ ['spar', Type.String, 'None', 'IPname' ] ]

    def run(self,spar):
        dev_name = "BL04/EX/CRY-01"
        dev = PyTango.DeviceProxy(dev_name)
        loctime = time.strftime("%a %b %d %Y %H:%M:%S",time.localtime())
        self.warning(loctime)
        sAtt="State"
        _ivState = dev.read_attribute(sAtt).value
        sAtt="Status"
        _ivStatus = dev.read_attribute(sAtt).value
      #  if PyTango.DevState.ALARM : 
      #    #self.error("WARNING !!! CryoCooler State in ALARM")
      #    #self.error("WARNING !!! %r"%(_ivStatus))
      #    raise Exception("CryoCooler State in ALARM")

        sAtt="ExternalInterlock"
        _ivItlk = dev.read_attribute(sAtt).value
        self.info("CryoCoolerInterlock is %r"%(_ivItlk))
        if not _ivItlk :
           self.error("WARNING !!!  CryoCooler Interlock active ")  

        sAtt="Ready"
        _ivReady = dev.read_attribute(sAtt).value
        self.info("CryoCoolerReady is %r"%(_ivReady))
        if not _ivReady :
           self.error("WARNING !!!  CryoCooler not ready ")  

        sAtt="CoolingPower"
        _ivPcool = dev.read_attribute(sAtt).value
        sAtt="PT1"
        _ivPT1 = dev.read_attribute(sAtt).value
        sAtt="T5"
        _iv5 = dev.read_attribute(sAtt).value
        sAtt="T6"
        _iv6 = dev.read_attribute(sAtt).value
        sAtt="V9_Control"
        _ivV9 = dev.read_attribute(sAtt).value
        sAtt="FT18"
        _ivFT18 = dev.read_attribute(sAtt).value
        sAtt="V11_Aperture"
        _ivV11 = dev.read_attribute(sAtt).value

        self.info("\n**** DCM ****")  
        self.info("T lN2 in/out (T5/T6)  =  %.1f/%.1f K, Pressure (PT1) %.1f Bar,  Power %.0f W "%(_iv5,_iv6,_ivPT1,_ivPcool))
        self.info("Valve (V9) lN2in open %r, Valve (V11) lN2out =  %.0f %%, Flow (FT18) lN2out  %.1f l/m "%(_ivV9,_ivV11,_ivFT18))

        sAtt="PT3"
        _ivPT3 = dev.read_attribute(sAtt).value
        sAtt="HeaterVesselAUT"
        _ivHeatPmode = dev.read_attribute(sAtt).value
        sAtt="HeaterVesselPressure"
        _ivHeatP = dev.read_attribute(sAtt).value
        sAtt="LT23"
        _ivLT23 = dev.read_attribute(sAtt).value
        sAtt="LT23_LowerLimit"
        _ivLT23low = dev.read_attribute(sAtt).value
        sAtt="LT23_UpperLimit"
        _ivLT23up = dev.read_attribute(sAtt).value

        self.info("\n**** HEATER VESSEL ****")  
        self.info("Pressure (PT3) = %.1f Bar (set %.1f), MODE AUTO %r, lN2 level (LT23) = %.1f %% (min/max = %.1f/%.1f )"%(_ivHeatP,_ivPT3,_ivHeatPmode, _ivLT23,_ivLT23low,_ivLT23up))
        if not _ivHeatPmode :
           self.error("WARNING !!!  Control system pressure mode is %r"%(_ivHeatPmode))  

        sAtt="LT19"
        _ivLT19 = dev.read_attribute(sAtt).value
        sAtt="LT19_LowerLimit"
        _ivLT19low = dev.read_attribute(sAtt).value
        sAtt="LT19_UpperLimit"
        _ivLT19up = dev.read_attribute(sAtt).value
        sAtt="FillSubCoolON"
        _ivLT19mode = dev.read_attribute(sAtt).value
        self.info("\n**** LN2 SUBCOOLER  ****")  
        self.info("lN2 level (LT19) = %.1f %% (min/max = %.1f/%.1f, AUTORefill mode %r )"%(_ivLT19,_ivLT19low,_ivLT19up,_ivLT19mode))
        if not _ivLT19mode :
           self.error("WARNING !!!  AUTORefill mode is %r"%(_ivLT19mode))  

        sAtt="V10_Aperture"
        _ivV10 = dev.read_attribute(sAtt).value
        sAtt="PumpFrequency"
        _ivPump = dev.read_attribute(sAtt).value
        self.info("\n**** PUMP ****")
        self.info("Pump frequency  = %.0f Hz (Valve (V10) circulation %.0f %%)"%(_ivPump,_ivV10))




class VACUUMstate(Macro):
    """Check status of VACUUM and fluids parameters  """

    def run(self, *args, **kwargs):
        loctime = time.strftime("%a %b %d %Y %H:%M:%S",time.localtime())
        self.warning(loctime)
        self.output("Valves")
        self.execMacro("PNVstate")
        self.output("Cold cathode gauges")
        self.execMacro("CCGstate")
        self.output("Ionic pump controllers")
        self.execMacro("IPstate")
     #   self.output("Water flow")
     #   self.execMacro("WFLOWstate")
     #   self.output("Air flow")
     #   self.execMacro("AIRstate")
     #   self.execMacro("_TEMPstat mono")


class PNVstate(Macro):
    """Check status of all gate valves  """

    param_def = [['iv1', Type.Integer, -99, 'valve nr: 1-5'],
                 ['iv2', Type.Integer, -99, 'valve nr: 1-5']]


    def run(self, *args, **kwargs):
        if args[0] < 0 :
            iv1 = 0
        else :
            iv1 = args[0]
        if args[1] < 0 :
            #iv2 = iv1
            iv2 = 5
        else :
            iv2 = args[1]

        for _iv in range(iv1,iv2+1):
            _r = self.execMacro("_PNVstat",_iv).getResult()


class _PNVstat(Macro):
    """Check status of specific valve (nr 0-5)  """

    param_def = [
       ['nValve', Type.Integer, -99, 'Valve number' ]
    ]

    def run(self,nValve):
        if nValve == -99 :  nValve =0
        dev = PyTango.DeviceProxy("BL04/ct/eps-plc-01")
        sValve = "pnv_oh01_"+("%.2d"%nValve)
        if nValve == 0 : sValve = "tru_vl"
        _iv = dev.read_attribute(sValve).value
        if _iv != 1 : self.error("Valve nr %d ( %-30s ) is %s "%(nValve,sValve,VALVE_STATE[_iv] ))
        else : self.info("Valve nr %d ( %-30s ) is %s "%(nValve,sValve,VALVE_STATE[_iv] ))

        return _iv


class _PNVopen(Macro):
    """Open/close of single gate valve (nr 0-5)  """

    param_def = [
       ['iV', Type.Integer, -99, 'valve nr (1-5)' ],
       ['nV', Type.Integer, -99, '0/1 close/open' ],
    ]

    def run(self,iV,nV):
        if iV < 0 or iV > 5 :
            raise Exception("valve shoudl be 0 to 5")

        if nV == -99 :
            raise Exception("Give either 0/1 for open/close")
        dev = PyTango.DeviceProxy("BL04/ct/eps-plc-01")

        sValve = "pnv_oh01_"+("%.2d"%iV)
        if iV == 0 : sValve = "tru_vl"
        self.output("%s to %s" %(sValve,VALVE_STATE[nV] ))
        dev.write_attribute(sValve, nV)

class PNVopen(Macro):
    """Open/close several  valves (nr 0-5)  """

    param_def = [
       ['iVl', Type.Integer, -99, 'valve nr (0-5)' ],
       ['iVh', Type.Integer, -99, 'valve nr (0-5)' ],
    ]

    def run(self,iVl,iVh):
        if iVh < iVl :iVh = iVl
        #if iVl > -1 :
        for iV in range(iVl,iVh+1) : self.execMacro('_PNVopen',iV,1)
        #else :
        #   self.execMacro("PNVstate")

class PNVclose(Macro):
    """Open/close oseveral valves (nr 0-5)  """

    param_def = [
       ['iVl', Type.Integer, 0, 'valve nr (0-5)' ],
       ['iVh', Type.Integer, 0, 'valve nr (0-5)' ],
    ]

    def run(self,iVl,iVh):
        if iVh < iVl :iVh = iVl
        for iV in range(iVl,iVh+1) : self.execMacro('_PNVopen',iV,0)


class WFLOWopen(Macro):
    """Open water valves  """

    param_def = [
       ['iVl', Type.Integer, 0, 'valve nr (0-5)' ],
       ['iVh', Type.Integer, 0, 'valve nr (0-5)' ],
    ]

    def run(self,iVl,iVh):
        dev_name = "BL04/ct/eps-plc-01"
        dev = PyTango.DeviceProxy(dev_name)
        for iV in range(2) :
            sValve = "was_x01_"+("%.2d"%(iV+1))+"_ev1"
            self.debug(dev_name + "/" + sValve)
            dev.write_attribute(sValve, 1)
        self.warning("!!! WARNING, reset FLOW SWITCHES to avoid water valve closing (type _PLCreset ")

#class _PLCreset(Macro):
#    """Reset PLC"""
#
#    def run(self):
#        dev_name = "BL04/ct/eps-plc-01"
#        dev = PyTango.DeviceProxy(dev_name)
#        #val = dev.read_attribute('PLC_CONFIG_RESET').value
#        self.warning("Resetting PLC,... ")
#        dev.write_attribute('PLC_CONFIG_RESET', 1)


class AIRopen(Macro):
    """Open air valve  """

    def run(self):
        for iV in range(1) :
            dev_name = "BL04/ct/eps-plc-01"
            dev = PyTango.DeviceProxy(dev_name)
            sValve = "PAAS_x01_01"
            self.debug(sValve)
            _iv=dev.read_attribute(sValve).value
            self.debug(_iv)
            if _iv != 1 : dev.write_attribute(sValve, 1)
        #self.warning("!!! WARNING, reset FLOW SWITCHES to avoid water valve closing (type _PLCreset ")


class AIRstate(Macro):
    """Status compressed air  """

    param_def = [ ['sIP', Type.String, 'None', 'IPname' ] ]

    def run(self, *args, **kwargs):

        sAtt="PAAS_X01_01_PS1_AF"
        dev_name = "BL04/ct/eps-plc-01"
        dev = PyTango.DeviceProxy(dev_name)
        _iv = dev.read_attribute(sAtt).value
        self.warning("Air flow 1 (%r) %f bar",sAtt,_iv)
        sAtt="PAAS_X01_01_PS2_AF"
        _iv = dev.read_attribute(sAtt).value
        self.warning("Air flow 2 (%r) %f bar",sAtt,_iv)



class WFLOWstate(Macro):
    """State ALL Water Flow switches """

    param_def = [ ['sIP', Type.String, 'None', 'IPname' ] ]

    def run(self, *args, **kwargs):


        loctime = time.strftime("%a %b %d %Y %H:%M:%S",time.localtime())
        self.warning(loctime)

        sAtt="FM_X01_01_AF"
        dev_name = "BL04/ct/eps-plc-01"
        dev = PyTango.DeviceProxy(dev_name)
        _iv = dev.read_attribute(sAtt).value
        self.warning("Main Water flow IN (%r) %f",sAtt,_iv)
        sAtt="FM_X01_02_AF"
        _iv = dev.read_attribute(sAtt).value
        self.warning("Main Water flow OUT (%r) %f",sAtt,_iv)

        for _iv in range(12) :
            _r = self.execMacro("_WFLOWstat",_iv+1).getResult()
      #  self.execMacro("wait %f"%3.)
      #  dev.write_attribute('PLC_CONFIG_RESET', 1)
      #  self.execMacro("wait %f"%3.)
      #  self.execMacro("WFLOWstate")

class _WFLOWstat(Macro):
    """State individual  Water Flow switches """

    param_def = [
       ['sIP', Type.Integer, -99, 'IP name' ]
    ]

    def run(self,sIP):
        if sIP < 1 or sIP > 12 :
            self.warning("Non defined FSW")
            self.warning("FSW name should be ranging from 1 to 12")
            return
        dev_name = "BL04/ct/eps-plc-01"
        dev = PyTango.DeviceProxy(dev_name)
        sAtt="fsw_oh_"+"%.2d"%sIP
        if sIP == 11 : sAtt="fsw_oh_03a"
        if sIP == 12 : sAtt="fsw_oh_06a"
        self.debug(dev_name + "/" + sAtt)
        _iv = dev.read_attribute(sAtt).value
        self.debug(_iv)

        if _iv  : self.error("FSW %s ( %s )  %d OFF "%(FLOWSW[sIP-1],dev_name + "/" + sAtt,sIP))
        else : self.info("FSW %s ( %s )  %d ON "%(FLOWSW[sIP-1],dev_name + "/" + sAtt,sIP))

        return _iv


class IPstate(Macro):
    """Check status of ALL IP controllers  """

    param_def = [ ['sIP', Type.String, 'None', 'IPname' ] ]

    def run(self, *args, **kwargs):
        for _iv in IPNAME :
            #_r = self.execMacro("_IPstat",_iv).getResult()
            _r = self.execMacro("_IPOnOff",_iv).getResult()




class _IPstat(Macro):
    """Check status of individual IP controller (filt/wbat/mir/blv/fs/mono/coll/pshu)  """

    param_def = [
       ['sIP', Type.String, 'None', 'IP name' ]
    ]

    def run(self,sIP):
        if sIP == 'None' :
            self.warning("Non defined IP")
            self.warning("IP name should be in %s",repr(IPNAME))
            return
        if sIP not in IPNAME :
            self.warning("Non defined IP")
            self.warning("FLOW name should be in %s",repr(IPNAME))
            return
        dev_name ="BL04/vc/ip-"+sIP+"-01"
        dev = PyTango.DeviceProxy(dev_name)
        self.debug(dev_name)
        #_aa = dev.read_attribute("Status").value
        #self.output(_aa)
        _iv = dev.read_attribute("State").value
        _iv2 = dev.read_attribute("Pressure").value        
        self.debug(_iv)


        if _iv != PyTango.DevState.ON : self.error("IP controller %-8s is %s, Pressure = %.2e "%(sIP,_iv,_iv2 ))
        else : self.info("IP controller %-8s is %s, Pressure = %.2e "%(sIP,_iv,_iv2 ))

        return _iv,_iv2
        #return _iv

class _IPOnOff(Macro):
    """Check status of IP controller asnd switch On/Off filt/wbat/mir/blv/fs/mono/coll/pshu)  """

    param_def = [
       ['sIP', Type.String, 'None', 'IP name' ],
       ['sVal', Type.String, 'None', 'On/Off' ]
    ]

    def run(self,sIP,sVal):


        if sIP == 'None' :
            self.warning("Non defined IP")
            self.warning("IP name should be in %s",repr(IPNAME))
            return
        if sIP not in IPNAME :
            self.warning("Non defined IP")
            self.warning("IP name should be in %s",repr(IPNAME))
            return

        _iv1= 1+IPNAME.index(sIP)/2
        _iv2= IPNAME.index(sIP)%2+1

        sDev = "BL04/vc/IPCT-0"+"%d"%_iv1
        sAttCh = _iv2
        sOut ="IP %-6s (%s) :"%(sIP,sDev)

        sAtt = "HV"+"%d"%sAttCh+"Status"
        sFull = sDev+"/"+sAtt
        dev = PyTango.DeviceProxy(sDev)
        _a = dev.read_attribute(sAtt).value
        sOut =sOut + "  %s = %s"%(sAtt,_a)
        _aStat = _a

        sAtt = "P"+"%d"%sAttCh
        sFull = sDev+"/"+sAtt
        self.debug(sFull)
        _a = dev.read_attribute(sAtt).value
        sOut =sOut + "  %s = %.2e"%(sAtt,_a)


        sAtt = "I"+"%d"%sAttCh
        sFull = sDev+"/"+sAtt
        _a = dev.read_attribute(sAtt).value
        sOut =sOut + "  %s = %.2e"%(sAtt,_a)

        sAtt = "V"+"%d"%sAttCh
        sFull = sDev+"/"+sAtt
        _a = dev.read_attribute(sAtt).value
        sOut =sOut + "  %s = %d"%(sAtt,_a)

        #if _aStat != PyTango.DevState.ON : self.error(sOut)
        if _aStat != "ON" : self.error(sOut)
        else : self.info(sOut)


        if sVal == 'On' :
            self.info("Switch on IP %s " %sIP)
            if sAttCh == 1 : dev.OnHV1()
            if sAttCh == 2 : dev.OnHV2()
        if sVal == 'Off' :
            self.error("Switch off IP %s " %sIP)
            if sAttCh == 1 : dev.OffHV1()
            if sAttCh == 2 : dev.OffHV2()

        return sOut


class CCGstate(Macro):
    """Check status of ALL CCG controllers  """

    param_def = [ ['sIP', Type.String, 'None', 'IPname' ] ]

    def run(self, *args, **kwargs):
        for _iv in CCGNAME :
            _r = self.execMacro("_CCGstat",_iv).getResult()


class _CCGstat(Macro):
    """Check status of individual CCG controller (filt/wbat/mir/blv/mono/coll/pshu)  """

    param_def = [
       ['sIP', Type.String, 'None', 'Valve number' ]
    ]

    def run(self,sIP):
        if sIP == 'None' :
            self.warning("Non defined CCG")
            self.warning("CCG name should be in %s",repr(CCGNAME))
            return
        if sIP not in CCGNAME :
            self.warning("Non defined CCG")
            self.warning("CCG name should be in %s",repr(CCGNAME))
            return

        sAtt="BL04/vc/ccg-"+sIP+"-01"
        if sIP == 'tru' :
           sAtt="FE04/vc/ccg-"+sIP+"-01"
      #  self.warning(sAtt)
        dev = PyTango.DeviceProxy(sAtt)
        self.debug(sAtt)
        _iv = dev.read_attribute("State").value
   #     _iv2 = dev.read_attribute("Pressure").value
        self.debug(_iv)


        #if _iv != PyTango.DevState.ON : self.error("CCG %-6s ( %-20s ) is %s, Pressure = %.2e "%(sIP,sAtt,_iv,_iv2 ))
        if _iv != PyTango.DevState.ON : 
            _iv2=1e99
            self.error("CCG %-6s ( %-20s ) is %s "%(sIP,sAtt,_iv))
            if sIP == 'mir' : 
               snum='-02'
               sch='P4'
            if sIP == 'mono' : 
               snum='-02'
               sch='P5'
            if sIP == 'filt' : 
               snum='-01'
               sch='P4'
            if sIP == 'wbat' : 
               snum='-01'
               sch='P5'
            if sIP == 'pshu' : 
               snum='-03'
               sch='P4'
            if sIP == 'blvs' : 
               snum='-03'
               sch='P5'

            sAtt="BL04/vc/vgct"+snum
            dev = PyTango.DeviceProxy(sAtt)               
            _iv2 = dev.read_attribute(sch).value
            self.error("--> PIR %-6s ( %-20s )  Pressure = %.2e "%(sIP,sAtt,_iv2 ))
        else : 
            _iv2 = dev.read_attribute("Pressure").value
            self.info("CCG %-6s ( %-20s ) is %s, Pressure = %.2e "%(sIP,sAtt,_iv,_iv2 ))

        return _iv,_iv2
        #return _iv

class TEMPstate(Macro):
    """Check status of ALL critical temperatures  """

    param_def = [ ['sIP', Type.String, 'None', 'IPname' ] ]

    def run(self, *args, **kwargs):
        loctime = time.strftime("%a %b %d %Y %H:%M:%S",time.localtime())
        self.warning(loctime)

        for _iv in TEMPNAME :
            self.output("Temperatures on %s"%_iv )
            _r = self.execMacro("_TEMPstat",_iv).getResult()


class _TEMPstat(Macro):
    """Check status of individual temperture (filt/vwin/wbat8front/wbat/mir/mma/mono)  """

    param_def = [
       ['sIP', Type.String, 'None', 'Valve number' ]
    ]

    def run(self,sIP):
        if sIP == 'None' :
            self.warning("Non defined Temperture group")
            self.warning("TEMP name should be in %s",repr(TEMPNAME))
            return
        if sIP not in TEMPNAME :
            self.warning("Non defined Temperature group")
            self.warning("TEMP name should be in %s",repr(TEMPNAME))
            return

        sAtt="BL04/ct/eps-plc-01"
        #self.warning(sAtt)
        if sIP == 'mono' :
           MONOsT=['01','12','02','09','10','08','03','11','15','16']
           sch0=sIP+"_OH01_01_PT"
        if sIP == 'mir' :
           MONOsT=['01','02','03','04','05','06']
           sch0=sIP+"_OH01_01_PT"
        if sIP == 'mma' :
           MONOsT=['TC1','TC2','TC3','TC4']
           sIP0='movm'
           sch0=sIP0+"_OH01_01_"
        if sIP == 'filt' :
           MONOsT=['TC1','TC2','TC3']
           sch0=sIP+"_OH01_"
        if sIP == 'vwin' :
           MONOsT=['TC1','TC2']
           sch0=sIP+"_OH01_"
        if sIP == 'wbat' :
           MONOsT=['TC1','TC2','TC3','TC4','TC5','TC6','TC7','TC8','TC9','TC10','TC11','TC12','TM1','TM2']
           sch0=sIP+"_OH01_"

        for snum in MONOsT :  
             idx=int(MONOsT.index(snum)/4)
             sch=sch0+snum
             if sIP == 'wbat' : sch=sch0+"0%i_"%(idx+1)+snum
             if MONOsT.index(snum) > 11 :  sch=sch0+snum

             #schStatus=sch+'_STATUS'
             #_iv = dev.read_attribute(schStatus).value
             #self.warning(_iv)

             dev = PyTango.DeviceProxy(sAtt)               
            # schAtt=dev.get_attribute_config(sch)    -> full info (array like)
             schLabel=dev.get_attribute_config(sch).label  
             schMin=float(dev.get_attribute_config(sch).min_alarm) 
             schMax=float(dev.get_attribute_config(sch).max_alarm) 
             schUnit=dev.get_attribute_config(sch).unit 
           # self.warning(schLabel)

             _iv2 = dev.read_attribute(sch).value
             if (_iv2 > schMin and _iv2 < schMax) :
               self.info("TEMP %-6s ( %-20s/ %s ) %s  = %.2f %s"%(sIP,sAtt,sch,schLabel,_iv2,schUnit ))
             else :
               self.error("TEMP %-6s ( %-20s/ %s ) %s  = %.2f %s"%(sIP,sAtt,sch,schLabel,_iv2,schUnit ))
	
        return _iv2
        #return _iv


class feauto(Macro):
    """This macro enables or disables the Front End Automatic opening mode"""

    param_def = [
       ['state', Type.String, '', '1/0 Yes/No' ]
    ]

    def run(self, state):
        dev_name, attr = FEAUTO_ATTR.rsplit("/", 1)
        dev = PyTango.DeviceProxy(dev_name)
        if state == '':
            self.output("FE Automatic mode is %d." % dev.read_attribute(attr).value)
        elif state == '1' or state.upper() == "YES":
            dev.write_attribute(attr, 1)
            # FF cnacel the line since it takes 3 sec to refresh
            # self.output("FE Automatic mode is  set to  %d." % dev.read_attribute(attr).value)
            self.output("FE Automatic mode is  set to  ON" )
        elif state == '0' or state.upper() == "NO":
            dev.write_attribute(attr, 0)
            self.output("FE Automatic mode is set to OFF")
        else:
            self.error("Error. FE state not valid.")
            self.output("FE Automatic mode is %d." % dev.read_attribute(attr).value)

class fepss(Macro):
    """This macro checks the permits of the PSS from the Machine to open the FE"""

    def run(self):
        dev_name, attr = FE_PSS_PERMIT.rsplit("/", 1)
        dev = PyTango.DeviceProxy(dev_name)
        self.output("FE PERMIT FROM THE PSS is %d" % dev.read_attribute(attr).value)


class fectrl(Macro):
    """This macro checks if the control of the FE is disabled"""

    def run(self):
        dev_name, attr = FE_CTRL_DISABLE.rsplit("/", 1)
        dev = PyTango.DeviceProxy(dev_name)
        self.output("FE CONTROL is %d" % dev.read_attribute(attr).value)


class festatus(Macro):
    """This macro checks if FE status"""

    def run(self):
        dev_name, attr = FE_CTRL_DISABLE.rsplit("/", 1)
        dev = PyTango.DeviceProxy(dev_name)
        _str="FE CONTROL"
        if dev.read_attribute(attr).value  == 1 : self.info("%s is %d -> OK" %(_str,dev.read_attribute(attr).value))
        else : self.error("%s is %d" %(_str,dev.read_attribute(attr).value))
        
        dev_name, attr = FE_PSS_PERMIT.rsplit("/", 1)
        dev = PyTango.DeviceProxy(dev_name)
        _str="FE PERMIT FROM THE PSS"
        if dev.read_attribute(attr).value  == 1 : self.info("%s is %d -> OK" %(_str,dev.read_attribute(attr).value))
        else : self.error("%s is %d" %(_str,dev.read_attribute(attr).value))

        dev_name, attr = FE_BL_READY.rsplit("/", 1)
        dev = PyTango.DeviceProxy(dev_name)
        _str="BL READY"
        if dev.read_attribute(attr).value  == 1 : self.info("%s is %d -> OK" %(_str,dev.read_attribute(attr).value))
        else : self.error("%s is %d" %(_str,dev.read_attribute(attr).value))

        fe_device = PyTango.DeviceProxy('bl04/ct/eps-plc-01')
        fe_status = fe_device.read_attribute('FE04_SHUTTER').value
        if fe_status == 0 :  self.error("FE is closed")
        if fe_status == 1 :  self.info("FE is open")


class feopen(Macro):
    """Open Front end"""

    def prepare(self):
        dev_name, attr = FE_CTRL_DISABLE.rsplit("/", 1)
        dev = PyTango.DeviceProxy(dev_name)
        _attrVal = dev.read_attribute(attr).value
        if _attrVal  == 1. :
            raise Exception("FE can not be open, FE_ctrl_disable is %d \nYou do not have the control of the FE (likely the machine disabled it) " %_attrVal)

        dev_name, attr = FE_BL_READY.rsplit("/", 1)
        dev = PyTango.DeviceProxy(dev_name)
        _attrVal = dev.read_attribute(attr).value
        if _attrVal  != 1. :
            raise Exception("FE can not be open, FE_BL_READY is %d \nCheck Optics hutch is searched  and/or valves are open" %_attrVal)

    def run(self):
        fe_device = PyTango.DeviceProxy('bl04/ct/eps-plc-01')
        fe_device.write_attribute('open_fe', 1)
        #fe_device.write_attribute('FE04_SHUTTER',1)
        self.info("Opening FE...")
        fe_status = fe_device.read_attribute('FE04_SHUTTER').value
        _n=0
        while fe_status != 1 :
            self.output("....FE state is %d so wait 2 sec..." %fe_status)
            time.sleep(2)
            fe_status = fe_device.read_attribute('fe_open').value
            #fe_status = fe_device.read_attribute('FE04_SHUTTER').value
            _n += 1
            if _n > 5  : fe_device.write_attribute('open_fe', 1)
            if _n > 10 : raise Exception("!!! WARNING, FE could not be open after 20 sec attempt, so give up")
        self.info("FE open now...")


class feclose(Macro):
    """Close Front end"""


    def run(self):
        fe_device = PyTango.DeviceProxy('bl04/ct/eps-plc-01')
        fe_device.write_attribute('close_fe', 1)
        #fe_device.write_attribute('FE04_SHUTTER',0)
        self.info("Closing FE...")
        fe_status = fe_device.read_attribute('fe_open').value
        #fe_status = fe_device.read_attribute('FE04_SHUTTER').value
        _n=0
        while fe_status != 0 :
            self.output("....FE state is %d so wait 2 sec..." %fe_status)
            time.sleep(2)
            fe_status = fe_device.read_attribute('fe_open').value
            #fe_status = fe_device.read_attribute('FE04_SHUTTER').value
            _n += 1
            if _n > 5  : fe_device.write_attribute('close_fe', 1)
            if _n > 10 : raise Exception("!!! WARNING, FE could not be closed after 20 sec attempt, so give up")
        self.info("FE close now...")
        self.error("\n!!! WARNING Closing the FE stop the FE automatice mode. Type feauto 1 after feopen to re-enable it\n" )


class festate(Macro):
    """Front end  state"""

    def run(self):
        fe_device = PyTango.DeviceProxy('fe')
        fe_status = fe_device.read_attribute('value').value
        if fe_status == 0 :  self.info("FE is closed")
        if fe_status == 1 :  self.info("FE is open")


class shopen(Macro):
    """Open EH Shutter"""

    def run(self):
       # 06Sep2017 FF commented teh method since problem with register
       # sh_device = PyTango.DeviceProxy('sh')
       # sh_device.write_attribute('value', 1)
        dev = PyTango.DeviceProxy('bl04/ct/eps-plc-01')
        dev.write_attribute('pshu_OH01',1)
        
        self.info("Opening SH...")
       # sh_status = sh_device.read_attribute('value').value
        sh_status = dev.read_attribute('pshu_OH01').value
        itim=2
        while sh_status != 1 :
            self.output("....SH state is %d so wait %d sec..." %(sh_status,itim))
            time.sleep(itim)
        #    sh_status = sh_device.read_attribute('value').value
            sh_status = dev.read_attribute('pshu_OH01').value
        self.info("SH open now...")


class shclose(Macro):
    """Close EH shutter"""

    def run(self):
        #sh_device = PyTango.DeviceProxy('sh')
        #sh_device.write_attribute('value', 0)
        PyTango.DeviceProxy('bl04/ct/eps-plc-01').write_attribute('pshu_OH01',0)
        self.info("Closing SH...")
  #      sh_status = sh_device.read_attribute('value').value
  #      while sh_status != 0 :
  #          self.output("....SH state is %d so wait 2 sec..." %sh_status)
  #          time.sleep(2)
  #          sh_status = sh_device.read_attribute('value').value
  #      self.info("SH closed now...")

class shstate(Macro):
    """EH shutter state"""

    def run(self):
        sh_device = PyTango.DeviceProxy('sh')
        sh_status = sh_device.read_attribute('value').value
        if sh_status == 0 :  self.info("SH is closed")
        if sh_status == 1 :  self.info("SH is open")
