# AI 全球指数 · AI Global Index

一个以 ChatGPT 公开发布日 (2022-11-30) 为 T₀ 的 AI 主题加权指数,
带 K 线 / 折线切换、日 / 周 / 月周期切换、USD / CNY / Local 计价切换、
周 / 月再平衡切换、AI 大事记 hover 浮动介绍。

## 成分

| 代码 | 名称 | 货币 | 权重 |
|---|---|---|---|
| 002594.SZ | 比亚迪 | CNY | 10% |
| PDD | 拼多多 | USD | 10% |
| 002222.SZ | 福晶科技 | CNY | 10% |
| 01879.HK | 曦智科技-P | HKD | 10% |
| 688072.SS | 拓荆科技 | CNY | 10% |
| NYT | 纽约时报 | USD | 50% |

## 用法

### 直接看 (合成数据)

双击 `ai_global_index.html`,浏览器打开就能用。
内置种子合成数据,起点为 ChatGPT 发布日 (2022-11-30),
覆盖至打开页面当天。

### 用真实数据 (推荐)

```bash
pip install yfinance pandas
python fetch_data.py
```

会在同目录生成 `data.json`,HTML 自动加载真实数据替换合成。

可选参数:
- `--start 2022-11-30` 起始日期 (默认 ChatGPT 发布日)
- `--end YYYY-MM-DD` 结束日期 (默认今天)

## 提交到 Entropy-AI 仓库

```bash
cd Entropy-AI/
cp ai_global_index.html .
cp fetch_data.py .
git add ai_global_index.html fetch_data.py
git commit -m "Add AI Global Index visualization"
```

## 技术细节

- 渲染: ECharts 5.4.3 (CDN)
- 指数构造: 起点归一化 + 权重加权
- 再平衡: 周度 (5 trading days) / 月度 (21 trading days)
- 计价: 三币种交叉折算 (CNY/USD via CNY=X, HKD/USD via HKD=X)
- 晚上市标的处理: 锚点日历 (BYD ∩ NYT) + 前向回填
- 14 条 AI 大事记 hover 浮动介绍

## 文件

- `ai_global_index.html` — 单文件可视化 (可独立部署)
- `fetch_data.py` — 真实数据抓取脚本
- `README.md` — 本文件
