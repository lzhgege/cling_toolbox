@echo off
setlocal EnableDelayedExpansion


chcp 65001


set "destination_folder=D:\Cling_toolbox"


if not exist "!destination_folder!" (
    mkdir "!destination_folder!"
)


set "download_url=https://tool.cgfml.com/Cling_toolbox/Cling_toolbox.zip"

set "temp_zip_file=!destination_folder!\Cling_toolbox.zip"


powershell -Command "(New-Object System.Net.WebClient).DownloadFile('!download_url!', '!temp_zip_file!')"


if not exist "!temp_zip_file!" (
    echo 无法下载Cling_toolbox.zip
    goto :error
)


powershell -Command "Add-Type -AssemblyName System.IO.Compression.FileSystem; [System.IO.Compression.ZipFile]::ExtractToDirectory('!temp_zip_file!', '!destination_folder!');"


if !errorlevel! neq 0 (
    echo 解压Cling_toolbox.zip失败
    goto :error
)


del "!temp_zip_file!"

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


echo 成功安装cling_toolbox，请重启maya享用，请勿删除 "!destination_folder!"
pause
goto :eof


:error
echo 下载和解压文件时发生错误请联系cling
pause

:end
