##
## JKBMS RS485 Modbus RTU frame helpers.
##
## Kept dependency-free so the parser can be unit-tested without PulseView.
##

FUNCTION_NAMES = {
    0x03: 'read holding registers',
    0x04: 'read input registers',
}

BASE_RUNTIME = 0x1200
MAX_CELLS = 32

REG_CELL0_MV = 0x1200
REG_CELL31_MV = 0x123E
REG_CELL_AVG_MV = 0x1244
REG_CELL_DIFF_MV = 0x1246
REG_MAX_MIN_CELL_IDX = 0x1248
REG_TEMP_MOS_DECIC = 0x128A
REG_PACK_VOLT_MV_U32 = 0x1290
REG_PACK_WATT_MW_U32 = 0x1294
REG_PACK_CURRENT_MA_I32 = 0x1298
REG_TEMP_BAT1_DECIC = 0x129C
REG_TEMP_BAT2_DECIC = 0x129E
REG_ALARM_U32 = 0x12A0
REG_BALANCE_CURRENT_MA_I16 = 0x12A4
REG_BALANCE_SOC_U8X2 = 0x12A6
REG_REMAIN_MAH_I32 = 0x12A8
REG_FULL_MAH_U32 = 0x12AC
REG_CYCLES_U32 = 0x12B0
REG_SOH_PRECHARGE_U8X2 = 0x12B8

POLL_BLOCKS = (
    (0x1200, 0x0010),
    (0x1210, 0x0010),
    (0x1220, 0x0010),
    (0x1230, 0x0010),
    (0x1240, 0x0020),
    (0x1244, 0x0006),
    (0x128A, 0x0028),
    (0x12B8, 0x0002),
)

REGISTER_NAMES = {
    REG_CELL_AVG_MV: 'cell_avg_mv',
    REG_CELL_DIFF_MV: 'cell_diff_max_mv',
    REG_MAX_MIN_CELL_IDX: 'max_min_cell_idx',
    REG_TEMP_MOS_DECIC: 'temp_mos_deciC',
    REG_PACK_VOLT_MV_U32: 'pack_voltage_mV_hi',
    REG_PACK_VOLT_MV_U32 + 1: 'pack_voltage_mV_lo',
    REG_PACK_WATT_MW_U32: 'pack_power_mW_hi',
    REG_PACK_WATT_MW_U32 + 1: 'pack_power_mW_lo',
    REG_PACK_CURRENT_MA_I32: 'pack_current_mA_hi',
    REG_PACK_CURRENT_MA_I32 + 1: 'pack_current_mA_lo',
    REG_TEMP_BAT1_DECIC: 'temp_bat1_deciC',
    REG_TEMP_BAT2_DECIC: 'temp_bat2_deciC',
    REG_ALARM_U32: 'alarm_u32_hi',
    REG_ALARM_U32 + 1: 'alarm_u32_lo',
    REG_BALANCE_CURRENT_MA_I16: 'balance_current_mA',
    REG_BALANCE_SOC_U8X2: 'balance_soc_u8x2',
    REG_REMAIN_MAH_I32: 'remaining_mAh_hi',
    REG_REMAIN_MAH_I32 + 1: 'remaining_mAh_lo',
    REG_FULL_MAH_U32: 'full_mAh_hi',
    REG_FULL_MAH_U32 + 1: 'full_mAh_lo',
    REG_CYCLES_U32: 'cycles_hi',
    REG_CYCLES_U32 + 1: 'cycles_lo',
    REG_SOH_PRECHARGE_U8X2: 'soh_precharge_u8x2',
}

ALARM_FLAGS = (
    (1 << 0, 'balance wire resistance fault'),
    (1 << 1, 'MOS overtemperature protection'),
    (1 << 2, 'cell count mismatch'),
    (1 << 3, 'current sensor fault'),
    (1 << 4, 'cell overvoltage protection'),
    (1 << 5, 'pack overvoltage protection'),
    (1 << 6, 'charge overcurrent protection'),
    (1 << 7, 'charge short-circuit protection'),
    (1 << 8, 'charge overtemperature protection'),
    (1 << 9, 'charge undertemperature protection'),
    (1 << 10, 'internal communication fault'),
    (1 << 11, 'cell undervoltage protection'),
    (1 << 12, 'pack undervoltage protection'),
    (1 << 13, 'discharge overcurrent protection'),
    (1 << 14, 'discharge short-circuit protection'),
    (1 << 15, 'discharge overtemperature protection'),
    (1 << 16, 'charge MOS fault'),
    (1 << 17, 'discharge MOS fault'),
    (1 << 18, 'GPS disconnected'),
    (1 << 19, 'authorization password warning'),
    (1 << 20, 'discharge enable failed'),
    (1 << 21, 'battery overtemperature alarm'),
    (1 << 22, 'temperature sensor anomaly'),
    (1 << 23, 'parallel module anomaly'),
)


def modbus_crc16(data):
    crc = 0xffff
    for byte in data:
        crc ^= byte
        for _ in range(8):
            if crc & 1:
                crc = (crc >> 1) ^ 0xA001
            else:
                crc >>= 1
    return crc & 0xffff


def frame_crc(raw):
    return raw[-2] | (raw[-1] << 8)


def hex_bytes(data):
    return ' '.join('{:02X}'.format(byte & 0xFF) for byte in data)


def be16(data, pos):
    return (data[pos] << 8) | data[pos + 1]


def be16s(data, pos):
    value = be16(data, pos)
    if value & 0x8000:
        value -= 0x10000
    return value


def bswap16(value):
    return ((value >> 8) | ((value & 0xFF) << 8)) & 0xFFFF


def u32_ab(a, b):
    return ((a & 0xFFFF) << 16) | (b & 0xFFFF)


def i32_from_u32(value):
    value &= 0xFFFFFFFF
    if value & 0x80000000:
        value -= 0x100000000
    return value


def known_alarm_mask():
    mask = 0
    for bit, _name in ALARM_FLAGS:
        mask |= bit
    return mask


def count_bits(value):
    count = 0
    while value:
        count += value & 1
        value >>= 1
    return count


def reverse_bytes32(value):
    return (((value & 0x000000FF) << 24) |
            ((value & 0x0000FF00) << 8) |
            ((value & 0x00FF0000) >> 8) |
            ((value & 0xFF000000) >> 24))


def normalize_alarm_bits(value):
    known = known_alarm_mask()
    reversed_value = reverse_bytes32(value)
    raw_unknown = count_bits(value & ~known)
    reversed_unknown = count_bits(reversed_value & ~known)
    if value and reversed_unknown < raw_unknown:
        return reversed_value
    return value


def alarm_list(value):
    value = normalize_alarm_bits(value)
    parts = [name for mask, name in ALARM_FLAGS if value & mask]
    known = known_alarm_mask()
    unknown = value & ~known
    for bit in range(32):
        if unknown & (1 << bit):
            parts.append('unknown bit {}'.format(bit))
    return ', '.join(parts) if parts else 'none'


def normalize_cell_mv(raw):
    candidates = []
    for value in (raw, bswap16(raw), raw // 10, bswap16(raw) // 10):
        if 2000 <= value <= 5000:
            candidates.append(value)
    if not candidates:
        return None
    return min(candidates, key=lambda value: abs(value - 4000))


def normalize_delta_mv(raw):
    return raw // 10 if raw > 5000 else raw


def decode_pct_byte_pair(raw, prefer_high=False):
    hi = (raw >> 8) & 0xFF
    lo = raw & 0xFF
    hi_ok = hi <= 100
    lo_ok = lo <= 100
    if hi_ok and lo_ok:
        if hi == 0 and lo > 0:
            return lo
        if lo == 0 and hi > 0:
            return hi
        return hi if prefer_high else lo
    if hi_ok:
        return hi
    if lo_ok:
        return lo
    return None


def best_u32(values, reg, min_value=0, max_value=0xFFFFFFFF):
    if reg not in values or reg + 1 not in values:
        return None
    a = values[reg]
    b = values[reg + 1]
    candidates = (u32_ab(a, b), u32_ab(b, a))
    valid = [value for value in candidates if min_value <= value <= max_value]
    if not valid:
        return None
    return min(valid)


def best_i32(values, reg, abs_limit=0x7FFFFFFF):
    if reg not in values or reg + 1 not in values:
        return None
    a = values[reg]
    b = values[reg + 1]
    candidates = (i32_from_u32(u32_ab(a, b)), i32_from_u32(u32_ab(b, a)))
    valid = [value for value in candidates if -abs_limit <= value <= abs_limit]
    if not valid:
        return None
    return min(valid, key=lambda value: abs(value))


def register_name(addr):
    if REG_CELL0_MV <= addr <= REG_CELL31_MV:
        off = addr - REG_CELL0_MV
        if off % 2 == 0:
            return 'cell{:02d}_mv'.format((off // 2) + 1)
        return 'cell_alt{:02d}_mv'.format(off + 1)
    return REGISTER_NAMES.get(addr, 'reg_0x{:04X}'.format(addr))


def describe_cell_register(addr, value):
    mv = normalize_cell_mv(value)
    off = addr - REG_CELL0_MV
    if off % 2 == 0:
        label = 'cell{:02d}'.format((off // 2) + 1)
    else:
        label = 'cell_alt{:02d}'.format(off + 1)
    if mv is None:
        return '{} raw=0x{:04X}'.format(label, value)
    return '{}={:.3f}V raw=0x{:04X}'.format(label, mv / 1000.0, value)


def describe_register(addr, value, values_by_addr=None):
    if REG_CELL0_MV <= addr <= REG_CELL31_MV:
        return describe_cell_register(addr, value)

    if addr == REG_CELL_AVG_MV:
        mv = normalize_cell_mv(value)
        return 'cell_avg={}'.format('{:.3f}V'.format(mv / 1000.0) if mv else 'raw0x{:04X}'.format(value))
    if addr == REG_CELL_DIFF_MV:
        return 'cell_diff={}mV'.format(normalize_delta_mv(value))
    if addr == REG_MAX_MIN_CELL_IDX:
        return 'cell_idx max#{} min#{}'.format((value >> 8) & 0xFF, value & 0xFF)
    if addr in (REG_TEMP_MOS_DECIC, REG_TEMP_BAT1_DECIC, REG_TEMP_BAT2_DECIC):
        return '{}={:.1f}C'.format(register_name(addr), be16s([(value >> 8) & 0xFF, value & 0xFF], 0) / 10.0)
    if addr == REG_BALANCE_CURRENT_MA_I16:
        signed = value - 0x10000 if value & 0x8000 else value
        return 'balance_current={:.3f}A'.format(signed / 1000.0)
    if addr == REG_BALANCE_SOC_U8X2:
        soc = decode_pct_byte_pair(value, False)
        return 'balance=0x{:02X} SOC={}%'.format((value >> 8) & 0xFF, soc if soc is not None else '-')
    if addr == REG_SOH_PRECHARGE_U8X2:
        soh = decode_pct_byte_pair(value, True)
        return 'SOH={}% precharge=0x{:02X}'.format(soh if soh is not None else '-', value & 0xFF)

    values = values_by_addr or {}
    if addr == REG_PACK_VOLT_MV_U32:
        combined = best_u32(values, addr, 1000, 200000)
        return 'pack_v={}'.format('{:.3f}V'.format(combined / 1000.0) if combined is not None else 'hi=0x{:04X}'.format(value))
    if addr == REG_PACK_CURRENT_MA_I32:
        combined = best_i32(values, addr, 1000000)
        return 'pack_i={}'.format('{:+.3f}A'.format(combined / 1000.0) if combined is not None else 'hi=0x{:04X}'.format(value))
    if addr == REG_PACK_WATT_MW_U32:
        combined = best_i32(values, addr, 200000000)
        return 'pack_p={}'.format('{:+.1f}W'.format(combined / 1000.0) if combined is not None else 'hi=0x{:04X}'.format(value))
    if addr == REG_ALARM_U32:
        combined = best_u32(values, addr, 0, 0xFFFFFFFF)
        return 'alarm=0x{:08X} ({})'.format(combined, alarm_list(combined)) if combined is not None else 'alarm_hi=0x{:04X}'.format(value)
    if addr == REG_REMAIN_MAH_I32:
        combined = best_i32(values, addr, 500000000)
        return 'remain={}'.format('{:.2f}Ah'.format(combined / 1000.0) if combined is not None else 'hi=0x{:04X}'.format(value))
    if addr == REG_FULL_MAH_U32:
        combined = best_u32(values, addr, 0, 500000000)
        return 'full={}'.format('{:.2f}Ah'.format(combined / 1000.0) if combined is not None else 'hi=0x{:04X}'.format(value))
    if addr == REG_CYCLES_U32:
        combined = best_u32(values, addr, 0, 1000000)
        return 'cycles={}'.format(combined if combined is not None else 'hi=0x{:04X}'.format(value))

    return '{}=0x{:04X}'.format(register_name(addr), value)


def parse_request(raw, crc, expected_crc, crc_ok):
    return {
        'raw': bytes(raw),
        'type': 'request',
        'slave': raw[0],
        'func': raw[1],
        'start': be16(raw, 2),
        'count': be16(raw, 4),
        'crc': crc,
        'expected_crc': expected_crc,
        'crc_ok': crc_ok,
    }


def parse_response(raw, request, crc, expected_crc, crc_ok):
    byte_count = raw[2]
    regs = []
    start = request.get('start') if request else None
    for idx in range(byte_count // 2):
        addr = (start + idx) if start is not None else None
        regs.append({
            'addr': addr,
            'value': be16(raw, 3 + (idx * 2)),
            'data_index': 3 + (idx * 2),
        })
    return {
        'raw': bytes(raw),
        'type': 'response',
        'slave': raw[0],
        'func': raw[1],
        'byte_count': byte_count,
        'start': start,
        'count': len(regs),
        'registers': regs,
        'crc': crc,
        'expected_crc': expected_crc,
        'crc_ok': crc_ok,
    }


def parse_exception(raw, crc, expected_crc, crc_ok):
    return {
        'raw': bytes(raw),
        'type': 'exception',
        'slave': raw[0],
        'func': raw[1] & 0x7f,
        'exception_func': raw[1],
        'exception_code': raw[2],
        'crc': crc,
        'expected_crc': expected_crc,
        'crc_ok': crc_ok,
    }


def parse_frame(raw, request=None):
    raw = bytes(raw)
    if len(raw) < 5:
        raise ValueError('frame too short')

    crc = frame_crc(raw)
    expected_crc = modbus_crc16(raw[:-2])
    crc_ok = crc == expected_crc
    func = raw[1]

    if func & 0x80:
        if len(raw) != 5:
            raise ValueError('invalid exception frame length')
        return parse_exception(raw, crc, expected_crc, crc_ok)

    if func not in FUNCTION_NAMES:
        raise ValueError('unsupported function 0x{:02X}'.format(func))

    if len(raw) == 8:
        return parse_request(raw, crc, expected_crc, crc_ok)

    byte_count = raw[2]
    expected_len = 3 + byte_count + 2
    if byte_count >= 2 and byte_count % 2 == 0 and len(raw) == expected_len:
        return parse_response(raw, request, crc, expected_crc, crc_ok)

    raise ValueError('could not classify Modbus RTU frame')


def frame_complete(raw):
    raw = bytes(raw)
    if len(raw) < 5:
        return False

    func = raw[1]
    if func & 0x80:
        return len(raw) >= 5

    if func not in FUNCTION_NAMES:
        return len(raw) >= 8

    if len(raw) >= 3:
        byte_count = raw[2]
        if byte_count >= 2 and byte_count % 2 == 0:
            expected_len = 3 + byte_count + 2
            if len(raw) < expected_len:
                if len(raw) == 8 and modbus_crc16(raw[:6]) == frame_crc(raw[:8]):
                    return True
                return False
            return True

    return len(raw) >= 8


def describe_cell_registers(registers):
    cells = []
    for reg in registers:
        addr = reg.get('addr')
        if addr is None or not (REG_CELL0_MV <= addr <= REG_CELL31_MV):
            continue
        mv = normalize_cell_mv(reg.get('value', 0))
        if mv is None:
            continue
        off = addr - REG_CELL0_MV
        doc_idx = (off // 2) + 1 if off % 2 == 0 else None
        compact_idx = off + 1
        cells.append((addr, doc_idx or compact_idx, mv))
    if not cells:
        return None
    min_cell = min(cells, key=lambda item: item[2])
    max_cell = max(cells, key=lambda item: item[2])
    return 'cells count={} min={:.3f}V#{} max={:.3f}V#{}'.format(
        len(cells),
        min_cell[2] / 1000.0,
        min_cell[1],
        max_cell[2] / 1000.0,
        max_cell[1],
    )


def describe_registers(registers):
    if not registers:
        return '0 register words'

    values = {reg['addr']: reg['value'] for reg in registers if reg.get('addr') is not None}
    cell_text = describe_cell_registers(registers)
    if cell_text:
        return cell_text

    priority = (
        REG_PACK_VOLT_MV_U32,
        REG_PACK_CURRENT_MA_I32,
        REG_BALANCE_SOC_U8X2,
        REG_SOH_PRECHARGE_U8X2,
        REG_TEMP_MOS_DECIC,
        REG_TEMP_BAT1_DECIC,
        REG_TEMP_BAT2_DECIC,
        REG_ALARM_U32,
        REG_CELL_AVG_MV,
        REG_CELL_DIFF_MV,
        REG_MAX_MIN_CELL_IDX,
        REG_FULL_MAH_U32,
        REG_CYCLES_U32,
    )
    known = []
    for addr in priority:
        if addr in values:
            known.append(describe_register(addr, values[addr], values))
    if known:
        return ', '.join(known[:7])

    if registers[0].get('addr') is not None:
        start = registers[0]['addr']
        end = registers[-1]['addr']
        return 'regs 0x{:04X}..0x{:04X}'.format(start, end)
    return '{} register words'.format(len(registers))


def describe_frame(frame):
    typ = frame.get('type')
    if typ == 'request':
        name = FUNCTION_NAMES.get(frame['func'], 'function')
        match = 'poll-block' if any(frame['start'] == start and frame['count'] == count for start, count in POLL_BLOCKS) else 'custom'
        return '{} start=0x{:04X} count={} {}'.format(name, frame['start'], frame['count'], match)
    if typ == 'response':
        regs = frame.get('registers', [])
        if frame.get('start') is not None and regs:
            return 'response regs 0x{:04X}..0x{:04X}: {}'.format(
                regs[0]['addr'], regs[-1]['addr'], describe_registers(regs))
        return 'response {} bytes'.format(frame.get('byte_count', 0))
    if typ == 'exception':
        return 'exception func=0x{:02X} code=0x{:02X}'.format(
            frame.get('func', 0), frame.get('exception_code', 0))
    return 'frame'


def frame_summary(frame, direction=''):
    prefix = (direction + ' ') if direction else ''
    crc_text = 'OK' if frame.get('crc_ok') else 'BAD'
    typ = frame.get('type')

    if typ == 'request':
        return '{}JKBMS Modbus req slave=0x{:02X} func=0x{:02X} start=0x{:04X} count={} crc={}'.format(
            prefix, frame['slave'], frame['func'], frame['start'], frame['count'], crc_text)
    if typ == 'response':
        regs = frame.get('registers', [])
        reg_text = ''
        if frame.get('start') is not None and regs:
            reg_text = ' regs=0x{:04X}..0x{:04X}'.format(regs[0]['addr'], regs[-1]['addr'])
        return '{}JKBMS Modbus rsp slave=0x{:02X} func=0x{:02X}{} bytes={} crc={}'.format(
            prefix, frame['slave'], frame['func'], reg_text, frame.get('byte_count', 0), crc_text)
    if typ == 'exception':
        return '{}JKBMS Modbus exception slave=0x{:02X} func=0x{:02X} code=0x{:02X} crc={}'.format(
            prefix, frame['slave'], frame['func'], frame['exception_code'], crc_text)
    return '{}JKBMS Modbus frame crc={}'.format(prefix, crc_text)
