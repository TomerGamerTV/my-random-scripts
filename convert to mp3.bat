@echo off
setlocal enabledelayedexpansion

for %%A in (*.*) do (
    if NOT "%%~xA"==".mp3" (
        set "filename=%%~nA"
        ffmpeg -i "%%A" -vn -acodec libmp3lame "!filename!.mp3"
    )
)

endlocal