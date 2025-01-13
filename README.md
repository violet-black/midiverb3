# MidiVerb 3

Patch editor for the [Alesis Midiverb III](https://www.vintagedigital.com.au/alesis-midiverb-iii/) hardware FX unit.

![Screenshot](/resources/screenshot.png?raw=true)

- [INSTALLATION](#Installation)
- [CONFIGURATION](#configuration)
- [USAGE](#usage)
- [MENU REFERENCE](#menu-reference)
- [PATCH REFERENCE](#patch-reference)
- [ROUTING](#routing)
- [MIDIVERB TIPS](#midiverb-tips)
- [TROUBLESHOOTING](#troubleshooting)

## Installation

Go to the [release page](https://github.com/violet-black/midiverb3/releases) and download the binary for your OS.

It may require permissions to access the user directory, since the app stores its settings in `.mverb3`
hidden folder inside the user directory.

Alternatively there's a [Python package](https://pypi.org/project/midiverb3/) available, which can be installed via
pip and run by executing `midiverb3` command in the terminal (or alternatively `python3 -m midiverb3`).
The app uses [pySide6](https://doc.qt.io/qtforpython-6/) Qt binding for the GUI.

## Configuration

1. Be sure that the MidiVerb is on and both MIDI in and MIDI out are plugged in.

2. Start the app, open `File/Settings` (or `midiverb3/Preferences` on Mac). Set MIDI in and MIDI out
   to the MidiVerb ports. Click OK.

3. Go to `Device/Request Bank` menu. The MidiVerb will now dump its current bank to the app.
   Then the bank will be sent back to the device. This operation may take up to 20 seconds. Once finished,
   you won't need to do it again or even use the device MIDI output.

4. Try to switch programs from the app to verify that the device is reacting to it.

## Usage

The easiest way to work with the app is to tweak sliders in the UI, then click `File/Save Single` and save the buffer
to a sysex file. Once you need it again, you can `File/Open` it. This will also automatically send the data to
the MidiVerb buffer.

This type of workflow doesn't require either storing data in a bank or saving it to the device program  memory.

Alternatively you can duplicate the current bank by using `File/Save As`. Go to the settings and click
`Send buffer to device on prog change` checkbox. Now you can work with your bank, change presets, and they will be
automatically sent to the MidiVerb buffer. I.e. the bank itself is stored entirely on your computer, but the sliders
and switches are synchronized with the device. This way you can manage multiple banks at once by switching them using
`File/Open`.

If you actually need to store programs on the device, use `Device/Store Program` or `Device/Store Bank`. MidiVerb 3
can store only one bank and 100 user programs (slots 100-199).

## Menu Reference

### File/New

Create a new bank from the default template and open it.
The action will NOT automatically sync the bank to the device.

### File/Open

Open a bank or a single program in the sysex format from a file. This way you can import banks and programs.
The action will NOT automatically sync the bank to the device.

### File/Save

Save the current bank changes on the computer. The buffer is saved to the currently selected program slot.
The action will NOT automatically sync the bank to the device.

### File/Save As

Copy the current bank to another location on the computer. You can use this for backups.
The action will NOT automatically sync the bank to the device.

### File/Save Single

Save a content of the buffer to a sysex file.
The action will NOT automatically sync the bank to the device.

### Device/Store Program

Store the current buffer in the selected program slot *in the device memory*. 

### Device/Store Bank

Send the whole bank to the device. This operation may take up to 10 seconds.
CAUTION: This operation will overwrite all the device data.

### Device/Request Bank

Request the whole bank from the device.
CAUTION: This operation will overwrite all the bank data on the computer.

## Patch reference

### LPF

Input EQ which is actually a lowpass filter.

### CHORUS

Select a chorus or flanger algorithm. Letters `XS` to `XL` indicate the depth of the effect. The slider indicates
the rate (speed) of the effect.

### DELAY

The delay parameters. The `time` is in milliseconds. `Regen` is the feedback level. `Level` indicates how much of the
delay is routed to the mix.

### REVERB

`Decay` is the reverb decay, `Level` indicates how much of the reverb is routed to the mix. `ALGORITHM` allows you to
select the reverb algorithm.

### LPF

Another lowpass filter may be either delay or reverb feedback signal filter depending on the algorithm.

### MODULATION

You can select the source and the destination for the MIDI modulation of one of the delay parameter (yes, only one).
The modulation itself can be kinda glitchy, so I'd recommend limiting the rate of MIDI messages and use mono mode
if using the note number or velocity modulation. The slider indicates the depth of the modulation.

### SYNC

Send current buffer (GUI values) to the device. To do this automatically on program switch you can set
`Send buffer to device on prog change` flag in the app settings. By default on program change the device retains its
stored program.

### RECALL

Discard the edit buffer and revert to the program stored in the local bank (not on the device).

## Routing

Although not ideal, there's a certain notation for the internal routing in the algorithm select menu. You may try to
get familiar with it or just tweak by ear.

- `LP` - input lowpass filter (*EQ* in the manual)
- `CHS` - chorus or flanger
- `DLY` - standard delay up to 100ms
- `XDLY` - extended delay up to 500ms
- `REV` - reverb
- `>` - section routed to another, for example `CHS > DLY` means *chorus routed to reverb*
- `( )` - section is not mixed to the output bus, for example `(LP)` means that the lowpass filtered signal,
   although routed somewhere, is not *directly* mixed to the output. Note that both delay and reverb may be routed to
   the mix bus, but their level may be set to zero. The chorus doesn't have a separate level parameter, so it's eiter
   all or nothing.
- `|` - parallel routing, for example `CHS > DLY | CHS > REV` means *chorus routed to the reverb and to the delay in parallel*

Examples:

`(LP)  >  CHS  >  DLY  |  (LP)  >  CHS  >  REV`

*Lowpass filter is routed to the chorus which routed to the delay. Also in parallel lowpass filter is routed to the chorus
which is routed to the reverb. Lowpass filter is not mixed to the output.*

`(LP)  >  (CHS)  >  XDLY`

*Lowpass filter is routed to the chorus which is routed to the extended delay.
Both the lowpass filter and the chorus are not routed to the mix bus, but delay is.*

## MidiVerb Tips

Route your piano or another keyboard to the delay input in your DAW and apply note number modulation to the delay time.
It will create 'random' glitchy echoes when played.

Alternatively try using negative reverb level / decay modulation on note velocity to create a glitchy 'compression' effect.

Use routing algorithms with extended delay (XDLY) to get delay time longer than 100ms.

Overload the input to produce ugly lo-fi digital distortion.

## Troubleshooting

### Will the app work with Midiverb I / II?

I don't have one, so I don't know. Probably it won't. I wouldn't recommend that.

### Unable to select programs below 100

This is intentional, because there's no way to edit factory programs anyways and there are only 127 possible MIDI program
numbers. On bank import the app will remap all program slots to presets 100-199
to be able to navigate between them using MIDI program change messages.

### Presets are not saved on the device

By default, the app is configured such way that it uses the internal memory as less as possible (who knows how many
writes it can withstand). The idea is that you load your device bank in the computer, and then you operate locally
only sending changes to the device buffer while you are using it.

You can press `Device/Store Program` button to actually save the program in the selected program slot.

### The app doesn't start anymore

Go to your user folder, locate and delete `mverb3/` directory. This will reset the app to its default settings.

### App doesn't switch programs etc

Check that the `program change` option is enabled on your MidiVerb unit.

### There's lag between switching programs or other operations

It's by design. The official MidiVerb service guide says that the device requires at least 40 ms in between messages.
It's a very old hardware after all, and midi processing speed is pretty limited, so some lags should be expected.

### The device produces pops / clicks when using MIDI modulators

Well, it's an old hardware with 3 MIPS CPU so what can you do? It's a miracle that it even works. For such values as
note number modulation or velocity modulation I'd suggest using mono note input. Note number modulation of the delay time
can provide quite interesting results when used carefully.

Cheers.
