"""Exercise privacy boundaries before a generated tree is replaced."""

import importlib.util
from hashlib import sha256
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/prepare_site.py"
SPEC = importlib.util.spec_from_file_location("prepare_site", SCRIPT)
PREPARE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(PREPARE)


class PublicationBoundary(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.site = self.root / "site"
        self.target = self.site / "src/content/docs"
        self.target.mkdir(parents=True)
        (self.target / "keep.md").write_text("previous output")
        (self.root / "faq").mkdir()
        self.article = self.root / "faq/one.md"
        self.article.write_text("# One\n\nPublic explanation.\n")
        self.page = {"source": "faq/one.md", "route": "", "group": "start"}
        self.manifest = {
            "pages": [self.page],
            "aliases": {"README.md": "", "docs/topic-map.md": "", "docs/history-audit.md": ""},
        }

    def run_prepare(self):
        (self.site / "content-manifest.json").write_text(json.dumps(self.manifest))
        with patch.multiple(PREPARE, ROOT=self.root, SITE=self.site, TARGET=self.target):
            PREPARE.main()

    def test_archive_pointer_does_not_require_or_read_archive(self):
        self.article.write_text("# One\n\n[42](../data/missing-export/messages.html#message42)\n")
        self.run_prepare()
        output = (self.target / "index.md").read_text()
        self.assertIn("сообщение 42", output)
        self.assertNotIn("data/", output)
        self.assertFalse((self.root / "data").exists())

    def test_private_source_is_rejected_and_old_output_preserved(self):
        self.page["source"] = "data/private.md"
        with self.assertRaises(AssertionError):
            self.run_prepare()
        self.assertEqual((self.target / "keep.md").read_text(), "previous output")

    def test_unlisted_link_fails_before_replacing_output(self):
        self.article.write_text("# One\n\n[Unlisted](../docs/private.md)\n")
        with self.assertRaisesRegex(AssertionError, "Unlisted link"):
            self.run_prepare()
        self.assertTrue((self.target / "keep.md").is_file())

    def test_symlink_cannot_expand_publication_scope(self):
        self.article.unlink()
        secret = self.root / "unlisted.md"
        secret.write_text("Must not enter output")
        self.article.symlink_to(secret)
        with self.assertRaises(AssertionError):
            self.run_prepare()
        self.assertTrue((self.target / "keep.md").is_file())

    def test_count_tracks_only_published_faq_articles(self):
        self.page["route"] = "faq/one"
        (self.site / "home.mdx").write_text("# Home\n\n{{ARTICLE_COUNT_LABEL}}\n")
        (self.site / "method.md").write_text("# Method\n\nAbout the sources.\n")
        self.manifest["pages"].extend([
            {"source": "site/home.mdx", "route": "", "group": "start"},
            {"source": "site/method.md", "route": "sources/method", "group": "sources"},
        ])
        (self.root / "faq/unlisted.md").write_text("# Unlisted\n")
        self.run_prepare()
        self.assertIn("1 статья", (self.target / "index.mdx").read_text())
        self.assertFalse((self.target / "faq/unlisted.md").exists())

        (self.root / "faq/two.md").write_text("# Two\n")
        self.manifest["pages"].append(
            {"source": "faq/two.md", "route": "faq/two", "group": "start"}
        )
        self.run_prepare()
        self.assertIn("2 статьи", (self.target / "index.mdx").read_text())

    def test_edit_link_points_to_canonical_article(self):
        self.run_prepare()
        self.assertIn(
            'editUrl: "https://github.com/demshin/elegoo-cc/edit/main/faq/one.md"',
            (self.target / "index.md").read_text(),
        )

    def test_unlisted_public_asset_preserves_previous_output(self):
        public = self.site / "public"
        public.mkdir()
        (public / "unlisted.html").write_text("Must not be published")
        with self.assertRaisesRegex(AssertionError, "Public assets"):
            self.run_prepare()
        self.assertTrue((self.target / "keep.md").is_file())

    def test_listed_public_asset_is_allowed(self):
        public = self.site / "public"
        public.mkdir()
        (public / "favicon.svg").write_text('<svg xmlns="http://www.w3.org/2000/svg"/>')
        self.manifest["assets"] = ["favicon.svg"]
        self.run_prepare()
        self.assertTrue((self.target / "index.md").is_file())

    def test_topic_lists_only_allowlisted_articles_with_scope(self):
        (self.site / "topics").mkdir()
        (self.site / "topics/printing.md").write_text("# Printing\n\n{{TOPIC_ARTICLES}}\n")
        self.article.write_text("# First layer\n\n**Область:** CC1; PLA. **Обновлено:** 02.11.2026.\n")
        (self.root / "faq/unlisted.md").write_text("# Must stay unlisted\n")
        self.page.update(route="faq/one", group="printing")
        self.manifest["groups"] = [{"id": "printing", "label": "Printing", "route": ""}]
        self.manifest["pages"].append({"source": "site/topics/printing.md", "route": "", "group": "topics", "topic": "printing"})
        self.run_prepare()
        output = (self.target / "index.md").read_text()
        self.assertIn("1 статья", output)
        self.assertIn("[First layer](/faq/one/)", output)
        self.assertIn("CC1; PLA.", output)
        self.assertNotIn("Обновлено", output)
        self.assertNotIn("Must stay unlisted", output)

    def test_feedback_prefills_canonical_url_and_form_fields(self):
        with patch.dict("os.environ", {"SITE_URL": "https://demshin.github.io", "SITE_BASE": "/elegoo-cc"}):
            links = PREPARE.feedback_links("faq/one", "Ошибка & решение", "CC2; TPU")
        case = parse_qs(urlsplit(links["case"]).query)
        correction = parse_qs(urlsplit(links["correction"]).query)
        self.assertEqual(case["template"], ["case.yml"])
        self.assertEqual(case["page"], ["https://demshin.github.io/elegoo-cc/faq/one/"])
        self.assertEqual(case["conditions"], ["CC2; TPU"])
        self.assertEqual(correction["template"], ["correction.yml"])
        self.assertEqual(correction["page"], case["page"])

    def test_bad_review_preserves_previous_output(self):
        (self.site / "article-reviews.json").write_text(json.dumps({"reviews": {"data/private.md": {}}}))
        with self.assertRaisesRegex(AssertionError, "Review for unlisted"):
            self.run_prepare()
        self.assertTrue((self.target / "keep.md").is_file())


class ReviewFreshness(unittest.TestCase):
    def test_review_is_stale_when_article_text_changes(self):
        text = "# Article\n\nA supported statement.\n"
        record = {
            "content_sha256": sha256(text.encode()).hexdigest(),
            "reviewed_on": "2026-11-02", "status": "supported", "summary": "Checked outcomes.",
        }
        self.assertIn("Сверено с источниками 02.11.2026", PREPARE.review_status(text, record))
        self.assertIn("нужна повторная сверка", PREPARE.review_status(text + "Changed claim.\n", record))

    def test_no_review_does_not_claim_verification(self):
        self.assertIn("отдельно не зафиксирована", PREPARE.review_status("# Article\n", None))


class ArticleCountLabel(unittest.TestCase):
    def test_russian_noun_forms(self):
        cases = {
            0: "статей", 1: "статья", 2: "статьи", 4: "статьи", 5: "статей",
            11: "статей", 14: "статей", 21: "статья", 22: "статьи", 25: "статей",
            101: "статья", 111: "статей", 114: "статей",
        }
        for count, noun in cases.items():
            with self.subTest(count=count):
                self.assertEqual(PREPARE.article_count_label(count), f"{count} {noun}")


if __name__ == "__main__":
    unittest.main()
