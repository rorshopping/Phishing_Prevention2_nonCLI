from array import array

BIAS = 0x84
CLIP = 32635
SIGN_BIT = 0x80
QUANT_MASK = 0x0F
SEG_SHIFT = 4
SEG_MASK = 0x70

EXP_LUT = (
    0, 0, 1, 1, 2, 2, 2, 2, 3, 3, 3, 3, 3, 3, 3, 3,
    4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4, 4,
    5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
    5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5, 5,
    6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
    6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
    6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
    6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6, 6,
    7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
    7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
    7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
    7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
    7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
    7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
    7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
    7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7, 7,
)


def pcm16_to_ulaw(sample: int) -> int:
    sample = max(-32768, min(32767, sample))
    sign = (sample >> 8) & 0x80
    if sign:
        sample = -sample
    if sample > CLIP:
        sample = CLIP
    sample += BIAS
    exponent = EXP_LUT[(sample >> 7) & 0xFF]
    mantissa = (sample >> (exponent + 3)) & QUANT_MASK
    return (~(sign | (exponent << SEG_SHIFT) | mantissa)) & 0xFF


def ulaw_to_pcm16(b: int) -> int:
    b = (~b) & 0xFF
    sign = b & SIGN_BIT
    exponent = (b >> SEG_SHIFT) & 0x07
    mantissa = b & QUANT_MASK
    sample = ((mantissa << 3) + BIAS) << exponent
    sample -= BIAS
    return -sample if sign else sample


_ULAW_TO_PCM = tuple(ulaw_to_pcm16(i) for i in range(256))


def ulaw_bytes_to_pcm16(data: bytes) -> bytes:
    a = array("h", (_ULAW_TO_PCM[x] for x in data))
    return a.tobytes()


def pcm16_bytes_to_ulaw(data: bytes) -> bytes:
    a = array("h")
    a.frombytes(data)
    return bytes(pcm16_to_ulaw(s) for s in a)


def upsample_2x(data: bytes) -> bytes:
    a = array("h")
    a.frombytes(data)
    out = array("h", [0]) * (len(a) * 2)
    for i, s in enumerate(a):
        out[2 * i] = s
        out[2 * i + 1] = s
    return out.tobytes()


def downsample_2x(data: bytes) -> bytes:
    a = array("h")
    a.frombytes(data)
    return a[0::2].tobytes()


def mulaw_to_pcm16k(data: bytes) -> bytes:
    pcm8k = ulaw_bytes_to_pcm16(data)
    return upsample_2x(pcm8k)


def pcm16k_to_mulaw(data: bytes) -> bytes:
    pcm8k = downsample_2x(data)
    return pcm16_bytes_to_ulaw(pcm8k)
