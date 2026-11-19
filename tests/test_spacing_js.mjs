/**
 * tests/test_spacing_js.mjs — cjk_spacing.js 的行为回归（jsdom）
 *
 * 为什么要有这一组：Python 侧早有「不吃已有空格」的用例，JS 侧一条都没有，
 * 于是同一个病修了一边、留了一边（`中 a 中` → `中a中`）。判据一致，两个实现都得钉住。
 *
 * 跑法：npm install && node tests/test_spacing_js.mjs
 * 退出码：0 全过／1 有用例失败／2 缺 jsdom（⛔ 不静默跳过）
 */
import { JSDOM } from 'jsdom'
import fs from 'node:fs'
import path from 'node:path'

const ROOT = path.resolve(path.dirname(new URL(import.meta.url).pathname), '..')
const SRC = fs.readFileSync(path.join(ROOT, 'tools/cjk_spacing.js'), 'utf8')

let pass = 0
let fail = 0

function run(html, selector = '.cjk', times = 1) {
  const dom = new JSDOM(`<!doctype html><html lang="zh-CN"><body>${html}</body></html>`, { runScripts: 'outside-only' })
  dom.window.eval(SRC)
  for (let i = 0; i < times; i++) dom.window.eval(`new CJKSpacing('${selector}').run()`)
  return dom.window.document.body
}

function check(name, cond, detail) {
  if (cond) { pass++; console.log(`  ✓ ${name}`) } else { fail++; console.log(`  ✗ ${name}${detail ? ' —— ' + detail : ''}`) }
}

console.log('cjk_spacing.js 行为回归：')

// 1 有空格：不插盒，也不删字符
{
  const body = run('<p class="cjk">中 a 中</p>')
  const p = body.querySelector('p')
  check('已有 ASCII 空格原样保留（不插盒）', p.textContent === '中 a 中' && !p.querySelector('cjk-spacing'), JSON.stringify(p.textContent))
}

// 2 无空格：落盒，但字符本身不变
{
  const body = run('<p class="cjk">中a中</p>')
  const p = body.querySelector('p')
  check('无空格时落间隙盒', !!p.querySelector('cjk-spacing'), p.innerHTML)
  check('落盒不改正文字符（copy 出来仍是 中a中）', p.textContent === '中a中', JSON.stringify(p.textContent))
}

// 3 幂等：跑两遍不叠盒
{
  const body = run('<p class="cjk">中a中</p>', '.cjk', 2)
  const p = body.querySelector('p')
  const n = p.querySelectorAll('cjk-spacing').length
  check('重复运行不叠盒（第二遍跳过已包裹节点）', n === 1, 'box=' + n)
}

// 4 代码块与嵌套：整条祖先链跳过
{
  const body = run('<p class="cjk"><code>中a中</code></p>')
  const p = body.querySelector('p')
  check('代码块不动', !p.querySelector('cjk-spacing') && p.textContent === '中a中', p.innerHTML)
}
{
  const body = run('<p class="cjk"><code><span>中a</span></code></p>')
  const p = body.querySelector('p')
  check('嵌套在 code 里的文本也不动', !p.querySelector('cjk-spacing'), p.innerHTML)
}

// 5 标点挤压：相邻全角开括号
{
  const body = run('<p class="cjk">（（</p>')
  const p = body.querySelector('p')
  check('相邻全角标点落挤压盒', !!p.querySelector('cjk-adjacent'), p.innerHTML)
  check('挤压不改字符', p.textContent === '（（', JSON.stringify(p.textContent))
}

// 6 跨元素边界：已知限制，不崩、不乱改
{
  const body = run('<p class="cjk">中<span>a</span>中</p>')
  const p = body.querySelector('p')
  check('跨元素边界不崩（已知缺口：缝拆到两个节点上拿不到盒）', p.textContent === '中a中', JSON.stringify(p.textContent))
}

// 7 空格 + 全角标点混排：空格留着，标点照挤
{
  const body = run('<p class="cjk">中 a 中（（</p>')
  const p = body.querySelector('p')
  check('空格与挤压可共存', p.textContent === '中 a 中（（' && p.querySelector('cjk-adjacent'), p.innerHTML)
}

console.log(`\n${fail ? 'FAIL' : 'ALL OK'}｜pass ${pass}｜fail ${fail}`)
process.exit(fail ? 1 : 0)
