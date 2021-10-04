from .tools._rename import Rename

def rename(filepath):
    run = Rename(filepath)
    run.rename()
