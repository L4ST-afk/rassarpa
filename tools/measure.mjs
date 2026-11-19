#!/usr/bin/env node
/**
 * cjk-spacing-lab · runner
 *
 * 用一个浏览器（默认本机 Chrome）跑 probe.html，把量到的 advance 落成 JSON 与 Markdown。
 * 只依赖浏览器自带的 --dump-dom：probe.html 在 load 时把结果写进 DOM，本脚本从 dump 里取。
 *
 * 用法：
 *   node run.mjs                                  # 默认 Chrome
 *   CHROME="/Applications/Firefox.app/Contents/MacOS/firefox" node run.mjs
 *   node run.mjs --out results                # 覆盖输出目录
 *
 * 退出码：0 量到结果；1 拿不到（多半是浏览器路径不对或该浏览器不支持 --dump-dom 的 JS 落盘）。
 */
import { execFile } from 'node:child_process';
import { mkdir, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const outIdx = args.indexOf('--out');
const OUT = outIdx > -1 ? args[outIdx + 1] : join(HERE, '..', 'results');

const CHROME =
  process.env.CHROME || '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome';

const flagSet = [
  '--headless=new',
  '--disable-gpu',
  '--no-sandbox',
  '--hide-scrollbars',
  '--virtual-time-budget=4000',
  '--dump-dom',
];

function run(cmd, argv, pageUrl) {
  return new Promise((resolve, reject) => {
    execFile(cmd, [...argv, pageUrl], { maxBuffer: 32 * 1024 * 1024 }, (err, stdout, stderr) => {
      if (err) return reject(new Error(`${cmd} failed: ${err.message}\n${stderr}`));
      resolve(stdout);
    });
  });
}

const PAGE = 'file://' + join(HERE, 'probe.html');
const dom = await run(CHROME, flagSet, PAGE);
const m = dom.match(/RESULT(\{.*?\})END/);
if (!m) {
  console.error('未在 DOM 里找到 RESULT 串——检查浏览器是否执行了页面脚本。');
  process.exit(1);
}

const r = JSON.parse(m[1]);
const shortUa = (r.ua.match(/(?:HeadlessChrome|Chrome|Firefox|Version)[^\s;)]*/) || ['unknown'])[0];
const slug = shortUa.toLowerCase().replace(/[^a-z0-9.]+/g, '-');

await mkdir(OUT, { recursive: true });
await writeFile(join(OUT, `${slug}.json`), JSON.stringify(r, null, 2) + '\n');

const em = (v) => (v === 0 ? '0' : (v < 0 ? '−' : '+') + Math.abs(v) + 'px');
const d = r.delta;
const md = `<!-- 由 run.mjs 生成于 ${new Date().toISOString()} · ${r.ua} -->
| 项 | 量到的值 |
|---|---|
| 单边界间隙（32px） | ${em(d.gap_32)} = ${d.gap_em} em |
| 单边界间隙（64px） | ${em(d.gap_64)} = ${d.gap_em} em |
| 无声明 vs \`no-autospace\` | ${em(d.undeclared_vs_off)}（0 = 无声明即关闭） |
| 已含 ASCII 空格的串 | ${em(d.spaced_delta)}（0 = 不再补） |
| 跨元素边界（\`中<abbr>a</abbr>中\`） | ${em(d.element_delta)} |
| 每缝空 span 叠在 normal 上 | ${em(d.empty_spans_delta)}（负值 = 把原生间隙打掉了） |
| \`.mx\` 盒（32px） | ${em(d.mx_32)} = ${d.mx_em} em |
| 挤压 · PingFang SC | ${em(d.trim_pingfang)} |
| 挤压 · Songti SC | ${em(d.trim_songti)} |
| 挤压 · Heiti SC | ${em(d.trim_heiti)} |

CSS.supports：\`text-autospace: normal\` = ${r.supports.autospace}｜\`no-autospace\` = ${r.supports.autospaceNo}｜\`text-spacing-trim: normal\` = ${r.supports.spacingTrim}
`;
await writeFile(join(OUT, `${slug}.md`), md);

process.stdout.write(md);
process.stdout.write(`\n已写入 ${join(OUT, slug + '.json')}\n`);
