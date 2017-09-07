import pkgutil

def list_modules(package = './modules'):
  return [module for _, module, _ in pkgutil.iter_modules(package)]


  # https://stackoverflow.com/a/1310912
