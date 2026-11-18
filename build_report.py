"""Point d'entrée conservé : le rapport est maintenant produit au format Word."""
from pathlib import Path
import runpy

if __name__ == '__main__':
    runpy.run_path(str(Path(__file__).with_name('build_report_word.py')), run_name='__main__')
