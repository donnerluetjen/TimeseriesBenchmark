import sys


def transformFloatToGermanKomma(value):
    return str(value).replace('.', ',')


def progress_start(message):
    print(f'{message} ', sep='', end='', flush=True)
    

def progress_increase():
    print('.', sep='', end='', flush=True)


def progress_end():
    print('\nDone', flush=True)
    