@ REM ######################################
@ REM # Variable to ignore <CR> in DOS
@ REM # line endings
@ set SHELLOPTS=igncr

@ REM ######################################
@ REM # Variable to ignore mixed paths
@ REM # i.e. G:/$SOPC_KIT_NIOS2/bin
@ set CYGWIN=nodosfilewarning

rem @C:\\altera\\15.0\\quartus\\bin64\\quartus_pgm.exe -m jtag -c 1 -o "p;my.sof"
@ set SOPC_BUILDER_PATH=%SOPC_KIT_NIOS2%+%SOPC_BUILDER_PATH%

@ "C:\altera\15.0\quartus\bin64\cygwin\bin\bash.exe" --rcfile ".\DE2_115_SD_Card_Audio_Player_bashrc"
pause