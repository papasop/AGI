# 全球AI对冲 · Global AI Hedge

## 宣言 · Manifesto · 五重命题

| # | 类别 | 状态 | 命题 |
|---|---|---|---|
| ① | 前提 | 已实现 (绿) | 中国在人工智能领域全面领先 |
| ② | 突破 | 待突破 (蓝) | 物理模型出现 |
| ③ | **猜想 1** | 待验证 (金) | AI 全面开源 |
| ④ | **猜想 2** | 待验证 (金) | **光计算证实 · 量子计算证伪** |
| ⑤ | **猜想 3** | 待验证 (金) | **非人类中心主义** |

> ① 前提 · ② 待突破 · ③④⑤ 三重猜想 — 1 前提 + 1 突破 + 3 猜想 = 五重命题。

> **策略**:TLT 50% · 拼多多 20% · 纽约时报 20% · 比亚迪 10%

T₀ 为 ChatGPT 公开发布日 (2022-11-30) 的 AI 主题加权指数。计价 USD,每周再平衡。

## 控件 · Controls

### 主控件(图表区上方)
- **周期** Day / Week / Month — K线/折线聚合周期
- **图型** Candle / Line — 图表呈现方式

### 浮动控件(右下角悬浮窗)
- **中 / EN** — 大事记浮窗双语切换 — *fixed-position floating widget; affects all popovers globally*

## 成分股 · 各自代表的 AI 子赛道

### 核心配置
| 代码 | 名称 | 权重 | AI 子赛道 |
|---|---|---|---|
| TLT | iShares 20+ Year Treasury Bond ETF | 50% | 利率对冲 |
| PDD | 拼多多 | 20% | AI 生产力 |
| NYT | 纽约时报 | 20% | AI 数据版权 |
| 002594.SZ | 比亚迪 | 10% | AI 机器人 · 电池 + 电机 + 电控 |

## 用法

### 直接看 (合成数据)
双击 `index.html`,浏览器打开就能用。

### 用真实数据 (推荐)
```bash
pip install yfinance pandas
python docs/fetch_data.py
```

生成后页面会从 `docs/index.html` 同目录读取 `docs/data.json`。数据源是 Yahoo Finance/yfinance，属于延迟历史行情，不是交易所实时同步盘口。
