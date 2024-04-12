import winsound  # Library for playing Windows system sounds
import mido  # Library for working with MIDI files
import time

# Load the MIDI file
midi_file = mido.MidiFile("C:\\Users\\tomer\\Desktop\\Synapse X\\workspace\\midi\\Bad_Piggies.mid")

# Analyze MIDI data
tempo = midi_file.ticks_per_beat

# Define sound mappings (expand as needed)
sound_mapping = {
    "note_on": {
        60: "SystemAsterisk",  # C4
        62: "SystemExclamation",  # D4
        # ... (map other notes to sounds)
    },
    "note_off": None,  # Handle note releases
    "control_change": {
        7: "SystemHand",  # Volume control (optional)
    },
}

# Calculate duration based on message type and tempo


def calculate_duration(message, tempo):
    if message.type == "note_on":
        duration = message.time * tempo / 500000  # MIDI ticks to seconds
    else:
        duration = 0  # Assume instant for other events
    return duration


# Playback loop
for message in midi_file.play():
    try:
        sound_name = sound_mapping[message.type][message.note]  # Access note attribute

        if sound_name:
            winsound.PlaySound(sound_name, winsound.SND_ASYNC)
    except KeyError:
        pass  # Ignore unmapped events

    time.sleep(calculate_duration(message, tempo))
