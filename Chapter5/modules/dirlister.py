import os


def run(**args):

    print('[*] In module dirlister.')
    files = os.listdir('.')

    return str(files)