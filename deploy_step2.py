#!/usr/bin/env python3
"""Deploy step 2: open a new contract project in Studio, paste TrustLeaf code."""
import json, time
from cdp_driver import ws_connect, cdp, eval_js
import urllib.request

CONTRACT = open('/home/ubuntu/trustleaf/contracts/supplier_trust.py').read()

def get_sock():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read())
    page = [t for t in tabs if t['type'] == 'page'][0]
    sock = ws_connect('/devtools/page/' + page['id'])
    cdp(sock, 'Runtime.enable')
    return sock

def click_text(sock, text, contains=False):
    expr = f'''
    (() => {{
      const els = document.querySelectorAll('button, a, [role=button]');
      for (const e of els) {{
        const t = (e.innerText || '').trim();
        if ({json.dumps(text in '' if contains else '')} ) {{}}
        const hit = {json.dumps(contains)} ? t.includes({json.dumps(text)}) : t === {json.dumps(text)};
        if (hit) {{ e.click(); return 'clicked: ' + t.slice(0, 50); }}
      }}
      return 'NOT FOUND: ' + {json.dumps(text)};
    }})()
    '''
    return eval_js(sock, expr)

def main():
    sock = get_sock()

    # "Start coding" = buat project baru
    print('start coding ::', click_text(sock, 'Start coding'))
    time.sleep(4)
    print('url ::', eval_js(sock, 'location.href'))

    # lihat UI editor sekarang
    state = eval_js(sock, '''
    (() => {
      const els = document.querySelectorAll('button, input, textarea, [contenteditable=true], .monaco-editor, [role=dialog]');
      return Array.from(els).map(e => ({
        tag: e.tagName,
        text: (e.innerText || e.value || e.placeholder || '').trim().slice(0, 40),
        dlg: e.getAttribute('role') === 'dialog'
      })).filter(x => x.text.length > 0).slice(0, 30);
    })()
    ''')
    print('editor UI ::', json.dumps(state, indent=1)[:2000])

if __name__ == '__main__':
    main()
