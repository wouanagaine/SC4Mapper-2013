@echo off
cl /O2 /GA /Foqfs.obj /Ic:\python27\include /Tcqfs.c /LD /link /LIBPATH:c:\python27\libs
cl /EHsc /O2 /GA /Fotools3D.obj /Ic:\python27\include /I./include /Tptools3D.cpp /LD /link /LIBPATH:c:\python27\libs 

copy tools3D.dll tools3D.pyd 
copy qfs.dll QFS.pyd 
copy *.pyd ..