from app.models.file.texfile import TexFile
from app.models.file.plaintextfile import PlainTextFile
from app.models.file.binaryfile import BinaryFile
from app.models.file.pdf import PDF
from app.models.file.image import Image

ALLOWEDMIMETYPES = {
    'plaintext': {
        'text/x-tex': TexFile,                      # Linux
        'application/x-tex': TexFile,               # Windows
        'text/plain': PlainTextFile,

        'text/x-c': PlainTextFile,                  # C Source File
        'text/html': PlainTextFile,                 # HTML
        'text/x-java-source,java': PlainTextFile    # Java Source File
    },
    'binary': {
        'image/png': Image,
        'image/jpg': Image,
        'image/jpeg': Image,
        'image/gif': Image,
        'application/tga': Image,

        'application/pdf': PDF,
        'application/postscript': BinaryFile,
        'application/x-dvi': BinaryFile,
        'application/zip': BinaryFile,
        'application/CDFV2-corrupt': BinaryFile
    }
}