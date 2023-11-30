@ECHO OFF

ECHO Locating Chrome Updater...

FOR /F "tokens=*" %%F IN ('WHERE /R C:\ GoogleUpdate.exe') DO (
  SET FOLDER=%%F & GOTO :execute
)

:execute
ECHO Updating Google Chrome...
START "" "%FOLDER%"
ECHO Google Chrome has been updated!
