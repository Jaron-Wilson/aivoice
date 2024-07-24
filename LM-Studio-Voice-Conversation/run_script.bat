@echo off
REM Activate the Conda environment
call conda activate python
REM INSTALL ALL THINGS IT SAYS IT DOES NEED
pip install git+https://github.com/openai/whisper.git
pip install pyaudio
pip install openai==0.28
pip install keyboard
pip install pyttsx3
pip install Numpy

REM Change to the specific drive and directory
D:
cd /d C:\Users\jaron\Documents\TTS_CONDA\LM-Studio-Voice-Conversation\

REM Check if the directory change was successful
if not exist "%cd%" (
    echo The system cannot find the path specified: D:\path\to your project\
    goto end
)

REM Run the Python script
python speak.py

:end
pause
