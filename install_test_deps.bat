@echo off
echo Installing test dependencies...
pip install behave==1.2.6
pip install requests==2.31.0
pip install pytest==7.4.3
pip install pytest-mock==3.12.0
pip install psutil
echo.
echo Test dependencies installed successfully!
echo.
echo You can now run tests with:
echo python run_tests.py
pause