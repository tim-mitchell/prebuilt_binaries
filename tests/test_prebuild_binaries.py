import sys
import unittest
import unittest.mock

import prebuilt_binaries
import setuptools.dist


@unittest.mock.patch('os.path.exists')
class TestExtension(unittest.TestCase):
    def test_file_existence_check(self, exists):
        exists.return_value = False
        with self.assertRaises(ValueError):
            prebuilt_binaries.PrebuiltExtension(r'c:\a\file\that\does\not\exist')

    def test_default_name(self, exists):
        exists.return_value = True
        e = prebuilt_binaries.PrebuiltExtension(r'c:\a\prebuilt\package.pyd')
        self.assertEqual('package', e.name)

    def test_package_name(self, exists):
        exists.return_value = True
        e = prebuilt_binaries.PrebuiltExtension(r'c:\a\prebuilt\sub.pyd', package='package')
        self.assertEqual('package.sub', e.name)


@unittest.mock.patch('os.path.exists')
@unittest.mock.patch('prebuilt_binaries.copy_file')
class TestSetuptoolsCommand(unittest.TestCase):
    def test_file_is_copied(self, copy_file, exists):
        exists.return_value = True
        cmd = prebuilt_binaries.prebuilt_binary(unittest.mock.create_autospec(spec=setuptools.dist.Distribution,
                                                                              instance=True, verbose=False))
        e = prebuilt_binaries.PrebuiltExtension(r'c:\a\prebuilt\package.pyd')
        cmd.dry_run = False
        cmd.build_lib = r'c:\path\to\nowhere'
        cmd.extensions = [e]

        cmd.run()
        # assert
        pyver = f'cp{sys.version_info.major}{sys.version_info.minor}'
        copy_file.assert_called_once()
        cargs = copy_file.call_args
        self.assertEqual(e.input_file, cargs.args[0])
        dest_filename = cargs.args[1]
        self.assertTrue(dest_filename.startswith(fr'{cmd.build_lib}\package'))
        self.assertTrue(pyver in dest_filename)
        self.assertTrue(dest_filename.endswith('.pyd'))

    def test_copied_file_excludes_package(self, copy_file, exists):
        exists.return_value = True
        cmd = prebuilt_binaries.prebuilt_binary(unittest.mock.create_autospec(spec=setuptools.dist.Distribution,
                                                                              instance=True, verbose=False))
        e = prebuilt_binaries.PrebuiltExtension(r'c:\a\prebuilt\sub.pyd', package='package')
        cmd.dry_run = False
        cmd.build_lib = r'c:\path\to\nowhere'
        cmd.extensions = [e]

        cmd.run()
        # assert
        pyver = f'cp{sys.version_info.major}{sys.version_info.minor}'
        copy_file.assert_called_once()
        cargs = copy_file.call_args
        self.assertEqual(e.input_file, cargs.args[0])
        dest_filename = cargs.args[1]
        self.assertTrue(dest_filename.startswith(fr'{cmd.build_lib}\sub'))
        self.assertTrue(pyver in dest_filename)
        self.assertTrue(dest_filename.endswith('.pyd'))
