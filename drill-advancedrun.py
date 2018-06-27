#!/usr/bin/python
# -*- coding: utf-8 -*-
# N. Rathmann, 2018

from header import *
import pyqtgraph as pg

#-----------------------
# INIT
#-----------------------

pg.setConfigOptions(background='#f0f0f0')
pg.setConfigOptions(foreground='k')

xaxisLenInMins = float(sys.argv[3]);

xaxisLenInSecs = 60 * xaxisLenInMins # 1 hour

# X-axis
hist_time  = np.flipud(np.arange(0,xaxisLenInSecs/dt+dt,dt))/60

# Y-axis data
hist_load  = np.full(len(hist_time),np.nan) # load
hist_pos   = np.full(len(hist_time),np.nan) # drill position
hist_vel   = np.full(len(hist_time),np.nan) # velocity (avg)
hist_cur   = np.full(len(hist_time),np.nan) # current
hist_rpm   = np.full(len(hist_time),np.nan) # RPM
hist_temp  = np.full(len(hist_time),np.nan) # RPM

# for time averages
velavg_hist = np.full(len(hist_time)/50,np.nan) # For averaging the velocity - the average of this array is the time-wise entries in hist_vel

# Y axis limits

ylim_load = [1,99]; # PERCENTILES of var
ylim_pos  = [-1, +4]; # meters above and below the current reference depth "dmsg-l" 
ylim_velslow  = [0, 4e-3]; # actual values of var
ylim_velfast  = [0, 1.3]; # actual values of var
ylim_cur  = [0,13]; # actual values of var
ylim_rpm  = [0,100]; # actual values of var
ylim_temp = [-10, 80]; # actual values of var

# Update rates
ticktock     = 0
updrate_load = 1
updrate_pos  = 2
updrate_vel  = 3
updrate_cur  = 3
updrate_rpm  = 3
updrate_temp = 5

def histroll(arr,pushme):
        arr = np.append(arr, pushme)
        arr = np.delete(arr, 0)
        return arr

#----------------------
# QT FUNCTIONS
#----------------------

def myEvenListener():

        global t, r
        global velavg_hist

        global hist_load, hist_pos, hist_vel, hist_cur, hist_rpm, hist_temp
        global curve_load, curve_pos, curve_vel, curve_cur, curve_rpm, curve_temp
        global ylim_load, ylim_pos, ylim_velfast,ylim_velslow, ylim_cur, ylim_rpm, ylim_temp

        testRedisConn(r)
        seconds = int(str(datetime.datetime.now())[17:19])

        #--------------------------------------
        # roll-over (update) histories
        #--------------------------------------
                
        hist_load = histroll(hist_load, getLoad(t))
        hist_pos  = histroll(hist_pos,  getDepth(t))

        (motorRPM,motorI,motorU) = getMotor(t)
        hist_cur  = histroll(hist_cur,  motorI)
        hist_rpm  = histroll(hist_rpm,  motorRPM)

        velavg_hist = histroll(velavg_hist, -getVel(t))
        velavg      = np.nanmean(velavg_hist)
        hist_vel    = histroll(hist_vel,  velavg)

        (temp1,temp2) = getTemperatures(t)    
        hist_temp  = histroll(hist_temp,  temp1)

        #--------------------------------------
        # update pygraph structures
        #-------------------------------------- 

        fsize = 5.5
        style = 'color="black"'
#        if head < head_warn: style = 'color="red" style="font-weight: bold;"';
#        plot_vel.setTitle(htmlfont('<b>v</b>: inst = %.1f,  <font color="#2c7fb8">avg = %.1f</font> [mm/s]'%(vdrill*1e3,vellong_hist[-1]*1e3),fsize) )

#        plot_tare.setTitle(htmlfont('<b>Tare</b>: tower - %.1fkg = %.1f kg'%(tareref,tare),fsize))
#        plot_head.setTitle(htmlfont('<b>&delta;</b>: <font %s>Tower - %.1fm*%.1fkg/m = %.1f kg</font>'%(style,(ldrill-drilllen),cabeldensity,head),fsize))
#        if vdrill<0: ETA = ldrill/(-vellong_hist[-1]) /60 
#        else:        ETA = np.inf  
#        statuslbls[0].setText('ETA: %.0f minutes'%(ETA) )
#        statuslbls[1].setText("Hole depth: %.2f m"%(l) )    
#        statuslbls[2].setText("Ping %s"%( datetime.datetime.now().strftime("%H:%M:%S::%f")[:-4]) ) 

        plot_load.setTitle(htmlfont('<b>Load:&nbsp; %.1f kg'%(hist_load[-1]),fsize))
        curve_load.setData(x=hist_time,y=hist_load)
        prctls = np.nanpercentile(hist_load,ylim_load);
        plot_load.setYRange(np.floor(prctls[0])-1,np.ceil(prctls[1])+1, padding=0)

        plot_vel.setTitle(htmlfont('<b>Average winch speed:&nbsp; %.2f m/s'%(hist_vel[-1]),fsize))
        curve_vel.setData(x=hist_time,y=hist_vel)
#        if hist_vel[-1]<0:      
        if hist_vel[-1]<6e-3:   plot_vel.setYRange(ylim_velslow[0],ylim_velslow[1], padding=0)
        else:                   plot_vel.setYRange(ylim_velfast[0],ylim_velfast[1], padding=0)

        plot_pos.setTitle(htmlfont('<b>Depth:&nbsp; %.2f m '%(hist_pos[-1]),fsize))
        curve_pos.setData(x=hist_time,y=hist_pos)
#        plot_pos.setYRange(ylim_vel[0],ylim_vel[1], padding=0)


        plot_cur.setTitle(htmlfont('<b>Motor current:&nbsp; %.1f A'%(hist_cur[-1]),fsize))
        curve_cur.setData(x=hist_time,y=hist_cur)
        plot_cur.setYRange(ylim_cur[0],ylim_cur[1], padding=0)

        plot_rpm.setTitle(htmlfont('<b>Motor speed:&nbsp; %.0f RPM'%(hist_rpm[-1]),fsize))
        curve_rpm.setData(x=hist_time,y=hist_rpm)
        plot_rpm.setYRange(ylim_cur[0],ylim_rpm[1], padding=0)

        plot_temp.setTitle(htmlfont('<b>Plate temperature:&nbsp; %.0f deg. C'%(hist_temp[-1]),fsize))
        curve_temp.setData(x=hist_time,y=hist_temp)
        plot_temp.setYRange(ylim_temp[0],ylim_temp[1], padding=0)

#        curve_tare.setData(x=hist_time,y=tare_hist)
#        curve_head.setData(x=hist_time,y=head_hist)
#        curve_velinst.setData(x=hist_time,y=velinst_hist*1e3)

#        minmin = np.nanmin([np.nanmin(vellong_hist),np.nanmin(velinst_hist)])
#        maxmax = np.nanmax([np.nanmax(vellong_hist),np.nanmax(velinst_hist)])
#        plot_vel.setYRange(minmin*1e3, maxmax*1e3, padding=0)
        
        t = t+dt

#----------------------
# QT MAIN
#----------------------

app = QApplication([])
w = QWidget() ## Define a top-level widget to hold everything
#w.resize(1500, 1000)
w.move(0,0)
w.setWindowTitle('Drill advanced plots')


# Set labels and positions

def labelObjMaker(text0):
                lbl = QLabel(text0); 
                lbl.setFont(font);
                return lbl

def setupaxis(obj):
        obj.invertX()
        obj.setXRange(0, xaxisLenInSecs/60, padding=0)
        obj.showAxis('right')
        obj.showAxis('top')        

# Plots
plot_load = pg.PlotWidget(); setupaxis(plot_load);
plot_vel  = pg.PlotWidget(); setupaxis(plot_vel);
plot_pos  = pg.PlotWidget(); setupaxis(plot_pos);
plot_cur  = pg.PlotWidget(); setupaxis(plot_cur);
plot_rpm  = pg.PlotWidget(); setupaxis(plot_rpm);
plot_temp = pg.PlotWidget(); setupaxis(plot_temp);

#----------------------
# Add widgets to the layout in their proper positions
#----------------------

layout = QGridLayout()
layout.setSpacing(15)
w.setLayout(layout)

# widgets

layout.addWidget(plot_load, 0, 0, 1,1)  # plot goes on right side, spanning 3 rows
layout.addWidget(plot_pos,  1, 0, 1,1)  # plot goes on right side, spanning 3 rows
layout.addWidget(plot_vel,  2, 0, 1,1)  # plot goes on right side, spanning 3 rows

layout.addWidget(plot_cur,  0, 1, 1,1)  # plot goes on right side, spanning 3 rows
layout.addWidget(plot_rpm,  1, 1, 1,1)  # plot goes on right side, spanning 3 rows
layout.addWidget(plot_temp, 2, 1, 1,1)  # plot goes on right side, spanning 3 rows


width = 3
plotpen_black = pg.mkPen(color='k',       width=width)
plotpen_blue  = pg.mkPen(color='#377eb8', width=width)
plotpen_purp  = pg.mkPen(color='#984ea3', width=width)
plotpen_brow  = pg.mkPen(color='#a65628', width=width)


plotpen_avg   = pg.mkPen(color=QColor(44,127,184), width=width)
plotpen_warn  = pg.mkPen(color=QColor(240,59,32), width=width*3)

curve_load    = plot_load.plot( x=hist_time,y=hist_time*0-1e4, pen=plotpen_black) 
curve_vel     = plot_vel.plot(  x=hist_time,y=hist_time*0-1e4, pen=plotpen_brow)
curve_pos     = plot_pos.plot(  x=hist_time,y=hist_time*0-1e4, pen=plotpen_black)
curve_cur     = plot_cur.plot(  x=hist_time,y=hist_time*0-1e4, pen=plotpen_blue)
curve_rpm     = plot_rpm.plot(  x=hist_time,y=hist_time*0-1e4, pen=plotpen_blue)
curve_temp    = plot_temp.plot( x=hist_time,y=hist_time*0-1e4, pen=plotpen_purp)


def setAxisTicksEtc(obj):
        fsize = 5
        offsetx = 10
        offsety = 10
        ax = obj.getAxis("bottom");   ax.tickFont = fontsmaller; ax.setStyle(tickTextOffset=offsetx)
        ax = obj.getAxis("top");      ax.setTicks([])
        ax = obj.getAxis("left");     ax.setTicks([])
        ax = obj.getAxis("right");    ax.tickFont = fontsmaller; ax.setStyle(tickTextOffset=offsety)
        obj.setLabel('right', htmlfont("&nbsp;",fsize))
        obj.showGrid(y=True)
#        obj.setLabel('bottom', htmlfont("Seconds ago",fsize))
        obj.setLabel('bottom', htmlfont("Minutes ago",fsize))
        
setAxisTicksEtc(plot_load)
setAxisTicksEtc(plot_pos)
setAxisTicksEtc(plot_vel)
setAxisTicksEtc(plot_cur)
setAxisTicksEtc(plot_rpm)
setAxisTicksEtc(plot_temp)

# Display the widget as a new window
#layout.setColumnStretch(0,0)
#layout.setColumnStretch(1,1)
#layout.setColumnStretch(2,1)
w.show()

# Run (main) window "updater" ever dt seconds
timer1 = QTimer()
timer1.timeout.connect(myEvenListener)
timer1.start(dt*1000)

# Start the Qt event loop
app.exec_()

