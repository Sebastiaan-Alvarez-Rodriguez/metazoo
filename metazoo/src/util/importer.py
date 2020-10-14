import sys
import importlib

def import_full_path(full_path):
    if sys.version_info >= (3, 5):
        import importlib.util
        spec = importlib.util.spec_from_file_location('module.name', full_path)
        foo = importlib.util.module_from_spec(spec)
        return spec.loader.exec_module(foo)
    elif sys.version_info >= (3, 3):
        from importlib.machinery import SourceFileLoader
        return SourceFileLoader('module.name', full_path).load_module()
    elif sys.version_info <= (2, 9):
        import imp
        return imp.load_source('module.name', full_path)