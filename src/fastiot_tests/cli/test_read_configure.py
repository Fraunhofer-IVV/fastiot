import os
import unittest
from tempfile import NamedTemporaryFile

from fastiot.cli.import_configure import import_configure
from fastiot.cli.model import Service


class TestConfigurationImport(unittest.TestCase):
    def test_smallest_configuration(self):
        with NamedTemporaryFile(suffix='.py') as f:
            f.write(b"project_namespace = 'fastiot_unittest'")
            f.seek(0)

            config = import_configure(f.name)

            self.assertEqual('fastiot_unittest', config.project_namespace)
            self.assertEqual(os.getcwd(), config.project_root_dir)
            self.assertEqual('', config.library_package)

    def test_missing_configuration_option(self):
        with NamedTemporaryFile(suffix='.py') as f:
            with self.assertRaises(ValueError):
                _ = import_configure(f.name)

    def test_with_service_packages(self):
        with NamedTemporaryFile(suffix='.py', encoding='utf8', mode="w") as f:
            f.write("project_namespace = 'fastiot_unittest'\n")
            f.write(f"project_root_dir = '{os.path.abspath(os.path.join(__file__, '../../../..'))}'\n")
            f.seek(0)

            config = import_configure(f.name)

            self.assertEqual('fastiot_unittest', config.project_namespace)
            self.assertIsInstance(config.services[0], Service)
            self.assertEqual("fastiot_sample_services", config.services[0].package)


if __name__ == '__main__':
    unittest.main()
