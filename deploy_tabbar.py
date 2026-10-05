#!/usr/bin/env python3
"""Run button missing. In Studio the Deploy button typically appears only
after the contract has no syntax errors (in editor top-right toolbar).
Maybe the button is hidden because contract failed compile check.
Check for error markers in minimap + any toolbar row + press the editor's
Run keyboard shortcut. Also check Studio docs: deploy via right-click menu?"""
import json, time, base64
from cdp_driver import ws_connect, cdp, eval_js
import urllib.request

def get_sock():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read())
    page = [t for t in tabs if t['type'] == 'page'][0]
    sock = ws_connect('/devtools/page/' + page['id'])
    cdp(sock, 'Runtime.enable')
    return sock

def main():
    sock = get_sock()

    # 1. Look at elements near tab row (top of editor pane) — maybe icon-only button
    top = eval_js(sock, '''
    (() => {
      // find the tab bar containing trustleaf.py then its siblings
      const tabs = Array.from(document.querySelectorAll('*')).filter(e =>
        e.children.length === 0 && (e.innerText || '').trim() === 'trustleaf.py');
      if (!tabs.length) return 'no tab';
      let bar = tabs[0].closest('[class*="tab"], [class*="header"], [class*="bar"]') || tabs[0].parentElement.parentElement;
      const btns = bar.querySelectorAll('button, svg, [role=button]');
      return Array.from(btns).map(b => ({
        tag: b.tagName,
        title: b.getAttribute('title') || b.getAttribute('aria-label') || '',
        cls: (b.className || '').toString().slice(0, 60),
        rect: (() => { const r = b.getBoundingClientRect(); return [Math.round(r.x), Math.round(r.y), Math.round(r.width)]; })()
      }));
    })()
    ''')
    print('tab bar elements ::', json.dumps(top, indent=1)[:2000])

if __name__ == '__main__':
    main()
