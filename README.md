# スカイピア削除自動化ツール

楽天RMSと連携しているスカイピア管理ツールで、商品管理画面の削除作業を自動化するための Python + Playwright ツールです。

## 優先実装

1. ログイン処理
2. 商品管理画面への遷移
3. 商品番号指定削除
4. 商品管理「削除済み」完全削除
5. 商品番号指定削除から削除済み完全削除の連続実行
6. ログ出力
7. エラー時スクリーンショット保存
8. リトライ処理
9. 出品選択 全削除

## 初期設定

1. `.env.example` をコピーして `.env` を作成します。
2. `.env` にスカイピア管理ツールのログイン情報を入力します。
3. 必要に応じて `config.json` のURLや画面セレクタを実画面に合わせて調整します。
4. 商品番号指定削除を使う場合は `input/item_numbers.txt` に商品番号を1行ずつ入力します。

## 実行例

```bash
python src/main.py --mode login-check
python src/main.py --mode delete-by-item-numbers
python src/main.py --mode delete-deleted-items
python src/main.py --mode delete-by-item-numbers-and-clean
python src/main.py --mode delete-listing-candidates
```

## 重要ルール

削除確認画面の「対象のASINをNG登録する」は絶対にチェックしません。もしチェック済みの場合は、必ず外してから削除します。

商品管理の「削除済み」完全削除と、出品選択の全削除ではページ送りを行わず、毎回1ページ目を削除して再検索または再読み込みします。
