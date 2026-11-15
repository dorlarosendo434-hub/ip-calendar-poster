# 温柔手写排版规范

使用已确认的 C 版作为每个系列的默认版式。以下像素值以 3072×4096 成图为基准，随输出宽度同比缩放。

| 信息 | 字库 | 排版 |
| --- | --- | --- |
| 中文年月 | 霞鹜文楷 Medium | 120px，3px 同色描边加粗，水彩卡片上部居中 |
| 英文月份 | 霞鹜文楷 Medium | 52px，原字重，居中另起一行 |
| 周一至周日 | 思源黑体 Heavy | 七列统一 56px，周末沿用当月强调色 |
| 公历数字 | 思源宋体 SemiBold | 随实际行高调整，最大 98px |
| 农历、节气和节日 | 思源黑体 Regular | 随实际行高调整，最大 43px，与公历数字的可见间距为 20px |

日期网格使用已确认样张的安全区作为排版起点：`--left 0.155 --right 0.815 --top 0.491 --bottom 0.886`。横向范围为画面宽度的 15.5% 至 81.5%，卡片排版起点和日期网格下界分别为画面高度的 49.1% 和 88.6%。按真实周数均分日期区，日期组在各行居中。以最后一行下方的留白和装饰为验收依据，可微调安全区以避开当月枝叶、果实和纸边。保留组内间距和字体层级，避免把样张的固定周间距套给不同周数的月份。

## 字库与渲染

把以下四个上游字体文件放入同一个目录。它们均为 SIL OFL 1.1。直接从该目录加载，排版不使用微软雅黑、Georgia 或其他系统字体作为自动回退。

- [LXGWWenKai-Medium.ttf](https://github.com/lxgw/LxgwWenKai/releases/latest/download/LXGWWenKai-Medium.ttf) · [授权](https://github.com/lxgw/LxgwWenKai/blob/main/OFL.txt)
- [SourceHanSansSC-Heavy.otf](https://raw.githubusercontent.com/adobe-fonts/source-han-sans/release/OTF/SimplifiedChinese/SourceHanSansSC-Heavy.otf) 和 [SourceHanSansSC-Regular.otf](https://raw.githubusercontent.com/adobe-fonts/source-han-sans/release/OTF/SimplifiedChinese/SourceHanSansSC-Regular.otf) · [授权](https://github.com/adobe-fonts/source-han-sans/blob/master/LICENSE.txt)
- [SourceHanSerifSC-SemiBold.otf](https://raw.githubusercontent.com/adobe-fonts/source-han-serif/release/OTF/SimplifiedChinese/SourceHanSerifSC-SemiBold.otf) · [授权](https://github.com/adobe-fonts/source-han-serif/blob/master/LICENSE.txt)

```text
python scripts/render_calendar_card.py --base base.png --data verified-calendar.json --out month.png --font-dir fonts
```

`--font-dir` 自动按上表分配字库，应用默认字号、加粗和安全区。新系列确认1月样张时记录实际字库文件版本、强调色和安全区，便于全年复现。只有用户明确换字体时才按需使用 `--font-title`、`--font-cn-bold`、`--font-number`、`--font-cn` 和 `--font-english` 覆盖字库。
