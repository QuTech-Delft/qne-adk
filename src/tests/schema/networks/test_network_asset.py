import os
from pathlib import Path
import unittest

from cli.settings import BASE_DIR
from cli.utils import read_json_file


class TestNetworkAssetSchema(unittest.TestCase):
    """Each change in the schema files we copied from the source should be tested. When the copy is done again these
    tests will fail when the change is not merged"""
    def setUp(self) -> None:
        self.schema_path = Path(os.path.join(BASE_DIR), 'schema', 'networks', 'network_asset.json')

    def test_addition_slug_as_required_field(self):
        json_schema = read_json_file(self.schema_path)
        self.assertIn("required", json_schema)
        required_fields = json_schema["required"]
        self.assertIn("slug", required_fields)
