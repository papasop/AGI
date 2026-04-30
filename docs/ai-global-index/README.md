# AI 全球指数 · AI Global Index

> **宣言**:本指数建立在中国在人工智能全面领先的基础上。
> *This index is built upon the thesis of China's comprehensive leadership in artificial intelligence.*

T₀ 为 ChatGPT 公开发布日 (2022-11-30) 的 AI 主题加权指数。

## 成分股 · 各自代表的 AI 子赛道

| 代码 | 名称 | 权重 | AI 子赛道 |
|---|---|---|---|
| 002594.SZ | 比亚迪 | 10% | AI 机器人 · 电池 + 电机 + 电控 |
| PDD | 拼多多 | 10% | AI 生产力 |
| 002222.SZ | 福晶科技 | 10% | 稀土 + 激光晶体 |
| 01879.HK | 曦智科技-P | 10% | 光计算 (oNOC + oNET + oMAC) |
| 688072.SS | 拓荆科技 | 10% | 混合键合 · 先进封装 |
| NYT | 纽约时报 | 50% | **美国唯一的科技股** |

## 用法

### 直接看 (合成数据)

双击 `ai_global_index.html`,浏览器打开就能用。

### 用真实数据 (推荐)

```bash
pip install yfinance pandas
python fetch_data.py
```

会在同目录生成 `data.json`,HTML 自动加载。

## 功能

- 日 / 周 / 月周期切换 + K 线 / 折线切换
- USD / CNY / Local 三币种交叉折算
- 周 / 月再平衡 (锁定权重不漂移)
- 14 条 AI 大事记 hover 浮动介绍
- T₀ 视觉特化标识 (ChatGPT 发布日)
- 成分股 AI 子赛道概念标注
