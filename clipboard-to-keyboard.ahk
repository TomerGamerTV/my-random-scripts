#SingleInstance, Force

^!v::
   ; Save the current clipboard content
   clipboard := ClipboardAll

   ; Save the state of the modifier keys (Ctrl and Alt)
   ctrlState := GetKeyState("Ctrl", "P")
   altState := GetKeyState("Alt", "P")

   ; Release Ctrl and Alt if they are currently pressed
   if (ctrlState)
      Send {Ctrl Up}
   if (altState)
      Send {Alt Up}

   ; Send the clipboard content as keystrokes
   SendInput, %clipboard%

   ; Restore the state of Ctrl and Alt
   if (ctrlState)
      Send {Ctrl Down}
   if (altState)
      Send {Alt Down}

   ; Restore the original clipboard content
   Clipboard := clipboard
   return
