@ECHO OFF

UsoClient StartScan
USOClient.exe StartInteractiveScan
UsoClient StartDownload
ScanInstallWait
UsoClient StartInstall
shutdown -r -t 1800
