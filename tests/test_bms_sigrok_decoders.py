import importlib
import importlib.util
import sys
import types
from pathlib import Path


DECODERS_DIR = Path(__file__).resolve().parents[1] / "decoders"
CHINA_TOWER_MODBUS_DECODER_DIR = DECODERS_DIR / "china_tower_modbus"
DEYE_CAN_DECODER_DIR = DECODERS_DIR / "deye_can"
GOODWE_CAN_DECODER_DIR = DECODERS_DIR / "goodwe_can"
GROWATT_CAN_DECODER_DIR = DECODERS_DIR / "growatt_can"
GROWATT_RS485_DECODER_DIR = DECODERS_DIR / "growatt_rs485"
JKBMS_MODBUS_DECODER_DIR = DECODERS_DIR / "jkbms_modbus"
JKBMS_CAN_DECODER_DIR = DECODERS_DIR / "jkbms_can"
PACE_MODBUS_DECODER_DIR = DECODERS_DIR / "pace_modbus"
PYLON_CAN_DECODER_DIR = DECODERS_DIR / "pylon_can"
PYLON_RS485_DECODER_DIR = DECODERS_DIR / "pylon_rs485"
SMA_CAN_DECODER_DIR = DECODERS_DIR / "sma_can"
SOFAR_CAN_DECODER_DIR = DECODERS_DIR / "sofar_can"
VICTRON_CAN_DECODER_DIR = DECODERS_DIR / "victron_can"
VOLTRONIC_MODBUS_DECODER_DIR = DECODERS_DIR / "voltronic_modbus"
WOW_MODBUS_DECODER_DIR = DECODERS_DIR / "wow_modbus"
PULSEVIEW_DECODER_DIR = Path(r"C:\Program Files\sigrok\PulseView\share\libsigrokdecode\decoders")
PULSEVIEW_SRD_DIR = Path(r"C:\Program Files\sigrok\PulseView\share\libsigrokdecode")


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


china_tower = load_module("china_tower_modbus_helper", CHINA_TOWER_MODBUS_DECODER_DIR / "china_tower_modbus.py")
deye_can = load_module("deye_can_helper", DEYE_CAN_DECODER_DIR / "deye_can.py")
goodwe_can = load_module("goodwe_can_helper", GOODWE_CAN_DECODER_DIR / "goodwe_can.py")
growatt_rs485 = load_module("growatt_rs485_helper", GROWATT_RS485_DECODER_DIR / "growatt.py")
growatt_can = load_module("growatt_can_helper", GROWATT_CAN_DECODER_DIR / "growatt_can.py")
jkbms = load_module("jkbms_modbus_helper", JKBMS_MODBUS_DECODER_DIR / "jkbms_modbus.py")
jkbms_can = load_module("jkbms_can_helper", JKBMS_CAN_DECODER_DIR / "jkbms_can.py")
pace_modbus = load_module("pace_modbus_helper", PACE_MODBUS_DECODER_DIR / "pace_modbus.py")
pylon_can = load_module("pylon_can_helper", PYLON_CAN_DECODER_DIR / "pylon_can.py")
pylon_rs485 = load_module("pylon_rs485_helper", PYLON_RS485_DECODER_DIR / "pylon.py")
sma_can = load_module("sma_can_helper", SMA_CAN_DECODER_DIR / "sma_can.py")
sofar_can = load_module("sofar_can_helper", SOFAR_CAN_DECODER_DIR / "sofar_can.py")
victron_can = load_module("victron_can_helper", VICTRON_CAN_DECODER_DIR / "victron_can.py")
voltronic = load_module("voltronic_modbus_helper", VOLTRONIC_MODBUS_DECODER_DIR / "voltronic_modbus.py")
wow_modbus = load_module("wow_modbus_helper", WOW_MODBUS_DECODER_DIR / "wow_modbus.py")


def with_modbus_crc(body, crc_func=growatt_rs485.modbus_crc16):
    body = list(body)
    crc = crc_func(body)
    return bytes(body + [crc & 0xFF, (crc >> 8) & 0xFF])


def words_to_bytes(words):
    data = []
    for word in words:
        data.extend([(word >> 8) & 0xFF, word & 0xFF])
    return data


def pylon_rs485_frame(addr, code, info_ascii=""):
    length_id = len(info_ascii)
    length_field = (pylon_rs485.length_check_nibble(length_id) << 12) | length_id
    body = "20{:02X}46{:02X}{:04X}{}".format(addr, code, length_field, info_ascii)
    checksum = pylon_rs485.ascii_checksum(body)
    return ("~{}{:04X}\r".format(body, checksum)).encode("ascii")


def test_active_decoder_folders_are_validated_only():
    decoder_names = sorted(path.name for path in DECODERS_DIR.iterdir() if path.is_dir())

    assert decoder_names == [
        "china_tower_modbus",
        "deye_can",
        "goodwe_can",
        "growatt_can",
        "growatt_rs485",
        "jkbms_can",
        "jkbms_modbus",
        "pace_modbus",
        "pylon_can",
        "pylon_rs485",
        "sma_can",
        "sofar_can",
        "victron_can",
        "voltronic_modbus",
        "wow_modbus",
    ]


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


def test_china_tower_modbus_parses_status_poll_block():
    request = china_tower.parse_frame(
        with_modbus_crc([0x01, 0x03, 0x00, 0x19, 0x00, 0x03], china_tower.modbus_crc16)
    )
    response = china_tower.parse_frame(
        with_modbus_crc([0x01, 0x03, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], china_tower.modbus_crc16),
        request,
    )
    decoded = china_tower.describe_frame(response)

    assert request["crc_ok"]
    assert request["start"] == 0x0019
    assert request["count"] == 3
    assert response["crc_ok"]
    assert response["registers"][0]["addr"] == 0x0019
    assert response["registers"][-1]["addr"] == 0x001B
    assert "warning=0x0000 (none)" in decoded
    assert "protection=0x0000 (none)" in decoded
    assert "status=0x0000 (none)" in decoded


def test_china_tower_modbus_parses_runtime_and_cell_values():
    request = china_tower.parse_frame(
        with_modbus_crc([0x01, 0x03, 0x00, 0x00, 0x00, 0x0D], china_tower.modbus_crc16)
    )
    response_words = [
        0x1655, 0x0010, 0x005D, 0x01F4, 0x0064, 0x0000, 0x001A,
        0x0019, 0x001A, 0x0DF7, 0x0DF4, 0x0DF5, 0x0DF5,
    ]
    response = china_tower.parse_frame(
        with_modbus_crc([0x01, 0x03, 0x1A] + words_to_bytes(response_words), china_tower.modbus_crc16),
        request,
    )
    decoded = china_tower.describe_frame(response)

    assert response["crc_ok"]
    assert response["registers"][0]["addr"] == 0x0000
    assert response["registers"][-1]["addr"] == 0x000C
    assert "pack_v=57.17V" in decoded
    assert "cell_count=16" in decoded
    assert "SOC=93%" in decoded
    assert "temp1=26C" in decoded
    assert "temp2=25C" in decoded
    assert "mos_temp=26C" in decoded
    assert "C01=3.575V" in decoded
    assert "min=3.572V#2" in decoded


def test_pace_modbus_parses_runtime_summary():
    request = pace_modbus.parse_frame(
        with_modbus_crc([0x01, 0x03, 0x00, 0x00, 0x00, 0x0D], pace_modbus.modbus_crc16)
    )
    response_words = [
        0xFFB4, 0x1602, 0x005B, 0x0064, 0x01C4, 0x01F4, 0x01F4,
        0x0000, 0x0000, 0x0000, 0x000E, 0x0000, 0x0000,
    ]
    response = pace_modbus.parse_frame(
        with_modbus_crc([0x01, 0x03, 0x1A] + words_to_bytes(response_words), pace_modbus.modbus_crc16),
        request,
    )
    decoded = pace_modbus.describe_frame(response)

    assert request["crc_ok"]
    assert request["start"] == 0x0000
    assert request["count"] == 0x000D
    assert response["crc_ok"]
    assert response["registers"][0]["addr"] == 0x0000
    assert response["registers"][-1]["addr"] == 0x000C
    assert "pack_i=-0.76A" in decoded
    assert "pack_v=56.34V" in decoded
    assert "SOC=91%" in decoded
    assert "SOH=100%" in decoded
    assert "remain=4.52Ah" in decoded
    assert "full=5.00Ah" in decoded
    assert "design=5.00Ah" in decoded
    assert "protection=0x000E" in decoded


def test_pace_modbus_parses_cells_and_temperatures():
    request = pace_modbus.parse_frame(
        with_modbus_crc([0x01, 0x03, 0x00, 0x0F, 0x00, 0x16], pace_modbus.modbus_crc16)
    )
    response_words = [
        0x0DC4, 0x0DBE, 0x0DC3, 0x0DC1, 0x0DC3, 0x0DC1, 0x0DC3, 0x0DC1,
        0x0DC3, 0x0DC1, 0x0DC3, 0x0DC1, 0x0DC3, 0x0DC1, 0x0DC3, 0x0DC1,
        0x0032, 0x0130, 0x012F, 0x0135, 0x011E, 0x0132,
    ]
    response = pace_modbus.parse_frame(
        with_modbus_crc([0x01, 0x03, 0x2C] + words_to_bytes(response_words), pace_modbus.modbus_crc16),
        request,
    )
    decoded = pace_modbus.describe_frame(response)

    assert response["crc_ok"]
    assert response["registers"][0]["addr"] == 0x000F
    assert response["registers"][-1]["addr"] == 0x0024
    assert "cells count=16" in decoded
    assert "C01=3.524V" in decoded
    assert "min=3.518V#2" in decoded
    assert "max=3.524V#1" in decoded
    assert "temp2=30.4C" in decoded
    assert "mos_temp=28.6C" in decoded


def test_wow_modbus_parses_runtime_summary():
    request = wow_modbus.parse_frame(
        with_modbus_crc([0x01, 0x03, 0x00, 0x00, 0x00, 0x0D], wow_modbus.modbus_crc16)
    )
    response_words = [
        0x0000, 0x164C, 0x0057, 0x0064, 0x01B0, 0x01F4, 0x01F4,
        0x0000, 0x0000, 0x0000, 0x0000, 0x000C, 0x0000,
    ]
    response = wow_modbus.parse_frame(
        with_modbus_crc([0x01, 0x03, 0x1A] + words_to_bytes(response_words), wow_modbus.modbus_crc16),
        request,
    )
    decoded = wow_modbus.describe_frame(response)

    assert request["crc_ok"]
    assert request["start"] == 0x0000
    assert request["count"] == 0x000D
    assert response["crc_ok"]
    assert response["registers"][0]["addr"] == 0x0000
    assert response["registers"][-1]["addr"] == 0x000C
    assert "pack_i=+0.00A" in decoded
    assert "pack_v=57.08V" in decoded
    assert "SOC=87%" in decoded
    assert "SOH=100%" in decoded
    assert "remain=4.32Ah" in decoded
    assert "full=5.00Ah" in decoded
    assert "design=5.00Ah" in decoded


def test_wow_modbus_parses_cells_and_temperatures():
    request = wow_modbus.parse_frame(
        with_modbus_crc([0x01, 0x03, 0x00, 0x0F, 0x00, 0x16], wow_modbus.modbus_crc16)
    )
    response_words = [
        0x0DF2, 0x0DED, 0x0DEF, 0x0DEE, 0x0DEF, 0x0DF1, 0x0DEE, 0x0DEF,
        0x0DEF, 0x0DEF, 0x0DF0, 0x0DF2, 0x0DF3, 0x0DF2, 0x0DF1, 0x0DF3,
        0x013B, 0x0139, 0x0140, 0x0128, 0x013C, 0x013A,
    ]
    response = wow_modbus.parse_frame(
        with_modbus_crc([0x01, 0x03, 0x2C] + words_to_bytes(response_words), wow_modbus.modbus_crc16),
        request,
    )
    decoded = wow_modbus.describe_frame(response)

    assert response["crc_ok"]
    assert response["registers"][0]["addr"] == 0x000F
    assert response["registers"][-1]["addr"] == 0x0024
    assert "cells count=16" in decoded
    assert "C01=3.570V" in decoded
    assert "min=3.565V#2" in decoded
    assert "max=3.571V#13" in decoded
    assert "temp1=31.5C" in decoded
    assert "env_temp=31.4C" in decoded


def test_voltronic_modbus_parses_wide_byte_count_runtime_values():
    request = voltronic.parse_frame(
        with_modbus_crc([0x01, 0x03, 0x00, 0x32, 0x00, 0x01], voltronic.modbus_crc16)
    )
    response = voltronic.parse_frame(
        with_modbus_crc([0x01, 0x03, 0x00, 0x02, 0x02, 0x30], voltronic.modbus_crc16),
        request,
    )
    decoded = voltronic.describe_frame(response)

    assert request["crc_ok"]
    assert request["start"] == 0x0032
    assert response["crc_ok"]
    assert response["format"] == "wide-byte-count"
    assert response["registers"][0]["addr"] == 0x0032
    assert "pack_v=56.0V" in decoded

    soc_request = voltronic.parse_frame(
        with_modbus_crc([0x01, 0x03, 0x00, 0x33, 0x00, 0x01], voltronic.modbus_crc16)
    )
    soc_response = voltronic.parse_frame(
        with_modbus_crc([0x01, 0x03, 0x00, 0x02, 0x00, 0x46], voltronic.modbus_crc16),
        soc_request,
    )
    assert "SOC=70%" in voltronic.describe_frame(soc_response)


def test_voltronic_modbus_parses_limits_and_status():
    charge_request = voltronic.parse_frame(
        with_modbus_crc([0x01, 0x03, 0x00, 0x72, 0x00, 0x01], voltronic.modbus_crc16)
    )
    charge_response = voltronic.parse_frame(
        with_modbus_crc([0x01, 0x03, 0x00, 0x02, 0x07, 0x08], voltronic.modbus_crc16),
        charge_request,
    )
    status_request = voltronic.parse_frame(
        with_modbus_crc([0x01, 0x03, 0x00, 0x74, 0x00, 0x01], voltronic.modbus_crc16)
    )
    status_response = voltronic.parse_frame(
        with_modbus_crc([0x01, 0x03, 0x00, 0x02, 0x00, 0xC0], voltronic.modbus_crc16),
        status_request,
    )

    assert "chg_i_limit=180.0A" in voltronic.describe_frame(charge_response)
    assert "status=0x00C0" in voltronic.describe_frame(status_response)
    assert "charge_enable" in voltronic.describe_frame(status_response)
    assert "discharge_enable" in voltronic.describe_frame(status_response)


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


def test_deye_can_describes_live_frames():
    soc = ("standard", 0x355, "data", 8, [0x63, 0x00, 0x64, 0x00, 0x00, 0x00, 0x00, 0x00])
    pack = ("standard", 0x356, "data", 8, [0x52, 0x16, 0x00, 0x00, 0x29, 0x01, 0x00, 0x00])
    status = ("standard", 0x35C, "data", 8, [0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    identity = ("standard", 0x35E, "data", 8, [0x4A, 0x4B, 0x2D, 0x42, 0x4D, 0x53, 0x00, 0x00])
    extremes = ("standard", 0x370, "data", 8, [0x1E, 0x00, 0x1D, 0x00, 0xF5, 0x0D, 0xF3, 0x0D])

    assert "SOC=99%" in deye_can.describe_packet(soc)
    assert "SOH=100%" in deye_can.describe_packet(soc)
    assert "V=57.14V" in deye_can.describe_packet(pack)
    assert "I=+0.0A" in deye_can.describe_packet(pack)
    assert "temp=29.7C" in deye_can.describe_packet(pack)
    assert "charge=ON" in deye_can.describe_packet(status)
    assert "discharge=ON" in deye_can.describe_packet(status)
    assert "balance=OFF" in deye_can.describe_packet(status)
    assert "identity 'JK-BMS'" in deye_can.describe_packet(identity)
    assert "cell_max=3.573V" in deye_can.describe_packet(extremes)
    assert "cell_min=3.571V" in deye_can.describe_packet(extremes)


def test_deye_can_describes_limits_and_indexes():
    limits = ("standard", 0x351, "data", 8, [0x02, 0x02, 0xF4, 0x01, 0xC8, 0x00, 0x64, 0x01])
    indexes = ("standard", 0x371, "data", 8, [0x01, 0x00, 0x02, 0x00, 0x05, 0x00, 0x09, 0x00])

    assert "chgV=51.4V" in deye_can.describe_packet(limits)
    assert "chgI=50.0A" in deye_can.describe_packet(limits)
    assert "disI=20.0A" in deye_can.describe_packet(limits)
    assert "lowV=35.6V" in deye_can.describe_packet(limits)
    assert "temp_max_sensor=1" in deye_can.describe_packet(indexes)
    assert "temp_min_sensor=2" in deye_can.describe_packet(indexes)
    assert "cell_max_idx=5" in deye_can.describe_packet(indexes)
    assert "cell_min_idx=9" in deye_can.describe_packet(indexes)


def test_goodwe_can_describes_jk_pylon_dialect_frames():
    limits = ("standard", 0x351, "data", 8, [0x9E, 0x02, 0x7C, 0x01, 0x6C, 0x07, 0xC6, 0x01])
    soc = ("standard", 0x355, "data", 8, [0x63, 0x00, 0x64, 0x00, 0x00, 0x00, 0x00, 0x00])
    pack = ("standard", 0x356, "data", 8, [0x53, 0x16, 0x00, 0x00, 0x33, 0x01, 0x00, 0x00])
    module = ("standard", 0x359, "data", 8, [0x00, 0x00, 0x00, 0x00, 0x01, 0x50, 0x4E, 0x00])

    assert "chgV=67.0V" in goodwe_can.describe_packet(limits)
    assert "chgI=38.0A" in goodwe_can.describe_packet(limits)
    assert "disI=190.0A" in goodwe_can.describe_packet(limits)
    assert "lowV=45.4V" in goodwe_can.describe_packet(limits)
    assert "SOC=99%" in goodwe_can.describe_packet(soc)
    assert "SOH=100%" in goodwe_can.describe_packet(soc)
    assert "V=57.15V" in goodwe_can.describe_packet(pack)
    assert "temp=30.7C" in goodwe_can.describe_packet(pack)
    assert "modules=1" in goodwe_can.describe_packet(module)
    assert "tag='PN'" in goodwe_can.describe_packet(module)


def test_goodwe_can_describes_native_frames():
    limits = ("standard", 0x456, "data", 8, [0x02, 0x02, 0xF4, 0x01, 0xC8, 0x00, 0x64, 0x01])
    soc = ("standard", 0x457, "data", 8, [0xE6, 0x03, 0xE8, 0x03, 0x00, 0x00, 0x00, 0x00])
    pack = ("standard", 0x458, "data", 8, [0x39, 0x02, 0xEC, 0xFF, 0x2A, 0x01, 0x00, 0x00])

    assert "chgV=51.4V" in goodwe_can.describe_packet(limits)
    assert "chgI=+50.0A" in goodwe_can.describe_packet(limits)
    assert "disI=+20.0A" in goodwe_can.describe_packet(limits)
    assert "lowV=35.6V" in goodwe_can.describe_packet(limits)
    assert "SOC=99.8% (100%)" in goodwe_can.describe_packet(soc)
    assert "SOH=100.0% (100%)" in goodwe_can.describe_packet(soc)
    assert "V=56.9V" in goodwe_can.describe_packet(pack)
    assert "I=-2.0A" in goodwe_can.describe_packet(pack)
    assert "temp=29.8C" in goodwe_can.describe_packet(pack)


def test_victron_can_describes_live_frames():
    limits = ("standard", 0x351, "data", 8, [0x9E, 0x02, 0x7C, 0x01, 0x6C, 0x07, 0xC6, 0x01])
    soc = ("standard", 0x355, "data", 8, [0x63, 0x00, 0x64, 0x00, 0x8E, 0x26, 0x00, 0x00])
    pack = ("standard", 0x356, "data", 8, [0x52, 0x16, 0x00, 0x00, 0x34, 0x01, 0x00, 0x00])
    vendor = ("standard", 0x35A, "data", 8, [0xA8, 0xA8, 0x02, 0x00, 0xA8, 0xA8, 0x02, 0x02])

    assert "chgV=67.0V" in victron_can.describe_packet(limits)
    assert "chgI=38.0A" in victron_can.describe_packet(limits)
    assert "disI=190.0A" in victron_can.describe_packet(limits)
    assert "lowV=45.4V" in victron_can.describe_packet(limits)
    assert "charge=ON" in victron_can.describe_packet(limits)
    assert "discharge=ON" in victron_can.describe_packet(limits)
    assert "SOC=99%" in victron_can.describe_packet(soc)
    assert "SOH=100%" in victron_can.describe_packet(soc)
    assert "raw_tail=8E 26 00 00" in victron_can.describe_packet(soc)
    assert "V=57.14V" in victron_can.describe_packet(pack)
    assert "I=+0.0A" in victron_can.describe_packet(pack)
    assert "temp=30.8C" in victron_can.describe_packet(pack)
    assert "0x35A vendor/raw raw=A8 A8 02 00 A8 A8 02 02" == victron_can.describe_packet(vendor)


def test_victron_can_describes_ascii_and_tentative_cell_frame():
    manufacturer = ("standard", 0x35E, "data", 8, [0x56, 0x69, 0x63, 0x74, 0x72, 0x6F, 0x6E, 0x00])
    cell_temps = ("standard", 0x373, "data", 8, [0xF3, 0x0D, 0xF5, 0x0D, 0x1E, 0x00, 0x1D, 0x00])

    assert "ASCII 'Victron'" in victron_can.describe_packet(manufacturer)
    assert "cell_min=3.571V" in victron_can.describe_packet(cell_temps)
    assert "cell_max=3.573V" in victron_can.describe_packet(cell_temps)
    assert "t1=30.0C" in victron_can.describe_packet(cell_temps)
    assert "t2=29.0C" in victron_can.describe_packet(cell_temps)


def test_sma_can_describes_live_frames():
    limits = ("standard", 0x351, "data", 8, [0x40, 0x02, 0x08, 0x07, 0x08, 0x07, 0x00, 0x02])
    pack = ("standard", 0x356, "data", 8, [0x3E, 0x16, 0x00, 0x00, 0xF9, 0x00, 0x00, 0x00])
    vendor = ("standard", 0x35A, "data", 8, [0xAA, 0xAA, 0x02, 0xAA, 0xAA, 0xAA, 0x02, 0x00])
    manufacturer = ("standard", 0x35E, "data", 8, [0x53, 0x4D, 0x41, 0x20, 0x20, 0x20, 0x20, 0x20])
    battery = ("standard", 0x35F, "data", 8, [0x00, 0x00, 0x00, 0x01, 0x22, 0x01, 0x00, 0x00])

    assert "chgV=57.6V" in sma_can.describe_packet(limits)
    assert "chgI=180.0A" in sma_can.describe_packet(limits)
    assert "disI=180.0A" in sma_can.describe_packet(limits)
    assert "lowV=51.2V" in sma_can.describe_packet(limits)
    assert "V=56.94V" in sma_can.describe_packet(pack)
    assert "I=+0.0A" in sma_can.describe_packet(pack)
    assert "temp=24.9C" in sma_can.describe_packet(pack)
    assert "SMA vendor" in sma_can.describe_packet(vendor)
    assert "raw=AA AA 02 AA AA AA 02 00" in sma_can.describe_packet(vendor)
    assert "SMA manufacturer 'SMA'" in sma_can.describe_packet(manufacturer)
    assert "0x35F SMA battery info" in sma_can.describe_packet(battery)


def test_sofar_can_describes_live_frames():
    limits = ("standard", 0x351, "data", 8, [0x40, 0x02, 0x08, 0x07, 0x08, 0x07, 0x00, 0x02])
    soc = ("standard", 0x355, "data", 8, [0x46, 0x00, 0x64, 0x00, 0x6C, 0x1B, 0x00, 0x00])
    pack = ("standard", 0x356, "data", 8, [0xEE, 0x15, 0x00, 0x00, 0xF8, 0x00, 0x00, 0x00])
    brand = ("standard", 0x35E, "data", 8, [0x53, 0x6F, 0x66, 0x61, 0x72, 0x20, 0x20, 0x20])
    module = ("standard", 0x35F, "data", 8, [0x00, 0x00, 0x00, 0x01, 0x22, 0x01, 0x00, 0x00])

    assert "chgV=57.6V" in sofar_can.describe_packet(limits)
    assert "chgI=180.0A" in sofar_can.describe_packet(limits)
    assert "disI=180.0A" in sofar_can.describe_packet(limits)
    assert "lowV=51.2V" in sofar_can.describe_packet(limits)
    assert "SOC=70%" in sofar_can.describe_packet(soc)
    assert "SOH=100%" in sofar_can.describe_packet(soc)
    assert "V=56.14V" in sofar_can.describe_packet(pack)
    assert "I=+0.0A" in sofar_can.describe_packet(pack)
    assert "temp=24.8C" in sofar_can.describe_packet(pack)
    assert "Sofar brand 'Sofar'" in sofar_can.describe_packet(brand)
    assert "u16=[0, 256, 290, 0]" in sofar_can.describe_packet(module)


def test_pylon_can_describes_live_frames():
    limits = ("standard", 0x351, "data", 8, [0x9E, 0x02, 0x7C, 0x01, 0x6C, 0x07, 0xC6, 0x01])
    soc = ("standard", 0x355, "data", 8, [0x63, 0x00, 0x64, 0x00, 0x00, 0x00, 0x00, 0x00])
    pack = ("standard", 0x356, "data", 8, [0x4B, 0x16, 0x00, 0x00, 0x34, 0x01, 0x00, 0x00])
    module = ("standard", 0x359, "data", 8, [0x00, 0x00, 0x00, 0x00, 0x01, 0x50, 0x4E, 0x00])
    status = ("standard", 0x35C, "data", 8, [0xC0, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    identity = ("standard", 0x35E, "data", 8, [0x4A, 0x4B, 0x2D, 0x42, 0x4D, 0x53, 0x00, 0x00])
    extremes = ("standard", 0x370, "data", 8, [0x1F, 0x00, 0x1E, 0x00, 0xF1, 0x0D, 0xED, 0x0D])

    assert "chgV=67.0V" in pylon_can.describe_packet(limits)
    assert "chgI=38.0A" in pylon_can.describe_packet(limits)
    assert "disI=190.0A" in pylon_can.describe_packet(limits)
    assert "lowV=45.4V" in pylon_can.describe_packet(limits)
    assert "SOC=99%" in pylon_can.describe_packet(soc)
    assert "SOH=100%" in pylon_can.describe_packet(soc)
    assert "V=57.07V" in pylon_can.describe_packet(pack)
    assert "I=0.0A" in pylon_can.describe_packet(pack)
    assert "temp=30.8C" in pylon_can.describe_packet(pack)
    assert "modules=1" in pylon_can.describe_packet(module)
    assert "status=0xC0 (charge=ON, discharge=ON, balance=OFF)" in pylon_can.describe_packet(status)
    assert "name='JK-BMS'" in pylon_can.describe_packet(identity)
    assert "tMax=31.0C" in pylon_can.describe_packet(extremes)
    assert "tMin=30.0C" in pylon_can.describe_packet(extremes)
    assert "cell_max=3.569V" in pylon_can.describe_packet(extremes)
    assert "cell_min=3.565V" in pylon_can.describe_packet(extremes)


def test_pylon_can_describes_indexes_and_cell_temp_frame():
    indexes = ("standard", 0x371, "data", 8, [0x01, 0x00, 0x02, 0x00, 0x05, 0x00, 0x09, 0x00])
    cell_temps = ("standard", 0x373, "data", 8, [0xF3, 0x0D, 0xF5, 0x0D, 0x2C, 0x01, 0x22, 0x01])

    assert "tMax#1" in pylon_can.describe_packet(indexes)
    assert "tMin#2" in pylon_can.describe_packet(indexes)
    assert "cellMax#5" in pylon_can.describe_packet(indexes)
    assert "cellMin#9" in pylon_can.describe_packet(indexes)
    assert "cell_min=3.571V" in pylon_can.describe_packet(cell_temps)
    assert "cell_max=3.573V" in pylon_can.describe_packet(cell_temps)
    assert "t1=30.0C" in pylon_can.describe_packet(cell_temps)
    assert "t2=29.0C" in pylon_can.describe_packet(cell_temps)


def test_pylon_rs485_parses_live_requests_and_responses():
    request61 = pylon_rs485.parse_frame(pylon_rs485_frame(0x02, 0x61))
    request42 = pylon_rs485.parse_frame(pylon_rs485_frame(0x01, 0x42, "FF"))
    response61 = pylon_rs485.parse_frame(pylon_rs485_frame(
        0x02,
        0x00,
        "DF0A0000630000000064640DF200050DEE000B0BE0BE600040BDB00030BCEBCE00000BCE00000BCE0BCE00000BCE0000",
    ))
    response63 = pylon_rs485.parse_frame(pylon_rs485_frame(0x02, 0x00, "05E0B180017C076CC0"))
    response62 = pylon_rs485.parse_frame(pylon_rs485_frame(0x02, 0x00, "00000000"))

    assert request61["length_ok"]
    assert request61["checksum_ok"]
    assert pylon_rs485.is_request(request61)
    assert "request analog/telemetry empty payload" == pylon_rs485.describe_info(request61)
    assert "selector=0xFF aggregate/all packs" in pylon_rs485.describe_info(request42)

    decoded61 = pylon_rs485.describe_info(response61, 0x61)
    assert response61["length_ok"]
    assert response61["checksum_ok"]
    assert "V=57.098V" in decoded61
    assert "I=0.0A" in decoded61
    assert "SOC=99%" in decoded61
    assert "SOH=100%" in decoded61
    assert "cell_max=3.570V#5" in decoded61
    assert "cell_min=3.566V#11" in decoded61

    assert "status=0xC0 (charge=ON, discharge=ON, balance=OFF)" in pylon_rs485.describe_info(response63, 0x63)
    assert "0x62 flags=0x00000000 (no flags set)" == pylon_rs485.describe_info(response62, 0x62)


def test_pylon_rs485_describes_cell_lists():
    info = [2, 0x0D, 0xF3, 0x0D, 0xF5]
    decoded = pylon_rs485.describe_info({"code": 0x00, "info_bytes": info, "info_ascii": "020DF30DF5"}, 0x42)

    assert "0x42 cells simple layout count=2" in decoded
    assert "min=3.571V#1" in decoded
    assert "max=3.573V#2" in decoded


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


def test_sigrok_deye_can_package_exports_decoder(monkeypatch):
    stub_sigrokdecode = types.SimpleNamespace(Decoder=object, OUTPUT_ANN=1, OUTPUT_PYTHON=2)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(PULSEVIEW_SRD_DIR))
    sys.path.insert(0, str(PULSEVIEW_DECODER_DIR))
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("can", "can.pd", "deye_can", "deye_can.pd", "deye_can.deye_can"):
        sys.modules.pop(name, None)

    module = importlib.import_module("deye_can")

    assert module.Decoder.id == "deye_can"
    assert module.Decoder.inputs == ["logic"]
    assert deye_can.VERSION in module.Decoder.name
    assert any(option["id"] == "input_mode" for option in module.Decoder.options)


def test_sigrok_deye_can_decoder_derives_bus_level_from_raw_can_lines(monkeypatch):
    stub_sigrokdecode = types.SimpleNamespace(Decoder=object, OUTPUT_ANN=1, OUTPUT_PYTHON=2)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(PULSEVIEW_SRD_DIR))
    sys.path.insert(0, str(PULSEVIEW_DECODER_DIR))
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("can", "can.pd", "deye_can", "deye_can.pd", "deye_can.deye_can"):
        sys.modules.pop(name, None)

    module = importlib.import_module("deye_can")
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


def test_sigrok_goodwe_can_package_exports_decoder(monkeypatch):
    stub_sigrokdecode = types.SimpleNamespace(Decoder=object, OUTPUT_ANN=1, OUTPUT_PYTHON=2)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(PULSEVIEW_SRD_DIR))
    sys.path.insert(0, str(PULSEVIEW_DECODER_DIR))
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("can", "can.pd", "goodwe_can", "goodwe_can.pd", "goodwe_can.goodwe_can"):
        sys.modules.pop(name, None)

    module = importlib.import_module("goodwe_can")

    assert module.Decoder.id == "goodwe_can"
    assert module.Decoder.inputs == ["logic"]
    assert goodwe_can.VERSION in module.Decoder.name
    assert any(option["id"] == "input_mode" for option in module.Decoder.options)


def test_sigrok_goodwe_can_decoder_derives_bus_level_from_raw_can_lines(monkeypatch):
    stub_sigrokdecode = types.SimpleNamespace(Decoder=object, OUTPUT_ANN=1, OUTPUT_PYTHON=2)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(PULSEVIEW_SRD_DIR))
    sys.path.insert(0, str(PULSEVIEW_DECODER_DIR))
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("can", "can.pd", "goodwe_can", "goodwe_can.pd", "goodwe_can.goodwe_can"):
        sys.modules.pop(name, None)

    module = importlib.import_module("goodwe_can")
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


def test_sigrok_victron_can_package_exports_decoder(monkeypatch):
    stub_sigrokdecode = types.SimpleNamespace(Decoder=object, OUTPUT_ANN=1, OUTPUT_PYTHON=2)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(PULSEVIEW_SRD_DIR))
    sys.path.insert(0, str(PULSEVIEW_DECODER_DIR))
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("can", "can.pd", "victron_can", "victron_can.pd", "victron_can.victron_can"):
        sys.modules.pop(name, None)

    module = importlib.import_module("victron_can")

    assert module.Decoder.id == "victron_can"
    assert module.Decoder.inputs == ["logic"]
    assert victron_can.VERSION in module.Decoder.name
    assert any(option["id"] == "input_mode" for option in module.Decoder.options)


def test_sigrok_victron_can_decoder_derives_bus_level_from_raw_can_lines(monkeypatch):
    stub_sigrokdecode = types.SimpleNamespace(Decoder=object, OUTPUT_ANN=1, OUTPUT_PYTHON=2)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(PULSEVIEW_SRD_DIR))
    sys.path.insert(0, str(PULSEVIEW_DECODER_DIR))
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("can", "can.pd", "victron_can", "victron_can.pd", "victron_can.victron_can"):
        sys.modules.pop(name, None)

    module = importlib.import_module("victron_can")
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


def test_sigrok_sma_can_package_exports_decoder(monkeypatch):
    stub_sigrokdecode = types.SimpleNamespace(Decoder=object, OUTPUT_ANN=1, OUTPUT_PYTHON=2)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(PULSEVIEW_SRD_DIR))
    sys.path.insert(0, str(PULSEVIEW_DECODER_DIR))
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("can", "can.pd", "sma_can", "sma_can.pd", "sma_can.sma_can"):
        sys.modules.pop(name, None)

    module = importlib.import_module("sma_can")

    assert module.Decoder.id == "sma_can"
    assert module.Decoder.inputs == ["logic"]
    assert sma_can.VERSION in module.Decoder.name
    assert any(option["id"] == "input_mode" for option in module.Decoder.options)


def test_sigrok_sma_can_decoder_derives_bus_level_from_raw_can_lines(monkeypatch):
    stub_sigrokdecode = types.SimpleNamespace(Decoder=object, OUTPUT_ANN=1, OUTPUT_PYTHON=2)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(PULSEVIEW_SRD_DIR))
    sys.path.insert(0, str(PULSEVIEW_DECODER_DIR))
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("can", "can.pd", "sma_can", "sma_can.pd", "sma_can.sma_can"):
        sys.modules.pop(name, None)

    module = importlib.import_module("sma_can")
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


def test_sigrok_sofar_can_package_exports_decoder(monkeypatch):
    stub_sigrokdecode = types.SimpleNamespace(Decoder=object, OUTPUT_ANN=1, OUTPUT_PYTHON=2)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(PULSEVIEW_SRD_DIR))
    sys.path.insert(0, str(PULSEVIEW_DECODER_DIR))
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("can", "can.pd", "sofar_can", "sofar_can.pd", "sofar_can.sofar_can"):
        sys.modules.pop(name, None)

    module = importlib.import_module("sofar_can")

    assert module.Decoder.id == "sofar_can"
    assert module.Decoder.inputs == ["logic"]
    assert sofar_can.VERSION in module.Decoder.name
    assert any(option["id"] == "input_mode" for option in module.Decoder.options)


def test_sigrok_sofar_can_decoder_derives_bus_level_from_raw_can_lines(monkeypatch):
    stub_sigrokdecode = types.SimpleNamespace(Decoder=object, OUTPUT_ANN=1, OUTPUT_PYTHON=2)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(PULSEVIEW_SRD_DIR))
    sys.path.insert(0, str(PULSEVIEW_DECODER_DIR))
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("can", "can.pd", "sofar_can", "sofar_can.pd", "sofar_can.sofar_can"):
        sys.modules.pop(name, None)

    module = importlib.import_module("sofar_can")
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


def test_sigrok_pylon_can_package_exports_decoder(monkeypatch):
    stub_sigrokdecode = types.SimpleNamespace(Decoder=object, OUTPUT_ANN=1, OUTPUT_PYTHON=2)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(PULSEVIEW_SRD_DIR))
    sys.path.insert(0, str(PULSEVIEW_DECODER_DIR))
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("can", "can.pd", "pylon_can", "pylon_can.pd", "pylon_can.pylon_can"):
        sys.modules.pop(name, None)

    module = importlib.import_module("pylon_can")

    assert module.Decoder.id == "pylon_can"
    assert module.Decoder.inputs == ["logic"]
    assert pylon_can.VERSION in module.Decoder.name
    assert any(option["id"] == "input_mode" for option in module.Decoder.options)


def test_sigrok_pylon_can_decoder_derives_bus_level_from_raw_can_lines(monkeypatch):
    stub_sigrokdecode = types.SimpleNamespace(Decoder=object, OUTPUT_ANN=1, OUTPUT_PYTHON=2)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(PULSEVIEW_SRD_DIR))
    sys.path.insert(0, str(PULSEVIEW_DECODER_DIR))
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("can", "can.pd", "pylon_can", "pylon_can.pd", "pylon_can.pylon_can"):
        sys.modules.pop(name, None)

    module = importlib.import_module("pylon_can")
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


def test_sigrok_china_tower_modbus_package_exports_decoder(monkeypatch):
    stub_sigrokdecode = types.SimpleNamespace(Decoder=object, OUTPUT_ANN=1)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("china_tower_modbus", "china_tower_modbus.pd", "china_tower_modbus.china_tower_modbus"):
        sys.modules.pop(name, None)

    module = importlib.import_module("china_tower_modbus")

    assert module.Decoder.id == "china_tower_modbus"
    assert module.Decoder.inputs == ["uart"]
    assert any(option["id"] == "inter_frame_gap_us" for option in module.Decoder.options)


def test_sigrok_pace_modbus_package_exports_decoder(monkeypatch):
    stub_sigrokdecode = types.SimpleNamespace(Decoder=object, OUTPUT_ANN=1)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("pace_modbus", "pace_modbus.pd", "pace_modbus.pace_modbus"):
        sys.modules.pop(name, None)

    module = importlib.import_module("pace_modbus")

    assert module.Decoder.id == "pace_modbus"
    assert module.Decoder.inputs == ["uart"]
    assert any(option["id"] == "inter_frame_gap_us" for option in module.Decoder.options)


def test_sigrok_voltronic_modbus_package_exports_decoder(monkeypatch):
    stub_sigrokdecode = types.SimpleNamespace(Decoder=object, OUTPUT_ANN=1)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("voltronic_modbus", "voltronic_modbus.pd", "voltronic_modbus.voltronic_modbus"):
        sys.modules.pop(name, None)

    module = importlib.import_module("voltronic_modbus")

    assert module.Decoder.id == "voltronic_modbus"
    assert module.Decoder.inputs == ["uart"]
    assert any(option["id"] == "inter_frame_gap_us" for option in module.Decoder.options)


def test_sigrok_wow_modbus_package_exports_decoder(monkeypatch):
    stub_sigrokdecode = types.SimpleNamespace(Decoder=object, OUTPUT_ANN=1)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("wow_modbus", "wow_modbus.pd", "wow_modbus.wow_modbus"):
        sys.modules.pop(name, None)

    module = importlib.import_module("wow_modbus")

    assert module.Decoder.id == "wow_modbus"
    assert module.Decoder.inputs == ["uart"]
    assert any(option["id"] == "inter_frame_gap_us" for option in module.Decoder.options)


def test_sigrok_pylon_rs485_package_exports_decoder(monkeypatch):
    stub_sigrokdecode = types.SimpleNamespace(Decoder=object, OUTPUT_ANN=1)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("pylon_rs485", "pylon_rs485.pd", "pylon_rs485.pylon"):
        sys.modules.pop(name, None)

    module = importlib.import_module("pylon_rs485")

    assert module.Decoder.id == "pylon_rs485"
    assert module.Decoder.inputs == ["uart"]
    assert pylon_rs485.VERSION in module.Decoder.name


def test_sigrok_pylon_rs485_decoder_emits_annotations_for_uart_frames(monkeypatch):
    class FakeSrdDecoder:
        def register(self, output):
            return output

        def put(self, ss, es, output, data):
            self.captured.append((ss, es, output, data))

    stub_sigrokdecode = types.SimpleNamespace(Decoder=FakeSrdDecoder, OUTPUT_ANN=1)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("pylon_rs485", "pylon_rs485.pd", "pylon_rs485.pylon"):
        sys.modules.pop(name, None)

    module = importlib.import_module("pylon_rs485")
    decoder = module.Decoder()
    decoder.captured = []
    decoder.start()

    request = pylon_rs485_frame(0x02, 0x61)
    response = pylon_rs485_frame(
        0x02,
        0x00,
        "DF0A0000630000000064640DF200050DEE000B0BE0BE600040BDB00030BCEBCE00000BCE00000BCE0BCE00000BCE0000",
    )

    for idx, byte in enumerate(request):
        decoder.decode(idx, idx + 1, ("DATA", 0, (byte, [])))
    for idx, byte in enumerate(response, start=200):
        decoder.decode(idx, idx + 1, ("DATA", 0, (byte, [])))

    texts = [
        text
        for _ss, _es, output, data in decoder.captured
        if output == stub_sigrokdecode.OUTPUT_ANN
        for text in data[1]
    ]

    assert any("Pylon req" in text for text in texts)
    assert any("Pylon rsp" in text for text in texts)
    assert any("0x61 V=57.098V" in text for text in texts)


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


def test_sigrok_china_tower_modbus_decoder_emits_annotations_for_uart_frames(monkeypatch):
    class FakeSrdDecoder:
        def register(self, output):
            return output

        def put(self, ss, es, output, data):
            self.captured.append((ss, es, output, data))

    stub_sigrokdecode = types.SimpleNamespace(Decoder=FakeSrdDecoder, OUTPUT_ANN=1)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("china_tower_modbus", "china_tower_modbus.pd", "china_tower_modbus.china_tower_modbus"):
        sys.modules.pop(name, None)

    module = importlib.import_module("china_tower_modbus")
    decoder = module.Decoder()
    decoder.captured = []
    decoder.start()

    request = with_modbus_crc([0x01, 0x03, 0x00, 0x19, 0x00, 0x03], china_tower.modbus_crc16)
    response = with_modbus_crc([0x01, 0x03, 0x06, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], china_tower.modbus_crc16)

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

    assert any("China Tower Modbus req" in text for text in texts)
    assert any("China Tower Modbus rsp" in text for text in texts)
    assert any("0x0019 warning=0x0000" in text for text in texts)


def test_sigrok_pace_modbus_decoder_emits_annotations_for_uart_frames(monkeypatch):
    class FakeSrdDecoder:
        def register(self, output):
            return output

        def put(self, ss, es, output, data):
            self.captured.append((ss, es, output, data))

    stub_sigrokdecode = types.SimpleNamespace(Decoder=FakeSrdDecoder, OUTPUT_ANN=1)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("pace_modbus", "pace_modbus.pd", "pace_modbus.pace_modbus"):
        sys.modules.pop(name, None)

    module = importlib.import_module("pace_modbus")
    decoder = module.Decoder()
    decoder.captured = []
    decoder.start()

    request = with_modbus_crc([0x01, 0x03, 0x00, 0x00, 0x00, 0x0D], pace_modbus.modbus_crc16)
    response = with_modbus_crc(
        [
            0x01, 0x03, 0x1A,
            0xFF, 0xB4,
            0x16, 0x02,
            0x00, 0x5B,
            0x00, 0x64,
            0x01, 0xC4,
            0x01, 0xF4,
            0x01, 0xF4,
            0x00, 0x00,
            0x00, 0x00,
            0x00, 0x00,
            0x00, 0x0E,
            0x00, 0x00,
            0x00, 0x00,
        ],
        pace_modbus.modbus_crc16,
    )

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

    assert any("PACE Modbus req" in text for text in texts)
    assert any("PACE Modbus rsp" in text for text in texts)
    assert any("0x0000 pack_i=-0.76A" in text for text in texts)


def test_sigrok_voltronic_modbus_decoder_emits_annotations_for_uart_frames(monkeypatch):
    class FakeSrdDecoder:
        def register(self, output):
            return output

        def put(self, ss, es, output, data):
            self.captured.append((ss, es, output, data))

    stub_sigrokdecode = types.SimpleNamespace(Decoder=FakeSrdDecoder, OUTPUT_ANN=1)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("voltronic_modbus", "voltronic_modbus.pd", "voltronic_modbus.voltronic_modbus"):
        sys.modules.pop(name, None)

    module = importlib.import_module("voltronic_modbus")
    decoder = module.Decoder()
    decoder.captured = []
    decoder.start()

    request = with_modbus_crc([0x01, 0x03, 0x00, 0x32, 0x00, 0x01], voltronic.modbus_crc16)
    response = with_modbus_crc([0x01, 0x03, 0x00, 0x02, 0x02, 0x30], voltronic.modbus_crc16)

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

    assert any("Voltronic Modbus req" in text for text in texts)
    assert any("Voltronic Modbus rsp" in text for text in texts)
    assert any("0x0032 pack_v=56.0V" in text for text in texts)


def test_sigrok_wow_modbus_decoder_emits_annotations_for_uart_frames(monkeypatch):
    class FakeSrdDecoder:
        def register(self, output):
            return output

        def put(self, ss, es, output, data):
            self.captured.append((ss, es, output, data))

    stub_sigrokdecode = types.SimpleNamespace(Decoder=FakeSrdDecoder, OUTPUT_ANN=1)
    monkeypatch.setitem(sys.modules, "sigrokdecode", stub_sigrokdecode)
    sys.path.insert(0, str(DECODERS_DIR))

    for name in ("wow_modbus", "wow_modbus.pd", "wow_modbus.wow_modbus"):
        sys.modules.pop(name, None)

    module = importlib.import_module("wow_modbus")
    decoder = module.Decoder()
    decoder.captured = []
    decoder.start()

    request = with_modbus_crc([0x01, 0x03, 0x00, 0x00, 0x00, 0x0D], wow_modbus.modbus_crc16)
    response = with_modbus_crc(
        [
            0x01, 0x03, 0x1A,
            0x00, 0x00,
            0x16, 0x4C,
            0x00, 0x57,
            0x00, 0x64,
            0x01, 0xB0,
            0x01, 0xF4,
            0x01, 0xF4,
            0x00, 0x00,
            0x00, 0x00,
            0x00, 0x00,
            0x00, 0x00,
            0x00, 0x0C,
            0x00, 0x00,
        ],
        wow_modbus.modbus_crc16,
    )

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

    assert any("WOW Modbus req" in text for text in texts)
    assert any("WOW Modbus rsp" in text for text in texts)
    assert any("0x0000 pack_i=+0.00A" in text for text in texts)

