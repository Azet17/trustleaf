#!/usr/bin/env python3
"""Try Monaco model access via window.monaco instances or via the editor's
owner. Then fallback: execCommand insertText after select-all."""
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

    # Find monaco through the editor DOM node (stored on element)
    probe = eval_js(sock, '''
    (() => {
      const ed = document.querySelector('.monaco-editor');
      if (!ed) return 'no editor';
      // monaco editor instance:
      const keys = Object.keys(ed);
      // check for editor instance in common locations
      let inst = null;
      for (const k of keys) {
        const v = ed[k];
        if (v && typeof v === 'object' && v.getModel) { inst = v; break; }
      }
      if (inst) {
        window.__tleditor = inst;
        const model = inst.getModel();
        window.__tlmodel = model;
        return 'instance found; model uri=' + (model && model.uri ? model.uri.toString() : 'n/a');
      }
      return 'keys: ' + keys.slice(0, 15).join(',');
    })()
    ''')
    print('probe ::', probe)

    if '__tlmodel' in str(probe) or 'instance found' in str(probe):
        expr = f'''
        (() => {{
          const model = window.__tlmodel;
          const full = model.getFullModelRange();
          model.pushEditOperations([], [{{ range: full, text: {json.dumps(CONTRACT)} }}], () => null);
          return 'set: ' + model.getValue().slice(0, 80);
        }})()
        '''
        print('editor set ::', eval_js(sock, expr))
        # save
        eval_js(sock, 'window.__tleditor.getAction("actions.save") ? window.__tleditor.trigger("src", "actions.save", null) : "no-save-action"')
        time.sleep(2)
        check = eval_js(sock, 'window.__tlmodel.getValue().includes("SupplierTrustScore")')
        print('verify ::', check)

if __name__ == '__main__':
    main()
