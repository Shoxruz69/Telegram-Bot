#!/bin/bash

# Botni orqa fonda ishga tushirish
python bot.py &

# Flask admin panelini ishga tushirish (Render bergan PORT da)
gunicorn admin_app:app --bind 0.0.0.0:$PORT
