import unittest

from unittest.mock import patch
from copy import deepcopy

from coala_quickstart.green_mode.file_aggregator import (
    aggregate_files)


class Test_file_aggregators(unittest.TestCase):
    def test_aggregate_files(self):
        files = [
            'main.py', 'another_main.py',
            'src/a.py', 'src/b.py',
            'src/a/c.py', 'src/a/d.py',
            'src/b/x.py',
            'test/y.py', 'test/p/z.py',
        ]
        return_val = (
            'main.py', 'another_main.py',
            'src/a.py', 'src/b.py',
            'src/a/c.py', 'src/a/d.py',
            'src/b/x.py', 'src/b/t.py',
            'test/y.py', 'test/p/z.py',
        )
        project_dir_ = '/some_dir/'
        new_files = []
        for i in files:
            new_files.append(project_dir_+i)
        files = new_files

        new_return_val = ()
        for i in return_val:
            new_return_val += (project_dir_+i,)
        return_val = new_return_val

        with patch('os.walk') as mockwalk:
            mockwalk.return_value = [
                ('', (), return_val), ]
            files_ret, ignore = aggregate_files(deepcopy(files), 'some_dir')
            self.assertEqual(files_ret, ['/some_dir/**'])
            self.assertEqual(ignore, ['/some_dir/src/b/t.py'])

        return_val = (
            'main.py', 'another_main.py', 'some.c',
            'src/a.py', 'src/b.py', 'src/omg.c', 'src/gsoc.c',
            'src/a/c.py', 'src/a/d.py',
            'src/b/x.py', 'src/b/t.py', 'src/b/x.c', 'src/b/y.c',
            'test/y.py', 'test/s.c', 'test/badass.c',
            'test/p/z.py', 'test/p/zx.c', 'test/p/xz.c',
        )

        new_return_val = ()
        for i in return_val:
            new_return_val += (project_dir_+i,)
        return_val = new_return_val

        with patch('os.walk') as mockwalk:
            mockwalk.return_value = [
                ('', (), return_val), ]
            files_ret, ignore = aggregate_files(deepcopy(files), 'some_dir')
            self.assertEqual(files_ret, ['/some_dir/**.py'])
            self.assertEqual(ignore, ['/some_dir/src/b/t.py'])

        return_val = (
            'main.py', 'another_main.py', 'some.c', 'README.md',
            'src/a.py', 'src/b.py', 'src/omg.c', 'src/gsoc.c',
            'src/a/c.py', 'src/a/d.py',
            'src/b/x.py', 'src/b/t.py', 'src/b/x.c', 'src/b/y.c',
            'test/y.py', 'test/s.c', 'test/badass.c',
            'test/p/z.py', 'test/p/zx.c', 'test/p/xz.c',
        )

        new_return_val = ()
        for i in return_val:
            new_return_val += (project_dir_+i,)
        return_val = new_return_val

        with patch('os.walk') as mockwalk:
            mockwalk.return_value = [
                ('', (), return_val), ]
            files_ret, ignore = aggregate_files(deepcopy(files), 'some_dir')
            self.assertEqual(files_ret, ['/some_dir/**.py'])
            self.assertEqual(ignore, ['/some_dir/src/b/t.py'])

        return_val = (
            'main.py', 'another_main.py', 'some.c', 'README.md',
            'src/a.py', 'src/b.py', 'src/omg.c', 'src/gsoc.c',
            'src/x.py', 'src/y.py', 'src/temp.py', 'src/h.py', 'src/u.py',
            'src/a/c.py', 'src/a/d.py', 'src/a/l.py', 'src/a/v.py',
            'src/b/x.py', 'src/b/t.py', 'src/b/x.c', 'src/b/y.c',
            'test/y.py', 'test/s.c', 'test/badass.c',
            'test/p/z.py', 'test/p/zx.c', 'test/p/xz.c',
        )

        new_return_val = ()
        for i in return_val:
            new_return_val += (project_dir_+i,)
        return_val = new_return_val

        with patch('os.walk') as mockwalk:
            mockwalk.side_effect = [[
                ('', (), return_val), ], [
                ('', (), (
                    '/some_dir/main.py', '/some_dir/another_main.py',
                    '/some_dir/some.c', '/some_dir/README.md')), ],
                [('/some_dir/src/', (), (
                    '/some_dir/src/a.py', '/some_dir/src/b.py',
                    '/some_dir/src/omg.c', '/some_dir/src/gsoc.c',
                    '/some_dir/src/x.py', '/some_dir/src/y.py',
                    '/some_dir/src/temp.py', '/some_dir/src/h.py',
                    '/some_dir/src/u.py',
                    '/some_dir/src/a/c.py', '/some_dir/src/a/d.py',
                    '/some_dir/src/a/l.py', '/some_dir/src/a/v.py'
                    '/some_dir/src/b/x.py', '/some_dir/src/b/t.py',
                    '/some_dir/src/b/x.c', '/some_dir/src/b/y.c',)), ],
                [('/some_dir/src/', (), (
                    '/some_dir/src/a.py', '/some_dir/src/b.py',
                    '/some_dir/src/omg.c', '/some_dir/src/gsoc.c',
                    '/some_dir/src/x.py', '/some_dir/src/y.py',
                    '/some_dir/src/temp.py', '/some_dir/src/h.py',
                    '/some_dir/src/u.py')), ],
                [('/some_dir/src/a/', (), (
                    '/some_dir/src/a/c.py', '/some_dir/src/a/d.py',
                    '/some_dir/src/a/l.py', '/some_dir/src/a/v.py')), ],
                [('/some_dir/test/', (), (
                    '/some_dir/test/y.py', '/some_dir/test/s.c',
                    '/some_dir/test/badass.c',
                    '/some_dir/test/p/z.py', '/some_dir/test/p/zx.c',
                    '/some_dir/test/p/xz.c',))], ]
            files_ret, ignore = aggregate_files(deepcopy(files), 'some_dir')
            self.assertEqual(files_ret, ['/some_dir/*', '/some_dir/src/*',
                                         '/some_dir/src/a/**',
                                         '/some_dir/test/**']
                             )
            self.assertEqual(ignore, ['/some_dir/some.c',
                                      '/some_dir/README.md',
                                      '/some_dir/src/omg.c',
                                      '/some_dir/src/gsoc.c',
                                      '/some_dir/src/x.py',
                                      '/some_dir/src/y.py',
                                      '/some_dir/src/temp.py',
                                      '/some_dir/src/h.py',
                                      '/some_dir/src/u.py',
                                      '/some_dir/src/a/l.py',
                                      '/some_dir/src/a/v.py',
                                      '/some_dir/test/s.c',
                                      '/some_dir/test/badass.c',
                                      '/some_dir/test/p/zx.c',
                                      '/some_dir/test/p/xz.c']
                             )
