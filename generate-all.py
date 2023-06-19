from pathlib import Path
import generate

for input_file in Path('translations').glob('*.txt'):
  generate.generate(input_file)
