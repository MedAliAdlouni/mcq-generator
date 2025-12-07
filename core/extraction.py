from markitdown import MarkItDown


def extract_text_from_file(path: str) -> str:
    """Extract text from word/pdf file and converts it in markdown format.
    Returns a string format. 

    Args:
        path (str): path of the file

    Returns:
        str: markdown consisting of the text extracted from the file
    """
    md = MarkItDown()
    result = md.convert(path)
    return result.text_content.strip()