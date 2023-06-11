"""
Convert text file to markdown and move into Hugo site
"""
import sys
import re
from pathlib import Path
from dataclasses import dataclass
from typing import List
import datetime
import enum

content_dir = Path(__file__).parent / 'site/content'

class LineType(enum.Enum):
  NORMAL = 1
  CONTINUATION = 2
  CORRECTION = 3
  NOTE = 4

@dataclass
class Line:
  content: str
  type = LineType

  def __init__(self, line):
    if line.startswith('  '):
      self.type = LineType.CONTINUATION
      self.content = line.lstrip()
    elif line.startswith(';') or line.startswith('；'):
      self.type = LineType.CORRECTION
      self.content = line[1:]
    elif line.startswith(':') or line.startswith('：'):
      self.type = LineType.NOTE
      self.content = line[1:]
    else:
      self.type = LineType.NORMAL
      self.content = line

  def __str__(self):
    return f'Line(content={self.content!r}, type={self.type.name})'

@dataclass
class Meta:
  title: str
  artist: str
  link: str
  date: str

  def __init__(self):
    self.title = None
    self.artist = None
    self.link = None
    self.date = None

@dataclass
class TranslatedBlock:
  source: str
  target: str
  correction: str
  note: str

  def __init__(self, line):
    self.source = line
    self.target = self.correction = self.note = None

@dataclass
class Stanza:
  lines = List[TranslatedBlock]

  def __init__(self):
    self.lines = []

  @property
  def last(self):
    return self.lines[-1] if len(self.lines) != 0 else None

  def add_line(self, line: Line):
    if self.last is None:
      self.lines.append(TranslatedBlock(line.content))
    elif line.type == LineType.CORRECTION:
      self.last.correction = line.content
    elif line.type == LineType.NOTE:
      self.last.note = line.content
    elif line.type == LineType.CONTINUATION:
      self.last.source += '\n' + line.content
    elif self.last.source is not None and self.last.target is not None:
      self.lines.append(TranslatedBlock(line.content))
    else:
      self.last.target = line.content

@dataclass
class Page:
  meta: Meta
  stanzas: list

class Newline:
  def __str__(self): return 'Newline'

def tokenize(input_file: Path):
  lines = get_lines(input_file)
  yield tokenize_meta(lines)

  for line in lines:
    match line:
      case None:
        return
      case '':
        yield Newline()
      case line:
        yield Line(line)

def tokenize_meta(lines):
  meta = Meta()

  for line in lines:
    if match := re.match(r'^(title|artist|link|date)\:\s*(.*)', line):
      key, value = match.groups()
      setattr(meta, key, value)
    else:
      break

  return meta

def get_lines(input_file: Path):
  with input_file.open() as fp:
    for line in fp:
      yield line.rstrip()

def parse(tokens):
  meta = None
  stanzas = [Stanza()]

  for token in tokens:
    match token:
      case Newline():
        stanzas.append(Stanza())
      case Meta() as m:
        meta = m
      case Line() as line:
        stanzas[-1].add_line(line)

  return Page(meta, stanzas)

def get_markdown_chunks(page: Page):
  yield '---'
  meta = page.meta
  yield f'title: "{meta.title}"'
  yield f'artist: "{meta.artist}"'
  yield f'link: "{meta.link}"'
  if meta.link.startswith('https://youtu.be/'):
    embed_id = meta.link[len('https://youtu.be/'):]
    yield f'youtubeEmbedId: "{embed_id}"'
  dt = datetime.datetime.fromisoformat(meta.date)
  yield f'date: {dt.astimezone().isoformat()}'
  yield '---\n'

  yield '## DeepL translation\n'

  for stanza in page.stanzas:
    for tline in stanza.lines:
      yield tline.source
      yield f'<span class="target">{tline.target}</span>'
    yield ''

  yield '## Corrections\n'

  footnotes = []

  for stanza in page.stanzas:
    for tline in stanza.lines:
      yield tline.source
      if tline.correction is not None:
        if tline.note is None:
          footnote_ref = ''
        else:
          footnote_ref = f'[^{len(footnotes)+1}]'
          footnotes.append(tline.note)

        yield f'<span class="target"><del>{tline.target}</del> <span class="correction">{tline.correction}</span>{footnote_ref}</span>'
      else:
        yield f'<span class="target">{tline.target}</span>'
    yield ''

  if len(footnotes) > 0:
    for i, footnote in enumerate(footnotes, 1):
      yield f'[^{i}]: {footnote}'

def convert_page_to_markdown(page: Page, output_file: Path):
  with output_file.open('w', encoding='utf8') as fp:
    for chunk in get_markdown_chunks(page):
      fp.write(chunk + '\n')

if __name__ == '__main__':
  if len(sys.argv) > 1:
    input_file = Path(sys.argv)
  else:
    txt_files = list(Path('translations').glob('*.txt'))
    txt_files.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    input_file = txt_files[0]

  output_file = (content_dir / Path(input_file.name)).with_suffix('.md')

  tokens = tokenize(input_file)
  page = parse(tokens)
  convert_page_to_markdown(page, output_file)
