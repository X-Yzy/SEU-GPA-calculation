@echo off
setlocal EnableExtensions DisableDelayedExpansion
chcp 65001 >nul
pushd "%~dp0" >nul 2>&1
if errorlevel 1 goto folder_error

set "SEU_SCRIPT=%~n0.py"
if not exist "%SEU_SCRIPT%" goto script_error

python -c "import sys, tkinter; raise SystemExit(sys.version_info < (3, 10))" >nul 2>&1
if not errorlevel 1 goto run_python
py -3 -c "import sys, tkinter; raise SystemExit(sys.version_info < (3, 10))" >nul 2>&1
if not errorlevel 1 goto run_py
echo Python 3.10 or newer with Tkinter is required.
echo Install Python with Tcl/Tk support, then run this file again.
set "SEU_RESULT=1"
goto failed

:run_python
python -c "import requests" >nul 2>&1
if not errorlevel 1 goto launch_python
echo Installing requests for school login...
python -m pip install requests
if errorlevel 1 goto dependency_error
python -c "import requests" >nul 2>&1
if errorlevel 1 goto dependency_error

:launch_python
python -B "%SEU_SCRIPT%"
set "SEU_RESULT=%ERRORLEVEL%"
goto finished

:run_py
py -3 -c "import requests" >nul 2>&1
if not errorlevel 1 goto launch_py
echo Installing requests for school login...
py -3 -m pip install requests
if errorlevel 1 goto dependency_error
py -3 -c "import requests" >nul 2>&1
if errorlevel 1 goto dependency_error

:launch_py
py -3 -B "%SEU_SCRIPT%"
set "SEU_RESULT=%ERRORLEVEL%"
goto finished

:finished
if "%SEU_RESULT%"=="0" goto success
echo The application exited with error %SEU_RESULT%. See the details above.
goto failed

:dependency_error
echo Could not install or load requests. Check the pip error and your network, then try again.
set "SEU_RESULT=1"
goto failed

:script_error
echo Cannot find "%SEU_SCRIPT%".
echo Extract the whole ZIP first. Keep the BAT and matching PY file together.
set "SEU_RESULT=1"
goto failed

:folder_error
echo Cannot open the application folder. Extract the ZIP to a writable folder.
pause
exit /b 1

:failed
pause
popd
exit /b %SEU_RESULT%

:success
popd
exit /b 0
