#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

; Open the file and read its contents into a list
FileOpen, file, "%1"
FileReadLines, lines, file
FileClose, file

; Keep track of the current line index
line_index = 0

; Bind Ctrl+V to a custom paste function that pastes a line from the file
; and moves to the next line
^v::
    global line_index

    ; Get the current line from the list
    line := lines[line_index]

    ; Increment the line index so we move to the next line next time
    line_index := (line_index + 1) % lines.MaxIndex()

    ; Set the clipboard contents to the current line
    clipboard := line
    return

; Bind Ctrl+Alt+T to a function that stops the script
^!t::
    exit
