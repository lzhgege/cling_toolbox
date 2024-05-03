@echo off
setlocal


set "getProgramName=Cling_toolbox"
set "getAimDir=D:\Cling_toolbox"
set "getMayaModDir=%USERPROFILE%\Documents\maya\"


if not exist "%getMayaModDir%modules\" (
    mkdir "%getMayaModDir%modules\"
)


(
    echo + %getProgramName% 1.0 %getAimDir%
) > "%getMayaModDir%modules\%getProgramName%.mod"


echo Maya module for %getProgramName% has been created.
