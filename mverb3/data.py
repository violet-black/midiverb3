EQ = [
    "0.16KHz",
    "0.33KHz",
    "0.49KHz",
    "0.66KHz",
    "0.85KHz",
    "1.03KHz",
    "1.23KHz",
    "1.43KHz",
    "1.64KHz",
    "1.86KHz",
    "2.09KHz",
    "2.34KHz",
    "2.59KHz",
    "2.86KHz",
    "3.15KHz",
    "3.45KHz",
    "3.77KHz",
    "4.11KHz",
    "4.48KHz",
    "4.88KHz",
    "5.31KHz",
    "5.79KHz",
    "6.31KHz",
    "6.89KHz",
    "7.56KHz",
    "8.33KHz",
    "9.23KHz",
    "10.3KHz",
    "11.8KHz",
    "13.8KHz",
    "Off"
]

CHORUS_ALGORITHMS = [
    # Chorus
    {"type": "chorus", "display": "C1", "display_stereo": "SC1", "characteristics": "Smallest Depth"},
    {"type": "chorus", "display": "C2", "display_stereo": "SC2", "characteristics": "Small Depth"},
    {"type": "chorus", "display": "C3", "display_stereo": "SC3", "characteristics": "Medium Depth"},
    {"type": "chorus", "display": "C4", "display_stereo": "SC4", "characteristics": "Medium Depth"},
    {"type": "chorus", "display": "C5", "display_stereo": "SC5", "characteristics": "Big Depth"},
    {"type": "chorus", "display": "C6", "display_stereo": "SC6", "characteristics": "Biggest Depth"},
    # Flanger
    {"type": "flanger", "display": "F1", "display_stereo": "SF1", "characteristics": "Smallest Depth"},
    {"type": "flanger", "display": "F2", "display_stereo": "SF2", "characteristics": "Small Depth"},
    {"type": "flanger", "display": "F3", "display_stereo": "SF3", "characteristics": "Medium Depth"},
    {"type": "flanger", "display": "F4", "display_stereo": "SF4", "characteristics": "Medium Depth"},
    {"type": "flanger", "display": "F5", "display_stereo": "SF5", "characteristics": "Big Depth"},
    {"type": "flanger", "display": "F6", "display_stereo": "SF6", "characteristics": "Biggest Depth"},
]

REVERB_ALGORITHMS = [
    {"display": "ro1", "algorithm": "Room 1", "label": "SMALL ROOM", "characteristics": "High density; low diffusion"},
    {"display": "ro2", "algorithm": "Room 2", "label": "SMALL ROOM", "characteristics": "High density; high diffusion"},
    {"display": "ro3", "algorithm": "Room 3", "label": "MEDIUM ROOM", "characteristics": "Medium density; medium diffusion"},
    {"display": "ro4", "algorithm": "Room 4", "label": "LARGE ROOM", "characteristics": "Low density; high diffusion"},
    {"display": "HL1", "algorithm": "Hall 1", "label": "SMALL HALL", "characteristics": "Medium density; high diffusion"},
    {"display": "HL2", "algorithm": "Hall 2", "label": "SMALL HALL", "characteristics": "High density; low diffusion"},
    {"display": "HL3", "algorithm": "Hall 3", "label": "MEDIUM HALL", "characteristics": "Medium density; medium diffusion"},
    {"display": "HL4", "algorithm": "Hall 4", "label": "LARGE HALL", "characteristics": "Low density; low diffusion"},
    {"display": "CH1", "algorithm": "Chamber 1", "label": "MEDIUM CHAMBER", "characteristics": "Medium density; medium diffusion"},
    {"display": "CH2", "algorithm": "Chamber 2", "label": "MEDIUM CHAMBER", "characteristics": "Medium density; high diffusion"},
    {"display": "CH3", "algorithm": "Chamber 3", "label": "LARGE CHAMBER", "characteristics": "High density; low diffusion"},
    {"display": "CH4", "algorithm": "Chamber 4", "label": "PERCUSSION CHAMBER", "characteristics": "Medium density; high diffusion"},
    {"display": "PL1", "algorithm": "Plate 1", "label": "PERCUSSION PLATE", "characteristics": "High density; low diffusion"},
    {"display": "PL2", "algorithm": "Plate 2", "label": "TIGHT PLATE", "characteristics": "High density; medium diffusion"},
    {"display": "PL3", "algorithm": "Plate 3", "label": "SOFT PLATE", "characteristics": "Medium density; medium diffusion"},
    {"display": "PL4", "algorithm": "Plate 4", "label": "VOCAL PLATE", "characteristics": "Low density; high diffusion"},
    {"display": "gt1", "algorithm": "Gate 1", "label": "BRIGHT GATE", "characteristics": "High density; low diffusion"},
    {"display": "gt2", "algorithm": "Gate 2", "label": "POWER GATE", "characteristics": "Medium density; medium diffusion"},
    {"display": "rE1", "algorithm": "Reverse 1", "label": "MEDIUM REVERSE", "characteristics": "High density; low diffusion"},
    {"display": "rE2", "algorithm": "Reverse 2", "label": "SLOW REVERSE", "characteristics": "Low density; low diffusion"},
]

MODULATION_SOURCES = [
    {
        "name": "VOLUME PEDAL (#7)",
        "description": "The common volume pedal found on some electronic keyboards can be used as a modulation controller (MIDI Controller #7)."
    },
    {
        "name": "PITCH BEND",
        "description": "The pitch bend wheel or lever common on most synthesizers."
    },
    {
        "name": "MOD WHEEL (#1)",
        "description": "The Mod Wheel common on most synthesizers is designated Controller #1 in the MIDI specification."
    },
    {
        "name": "NOTE NUMBER",
        "description": "Any MIDI note from keyboard, sequencer, or drum machine."
    },
    {
        "name": "NOTE VELOCITY",
        "description": "The target parameter will change in relation to how hard a key is struck."
    },
    {
        "name": "AFTER TOUCH",
        "description": "After a note is depressed, a pressure on the key will cause a MIDI command."
    },
    {
        "name": "SUSTAIN PEDAL (#64)",
        "description": "The common sustain pedal found on most electronic keyboards can be used as a modulation controller."
    },
    {
        "name": "BREATH (#2)",
        "description": "The breath controller found on some electronic keyboards can be used as a modulation controller."
    }
]

MODULATION_DESTINATIONS = [
    {
        "name": "Off",
        "description": "No modulation."
    },
    {
        "name": "Reverb Decay",
        "description": "Length of time before the Reverb dies can be modulated."
    },
    {
        "name": "Delay Time",
        "description": "Length of time between repeats can be modulated"
    },
    {
        "name": "Delay Regeneration",
        "description": "Number of echo repeats can be modulated"
    },
    {
        "name": "Chorus Speed",
        "description": "How fast or slow the Chorus or Flange oscillates can be modulated"
    },
    {
        "name": "Reverb Level",
        "description": "The output of the Reverb can be remotely modulated"
    },
    {
        "name": "Delay Level",
        "description": "The output of the Delay can be remotely modulated"
    }
]
