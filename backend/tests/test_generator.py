import pytest
from app.services.generator import validate_generated_config, _parse_response
from app.schemas.sync import ImportData


class TestValidateGeneratedConfig:
    def test_valid_config(self):
        data = ImportData(
            tags=[{"name": "GA4", "type": "gaawc"}],
            triggers=[{"name": "All Pages", "type": "pageview"}],
            variables=[{"name": "Page URL", "type": "u"}],
        )
        errors = validate_generated_config(data)
        assert errors == []

    def test_tag_missing_name(self):
        data = ImportData(tags=[{"type": "gaawc"}])
        errors = validate_generated_config(data)
        assert len(errors) == 1
        assert "missing 'name'" in errors[0]

    def test_tag_missing_type(self):
        data = ImportData(tags=[{"name": "My Tag"}])
        errors = validate_generated_config(data)
        assert len(errors) == 1
        assert "missing 'type'" in errors[0]

    def test_trigger_missing_name(self):
        data = ImportData(triggers=[{"type": "pageview"}])
        errors = validate_generated_config(data)
        assert any("Trigger" in e and "missing 'name'" in e for e in errors)

    def test_variable_missing_type(self):
        data = ImportData(variables=[{"name": "My Var"}])
        errors = validate_generated_config(data)
        assert any("Variable" in e and "missing 'type'" in e for e in errors)

    def test_custom_html_with_script_rejected(self):
        data = ImportData(tags=[{
            "name": "Bad Tag",
            "type": "html",
            "parameter": [{"key": "html", "value": "<script>alert('xss')</script>"}],
        }])
        errors = validate_generated_config(data)
        assert any("prohibited Custom HTML" in e for e in errors)

    def test_custom_html_without_script_allowed(self):
        data = ImportData(tags=[{
            "name": "Safe Tag",
            "type": "html",
            "parameter": [{"key": "html", "value": "<div>Hello</div>"}],
        }])
        errors = validate_generated_config(data)
        assert errors == []

    def test_empty_config(self):
        data = ImportData()
        errors = validate_generated_config(data)
        assert errors == []


class TestParseResponse:
    def test_plain_json(self):
        result = _parse_response('{"config": {}, "explanations": []}')
        assert result == {"config": {}, "explanations": []}

    def test_json_in_code_block(self):
        raw = '```json\n{"config": {}, "explanations": []}\n```'
        result = _parse_response(raw)
        assert result == {"config": {}, "explanations": []}

    def test_json_in_generic_code_block(self):
        raw = '```\n{"config": {}, "explanations": []}\n```'
        result = _parse_response(raw)
        assert result == {"config": {}, "explanations": []}

    def test_invalid_json_raises(self):
        with pytest.raises(Exception):
            _parse_response("not json at all")
