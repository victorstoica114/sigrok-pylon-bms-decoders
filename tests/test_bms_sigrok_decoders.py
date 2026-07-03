import importlib
import importlib.util
import sys
import types
from pathlib import Path


DECODERS_DIR = Path(__file__).resolve().parents[1] / "decoders"
GROWATT_CAN_DECODER_DIR = DECODERS_DIR / "growatt_can"
GROWATT_RS485_DECODER_DIR = DECODERS_DIR / "growatt_rs485"
JKBMS_MODBUS_DECODER_DIR = DECODERS_DIR / "jkbms_modbus"
JKBMS_CAN_DECODER_DIR = DECODERS_DIR / "jkbms_can"
PULSEVIEW_DECODER_DIR = Path(r"C:\Program Files\sigrok\PulseView\share\libsigrokdecode\decoders")
PULSEVIEW_SRD_DIR = Path(r"C:\Program Files\sigrok\PulseView\share\libsigrokdecode")


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


growatt_rs485 = load_module("growatt_rs485_helper", GROWATT_RS485_DECODER_DIR / "growatt.py")
growatt_can = load_module("growatt_can_helper", GROWATT_CAN_DECODER_DIR / "growatt_can.py")
jkbms = load_module("jkbms_modbus_helper", JKBMS_MODBUS_DECODER_DIR / "jkbms_modbus.py")
jkbms_can = load_module("jkbms_can_helper", JKBMS_CAN_DECODER_DIR / "jkbms_can.py")


def with_modbus_crc(body, crc_func=growatt_rs485.modbus_crc16):
    body = list(body)
    crc = crc_func(body)
    return bytes(body + [crc & 0xFF, (crc >> 8) & 0xFF])


def words_to_bytes(words):
    data = []
    for word in words:
        data.extend([(word >> 8) & 0xFF, word & 0xFF])
    return data


def test_active_decoder_folders_are_validated_only():
    decoder_names = sorted(path.name for path in DECODERS_DIR.iterdir() if path.is_dir())

    assert decoder_names == ["growatt_can", "growatt_rs485", "jkbms_can", "jkbms_modbus"]


def test_growatt_rs485_parses_modbus_request_and_response():
    request = growatt_rs485.parse_frame(
        with_modbus_crc([0x01, 0x03, 0x00, 0x13, 0x00, 0x08])
    )
    response = growatt_rs485.parse_frame(
        with_modbus_crc([
            0x01, 0x03, 0x10,
            0x00, 0x02,
            0x00, 0x00,
            0x00, 0x63,
            0x16, 0x53,
            0x00, 0x00,
            0x00, 0xE8,
            0x00, 0x00,
            0x00, 0x00,
        ]),
        request,
    )

    assert request["crc_ok"]
    assert response["crc_ok"]
    assert response["registers"][0]["addr"] == 0x0013
    assert response["registers"][-1]["addr"] == 0x001A
    assert "response regs 0x0013..0x001A" in growatt_rs485.describe_frame(response)
    assert "SOC=99%" in growatt_rs485.describe_frame(response)
    assert "pack_v=57.15V" in growatt_rs485.describe_frame(response)


def test_growatt_can_describes_live_frames():
    packet_313 = ("standard", 0x313, "data", 8, [0x16, 0x53, 0x00, 0x00, 0x00, 0xE8, 0x63, 0x64])
    packet_319 = ("standard", 0x319, "data", 8, [0xC0, 0x0D, 0xF4, 0x0D, 0xF3, 0x05, 0x09, 0x00])
    packet_322 = ("standard", 0x322, "data", 8, [0x00, 0xE6, 0x00, 0xE6, 0x01, 0x01, 0x63, 0x63])

    assert "0x313 pack V=57.15V" in growatt_can.describe_packet(packet_313)
    assert "SOC=99%" in growatt_can.describe_packet(packet_313)
    assert "cell_max=3.572V#5" in growatt_can.describe_packet(packet_319)
    assert "cell_min=3.571V#9" in growatt_can.describe_packet(packet_319)
    assert "0x322 Tmax=23.0C#1" in growatt_can.describe_packet(packet_322)
    assert "Growatt CAN 0x319" in growatt_can.frame_summary(packet_319)


def test_jkbms_can_describes_live_frames_and_extended_cells():
    status = ("extended", 0x02F4, "data", 8, [0xD7, 0x02, 0xA0, 0x0F, 80, 0, 100, 0])
    extremes = ("extended", 0x04F4, "data", 8, [0x0A, 0x12, 3, 0x7C, 0x11, 12, 0, 0])
    cell25 = ("extended", 0x18E628F4, "data", 8, [0xF2, 0x0D, 0xF3, 0x0D, 0xF4, 0x0D, 0xF5, 0x0D])

    assert "V=72.7V" in jkbms_can.describe_packet(status)
    assert "I=+0.0A" in jkbms_can.describe_packet(status)
    assert "SOC=80%" in jkbms_can.describe_packet(status)
    assert "cell_max=4.618V#3" in jkbms_can.describe_packet(extremes)
    assert "cell_min=4.476V#12" in jkbms_can.describe_packet(extremes)
    decoded_cells = jkbms_can.describe_packet(cell25)
    assert "C25=3.570V" in decoded_cells
    assert "C26" not in decoded_cells


def test_jkbms_can_describes_capacity_temperatures_and_charge_info():
    capacity = ("extended", 0x18F128F4, "data", 8, [0xF4, 0x01, 0x80, 0x02, 0x00, 0x00, 0x40, 0x00])
    temps = ("extended", 0x18F228F4, "data", 8, [0x1F, 76, 77, 79, 75, 78, 0, 0])
    charge = ("extended", 0x1806E5F4, "data", 8, [0x40, 0x02, 0xF4, 0x01, 0, 0, 0, 0])

    assert "remain=50.0Ah" in jkbms_can.describe_packet(capacity)
    assert "cycles=64" in jkbms_can.describe_packet(capacity)
    assert "T1=26.0C" in jkbms_can.describe_packet(temps)
    assert "T5=28.0C" in jkbms_can.describe_packet(temps)
    assert "charge info V=57.6V I=50.0A" in jkbms_can.describe_packet(charge)


def test_jkbms_modbus_parses_runtime_voltage_and_current_response():
    request = jkbms.parse_frame(
        with_modbus_crc([0x01, 0x03, 0x12, 0x90, 0x00, 0x0A], jkbms.modbus_crc16)
    )
    response_words = [
        0x0000, 0xDF36,
        0x0000, 0x0000,
        0x0000, 0x3039,
        0x0000, 0x0000,
        0xFFFF, 0xF830,
    ]
    response = jkbms.parse_frame(
        with_modbus_crc([0x01, 0x03, 0x14] + words_to_bytes(response_words), jkbms.modbus_crc16),
        request,
    )
    decoded = jkbms.describe_frame(response)

    assert request["crc_ok"]
    assert response["crc_ok"]
    assert response["registers"][0]["addr"] == 0x1290
    assert response["registers"][-1]["addr"] == 0x1299
    assert "response regs 0x1290..0x1299" in decoded
    assert "pack_v=57.142V" in decoded
    assert "pack_i=-2.000A" in decoded


def test_jkbms_modbus_describes_runtime_register_map_values():
    assert (0x1200, 0x0010) in jkbms.POLL_BLOCKS
    assert (0x128A, 0x0028) in jkbms.POLL_BLOCKS
    assert "cell01=3.572V" in jkbms.describe_register(0x1200, 0x0DF4)
    assert jkbms.describe_register(0x1246, 12) == "cell_diff=12mV"
    assert jkbms.describe_register(0x1248, 0x0509) == "cell_idx max#5 min#9"


def test_sigrok_growatt_rs485_package_exports_decoder(monkeypatch):
    stub_sigrokdecode = types.SimpleNamespace(Decoder=object, OUTPUT_ANN=1)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("growatt_rs485", "growatt_rs485.pd", "growatt_rs485.growatt"):
        sys.modules.pop(name, None)

    module = importlib.import_module("growatt_rs485")

    assert module.Decoder.id == "growatt_rs485"
    assert module.Decoder.inputs == ["uart"]
    assert any(option["id"] == "inter_frame_gap_us" for option in module.Decoder.options)


def test_sigrok_growatt_can_package_exports_decoder(monkeypatch):
    stub_sigrokdecode = types.SimpleNamespace(Decoder=object, OUTPUT_ANN=1, OUTPUT_PYTHON=2)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(PULSEVIEW_SRD_DIR))
    sys.path.insert(0, str(PULSEVIEW_DECODER_DIR))
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("can", "can.pd", "growatt_can", "growatt_can.pd", "growatt_can.growatt_can"):
        sys.modules.pop(name, None)

    module = importlib.import_module("growatt_can")

    assert module.Decoder.id == "growatt_can"
    assert module.Decoder.inputs == ["logic"]
    assert any(option["id"] == "input_mode" for option in module.Decoder.options)


def test_sigrok_growatt_can_decoder_derives_bus_level_from_raw_can_lines(monkeypatch):
    stub_sigrokdecode = types.SimpleNamespace(Decoder=object, OUTPUT_ANN=1, OUTPUT_PYTHON=2)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(PULSEVIEW_SRD_DIR))
    sys.path.insert(0, str(PULSEVIEW_DECODER_DIR))
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("can", "can.pd", "growatt_can", "growatt_can.pd", "growatt_can.growatt_can"):
        sys.modules.pop(name, None)

    module = importlib.import_module("growatt_can")
    decoder = module.Decoder()

    decoder.options = {"input_mode": "rx/canl-direct"}
    assert decoder.derive_can_rx(1) == 1
    assert decoder.derive_can_rx(0) == 0

    decoder.options = {"input_mode": "canh-inverted"}
    assert decoder.derive_can_rx(0) == 1
    assert decoder.derive_can_rx(1) == 0

    decoder.options = {"input_mode": "canh-canl-diff"}
    assert decoder.derive_can_rx(1, 0) == 0
    assert decoder.derive_can_rx(0, 1) == 1
    assert decoder.derive_can_rx(1, 1) == 1


def test_sigrok_jkbms_can_package_exports_decoder(monkeypatch):
    stub_sigrokdecode = types.SimpleNamespace(Decoder=object, OUTPUT_ANN=1, OUTPUT_PYTHON=2)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(PULSEVIEW_SRD_DIR))
    sys.path.insert(0, str(PULSEVIEW_DECODER_DIR))
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("can", "can.pd", "jkbms_can", "jkbms_can.pd", "jkbms_can.jkbms_can"):
        sys.modules.pop(name, None)

    module = importlib.import_module("jkbms_can")

    assert module.Decoder.id == "jkbms_can"
    assert module.Decoder.inputs == ["logic"]
    assert jkbms_can.DECODER_VERSION in module.Decoder.name
    assert any(option["id"] == "input_mode" for option in module.Decoder.options)


def test_sigrok_jkbms_can_decoder_derives_bus_level_from_raw_can_lines(monkeypatch):
    stub_sigrokdecode = types.SimpleNamespace(Decoder=object, OUTPUT_ANN=1, OUTPUT_PYTHON=2)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(PULSEVIEW_SRD_DIR))
    sys.path.insert(0, str(PULSEVIEW_DECODER_DIR))
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("can", "can.pd", "jkbms_can", "jkbms_can.pd", "jkbms_can.jkbms_can"):
        sys.modules.pop(name, None)

    module = importlib.import_module("jkbms_can")
    decoder = module.Decoder()

    decoder.options = {"input_mode": "rx/canl-direct"}
    assert decoder.derive_can_rx(1) == 1
    assert decoder.derive_can_rx(0) == 0

    decoder.options = {"input_mode": "canh-inverted"}
    assert decoder.derive_can_rx(0) == 1
    assert decoder.derive_can_rx(1) == 0

    decoder.options = {"input_mode": "canh-canl-diff"}
    assert decoder.derive_can_rx(1, 0) == 0
    assert decoder.derive_can_rx(0, 1) == 1
    assert decoder.derive_can_rx(1, 1) == 1


def test_sigrok_jkbms_modbus_package_exports_decoder(monkeypatch):
    stub_sigrokdecode = types.SimpleNamespace(Decoder=object, OUTPUT_ANN=1)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("jkbms_modbus", "jkbms_modbus.pd", "jkbms_modbus.jkbms_modbus"):
        sys.modules.pop(name, None)

    module = importlib.import_module("jkbms_modbus")

    assert module.Decoder.id == "jkbms_modbus"
    assert module.Decoder.inputs == ["uart"]
    assert any(option["id"] == "inter_frame_gap_us" for option in module.Decoder.options)


def test_sigrok_jkbms_modbus_decoder_emits_annotations_for_uart_frames(monkeypatch):
    class FakeSrdDecoder:
        def register(self, output):
            return output

        def put(self, ss, es, output, data):
            self.captured.append((ss, es, output, data))

    stub_sigrokdecode = types.SimpleNamespace(Decoder=FakeSrdDecoder, OUTPUT_ANN=1)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("jkbms_modbus", "jkbms_modbus.pd", "jkbms_modbus.jkbms_modbus"):
        sys.modules.pop(name, None)

    module = importlib.import_module("jkbms_modbus")
    decoder = module.Decoder()
    decoder.captured = []
    decoder.start()

    request = with_modbus_crc([0x01, 0x03, 0x12, 0x90, 0x00, 0x02], jkbms.modbus_crc16)
    response = with_modbus_crc([0x01, 0x03, 0x04, 0x00, 0x00, 0xDF, 0x36], jkbms.modbus_crc16)

    for idx, byte in enumerate(request):
        decoder.decode(idx, idx + 1, ("DATA", 1, (byte, [])))
    for idx, byte in enumerate(response, start=100):
        decoder.decode(idx, idx + 1, ("DATA", 0, (byte, [])))

    texts = [
        text
        for _ss, _es, output, data in decoder.captured
        if output == stub_sigrokdecode.OUTPUT_ANN
        for text in data[1]
    ]

    assert any("JKBMS Modbus req" in text for text in texts)
    assert any("JKBMS Modbus rsp" in text for text in texts)
    assert any("0x1290 pack_v=57.142V" in text for text in texts)

