@echo off
echo ================================================
echo  GreySignal Pipeline — %date% %time%
echo ================================================

cd /d D:\GreySignal
call conda activate greysignal

echo.
echo [1/8] Scraping news...
python scraping/google_news.py
if %errorlevel% neq 0 ( echo ERROR in scraper & pause & exit /b 1 )

echo.
echo [2/8] Cleaning text...
python nlp/cleaning.py
if %errorlevel% neq 0 ( echo ERROR in cleaning & pause & exit /b 1 )

echo.
echo [3/8] Filtering IPO articles...
python nlp/ipo_filter.py
if %errorlevel% neq 0 ( echo ERROR in filter & pause & exit /b 1 )

echo.
echo [4/8] Extracting IPO names...
python nlp/ipo_name_extractor.py
if %errorlevel% neq 0 ( echo ERROR in extractor & pause & exit /b 1 )

echo.
echo [5/8] Scoring sentiment...
python nlp/sentiment.py
if %errorlevel% neq 0 ( echo ERROR in sentiment & pause & exit /b 1 )

echo.
echo [6/8] Aggregating sentiment...
python nlp/aggregate_sentiment.py
if %errorlevel% neq 0 ( echo ERROR in aggregation & pause & exit /b 1 )

echo.
echo [7/8] Generating signals...
python nlp/ipo_signal.py
if %errorlevel% neq 0 ( echo ERROR in signal generator & pause & exit /b 1 )

echo.
echo [7b] Scraping GMP...
python fundamentals/fetch_gmp.py

echo.
echo [8/8] Writing to database...
python tools/db_writer.py
if %errorlevel% neq 0 ( echo ERROR writing to DB & pause & exit /b 1 )

echo.
echo ================================================
echo  Pipeline complete! %time%
echo ================================================