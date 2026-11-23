#!/usr/bin/env node
/**
 * 跨引擎读数：用 Playwright 起 Firefox 或 WebKit，跑同一份 tools/probe.html，
 * 把 #out 里那段 RESULT{json}END 取出来，落成 results/<engine>-pw.json 与同名 .md。
 *
 * 为什么不用浏览器本体：
 *   Chrome 有 --dump-dom，直接命令行即可；Firefox、Safari 没有这个开关。
 *   Playwright 给的是 WebKit 的构建（不是 Apple 发的 Safari），所以结果只能写
 *   「WebKit 引擎」——要写「Safari」三个字，得用 tools/measure_safari.mjs 在真机上跑。
 *
 * 用法：
 *   node tools/measure_pw.mjs                      # 两个引擎都跑
 *   node tools/measure_pw.mjs --engine firefox     # 只跑一个
 *   node tools/measure_pw.mjs --out results/ci
 * 退出码：0 全部量到；1 有引擎没量到（会打印哪个）。
 *
 * 依赖：npm i（playwright 在 devDependencies），浏览器二进制需 npx playwright install firefox webkit。
 */
import { mkdir, writeFile } from 'node:fs/promises';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const probe = join(HERE, 'probe.html');

const args = process.argv.slice(2);
const argOf = (name, dflt) => {
  const i = args.indexOf(name);
  return i > -1 && args[i + 1] ? args[i + 1] : dflt;
};
const OUT = argOf('--out', join(HERE, '..', 'results'));
const only = argOf('--engine', null);

const ENGINES = ['firefox', 'webkit'];

function parseResult(text) {
  if (!text) return null;
  const m = /RESULT(\{[\s\S]*\})END/.exec(text);
  if (!m) return null;
  try {
    return JSON.parse(m[1]);
  } catch {
    return null;
  }
}

async function measure(pw, name) {
  const launcher = name === 'firefox' ? pw.firefox : pw.webkit;
  const browser = await launcher.launch();
  try {
    const page = await browser.newPage();
    await page.goto('file://' + probe, { waitUntil: 'load' });
    const text = await page.locator('#out').textContent();
    const r = parseResult(text);
    if (!r) throw new Error('probe 没吐出 RESULT 串');

    // 字体探针：Linux 的 CI 上没有苹方／宋体／黑体，C7 那三条读数必然是 0，得标明原因
    // ⚠️ 别用 document.fonts.check()——没装也返回 true；也别靠量字宽——macOS 的回退本身就是苹方，
    // 量出来和「该字体」几乎同宽，分不清。改用 FontFace 的 local()：装了就 load 成功，没装 reject。
    r.env = {
      engine: name,
      engineVersion: browser.version(),
      platform: process.platform,
      fonts: await page.evaluate(async () => {
        const has = async (family) => {
          try {
            await new FontFace('probe', `local("${family}")`).load();
            return true;
          } catch {
            return false;
          }
        };
        return {
          pingfang: await has('PingFang SC'),
          songti: await has('Songti SC'),
          heiti: await has('Heiti SC'),
          anyCJK: await has('Noto Sans CJK SC'),
        };
      }),
    };
    return r;
  } finally {
    await browser.close();
  }
}

function toMarkdown(name, r) {
  const d = r.delta;
  const yesno = v => (v ? '支持' : '不支持');
  return `# ${name}（Playwright 构建）

- 引擎：${r.env.engine} ${r.env.engineVersion} · ${r.env.platform}
- UA：\`${r.ua}\`
- 属性支持：\`text-autospace\` ${yesno(r.supports.autospace)}；\`text-spacing-trim\` ${yesno(r.supports.spacingTrim)}
- 字体：苹方 ${r.env.fonts.pingfang ? '有' : '无'}｜宋体 ${r.env.fonts.songti ? '有' : '无'}｜黑体 ${r.env.fonts.heiti ? '有' : '无'}｜Noto CJK ${r.env.fonts.anyCJK ? '有' : '无'}

| 项 | 读数 |
|---|---|
| 单边界间隙（32px） | ${d.gap_32}px |
| 单边界间隙（64px） | ${d.gap_64}px |
| 折算 | ${d.gap_em} em |
| 不声明 vs 显式关闭 | ${d.undeclared_vs_off}px |
| 串内已有空格时加 normal | ${d.spaced_delta}px |
| 跨元素边界（normal − 无声明） | ${d.element_delta}px |
| 每缝包空 span | ${d.empty_spans_delta}px |
| \`.mx\` 盒（32px） | ${d.mx_32}px（${d.mx_em} em） |
| 挤压（苹方／宋体／黑体） | ${d.trim_pingfang}／${d.trim_songti}／${d.trim_heiti}px |

${r.supports.spacingTrim
      ? (r.env.fonts.pingfang ? '' : '> 这台机器上没有苹方／宋体／黑体，挤压那三条读数为 0 是「缺字体」而不是「挤压无效」，⛔ 不能据此推 C7。\n')
      : '> 这个引擎不支持 `text-spacing-trim`，挤压三条读数为 0 是「属性没有」，不是「字体没 halt」，⛔ 不能和 C7 混着读。\n'}
`;
}

if (only && !ENGINES.includes(only)) {
  // 引擎名打错时循环会一个都不跑、failed 仍为空，于是「没测」被当成「通过」（2026-11-23 补）
  console.error(`❌ 未知引擎 ${only}；可选：${ENGINES.join(' / ')}`);
  process.exit(2);
}

const pw = await import('playwright');
await mkdir(OUT, { recursive: true });

const failed = [];
for (const name of ENGINES) {
  if (only && only !== name) continue;
  try {
    const r = await measure(pw, name);
    await writeFile(join(OUT, `${name}-pw.json`), JSON.stringify(r, null, 2) + '\n');
    await writeFile(join(OUT, `${name}-pw.md`), toMarkdown(name, r));
    console.log(`✅ ${name} ${r.env.engineVersion}：间隙 ${r.delta.gap_em} em，不声明差 ${r.delta.undeclared_vs_off}px`);
  } catch (e) {
    failed.push(name);
    console.error(`❌ ${name}: ${e.message}`);
  }
}

process.exit(failed.length ? 1 : 0);
