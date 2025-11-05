@echo off
REM Windows Installation Script for AfterSchoolSurvivors
REM Exit on error is handled via errorlevel checks

setlocal enabledelayedexpansion

REM Parse command-line options
set REINSTALL=false
if "%1"=="--reinstall" (
    set REINSTALL=true
    echo Reinstall mode enabled. Removing existing installations...
)

REM Get the absolute path of the project directory
set PROJECT_DIR=%~dp0
set PROJECT_DIR=%PROJECT_DIR:~0,-1%
echo Project directory: %PROJECT_DIR%

REM --- Cleanup Function (for --reinstall) ---
if "%REINSTALL%"=="true" (
    echo Cleaning up existing installation...

    REM Remove uv lockfile (for clean dependency resolution)
    set UV_LOCK=%PROJECT_DIR%\uv.lock
    if exist "!UV_LOCK!" (
        del /f "!UV_LOCK!"
        echo   Removed: !UV_LOCK!
    )

    echo Cleanup completed.
)

REM --- Remove existing launcher script (Always executed) ---
echo Removing existing launcher script...

REM Remove launcher script
set LAUNCHER_PATH=%USERPROFILE%\afterschool-survivors.bat
if exist "!LAUNCHER_PATH!" (
    del /f "!LAUNCHER_PATH!"
    echo   Removed: !LAUNCHER_PATH!
)

REM --- 1. Check for Python 3 ---
echo Step 1: Checking for Python 3...
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: python is not installed. Please install Python 3 and try again.
    exit /b 1
)
echo Python 3 found.

REM --- 2. Check Python Version ---
echo Step 2: Checking Python version...
set PYTHON_CMD=python

if exist "%PROJECT_DIR%\.python-version" (
    set /p REQUIRED_VERSION=<"%PROJECT_DIR%\.python-version"
    echo Required Python version: !REQUIRED_VERSION!

    REM Try to find specific Python version
    set PYTHON_SPECIFIC=python!REQUIRED_VERSION!
    !PYTHON_SPECIFIC! --version >nul 2>&1
    if not errorlevel 1 (
        set PYTHON_CMD=!PYTHON_SPECIFIC!
        echo Found !PYTHON_SPECIFIC!
    ) else (
        REM Check if default python matches
        for /f "tokens=2" %%i in ('python --version 2^>^&1') do set CURRENT_VERSION=%%i

        if "!CURRENT_VERSION!"=="!REQUIRED_VERSION!" (
            echo Default python version matches ^(!CURRENT_VERSION!^).
        ) else (
            echo Warning: Required Python version is '!REQUIRED_VERSION!', but you are using '!CURRENT_VERSION!'.
            echo Attempting to use python, but compatibility issues may occur.
            echo.
            echo To install Python !REQUIRED_VERSION!:
            echo   Visit https://www.python.org/downloads/
            echo.
            set /p CONTINUE="Continue with python (!CURRENT_VERSION!)? [y/N] "
            if /i not "!CONTINUE!"=="y" (
                exit /b 1
            )
        )
    )
) else (
    echo Warning: .python-version file not found. Using default python.
)

echo Using Python command: %PYTHON_CMD%

REM --- 3. Create Virtual Environment ---
set VENV_DIR=%PROJECT_DIR%\.venv
echo Step 3: Setting up virtual environment at %VENV_DIR%...
if exist "%VENV_DIR%" (
    echo Virtual environment already exists. Skipping creation.
) else (
    %PYTHON_CMD% -m venv "%VENV_DIR%"
    if errorlevel 1 (
        echo Error: Failed to create virtual environment.
        exit /b 1
    )
    echo Virtual environment created.
)

REM --- 4. Activate Venv and Install/Update pip and uv ---
call "%VENV_DIR%\Scripts\activate.bat"
echo Step 4: Setting up pip and uv build tool...

REM Ensure pip is installed in the virtual environment
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo pip not found in virtual environment. Installing pip...

    REM Try ensurepip first
    python -m ensurepip --upgrade >nul 2>&1
    if errorlevel 1 (
        echo ensurepip failed. Downloading get-pip.py...
        powershell -Command "Invoke-WebRequest -Uri https://bootstrap.pypa.io/get-pip.py -OutFile %TEMP%\get-pip.py"
        python %TEMP%\get-pip.py
        del %TEMP%\get-pip.py
        echo pip installed via get-pip.py.
    ) else (
        echo pip installed via ensurepip.
    )
)

REM Upgrade pip and install uv
python -m pip install --upgrade pip
if errorlevel 1 (
    echo Error: Failed to upgrade pip.
    exit /b 1
)
python -m pip install -U uv
if errorlevel 1 (
    echo Error: Failed to install uv.
    exit /b 1
)
echo pip and uv installed.

REM --- 5. Install Dependencies ---
echo Step 5: Installing dependencies from pyproject.toml...
cd /d "%PROJECT_DIR%"
python -m uv sync
if errorlevel 1 (
    echo Error: Failed to install dependencies.
    exit /b 1
)
echo Dependencies installed.

REM --- 6. Create Launcher Script ---
set LAUNCHER_NAME=afterschool-survivors.bat
set LAUNCHER_PATH=%USERPROFILE%\%LAUNCHER_NAME%
echo Step 6: Creating launcher script at %LAUNCHER_PATH%...

REM Force overwrite if reinstall mode, otherwise check existence
if "%REINSTALL%"=="true" goto CREATE_LAUNCHER
if not exist "%LAUNCHER_PATH%" goto CREATE_LAUNCHER
echo Launcher script already exists at %LAUNCHER_PATH%. Skipping.
goto SKIP_LAUNCHER

:CREATE_LAUNCHER
(
echo @echo off
echo REM This script activates the project's virtual environment and runs the main Python script.
echo.
echo REM Absolute path to the project directory
echo set PROJECT_DIR=%PROJECT_DIR%
echo.
echo REM Activate the virtual environment
echo call "%%PROJECT_DIR%%\.venv\Scripts\activate.bat"
echo.
echo REM Change to the project directory
echo cd /d "%%PROJECT_DIR%%"
echo.
echo REM Run the main application
echo python src\main.py %%*
) > "%LAUNCHER_PATH%"

echo Launcher script created at %LAUNCHER_PATH%

:SKIP_LAUNCHER

REM --- Completion Message ---
echo.
echo ----------------------------------------
echo Installation Complete!
echo ----------------------------------------

if "%REINSTALL%"=="true" (
    echo Reinstallation finished successfully.
    echo.
    echo Note: Virtual environment ^(.venv^) was preserved.
    echo       If you experience dependency issues, manually remove it:
    echo       rmdir /s /q "%PROJECT_DIR%\.venv"
    echo       Then run: install.bat
    echo.
)

echo To run the application:
echo   Method 1: Double-click: %LAUNCHER_PATH%
echo   Method 2: Type in command prompt: %LAUNCHER_NAME%
echo.
echo Or run directly from project directory:
echo   .venv\Scripts\activate.bat
echo   python src\main.py
echo.
echo Optional: Add launcher to PATH for easier access
echo   1. Search "Environment Variables" in Windows Start Menu
echo   2. Edit "Path" variable for your user
echo   3. Add new entry: %USERPROFILE%
echo   4. Restart command prompt
echo.
echo To reinstall ^(remove launcher before installing^):
echo   install.bat --reinstall
echo.

endlocal
