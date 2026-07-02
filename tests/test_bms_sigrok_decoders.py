import importlib
import importlib.util
import sys
import types
from pathlib import Path


DECODERS_DIR = Path(__file__).resolve().parents[1] / "decoders"
GROWATT_RS485_DECODER_DIR = DECODERS_DIR / "growatt_rs485"
JKBMS_MODBUS_DECODER_DIR = DECODERS_DIR / "jkbms_modbus"

sys.path.insert(0, str(GROWATT_RS485_DECODER_DIR))

from growatt import describe_frame as describe_growatt_frame  # noqa: E402
from growatt import modbus_crc16 as growatt_crc16  # noqa: E402
from growatt import parse_frame as parse_growatt_frame  # noqa: E402


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


jkbms = load_module(
    "jkbms_modbus_helper",
    JKBMS_MODBUS_DECODER_DIR / "jkbms_modbus.py",
)


def with_modbus_crc(body, crc_func):
    body = list(body)
    crc = crc_func(body)
    return bytes(body + [crc & 0xFF, (crc >> 8) & 0xFF])


def words_to_bytes(words):
    data = []
    for word in words:
        data.extend([(word >> 8) & 0xFF, word & 0xFF])
    return data


def test_growatt_rs485_parses_modbus_request_and_response():
    request = parse_growatt_frame(
        with_modbus_crc([0x01, 0x03, 0x00, 0x13, 0x00, 0x08], growatt_crc16)
    )
    response = parse_growatt_frame(
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
        ], growatt_crc16),
        request,
    )

    assert request["crc_ok"]
    assert response["crc_ok"]
    assert response["registers"][0]["addr"] == 0x0013
    assert response["registers"][-1]["addr"] == 0x001A
    assert "response regs 0x0013..0x001A" in describe_growatt_frame(response)
    assert "SOC=99%" in describe_growatt_frame(response)
    assert "pack_v=57.15V" in describe_growatt_frame(response)


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

    texts = [item[3][1][0] for item in decoder.captured if item[2] == stub_sigrokdecode.OUTPUT_ANN]

    assert any("JKBMS Modbus req" in text for text in texts)
    assert any("JKBMS Modbus rsp" in text for text in texts)
    assert any("0x1290 pack_v=57.142V" in text for text in texts)
