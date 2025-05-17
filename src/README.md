# PostgreSQL to CSV Exporter

このPythonスクリプトは、PostgreSQLデータベースからデータを取得し、CSVファイルにエクスポートするためのツールです。

## 機能

- データベース接続情報（ホスト、ポート、DB名、ユーザー名、パスワード）をコマンドライン引数で指定
- テーブル名またはカスタムSQL文を指定してデータを抽出
- 出力CSVファイルのパスを指定
- CSVフォーマットのカスタマイズ（区切り文字、引用文字、エンコーディングなど）
- エラー処理の実装
- 実行中の進捗状況の表示
- バッチ処理によるメモリ効率の向上

## 必要条件

- Python 3.6以上
- psycopg2-binary パッケージ

## インストール

```bash
pip install psycopg2-binary
```

## 使用方法

```bash
python pg_to_csv.py --host <ホスト名> --port <ポート番号> --dbname <データベース名> \
                    --user <ユーザー名> [--password <パスワード>] \
                    (--table <テーブル名> | --sql <SQL文>) \
                    --output <出力ファイル名> \
                    [--delimiter <区切り文字>] [--quotechar <引用文字>] \
                    [--encoding <エンコーディング>] [--no-header] [--batch-size <バッチサイズ>]
```

## 引数の説明

### 必須引数

- `--dbname`: データベース名
- `--user`: データベースユーザー名
- `--output`: 出力CSVファイルのパス
- `--table` または `--sql`: エクスポートするテーブル名またはSQL文（どちらか一方を指定）

### オプション引数

- `--host`: データベースホスト名（デフォルト: localhost）
- `--port`: データベースポート番号（デフォルト: 5432）
- `--password`: データベースパスワード（指定しない場合、環境変数やPgPassファイルから取得）
- `--delimiter`: CSV区切り文字（デフォルト: ,）
- `--quotechar`: CSV引用文字（デフォルト: "）
- `--encoding`: 出力ファイルのエンコーディング（デフォルト: utf-8）
- `--no-header`: ヘッダー行を含めない（デフォルト: ヘッダー行を含める）
- `--batch-size`: 一度に処理する行数（デフォルト: 10000）

## 使用例

### テーブル全体をエクスポート

```bash
python pg_to_csv.py --host localhost --port 5432 --dbname mydb --user myuser --password mypass \
                    --table customers --output customers.csv
```

### カスタムSQLクエリの結果をエクスポート

```bash
python pg_to_csv.py --host localhost --port 5432 --dbname mydb --user myuser --password mypass \
                    --sql "SELECT id, name, email FROM customers WHERE active = true" \
                    --output active_customers.csv
```

### CSVフォーマットのカスタマイズ

```bash
python pg_to_csv.py --host localhost --dbname mydb --user myuser \
                    --table products \
                    --output products.csv \
                    --delimiter ";" --quotechar "'" --encoding "shift-jis"
```

## エラー処理

スクリプトは以下のようなエラーを適切に処理します：

- データベース接続エラー
- SQLクエリエラー
- ファイル入出力エラー
- その他の予期しないエラー

エラーが発生した場合、スクリプトは適切なエラーメッセージを表示して終了します。

## 進捗状況の表示

スクリプトは実行中に以下の情報を表示します：

- データベース接続の状態
- エクスポートする行数（可能な場合）
- 処理の進捗状況（パーセンテージ）
- 経過時間
- 完了時の統計情報（エクスポートした行数、所要時間）
