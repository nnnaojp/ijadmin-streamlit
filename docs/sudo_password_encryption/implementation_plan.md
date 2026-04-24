# sudoパスワードの暗号化の提案と計画

## 背景と目的
現在 `config.toml` に `sudo_password=...` と平文で保存されている sudo 用のパスワードを暗号化する。
ユーザーが Linux の標準コマンドで作れるようにし、かつシステム内で安全に復号して利用する仕組みを構築する。

## 実装案の比較

### 案1: openssl を使用した AES 暗号化 (推奨)
Linux 標準の `openssl` コマンドを使用し、共通鍵（パスフレーズ）を指定して AES-256 で暗号化・復号を行う。

*   **作成コマンド**:
    ```bash
    echo -n '実際のsudoパスワード' | openssl enc -aes-256-cbc -pbkdf2 -a -salt -pass pass:'my_secret_key'
    ```
*   **アプリ側 (復号)**: `subprocess` を用いて、同じ共通鍵で `openssl enc -d` を呼び出して復号する。

### 案2: /etc/machine-id を復号鍵にする方式 (案1の強化版・最も推奨)
案1の共通鍵をソースコードに直書きするのを避け、マシンのユニークID (`/etc/machine-id`) を共通鍵として使用する。環境ごとに一意の鍵となるため安全性が非常に高い。

*   **作成コマンド**:
    ```bash
    SECRET_KEY=$(cat /etc/machine-id)
    echo -n '実際のsudoパスワード' | openssl enc -aes-256-cbc -pbkdf2 -a -salt -pass pass:"$SECRET_KEY"
    ```
*   **アプリ側 (復号)**: Python で `/etc/machine-id` を読み込み、その値を鍵として案1と同様に復号する。

### 案3: Base64 による難読化 (簡易版)
セキュリティレベルは低いが、「平文をとりあえず回避したい」場合の手軽な方式（誰でも復号可能）。

*   **作成コマンド**:
    ```bash
    echo -n '実際のsudoパスワード' | base64
    ```
*   **アプリ側 (デコード)**: Python の `base64.b64decode()` を用いる。
