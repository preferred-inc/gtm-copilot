"""Preset GTM template definitions."""

PRESET_TEMPLATES = [
    {
        "id": "ga4-basic",
        "name": "GA4 基本設定",
        "description": "Google Analytics 4 の基本的なページビュー計測とイベント計測を設定します。すべてのサイトに推奨。",
        "category": "analytics",
        "site_types": ["ec", "saas", "media", "lp", "corporate"],
        "config": {
            "tags": [
                {
                    "name": "GA4 - 設定タグ",
                    "type": "gaawc",
                    "tagId": "GA4_CONFIG",
                    "parameter": [
                        {"type": "TEMPLATE", "key": "measurementId", "value": "G-XXXXXXXXXX"},
                        {"type": "BOOLEAN", "key": "sendPageView", "value": "true"},
                    ],
                    "firingTriggerId": ["__ALL_PAGES"],
                },
                {
                    "name": "GA4 - 外部リンククリック",
                    "type": "gaawe",
                    "parameter": [
                        {"type": "TEMPLATE", "key": "eventName", "value": "click"},
                        {"type": "TAG_REFERENCE", "key": "measurementId", "value": "GA4 - 設定タグ"},
                    ],
                    "firingTriggerId": ["OUTBOUND_CLICK_TRIGGER"],
                },
            ],
            "triggers": [
                {
                    "name": "外部リンククリック",
                    "type": "LINK_CLICK",
                    "triggerId": "OUTBOUND_CLICK_TRIGGER",
                    "filter": [
                        {
                            "type": "MATCH_REGEX",
                            "parameter": [
                                {"type": "TEMPLATE", "key": "arg0", "value": "{{Click URL}}"},
                                {"type": "TEMPLATE", "key": "arg1", "value": "^https?://(?!{{Page Hostname}})"},
                            ],
                        }
                    ],
                    "autoEventFilter": [
                        {
                            "type": "MATCH_REGEX",
                            "parameter": [
                                {"type": "TEMPLATE", "key": "arg0", "value": "{{Click URL}}"},
                                {"type": "TEMPLATE", "key": "arg1", "value": "^https?://(?!{{Page Hostname}})"},
                            ],
                        }
                    ],
                    "waitForTags": {"type": "BOOLEAN", "value": "true"},
                    "checkValidation": {"type": "BOOLEAN", "value": "true"},
                    "waitForTagsTimeout": {"type": "TEMPLATE", "value": "2000"},
                },
            ],
            "variables": [
                {
                    "name": "GA4 測定ID",
                    "type": "c",
                    "parameter": [
                        {"type": "TEMPLATE", "key": "value", "value": "G-XXXXXXXXXX"},
                    ],
                },
            ],
            "built_in_variables": [],
        },
        "explanations": [
            {"name": "GA4 - 設定タグ", "type": "tag", "reason": "GA4のデータストリームに接続する基本設定タグ", "priority": "required"},
            {"name": "GA4 - 外部リンククリック", "type": "tag", "reason": "外部サイトへの遷移を計測", "priority": "recommended"},
            {"name": "外部リンククリック", "type": "trigger", "reason": "外部リンクのクリックを検知するトリガー", "priority": "recommended"},
        ],
    },
    {
        "id": "scroll-tracking",
        "name": "スクロール深度計測",
        "description": "ページのスクロール深度（25%, 50%, 75%, 90%）をGA4イベントとして計測します。",
        "category": "engagement",
        "site_types": ["media", "lp", "corporate"],
        "config": {
            "tags": [
                {
                    "name": "GA4 - スクロール深度",
                    "type": "gaawe",
                    "parameter": [
                        {"type": "TEMPLATE", "key": "eventName", "value": "scroll_depth"},
                        {"type": "TAG_REFERENCE", "key": "measurementId", "value": "GA4 - 設定タグ"},
                        {
                            "type": "LIST",
                            "key": "eventParameters",
                            "list": [
                                {
                                    "type": "MAP",
                                    "map": [
                                        {"type": "TEMPLATE", "key": "name", "value": "scroll_threshold"},
                                        {"type": "TEMPLATE", "key": "value", "value": "{{Scroll Depth Threshold}}"},
                                    ],
                                },
                                {
                                    "type": "MAP",
                                    "map": [
                                        {"type": "TEMPLATE", "key": "name", "value": "scroll_direction"},
                                        {"type": "TEMPLATE", "key": "value", "value": "{{Scroll Direction}}"},
                                    ],
                                },
                            ],
                        },
                    ],
                    "firingTriggerId": ["SCROLL_DEPTH_TRIGGER"],
                },
            ],
            "triggers": [
                {
                    "name": "スクロール深度 - 25/50/75/90%",
                    "type": "SCROLL_DEPTH",
                    "triggerId": "SCROLL_DEPTH_TRIGGER",
                    "parameter": [
                        {"type": "BOOLEAN", "key": "verticalThresholdsOn", "value": "true"},
                        {"type": "TEMPLATE", "key": "verticalThresholdUnits", "value": "PERCENT"},
                        {"type": "TEMPLATE", "key": "verticalThresholdPercent", "value": "25,50,75,90"},
                    ],
                },
            ],
            "variables": [],
            "built_in_variables": [],
        },
        "explanations": [
            {"name": "GA4 - スクロール深度", "type": "tag", "reason": "スクロール到達率をGA4に送信", "priority": "recommended"},
            {"name": "スクロール深度 - 25/50/75/90%", "type": "trigger", "reason": "4段階のスクロール深度を検知", "priority": "recommended"},
        ],
    },
    {
        "id": "form-submission",
        "name": "フォーム送信計測",
        "description": "フォーム送信をGA4イベントとして計測します。お問い合わせフォームや申し込みフォームの計測に。",
        "category": "conversion",
        "site_types": ["saas", "lp", "corporate"],
        "config": {
            "tags": [
                {
                    "name": "GA4 - フォーム送信",
                    "type": "gaawe",
                    "parameter": [
                        {"type": "TEMPLATE", "key": "eventName", "value": "form_submit"},
                        {"type": "TAG_REFERENCE", "key": "measurementId", "value": "GA4 - 設定タグ"},
                        {
                            "type": "LIST",
                            "key": "eventParameters",
                            "list": [
                                {
                                    "type": "MAP",
                                    "map": [
                                        {"type": "TEMPLATE", "key": "name", "value": "form_id"},
                                        {"type": "TEMPLATE", "key": "value", "value": "{{Form ID}}"},
                                    ],
                                },
                                {
                                    "type": "MAP",
                                    "map": [
                                        {"type": "TEMPLATE", "key": "name", "value": "form_url"},
                                        {"type": "TEMPLATE", "key": "value", "value": "{{Form URL}}"},
                                    ],
                                },
                            ],
                        },
                    ],
                    "firingTriggerId": ["FORM_SUBMIT_TRIGGER"],
                },
            ],
            "triggers": [
                {
                    "name": "フォーム送信",
                    "type": "FORM_SUBMISSION",
                    "triggerId": "FORM_SUBMIT_TRIGGER",
                    "waitForTags": {"type": "BOOLEAN", "value": "true"},
                    "checkValidation": {"type": "BOOLEAN", "value": "true"},
                    "waitForTagsTimeout": {"type": "TEMPLATE", "value": "2000"},
                },
            ],
            "variables": [],
            "built_in_variables": [],
        },
        "explanations": [
            {"name": "GA4 - フォーム送信", "type": "tag", "reason": "フォーム送信完了をGA4に記録", "priority": "required"},
            {"name": "フォーム送信", "type": "trigger", "reason": "HTMLフォームの送信を検知", "priority": "required"},
        ],
    },
    {
        "id": "google-ads-conversion",
        "name": "Google 広告コンバージョン計測",
        "description": "Google 広告のコンバージョントラッキングを設定します。リード獲得や購入完了の計測に。",
        "category": "advertising",
        "site_types": ["ec", "saas", "lp"],
        "config": {
            "tags": [
                {
                    "name": "Google Ads - コンバージョンリンカー",
                    "type": "gclidw",
                    "firingTriggerId": ["__ALL_PAGES"],
                },
                {
                    "name": "Google Ads - コンバージョン",
                    "type": "awct",
                    "parameter": [
                        {"type": "TEMPLATE", "key": "conversionId", "value": "AW-XXXXXXXXX"},
                        {"type": "TEMPLATE", "key": "conversionLabel", "value": "XXXXXXXXXX"},
                    ],
                    "firingTriggerId": ["CONVERSION_TRIGGER"],
                },
            ],
            "triggers": [
                {
                    "name": "コンバージョンページ",
                    "type": "PAGEVIEW",
                    "triggerId": "CONVERSION_TRIGGER",
                    "filter": [
                        {
                            "type": "CONTAINS",
                            "parameter": [
                                {"type": "TEMPLATE", "key": "arg0", "value": "{{Page URL}}"},
                                {"type": "TEMPLATE", "key": "arg1", "value": "/thank-you"},
                            ],
                        }
                    ],
                },
            ],
            "variables": [],
            "built_in_variables": [],
        },
        "explanations": [
            {"name": "Google Ads - コンバージョンリンカー", "type": "tag", "reason": "広告クリックとコンバージョンを紐づけるために必須", "priority": "required"},
            {"name": "Google Ads - コンバージョン", "type": "tag", "reason": "コンバージョンアクションを記録", "priority": "required"},
            {"name": "コンバージョンページ", "type": "trigger", "reason": "サンクスページの表示で発火", "priority": "required"},
        ],
    },
    {
        "id": "ecommerce-basic",
        "name": "EC サイト基本計測",
        "description": "ECサイト向けのGA4 eコマースイベント計測（商品表示、カート追加、購入完了）を設定します。",
        "category": "ecommerce",
        "site_types": ["ec"],
        "config": {
            "tags": [
                {
                    "name": "GA4 - 商品表示 (view_item)",
                    "type": "gaawe",
                    "parameter": [
                        {"type": "TEMPLATE", "key": "eventName", "value": "view_item"},
                        {"type": "TAG_REFERENCE", "key": "measurementId", "value": "GA4 - 設定タグ"},
                        {
                            "type": "LIST",
                            "key": "eventParameters",
                            "list": [
                                {
                                    "type": "MAP",
                                    "map": [
                                        {"type": "TEMPLATE", "key": "name", "value": "items"},
                                        {"type": "TEMPLATE", "key": "value", "value": "{{DLV - ecommerce.items}}"},
                                    ],
                                },
                            ],
                        },
                    ],
                    "firingTriggerId": ["VIEW_ITEM_TRIGGER"],
                },
                {
                    "name": "GA4 - カート追加 (add_to_cart)",
                    "type": "gaawe",
                    "parameter": [
                        {"type": "TEMPLATE", "key": "eventName", "value": "add_to_cart"},
                        {"type": "TAG_REFERENCE", "key": "measurementId", "value": "GA4 - 設定タグ"},
                        {
                            "type": "LIST",
                            "key": "eventParameters",
                            "list": [
                                {
                                    "type": "MAP",
                                    "map": [
                                        {"type": "TEMPLATE", "key": "name", "value": "items"},
                                        {"type": "TEMPLATE", "key": "value", "value": "{{DLV - ecommerce.items}}"},
                                    ],
                                },
                            ],
                        },
                    ],
                    "firingTriggerId": ["ADD_TO_CART_TRIGGER"],
                },
                {
                    "name": "GA4 - 購入完了 (purchase)",
                    "type": "gaawe",
                    "parameter": [
                        {"type": "TEMPLATE", "key": "eventName", "value": "purchase"},
                        {"type": "TAG_REFERENCE", "key": "measurementId", "value": "GA4 - 設定タグ"},
                        {
                            "type": "LIST",
                            "key": "eventParameters",
                            "list": [
                                {
                                    "type": "MAP",
                                    "map": [
                                        {"type": "TEMPLATE", "key": "name", "value": "transaction_id"},
                                        {"type": "TEMPLATE", "key": "value", "value": "{{DLV - ecommerce.transaction_id}}"},
                                    ],
                                },
                                {
                                    "type": "MAP",
                                    "map": [
                                        {"type": "TEMPLATE", "key": "name", "value": "value"},
                                        {"type": "TEMPLATE", "key": "value", "value": "{{DLV - ecommerce.value}}"},
                                    ],
                                },
                                {
                                    "type": "MAP",
                                    "map": [
                                        {"type": "TEMPLATE", "key": "name", "value": "items"},
                                        {"type": "TEMPLATE", "key": "value", "value": "{{DLV - ecommerce.items}}"},
                                    ],
                                },
                            ],
                        },
                    ],
                    "firingTriggerId": ["PURCHASE_TRIGGER"],
                },
            ],
            "triggers": [
                {
                    "name": "view_item イベント",
                    "type": "CUSTOM_EVENT",
                    "triggerId": "VIEW_ITEM_TRIGGER",
                    "customEventFilter": [
                        {
                            "type": "EQUALS",
                            "parameter": [
                                {"type": "TEMPLATE", "key": "arg0", "value": "{{_event}}"},
                                {"type": "TEMPLATE", "key": "arg1", "value": "view_item"},
                            ],
                        }
                    ],
                },
                {
                    "name": "add_to_cart イベント",
                    "type": "CUSTOM_EVENT",
                    "triggerId": "ADD_TO_CART_TRIGGER",
                    "customEventFilter": [
                        {
                            "type": "EQUALS",
                            "parameter": [
                                {"type": "TEMPLATE", "key": "arg0", "value": "{{_event}}"},
                                {"type": "TEMPLATE", "key": "arg1", "value": "add_to_cart"},
                            ],
                        }
                    ],
                },
                {
                    "name": "purchase イベント",
                    "type": "CUSTOM_EVENT",
                    "triggerId": "PURCHASE_TRIGGER",
                    "customEventFilter": [
                        {
                            "type": "EQUALS",
                            "parameter": [
                                {"type": "TEMPLATE", "key": "arg0", "value": "{{_event}}"},
                                {"type": "TEMPLATE", "key": "arg1", "value": "purchase"},
                            ],
                        }
                    ],
                },
            ],
            "variables": [
                {
                    "name": "DLV - ecommerce.items",
                    "type": "v",
                    "parameter": [
                        {"type": "INTEGER", "key": "dataLayerVersion", "value": "2"},
                        {"type": "TEMPLATE", "key": "name", "value": "ecommerce.items"},
                    ],
                },
                {
                    "name": "DLV - ecommerce.transaction_id",
                    "type": "v",
                    "parameter": [
                        {"type": "INTEGER", "key": "dataLayerVersion", "value": "2"},
                        {"type": "TEMPLATE", "key": "name", "value": "ecommerce.transaction_id"},
                    ],
                },
                {
                    "name": "DLV - ecommerce.value",
                    "type": "v",
                    "parameter": [
                        {"type": "INTEGER", "key": "dataLayerVersion", "value": "2"},
                        {"type": "TEMPLATE", "key": "name", "value": "ecommerce.value"},
                    ],
                },
            ],
            "built_in_variables": [],
        },
        "explanations": [
            {"name": "GA4 - 商品表示 (view_item)", "type": "tag", "reason": "商品詳細ページの閲覧を計測", "priority": "required"},
            {"name": "GA4 - カート追加 (add_to_cart)", "type": "tag", "reason": "カートへの商品追加を計測", "priority": "required"},
            {"name": "GA4 - 購入完了 (purchase)", "type": "tag", "reason": "購入完了を計測（売上データ含む）", "priority": "required"},
            {"name": "DLV - ecommerce.items", "type": "variable", "reason": "dataLayerから商品情報を取得", "priority": "required"},
        ],
    },
    {
        "id": "cta-click-tracking",
        "name": "CTA クリック計測",
        "description": "CTAボタンのクリックをGA4イベントとして計測します。LPやサービスサイトに最適。",
        "category": "engagement",
        "site_types": ["lp", "saas", "corporate"],
        "config": {
            "tags": [
                {
                    "name": "GA4 - CTAクリック",
                    "type": "gaawe",
                    "parameter": [
                        {"type": "TEMPLATE", "key": "eventName", "value": "cta_click"},
                        {"type": "TAG_REFERENCE", "key": "measurementId", "value": "GA4 - 設定タグ"},
                        {
                            "type": "LIST",
                            "key": "eventParameters",
                            "list": [
                                {
                                    "type": "MAP",
                                    "map": [
                                        {"type": "TEMPLATE", "key": "name", "value": "click_text"},
                                        {"type": "TEMPLATE", "key": "value", "value": "{{Click Text}}"},
                                    ],
                                },
                                {
                                    "type": "MAP",
                                    "map": [
                                        {"type": "TEMPLATE", "key": "name", "value": "click_url"},
                                        {"type": "TEMPLATE", "key": "value", "value": "{{Click URL}}"},
                                    ],
                                },
                                {
                                    "type": "MAP",
                                    "map": [
                                        {"type": "TEMPLATE", "key": "name", "value": "click_classes"},
                                        {"type": "TEMPLATE", "key": "value", "value": "{{Click Classes}}"},
                                    ],
                                },
                            ],
                        },
                    ],
                    "firingTriggerId": ["CTA_CLICK_TRIGGER"],
                },
            ],
            "triggers": [
                {
                    "name": "CTAボタンクリック",
                    "type": "LINK_CLICK",
                    "triggerId": "CTA_CLICK_TRIGGER",
                    "filter": [
                        {
                            "type": "MATCH_REGEX",
                            "parameter": [
                                {"type": "TEMPLATE", "key": "arg0", "value": "{{Click Classes}}"},
                                {"type": "TEMPLATE", "key": "arg1", "value": "(btn|button|cta|submit)"},
                            ],
                        }
                    ],
                    "autoEventFilter": [
                        {
                            "type": "MATCH_REGEX",
                            "parameter": [
                                {"type": "TEMPLATE", "key": "arg0", "value": "{{Click Classes}}"},
                                {"type": "TEMPLATE", "key": "arg1", "value": "(btn|button|cta|submit)"},
                            ],
                        }
                    ],
                },
            ],
            "variables": [],
            "built_in_variables": [],
        },
        "explanations": [
            {"name": "GA4 - CTAクリック", "type": "tag", "reason": "CTAボタンのクリックをイベントとして送信", "priority": "recommended"},
            {"name": "CTAボタンクリック", "type": "trigger", "reason": "CTA系クラスを持つリンクのクリックを検知", "priority": "recommended"},
        ],
    },
]
