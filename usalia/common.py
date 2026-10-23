"""Shared validation and transactional output helpers."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
from contextlib import contextmanager

class FormatError(ValueError):
    pass

def require(condition, message):
    if not condition:
        raise FormatError(message)

def sha256(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda: f.read(8 * 1024 * 1024), b''):
            h.update(chunk)
    return h.hexdigest()

def read_at(path, offset, size):
    require(offset >= 0 and size >= 0, 'Negative offset/size')
    with Path(path).open('rb') as f:
        f.seek(offset)
        b = f.read(size)
    require(len(b) == size, 'Truncated input')
    return b

@contextmanager
def atomic_output(output, source=None):
    """Never edit the source, never silently replace an existing output."""
    output = Path(output)
    require(source is None or output.resolve() != Path(source).resolve(), 'Output equals source')
    require(not output.exists(), f'Output already exists: {output}')
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix='.' + output.name + '.', dir=output.parent)
    os.close(fd)
    try:
        yield Path(tmp)
        # Same-directory hardlink installs the finished file atomically and exclusively.
        # FileExistsError is intentionally not bypassed: another process may have created it.
        try:
            os.link(tmp, output)
        except FileExistsError:
            raise
        except OSError as ex:
            raise OSError('Output filesystem must support hardlinks; build in a local working folder before copying to SD') from ex
        os.unlink(tmp)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise

def write_bytes(path, data, source=None):
    with atomic_output(path, source) as tmp:
        tmp.write_bytes(data)

def write_json(path, data):
    write_bytes(path, (json.dumps(data, ensure_ascii=False, indent=2) + '\n').encode('utf-8'))
