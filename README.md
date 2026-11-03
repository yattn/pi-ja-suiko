# pi-japanese-editor

Pi用の日本語推敲パッケージ。

`japanese_editor` で別のPiプロセスを起動し、DeepSeek V4.1 Flashで原稿を推敲します。

## 必要なもの

- Pi
- `opencode-go/deepseek-v4.1-flash`
- Node.js

モデル名は `deepseek-v4.1-flash` で固定しています。

## インストール

```sh
pi install git:github.com/yattn/pi-japanese-editor
```

## 使い方

```text
/skill:japanese-editor README.mdを推敲して
```

子Piではツール・拡張・MCP・セッション保存を無効にし、次の内容を返します。

- 推敲案の全文
- 主な変更点
- 意味や事実関係の要確認箇所

失敗時は別モデルに切り替えません。原稿は最大60,000文字、実行上限は240秒です。

## 任意の差分検査

Python 3.10以降があれば、数字・否定・条件・コードなどの変更を検出できます。

```sh
python3 skills/japanese-editor/scripts/check.py examples/original.md examples/revised.md
```

テスト：

```sh
node --test tests/runner.test.mjs
python3 -m unittest discover -s tests -p 'test_check.py'
```

## 参考

原意を守る推敲方針は [yomiyasu](https://github.com/nanaism/yomiyasu) を参考にしました。
