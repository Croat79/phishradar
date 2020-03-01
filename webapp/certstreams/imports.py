import importlib


def import_class(path):
    module_path, _, class_name = path.rpartition('.')
    module = importlib.import_module(module_path)
    return getattr(module, class_name)
