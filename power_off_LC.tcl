

#nx os python to send test log message
import syslog
syslog.syslog(1,"2021 Aug 17 22:10:56 YQB-9513-F6SE6 %MODULE-2-MOD_SOMEPORTS_FAILED: Module 1 (Serial number: JAE200606DY) reported failure on ports fc6/34-36 (Fibre Channel) due to Local serial link syncing exception in device DEV_LOCAL_SAC_ASIC (device error 0xc9100200)")

syslog.syslog(1,'''2021 Aug 17 22:11:05 YQB-9513-F6SE6 %SYSMGR-2-SERVICE_CRASHED: Service "port" (PID 3685) hasn't caught signal 11 (core will be saved).''')





#check_log.tcl
#event syslog service port crashed due to module DEV_LOCAL_SAC_ASIC local serial link sync exception
#tcl script to collect log and abstract malfunction slot
set log [exec "sh logg | incl DEV_LOCAL_SAC_ASIC | incl Module | last 1"]
regexp -indices "Module " $log index;
set slotnum [lindex  $index 1]
set slot [string range $log $slotnum+1 $slotnum+2]




#exec command , should be shutdown $slot in real env
exec "show module $slot"

# eem config sample
event manager applet testlog
  event syslog pattern "%SYSMGR-2-SERVICE_CRASHED: Service"
  action 1 cli tclsh bootflash:///check_log.tcl
  action 2 syslog priority critical msg module shoule be poweroffed