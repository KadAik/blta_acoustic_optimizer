@echo off
REM ===========================================================================
REM  BTLA Acoustic Optimizer — lanceur en un clic
REM  Double-cliquez simplement sur ce fichier. Le premier lancement installe
REM  tout (prend quelques minutes) ; les suivants démarrent instantanément.
REM ===========================================================================
cd /d "%~dp0"

REM --- Recherche de Python ----------------------------------------------------
where python >nul 2>nul
if errorlevel 1 (
    echo [ERREUR] Python est introuvable sur cet ordinateur.
    echo Veuillez installer Python 3.12 ou plus recent depuis https://www.python.org/downloads/
    echo et bien cocher "Add Python to PATH" pendant l'installation.
    echo.
    pause
    exit /b 1
)

REM --- Creation de l'environnement prive au premier lancement -----------------
if not exist ".venv\Scripts\activate.bat" (
    echo Creation d'un environnement Python prive ^(premier lancement uniquement^)...
    python -m venv .venv
    if errorlevel 1 (
        echo [ERREUR] Impossible de creer l'environnement.
        pause
        exit /b 1
    )
)

call ".venv\Scripts\activate.bat"

REM --- Installation / mise a jour des dependances ------------------------------
echo Verification des dependances ^(le premier lancement les telecharge^)...
python -m pip install --upgrade pip >nul
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERREUR] Impossible d'installer les paquets requis.
    pause
    exit /b 1
)

REM --- Lancement ---------------------------------------------------------------
echo.
echo Demarrage de BTLA Acoustic Optimizer dans votre navigateur web...
echo Laissez cette fenetre noire ouverte pendant l'utilisation de l'application.
echo Fermez cette fenetre lorsque vous avez termine.
echo.
streamlit run app.py

pause
