# handle-solver

自动解 [汉兜](https://handle.antfu.me)（中文 Wordle）的命令行工具。

## 使用

```bash
python solve.py
```

首次运行自动建库。然后跟着提示操作：

1. 在汉兜官网猜一个成语
2. 回到终端，输入你猜的词
3. 工具显示拼音，你对照游戏颜色输入 12 个数字（0=灰 1=黄 2=绿）
4. 工具给出候选词，选一个继续猜

示例输入：`马到成功 002 102 000 002`

## 词库

来自 [pwxcoo/chinese-xinhua](https://github.com/pwxcoo/chinese-xinhua)，已修正部分标注错误。
