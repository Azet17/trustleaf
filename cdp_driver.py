#!/usr/bin/env python3
"""Deploy TrustLeaf contract via GenLayer Studio (raw CDP per skill).
Reuse one page, Page.navigate. Log every step to stdout."""
import json, socket, base64, time, sys, struct, os

WS_HOST, WS_PORT = '127.0.0.1', 9222

def ws_connect(path):
    """Minimal WebSocket client (no-mask frames from client are required actually)."""
    import hashlib, os, struct
    sock = socket.create_connection((WS_HOST, WS_PORT))
    key = base64.b64encode(os.urandom(16)).decode()
    req = (f"GET {path} HTTP/1.1\r\nHost: {WS_HOST}:{WS_PORT}\r\n"
           f"Upgrade: websocket\r\nConnection: Upgrade\r\n"
           f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n\r\n")
    sock.send(req.encode())
    # read until \r\n\r\n
    resp = b''
    while b'\r\n\r\n' not in resp:
        resp += sock.recv(4096)
    # verify 101
    if b'101' not in resp.split(b'\r\n')[0]:
        raise Exception('WS upgrade failed: ' + resp.split(b'\r\n')[0].decode())
    return sock

def ws_send(sock, data: str):
    payload = data.encode()
    header = bytearray([0x81])  # FIN + text
    length = len(payload)
    if length < 126:
        header.append(0x80 | length)
    elif length < 65536:
        header.append(0x80 | 126)
        header += struct.pack('>H', length)
    else:
        header.append(0x80 | 127)
        header += struct.pack('>Q', length)
    mask = os.urandom(4)
    header += mask
    masked = bytes(b ^ mask[i % 4] for i, b in enumerate(payload))
    sock.send(bytes(header) + masked)

def ws_recv(sock, timeout=30):
    sock.settimeout(timeout)
    def read_exact(n):
        buf = b''
        while len(buf) < n:
            chunk = sock.recv(n - len(buf))
            if not chunk:
                raise ConnectionError('ws closed')
            buf += chunk
        return buf
    b1, b2 = read_exact(2)
    opcode = b1 & 0x0F
    length = b2 & 0x7F
    if length == 126:
        length = struct.unpack('>H', read_exact(2))[0]
    elif length == 127:
        length = struct.unpack('>Q', read_exact(8))[0]
    data = read_exact(length) if length else b''
    if opcode == 1:
        return data.decode(errors='replace')
    return data

def cdp(sock, method, params=None, msg_id=None):
    msg_id = msg_id or int(time.time() * 1000) % 100000
    ws_send(sock, json.dumps({'id': msg_id, 'method': method, 'params': params or {}}))
    while True:
        resp = json.loads(ws_recv(sock, timeout=60))
        if resp.get('id') == msg_id:
            return resp

def eval_js(sock, expression, await_promise=False):
    params = {'expression': expression, 'returnByValue': True,
              'awaitPromise': await_promise}
    r = cdp(sock, 'Runtime.evaluate', params)
    return r.get('result', {}).get('result', {}).get('value')

if __name__ == '__main__':
    # list pages → get WS path of first page
    import urllib.request
    tabs = json.loads(urllib.request.urlopen('http://127.0.0.1:9222/json').read())
    page = [t for t in tabs if t['type'] == 'page'][0]
    ws_path = '/devtools/page/' + page['id']
    print(f'binding page :: {page["id"][:12]} url={page["url"][:60]}')

    sock = ws_connect(ws_path)
    cdp(sock, 'Runtime.enable')

    action = sys.argv[1] if len(sys.argv) > 1 else 'goto'
    if action == 'goto':
        url = sys.argv[2]
        cdp(sock, 'Page.enable')
        cdp(sock, 'Page.navigate', {'url': url})
        time.sleep(8)
        print('now at ::', eval_js(sock, 'location.href'))
    elif action == 'eval':
        expr = sys.stdin.read()
        print(eval_js(sock, expr))
    elif action == 'shot':
        r = cdp(sock, 'Page.captureScreenshot', {'format': 'png'})
        open(sys.argv[2], 'wb').write(base64.b64decode(r['data']))
        print('screenshot saved:', sys.argv[2])
