#!/usr/bin/env python3
"""Deploy FINAL: replace storage.py editor content with TrustLeaf code,
save, then click Run (Deploy). Monaco exists per-editor-instance (not global)."""
import json, time, base64
from cdp_driver import ws_connect, cdp, eval_js
import urllib.request

CONTRACT = open('/home/ubuntu/trustleaf/contracts/supplier_trust.py').read()

def get_sock():
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read())
    page = [t for t in tabs if t['type'] == 'page'][0]
    sock = ws_connect('/devtools/page/' + page['id'])
    cdp(sock, 'Runtime.enable')
    return sock

def shot(sock, path):
    r = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
    if 'data' in r.get('result', {}):
        open(path, 'wb').write(base64.b64decode(r['result']['data']))
        print('shot ::', path)

def main():
    sock = get_sock()

    # Monaco stores models on window instance — find via DOM: monaco editor
    # uses _modelData. Common trick: use editor instance exposed on window.
    # Alternative: select-all in editor via keyboard events + insert text.

    # 1. Focus editor (click on it)
    eval_js(sock, '''
    (() => {
      const ed = document.querySelector('.monaco-editor');
      if (ed) { ed.dispatchEvent(new MouseEvent('mousedown', {bubbles: true})); ed.focus(); }
      return !!ed;
    })()
    ''')
    time.sleep(1)

    # 2. Select all (Ctrl+A) via Input.dispatchKeyEvent
    for key, code, kc in [('Control', 'ControlLeft', 17), ('a', 'KeyA', 65)]:
        cdp(sock, 'Input.dispatchKeyEvent', {'type': 'keyDown', 'key': key,
             'code': code, 'windowsVirtualKeyCode': kc, 'modifiers': 2 if key == 'a' else 0})
    cdp(sock, 'Input.dispatchKeyEvent', {'type': 'keyUp', 'key': 'a',
         'code': 'KeyA', 'windowsVirtualKeyCode': 65, 'modifiers': 2})
    cdp(sock, 'Input.dispatchKeyEvent', {'type': 'keyUp', 'key': 'Control',
         'code': 'ControlLeft', 'windowsVirtualKeyCode': 17})
    time.sleep(0.5)

    # 3. Insert our contract via Input.insertText (respects Monaco)
    cdp(sock, 'Input.insertText', {'text': CONTRACT})
    time.sleep(2)

    # 4. Verify editor content now contains TrustLeaf
    check = eval_js(sock, '''
    (() => {
      const lines = document.querySelectorAll('.monaco-editor .view-lines span');
      const txt = Array.from(lines).map(l => l.textContent).join('');
      return {hasTrustLeaf: txt.includes('SupplierTrustScore'),
              sample: txt.slice(0, 120)};
    })()
    ''')
    print('editor check ::', json.dumps(check))

    # 5. Save via Ctrl+S
    cdp(sock, 'Input.dispatchKeyEvent', {'type': 'keyDown', 'key': 's',
         'code': 'KeyS', 'windowsVirtualKeyCode': 83, 'modifiers': 2})
    cdp(sock, 'Input.dispatchKeyEvent', {'type': 'keyUp', 'key': 's',
         'code': 'KeyS', 'windowsVirtualKeyCode': 83, 'modifiers': 2})
    time.sleep(2)
    print('saved')

    shot(sock, '/tmp/studio_after_edit.png')

if __name__ == '__main__':
    main()
