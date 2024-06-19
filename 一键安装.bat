@echo off
chcp 65001 >nul
setlocal

set "getProgramName=Cling_toolbox"
set "getAimDir=D:\Cling_toolbox"
set "getMayaModDir=%USERPROFILE%\Documents\maya\"

if not exist "%getMayaModDir%modules\" (
    mkdir "%getMayaModDir%modules\" || (
        echo 创建目录 %getMayaModDir%modules\ 失败。
        pause
        exit /b 1
    )
)

(
    echo + %getProgramName% 1.0 %getAimDir%
) > "%getMayaModDir%modules\%getProgramName%.mod" || (
    echo 创建工具文件 %getMayaModDir%modules\%getProgramName%.mod 失败。
    pause
    exit /b 1
)

echo Maya工具 %getProgramName% 已成功创建。
pause
