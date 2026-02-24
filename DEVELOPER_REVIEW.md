# Developer Review: 化学+ (claw-web) 技术审查报告

> 审查日期: 2026-02-25
> 审查范围: 全站 HTML/CSS/JS/Python 构建脚本, 用户体验, 可访问性, 移动端适配

---

## 一、现有代码质量评估

### 1.1 HTML 语义化

**现状**: 整体结构合理, 使用了 `<nav>`, `<section>`, `<footer>`, `<main>`, `<aside>`, `<details>/<summary>` 等语义化标签。实验页面有面包屑导航、aside 侧边栏, 结构层次清晰。

**问题**:

- `index.html` 中 `<section id="basics">` 使用 `class="portfolio"`, `<section id="experiments">` 使用 `class="about"`, 类名与语义不匹配(这些是从模板沿用的命名, 如 "portfolio" / "about" / "contact")。
- Hero 区域的布局使用了 inline style `style="display: flex; align-items: center;"`, 应移入 CSS。
- 实验卡片列表 `#expCardList` 的 `style="margin-top: 1.25rem;"` 也是 inline style。
- 缺少 `<h1>` 在实验页面(只有 `<h2>` 作为标题), 不利于 SEO 和文档大纲。
- 导航栏缺少 `aria-label="主导航"` 等无障碍属性。

### 1.2 CSS 组织

**现状**: 单文件 `site.css` 约 530 行, 使用 CSS 变量管理主题色, 结构清晰(按区域分块注释)。有 `@media print` 和 `@media (max-width: 768px)` 两个媒体查询。

**问题**:

- 只有一个断点 `768px`, 缺少平板(1024px)和小屏手机(480px)的适配。
- `.portfolio` / `.about` / `.contact` 的命名不直观, 实际只是背景色不同的 section 容器。
- 没有 `:focus-visible` 样式, 键盘导航时无法看到焦点指示器。
- 没有 `prefers-color-scheme` 或 `prefers-reduced-motion` 的媒体查询。
- 打印样式不完整: `details` 元素在打印时不会自动展开; 文本渐变色在打印时会消失(如 `.section-title` 的 `-webkit-background-clip: text`)。

### 1.3 JavaScript 代码结构

**现状**: 两个极简脚本, 分别约 50 行和 27 行, 用 IIFE 包裹避免全局污染。无第三方依赖, 纯原生 JS, 非常轻量。

**问题**:

- `site.js` 搜索只支持精确匹配中文字符串(不支持拼音、模糊匹配、分词)。
- 搜索无防抖(debounce), 每次按键都触发 DOM 遍历。对 20 个卡片影响不大, 但不是最佳实践。
- 联系表单提交是纯前端模拟(setTimeout 800ms), 不连接后端, 用户提交后数据丢失。
- `experiment.js` 中"全部展开/收起"无动画过渡。
- 没有错误处理或 fallback 逻辑。

### 1.4 构建脚本 (Python)

**现状**: `build_site.py` 约 445 行, `generate_experiment_data.py` 约 158 行, `generate_covers.py` 约 377 行。代码质量较高: 使用 dataclass、type hints、合理的函数拆分。

**问题**:

- `generate_experiment_data.py` 依赖系统命令 `pdftotext`, 未在文档中说明依赖项。
- `_extract_text_from_pdf()` 创建临时文件后未显式删除(`delete=False` 且无 cleanup)。
- `build_site.py` 中 HTML 模板用 f-string 拼接, 当模板复杂度增加时可维护性会下降。
- 没有 `requirements.txt` 或构建说明文档。
- `generate_covers.py` 中 SVG 元素的 `id` 属性(如 `id="bg"`, `id="accent"`, `id="shadow"`)在同一页面中多个 SVG 内联时可能冲突。

---

## 二、移动端适配

### 2.1 当前状况

- 在 768px 以下: 导航链接完全隐藏 (`display: none`), 但没有汉堡菜单替代。
- Hero 区域布局切换为 column, 但 avatar 的 `margin-top: 2rem` 在小屏上偏大。
- `.two-col` 在移动端正确切换为单列, 但 aside(keybox) 会排在主内容下方, 需要滚动很远才能看到。
- PDF 查看器在手机上几乎不可用(75vh 高度但 PDF 嵌入在移动浏览器上通常不渲染)。

### 2.2 缺失的适配

- 无汉堡菜单: 移动端用户无法导航到其他 section。
- 搜索框在手机上没有特殊处理: `min-width: 240px` 在 320px 宽屏幕上溢出。
- 实验页面的标题使用 `font-size: 2.5rem` (section-title 默认), 在手机上过大。
- 卡片网格 `minmax(260px, 1fr)` 在 320px 设备上会出现水平滚动。
- 触控目标: 导航链接和 pill 按钮的点击区域偏小, 建议最小 44x44px。

---

## 三、交互体验

### 3.1 搜索功能
- 只有首页有搜索, 实验页面内部没有搜索。
- 不支持拼音输入(如输入 "yangqi" 无法匹配 "氧气")。
- 搜索结果无高亮, 无"未找到结果"提示。
- 无分类筛选(如按实验类型: 制气、性质、定量等)。

### 3.2 导航
- 实验页面有上一篇/下一篇导航, 但缺少"回到顶部"按钮。
- 实验页面没有页内锚点导航(目录), 长页面需要大量滚动。
- 首页导航锚点使用自定义 smooth scroll, 但 `offset: -80` 是硬编码值, 如果导航栏高度变化会错位。

### 3.3 折叠面板
- 默认全部展开(除 PDF 摘录), 合理。
- "全部展开/收起"按钮功能正确, 但没有状态反馈(如按钮文字变化)。
- 单个 details 没有过渡动画。

---

## 四、可访问性 (A11y)

**问题清单**:

1. **键盘导航**: 无 `:focus-visible` 样式, Tab 键导航时用户无法看到当前焦点位置。
2. **ARIA 标签**: 导航栏缺少 `role="navigation"` 或 `aria-label`; 搜索框缺少 `aria-label`; 展开/收起按钮缺少 `aria-expanded` 状态。
3. **色彩对比度**: `--text-gray: #94a3b8` 在 `--bg-dark: #0f172a` 上的对比度约 5.4:1, 达到 AA 标准但未达到 AAA。卡片内的灰色文字 `--text-gray` 在 `--bg-card: #1e293b` 上对比度约 4.5:1, 刚好通过 AA。
4. **Skip-to-content 链接**: 缺少"跳到主要内容"的隐藏链接。
5. **语言切换**: 页面全中文, `lang="zh-CN"` 正确, 但化学方程式中的英文字母没有标注 `lang="en"`(影响较小)。
6. **图片 alt 文字**: SVG 封面图有 alt 文字, 较好; 但 Hero 区域的 emoji "test tube" 对屏幕阅读器不友好。

---

## 五、性能

**优势**:
- 零第三方依赖, 纯 HTML/CSS/JS, 首屏加载极快。
- SVG 封面图使用 `loading="lazy"`, 良好。
- CSS/JS 文件极小(CSS 约 12KB, JS 约 2KB)。

**问题**:
- PDF 文件名含中文, 可能在某些服务器/CDN 上造成编码问题。
- 没有 `<meta name="description">` 和 Open Graph 标签。
- 没有 favicon。
- SVG 封面文件虽然小, 但 20 个 SVG 在首页同时存在, 可考虑更激进的懒加载。
- CSS 中 `backdrop-filter: blur(10px)` 在低端设备上可能卡顿。

---

## 六、改进建议

### P0 - 高优先级

#### 6.1 移动端汉堡菜单
- **问题**: 768px 以下导航链接被隐藏, 用户无法导航。
- **方案**: 添加 CSS-only 或轻量 JS 汉堡菜单按钮, 点击展开/收起导航链接。
- **优先级**: 高 | **难度**: 简单
- **实现思路**: 添加一个 `<button class="menu-toggle">` 到 nav-container, 在 768px 以下显示; 点击切换 `.nav-links` 的 `display` 或 `max-height` 动画。纯 CSS 方案可用 checkbox hack, 但 JS 方案更灵活(约 15 行代码)。

#### 6.2 自测/遮盖模式
- **问题**: 学生复习时想先自己回忆再看答案, 目前所有内容直接可见。
- **方案**: 为 `<details>` 内的列表项添加"遮盖模式"切换, 开启后所有 `<li>` 内容被模糊/隐藏, 点击单个项才显示。
- **优先级**: 高 | **难度**: 中等
- **实现思路**: 添加一个"自测模式"toggle 按钮。开启时给 `.block-list li` 添加 CSS class `blur`, 样式为 `filter: blur(5px); cursor: pointer; user-select: none`。点击 `<li>` 时切换 class 显示内容。用 `localStorage` 记住用户偏好。

#### 6.3 学习进度追踪
- **问题**: 学生无法知道自己已经复习了哪些实验。
- **方案**: 使用 `localStorage` 记录已学习的实验, 在首页卡片上显示"已学习"标记, 提供进度条。
- **优先级**: 高 | **难度**: 简单
- **实现思路**: 每个实验页底部添加"标记为已学习"按钮。点击后将实验 ID 存入 `localStorage` 的 JSON 数组。首页卡片渲染时读取 localStorage, 已学习的卡片添加绿色 checkmark 角标。顶部显示 "已学习 X/20" 进度条。约 40 行 JS。

#### 6.4 键盘焦点与基本 A11y
- **问题**: 键盘导航无视觉反馈, 缺少 skip-to-content 链接。
- **方案**: 添加 `:focus-visible` 全局样式和 skip link。
- **优先级**: 高 | **难度**: 简单
- **实现思路**: CSS 中添加 `*:focus-visible { outline: 2px solid var(--primary); outline-offset: 2px; }`, 添加 `.sr-only` 隐藏类和 skip-to-content 链接。为搜索框和按钮添加 `aria-label`。

### P1 - 中优先级

#### 6.5 实验页内目录(TOC)导航
- **问题**: 实验页内容较长, 缺少快速跳转到特定 section 的方式。
- **方案**: 在实验页侧边栏(keybox)或顶部生成页内目录, 点击可平滑滚动到对应 `<details>` 块。
- **优先级**: 中 | **难度**: 中等
- **实现思路**: `experiment.js` 中遍历所有 `.exp-block summary`, 生成目录列表插入到 aside 中。每个目录项绑定 click 事件, scrollIntoView 到对应 details 并自动展开。可配合 IntersectionObserver 做高亮当前 section。

#### 6.6 暗/亮模式切换
- **问题**: 当前仅有暗色模式, 部分学生(尤其白天使用或打印)可能偏好亮色。
- **方案**: 添加 light theme CSS 变量集, 切换按钮存储到 localStorage。
- **优先级**: 中 | **难度**: 中等
- **实现思路**: 定义 `[data-theme="light"]` 变量覆盖: `--bg-dark: #f8fafc; --bg-card: #ffffff; --text-light: #1e293b; --text-gray: #64748b; --border: #e2e8f0`。在 nav 中添加切换按钮。JS 中读取 localStorage 并设置 `document.documentElement.dataset.theme`。约 20 行 JS + 20 行 CSS 变量。

#### 6.7 改进搜索 - 无结果提示 + 分类标签
- **问题**: 搜索无反馈, 无分类。
- **方案**: 添加"无结果"提示文字; 添加标签筛选(如"制气实验"/"性质探究"/"定量实验")。
- **优先级**: 中 | **难度**: 简单
- **实现思路**: 搜索后检查可见卡片数, 为 0 时显示提示 div。为每个实验卡片添加 `data-tags="制气,排水,KMnO4"` 属性, 添加 pill 标签按钮组, 点击切换 active 状态并过滤。约 30 行 JS。

#### 6.8 字体大小调节
- **问题**: 初中生视力差异较大, 固定字体大小可能不适合所有人。
- **方案**: 提供 A-/A/A+ 按钮, 切换 `<html>` 的 `font-size`。
- **优先级**: 中 | **难度**: 简单
- **实现思路**: 由于全站使用 rem 单位, 只需修改 `html { font-size }` 即可全局生效。在 nav 中添加三个按钮, JS 切换 font-size 在 14px / 16px / 18px 之间, 存 localStorage。约 15 行 JS。

#### 6.9 知识点收藏/标记
- **问题**: 学生无法标记重点或薄弱知识点。
- **方案**: 每个 `<li>` 旁添加"星标"按钮, 收藏后可在专门页面查看所有已收藏项。
- **优先级**: 中 | **难度**: 中等
- **实现思路**: 每个 `.block-list li` 前添加一个星标 icon button。点击后存入 localStorage, key 为 `starred`, value 为 `[{expId, blockLabel, itemIndex}]`。可在首页添加"我的收藏"入口, 汇总显示。约 60 行 JS。

#### 6.10 打印样式完善
- **问题**: 打印时渐变文字消失、details 不展开、侧边栏排版混乱。
- **方案**: 完善 `@media print` 样式。
- **优先级**: 中 | **难度**: 简单
- **实现思路**: 添加以下打印规则: `details[open] { display: block; }` (或 JS 在 beforeprint 时全部展开); `.section-title { background: none; -webkit-text-fill-color: #111827; }`; `.two-col { grid-template-columns: 1fr; }`; `.keybox { break-inside: avoid; border: 1px solid #d1d5db; }`. 约 20 行 CSS。

### P2 - 低优先级

#### 6.11 PWA 支持(离线使用)
- **问题**: 学生在地铁/无网络环境无法访问。
- **方案**: 添加 Service Worker 和 manifest.json, 实现离线缓存。
- **优先级**: 低 | **难度**: 中等
- **实现思路**: 创建 `manifest.json`(name, icons, theme_color); 创建 `sw.js` 使用 cache-first 策略缓存所有 HTML/CSS/JS/SVG; 在 `site.js` 中注册 Service Worker。PDF 文件较大(数 MB), 可选择性缓存或不缓存。

#### 6.12 实验之间的关联导航
- **问题**: 相关实验之间没有交叉引用(如"制氧气"的三个实验, "过滤"在多个实验中出现)。
- **方案**: 在实验页底部添加"相关实验"推荐。
- **优先级**: 低 | **难度**: 中等
- **实现思路**: 在 `exp_notes.json` 中为每个实验添加 `related: [2, 3]` 字段。`build_site.py` 渲染时读取并生成"相关实验"卡片链接。或通过共享关键词自动匹配。

#### 6.13 页面过渡动画
- **问题**: 页面间切换生硬, 无过渡效果。
- **方案**: 使用 View Transitions API 或轻量 CSS 动画。
- **优先级**: 低 | **难度**: 简单
- **实现思路**: 在 `<head>` 中添加 `<meta name="view-transition" content="same-origin">`, 配合 `::view-transition-old(root)` / `::view-transition-new(root)` CSS 规则。目前浏览器支持有限, 需 progressive enhancement。

#### 6.14 添加 favicon 和 meta 标签
- **问题**: 缺少 favicon, 无 Open Graph 标签, 分享到社交平台无预览。
- **方案**: 添加 favicon.ico/favicon.svg, 添加 OG 标签。
- **优先级**: 低 | **难度**: 简单
- **实现思路**: 用 SVG 制作一个简单的化学试管 favicon; 在 `<head>` 中添加 `<meta name="description">`, `<meta property="og:title">`, `<meta property="og:description">`, `<meta property="og:image">`。在 `build_site.py` 模板中统一添加。

#### 6.15 构建脚本改进
- **问题**: 缺少构建文档, 临时文件未清理, 无依赖声明。
- **方案**: 添加 README 构建说明, 修复临时文件泄漏, 添加 requirements.txt。
- **优先级**: 低 | **难度**: 简单
- **实现思路**: 在 `_extract_text_from_pdf()` 中使用 `try/finally` 或 `atexit` 清理临时文件。创建 `requirements.txt`(只需标注 pdftotext 系统依赖)。SVG 的 id 属性加 experiment 序号前缀避免冲突(如 `id="bg-01"`)。

---

## 七、CSS 类名重构建议(非紧急)

当前类名部分沿用自通用模板, 建议未来重构时统一命名:

| 现有类名 | 建议类名 | 原因 |
|----------|----------|------|
| `.about` | `.section-alt` 或 `.section--dark` | "about" 与化学实验无关 |
| `.portfolio` | `.section--card-bg` | "portfolio" 不直观 |
| `.contact` | `.section-qa` | 实际是问答区 |
| `.pill` | `.btn-pill` | 明确是按钮变体 |
| `.muted` | 保留 | 通用且直观 |

---

## 八、总结

### 做得好的地方
1. **零依赖架构**: 纯静态 HTML/CSS/JS, 加载速度极快, 非常适合教育场景。
2. **内容结构清晰**: 实验按 details/summary 分块, 层次分明, 适合复习。
3. **Python 构建脚本**: 代码质量高, 自动化程度好, 从 PDF 到网页的 pipeline 完整。
4. **SVG 封面图**: 程序化生成, 统一风格, 视觉效果好。
5. **化学式渲染**: 上下标处理考虑了多种场景(离子电荷、化学方程式系数等)。

### 最需改进的 3 件事
1. **移动端导航**: 添加汉堡菜单, 这是功能性 bug 而非优化。
2. **自测模式**: 对学习效果影响最大的功能改进, 符合"主动回忆"学习原理。
3. **学习进度**: 给学生成就感和方向感, 激励持续复习。

### 实施建议顺序
1. 汉堡菜单 + 焦点样式 (P0, 简单)
2. 学习进度追踪 (P0, 简单)
3. 自测遮盖模式 (P0, 中等)
4. 打印样式完善 (P1, 简单)
5. 搜索改进 (P1, 简单)
6. 暗亮模式 + 字体调节 (P1, 中等)
7. 页内 TOC (P1, 中等)
8. 其余 P2 项按需实施
