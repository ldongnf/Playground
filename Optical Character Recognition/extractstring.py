from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract
import optparse

# extract string using pytesseract

def extract_string(path):
    im = Image.open(path)

    im = im.convert('RGB')
    im = im.filter(ImageFilter.SHARPEN)
    enhancer = ImageEnhance.Contrast(im)
    # contrast
    im = enhancer.enhance(2)
    im = im.convert('L')
    #im.show()
    text = pytesseract.image_to_string(im)
    words = text.split()
    return " ".join(words)


def commandline():
    # the command line
    parser = optparse.OptionParser("usage%prog "+"-t <image_file>");
    parser.add_option('-t',dest='filename',type='string',help='type');
    (options, args) = parser.parse_args()
    if options.filename == None:
        print parser.usage
        exit(0)
    else:
        filename = options.filename
        print '--- Start recognize text from image ---'
        print extract_string(filename)
        print "------ Done -------"

commandline()
