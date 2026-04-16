@echo off
chcp 65001 >nul
REM StudyStride API测试运行脚本

setlocal enabledelayedexpansion

REM 默认配置
set ALLURE_DIR=reports\allure-results
set REPORT_DIR=reports\allure-report
set PARALLEL=1
set RERUNS=2

REM 解析参数
if "%~1"=="" goto :help

if "%~1"=="all" goto :run_all
if "%~1"=="smoke" goto :run_smoke
if "%~1"=="regression" goto :run_regression
if "%~1"=="report" goto :generate_report
if "%~1"=="serve" goto :serve_report
if "%~1"=="help" goto :help
goto :help

:run_all
echo ========================================
echo 运行所有测试
echo ========================================
python -m pytest testcases -v --alluredir=%ALLURE_DIR% --clean-alluredir -n %PARALLEL% --reruns %RERUNS%
goto :end

:run_smoke
echo ========================================
echo 运行冒烟测试
echo ========================================
python -m pytest testcases -v -m "smoke" --alluredir=%ALLURE_DIR% --clean-alluredir
goto :end

:run_regression
echo ========================================
echo 运行回归测试
echo ========================================
python -m pytest testcases -v -m "regression" --alluredir=%ALLURE_DIR% --clean-alluredir -n %PARALLEL%
goto :end

:generate_report
echo ========================================
echo 生成Allure报告
echo ========================================
if not exist %REPORT_DIR% mkdir %REPORT_DIR%
allure generate %ALLURE_DIR% -o %REPORT_DIR% --clean
echo.
echo 报告已生成: %REPORT_DIR%
echo 使用命令查看: allure open %REPORT_DIR%
goto :end

:serve_report
echo ========================================
echo 启动Allure报告服务
echo ========================================
allure serve %ALLURE_DIR%
goto :end

:help
echo StudyStride API测试运行脚本
echo.
echo 用法: run.bat [命令] [选项]
echo.
echo 命令:
echo   all          运行所有测试
echo   smoke        运行冒烟测试
echo   regression   运行回归测试
echo   report       生成Allure报告
echo   serve        启动Allure报告服务
echo   help         显示帮助信息
echo.
echo 示例:
echo   run.bat all
echo   run.bat smoke
echo   run.bat report
echo   run.bat serve
echo.

:end
endlocal
