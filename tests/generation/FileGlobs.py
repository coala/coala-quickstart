import os
import unittest

from pyprint.NullPrinter import NullPrinter
from coalib.output.printers.LogPrinter import LogPrinter
from coalib.misc.ContextManagers import (
    simulate_console_inputs, suppress_stdout, retrieve_stdout)
from coala_quickstart.generation.FileGlobs import (
    get_project_files, generate_glob_exps)
from coalib.collecting.Collectors import collect_files


class TestQuestion(unittest.TestCase):

    def setUp(self):
        self.printer = NullPrinter()
        self.log_printer = LogPrinter(self.printer)

    def test_get_project_files(self):
        orig_cwd = os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.makedirs("file_globs_testfiles", exist_ok=True)
        os.chdir("file_globs_testfiles")

        os.makedirs("src", exist_ok=True)
        os.makedirs("ignore_dir", exist_ok=True)
        open(os.path.join("src", "file.c"), "w").close()
        open("root.c", "w").close()
        open(os.path.join("ignore_dir", "src.c"), "w").close()
        open(os.path.join("ignore_dir", "src.js"), "w").close()

        with suppress_stdout(), simulate_console_inputs("**.c", "ignore_dir/**"):
            res = get_project_files(self.log_printer, self.printer, os.getcwd())
            self.assertIn(os.path.join(os.getcwd(), "src", "file.c"), res)
            self.assertIn(os.path.join(os.getcwd(), "root.c"), res)
            self.assertNotIn(os.path.join(os.getcwd(), "ignore_dir/src.c"), res)
            self.assertNotIn(os.path.join(os.getcwd(), "ignore_dir/src.js"), res)

        os.chdir(orig_cwd)

    def test_generate_glob_exps(self):
        orig_cwd = os.getcwd()
        os.chdir(os.path.dirname(os.path.realpath(__file__)))
        os.makedirs("file_globs_gen_testfiles", exist_ok=True)
        os.chdir("file_globs_gen_testfiles")

        dir1 = os.path.join("src", "inc", "dir")
        dir2 = os.path.join("src", "inc", "abs")
        dir3 = os.path.join("src", "run", "dir")
        dir4 = os.path.join("src", "run", "abs")
        os.makedirs(dir1, exist_ok=True)
        os.makedirs(dir2, exist_ok=True)
        os.makedirs(dir3, exist_ok=True)
        os.makedirs(dir4, exist_ok=True)

        files = [os.path.join(dir1, "file1.c"),
            os.path.join(dir1, "file2.c"),
            os.path.join(dir2, "file3.c"),
            os.path.join(dir2, "file4.c"),
            os.path.join(dir3, "file5.c"),
            os.path.join(dir4, "file9.c"),
            os.path.join(dir4, "file10.c"),
            os.path.join(dir1, "run.js")]
        ignored_files = [os.path.join(dir3, "file6.c"),
            os.path.join(dir3, "file7.c"),
            os.path.join(dir4, "file8.c"),
            os.path.join(dir4, "test.js"),
            os.path.join(dir3, "run.py")]
        # src/inc/dir and src/inc/abs have all files included
        # thus src/inc is fully included
        # src/run/dir has 1 inclusion, 2 exclusions
        # src/run/abs has 2 inclusions, 1 exclusion

        files = [os.path.abspath(file) for file in files]
        ignored_files = [os.path.abspath(file) for file in ignored_files]
        for file in files + ignored_files:
            open(file, "w").close()

        include_globs, exclude_globs = generate_glob_exps(
            project_files=files,
            extensions=[".c", ".js"],
            project_dir=os.getcwd())

        glob1 = os.path.join(dir1, "*.c")
        glob2 = os.path.join(dir2, "*.c")
        glob3 = os.path.join(dir3, "*.c")
        glob4 = os.path.join(dir4, "*.c")
        jsglob1 = os.path.join(dir1, "*.js")
        jsglob4 = os.path.join(dir4, "*.js")
        self.assertEqual(
            sorted(include_globs),
            sorted([jsglob1, glob1, glob2, glob4, os.path.join(dir3, "file5.c")]))
        self.assertEqual(
            sorted(exclude_globs),
            sorted([jsglob4, os.path.join(dir4, "file8.c")]))

        returned_files = {os.path.abspath(file) for file in collect_files(
            include_globs, self.log_printer, ignored_file_paths=exclude_globs)}
        self.assertEqual(sorted(returned_files), sorted(files))

        os.chdir(orig_cwd)
