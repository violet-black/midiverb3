import json
from dataclasses import dataclass, asdict
from pathlib import Path
from threading import Thread, Lock
from typing import Union, List, Sequence, Tuple
from queue import Queue
from time import sleep

import rtmidi
from PySide6.QtCore import QUrl, QSignalBlocker
from PySide6.QtWidgets import QMainWindow, QDialog, QFileDialog, QWidget, QComboBox, QMessageBox
from PySide6.QtGui import QDesktopServices

from mverb3.bank import BANK
from mverb3.ui.main import Ui_UIMainWindow
from mverb3.ui.settings import Ui_SETTINGS
from mverb3.ui.about import Ui_AboutDialog

__all__ = ["Program", "Bank", "Settings", "Device"]


def _load_value(byte_1: int, byte_2: int) -> int:
    return ((byte_2 & 7) << 7) | (byte_1 & 127)


def _dump_value(value: int) -> Tuple[int, int]:
    return value & 127, (value >> 7) & 7


def _trace_midi(send_message_f):

    def _wrap(message: Sequence[Union[bytes, int]], *args, **kws):
        print([hex(s) for s in message])
        return send_message_f(message, *args, **kws)

    return _wrap


class _SettingsDlg(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._ui = Ui_SETTINGS()
        self._ui.setupUi(self)


class _AboutDlg(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._ui = Ui_AboutDialog()
        self._ui.setupUi(self)


class _MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self._ui = Ui_UIMainWindow()
        self._ui.setupUi(self)


@dataclass
class Program:
    in_eq: int = 0
    out_eq: int = 0
    chrs_type: int = 0
    chrs_speed: int = 0
    dly_time: int = 0
    dly_regen: int = 0
    rev_type: int = 0
    rev_decay: int = 0
    rev_mix: int = 0
    dly_mix: int = 0
    mod_amount: int = 0
    mod_routing: int = 0
    configuration: int = 0


@dataclass
class Bank:
    programs: List[Program]
    edit_buffer: Program
    program_id: int


@dataclass
class Settings:
    midi_in_port: Union[str, None]
    midi_out_port: Union[str, None]
    midi_channel: int
    bank_path: str
    auto_send_buffer_on_prog_change: bool
    auto_send_prog_to_device_on_save: bool
    trace: bool


class Device:

    MANUFACTURER_ID = (0x0, 0x0, 0x0E)
    DEVICE_ID = 0x03
    PATH = Path("~/.mverb3").expanduser()
    SETTINGS = "settings.json"
    CURRENT_BANK = "bank.syx"
    PROG_NUM = 100
    REFRESH_RATE_MS = 100
    HELP_URL = "https://github.com/violet-black/midiverb3"

    PROG_MAP_TABLE = []
    for n in range(128):
        PROG_MAP_TABLE.extend(_dump_value(min(PROG_NUM + n, PROG_NUM * 2 - 1)))

    """
    Map presets 100-199 onto MIDI program numbers 0-99. This is required for two main reasons.
    
    - Presets below 100 are not editable anyways.
    - There are no 'banks' on the device, so you can't otherwise select editable presets using MIDI because of
    the max number of programs limitation (128).
    """

    _bank: Bank
    _settings: Settings

    def __init__(self, window: _MainWindow):
        self._window = window
        self._ui = window._ui
        self._midi_lock = Lock()
        self._queue = Queue()
        self._midi_thread: Thread = Thread(target=self._process_message_queue, args=(self._queue,), daemon=True)
        self._midi_in = rtmidi.MidiIn()
        self._midi_out = rtmidi.MidiOut()
        self.init()
        if self._settings.trace:
            self._send_message = _trace_midi(self._send_message)
        self._ui.actionNew.triggered.connect(self.open_bank_new_dlg)
        self._ui.actionBankSave.triggered.connect(self.save_current_bank)
        self._ui.actionImport.triggered.connect(self.open_file_import_dlg)
        self._ui.actionBankExport.triggered.connect(self.open_bank_export_dlg)
        self._ui.actionBufferExport.triggered.connect(self.open_program_export_dlg)
        self._ui.actionSettings.triggered.connect(self.open_settings_dlg)
        self._ui.actionHelp.triggered.connect(self.open_help)
        self._ui.actionAbout.triggered.connect(self.open_about_dlg)
        self._ui.actionQuit.triggered.connect(self.close)
        self._ui.actionStoreProgram.triggered.connect(self.save_buffer_to_device_program_slot)
        self._ui.actionDeviceStoreBank.triggered.connect(self.save_current_bank_to_device)
        self._ui.actionDeviceRequestBank.triggered.connect(self.request_bank_dump)
        self._ui.PROGRAM_ID.valueChanged.connect(self.on_program_change)
        self._ui.CONFIGURATION.currentIndexChanged.connect(self.on_configuration_change)
        self._ui.PROG_SYNC.clicked.connect(self.send_current_program_to_device_buffer)
        self._ui.PROG_RECALL.clicked.connect(self.recall_stored_program)
        self._ui.IN_EQ.valueChanged.connect(self.on_in_eq_change)
        self._ui.CHRS_TYPE.currentIndexChanged.connect(self.on_chrs_type_change)
        self._ui.CHRS_STEREO.stateChanged.connect(self.on_chrs_type_change)
        self._ui.CHRS_SPEED.valueChanged.connect(self.on_chrs_speed_change)
        self._ui.DLY_TIME.valueChanged.connect(self.on_dly_time_change)
        self._ui.DLY_REGEN.valueChanged.connect(self.on_dly_regen_change)
        self._ui.DLY_MIX.valueChanged.connect(self.on_dly_mix_change)
        self._ui.REVERB_TYPE.currentIndexChanged.connect(self.on_rev_type_change)
        self._ui.REV_DECAY.valueChanged.connect(self.on_rev_decay_change)
        self._ui.REV_MIX.valueChanged.connect(self.on_rev_mix_change)
        self._ui.OUT_EQ.valueChanged.connect(self.on_out_eq_change)
        self._ui.MOD_SOURCE.currentIndexChanged.connect(self.on_mod_source_dest_change)
        self._ui.MOD_DEST.currentIndexChanged.connect(self.on_mod_source_dest_change)
        self._ui.MOD_AMT.valueChanged.connect(self.on_mod_amount_change)

    def init(self) -> None:
        self.load_settings()
        self.open_midi_in()
        self.open_midi_out()
        if not Path(self._settings.bank_path).exists():
            self.init_bank(self.PATH / self.CURRENT_BANK)
        else:
            self.load_current_bank_from_file(self._settings.bank_path)
        self._midi_thread.start()
        self._clear_queue()

    def close(self) -> None:
        self._queue.join()
        self._midi_thread.join(timeout=1.0)
        with self._midi_lock:
            self._midi_in.close_port()
            self._midi_out.close_port()
            self._window.close()
        self.save_settings()
        self.dump_current_bank_to_file(self._settings.bank_path)

    def open_midi_in(self) -> None:
        if not self._settings.midi_in_port:
            return
        self._midi_in.close_port()
        ports = self._midi_in.get_ports()
        if self._settings.midi_in_port not in ports:
            return
        self._midi_in.open_port(ports.index(self._settings.midi_in_port))
        self._clear_queue()

    def open_midi_out(self) -> None:
        if not self._settings.midi_out_port:
            return
        self._midi_out.close_port()
        ports = self._midi_out.get_ports()
        if self._settings.midi_out_port not in ports:
            return
        self._midi_out.open_port(ports.index(self._settings.midi_out_port))
        self._clear_queue()

    def load_settings(self) -> None:
        _path = self.PATH / self.SETTINGS
        if not _path.exists():
            self._settings = Settings(
                midi_in_port=None,
                midi_out_port=None,
                midi_channel=0,
                bank_path=str(self.PATH / self.CURRENT_BANK),
                auto_send_buffer_on_prog_change=False,
                auto_send_prog_to_device_on_save=False,
                trace=False,
            )
            return
        with open(_path, "r") as f:
            data = json.loads(f.read())
            self._settings = Settings(
                midi_in_port=data.get("midi_in_port"),
                midi_out_port=data.get("midi_out_port"),
                midi_channel=data.get("midi_channel", 0),
                bank_path=data.get(
                    "bank_path", str(Path(self.PATH) / self.CURRENT_BANK)
                ),
                auto_send_buffer_on_prog_change=data.get(
                    "auto_send_buffer_on_prog_change", False
                ),
                auto_send_prog_to_device_on_save=data.get(
                    "auto_send_prog_to_device", False
                ),
                trace=data.get("trace", False),
            )

    def save_settings(self) -> None:
        _path = self.PATH / self.SETTINGS
        _path.parent.mkdir(parents=True, exist_ok=True)
        with open(_path, "w") as f:
            f.write(json.dumps(asdict(self._settings)))

    def init_bank(self, fp: Union[str, Path]) -> None:
        fp = Path(fp)
        fp.parent.mkdir(parents=True, exist_ok=True)
        with open(fp, "wb") as f:
            f.write(BANK)
        self._settings.bank_path = str(fp)
        self.load_current_bank_from_syx(BANK)

    def recall_stored_program(self) -> None:
        self._bank.edit_buffer = Program(
            **asdict(self._bank.programs[self._bank.program_id])
        )
        self.send_current_program_to_device_buffer()
        self.refresh_ui()

    def save_current_bank(self) -> None:
        self._bank.programs[self._bank.program_id] = Program(
            **asdict(self._bank.edit_buffer)
        )
        self.dump_current_bank_to_file(self._settings.bank_path)
        if self._settings.auto_send_prog_to_device_on_save:
            self.save_buffer_to_device_program_slot()

    def dump_current_bank_to_file(self, fp: Union[Path, str]) -> None:
        with open(fp, "wb") as f:
            f.write(bytes(self.dump_current_bank_to_syx()))

    def load_current_bank_from_file(self, fp: Union[Path, str]) -> None:
        with open(fp, "rb") as f:
            self.load_current_bank_from_syx(f.read())

    def dump_current_bank_to_syx(self) -> List[int]:
        """Dump the entire bank to a syx data dump.

        If sent to the device the whole bank will be written to EEPROM. It may take up to 10 sec! All programs will
        be also rewritten forever!
        """
        data = [0xF0, *self.MANUFACTURER_ID, self.DEVICE_ID, 0x00]
        data.extend(self.dump_bank_to_bin(self._bank))
        data.append(0xF7)
        return data

    def load_current_bank_from_syx(self, data: Sequence[int]) -> None:
        self._bank = self.load_bank_from_bin(data[6:-1])
        self._clear_queue()
        self.send_current_program_id_to_device()
        self.send_current_program_to_device_buffer()
        self.refresh_ui()

    def dump_bank_to_bin(self, bank: Bank) -> List[int]:
        data = []
        for prog in bank.programs:
            data.extend(self.dump_program_to_bin(prog))
        data.extend(self.dump_program_to_bin(bank.edit_buffer))
        data.extend(
            (
                *_dump_value(bank.program_id),  # selected program slot
                0, 0,  # edit buffer off
                0, 0,  # edit step off
                0, 0,  # midi echo off
                *_dump_value(self._settings.midi_channel),
                *_dump_value(1),  # program change enabled
            )
        )
        data.extend(self.PROG_MAP_TABLE)
        return data

    def load_bank_from_bin(self, data: Sequence[int]) -> Bank:
        offset, prog_size = 0, 32
        programs = []
        for n in range(self.PROG_NUM + 1):
            program = self.load_program_from_bin(data[offset : offset + prog_size])
            programs.append(program)
            offset += prog_size
        prog_num = _load_value(data[offset], data[offset + 1])
        bank = Bank(
            programs=programs[:-1], edit_buffer=programs[-1], program_id=prog_num
        )
        return bank

    def dump_current_program_to_file(self, file_path: Path) -> None:
        with open(file_path, "wb") as f:
            f.write(bytes(self.dump_program_to_syx()))

    def load_current_program_from_file(self, file_path: Path) -> None:
        with open(file_path, "rb") as f:
            self.load_current_program_from_syx(f.read())

    def load_current_program_from_syx(self, data: Sequence[int]) -> None:
        data = self.load_program_from_bin(data[7:-1])
        self._bank.edit_buffer = data
        self._clear_queue()
        self.send_current_program_to_device_buffer()
        self.refresh_ui()

    def dump_program_to_syx(self, program_id: int = PROG_NUM) -> List[int]:
        """Dump program to a syx file."""
        data = [
            0xF0,
            *self.MANUFACTURER_ID,
            self.DEVICE_ID,
            0x01,
            program_id,
            *self.dump_program_to_bin(self._bank.edit_buffer),
            0xF7,
        ]
        return data

    def dump_program_to_bin(self, program: Program) -> List[int]:
        return [
            *_dump_value(program.in_eq),
            *_dump_value(program.out_eq),
            *_dump_value(program.chrs_type),
            *_dump_value(program.chrs_speed),
            0,
            0,
            *_dump_value(program.dly_time),
            *_dump_value(program.dly_regen),
            *_dump_value(program.rev_type),
            *_dump_value(program.rev_decay),
            *_dump_value(program.rev_mix),
            *_dump_value(program.dly_mix),
            *_dump_value(program.configuration),
            *_dump_value(program.mod_routing),
            *_dump_value(program.mod_amount),
            0,
            0,
            0,
            0,
        ]

    def load_program_from_bin(self, data: Sequence[int]) -> Program:
        data = Program(
            in_eq=_load_value(data[0], data[1]),
            out_eq=_load_value(data[2], data[3]),
            chrs_type=_load_value(data[4], data[5]),
            chrs_speed=_load_value(data[6], data[7]),
            dly_time=_load_value(data[10], data[11]),
            dly_regen=_load_value(data[12], data[13]),
            rev_type=_load_value(data[14], data[15]),
            rev_decay=_load_value(data[16], data[17]),
            rev_mix=_load_value(data[18], data[19]),
            dly_mix=_load_value(data[20], data[21]),
            configuration=_load_value(data[22], data[23]),
            mod_routing=_load_value(data[24], data[25]),
            mod_amount=_load_value(data[26], data[27]),
        )
        return data

    def open_file_import_dlg(self, *_) -> None:
        dlg = QFileDialog(self._window)
        dlg.setDefaultSuffix(".syx")
        dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptOpen)
        if dlg.exec():
            fp = Path(dlg.selectedFiles()[0])
            with open(fp, "rb") as f:
                data = f.read()
                if data[:6] == bytes(
                    [0xF0, *self.MANUFACTURER_ID, self.DEVICE_ID, 0x00]
                ):
                    self.load_current_bank_from_syx(data)
                elif data[:6] == bytes(
                    [0xF0, *self.MANUFACTURER_ID, self.DEVICE_ID, 0x01]
                ):
                    self.load_current_program_from_syx(data)
                else:
                    box = QMessageBox()
                    box.setText('Unsupported file format')
                    box.setInformativeText(
                        'Only MidiVerb III sysex banks or programs with the proper device id are supported. '
                        'Are you sure you are trying to open a MidiVerb III file?')
                    box.exec_()

    def open_program_export_dlg(self, *_) -> None:
        dlg = QFileDialog(self._window)
        dlg.setDefaultSuffix(".syx")
        dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        if dlg.exec():
            fp = Path(dlg.selectedFiles()[0])
            self.dump_current_program_to_file(fp)

    def open_bank_new_dlg(self, *_) -> None:
        dlg = QFileDialog(self._window)
        dlg.setDefaultSuffix(".syx")
        dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        if dlg.exec():
            fp = Path(dlg.selectedFiles()[0])
            self.init_bank(fp)

    def open_bank_export_dlg(self, *_) -> None:
        dlg = QFileDialog(self._window)
        dlg.setDefaultSuffix(".syx")
        dlg.setAcceptMode(QFileDialog.AcceptMode.AcceptSave)
        if dlg.exec():
            fp = Path(dlg.selectedFiles()[0])
            self.dump_current_bank_to_file(fp)

    def open_settings_dlg(self, *_) -> None:

        def _set_port(
            conn: Union[rtmidi.MidiIn, rtmidi.MidiOut],
            widget: QComboBox,
            port_name: str,
        ) -> int:
            ports_available = ["NONE", *conn.get_ports()]
            port_id = 0
            if port_name in ports_available:
                port_id = ports_available.index(port_name)
            widget.addItems(list(ports_available))
            widget.setCurrentIndex(port_id)
            return port_id

        dlg = _SettingsDlg(self._window)
        dlg._ui.SETTINGS_DIAG.accepted.connect(dlg.accept)
        dlg._ui.SETTINGS_DIAG.rejected.connect(dlg.reject)
        port_in_id = _set_port(
            self._midi_in, dlg._ui.PORT_IN, self._settings.midi_in_port
        )
        port_out_id = _set_port(
            self._midi_out, dlg._ui.PORT_OUT, self._settings.midi_out_port
        )
        dlg._ui.CHANNEL.setValue(self._settings.midi_channel + 1)
        dlg._ui.OPT_SEND_BUFFER.setChecked(
            self._settings.auto_send_buffer_on_prog_change
        )
        dlg._ui.OPT_DUMP_SAVE.setChecked(
            self._settings.auto_send_prog_to_device_on_save
        )
        if dlg.exec():
            self._settings.midi_channel = dlg._ui.CHANNEL.value() - 1
            self._settings.auto_send_buffer_on_prog_change = (
                dlg._ui.OPT_SEND_BUFFER.isChecked()
            )
            self._settings.auto_send_prog_to_device_on_save = (
                dlg._ui.OPT_DUMP_SAVE.isChecked()
            )
            if port_in_id != dlg._ui.PORT_IN.currentIndex():
                self._settings.midi_in_port = dlg._ui.PORT_IN.currentText()
                self.open_midi_in()
            if port_out_id != dlg._ui.PORT_OUT.currentIndex():
                self._settings.midi_out_port = dlg._ui.PORT_OUT.currentText()
                self.open_midi_out()

    def open_about_dlg(self, *_) -> None:
        dlg = _AboutDlg(self._window)
        dlg.exec()

    def open_help(self) -> None:
        QDesktopServices.openUrl(QUrl(self.HELP_URL))

    def on_in_eq_change(self, *_) -> None:
        value = self._ui.IN_EQ.value()
        self._ui.IN_EQ_L.setText(str(value))
        self._bank.edit_buffer.in_eq = value
        self._queue.put_nowait((0, value))

    def on_out_eq_change(self, *_) -> None:
        value = self._ui.OUT_EQ.value()
        self._ui.OUT_EQ_L.setText(str(value))
        self._bank.edit_buffer.out_eq = value
        self._queue.put_nowait((1, value))

    def on_chrs_type_change(self, *_) -> None:
        value = self._ui.CHRS_TYPE.currentIndex()
        modifier = self._ui.CHRS_STEREO.isChecked()
        value = value * 2 + modifier
        self._bank.edit_buffer.chrs_type = value
        self._queue.put_nowait((2, value))

    def on_chrs_speed_change(self, *_) -> None:
        value = self._ui.CHRS_SPEED.value()
        self._ui.CHRS_SPEED_L.setText(str(value))
        self._bank.edit_buffer.chrs_speed = value
        self._queue.put_nowait((3, value))

    def on_dly_time_change(self, *_) -> None:
        value = self._ui.DLY_TIME.value()
        self._ui.DLY_TIME_L.setText(str(value))
        self._bank.edit_buffer.dly_time = value
        self._queue.put_nowait((4, value))

    def on_dly_regen_change(self, *_) -> None:
        value = self._ui.DLY_REGEN.value()
        self._ui.DLY_REGEN_L.setText(str(value))
        self._bank.edit_buffer.dly_regen = value
        self._queue.put_nowait((5, value))

    def on_rev_type_change(self, *_) -> None:
        value = self._ui.REVERB_TYPE.currentIndex()
        self._bank.edit_buffer.rev_type = value
        self._queue.put_nowait((6, value))

    def on_rev_decay_change(self, *_) -> None:
        value = self._ui.REV_DECAY.value()
        self._ui.REV_DECAY_L.setText(str(value))
        self._bank.edit_buffer.rev_decay = value
        self._queue.put_nowait((7, value))

    def on_rev_mix_change(self, *_) -> None:
        value = self._ui.REV_MIX.value()
        self._ui.REV_MIX_L.setText(str(value))
        self._bank.edit_buffer.rev_mix = value
        self._queue.put_nowait((8, value))

    def on_dly_mix_change(self, *_) -> None:
        value = self._ui.DLY_MIX.value()
        self._ui.DLY_MIX_L.setText(str(value))
        self._bank.edit_buffer.dly_mix = value
        self._queue.put_nowait((9, value))

    def on_configuration_change(self, *_) -> None:
        value = self._ui.CONFIGURATION.currentIndex()
        if value == 13 or value == 14:
            self._ui.DLY_TIME.setMaximum(490)
        else:
            self._ui.DLY_TIME.setMaximum(100)
            self._ui.DLY_TIME.setValue(min(self._ui.DLY_TIME.value(), 490))
        self._bank.edit_buffer.configuration = value
        self._queue.put_nowait((10, value))

    def on_mod_source_dest_change(self, *_) -> None:
        value = self._ui.MOD_SOURCE.currentIndex()
        modifier = self._ui.MOD_DEST.currentIndex()
        if modifier == 0:
            # OFF switch
            value = 0
        else:
            # for CC7 (source id == 0) every destination starts from 1
            # because 0 0 is reserved for MOD OFF
            # for every other source destination starts from 0
            # since in the menu the first selectable is OFF we must
            # decrement index by 1 for each source except CC7
            if value != 0:
                modifier -= 1
            value = modifier * 8 + value
        self._bank.edit_buffer.mod_routing = value
        self._queue.put_nowait((11, value))

    def on_mod_amount_change(self, *_) -> None:
        value = self._ui.MOD_AMT.value()
        self._ui.MOD_AMT_L.setText(str(value - 99))
        self._bank.edit_buffer.mod_amount = value
        self._queue.put_nowait((12, value))

    def on_program_change(self, *_) -> None:
        value = self._ui.PROGRAM_ID.value()
        self._bank.program_id = value - self.PROG_NUM
        self._bank.edit_buffer = Program(
            **asdict(self._bank.programs[self._bank.program_id])
        )
        self.send_current_program_id_to_device()
        if self._settings.auto_send_buffer_on_prog_change:
            self.send_current_program_to_device_buffer()
        self.refresh_ui()

    def refresh_ui(self) -> None:
        blockers = [
            QSignalBlocker(widget) for widget in self._window.findChildren(QWidget)
        ]
        self._ui.IN_EQ.setValue(self._bank.edit_buffer.in_eq)
        self._ui.IN_EQ_L.setText(str(self._bank.edit_buffer.in_eq))
        self._ui.OUT_EQ.setValue(self._bank.edit_buffer.out_eq)
        self._ui.OUT_EQ_L.setText(str(self._bank.edit_buffer.out_eq))
        self._ui.CHRS_TYPE.setCurrentIndex(self._bank.edit_buffer.chrs_type // 2)
        self._ui.CHRS_STEREO.setChecked(self._bank.edit_buffer.chrs_type % 2)
        self._ui.CHRS_SPEED.setValue(self._bank.edit_buffer.chrs_speed)
        self._ui.CHRS_SPEED_L.setText(str(self._bank.edit_buffer.chrs_speed))
        self._ui.DLY_TIME.setValue(self._bank.edit_buffer.dly_time)
        self._ui.DLY_TIME_L.setText(str(self._bank.edit_buffer.dly_time))
        self._ui.DLY_REGEN.setValue(self._bank.edit_buffer.dly_regen)
        self._ui.DLY_REGEN_L.setText(str(self._bank.edit_buffer.dly_regen))
        self._ui.DLY_MIX.setValue(self._bank.edit_buffer.dly_mix)
        self._ui.DLY_MIX_L.setText(str(self._bank.edit_buffer.dly_mix))
        self._ui.REV_DECAY.setValue(self._bank.edit_buffer.rev_decay)
        self._ui.REV_DECAY_L.setText(str(self._bank.edit_buffer.rev_decay))
        self._ui.REV_MIX.setValue(self._bank.edit_buffer.rev_mix)
        self._ui.REV_MIX_L.setText(str(self._bank.edit_buffer.rev_mix))
        self._ui.REVERB_TYPE.setCurrentIndex(self._bank.edit_buffer.rev_type)
        self._ui.MOD_AMT.setValue(self._bank.edit_buffer.mod_amount)
        self._ui.MOD_AMT_L.setText(str(self._bank.edit_buffer.mod_amount - 99))
        if self._bank.edit_buffer.mod_routing == 0:
            # OFF
            self._ui.MOD_SOURCE.setCurrentIndex(0)
            self._ui.MOD_DEST.setCurrentIndex(0)
        elif self._bank.edit_buffer.mod_routing % 8 == 0:
            # CC7
            self._ui.MOD_SOURCE.setCurrentIndex(0)
            self._ui.MOD_DEST.setCurrentIndex(self._bank.edit_buffer.mod_routing // 8)
        else:
            self._ui.MOD_SOURCE.setCurrentIndex(self._bank.edit_buffer.mod_routing % 8)
            self._ui.MOD_DEST.setCurrentIndex(
                self._bank.edit_buffer.mod_routing // 8 + 1
            )
        self._ui.CONFIGURATION.setCurrentIndex(self._bank.edit_buffer.configuration)
        self._ui.PROGRAM_ID.setValue(self._bank.program_id + self.PROG_NUM)
        self._ui.BANK_PATH.setText(self._settings.bank_path)
        blockers.clear()

    def send_current_program_id_to_device(self) -> None:
        with self._midi_lock:
            self._send_message(
                (0xC0 + self._settings.midi_channel, self._bank.program_id)
            )
            sleep(0.33)

    def send_current_program_to_device_buffer(self) -> None:
        with self._midi_lock:
            self._send_message(self.dump_program_to_syx(self.PROG_NUM))
            sleep(0.33)  # service guide recommended timeout

    def save_buffer_to_device_program_slot(self) -> None:
        with self._midi_lock:
            self._send_message(self.dump_program_to_syx(self._bank.program_id))

    def save_current_bank_to_device(self) -> None:
        with self._midi_lock:
            self._send_message(
                (
                    0xF0,
                    *self.MANUFACTURER_ID,
                    self.DEVICE_ID,
                    0x00,
                    *self.dump_bank_to_bin(self._bank),
                    0xF7,
                )
            )
            sleep(10)  # service guide recommended timeout

    def request_bank_dump(self) -> None:
        self._midi_in.ignore_types(sysex=False)
        with self._midi_lock:
            self._send_message(
                (
                    0xF0,
                    *self.MANUFACTURER_ID,
                    self.DEVICE_ID,
                    0x02,
                    0xF7,
                )
            )
        timeout, data = 0, None
        while timeout < 10:
            data = self._midi_in.get_message()
            if data and len(data[0]) > 500:  # hack to ignore possible short 'midi echo' messages
                self.load_current_bank_from_syx(data[0])
                self.save_current_bank_to_device()
                break
            timeout += 1
            sleep(1)
        else:
            box = QMessageBox()
            box.setText('Bank receive timeout')
            box.setInformativeText(
                'The bank has not been received.'
                'Check that both your MidiVerb III unit MIDI In and Out are connected to the MIDI interface, '
                'and that the proper MIDI ports and the channel are provided in the application settings.')
            box.exec_()

    def _process_message_queue(self, queue: Queue) -> None:
        """Send data to the device.

        Send interval `midi_refresh_rate_ms` is set in app settings. Messages are deduplicated — only the last
        message for each param is sent.
        """
        data = {}
        header = (0xF0, *self.MANUFACTURER_ID, self.DEVICE_ID, 0x03)
        while True:
            if not queue.empty():
                for _ in range(queue.qsize()):
                    param_id, value = queue.get_nowait()
                    queue.task_done()
                    data[param_id] = value
                if data:
                    with self._midi_lock:
                        for param_id, value in data.items():
                            self._send_message(
                                [*header, param_id, *_dump_value(value), 0xF7]
                            )
                            sleep(0.05)  # service guide recommended timeout
                data.clear()
            sleep(0.05)

    def _send_message(self, message: Sequence[Union[bytes, int]]) -> None:
        if self._midi_out:
            return self._midi_out.send_message(message)

    def _clear_queue(self) -> None:
        for _ in range(self._queue.qsize()):
            param_id, value = self._queue.get_nowait()
            self._queue.task_done()
