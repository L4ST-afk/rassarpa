/**
 * cjk_spacing.js — 中西文混排间隙 + 全角标点挤压（浏览器零依赖）
 *
 * 吸收自 Sivan《赫蹏》(heti-addon.js，MIT)，有扬弃：
 *  - 保留其"逐文本节点包裹负边距元素"的核心思路（不用 CSS text-spacing-trim，浏览器支持差）
 *  - 保留其正则（含 lookbehind 降级）与跳过 pre/code/sup/sub 的策略
 *  - 不引入 heti 的字体族与 max-width 默认值
 *
 * 用法：
 *   <script src="cjk_spacing.js"></script>
 *   <script>new CJKSpacing('.cjk').run()</script>
 * 或：new CJKSpacing('.cjk, .entry').run()
 */

(function (global) {
  'use strict'

  // 简体直角引号预设（与 CSS q{quotes} 对应；竖排自动旋转，不另定义）
  // tw/common 用「」『』，cn 用""''；本 skill 默认 common（简体直角引号）。
  var QUOTE_SET = {
    cn: { horizontal: ['“', '”', '‘', '’'], vertical: ['『', '』', '「', '」'] },
    tw: { horizontal: ['「', '」', '『', '』'], vertical: ['「', '」', '『', '』'] },
    common: { horizontal: ['「', '」', '『', '』'], vertical: ['「', '」', '『', '』'] }
  }

  // 部分正则修改自 pangu.js (https://github.com/vinta/pangu.js，MIT)
  var CJK = '\\u2e80-\\u2eff\\u2f00-\\u2fdf\\u3040-\\u309f\\u30a0-\\u30fa\\u30fc-\\u30ff\\u3100-\\u312f\\u3200-\\u32ff\\u3400-\\u4dbf\\u4e00-\\u9fff\\uf900-\\ufaff'
  var A = 'A-Za-z\\u0080-\\u00ff\\u0370-\\u03ff'
  var N = '0-9'
  var S = '`~!@#\\$%\\^&\\*\\(\\)\\-_=\\+\\[\\]{}\\\\\\|;:\'",<.>\\/?'
  var ANS = A + N + S
  var REG_CJK_FULL = '(?<=[' + CJK + '])( *[' + ANS + ']+(?: +[' + ANS + ']+)* *)(?=[' + CJK + '])'
  var REG_CJK_START = '([' + ANS + ']+(?: +[' + ANS + ']+)* *)(?=[' + CJK + '])'
  var REG_CJK_END = '(?<=[' + CJK + '])( *[' + ANS + ']+(?: +[' + ANS + ']+)*)'
  var REG_CJK_FULL_WL = '(?:[' + CJK + '])( *[' + ANS + ']+(?: +[' + ANS + ']+)* *)(?=[' + CJK + '])'
  var REG_CJK_END_WL = '(?:[' + CJK + '])( *[' + ANS + ']+(?: +[' + ANS + ']+)*)'

  // 标点分类（全角）
  var BD_STOP = '。．，、：；！‼？⁇'
  var BD_SEP = '·・‧'
  var BD_OPEN = '「『（《〈【〖〔［｛'
  var BD_CLOSE = '」』）》〉】〗〕］｝'
  var BD_START = BD_OPEN + BD_CLOSE
  var BD_END = BD_STOP + BD_OPEN + BD_CLOSE
  var BD_HALF_OPEN = '“‘'
  var BD_HALF_CLOSE = '”’'
  var BD_HALF_START = BD_HALF_OPEN + BD_HALF_CLOSE

  var CJK_SKIPPED_ELEMENTS = {
    pre: 1, code: 1, sup: 1, sub: 1,
    'cjk-spacing': 1, 'cjk-adjacent': 1, 'script': 1, 'style': 1
  }
  var CJK_SKIPPED_CLASS = 'cjk-skip'
  // 祖先链任一层命中即跳过（closest 用；见 walkTextNodes 的注释）
  var SKIP_SELECTOR = 'pre, code, sup, sub, script, style, cjk-spacing, cjk-adjacent, .' + CJK_SKIPPED_CLASS

  function hasOwn(o, k) { return Object.prototype.hasOwnProperty.call(o, k) }

  function makeRegExps(lookbehind) {
    var re = {}
    re.full = new RegExp(lookbehind ? REG_CJK_FULL : REG_CJK_FULL_WL, 'g')
    re.start = new RegExp(REG_CJK_START, 'g')
    re.end = new RegExp(lookbehind ? REG_CJK_END : REG_CJK_END_WL, 'g')
    // 全角相邻 → 挤半字
    re.half = new RegExp('([' + BD_STOP + '])(?=[' + BD_START + '])|([' + BD_OPEN + '])(?=[' + BD_OPEN + '])|([' + BD_CLOSE + '])(?=[' + BD_END + '])', 'g')
    // 间隔符接引号 / 闭引号接间隔符 → 挤 quarter
    re.quarterSep = new RegExp('([' + BD_SEP + '])(?=[' + BD_OPEN + '])|([' + BD_CLOSE + '])(?=[' + BD_SEP + '])', 'g')
    // 弯引号场景：停顿接弯引号 / 弯开引号接全角开引号 → quarter
    re.quarterHalf = new RegExp('([' + BD_STOP + '])(?=[' + BD_HALF_START + '])|([' + BD_HALF_OPEN + '])(?=[' + BD_OPEN + '])', 'g')
    return re
  }

  function walkTextNodes(root, filter) {
    var nodes = []
    var walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, {
      acceptNode: function (node) {
        if (!node.nodeValue || !node.nodeValue.trim()) return NodeFilter.FILTER_REJECT
        var p = node.parentNode
        if (!p) return NodeFilter.FILTER_REJECT
        // 判整个祖先链，不只看直接父元素：<code><span>中a</span></code> 的父元素是 span，
        // 只看一层就会把代码里的字也改掉。
        if (p.nodeType === 1 && p.closest(SKIP_SELECTOR)) return NodeFilter.FILTER_REJECT
        if (p.classList && p.classList.contains(CJK_SKIPPED_CLASS)) return NodeFilter.FILTER_REJECT
        if (filter && !filter(node)) return NodeFilter.FILTER_REJECT
        return NodeFilter.FILTER_ACCEPT
      }
    })
    var n
    while ((n = walker.nextNode())) nodes.push(n)
    return nodes
  }

  function wrap(parent, text, cls) {
    var el = document.createElement(cls === 'adj' ? 'cjk-adjacent' : 'cjk-spacing')
    if (cls === 'start') el.className = 'cjk-spacing-start'
    else if (cls === 'end') el.className = 'cjk-spacing-end'
    else if (cls === 'half') el.className = 'cjk-adjacent-half'
    else if (cls === 'quarter') el.className = 'cjk-adjacent-quarter'
    el.textContent = text
    return el
  }

  function CJKSpacing(rootSelector, opts) {
    this.rootSelector = rootSelector || '.cjk'
    // 引号切换不在这里做：弯直引号的取舍走 CSS `q { quotes: ... }`（SKILL.md §B）。
    // CJKSpacing.QUOTE_SET 只是各语域的预设数据，供使用方取用，脚本不自动替换字符。
    var lookbehind = true
    try { new RegExp('(?<=x)x', 'g').test('') } catch (e) { lookbehind = false }
    this.lookbehind = lookbehind
    this.re = makeRegExps(lookbehind)
    this.offset = lookbehind ? 0 : 1
  }

  CJKSpacing.prototype.run = function () {
    var roots = document.querySelectorAll(this.rootSelector)
    for (var i = 0; i < roots.length; i++) this.spacingElement(roots[i])
    return this
  }

  CJKSpacing.prototype.spacingElement = function (root) {
    var self = this
    var rules = [
      { re: self.re.full, cls: 'both' },
      { re: self.re.start, cls: 'start' },
      { re: self.re.end, cls: 'end' },
      { re: self.re.half, cls: 'half' },
      { re: self.re.quarterSep, cls: 'quarter' },
      { re: self.re.quarterHalf, cls: 'quarter' }
    ]
    rules.forEach(function (rule) {
      var nodes = walkTextNodes(root)
      nodes.forEach(function (textNode) {
        var s = textNode.nodeValue
        rule.re.lastIndex = 0
        if (!rule.re.test(s)) return
        rule.re.lastIndex = 0
        var frag = document.createDocumentFragment()
        var last = 0
        var m
        while ((m = rule.re.exec(s))) {
          if (m.index > last) frag.appendChild(document.createTextNode(s.slice(last, m.index)))
          var matched = m[0]
          // 中西文间隙用 cjk-spacing；标点挤压用 cjk-adjacent
          var isSpacing = (rule.cls === 'both' || rule.cls === 'start' || rule.cls === 'end')
          var el
          if (isSpacing && /^\s|\s$/.test(matched)) {
            // 边界上已经有人打了 ASCII 空格：⛔ 不插盒，更⛔ 不删字符。
            // trim 会把两侧空格吃掉，`中 a 中` 就变成 `中a中`——复制、检索、翻译全丢。
            frag.appendChild(document.createTextNode(matched))
            last = m.index + matched.length + (self.offset || 0)
            rule.re.lastIndex = last
            continue
          }
          if (isSpacing) {
            el = document.createElement('cjk-spacing')
            if (rule.cls === 'start') el.className = 'cjk-spacing-start'
            else if (rule.cls === 'end') el.className = 'cjk-spacing-end'
            else el.className = 'cjk-spacing-start cjk-spacing-end'
            el.textContent = matched.trim()
          } else {
            el = document.createElement('cjk-adjacent')
            el.className = (rule.cls === 'half') ? 'cjk-adjacent-half' : 'cjk-adjacent-quarter'
            el.textContent = matched
          }
          frag.appendChild(el)
          last = m.index + matched.length + (self.offset || 0)
          rule.re.lastIndex = last
        }
        if (last < s.length) frag.appendChild(document.createTextNode(s.slice(last)))
        if (frag.childNodes.length) textNode.parentNode.replaceChild(frag, textNode)
      })
    })
    return this
  }

  CJKSpacing.QUOTE_SET = QUOTE_SET
  global.CJKSpacing = CJKSpacing
})(typeof window !== 'undefined' ? window : this)
