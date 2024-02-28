# SkAsyncGeneratorSample

# 概要
Semantic Kernel v0.5.0 でAsync Generator を使いたいサンプルコード
asyncio.Queue 周りの管理が面倒

# 使い方
サーバー立ち上げ
```shell
make dev
```

クライアントから呼び出し
```shell
curl -N http://localhost:8000
```

## 開発者向け

### フォーマット、リント
```shell
make fmt
make lint
```

### テスト
```shell
make test
```
