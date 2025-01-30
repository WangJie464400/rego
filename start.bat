@echo off
echo =============================
echo START  Project: Rego
echo =============================

REM 启动 Django 后端
echo.
echo Strat Django ...
cd food_calorie_detection


REM 在新的命令窗口中启动 Django 服务器
start cmd /k "python manage.py runserver"

REM 返回根目录
cd ..

REM 启动 Vue 前端
echo.
echo Start Vue ...
cd food-calorie-frontend

REM 在新的命令窗口中安装依赖并启动 Vue 服务
start cmd /k "npm run serve"

start http://localhost:8080

echo.
echo OK!
