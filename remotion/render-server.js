/**
 * Lightweight render server — accepts POST /render to trigger Remotion renders.
 * Runs alongside Remotion Studio on port 3335.
 */
const http = require('http');
const { execFile } = require('child_process');
const path = require('path');

const PORT = 3335;

const server = http.createServer((req, res) => {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, GET, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  if (req.method === 'OPTIONS') { res.writeHead(200); res.end(); return; }

  // Health check
  if (req.method === 'GET' && req.url === '/health') {
    res.writeHead(200, { 'Content-Type': 'application/json' });
    res.end(JSON.stringify({ status: 'ok' }));
    return;
  }

  // POST /render
  if (req.method === 'POST' && req.url === '/render') {
    let body = '';
    req.on('data', chunk => { body += chunk; });
    req.on('end', () => {
      try {
        const { composition, output, props } = JSON.parse(body);
        const comp = composition || 'SeasonStory';
        const outFile = output || '/app/outputs/render.mp4';

        const args = ['remotion', 'render', comp, '--output', outFile];
        if (props) {
          args.push('--props', JSON.stringify(props));
        }

        console.log(`[Render] Starting: npx ${args.join(' ')}`);

        // Fire and forget — return immediately
        res.writeHead(200, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ status: 'rendering', output: outFile }));

        const child = execFile('npx', args, {
          cwd: '/app',
          timeout: 600000, // 10 min
        }, (error, stdout, stderr) => {
          if (error) {
            console.error(`[Render] FAILED: ${error.message}`);
            if (stderr) console.error(stderr);
          } else {
            console.log(`[Render] DONE: ${outFile}`);
          }
        });

      } catch (e) {
        res.writeHead(400, { 'Content-Type': 'application/json' });
        res.end(JSON.stringify({ error: e.message }));
      }
    });
    return;
  }

  res.writeHead(404);
  res.end('Not found');
});

server.listen(PORT, () => {
  console.log(`[Render Server] Listening on port ${PORT}`);
});
