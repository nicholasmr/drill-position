#!/usr/bin/python
# -*- coding: utf-8 -*-
from header import *
from PyQt4 import QtCore
import numpy as np
import code # code.interact(local=locals())
import time

#-----------------------
# INIT
#-----------------------

if dt==0:  vdrill_hist = np.full(120,1e-10)
else:      vdrill_hist = np.full(50,1e-10)
ETA         = np.inf

#----------------------
# QT FUNCTIONS
#----------------------

qstr_deg = QtCore.QString(u"\u00B0")

penCase   = QPen(Qt.black, 9, Qt.SolidLine)
penHole   = QPen(Qt.black, 3, Qt.SolidLine)
penThn    = QPen(Qt.black, 3, Qt.SolidLine)

COLOR_WARN     = QColor(COLOR_WARN_RGB[0],COLOR_WARN_RGB[1],COLOR_WARN_RGB[2])
COLOR_BLUE_RGB = QColor(COLOR_BLUE_RGB[0],COLOR_BLUE_RGB[1],COLOR_BLUE_RGB[2])
COLOR_OK       = QColor(COLOR_OK_RGB[0],COLOR_OK_RGB[1],COLOR_OK_RGB[2])
##penWarn   = QPen(COLOR_WARN, 15, Qt.SolidLine)
penWarn   = QPen(Qt.white, 12, Qt.SolidLine)
penWarnred= QPen(COLOR_WARN, 12, Qt.SolidLine)
penReg    = QPen(Qt.black,3, Qt.SolidLine)
penThick  = QPen(Qt.black,6, Qt.SolidLine)
penThickCable = QPen(QColor(191,129,45),6, Qt.SolidLine)
#penTarget = QPen(QColor(33,113,181), 5, Qt.SolidLine);

penReg.setMiterLimit(100)
penReg.setJoinStyle(Qt.BevelJoin)

brush_liq             = QBrush(QColor(217,217,217),Qt.SolidPattern)
brush_undrilled       = QBrush(QColor(255,255,255),Qt.SolidPattern)
brush_drillbody       = QBrush(QColor(115,115,115),Qt.SolidPattern);
brush_drillbarreldiag = QBrush(QColor(0,0,0),Qt.BDiagPattern);  

BRUSH_WARN = QBrush(COLOR_WARN,Qt.SolidPattern);

COLOR_RPM_LVLS = [0.01]
COLOR_RPM      = [[189,189,189],[255,237,160]]
BRUSH_RPM      = [QBrush(QColor(c[0],c[1],c[2]),Qt.SolidPattern) for c in COLOR_RPM]

COLOR_HAMMER_LVLS = [warn_hammer]
COLOR_HAMMER      = [[189,189,189],  COLOR_WARN_RGB]
BRUSH_HAMMER      = [QBrush(QColor(c[0],c[1],c[2]),Qt.SolidPattern) for c in COLOR_HAMMER]
BRUSH_HAMMER_PAT  = QBrush(QColor(0,0,0),Qt.HorPattern)

def getColorGivenValue(val, lvls, colors):
#        print val,lvls,np.arange(len(lvls)),np.flip(np.arange(len(lvls)),0)
        for ii in np.flipud(np.arange(len(lvls))):
#                print val, lvls[ii], ii
                if val > lvls[ii]: return colors[ii+1]
        return colors[0] 

def LRwall(x0,w): return (x0-w/2,x0+w/2)

if DRILL_SIZE == 'short': dmul = 100
#if DRILL_SIZE == 'long': dmul = 30 #debug
if DRILL_SIZE == 'long': dmul = 63
wmul = 30*3.9
x0=300-85
#if INFOMODE: x0 = 370
mywidths      = np.multiply(widths, wmul)
mydepths      = np.multiply([0,      59,   62,   66,   98, L], dmul)
mytowerlen    = dmul*80
mydrilllen    = dmul*drilllen
mycbarrellen  = dmul*cbarrellen # length of drilllen which is the core barrel
myhammerlen   = dmul*hammerlen
mymotorseclen = dmul*motorseclen

def drawBoreHole(qp, OVERVIEW):

        global l,lliq,ldrill,load,hammer,sliprate,motorRPM,motorI,motorU,motorflash, temp1,temp2, incl,azi,  vdrill_hist,vdrill,ETA

#        flashon = np.mod(np.round(t),2)
        flashon = True

        # Measures        
        mylliq       = dmul*lliq
        myl          = dmul*l
        myldrill     = dmul*ldrill

        w        = mywidths[-2]
        extend   = 1.3*drilllen # extent to which we draw the portion of the QT image not seen (outside window). This should be adjusted according to the zoom-in scale "dmul"
        myextend = dmul*extend
        # x0 = center (vertical) line through drill
        dxdrill = w/3
        dwdrill = 2*dxdrill
        x0l = x0-dxdrill # left side of drill
        x0r = x0+dxdrill # right side of drill


        # Vertical offsets
        if OVERVIEW: y0 = 80.
        else:        y0 = -(myldrill-1.15*mydrilllen)
        Y0 = y0 
        y0drill = Y0+myldrill

        # Depth ticks
        if OVERVIEW:  del_d = 200 # metres
        else:         del_d = 1
        dx = 20 # pixels
        tickslist = np.arange(np.max([0,np.round(ldrill-extend)]), np.min([L,np.round(ldrill+extend)]), del_d)
        for d in tickslist:
                dref=dmul*d
                di = 0
                for di in np.arange(len(depths)-2):
                        if (d>=depths[di]) and (d<=depths[di+1]): break
                        else: di=di+1
                        
                wi = mywidths[di]
                recty = 40
                rectx = 120
                wl,wr = LRwall(x0,wi)
                rect = QRect(wr+dx, Y0+dref-recty/2,  rectx, recty)
                if np.mod(d,2*del_d)==0:
                        qp.drawText(rect, Qt.AlignLeft, '%1.0fm'%(d))   
                qp.drawLine(wr+dx-6, Y0+dref,  wr+6, Y0+dref)

        # level labels for l, lliq, delta l, etc.
        rectx = 250
        x0lbl = wl-dx-rectx*0.95
        recty = 80 
        wl,wr = LRwall(x0,w)
        rect_lliq = QRect(x0lbl, Y0+mylliq-0.5*recty/2,  rectx, recty)
        rect_l    = QRect(x0lbl, Y0+myl   -0.5*recty/2,  rectx, recty)
#        qp.drawText(rect_lliq,  Qt.AlignRight, 'll=%.1fm '%(lliq))   
#        qp.drawLine(wl-6, Y0+mylliq,  wl-dx+6, Y0+mylliq)
        qp.drawText(rect_l,     Qt.AlignRight, '%.2fm '%(l))   
        qp.drawLine(wl-6, Y0+myl   ,  wl-dx+6, Y0+myl   )

        if ldrill>l:
                rextx_l = rectx*1.2
                rect_lnew = QRect(wl-dx-rextx_l, Y0+max(myl+recty*0.4,myldrill-0.5*recty/2),  rextx_l, recty)
                isNearEnd = (ldrill-l)>=0.95*cbarrellen
#                if isNearEnd: qp.setPen(penWarnred)
                qp.drawText(rect_lnew,  Qt.AlignRight, 'L=%3.0fcm'%((ldrill-l)*1e2) )   
                if isNearEnd: qp.setPen(penHole)
                qp.drawLine(wl-6, y0drill,  wl-dx+6, y0drill)
        elif l-ldrill<10:
#        elif l-ldrill>cbarrellen/3 and ldrill>depths[-3]+1:


                rect = QRect(x0lbl, y0drill-0.5*recty/2,  rectx, recty)
                qp.drawText(rect,  Qt.AlignRight, '%.2fm '%(ldrill))   
                qp.drawLine(wl-6, y0drill,  wl-dx+6, y0drill)

        # Color drill, liquid, undrilled
#        qp.setBrush(brush_liq)
#        yliq0=myldrill-myextend
#        if mylliq>yliq0: yliq0=mylliq
#        if myl<myldrill+myextend:    dyliq=myl-yliq0
#        else:                      dyliq=myextend
#        qp.drawRect(x0-w/2,Y0+yliq0, w,dyliq)

        qp.setBrush(brush_undrilled)      
        qp.drawRect(x0-w/2,Y0+myl, w,myextend)      

        # Draw hole + casing
        mydepths[-1] = np.max([mydepths[-2],myldrill+myextend])
        N = len(mywidths)
        for ii in np.arange(N):
                if ii<N-1: qp.setPen(penCase)
                else:      qp.setPen(penHole)
                D = mydepths[ii+1]-mydepths[ii]
                y0 = y0+D
                W = mywidths[ii]
                wl,wr = LRwall(x0,W)
                qp.drawLine(wl, y0-D, wl, y0)    
                qp.drawLine(wr, y0-D, wr, y0) 
                if ii<len(mywidths)-1:
                        Wnext = mywidths[ii+1]
                        wlnext,wrnext = LRwall(x0,Wnext)
                        qp.drawLine(wl, y0, wlnext, y0)
                        qp.drawLine(wr, y0, wrnext, y0)

        #-------------------
        # The drill 
        #-------------------

        # -- body
        qp.setPen(penThick); 
        if load>warn_load and flashon and not INFOMODE: qp.setPen(penWarnred); 
        qp.drawLine(x0, Y0-mytowerlen,  x0, y0drill-mydrilllen)
        qp.setPen(penReg)

        qp.setBrush(brush_drillbody)
        qp.drawRect(x0l, y0drill,  dwdrill, -mydrilllen)
        
        # -- skates
        qp.setBrush(BRUSH_HAMMER[0]) 
        if abs(sliprate)>warn_sliprate and flashon and not INFOMODE:  qp.setBrush(BRUSH_WARN)
	qp.drawRect(x0l-w*0.12, y0drill-mydrilllen,  dwdrill+2*w*0.12, +myhammerlen)

        # -- hammer
        qp.setBrush(BRUSH_HAMMER[0])
        if (hammer>warn_hammer) and flashon and not INFOMODE: qp.setBrush(getColorGivenValue(hammer, COLOR_HAMMER_LVLS, BRUSH_HAMMER))  
        qp.drawRect(x0l, y0drill-mydrilllen,  dwdrill, +myhammerlen)

        # -- motor section
        qp.setBrush(BRUSH_HAMMER[0])
        if (temp1>warn_temp or temp2>warn_temp) and flashon and not INFOMODE:  qp.setBrush(BRUSH_WARN)
        qp.drawRect(x0l, y0drill-mydrilllen+myhammerlen,  dwdrill, +myhammerlen)
                

        # -- corebarrel
#        if WRITEMODE:
#                qp.setBrush(BRUSH_RPM[0])
#        else: # INFOMODE
#                qp.setBrush(BRUSH_RPM[0])
#                if (motorRPM>0) and flashon: qp.setBrush(getColorGivenValue(motorRPM, COLOR_RPM_LVLS, BRUSH_RPM))

        qp.setBrush(BRUSH_RPM[0])
        if (motorRPM>0) and flashon: qp.setBrush(getColorGivenValue(motorRPM, COLOR_RPM_LVLS, BRUSH_RPM))

        if motorI>warn_motorI and flashon and not INFOMODE: qp.setBrush(BRUSH_WARN) # Override "on" blink if warning (red)
        qp.drawRect(x0l, y0drill,  dwdrill, -mycbarrellen)
        qp.setBrush(brush_drillbarreldiag)
        qp.drawRect(x0l, y0drill,  dwdrill, -mycbarrellen)

        #----------------
        # Labels
        #----------------

        dx=0.1*dxdrill; # x padding of text box
        x0txt = x0l+dx
	dy=40 # height of text box

        if SET_VALS_TO_WARN: ETA=-100
        isETA = (ETA is not np.inf) and abs(ETA)<60*3
        if isETA: 
                isOnWayDown = ETA<0
                if isOnWayDown: ETA = abs(ETA)
                if isOnWayDown and INFOMODE: ETA = np.inf
                eta = ETA
                qp.setFont(fonttitle);
                y0ETA = y0drill+mycbarrellen*0.15
                w_ = dxdrill*2.6
                c = COLOR_BLUE_RGB
                #if isOnWayDown: c = QColor(158,202,225)
                #else:           c = QColor(178,223,138)
                qp.setBrush(c); qp.drawRect(QRect(0, 0, w_,dy*2.1))
                dw_ = 0.04*w_
                r = QRect(dw_, 0,    w_,dy);  qp.drawText(r, Qt.AlignLeft, 'ETA')   
                r = QRect(dw_, 0+dy, w_,dy);  qp.drawText(r, Qt.AlignLeft, '%i min'%(eta) )      
                qp.setFont(font);

        # vel
        x0vel = x0l
        y0vel = y0drill+mycbarrellen*0.1
        if abs(vdrill)>warn_vdrill and flashon and not INFOMODE: qp.setPen(penWarnred); qp.setFont(fontb);
        else:                                                    qp.setPen(penReg);qp.setFont(fontb);
        v = '%.0f'%(vdrill)
        if abs(vdrill)<3.0: v = '%.1f'%(vdrill)
        r = QRect(x0vel,y0vel,          dwdrill,dy); qp.drawText(r, Qt.AlignRight, v)   
        r = QRect(x0vel,y0vel+dy*0.6,   dwdrill,dy); qp.drawText(r, Qt.AlignRight, 'cm/s')   
        qp.setFont(font); 

        # orientation
        y0drill-mydrilllen
        qp.setPen(penReg); qp.setFont(fontb);
        qstr_theta = QtCore.QString(u"\u03B8")
        qstr_phi   = QtCore.QString(u"\u03C6")
        if incl>-10: # debug, don't show if get() function not implemented
                r = QRect(x0txt, y0drill-mydrilllen/2, w/2,dy);     qp.drawText(r, Qt.AlignCenter, '%.1f%s'%(incl,qstr_deg))   
        #r = QRect(x0txt, y0drill-mydrilllen/2, w,dy);     qp.drawText(r, Qt.AlignLeft, '%s = %.1f%s'%(qstr_theta,incl,qstr_deg))   
        #r = QRect(x0txt, y0drill-mydrilllen/2+dy, w,dy);  qp.drawText(r, Qt.AlignLeft, '%s = %03i%s'%(qstr_phi,azi,qstr_deg))   

        if not INFOMODE:
#        if True: # Show all info for drill

                # cabel load
                ymidload = y0drill-mydrilllen*1.12
                if load>warn_load and flashon: qp.setPen(penWarnred); qp.setFont(fontb);
                else:                          qp.setPen(penReg); qp.setFont(fontb);
                r = QRect(x0-w/2*1.08, ymidload,        w/2,dy);  qp.drawText(r, Qt.AlignRight, '%.0f'%(load))   
                r = QRect(x0-w/2*1.08, ymidload+dy*0.6, w/2,dy);  qp.drawText(r, Qt.AlignRight, 'kg')   
                qp.setFont(font)

                # hammer
                ymidhammer = y0drill-mydrilllen - 0.02*myhammerlen
                hammerflash = hammer>warn_hammer and flashon
                if hammerflash: 
                        qp.setPen(penWarn); qp.setFont(fontb);
                        r = QRect(x0txt-dx/2, ymidhammer,        dwdrill,dy); qp.drawText(r, Qt.AlignCenter, 'Ham.')        
                        r = QRect(x0txt-dx/2, ymidhammer+dy*0.6, dwdrill,dy); qp.drawText(r, Qt.AlignCenter, '%i%%'%(float(hammer)/max_hammer*100))        
                qp.setFont(font)

                # skates
                ymidskates = y0drill-mydrilllen + 0.45*myhammerlen
                if abs(sliprate)>warn_sliprate and flashon:
                        if hammerflash: qp.setPen(penWarn); 
                        else:           qp.setPen(penWarnred); 
                        qp.setFont(fontb);
                        r = QRect(x0txt-dx, ymidskates, dwdrill,dy); qp.drawText(r, Qt.AlignCenter, 'Slip')      
                        r = QRect(x0txt-dx, ymidskates+0.65*dy, dwdrill,dy); qp.drawText(r, Qt.AlignCenter, '%iRPM'%(sliprate))      
                qp.setFont(font)

                # motor section
#                if motorRPM > 1.0:
		if True:

                        ymidmotorsec = y0drill-mydrilllen+myhammerlen + mymotorseclen/2
                        dy_ = 0.8*dy

                        qp.setPen(penReg); qp.setFont(fontb);
                        if temp1>warn_temp and flashon: qp.setPen(penWarn); qp.setFont(fontb); 
                        r = QRect(x0txt+dx, ymidmotorsec-0*dy_, dwdrill,dy_); qp.drawText(r, Qt.AlignLeft, '%i%sC'%(temp1,qstr_deg))   
                        qp.setFont(font)

                        qp.setPen(penReg); qp.setFont(fontb);
                        if temp2>warn_temp and flashon: qp.setPen(penWarn); qp.setFont(fontb); 
                        if temp2 is not np.nan:
                                r = QRect(x0txt+dx, ymidmotorsec-1*dy_, dwdrill,dy_); qp.drawText(r, Qt.AlignLeft, '%i%sC'%(temp2,qstr_deg))   
                        qp.setFont(font)

                # barrel/motor
                if motorRPM > 1.0:

                        ymidbarrel = y0drill-mycbarrellen/2
                        dy_ = 0.8*dy

                        qp.setPen(penReg); qp.setFont(fontb);
                        r = QRect(x0txt, ymidbarrel+1*dy_, dwdrill,dy_); qp.drawText(r, Qt.AlignLeft, '%.0fRPM'%(motorRPM))   

                        qp.setPen(penReg); qp.setFont(fontb);
                        if motorI>warn_motorI and flashon: qp.setPen(penWarn); qp.setFont(fontb); 
                        r = QRect(x0txt, ymidbarrel-0*dy_, dwdrill,dy_); qp.drawText(r, Qt.AlignLeft, '%.1fA'%(motorI))   
                        qp.setFont(font)

                        qp.setPen(penReg); qp.setFont(fontb);
                        r = QRect(x0txt, ymidbarrel-1*dy_, dwdrill,dy_); qp.drawText(r, Qt.AlignLeft, '%.0fV'%(motorU))   


class drillLocation(QWidget):

        def __init__(self, parent = None):
                QWidget.__init__(self, parent)

        def paintEvent(self, event):
                qp = QPainter()
                qp.begin(self)
                qp.setFont(font)        
                drawBoreHole(qp,0)
                self.qp = qp
                qp.end()

        def sizeHint(self): return QSize(400, 1200)

#----------------------
#----------------------
#----------------------

def myEvenListener():

        global t, r,   l,lliq,ldrill,load,hammer,sliprate,motorRPM,motorI,motorU,motorflash, temp1,temp2, incl,azi, vdrill_hist,vdrill,ETA
        testRedisConn(r)
        l       = getZero(t)
        ldrill  = getDepth(t)
#        print ldrill
        load    = getLoad(t)
        hammer  = getHammer(t)
        sliprate  = getGyroSlipRate(t)
        (motorRPM,motorI,motorU) = getMotor(t)
        (temp1,temp2) = getTemperatures(t)    
        (incl,azi)    = getOrientation(t)     
        vdrill_inst  = -getVel(t) * 1e2
        vdrill_hist  = np.hstack([vdrill_hist[1::],vdrill_inst]) 
        vdrill       = np.nanmean(vdrill_hist) 
#        vdrill = vdrill_inst
        
        if   vdrill<-10 and ldrill<(l-30): ETA =      (ldrill/(-vdrill*1e-2)) /60 
        elif vdrill>+10 and ldrill>(30):   ETA = -((l-ldrill)/(-vdrill*1e-2)) /60
        else:                              ETA = np.inf  

        #debug
        if SET_VALS_TO_WARN:
                f = 1.01
                hammer   = f*warn_hammer
                sliprate = f*warn_sliprate
                motorRPM = f*1
                motorI   = f*warn_motorI
                temp1    = f*warn_temp
                temp2    = f*warn_temp
                load     = f*warn_load 
                vdrill   = f*warn_vdrill

        motoron = (motorRPM > 1.0) 
#        if WRITEMODE and (not motoron) and ldrill>l: setNewZero(ldrill)

        progress.repaint()        
        t = t+dt

       
#----------------------
# QT MAIN
#----------------------

app = QApplication([])
w = QWidget() ## Define a top-level widget to hold everything
geom_xy = getMaxGeom()
f = 1./3.93
w.resize(geom_xy[0]*f, geom_xy[1]*0.97)
w.move(geom_xy[0]*(1-f),0)
w.setWindowTitle('Drill position')

#----------------------
# Add widgets to the layout in their proper positions
#----------------------

layout = QGridLayout()
layout.setSpacing(10)
w.setLayout(layout)
progress = drillLocation()
layout.addWidget(progress, 0, 0, 4, 1)  # plot goes on right side, spanning 3 rows
#advplots = QPushButton("Advanced plots")
#advplots.clicked.connect(lambda: os.system('python2.7 drill-advancedrun.py read 0.25 40')) 
#layout.addWidget(advplots, 0, 0);
w.show()

if dt>0:
        # Run (main) window "updater" ever dt seconds
        timer1 = QTimer()
        timer1.timeout.connect(myEvenListener)
        timer1.start(dt*1000.0)

        # Start the Qt event loop
        app.exec_()
else:
        while 1: myEvenListener()

