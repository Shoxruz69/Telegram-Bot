#!/bin/bash

echo "=== Telegram Bot va Admin Panel ishga tushmoqda ==="

# Bot.py ni orqa fonda ishga tushirish - crash bo'lsa avtomatik qayta start
while true; do
    echo "[$(date)] Bot ishga tushirilmoqda..."
    python bot.py
    echo "[$(date)] Bot to'xtadi. 5 soniyadan so'ng qayta ishga tushiriladi..."
    sleep 5
done &

BOT_PID=$!
echo "Bot PID: $BOT_PID"

# Flask admin panelini ishga tushirish (Render bergan PORT da)
echo "Admin panel ishga tushirilmoqda (PORT: ${PORT:-5000})..."
exec gunicorn admin_app:app \
    --bind 0.0.0.0:${PORT:-5000} \
    --workers 2 \
    --threads 4 \
    --timeout 60 \
    --keep-alive 15 \
    --log-level info \
    --access-logfile - \
    --error-logfile -
