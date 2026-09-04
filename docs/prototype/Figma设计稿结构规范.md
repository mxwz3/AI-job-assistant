# AI 求职助手 · Figma 设计稿结构规范

> 源文件：`docs/prototype/AI求职助手-低保真原型.html`
> 用途：将该 HTML 低保真原型 1:1 还原为 Figma 可编辑设计稿。所有尺寸/颜色/间距均取自原型 CSS，可直接照表搭建。
> 字体建议：**Noto Sans SC**（Figma 内置 Google 字体，跨平台一致；权重 400 / 500 / 700）

---

## 1. Figma 文件组织

```
📄 AI求职助手-低保真原型
├── Page 1  📐 设计规范 Tokens      （颜色/文字/效果样式表）
├── Page 2  🧩 组件库 Components    （全部组件 + Variants）
└── Page 3  📱 原型-用户流程 Prototype（5 个页面 Frame + 标注 + 原型连线）
```

页面 Frame 命名：

| Frame | 名称 | 尺寸 |
|---|---|---|
| F1 | `01 上传简历` | 1440 × 自适应（min 900） |
| F2 | `02 上传JD` | 1440 × 自适应 |
| F3 | `03 匹配分析` | 1440 × 自适应 |
| F4 | `04 优化建议` | 1440 × 自适应 |
| F5 | `05 优化后简历` | 1440 × 自适应 |
| F0（可选） | `00 用户流程图 Cover` | 1440 × 640 |

---

## 2. 设计令牌（Tokens）

### 2.1 颜色样式（Paint Styles）

| 样式名 | HEX | 用途 |
|---|---|---|
| `ink/主文字` | `#2B2F33` | 标题、正文、强调描边 |
| `ink/次文字` | `#6B7178` | 说明文字、未激活态、占位标签 |
| `line/强描边` | `#9AA0A6` | 卡片描边、主按钮描边 |
| `line/细分隔` | `#C9CCD1` | 分隔线、虚线、未完成步骤线 |
| `fill/灰底` | `#F1F2F4` | 标签底、AI 气泡底 |
| `fill/灰底深` | `#E4E6E9` | 主按钮底、占位条、中性徽章底 |
| `paper/白` | `#FFFFFF` | 卡片、Frame 背景 |
| `accent/绿` | `#10B981` | 步骤完成/当前、成功徽章、匹配-已匹配 |
| `accent/绿-浅底` | `#E7F7F0` | 修改后对比块、成功提示底、激活侧栏项 |
| `accent/绿-深字` | `#14684A` | 绿底上的文字（对比块标签、✓徽章文字） |
| `warn/黄` | `#F5A623` | 部分匹配徽章/描边 |
| `warn/黄-浅底` | `#FDF3E0` | 匹配度分数盒底、部分匹配区底 |
| `danger/红` | `#E05252` | 不匹配徽章/描边、问题关键词 |
| `danger/红-浅底` | `#FBECEC` | 不匹配区底 |
| `note/标注底` | `#FFF8D6` | 交互标注块底色 |
| `note/标注描边` | `#B89A12` | 标注块虚线描边、标注圆点描边 |
| `note/标注文字` | `#554800` | 标注正文 |
| `canvas/画布` | `#DFE2E6` | Figma 画布底（非 Frame 内） |

> 说明：原 CSS 中 1.2px / 1.5px 描边在 Figma 中统一取整为 **1px（细）/ 2px（强）**。

### 2.2 文字样式（Text Styles）

| 样式名 | 字号/行高 | 权重 | 用途 |
|---|---|---|---|
| `T1/页面标题` | 15 / 22 | Bold | 顶栏「AI 求职工作台」 |
| `T2/卡片标题` | 14 / 20 | Bold | 各卡片 h3、页面大标题 |
| `T3/正文` | 13 / 20 | Regular | 通用正文、按钮文字 |
| `T3M/正文强调` | 13 / 20 | Medium | 卡片内字段值、数字 |
| `T4/辅助说明` | 12 / 18 | Regular | 副标题 sub、AI 气泡、标注正文 |
| `T5/标签徽章` | 11 / 16 | Bold | Tag、Badge、diff 标签 |
| `T6/匹配度数字` | 30 / 36 | Bold | 82% 大数字 |
| `T7/流程说明` | 11.5 / 17 | Regular | 状态流转图、快捷提问 chip |

### 2.3 圆角与描边

| 令牌 | 值 | 应用 |
|---|---|---|
| `R/小` | 4 | 文件框、流程节点 |
| `R/中` | 5–6 | 按钮、卡片、PartItem、页面 Frame |
| `R/大` | 8 | 对话气泡、分数盒 |
| `R/胶囊` | 10–14 | Badge(10)、chip(12)、步骤项(14) |
| `B/细` | 1px `line/细分隔` | 分隔线、虚线 |
| `B/默认` | 1px `line/强描边` | 卡片、标签 |
| `B/强` | 2px `ink/主文字` | 页面 Frame 外框、主按钮、当前步骤 |
| `B/强调` | 2px `accent/绿` | 当前步骤、修改后块、已接受卡片 |
| `B/虚线` | 1px dashed | Ghost 按钮、待确认卡片、标注块 |

### 2.4 效果样式（Effect Styles）

| 样式名 | 值 | 应用 |
|---|---|---|
| `E/页面投影` | Drop shadow `0, 2, 0` `rgba(0,0,0,0.15)` | 页面 Frame |
| `E/主按钮底边` | Inner shadow `0, -2, 0` `#C9CCD1` | Primary 按钮底边压线 |

### 2.5 栅格

- 主内容区按 **2pt 基准**（间距值 4/6/8/10/12/14/16，均来自原型 CSS，勿随意归整为 8pt）。
- 页面 Frame：垂直 Auto Layout；Body 三栏水平布局：侧栏 128 固定 / 主区 Fill / AI 助手 250 固定。

---

## 3. 组件库（Page 2）

> 目录结构建议按「原子 → 分子 → 页面级」三层；全部使用 Auto Layout；变色处一律做成 **Variants**，不要散搭。

### 3.1 原子组件（Atoms）

**① Button 按钮**　Variant 属性：`Type = Primary | Secondary | Ghost`　`Size = Default | Small`　`State = Default | Loading | Disabled`

| Type | 底色 | 描边 | 文字 |
|---|---|---|---|
| Primary | `fill/灰底深` + `E/主按钮底边` | 2px `ink` | `ink` Bold |
| Secondary | `paper/白` | 2px `ink` | `ink` |
| Ghost | 透明 | 1px dashed `line/强描边` | `ink/次文字` |

- Size：Default padding `6/14`；Small padding `3/9`（T4 字号）
- Loading：文字替换为「解析中…／分析中…／AI正在生成…」+ 左侧 12px 虚线圆环（loading 图标占位）
- Disabled：整体 45% 透明度
- 实例文案：`上传并解析`、`开始分析`、`接受修改`、`全部接受`、`全部保留`、`下载 AI 优化版 PDF`、`查看修改记录`、`下载原始简历`（后两个为 Secondary/Small）

**② Tag 标签**　Variant：`Kind = Module模块 | Type建议类型 | Skill技能 | Keyword关键词`
- 样式：`fill/灰底` + 1px `line/强描边`，R 胶囊(12)，padding `2/10`，T5
- 实例文案：模块（项目经历/技能/教育经历…）、类型（修改/强化/新增/删除/保留）、技能（SQL、Postman…）

**③ Badge 状态徽章**　Variant：`Status = Pending待确认 | Accepted已接受 | Kept已保留 | Edited已编辑 | CountOk已匹配 | CountPart部分 | CountBad不匹配 | Neutral中性`

| Status | 底 | 描边 | 文字 |
|---|---|---|---|
| Pending | `warn/黄` | 无 | 白「待确认」 |
| Accepted | `accent/绿-浅底` | 1px `accent/绿` | `accent/绿-深字`「✓ 已接受」 |
| Kept | `fill/灰底深` | 无 | `ink/次文字`「已保留原文」 |
| Edited | 同 Accepted | 同上 | 「✓ 已编辑并采用」 |
| CountOk / CountPart / CountBad | 绿/黄/红 | 无 | 白色数字 |
| Neutral | `fill/灰底深` | 无 | `ink/次文字`（类型/修改） |

**④ StepLine 步骤连接线**：22 × 0，1px dashed `line/细分隔`
**⑤ TextLine 占位文本条**：Variant `W = W40 | W60 | W80 | W100`；高 10，R 3，`fill/灰底深`
**⑥ ImgPlaceholder 图片占位**：斜线纹理填充（45°，`fill/灰底`），1px dashed `line/强描边`，内文字「占位」
**⑦ ChipQ 快捷提问**：`fill/灰底` + 1px `line/细分隔`，R 12，padding `3/9`，T7
**⑧ Notice 成功提示条**：`accent/绿-浅底` + 1px dashed `accent/绿`，R 5，padding `7/12`，T4，文字 `accent/绿-深字`，前缀「✓」
**⑨ LinkEdit 文字链**：T4，`ink/次文字`，下划线；实例：「重新上传」「编辑」
**⑩ Anno 标注点**：16 × 16 圆，`note/标注底` + 1px `note/标注描边`，内 10.5px 数字；**放在标注层，不入产品 Frame**（见 §5）

### 3.2 分子组件（Molecules）

**⑪ StepItem 步骤项**　Variant：`State = Current当前 | Done完成 | Upcoming未完成`
- 容器：水平 AL，padding `4/10`，gap 6，R 14
- 编号圈：20 × 20 圆。Current/Upcoming：白底；Done：`accent/绿`底白字「✓」
- Current：外描边 2px `accent/绿`，编号圈同色白字 Bold，label `ink` Bold；Upcoming：label/编号 `ink/次文字`；Done：label `accent/绿`
- Label 文案：上传简历 / 输入岗位JD / 匹配分析 / 优化建议 / 优化后简历

**⑫ SideItem 侧栏项**　Variant：`State = Default | Active`
- 水平 AL，padding `8/10`，gap 7，R 5；图标 13×13（1.2px 描边方框占位）+ 文字
- Active：`accent/绿-浅底` + 1.5→2px `accent/绿` 描边（outline），文字 `ink` Bold

**⑬ Card 基础卡片**：白底 + 1px `line/强描边`，R 6，padding `14/16`；头部槽位（标题 T2 + 右侧链接槽）+ 内容槽

**⑭ ScoreBox 匹配度盒**：`warn/黄-浅底` + 2px `warn/黄`，R 8，padding `10/22`，居中；T6 数字 + T4 说明（「基本匹配」）

**⑮ BarRow 分数条**　水平 AL，gap 10：label 88 固定（T4 `ink/次文字`）→ Track（Fill 宽，高 12，白底 1px `line/强描边`，R 7，内 FillBar 条 R 6，条纹填充 `#C4C9CF/#D8DCE1`）→ 百分比 40 固定右对齐（T3M Bold）
- 实例宽度覆盖：85% / 75% / 80% / 85%

**⑯ PartItem 部分匹配条目**：白底 1px `line/细分隔` R 6，padding `9/12`；结构：名称（T3M Bold）→ 原因（T4 `ink/次文字`）→ Button/Small「发给 AI 助手优化」

**⑰ MatchZone 匹配分区**　Variant：`Severity = OK | Part | Bad`

| Severity | 描边 | 底色 | 头部 |
|---|---|---|---|
| OK | 1px `accent/绿` | `accent/绿-浅底` | 「已匹配」+ Badge/CountOk |
| Part | 1px `warn/黄` | `warn/黄-浅底` | 「部分匹配」+ Badge/CountPart |
| Bad | 1px `danger/红` | `danger/红-浅底` | 「不匹配」+ Badge/CountBad |

- Part 内容槽放 N × PartItem；OK/Bad 内容槽放 Tag/Skill 组（水平换行 AL，gap 6）

**⑱ DiffBlock 对比块**　Variant：`Kind = Before修改前 | After修改后`
- Before：`#F6F7F8` + 1px dashed `line/强描边`，R 5，padding `9/12`，文字 `ink/次文字`；顶部标签「修改前（原文摘录）」T5 `ink/次文字`
- After：`accent/绿-浅底` + 2px `accent/绿`，R 5；顶部标签「修改后（AI 建议）」T5 `accent/绿-深字`

**⑲ Bubble 对话气泡**　Variant：`Role = AI | User`
- AI：`fill/灰底` + 1px `line/细分隔`，R 8，padding `8/10`，T4
- User：`accent/绿-浅底` + 1px `accent/绿`，左边距 34

**⑳ StatsBar 统计栏**：`fill/灰底` + 2px `line/强描边`，R 6，padding `9/14`，gap 14，水平换行；内容：4 段统计文本（数字 Bold）+ 弹性空隙 + Button/Small ×2

### 3.3 页面级组件（Page-level）

**㉑ SuggestionCard 建议卡片**　Variant：`Status = Pending待确认 | Accepted已接受 | Kept已保留`

```
SuggestionCard（垂直 AL，1px line/强描边，R 6，裁切）
├─ Head（水平 AL，padding 8/14，#FAFAFA，底部虚线分隔，gap 8）
│   ├─ 编号 "#1"（T3M Bold）
│   ├─ Tag/Module（所属模块）
│   ├─ Tag/Type（建议类型）
│   ├─ Spacer(fill)
│   └─ Badge/Status
└─ Body（垂直 AL，padding 12/14，gap 10）
    ├─ 问题行：「问题：」红字 Bold + 描述（T3）
    ├─ DiffBlock/Before（槽：原文文本）
    ├─ DiffBlock/After（槽：建议文本）
    └─ [仅 Pending] Actions（水平 AL，gap 8，padding 0/14/12）
        ├─ Button/Small/Primary「接受修改」
        ├─ Button/Small/Secondary「编辑」
        └─ Button/Small/Secondary「保留原文」
```
- Accepted/Kept 变体：无 Actions 行；Pending 变体外框改 **dashed**
- Slots：Head 编号/Tag 文字、问题、Before 文本、After 文本均设为可覆盖文本

**㉒ TopBar 顶栏**：水平 AL，padding `10/16`，gap 12，底部 1px `line/强描边`；LogoPlaceholder 28×28（R 6，2px `ink`，斜纹填充 + 「Logo」）+ T1 标题

**㉓ StepsBar 步骤导航**：水平 AL，padding `12/16`，gap 6；结构 `StepItem ×5`，项间插入 StepLine；实例按当前页覆盖 Variant（见 §4 各 Frame 状态表）

**㉔ Sidebar 侧栏**：垂直 AL，宽 128 固定，padding `12/8`，gap 4，`#FAFAFA`，右侧 1px `line/细分隔`；5 × SideItem

**㉕ AssistantPanel AI 助手面板**：垂直 AL，宽 250 固定，`#FCFCFD`，左侧 1px `line/细分隔`，高度 Fill

```
├─ Head（padding 10/12，底部细分隔，gap 6）：状态点 7×7(accent 绿) + 「AI 助手」Bold + 「已就绪 >>」T4
├─ Chips（padding 8/10，换行，gap 5，底部虚线）：ChipQ ×3–5
├─ Messages（Fill 高，padding 10，gap 8）：Bubble ×N
└─ Input（padding 8/10，gap 6，顶部分隔）：输入框（Fill，1px line/细分隔 R5，T4 占位「有问题随时问我…」）+ 发送按钮（2px ink 描边 R5 padding 5/12）
```

**㉖ PageFrame 页面骨架**（嵌套实例用）

```
PageFrame（垂直 AL，宽 1440，白底，2px ink 外框 R6，E/页面投影）
├─ TopBar
├─ StepsBar
└─ Body（水平 AL，Fill，min-height 560）
    ├─ Sidebar
    ├─ Main（垂直 AL，Fill，padding 16/18，gap 14）  ← 每页差异区
    └─ AssistantPanel
```

---

## 4. 五个页面的 Main 区内容（差异层）

### F1 `01 上传简历`（流程：上传资料）

步骤状态：`1 Current`，其余 Upcoming；侧栏 Active=上传简历

| 顺序 | 组件 | 覆盖内容 |
|---|---|---|
| 1 | Card「上传简历」 | sub「支持文档 PDF 格式」；行内：文件框「选择文件」+ 文件名「王小明-软件测试工程师-简历.pdf」+ Button/Primary「上传并解析」；底部 Notice「✓ 简历解析成功，已提取关键信息用于匹配分析」 |
| 2 | Card「简历信息」 | 头部右侧 LinkEdit「重新上传」；三等分字段行：姓名 王小明 / 学校 武汉科技大学 / 专业 网络工程 本科；「技能」Tag/Skill ×11（功能测试、测试用例设计、SQL、MySQL、Java、Spring Boot、Postman、Git、Linux、SQL注入原理、Web安全基础）；「项目经历」bullet ×2（差旅报销系统 / Web 安全测试实验，全文见 HTML） |

### F2 `02 上传JD`（流程：上传资料）

步骤状态：`1 Done，2 Current`；侧栏 Active=上传 JD

| 顺序 | 组件 | 覆盖内容 |
|---|---|---|
| 1 | Card「招聘 JD」 | sub「粘贴目标岗位的职位描述文本」；JD 文本容器（1px `line/强描边` R5，`#FCFCFD`，padding `12/14`，高 220 裁切，岗位职责 4 条 + 任职要求 4 条全文）；右对齐 Button/Primary「开始分析」 |
| 2 | Card「分析结果」 | sub「AI 提取的岗位结构化信息」；两列栅格（水平 AL 两个 Fill 列）：左=岗位名称 TextLine/W60 + 岗位职责 W100/W80/W80；右=技能要求 W100/W60 + 硬性要求 W80/W40 |

### F3 `03 匹配分析`（流程：AI 分析）

步骤状态：`1–2 Done，3 Current`；侧栏 Active=匹配分析

| 顺序 | 组件 | 覆盖内容 |
|---|---|---|
| 1 | Card「岗位匹配分析」 | 头部左：标题 + sub「目标岗位：软件测试工程师」；头部右：ScoreBox（**82%** / 基本匹配）；总结行：「整体匹配较好，主要差距集中在**接口测试经验**和**相关项目描述**…」（关键词 Bold） |
| 2 | Card「四维匹配拆解」 | BarRow ×4：技能匹配 85% / 项目匹配 75% / 经验匹配 80% / 岗位要求覆盖 85% |
| 3 | Card「技能匹配情况」 | MatchZone/OK：Tag ×8；MatchZone/Part：PartItem ×3（接口测试 / 自动化测试与测试平台开发 / 缺陷跟踪与报告输出，原因全文见 HTML）；MatchZone/Bad：Tag ×3（性能测试基础、Jira/禅道等管理工具、测试平台开发经验） |

### F4 `04 优化建议`（流程：获取建议）

步骤状态：`1–3 Done，4 Current`；侧栏 Active=优化建议

| 顺序 | 组件 | 覆盖内容 |
|---|---|---|
| 1 | 标题组 | 「AI 优化建议」T2 + sub「AI 只提出建议，不会直接修改简历。逐条确认后才会写入『优化后简历』。」 |
| 2 | StatsBar | 「AI 发现 **4** 项可优化内容／已接受 **3** 项／已保留 **1** 项／待确认 **0** 项」+ Button/Small ×2「全部接受」「全部保留」 |
| 3 | SuggestionCard `#1` Accepted | 模块=技能标签，类型=修改；问题「项目时间逻辑描述缺乏量化与深度」；Before/After 全文见 HTML |
| 4 | SuggestionCard `#2` Kept | 模块=技能，类型=修改；问题「接口测试技能覆盖面描述不够专业」 |
| 5 | SuggestionCard `#4` **Pending（dashed）** | 模块=项目经历，类型=强化；含 Actions 行：接受修改 / 编辑 / 保留原文 |

### F5 `05 优化后简历`（流程：生成优化简历）

步骤状态：`1–4 Done，5 Current`；侧栏 Active=优化后简历

| 顺序 | 组件 | 覆盖内容 |
|---|---|---|
| 1 | 头部行 | 左：标题「我的优化后简历」+ sub「基于 AI 建议逐条编辑和确认后的真实可编辑简历」；右：Button/Small「查看修改记录」+「下载原始简历」+ Button/Small/Primary「下载 AI 优化版 PDF」 |
| 2 | TabBar | 水平 AL，gap 4，底 1px `line/细分隔`；Tab（padding 7/16，R 6/6/0/0）：原始简历 / **优化后简历（on：白底 2px ink 顶描边 Bold）** / PDF 预览 / 修改记录 |
| 3–8 | Card ×6 | 姓名 / 联系方式 / 求职意向 / 教育经历 / 技能（Tag ×9 + Tag ×2 说明行）/ 项目经历（bullet ×2，内容为接受 AI 建议后的版本）；每卡右上 LinkEdit「编辑」 |

---

## 5. 标注层（评审用，与产品 Frame 分离）

- HTML 中每页底部的黄色「本页交互说明」块 → Figma 中做成 **NotesBlock 组件**（`note/标注底` + 1px dashed `note/标注描边`，R 6，padding `12/16`，内含 Anno 点 + 说明行），**放置在对应页面 Frame 右侧或下方 40px 处**，不嵌入产品 Frame 内部。
- 界面内的 Anso 编号点（①②…）：在产品 Frame 上以「标注覆盖层」形式叠加（单独 Layer 文件夹 `Annotations`，评审时可整体隐藏，原型演示时关闭可见性）。
- F4 的「状态流转图」（pending→accepted/edited/kept→解锁第 5 步）：做成独立 FD-Flow 组件（`fd-node` 白底 1px `note/标注描边` R4 + 箭头文字），置于 F4 标注块内。

---

## 6. 原型连线（Prototype）

| 触发对象 | 交互 | 目标 Frame |
|---|---|---|
| StepsBar 的 StepItem（所有页） | On Click → Navigate to | 对应 F1–F5 |
| Sidebar 的 SideItem（所有页） | On Click → Navigate to | 对应 F1–F5 |
| F1「上传并解析」 | On Click → Navigate to F1（自身，演示 loading 态可用 Component Interaction 或跳回） | 可选 |
| F1→F2 顺序演示 | On Click（步骤2） | F2 |
| F4 Pending 卡「接受修改」 | On Click → Navigate to F4（覆盖展示 Accepted 变体，或用 Variant Interaction 切换 Status） | 建议：用 **After delay 800ms → 变体切换** 演示状态流转 |
| F5「下载 AI 优化版 PDF」 | On Click → 无跳转（标注即可） | — |

- Flow 设置：F1 为 Flow Start（设备：Desktop 1440）；五个 Frame 可放入同一条 Flow 按步骤串联，也可分 5 条 Flow 便于评审跳转。
- 滚动：Main 与 AssistantPanel 的 Messages 设 Overflow → Vertical。
- HTML 原型里的深色「原型工具栏」**不复刻**——其功能（流程跳转/上一步下一步）由 Figma Prototype 连线与 Flow 导航承担。

---

## 7. 快速落地路径（二选一）

1. **插件导入（推荐起步）**：Figma 安装 `html.to.design` 插件 → 粘贴原型 HTML 或上传文件 → 生成可编辑图层 → 按 §2 令牌替换颜色/文字样式、按 §3 重组为组件。导入结果仅作底稿，Auto Layout 需手工校正。
2. **按规范手工搭建**：先建 Page1 Tokens（发布为样式库）→ Page2 组件（发布组件库）→ Page3 用实例拼装 5 个 Frame。搭建顺序：PageFrame 骨架 → TopBar/StepsBar/Sidebar/Assistant → 各页 Main 差异区。

> 验收基准：5 个 Frame 的步骤状态、侧栏激活项、卡片内容与 HTML 原型逐页一致；组件变体切换后无需重排版（Auto Layout 正确约束）。
