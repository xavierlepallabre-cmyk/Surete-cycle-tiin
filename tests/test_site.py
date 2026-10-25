"""Tests de non-régression de Sûreté & Cycle TIIN.

Prérequis (une fois) :
    pip install playwright
    python -m playwright install chromium

Lancement, à la racine du dépôt :
    python tests/test_site.py

Ce que le script vérifie, dans un vrai navigateur (Chromium) :
  1. la version du cache correspond au contenu des fichiers (tools/version.py) ;
  2. chaque page s'ouvre sans erreur JavaScript, en thème clair et sombre ;
  3. sûreté et accidents : chaque vue et chaque étape s'affichent, les mises en
     situation se terminent, le synoptique et la visite guidée répondent ;
  4. aucune page ne déborde horizontalement à 360 px de large ;
  5. la page maître ouvre les six parcours, les liens entre parcours restent
     dans l'application ;
  6. hors ligne : après une première visite, tout reste accessible ;
  7. une nouvelle version déclenche le bandeau « Mettre à jour ».
Le script s'arrête au premier échec et affiche ce qui ne va pas.
"""
import asyncio, functools, http.server, pathlib, shutil, subprocess, sys, tempfile, threading

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ['index', 'amont', 'rep1300', 'lahague', 'andra', 'surete', 'accidents']
OK, FAILS = [], []

def check(cond, msg):
    (OK if cond else FAILS).append(msg)
    print(('  ✓ ' if cond else '  ✗ ') + msg)

def serve(directory):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a): pass
    handler = functools.partial(Quiet, directory=str(directory))
    srv = http.server.ThreadingHTTPServer(('127.0.0.1', 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f'http://127.0.0.1:{srv.server_address[1]}/'

async def main():
    from playwright.async_api import async_playwright
    print('1. Version du cache')
    r = subprocess.run([sys.executable, str(ROOT / 'tools/version.py'), '--check'], capture_output=True, text=True)
    check(r.returncode == 0, (r.stdout or r.stderr).strip())

    srv, base = serve(ROOT)
    async with async_playwright() as p:
        browser = await p.chromium.launch()

        print('2. Ouverture des pages (clair et sombre)')
        for scheme in ('light', 'dark'):
            for name in PAGES:
                page = await browser.new_page(color_scheme=scheme)
                errors = []
                page.on('pageerror', lambda e: errors.append(str(e)))
                await page.goto(base + f'{name}.html')
                await page.wait_for_timeout(400)
                check(not errors, f'{name}.html ({scheme}) sans erreur' + (f' : {errors[0]}' if errors else ''))
                await page.close()

        print('3. Sûreté et accidents : vues, étapes, quiz, synoptique')
        for name in ('surete', 'accidents'):
            page = await browser.new_page()
            errors = []
            page.on('pageerror', lambda e: errors.append(str(e)))
            await page.goto(base + f'{name}.html')
            res = await page.evaluate('''() => { const out = {views: 0, steps: 0, quiz: 0, nodes: 0};
              for (const v of VIEW_ORDER) { openView(v); const V = VIEWS[v];
                if (V.quiz) { for (let t = 0; t < ACTIVITIES.length; t++) { qStart(t);
                    for (const st of ACTIVITIES[t].steps) { document.querySelector(`[data-a="${st.answer}"]`).click(); document.getElementById('qGo').click(); }
                    if (document.querySelector('#qcard h3')) out.quiz++; } qBilan(); continue; }
                out.views++; for (let i = 0; i <= V.steps.length; i++) { setStep(i); out.steps++; } }
              showSyn(); for (const n of TOUR) { selectNode(n); selNode = null; out.nodes++; }
              return out; }''')
            check(not errors, f'{name} : {res["views"]} vues, {res["steps"]} étapes, {res["quiz"]} situations, {res["nodes"]} fiches, sans erreur' + (f' ({errors[0]})' if errors else ''))
            await page.close()

        print('4. Largeur mobile (360 px)')
        for name in PAGES:
            page = await browser.new_page(viewport={'width': 360, 'height': 740})
            await page.goto(base + f'{name}.html')
            await page.wait_for_timeout(300)
            over = await page.evaluate('document.documentElement.scrollWidth - innerWidth')
            check(over <= 1, f'{name}.html : pas de défilement horizontal' + (f' (+{over} px)' if over > 1 else ''))
            await page.close()

        print('5. Page maître et liens entre parcours')
        ctx = await browser.new_context()
        page = await ctx.new_page()
        await page.goto(base)
        for i in range(1, 7):
            await page.keyboard.press(f'Alt+{i}')
            await page.wait_for_timeout(500)
        n = await page.evaluate("document.querySelectorAll('iframe').length")
        check(n == 6, f'les six parcours s’ouvrent dans la page maître ({n})')
        await page.keyboard.press('Alt+1'); await page.wait_for_timeout(300)
        amont = next(f for f in page.frames if f.url.endswith('amont.html'))
        await amont.evaluate("document.querySelector('a[href=\"lahague.html\"]').click()")
        await page.wait_for_timeout(400)
        tab = await page.evaluate("document.querySelector('#switch [aria-current]').textContent")
        check(tab.strip() == 'La Hague', f'le lien Cycle amont → La Hague reste dans l’application ({tab.strip()})')

        print('6. Hors ligne')
        await page.goto(base)
        await page.evaluate('navigator.serviceWorker.ready.then(() => 1)')
        await page.wait_for_timeout(1500)
        cached = await page.evaluate("caches.keys().then(k => Promise.all(k.map(n => caches.open(n).then(c => c.keys())))).then(a => a.flat().length)")
        check(cached >= 14, f'{cached} fichiers en cache')
        await ctx.set_offline(True)
        for name in PAGES:
            p2 = await ctx.new_page()
            try:
                await p2.goto(base + f'{name}.html')
                title = await p2.title()
                check(bool(title), f'{name}.html accessible hors ligne')
            except Exception as e:
                check(False, f'{name}.html hors ligne : {e}')
            await p2.close()
        await ctx.close()

        print('7. Proposition de mise à jour')
        with tempfile.TemporaryDirectory() as tmp:
            copy = pathlib.Path(tmp) / 'site'
            shutil.copytree(ROOT, copy, ignore=shutil.ignore_patterns('.git', 'tests'))
            srv2, base2 = serve(copy)
            ctx = await browser.new_context()
            page = await ctx.new_page()
            await page.goto(base2)
            await page.evaluate('navigator.serviceWorker.ready.then(() => 1)')
            await page.wait_for_timeout(1000)
            sw = copy / 'service-worker.js'
            sw.write_text(sw.read_text(encoding='utf-8').replace("const VERSION = '", "const VERSION = 'test-"), encoding='utf-8')
            await page.reload(); await page.wait_for_timeout(2500)
            shown = await page.evaluate("!document.getElementById('updateBar').hidden")
            check(shown, 'le bandeau « Mettre à jour » apparaît')
            if shown:
                await page.click('#updateBtn'); await page.wait_for_timeout(2000)
                keys = await page.evaluate('caches.keys()')
                check(len(keys) == 1 and 'test-' in keys[0], 'la nouvelle version remplace l’ancienne dans le cache')
            await ctx.close(); srv2.shutdown()
        await browser.close()
    srv.shutdown()
    print(f'\n{len(OK)} vérifications réussies, {len(FAILS)} échec(s).')
    sys.exit(1 if FAILS else 0)

asyncio.run(main())
