# Playwright snippet executed via mcp_browser_automation on 2026-07-17.
# URL tested: https://responder-registry.preview.emergentagent.com/test/5pSa-Lczj798OMV2A0A7mX4oAnRaTxsV
try:
    await page.set_viewport_size({"width": 1440, "height": 900})
    await page.wait_for_load_state('networkidle')
    await page.wait_for_selector('[data-testid="next-btn"]', timeout=15000)
    next_styles = await page.locator('[data-testid="next-btn"]').evaluate("""el => {
        const s = getComputedStyle(el); const r = el.getBoundingClientRect();
        return {backgroundColor: s.backgroundColor, color: s.color, opacity: s.opacity, visibility: s.visibility, display: s.display, rect: {x:r.x,y:r.y,width:r.width,height:r.height}};
    }""")
    await page.locator('[data-testid="option-A"]').click()
    await page.wait_for_timeout(300)
    opt_styles = await page.locator('[data-testid="option-A"]').evaluate("""el => {
        const s = getComputedStyle(el); const badge = el.querySelector('div'); const bs = getComputedStyle(badge);
        return {borderColor: s.borderColor, borderWidth: s.borderWidth, backgroundColor: s.backgroundColor, boxShadow: s.boxShadow, badgeBackgroundColor: bs.backgroundColor, badgeColor: bs.color, classes: el.className, badgeClasses: badge.className};
    }""")
    await page.set_viewport_size({"width": 390, "height": 844})
    await page.wait_for_timeout(500)
    mobile_next_styles = await page.locator('[data-testid="next-btn"]').evaluate("""el => {
        const s = getComputedStyle(el); const r = el.getBoundingClientRect();
        return {backgroundColor: s.backgroundColor, color: s.color, opacity: s.opacity, visibility: s.visibility, display: s.display, rect: {x:r.x,y:r.y,width:r.width,height:r.height}, viewport: {w: window.innerWidth, h: window.innerHeight}};
    }""")
    assert next_styles['backgroundColor'] == 'rgb(11, 27, 61)'
    assert next_styles['color'] == 'rgb(255, 255, 255)'
    assert mobile_next_styles['backgroundColor'] == 'rgb(11, 27, 61)'
    assert mobile_next_styles['color'] == 'rgb(255, 255, 255)'
    assert opt_styles['borderColor'] == 'rgb(230, 57, 70)'
    assert opt_styles['borderWidth'] == '2px'
    assert opt_styles['backgroundColor'] in ['rgb(254, 242, 242)', 'rgba(254, 242, 242, 1)']
    assert opt_styles['badgeBackgroundColor'] == 'rgb(230, 57, 70)'
    assert opt_styles['badgeColor'] == 'rgb(255, 255, 255)'
    assert 'rgba(230, 57, 70' in opt_styles['boxShadow'] or 'rgb(230, 57, 70' in opt_styles['boxShadow']
except Exception:
    raise
