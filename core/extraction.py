from markitdown import MarkItDown
from typing import BinaryIO

def extract_text_from_file(stream: BinaryIO) -> str:
    """Extract text from word/pdf file and converts it in markdown format.
    Returns a string format. 

    Args:
        path (str): path of the file

    Returns:
        str: markdown consisting of the text extracted from the file
    """
    stream.seek(0)
    md = MarkItDown()
    result = md.convert(stream)
    return result.text_content.strip()