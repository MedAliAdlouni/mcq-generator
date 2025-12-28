from markitdown import MarkItDown
from typing import BinaryIO, Union

def _extract_from_stream(stream: BinaryIO) -> str:
    stream.seek(0)
    md = MarkItDown()
    result = md.convert(stream)
    return result.text_content.strip()

def extract_text_from_file(stream: Union[BinaryIO, str]) -> str:
    """Extract text from word/pdf file and convert it to markdown.
    Accepts either a file-like binary stream or a filesystem path (str).
    """
    if isinstance(stream, str):
        with open(stream, "rb") as f:
            return _extract_from_stream(f)
    else:
        return _extract_from_stream(stream)