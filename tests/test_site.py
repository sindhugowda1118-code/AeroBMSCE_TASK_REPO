import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

from server.app import INTERESTS, YEARS


ROOT = Path(__file__).resolve().parent.parent


class SiteParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []
        self.ids = set()
        self.fields = set()
        self.select_options = {}
        self.current_select = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        for attribute in ("href", "src"):
            value = attrs.get(attribute)
            if value:
                self.references.append(value)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag in {"input", "select", "textarea"} and attrs.get("name"):
            self.fields.add(attrs["name"])
        if tag == "select":
            self.current_select = attrs.get("name")
            if self.current_select:
                self.select_options[self.current_select] = set()
        if tag == "option" and self.current_select:
            self.select_options[self.current_select].add(attrs.get("value", ""))

    def handle_endtag(self, tag):
        if tag == "select":
            self.current_select = None


class StaticSiteTests(unittest.TestCase):
    def test_all_local_page_and_asset_references_resolve(self):
        for page in sorted(ROOT.glob("*.html")):
            parser = SiteParser()
            parser.feed(page.read_text(encoding="utf-8"))
            for reference in parser.references:
                parsed = urlsplit(reference)
                if parsed.scheme or parsed.netloc:
                    continue
                if not parsed.path:
                    if parsed.fragment:
                        self.assertIn(parsed.fragment, parser.ids, f"{page.name}: missing #{parsed.fragment}")
                    continue
                if parsed.path.lstrip("/") == "api/interest":
                    continue
                target = (ROOT / unquote(parsed.path)).resolve()
                self.assertTrue(target.is_relative_to(ROOT), f"{page.name}: {reference} escapes the site")
                self.assertTrue(target.is_file(), f"{page.name}: missing {reference}")
                if parsed.fragment and target.suffix == ".html":
                    target_parser = SiteParser()
                    target_parser.feed(target.read_text(encoding="utf-8"))
                    self.assertIn(parsed.fragment, target_parser.ids, f"{page.name}: missing #{parsed.fragment}")

        stylesheet = (ROOT / "style.css").read_text(encoding="utf-8")
        for asset in re.findall(r"""url\(["']?([^"')]+)""", stylesheet):
            if asset.startswith(("data:", "http:", "https:")):
                continue
            self.assertTrue((ROOT / asset).is_file(), f"style.css: missing {asset}")

    def test_join_form_matches_registration_api(self):
        parser = SiteParser()
        parser.feed((ROOT / "join.html").read_text(encoding="utf-8"))
        self.assertEqual(
            parser.fields,
            {"fullName", "email", "department", "studyYear", "interest", "consent"},
        )
        self.assertEqual(parser.select_options["studyYear"] - {""}, YEARS)
        self.assertEqual(parser.select_options["interest"] - {""}, INTERESTS)


if __name__ == "__main__":
    unittest.main()
