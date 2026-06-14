# スカイピア削除自動化 仕様書

## 目的

楽天RMSと連携しているスカイピア管理ツールで、削除対象の商品データを安全に削除する作業を自動化する。

## 対象機能

1. 商品番号指定削除
2. 商品管理「削除済み」完全削除
3. 出品選択 全削除

## 実装優先順

1. ログイン処理
2. 商品管理画面への遷移
3. 商品番号指定削除
4. 商品管理「削除済み」完全削除
5. 商品番号指定削除から削除済み完全削除の連続実行
6. ログ出力
7. エラー時スクリーンショット保存
8. リトライ処理
9. 出品選択 全削除

## 重要ルール

1. 削除確認画面の「対象のASINをNG登録する」は絶対にチェックしない。
2. もしチェックされている場合は、必ず外してから削除する。
3. 表示件数は原則200件とする。
4. 500件、1000件は重くなるため通常使用しない。
5. 商品管理の「削除済み」検索では、必ずソート「登録が古い順」を指定する。
6. 商品管理の「削除済み」完全削除では、ページ送りはせず、毎回1ページ目を削除して再検索する。
7. 出品選択 全削除でも、ページ送りはせず、毎回1ページ目を削除して再読み込みする。
8. 処理結果は必ずCSVに記録する。
9. エラー時はスクリーンショットを保存する。
10. ログイン情報はコードに直接書かず、`.env` で管理する。

## URL

ログインURL:

```text
https://skypiea-5729766ef843.herokuapp.com/users/sign_in
```

商品管理画面URLは、実画面確認後に `config.json` の `product_management_url` に設定する。未設定の場合はログイン後に「商品管理」リンクをクリックして遷移する。

## 入力

商品番号指定削除では、以下のファイルに商品番号を1行ずつ記載する。

```text
input/item_numbers.txt
```

空行と前後の空白は除外し、重複は削除する。

## 出力

ログ:

```text
output/logs/
```

スクリーンショット:

```text
output/screenshots/
```

処理結果CSV:

```text
output/delete_results.csv
```

CSV列:

```csv
datetime,mode,loop,display_count,deleted_count,result,detail,screenshot
```

## 設定値

```text
DEFAULT_DISPLAY_COUNT=200
FALLBACK_DISPLAY_COUNTS=100,50
DISABLED_DISPLAY_COUNTS=500,1000
ITEM_NUMBER_DELETE_CHUNK_SIZE=50
ITEM_NUMBER_DELETE_FALLBACK_CHUNK_SIZE=30,10,1
WAIT_AFTER_DELETE_SECONDS=5
MAX_RETRY=2
PAGE_LOAD_TIMEOUT=60
SEARCH_TIMEOUT=60
DELETE_CONFIRM_TIMEOUT=60
DELETE_COMPLETE_TIMEOUT=120
RESTART_BROWSER_EVERY_LOOPS=20
```

## 完了条件

- `docs/SPEC.md` が作成されている。
- ログインできる。
- 商品管理画面へ移動できる。
- 商品番号指定削除ができる。
- 削除確認画面でASIN NG登録チェックを外せる。
- 商品管理でステータス「削除済み」、ソート「登録が古い順」、表示件数200件で検索できる。
- 削除済み商品が0件になるまで完全削除を繰り返せる。
- 商品番号指定削除から削除済み完全削除を連続実行できる。
- 出品選択画面の一覧を200件ずつ全削除できる。
- ログをCSVに保存できる。
- エラー時にスクリーンショットを保存できる。
