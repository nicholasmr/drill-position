from PyQt4.QtGui import *
from PyQt4.QtCore import *
import numpy as np
import code # code.interact(local=dict(globals(), **locals())) 
import sys, signal, time, redis, socket, json, datetime
signal.signal(signal.SIGINT, signal.SIG_DFL)
hostname = socket.gethostname()

if len(sys.argv) < 3: sys.exit('usage: %s mode dt'%(sys.argv[0]))
mode = str(sys.argv[1])
dt = float(sys.argv[2]); #print "*** dt=%.2f"%(dt)
t = 0

#--------------------------
# Mode
#--------------------------
READONLY         = (mode=='read')  # Remote viewer mode
INFOMODE         = (mode=='info')  # read mode + large fonts for info screen

# Write
SETUPREDIS       = (mode=='setup') # Setup REDIS fields
WRITEMODE        = (mode=='write') # Drillers mode

# Local
SETUPREDIS_LOCAL = (mode=='setuplocal') 
DEBUG            = (mode=='debug') # Debug without redis
NOREDIS          = DEBUG


SET_VALS_TO_WARN = DEBUG

#--------------

#IS_HOST_THE_CONTROLLER = (hostname == 'raspberrypi') # This is the hostname of the drill control computer! Will make the redis server the local host
if      DEBUG: host='localhost'
#else:          host='10.2.3.10'
else:          host='drill.egrip.camp'

if SETUPREDIS_LOCAL:
        SETUPREDIS = 1
        host       = 'localhost'

#-------------------------

def redisConnect():

        tstep = 30
        if not NOREDIS:

                print "*** this host is %s, using redis server at %s"%(hostname, host)

                noconnect = True
                while noconnect:
                        rs = redis.StrictRedis(host=host)
                        noconnect = False
                        try: rs.ping()
                        except redis.ConnectionError:
                            print "*** Redis connection failed to %s. Re-attempting in %i secs"%(host, tstep)
                            noconnect = True
                            time.sleep(tstep);
                return rs
        else: return -1;

#--------------------------

r = redisConnect()

if SETUPREDIS:
        print "Setting redis defaults"
        r.delete('dmsg-l');          r.set('dmsg-l',100)
        r.delete('dmsh-lliq');       r.set('dmsg-lliq',91)
        r.delete('dmsg-tare-load');  r.set('dmsg-tare-load', 0)
        r.delete('dmsg-tare-motorI');r.set('dmsg-tare-motorI', 0)

#--------------------------
# Warning vals
#--------------------------

warn_load     = 1100  # kg
warn_hammer   = 40.   # native value (640 is max)
warn_sliprate = 1     # 1 rpm
warn_motorI   = 11    # I
warn_vdrill   = 1.3e2 # cm/s
warn_temp     = 65 # deg C

max_hammer = 630

load       = 0;
motorRPM   = 0; 
motorI     = 0; 
motorU     = 0;
hammer     = 0;
sliprate   = 0;
temp1      = 0;
temp2      = 0;
incl       = 0;
azi        = 0;
lliq       = 77
l          = 900
ldrill     = 900+0.5
#ldrill     = l
vdrill     = 0
tareload   = 0
taremotorI = 0

tareref = 0;

#--------------------------
# Drill geom
#--------------------------

#DRILL_SIZE = 'short'
DRILL_SIZE = 'long'

if DRILL_SIZE == 'short':
        drilllen   = 7
        cbarrellen = 2 # length of drilllen which is the core barrel
if DRILL_SIZE == 'long':
        drilllen   = 11 + 0.5 # 0.5 is the length of dead weight
        cbarrellen = 3.5

hammerlen   = (drilllen-cbarrellen)*0.25
motorseclen = hammerlen

cabeldensity = 0.2 # kg/m

#--------------------------
# Depth and casing         
#--------------------------
 
#widths = np.multiply([2.55, 2.22, 1.85, 1.35, 1.29], 1)
widths = np.multiply([2.55, 2.22, 1.85, 1.29, 1.29], 1) # Above is the real one, but this is practial because of "lliq" is sometimes in the casing, making thick lines when drawing casing.
L      = 2.7 * 1e3 
depths = np.multiply([0,      59,   62,   66,   98, L], 1)

#--------------------------
# Fonts
#--------------------------

COLOR_WARN_RGB = [240,59,32]
COLOR_WARN_HEX = '#F03B20'
COLOR_OBS_RGB  = [255,237,160]
COLOR_OBS_HEX  = '#FFEDA0'
COLOR_BLUE_RGB = [158,202,225] 
COLOR_BLUE_HEX = '#9ECAE1'
COLOR_OK_RGB   = [26,152,80]   
COLOR_OK_HEX   = '#1A9850'

#if INFOMODE: FontSize0 = 21
FontSize0 = 14
dFont = 4

fontname = 'Helvetica'
font = QFont(fontname); 
#font.setBold(True)
font.setPointSizeF(FontSize0+dFont);

fontb = QFont(fontname); 
fontb.setBold(True)
fontb.setPointSizeF(FontSize0+dFont);

fontsmaller = QFont(fontname); 
fontsmaller.setPointSizeF(FontSize0+dFont-3)

fonttitle = QFont(fontname); 
fonttitle.setBold(True)
fonttitle.setPointSizeF(FontSize0+8); 

#--------------------------
# Redis calls
#--------------------------

def testRedisConn(r):
        if not NOREDIS:
                try: r.ping()
                except redis.ConnectionError: r = redisConnect()

def setDrillersMsgs(msg):     
        print "Saving drillers messages"
        r.set('dmsg-drillersmsg',  msg)
        
def getDrillersMsgs():
        if not NOREDIS: return r.get('dmsg-drillersmsg')
        else:           return 'IN DEBUG MODE'
        
def setNewZero(newzero):
        global l
        print 'Setting new zero l = ldrill = %f (prev %f)'%(newzero,l)
        l = newzero
        if not NOREDIS: r.set('dmsg-l', l)
        return l
        
def setNewTareref(newtareref):
        global tareref, tare_hist
        print 'Setting tareref = load = %f (prev %f)'%(newtareref,tareref)
        tareref = newtareref
#        tare_hist = np.full(len(tare_hist),np.nan)
        if not NOREDIS: r.set('dmsg-tareref', newtareref)
        return tareref

def getDepth(t):
        global  ldrill
        if not DEBUG:    return -1*float(json.loads(r.get('depth-encoder'))['depth'])
#        else:            return ldrill
#        else:            return 29+76 + 1*t + .02*t**2#+ np.sin(t)
        else:            return ldrill + 3* np.sin(t)

def getVel(t):
        if not DEBUG:    return (json.loads(r.get('depth-encoder'))['velocity'])
        else:            return 0

def getLoad(t):
        if not DEBUG:    return json.loads(r.get('load-cell'))['load']
        else:            return warn_load
#        else:            return 300 + 10*np.cos(t)+5*np.sin(3*t)

def getTareref():
        global tareref
        if not NOREDIS: return float(r.get('dmsg-tare-load'))
        else:           return tareref

def getZero(t):
        global l
        if not NOREDIS: return float(r.get('dmsg-l'))
        else:           return l
#        else:           return 110+0.5*np.sin(t)
       
def getHeadLoad(load,ldrill):
        return load-cabeldensity*(ldrill-drilllen)

def getMotor(t):
        if not NOREDIS:
                motorRPM = json.loads(r.get('drill-state-motor'))['rpm'];        
                motorI   = json.loads(r.get('drill-state-motor'))['current'];        
                motorU   = json.loads(r.get('drill-state-motor'))['voltage'];        
                return (motorRPM,motorI,motorU)
        else:
                return (0,0,0)
               
def getHammer(t):
        if not NOREDIS:
                return json.loads(r.get('drill-state-hammer'))['position']
        else:        
                return 0                

def getGyroSlipRate(t):
        gyrox = 0
        if not NOREDIS: gyrox = float(json.loads(r.get('drill-state-orientation'))['gyroscope']['x'])
#        RPM_per_gyrox = 0.1450
        RPM_per_gyrox = 0.15
        return gyrox * RPM_per_gyrox        

def getTemperatures(t):
        if not NOREDIS:
#                code.interact(local=dict(globals(), **locals())) 
                temps = json.loads(r.get('drill-state-temperature'))
                k = temps.keys()
                temp1 = np.round(float(temps[k[0]]))
#                temp2 = np.round(float(temps[k[1]]))
                temp2 = np.nan
                return (temp1,temp2)
        else:
                return (0,0)
        

def getOrientation(t):

        if not NOREDIS:
#                orien = json.loads(r.get('dmsg-calorientation'))
                return (-10,-10)
        else:
                return (0,0)


#-----------------------

def getMaxGeom():
#        geom_screen = QDesktopWidget().screenGeometry()
        geom_avail  = QDesktopWidget().availableGeometry() # ex [0, 28, 1920, 1028], "28" ypixels reserved for top/bottom window manager bars
#        code.interact(local=locals())
#        geom_xy     = [geom_avail.width()-geom_avail.x(), geom_avail.height()-geom_avail.y()]
        geom_xy     = [geom_avail.width(), geom_avail.height()]
        return geom_xy
        
def mylistroller(thelist, newval):
        thelist[:-1] = thelist[1:]; 
        thelist[-1]  = newval                
        return thelist     

def htmlfont(text,fsize, color='#000000'): return '<font size="%i" color="%s">%s</font>'%(fsize,color,text)
       
def shoot():
        p = QPixmap.grabWindow(w.winId())
        p.save('bhprogress.jpg', 'jpg')

