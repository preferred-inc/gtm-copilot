SYSTEM_PROMPT = """あなたはGoogle Tag Manager（GTM）設定の専門家です。
サイト分析結果を元に、最適なGTM設定（tags, triggers, variables）を生成してください。

## ルール
1. 出力はGTM API互換のJSON形式であること
2. 既存タグとの重複を避けること
3. 各要素に `name` と適切な `type` を必ず含めること
4. Custom HTML タグで任意のスクリプトを挿入するのは禁止
5. trigger の firingTriggerId 参照は、同時に生成する trigger の名前を使うこと

## タグの type 値の対応表
- GA4設定タグ: "gaawc"
- GA4イベントタグ: "gaawe"
- Google Adsコンバージョン: "awct"
- Google Adsリマーケティング: "sp"
- Meta Pixel: "html" (Custom HTML として実装)は禁止。代わりにカスタムテンプレートを使用

## トリガーの type 値
- ページビュー: "pageview"
- DOM Ready: "domReady"
- Window Loaded: "windowLoaded"
- クリック（全要素）: "click"
- クリック（リンクのみ）: "linkClick"
- フォーム送信: "formSubmission"
- スクロール深度: "scrollDepth"
- カスタムイベント: "customEvent"
- 履歴の変更: "historyChange"
- タイマー: "timer"

## 変数の type 値
- URL: "u"
- ページパス: "u" (component: "PATH")
- クリック要素: "ae"
- クリッククラス: "ec"
- クリックID: "eid"
- クリックテキスト: "et"
- クリックURL: "eu"
- フォームID: "fid"
- データレイヤー変数: "v"
- 定数: "c"
- カスタムJavaScript: "jsm"

## 出力JSON形式

```json
{
  "config": {
    "tags": [
      {
        "name": "GA4 Configuration",
        "type": "gaawc",
        "parameter": [
          { "type": "TEMPLATE", "key": "measurementId", "value": "G-XXXXXXXX" }
        ],
        "firingTriggerId": ["trigger_name_here"]
      }
    ],
    "triggers": [
      {
        "name": "All Pages",
        "type": "pageview"
      }
    ],
    "variables": [
      {
        "name": "Page Path",
        "type": "u",
        "parameter": [
          { "type": "TEMPLATE", "key": "component", "value": "PATH" }
        ]
      }
    ],
    "built_in_variables": []
  },
  "explanations": [
    {
      "name": "GA4 Configuration",
      "type": "tag",
      "reason": "基本的なGA4計測に必須の設定タグです",
      "priority": "required"
    }
  ]
}
```
"""

USER_PROMPT_TEMPLATE = """以下のサイト分析結果を元に、最適なGTM設定を生成してください。

## サイト分析結果
{site_analysis}

## 既存GTM設定（重複回避用）
{existing_config}

## サイト種別に応じた生成ガイドライン

### 必須（どのサイトでも）
- GA4設定タグ（measurement_idが分析から取得できた場合はそれを使用、なければプレースホルダ "G-XXXXXXXX"）
- All Pages トリガー（pageview）
- 基本変数（Page URL, Page Path）

### サイト種別: {site_type}
{site_type_guidelines}

### 検出ベースの追加設定
{detection_guidelines}

JSON形式で出力してください。`config` と `explanations` を含むオブジェクトを返してください。
"""

SITE_TYPE_GUIDELINES = {
    "ec": """- purchase イベントタグ（購入完了の計測）— priority: required
- add_to_cart イベントタグ（カート追加の計測）— priority: required
- view_item イベントタグ（商品閲覧の計測）— priority: recommended
- begin_checkout イベントタグ（決済開始の計測）— priority: recommended
- view_cart イベントタグ（カート閲覧の計測）— priority: optional
- 各ECイベントに対応するカスタムイベントトリガー
- データレイヤー変数（ecommerce関連）""",

    "saas": """- sign_up イベントタグ（ユーザー登録の計測）— priority: required
- login イベントタグ（ログインの計測）— priority: recommended
- フォーム送信トリガー（登録フォーム検出時）
- CTA クリックトリガー — priority: recommended
- scroll_depth トリガー — priority: optional""",

    "lp": """- form_submit イベントタグ（フォーム送信の計測）— priority: required
- scroll_depth トリガー（25%, 50%, 75%, 100%）— priority: required
- CTA click イベントタグ（CTAクリックの計測）— priority: recommended
- フォーム送信トリガー
- スクロール深度トリガー""",

    "media": """- scroll_depth トリガー（25%, 50%, 75%, 100%）— priority: required
- article_view イベントタグ（記事閲覧の計測）— priority: recommended
- outbound_click イベントタグ（外部リンククリック）— priority: recommended
- スクロール深度トリガー
- リンククリックトリガー（外部リンク用）""",

    "corporate": """- form_submit イベントタグ（お問い合わせフォーム等）— priority: recommended
- scroll_depth トリガー — priority: optional
- CTA click イベントタグ — priority: optional
- フォーム送信トリガー（フォーム検出時）""",
}


def get_detection_guidelines(analysis) -> str:
    lines = []
    # Existing GA4 tag
    ga4_ids = [t.identifier for t in analysis.existing_tags if t.type == "ga4"]
    if ga4_ids:
        lines.append(f"- GA4が既に検出されています（{', '.join(ga4_ids)}）。このmeasurement_idを使用してください。")
    else:
        lines.append("- GA4が検出されていません。プレースホルダ G-XXXXXXXX を使用してください。")

    # Meta Pixel
    meta_ids = [t.identifier for t in analysis.existing_tags if t.type == "meta_pixel"]
    if meta_ids:
        lines.append(f"- Meta Pixelが検出されています（{', '.join(meta_ids)}）。重複しないよう注意してください。")

    # Forms
    if analysis.forms:
        lines.append(f"- {len(analysis.forms)}個のフォームが検出されています。フォーム送信イベントを追加してください。")

    # Stripe
    if "Stripe" in analysis.technology:
        lines.append("- Stripeが検出されています。決済完了イベントの追加を検討してください。")

    # SPA frameworks
    spa_frameworks = [t for t in analysis.technology if t in ["Next.js", "Nuxt.js", "React", "Vue.js", "Angular"]]
    if spa_frameworks:
        lines.append(f"- SPAフレームワーク（{', '.join(spa_frameworks)}）が検出されています。履歴変更トリガーの追加を検討してください。")

    if not lines:
        lines.append("- 特別な検出項目はありません。")

    return "\n".join(lines)
