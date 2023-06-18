from pathlib import Path
import subprocess
import json
import datetime

HERE = Path(__file__).parent
tracks_dir = Path('~/tracks').expanduser()
output_dir = HERE / 'translations'

def get_meta(track: Path):
  cmd = [
    'ffprobe',
    '-v', 'quiet',
    '-print_format', 'json',
    '-show_format', '-show_streams',
    track
  ]
  result = subprocess.run(cmd, capture_output=True)
  source = json.loads(result.stdout)['format']['tags']
  meta = {}
  for key in ('title', 'artist', 'comment', 'lyrics'):
    meta[key] = source[key]
  return meta

def get_track():
  search = input('Enter name of file: ')

  tracks = tracks_dir.glob('**/*.m4a')
  for track in tracks:
    if search in track.stem.lower():
      return track

  return None

def get_text_file_chunks(meta: dict):
  yield 'title: '
  yield f'trackTitle: {meta["title"]}'
  yield f'artist: {meta["artist"]}'
  yield f'link: {meta["comment"]}'
  yield f'data: {datetime.date.today():%Y-%m-%d}'
  yield f'draft: true'
  yield ''
  lyrics = meta['lyrics'].replace('\r', '\n')
  yield lyrics

def generate_text_file(meta: dict):
  output_file = output_dir / Path(meta['title'].lower().replace(' ', '-')).with_suffix('.txt')
  with output_file.open('w', encoding='utf8') as fp:
   for line in get_text_file_chunks(meta):
     fp.write(line + '\n')

if __name__ == '__main__':
  track = get_track()
  meta = get_meta(track)
  generate_text_file(meta)
