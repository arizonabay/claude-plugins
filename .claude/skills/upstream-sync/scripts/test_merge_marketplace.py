"""Tests for merge_marketplace.merge_plugins."""
import unittest

from merge_marketplace import merge_plugins


def _entry(name):
    return {"name": name, "source": f"url://{name}"}


class MergePluginsTests(unittest.TestCase):
    def test_concatenates_and_sorts_alphabetically(self):
        upstream = [_entry("apple"), _entry("cherry")]
        manifest = [_entry("banana")]
        result = merge_plugins(upstream, manifest)
        self.assertEqual([p["name"] for p in result], ["apple", "banana", "cherry"])

    def test_sort_is_case_insensitive(self):
        upstream = [_entry("Apple"), _entry("banana")]
        manifest = [_entry("Avocado")]
        result = merge_plugins(upstream, manifest)
        self.assertEqual([p["name"] for p in result], ["Apple", "Avocado", "banana"])

    def test_empty_manifest_returns_upstream_sorted(self):
        upstream = [_entry("zeta"), _entry("alpha")]
        result = merge_plugins(upstream, [])
        self.assertEqual([p["name"] for p in result], ["alpha", "zeta"])

    def test_duplicate_name_raises(self):
        upstream = [_entry("toolbelt")]
        manifest = [_entry("toolbelt")]
        with self.assertRaises(ValueError) as ctx:
            merge_plugins(upstream, manifest)
        self.assertIn("toolbelt", str(ctx.exception))

    def test_preserves_entry_fields_verbatim(self):
        upstream = [{"name": "a", "source": "x", "extra": 1}]
        manifest = [{"name": "b", "source": "y", "homepage": "h"}]
        result = merge_plugins(upstream, manifest)
        self.assertEqual(result[0], {"name": "a", "source": "x", "extra": 1})
        self.assertEqual(result[1], {"name": "b", "source": "y", "homepage": "h"})


if __name__ == "__main__":
    unittest.main()
