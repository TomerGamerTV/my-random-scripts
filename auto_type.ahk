; Script is half broken if your keyboard layout chages for some reason you will have to change it back to english manually

SoundPlay *-1

; Change the keyboard layout to English
;PostMessage, 0x50, 0, % (hkl := DllCall("LoadKeyboardLayout", "Str", "00000409", "UInt", 1)), "ahk_id " . DllCall("GetForegroundWindow")

; Check if Caps Lock is on
if GetKeyState("CapsLock", "T")
    SetCapsLockState, Off  ; Turn off Caps Lock if it's on

; Wait for 5 seconds (5000 milliseconds)
Sleep, 5000

; Press the Win+Space key combination
SendInput, {LWin down}{Space down}{Space up}{LWin up}

StopScript := false  ; Variable to track if the script should stop

; Set the PID of the program to check
programPID := 28560

; Read the text file
Loop, Read, ransomware-extension-list.txt
{
    line := A_LoopReadLine  ; Get the current line

    ; Check if the program with the specified PID is frozen
    Process, Exist, %programPID%
    If (ErrorLevel = 0)
    {
        ; Wait for a couple of seconds until it unfreezes
        Sleep, 2000
    }

    ; Type the line and hit enter
    SendInput %line%{Enter}
    Sleep, 500  ; Wait for 1 second (1000 milliseconds)

    ; Check if one of the hotkeys to stop or close the script is pressed
    if StopScript
    {
        ; Turn off Caps Lock if it's on
        if GetKeyState("CapsLock", "T")
            SetCapsLockState, Off

        ExitApp  ; Exit the script
    }
}

; Play a sound when the script has finished running over all the lines
SoundPlay *-1

; Show a notification when the script has finished running over all the lines
TrayTip, Script Finished, The script has finished running over all the lines.

; Close the script after playing the sound and showing the notification
ExitApp

; Hotkey to stop the script on pressing a specific key combination (e.g., Ctrl+Alt+S)
^!s::
    StopScript := true
return

; Hotkey to close the script on pressing a specific key combination (e.g., Ctrl+Q)
^q::
    StopScript := true
return
