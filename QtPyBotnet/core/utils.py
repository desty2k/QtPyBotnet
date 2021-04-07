
def base64_to_image(image: str) -> str:
    from zlib import decompress
    from base64 import b64decode
    return decompress(b64decode(image)).decode()
