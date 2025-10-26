@echo off
REM ========================================================================
REM  NutriLogic Email Configuration Setup (Windows)
REM  This script helps you set up the email password for password resets
REM ========================================================================

color 0A
echo.
echo ========================================================================
echo               NUTRILOGIC - EMAIL CONFIGURATION SETUP
echo ========================================================================
echo.
echo This script will help you configure Gmail SMTP for password resets
echo.
echo Sender Email: nutrilogic79@gmail.com
echo.
echo ========================================================================
echo.

REM Check if EMAIL_HOST_PASSWORD is already set
if defined EMAIL_HOST_PASSWORD (
    echo [INFO] EMAIL_HOST_PASSWORD is already set!
    echo Current value: %EMAIL_HOST_PASSWORD%
    echo.
    set /p OVERWRITE="Do you want to overwrite it? (Y/N): "
    if /i not "%OVERWRITE%"=="Y" (
        echo.
        echo Setup cancelled. Exiting...
        timeout /t 3 >nul
        exit /b
    )
)

echo.
echo ========================================================================
echo                      STEP 1: Generate App Password
echo ========================================================================
echo.
echo Please follow these steps to generate a Gmail App Password:
echo.
echo 1. Open your browser and go to:
echo    https://myaccount.google.com/apppasswords
echo.
echo 2. Sign in with: nutrilogic79@gmail.com
echo.
echo 3. Select:
echo    - App: Mail
echo    - Device: Other (Custom name) -- Type "NutriLogic"
echo.
echo 4. Click "Generate"
echo.
echo 5. Copy the 16-character password
echo.
echo ========================================================================
echo.
set /p OPEN_BROWSER="Open the Google App Passwords page now? (Y/N): "
if /i "%OPEN_BROWSER%"=="Y" (
    start https://myaccount.google.com/apppasswords
    echo.
    echo Browser opened. Please follow the steps above.
    echo.
)

echo.
echo ========================================================================
echo                   STEP 2: Enter App Password
echo ========================================================================
echo.
echo Paste your 16-character App Password below:
echo (Format: xxxx xxxx xxxx xxxx - spaces will be removed automatically)
echo.

set /p APP_PASSWORD="App Password: "

REM Remove spaces from the password
set "APP_PASSWORD=%APP_PASSWORD: =%"

if "%APP_PASSWORD%"=="" (
    echo.
    echo [ERROR] No password entered!
    echo Setup failed. Please run this script again.
    pause
    exit /b 1
)

REM Set the environment variable for the current session
set EMAIL_HOST_PASSWORD=%APP_PASSWORD%

echo.
echo ========================================================================
echo                        Configuration Complete!
echo ========================================================================
echo.
echo [SUCCESS] EMAIL_HOST_PASSWORD has been set for this session!
echo.
echo IMPORTANT NOTES:
echo.
echo 1. This setting is TEMPORARY (current terminal session only)
echo.
echo 2. To make it permanent for your user account, run:
echo    setx EMAIL_HOST_PASSWORD "%APP_PASSWORD%"
echo.
echo 3. For project-only persistence, create a .env file in the project root:
echo    EMAIL_HOST_PASSWORD=%APP_PASSWORD%
echo.
echo ========================================================================
echo.

set /p MAKE_PERMANENT="Would you like to make this setting permanent? (Y/N): "
if /i "%MAKE_PERMANENT%"=="Y" (
    setx EMAIL_HOST_PASSWORD "%APP_PASSWORD%" >nul 2>&1
    if %ERRORLEVEL% EQU 0 (
        echo.
        echo [SUCCESS] Environment variable saved permanently!
        echo You may need to restart your terminal for it to take effect.
    ) else (
        echo.
        echo [WARNING] Could not save permanently. You may need administrator rights.
        echo The variable is still set for this session.
    )
)

echo.
echo ========================================================================
echo                        NEXT STEPS
echo ========================================================================
echo.
echo 1. Run the test script to verify the configuration:
echo    python test_email.py
echo.
echo 2. Or test via the website:
echo    python manage.py runserver
echo    Then go to: http://127.0.0.1:8000/password-reset/
echo.
echo 3. Check your email inbox (adithiyavinu.b@gmail.com) for the test email
echo.
echo ========================================================================
echo.

set /p RUN_TEST="Would you like to run the email test now? (Y/N): "
if /i "%RUN_TEST%"=="Y" (
    echo.
    echo Running email test...
    echo.
    python test_email.py
)

echo.
echo ========================================================================
echo                      Setup Script Complete
echo ========================================================================
echo.
echo For more information, see:
echo   - EMAIL_SETUP_GUIDE.md (detailed guide)
echo   - QUICK_EMAIL_SETUP.txt (quick reference)
echo.
pause

