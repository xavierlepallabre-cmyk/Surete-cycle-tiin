"""Calcule la version du cache hors ligne à partir du contenu des fichiers.

Usage (à la racine du dépôt) :
    python tools/version.py          # met à jour VERSION dans service-worker.js
    python tools/version.py --check  # échoue si VERSION ne correspond pas aux fichiers

Toute modification d'une page change la version : les appareils des élèves
reçoivent alors la proposition « Mettre à jour ». Plus besoin d'y penser.
"""
import hashlib, pathlib, re, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SW = ROOT / 'service-worker.js'

def assets():
    src = SW.read_text(encoding='utf-8')
    block = re.search(r'const ASSETS = \[(.*?)\];', src, re.S).group(1)
    files = [f.strip().strip("'\"") for f in block.split(',') if f.strip()]
    return [f[2:] for f in files if f not in ('./',)]

def compute():
    h = hashlib.sha256()
    for rel in sorted(assets()):
        path = ROOT / rel
        if not path.exists():
            sys.exit(f'Fichier listé dans ASSETS mais absent : {rel}')
        h.update(rel.encode()); h.update(path.read_bytes())
    return h.hexdigest()[:10]

def main():
    version = compute()
    src = SW.read_text(encoding='utf-8')
    current = re.search(r"const VERSION = '([^']*)';", src).group(1)
    if '--check' in sys.argv:
        if current != version:
            sys.exit(f'VERSION obsolète ({current}) : lancez « python tools/version.py » (attendu {version}).')
        print(f'VERSION à jour : {version}')
        return
    SW.write_text(src.replace(f"const VERSION = '{current}';", f"const VERSION = '{version}';"), encoding='utf-8')
    print(f'VERSION : {current} → {version}')

if __name__ == '__main__':
    main()
