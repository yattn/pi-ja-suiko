# pi-suiko

Pi用の日本語推敲パッケージ。

読者の認知負荷を下げ、必要な情報を迷わず正確に理解できる文章に整えます。AIらしいかどうかではなく、読みやすさと正確さを基準に推敲します。短縮を目的にせず、理解に必要な説明は残します。

`suiko` で別のPiプロセスを起動し、DeepSeek V4.1 Flashで原稿を推敲します。

## 必要なもの

- Pi
- `opencode-go/deepseek-v4.1-flash`
- Node.js

モデル名は `deepseek-v4.1-flash` で固定しています。

## 方針

- 原意、技術的事実、コード、条件を守る。
- 情報の順序や構造を整え、理解に必要な説明を残す。
- 文章がAIらしいという理由だけでは修正しない。
- 自然で読みやすい箇所は無理に変更しない。

## インストール

```sh
pi install git:github.com/yattn/pi-ja-suiko
```

GitHubのリポジトリ名は現在も旧名です。リポジトリを `pi-suiko` に改名したら、インストール先も新しい名前に更新します。

## 使い方

```text
/skill:suiko README.mdを推敲して
```

推敲結果には次の内容が含まれます。

- 推敲案の全文
- 主な変更点
- 意味や事実関係の要確認箇所

原稿は最大60,000文字、実行上限は240秒です。失敗時は別モデルに切り替えません。

推敲用プロセスでは、ツール・拡張・MCP・セッション保存を無効にします。

## 任意の差分検査

Python 3.10以降があれば、数字・否定・条件・コードなどの変更を検出できます。

```sh
python3 skills/suiko/scripts/check.py examples/original.md examples/revised.md
```

テスト：

```sh
node --test tests/runner.test.mjs
python3 -m unittest discover -s tests -p 'test_check.py'
```

## 参考

原意を守る推敲方針は [yomiyasu](https://github.com/nanaism/yomiyasu) を参考にしました。
