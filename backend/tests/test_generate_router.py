from unittest.mock import AsyncMock, patch
from app.schemas.analysis import SiteAnalysis
from app.schemas.sync import ImportData
from app.schemas.generate import GenerateResult, TagExplanation


def _mock_analysis():
    return SiteAnalysis(
        url="https://example.com",
        title="Example",
        description="Test site",
        site_type="corporate",
        existing_tags=[],
        forms=[],
        cta_elements=[],
        technology=[],
        pages_analyzed=[],
    )


def _mock_result():
    return GenerateResult(
        config=ImportData(
            tags=[{"name": "GA4 Config", "type": "gaawc"}],
            triggers=[{"name": "All Pages", "type": "pageview"}],
            variables=[],
        ),
        explanations=[
            TagExplanation(name="GA4 Config", type="tag", reason="Basic tracking", priority="required"),
        ],
    )


class TestGenerateEndpoint:
    @patch("app.routers.generate.generate_gtm_config", new_callable=AsyncMock)
    @patch("app.routers.generate.crawl_site", new_callable=AsyncMock)
    def test_generate_success(self, mock_crawl, mock_generate, unauth_client):
        mock_crawl.return_value = _mock_analysis()
        mock_generate.return_value = _mock_result()

        resp = unauth_client.post("/api/generate", json={"url": "https://example.com"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["analysis"]["site_type"] == "corporate"
        assert len(data["config"]["tags"]) == 1
        assert len(data["explanations"]) == 1

    def test_generate_invalid_url(self, unauth_client):
        resp = unauth_client.post("/api/generate", json={"url": "not-a-url"})
        assert resp.status_code == 400

    def test_generate_ftp_url(self, unauth_client):
        resp = unauth_client.post("/api/generate", json={"url": "ftp://example.com"})
        assert resp.status_code == 400

    @patch("app.routers.generate.crawl_site", new_callable=AsyncMock)
    def test_generate_crawl_failure(self, mock_crawl, unauth_client):
        mock_crawl.side_effect = Exception("Timeout")
        resp = unauth_client.post("/api/generate", json={"url": "https://example.com"})
        assert resp.status_code == 422

    @patch("app.routers.generate.generate_gtm_config", new_callable=AsyncMock)
    @patch("app.routers.generate.crawl_site", new_callable=AsyncMock)
    def test_generate_llm_failure(self, mock_crawl, mock_generate, unauth_client):
        mock_crawl.return_value = _mock_analysis()
        mock_generate.side_effect = ValueError("LLM failed")
        resp = unauth_client.post("/api/generate", json={"url": "https://example.com"})
        assert resp.status_code == 500
