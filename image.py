from PIL import ExifTags, Image
# file formats that can be 'read' by PIL
FILETYPES = ['.bmp', '.dib', '.dcx', '.gif', '.im', '.jpg',
             '.jpe', '.jpeg', '.pcd', '.pcx', '.png', '.pbm',
             '.pgm', '.ppm', '.psd', '.tif', '.tiff', '.xbm', '.xpm']


def orientate(im):
    try:
        exif = dict((ExifTags.TAGS[k], v) for k, v in im._getexif().items() if k in ExifTags.TAGS)
        orientation = exif.get('Orientation', 1)
    except (KeyError, AttributeError):
        orientation = 1
    print('orientation', orientation)
    if orientation == 3:
        im = im.rotate(180, expand=True)
    elif orientation == 6:
        im = im.rotate(270, expand=True)
    elif orientation == 8:
        im = im.rotate(90, expand=True)
    elif orientation and orientation != 1:
        print('Unknown orientation:', orientation)
    return im


def rotate(path, degrees=-90):
    """
    Rotate the given photo the amount of given degrees, show it and save it
    @param path: The path to the image to edit
    @param degrees: The number of degrees to rotate the image
    """
    im = orientate(Image.open(path))
    rotated_im = im.rotate(degrees, expand=True)
    rotated_im.save(path)


def lucky(path):
    """

    """
    im = orientate(Image.open(path))
    im.im_feeling_lucky()
    im.save(path)
