# pi-japanese-editor

Pi用の日本語推敲パッケージ。`japanese_editor` ツールから別のPiプロセスを起動し、DeepSeek V4.1 Flashで原稿を推敲する。

追加のサブエージェント拡張やnpmパッケージは不要。原文のファイルは変更しない。

## 必要なもの

- Piと、`PATH` 上の `pi` コマンド
- Piに登録済みの `opencode-go/deepseek-v4.1-flash` と利用可能な認証情報
- Node.js（Piの実行環境）

モデル名は固定。OpenCode Goが配信するモデルのスナップショット（1017など）は、このパッケージでは指定・保証できない。

## インストール

```sh
pi install git:github.com/yattn/pi-japanese-editor
```

起動中のPiでは `/reload` を実行する。

## 使い方

```text
/skill:japanese-editor README.mdを推敲して。ファイルは変更しないで。
```

親Piが原稿を読み、`japanese_editor` ツールへ渡す。子Piはツール・拡張・MCP・セッション保存を無効にして1回実行し、次を返す。

- 推敲案の全文
- 主な変更点
- 意味や事実関係の要確認箇所

失敗時は別モデルに切り替えない。原稿は最大60,000文字、実行上限は240秒。

## 任意の差分検査

Python 3.10以降があれば、数字・否定・条件・コードなどの変更を検出できる。

```sh
python3 skills/japanese-editor/scripts/check.py examples/original.md examples/revised.md
```

検査は補助的なもの。警告がなくても意味の一致は保証しない。

テスト：

```sh
node --test tests/runner.test.mjs
python3 -m unittest discover -s tests -p 'test_check.py'
```

## 注意

原稿はOpenCode Goへ送信される。送信が認められていない文書には使用しない。子Piのツール制限はOSレベルのサンドボックスではない。

原意を守る推敲方針は [yomiyasu](https://github.com/nanaism/yomiyasu) を参考にした。コードは独立実装。

MIT License。詳細は [LICENSE](LICENSE) を参照。
