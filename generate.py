"""
Convert text file to markdown and move into Hugo site
"""
import sys
import re
from pathlib import Path
from dataclasses import dataclass
import itertools

content_dir = Path(__file__).parent / 'site/content'

if len(sys.argv) > 1:
  input_file = Path(sys.argv)
else:
  txt_files = list(Path('translations').glob('*.txt'))
  txt_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
  input_file = txt_files[0]

output_file = (content_dir / Path(input_file.name)).with_suffix('.md')

@dataclass
class TranslatedLine:
  source: str
  target: str
  correction: str

@dataclass
class Meta:
  title: str
  artist: str
  link: str

@dataclass
class Page:
  meta: Meta
  paras: list

class Newline:
  def __str__(self): return 'Newline'

def tokenize(input_file: Path):
  lines = get_lines(input_file)
  yield tokenize_meta(lines)

  while True:
    line = next(lines, None)

    match line:
      case None:
        return
      case '':
        yield Newline()
      case line:
        match tokenize_translated_line(line, lines):
          case (translated_line, extra):
            yield translated_line
            if extra is not None:
              lines = itertools.chain([extra], lines)
          case _:
            continue

def tokenize_meta(lines):
  meta = Meta(None, None, None)

  for line in lines:
    if match := re.match(r'^(title|artist|link)\:\s*(.*)', line):
      key, value = match.groups()
      setattr(meta, key, value)
    else:
      break

  return meta

def tokenize_translated_line(source_line, lines):
  translated_line = TranslatedLine(source_line, next(lines), None)
  extra = next(lines, None)
  if extra is None:
    return translated_line, None

  if extra.startswith('；'):
    translated_line.correction = extra[1:]
    extra = None

  return translated_line, extra

def get_lines(input_file: Path):
  with input_file.open() as fp:
    for line in fp:
      yield line.strip()

if __name__ == '__main__':
  for token in tokenize(input_file):
    print(token)
