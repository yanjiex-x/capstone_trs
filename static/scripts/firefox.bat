@ECHO OFF

ECHO Locating Firefox Uninstaller...

FOR /F "tokens=*" %%F IN ('WHERE /R C:\ helper.exe') DO (
  SET FOLDER=%%F & GOTO :Uninstall
)

:Uninstall
ECHO Located Firefox Uninstaller
ECHO Uninstalling Firefox...
"%FOLDER%" /S & GOTO :LocateInstaller

:LocateInstaller
ECHO Locating Firefox Installer...
FOR /F "tokens=*" %%K IN ('WHERE /R C:\ "Firefox Installer.exe"') DO (
  SET INSTALLER=%%K & GOTO :Execute
)

:Execute
ECHO Reinstalling Firefox...
"%INSTALLER%"
ECHO Firefox has been reinstalled and up-to-date!
