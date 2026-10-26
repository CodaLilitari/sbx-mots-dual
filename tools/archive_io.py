"""Strict, byte-preserving JK/MotS GOB/GOO reader for this conversion."""
import hashlib
import struct
from pathlib import Path, PurePosixPath

def digest(data):
    return hashlib.sha256(data).hexdigest()

def read_gob(path):
    data = Path(path).read_bytes()
    magic, version, table = struct.unpack_from('<4sII', data)
    if magic != b'GOB ' or version != 20:
        raise ValueError(f'Unexpected archive header: {path}')
    count, = struct.unpack_from('<I', data, table)
    if table + 4 + count * 136 > len(data):
        raise ValueError('Invalid entry table')
    entries = {}
    for i in range(count):
        off, size, raw = struct.unpack_from('<II128s', data, table + 4 + i * 136)
        name = raw.split(b'\0')[0].decode('latin1').replace('\\', '/').lower()
        # Historical Patch Commander archives use one archive-root slash.
        if name.startswith('/') and not name.startswith('//'):
            name = name[1:]
        p = PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts or ':' in name or name in entries:
            raise ValueError(f'Unsafe or duplicate archive member: {name}')
        if off + size > len(data):
            raise ValueError(f'Truncated member: {name}')
        entries[name] = data[off:off+size]
    return entries

def extract(entries, dest):
    dest = Path(dest).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    for name, data in entries.items():
        target = dest / name
        if not target.resolve().is_relative_to(dest):
            raise ValueError('Unsafe extraction path')
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)

def write_gob(entries, dest):
    names = sorted(entries)
    offset = 16 + 136 * len(names)
    table = bytearray(struct.pack('<4sIII', b'GOB ', 20, 12, len(names)))
    payload = bytearray()
    for name in names:
        encoded = name.replace('/', '\\').encode('ascii')
        if len(encoded) > 127:
            raise ValueError('Member name too long')
        data = entries[name]
        table += struct.pack('<II128s', offset, len(data), encoded)
        payload += data
        offset += len(data)
    Path(dest).write_bytes(table + payload)
    if read_gob(dest) != entries:
        raise ValueError('Archive round trip mismatch')
