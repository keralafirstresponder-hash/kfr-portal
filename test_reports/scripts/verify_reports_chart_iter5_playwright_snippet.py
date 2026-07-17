# Playwright snippet executed via mcp_browser_automation on 2026-07-17.
# URL tested: https://responder-registry.preview.emergentagent.com/admin/reports
try:
    await page.set_viewport_size({"width": 1440, "height": 900})
    await page.wait_for_load_state('domcontentloaded')
    await page.evaluate("""async () => {
        const r = await fetch('/api/auth/login', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({email: 'admin@kfr.org', password: 'Kfr@2026'})});
        if (!r.ok) throw new Error('login failed ' + r.status + ' ' + await r.text());
        const data = await r.json(); localStorage.setItem('kfr_token', data.token);
    }""")
    await page.goto('https://responder-registry.preview.emergentagent.com/admin/reports')
    await page.wait_for_selector('[data-testid="reports-title"]', timeout=20000)
    await page.wait_for_timeout(2000)
    report_info = await page.evaluate("""() => {
        const allCards = Array.from(document.querySelectorAll('div'));
        const card = allCards.find(el => (el.textContent || '').includes('Category distribution') && el.querySelector('svg'));
        if (!card) return {foundCard: false};
        const texts = Array.from(card.querySelectorAll('svg text')).map(t => {
            const s = getComputedStyle(t); const r = t.getBoundingClientRect();
            return {text: t.textContent, fillAttr: t.getAttribute('fill'), computedFill: s.fill, fontWeight: s.fontWeight, width: r.width, height: r.height};
        });
        return {foundCard: true, textCount: texts.length, texts};
    }""")
    assert report_info['foundCard']
    category_texts = [t for t in report_info['texts'] if ('Student' in t['text'] or 'NCC' in t['text'] or '·' in t['text'])]
    assert category_texts
    white_labels = [t for t in category_texts if t['fillAttr'] == '#ffffff' or t['computedFill'] in ['rgb(255, 255, 255)', '#ffffff']]
    assert white_labels
    assert [t for t in white_labels if int(t['fontWeight']) >= 600 and t['width'] > 0 and t['height'] > 0]
except Exception:
    raise
