import assert from "node:assert/strict";
import { chmod, mkdtemp, rm, writeFile } from "node:fs/promises";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { after, before, test } from "node:test";
import { MAX_INPUT, MODEL, PROVIDER, runEditor } from "../extensions/runner.js";

let temp;
let mock;
before(async () => {
  temp = await mkdtemp(join(tmpdir(), "pi-ja-test-"));
  mock = join(temp, "pi");
  await writeFile(mock, `#!/usr/bin/env node
const args = process.argv.slice(2);
let input = '';
process.stdin.on('data', chunk => input += chunk);
process.stdin.on('end', () => {
  if (input.includes('fail-test')) { console.error('mock failure'); process.exit(7); }
  process.stdout.write(JSON.stringify({args, input}));
});
`, "utf8");
  await chmod(mock, 0o700);
});
after(async () => { if (temp) await rm(temp, { recursive: true, force: true }); });

test("子Piは固定モデル・ツール無効・標準入力で推敲原稿を受け取る", async () => {
  const result = JSON.parse(await runEditor("# 要件\n\n処理すること。", "である調を維持", { command: mock }));
  const args = result.args;
  for (const option of ["--print", "--no-tools", "--no-extensions", "--no-skills", "--no-mcp", "--no-context-files", "--no-session", "--no-prompt-templates", "--no-approve", "--system-prompt"]) {
    assert.ok(args.includes(option), `missing ${option}`);
  }
  assert.equal(args[args.indexOf("--provider") + 1], PROVIDER);
  assert.equal(args[args.indexOf("--model") + 1], MODEL);
  assert.match(result.input, /処理すること/);
  assert.match(result.input, /である調を維持/);
  assert.ok(!args.some(x => x.includes("処理すること")), "原稿はargvに出さない");
});

test("空原稿を拒否する", async () => {
  await assert.rejects(runEditor("\n"), /空/);
});

test("入力上限超過を拒否する", async () => {
  await assert.rejects(runEditor("あ".repeat(MAX_INPUT + 1)), /長すぎ/);
});

test("追加指示の上限超過を拒否する", async () => {
  await assert.rejects(runEditor("文章", "x".repeat(3001)), /追加指示/);
});

test("子Piが失敗した場合は成功扱いしない", async () => {
  await assert.rejects(runEditor("fail-test", "", { command: mock }), /exit 7/);
});

test("Piコマンドが見つからない場合も成功扱いしない", async () => {
  await assert.rejects(runEditor("文章", "", { command: join(temp, "missing-pi") }), /起動できません/);
});
