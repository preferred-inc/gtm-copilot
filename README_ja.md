# GTM Copilot

このプロジェクトでは、AIを活用してGoogleタグマネージャー（GTM）の実装作業を自動化するためのプログラムやプロンプトを構築しています。

## 主な仕組み

1. **抽出**: GoogleタグマネージャーAPIを使用して、既存のタグ、トリガー、変数などのコンポーネントを取得し、JSON形式で保存します。
2. **AIによる修正**: AIを使用してJSONファイルを更新し、実際のタグ実装ロジックをファイル上で行います。
3. **同期**: 実装（JSONの編集）が完了したら、APIを使用して変更をGoogleタグマネージャーに同期させます。

## アーキテクチャ

ポータビリティとセットアップの容易さを確保するため、このプロジェクトは**Python標準ライブラリのみ**を使用して実装されています。外部依存ライブラリ（`requests`や`google-auth`など）は不要です。

- **プログラミング言語**: Python 3.x（標準ライブラリのみ）

## AI自動生成機能

URLを入力するだけで、サイトを分析し最適なGTM設定を自動生成します。

### フロー
```
URL入力 → サイト分析（Playwright） → AI生成（Claude） → プレビュー → GTMに適用
```

### 対応サイト種別
- **EC**: purchase, add_to_cart, view_item 等のECイベント
- **SaaS**: sign_up, login, CTA click 等
- **LP**: form_submit, scroll_depth, CTA click
- **メディア**: scroll_depth, article_view, outbound_click
- **コーポレート**: form_submit, 基本計測

### 起動方法
```bash
# 環境変数の設定
# src/.env に ANTHROPIC_API_KEY を追加

# Docker
docker compose up --build

# ブラウザで http://localhost:3000/generate を開く
```

---

## Agent Skills のセットアップ

Agent Skills の全般的な情報については [agentskills.io](https://agentskills.io/home) を参照してください。

GTM Copilot のスキルを使用するには、以下の手順を実行してください：

1. **ダウンロード**: [Releases](https://github.com/sem-technology/gtm-copilot/releases) ページからビルド済みの `gtm-copilot_vX.X.X.zip` を取得します。
2. **配置**: Zip ファイルを解凍し、中身を AI エージェントのスキルディレクトリ（例: `.agent/skills/gtm-copilot/`）に配置します。
3. **認証**: スキルディレクトリ内の `.env.example` をコピーして `.env` を作成し、認証情報を更新します。
3. **利用**: 配置が完了すると、AI エージェントは `SKILL.md` に定義されたツールを自動的に認識し、GTM の自動化作業を開始できるようになります。
