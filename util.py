from typing import Any, Callable
import yaml


with open('settings.yml', 'r') as f:
  settings = yaml.safe_load(f)

log_lebel = settings.get('logLevel')

def print_info(func: Callable) -> Any:
  def wraper(*args, **kwargs):
    # print function name
    if log_lebel == 'debug':
      print(f'Called Func : {func.__name__}')
      print(f'args: {args}, kwargs: {kwargs}')
    result = func(*args, **kwargs)
    return result
  return wraper