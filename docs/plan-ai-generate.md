# AI GTM設定生成プラン

## ゴール

URLを貼るだけで、GTM設定（tags / triggers / variables）をAIが生成し、プレビュー → ワンクリックでGTMにimportまで完結するSaaSにする。

## 現状のシステム

```
URL入力 → workspace接続 → 手動export/import
```

- OAuth認証済み（Google OAuth フロー実装済み）
- GTM APIへの読み書きは `GTMClient` で完結
- import機能は `ImportService` で依存解決込みで動作
- `ImportData` スキーマ: `{ tags[], triggers[], variables[], built_in_variables[] }`（各要素はGTM APIの生dictそのまま）

## ターゲットのフロー

```
[ユーザー]
  URL入力 → 「生成」ボタン
     ↓
[Backend: POST /api/generate]
  ├── Step 1: Crawler — URL → サイト情報を構造化
  ├── Step 2: LLM — サイト情報 → GTM設定JSON (ImportData形式)
  └── return ImportData + 説明
     ↓
[Frontend]
  生成結果プレビュー（何を入れるか・なぜ入れるかの説明付き）
  「GTMに適用」ボタン → POST /api/import/execute（既存）
```

---

## Phase 1: サイト分析（Crawler）

### 目的
URLからGTM設定生成に必要な情報を抽出する。

### 抽出する情報

| カテゴリ | 抽出内容 | 用途 |
|---------|---------|------|
| メタ情報 | title, description, OGP, canonical | サイト種別の推定 |
| 既存タグ | GA4 / Meta Pixel / GTM等の既存スクリプト | 重複回避、measurement_id取得 |
| ページ構造 | フォーム要素、CTA、ナビゲーション | トリガー/イベント設計 |
| Ecommerce | 商品ページ、カート、決済フローの検出 | EC系イベント設計 |
| テクノロジー | フレームワーク（Next.js, Shopify等） | SPA対応判断 |
| 外部サービス | Stripe, Intercom等のSDK検出 | 連携タグ設計 |

### 技術選択

- **Playwright** でヘッドレスブラウジング（JSレンダリング後のDOMが必要）
- トップページ + 主要ページ（最大5ページ）をクロール
- タイムアウト: 30秒/ページ

### 出力スキーマ

```python
@dataclass
class SiteAnalysis:
    url: str
    title: str
    description: str
    site_type: str                    # "ec", "saas", "media", "lp", "corporate"
    existing_tags: list[ExistingTag]  # 既に入っているタグ
    forms: list[FormInfo]             # フォーム要素
    cta_elements: list[CTAInfo]       # CTA（ボタン、リンク）
    ecommerce: EcommerceInfo | None   # EC情報（あれば）
    technology: list[str]             # 検出されたフレームワーク/サービス
    pages_analyzed: list[PageInfo]    # 分析した各ページの情報
```

### 実装ファイル

- `backend/app/services/crawler.py` — メインのクロール処理
- `backend/app/schemas/analysis.py` — SiteAnalysis等のスキーマ

---

## Phase 2: AI生成（LLM）

### 目的
サイト分析結果を元に、最適なGTM設定を生成する。

### プロンプト設計

```
あなたはGTM設定の専門家です。
以下のサイト分析結果を元に、最適なGTM設定を生成してください。

## サイト情報
{site_analysis}

## 制約
- 出力は厳密にGTM API互換のJSON形式
- 既存タグとの重複を避ける
- 各タグ/トリガー/変数に `_reason` フィールドで設定理由を付与

## 出力形式
{ImportData schema + examples}
```

### 生成対象の優先度

**必須（どのサイトでも）:**
- GA4 設定タグ（measurement_id）
- ページビュートリガー
- 基本変数（Page URL, Page Path, Click Element等）

**サイト種別で追加:**

| サイト種別 | 追加するタグ/イベント |
|-----------|---------------------|
| EC | purchase, add_to_cart, view_item, begin_checkout |
| SaaS | sign_up, login, feature_usage |
| LP | form_submit, scroll_depth, cta_click |
| メディア | scroll_depth, article_view, outbound_click |

**検出ベースで追加:**
- Meta Pixel → Meta Conversion API タグ
- フォーム検出 → form_submit イベント
- Stripe検出 → 決済完了イベント

### LLM選択

- **Claude API**（Sonnet）— コスト・精度バランスが良い
- JSON mode / structured output で出力の安定性を担保
- フォールバック: リトライ3回、スキーマバリデーション失敗時はエラー返却

### バリデーション

LLM出力をGTMにpushする前に必ずバリデーションする。

```python
def validate_generated_config(data: ImportData) -> list[str]:
    """
    - 各tagにnameとtypeがあるか
    - triggerの参照が存在するか
    - variableの参照が存在するか
    - 禁止パターン（Custom HTML with arbitrary script等）がないか
    """
```

### 実装ファイル

- `backend/app/services/generator.py` — LLM呼び出し + バリデーション
- `backend/app/services/templates/` — サイト種別ごとのベーステンプレート（プロンプト内のfew-shot例）

---

## Phase 3: API + Frontend

### Backend

#### `POST /api/generate`

```python
# backend/app/routers/generate.py

@router.post("/api/generate")
async def generate(req: GenerateRequest, client: GTMClient = Depends(get_gtm_client)):
    # 1. クロール
    analysis = await crawl_site(req.url)

    # 2. 既存GTM設定を取得（重複回避用）
    existing = None
    if req.workspace_path:
        existing = ExportService(client).export(req.workspace_path)

    # 3. AI生成
    result = await generate_gtm_config(analysis, existing)

    # 4. レスポンス
    return GenerateResponse(
        analysis=analysis,
        config=result.config,        # ImportData形式
        explanations=result.explanations,  # 各設定の説明
    )
```

#### スキーマ

```python
# backend/app/schemas/generate.py

class GenerateRequest(BaseModel):
    url: str
    workspace_path: str | None = None  # 既存workspace（重複回避用）

class TagExplanation(BaseModel):
    name: str
    type: str         # "tag" | "trigger" | "variable"
    reason: str       # なぜこの設定が必要か
    priority: str     # "required" | "recommended" | "optional"

class GenerateResponse(BaseModel):
    analysis: SiteAnalysis
    config: ImportData
    explanations: list[TagExplanation]
```

### Frontend

#### 新規ページ: `/generate`

```
┌─────────────────────────────────────────┐
│  GTM設定を自動生成                         │
│                                         │
│  URL: [https://example.com      ] [生成] │
│                                         │
│  ── 分析結果 ──                           │
│  サイト種別: EC (Shopify)                  │
│  既存タグ: GA4 (G-XXXXX), Meta Pixel      │
│  検出: 商品ページ, カート, 決済フォーム       │
│                                         │
│  ── 生成された設定 ──                      │
│  ✅ GA4 設定タグ          [必須]          │
│     → 基本的な計測に必要                    │
│  ✅ purchase イベント     [必須]          │
│     → EC売上計測に必須                     │
│  ☑️ add_to_cart イベント  [推奨]          │
│     → カート追加の計測                     │
│  ☐ scroll_depth          [任意]          │
│     → スクロール深度の計測                  │
│                                         │
│  [GTMに適用] [JSONダウンロード]             │
└─────────────────────────────────────────┘
```

- チェックボックスで適用する設定を選択可能
- 各設定に理由が表示される
- 「GTMに適用」で既存の `/api/import/execute` を呼ぶ

#### 実装ファイル

- `frontend/src/app/generate/page.tsx` — 生成ページ
- `frontend/src/components/generate/AnalysisResult.tsx` — 分析結果表示
- `frontend/src/components/generate/ConfigPreview.tsx` — 生成設定プレビュー（チェックボックス付き）

---

## Phase 4: SaaS化（後回しでOK）

Phase 1-3 が動けばコア機能は完成。SaaSにするには追加で以下が必要:

| 項目 | 内容 | 優先度 |
|------|------|--------|
| マルチテナント | ユーザーごとにセッション/履歴を分離 | 高 |
| 生成履歴 | DB（PostgreSQL）に生成結果を保存 | 高 |
| 課金 | Stripe連携、フリー/プロプラン | 中 |
| 非同期処理 | クロール+生成をバックグラウンドジョブに（Celery/ARQ） | 中 |
| ランディングページ | プロダクトサイト | 中 |
| レート制限 | API/生成回数の制限 | 中 |
| エラー監視 | Sentry連携 | 低 |

---

## 依存パッケージ（追加）

```
# backend/requirements.txt に追加
playwright>=1.40.0
anthropic>=0.40.0
```

## 実装順序

```
Phase 1 (Crawler)        ████░░░░░░  ← まずここ
Phase 2 (AI生成)          ░░████░░░░  ← 次にここ（Phase 1の出力を入力にする）
Phase 3 (API + Frontend)  ░░░░████░░  ← つなぎこみ
Phase 4 (SaaS化)          ░░░░░░░███  ← PMF確認後
```

### マイルストーン

1. **M1: Crawler動作確認** — URLを入れてSiteAnalysisが返る
2. **M2: AI生成動作確認** — SiteAnalysisからImportData JSONが生成される
3. **M3: E2E動作** — URL入力 → プレビュー → GTM適用が一気通貫で動く
4. **M4: SaaS MVP** — マルチテナント + 課金 + デプロイ
