from markitdown import MarkItDown
from typing import BinaryIO, Union

def _extract_from_stream(stream: BinaryIO) -> str:
    stream.seek(0)  # Move to the beginning of the file
    # Check if the file is empty by seeking to the end and checking position
    stream.seek(0, 2)  # Seek to end (2 = SEEK_END)
    file_size = stream.tell()  # Get the current position (which is the file size)
    if file_size == 0:
        return ""
    stream.seek(0)  # Reset to beginning for conversion
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