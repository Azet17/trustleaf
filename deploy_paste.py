#!/usr/bin/env python3
"""Robust: set clipboard, focus editor, Ctrl+A, paste (Ctrl+V) via CDP.
Also try document.execCommand('insertText') path."""
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

def main():
    sock = get_sock()

    # Focus textarea inside monaco (monaco uses hidden textarea for input)
    focus = eval_js(sock, '''
    (() => {
      const ta = document.querySelector('.monaco-editor textarea, .inputarea');
      if (ta) { ta.focus(); return 'focused textarea'; }
      const ed = document.querySelector('.monaco-editor');
      if (ed) { ed.focus(); return 'focused editor'; }
      return 'nothing';
    })()
    ''')
    print('focus ::', focus)
    time.sleep(1)

    # Ctrl+A
    cdp(sock, 'Input.dispatchKeyEvent', {'type': 'rawKeyDown', 'key': 'a',
         'code': 'KeyA', 'windowsVirtualKeyCode': 65, 'modifiers': 2})
    cdp(sock, 'Input.dispatchKeyEvent', {'type': 'keyUp', 'key': 'a',
         'code': 'KeyA', 'windowsVirtualKeyCode': 65, 'modifiers': 2})
    time.sleep(0.3)

    # insertText (CDP native, works with monaco's IME)
    cdp(sock, 'Input.insertText', {'text': CONTRACT})
    time.sleep(2)

    # Verify via textarea value or view-lines
    check = eval_js(sock, '''
    (() => {
      const lines = document.querySelectorAll('.monaco-editor .view-lines');
      const txt = lines.length ? lines[0].textContent : '';
      const has = txt.includes('SupplierTrustScore') || document.body.innerText.includes('SupplierTrustScore');
      return {has, len: txt.length};
    })()
    ''')
    print('verify ::', check)
    return check and check.get('has')

if __name__ == '__main__':
    ok = main()
    print('RESULT ::', 'INSERTED' if ok else 'FAILED')
