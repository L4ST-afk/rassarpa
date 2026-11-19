#!/usr/bin/env node
/**
 * Safari 本体读数：用系统自带的 safaridriver（WebDriver），开一个真 Safari，
 * 跑同一份 tools/probe.html，把 #out 里的 RESULT{json}END 取回来。
 *
 * 为什么不能像 Chrome 那样一行命令：Safari 没有 --dump-dom，也没有可脚本化的无头模式，
 * 只认 WebDriver。所以这条路只能在本机跑，进不了 CI。
 *
 * 跑之前要开两个开关（各一次）：
 *   1. sudo safaridriver --enable          # 开启 WebDriver 支持，需管理员密码
 *   2. Safari → 开发 → 允许远程自动化       # 没有「开发」菜单，先在「设置 → 高级」勾上
 *
 * 用法：
 *   node tools/measure_safari.mjs
 *   node tools/measure_safari.mjs --port 4445 --out results
 * 退出码：0 量到；1 起不来或拿不到读数（会打印差哪一步）。
 */
import { spawn } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const probe = pathToFileURL(join(HERE, 'probe.html')).href;

const args = process.argv.slice(2);
const argOf = (name, dflt) => {
  const i = args.indexOf(name);
  return i > -1 && args[i + 1] ? args[i + 1] : dflt;
};
const PORT = Number(argOf('--port', 4444));
const OUT = argOf('--out', join(HERE, '..', 'results'));
const BASE = `http://127.0.0.1:${PORT}`;

const sleep = ms => new Promise(r => setTimeout(r, ms));

async function req(method, path, body) {
  const res = await fetch(BASE + path, {
    method,
    headers: body ? { 'content-type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  const text = await res.text();
  let json = {};
  try {
    json = text ? JSON.parse(text) : {};
  } catch {
    throw new Error(`${method} ${path} 返回非 JSON：${text.slice(0, 200)}`);
  }
  return { status: res.status, json };
}

async function waitForDriver() {
  for (let i = 0; i < 60; i++) {
    try {
      const { status } = await req('GET', '/status');
      if (status === 200) return true;
    } catch {
      // 还没起来
    }
    await sleep(500);
  }
  return false;
}

const driver = spawn('safaridriver', ['-p', String(PORT)], { stdio: ['ignore', 'pipe', 'pipe'] });
let driverErr = '';
driver.stderr.on('data', d => { driverErr += d.toString(); });

const cleanup = async () => {
  try { driver.kill('SIGTERM'); } catch {}
};

try {
  if (!(await waitForDriver())) {
    console.error('❌ safaridriver 起不来。多半是没开开关，两条命令各一次：');
    console.error('   sudo safaridriver --enable');
    console.error('   Safari → 开发 → 允许远程自动化（没有「开发」菜单，先在「设置 → 高级」里勾上）');
    if (driverErr.trim()) console.error('   驱动输出：' + driverErr.trim().split('\n').slice(-3).join(' | '));
    await cleanup();
    process.exit(1);
  }

  const created = await req('POST', '/session', {
    capabilities: { alwaysMatch: { browserName: 'safari' } },
  });
  const sid = created.json?.value?.sessionId;
  if (!sid) {
    console.error('❌ 建会话失败：' + JSON.stringify(created.json).slice(0, 300));
    await cleanup();
    process.exit(1);
  }

  const run = (script) => req('POST', `/session/${sid}/execute/sync`, { script, args: [] })
    .then(r => r.json?.value);

  await req('POST', `/session/${sid}/url`, { url: probe });
  await sleep(800); // 等 probe 在 load 里把结果写进 #out

  const text = await run('return document.getElementById("out").textContent');
  const m = /RESULT(\{[\s\S]*\})END/.exec(text || '');
  if (!m) {
    console.error('❌ 没从 probe 里取到 RESULT 串，页面可能没加载完');
    await req('DELETE', `/session/${sid}`);
    await cleanup();
    process.exit(1);
  }

  const r = JSON.parse(m[1]);
  r.env = {
    engine: 'safari',
    engineVersion: (await run('return navigator.userAgent'))?.match(/Version\/([\d.]+)/)?.[1] ?? 'unknown',
    platform: 'darwin',
    fonts: await run(`return {
      pingfang: document.fonts.check('32px "PingFang SC"'),
      songti: document.fonts.check('32px "Songti SC"'),
      heiti: document.fonts.check('32px "Heiti SC"'),
      anyCJK: document.fonts.check('32px "Noto Sans CJK SC"'),
    }`),
  };

  await req('DELETE', `/session/${sid}`);
  await cleanup();

  await mkdir(OUT, { recursive: true });
  await writeFile(join(OUT, 'safari.json'), JSON.stringify(r, null, 2) + '\n');
  const d = r.delta;
  await writeFile(join(OUT, 'safari.md'), `# Safari ${r.env.engineVersion}（本体，非构建）

- UA：\`${r.ua}\`
- 属性支持：\`text-autospace\` ${r.supports.autospace ? '支持' : '不支持'}；\`text-spacing-trim\` ${r.supports.spacingTrim ? '支持' : '不支持'}
- 字体：苹方 ${r.env.fonts.pingfang ? '有' : '无'}｜宋体 ${r.env.fonts.songti ? '有' : '无'}｜黑体 ${r.env.fonts.heiti ? '有' : '无'}

| 项 | 读数 |
|---|---|
| 单边界间隙（32px / 64px） | ${d.gap_32}px / ${d.gap_64}px（${d.gap_em} em） |
| 不声明 vs 显式关闭 | ${d.undeclared_vs_off}px |
| 串内已有空格时加 normal | ${d.spaced_delta}px |
| 跨元素边界（两缝） | ${d.element_delta}px |
| 每缝包空 span | ${d.empty_spans_delta}px |
| \`.mx\` 盒 | ${d.mx_32}px（${d.mx_em} em） |
| 挤压（苹方／宋体／黑体） | ${d.trim_pingfang}／${d.trim_songti}／${d.trim_heiti}px |
`);

  console.log(`✅ Safari ${r.env.engineVersion}：间隙 ${d.gap_em} em，元素边界 ${d.element_delta}px，包 span ${d.empty_spans_delta}px`);
} catch (e) {
  console.error('❌ ' + e.message);
  await cleanup();
  process.exit(1);
}
