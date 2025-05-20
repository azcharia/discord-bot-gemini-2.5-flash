@echo off
echo ========================================
echo    GITHUB REPOSITORY UPLOAD SCRIPT
echo ========================================
echo.

REM Cek apakah git sudah terinstall
where git >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Git tidak ditemukan. Silakan install git terlebih dahulu.
    echo Download git dari: https://git-scm.com/downloads
    exit /b
)

REM Inisialisasi git jika belum ada
if not exist .git (
    echo Inisialisasi repository Git baru...
    git init
    echo.
)

REM Minta input untuk nama repository
set /p repo_name=Masukkan nama repository GitHub (misalnya: shapes-chat-bot): 
echo.

REM Minta input untuk username GitHub
set /p username=Masukkan username GitHub Anda: 
echo.

REM Buat .gitignore jika belum ada
if not exist .gitignore (
    echo Membuat file .gitignore...
    echo node_modules/ > .gitignore
    echo .env >> .gitignore
    echo .wwebjs_auth/ >> .gitignore
    echo .wwebjs_cache/ >> .gitignore
    echo.
)

REM Tambahkan semua file
echo Menambahkan file ke staging area...
git add .
echo.

REM Commit perubahan
set /p commit_message=Masukkan pesan commit (misalnya: "Initial commit"): 
git commit -m "%commit_message%"
echo.

REM Cek apakah remote origin sudah ada
git remote -v | findstr origin >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Menambahkan remote origin...
    git remote add origin https://github.com/%username%/%repo_name%.git
) else (
    echo Remote origin sudah ada, melanjutkan...
)
echo.

REM Push ke GitHub
echo Push ke GitHub repository...
git branch -M main
git push -u origin main

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo Repository berhasil di-upload ke GitHub!
    echo.
    echo Repository URL: https://github.com/%username%/%repo_name%
    echo ========================================
    echo.
) else (
    echo.
    echo Terjadi kesalahan saat push ke GitHub.
    echo Pastikan username dan nama repository sudah benar.
    echo Juga, pastikan Anda sudah login ke GitHub di komputer ini.
    echo.
    echo Untuk login ke GitHub, gunakan perintah:
    echo git config --global user.name "USERNAME"
    echo git config --global user.email "EMAIL"
    echo.
)

pause 