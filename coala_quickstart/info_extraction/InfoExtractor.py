import os

from coalib.parsing.Globbing import glob, fnmatch
from coala_quickstart.info_extraction.Info import Info


class InfoExtractor:
    # tuple of file globs supported by the extractor.
    supported_file_globs = tuple()

    # Links to the issues/documentations for relevant specs of supported files.
    spec_references = []

    # tuple of ``Info`` classes that can be extracted.
    supported_info_kinds = (Info,)

    def __init__(self,
                 target_globs,
                 project_directory):
        """
        :param target_globs:      list of file globs to extract information
                                  from.
        :param project_directory: Absolute path to project directory in which
                                  the target files will be searched.
        """
        target_files = self.retrieve_files(target_globs, project_directory)
        for fname in target_files:
            if not fnmatch(fname, self.supported_file_globs):
                raise ValueError('The taraget file {} does not match the '
                                 'supported file globs {} of {}'.format(
                                    fname,
                                    self.supported_file_globs,
                                    self.__class__.__name__))
        self.target_files = [
            os.path.join(project_directory, f) for f in target_files]
        self.directory = project_directory
        self._information = dict()

    @property
    def information(self):
        """
        Return extracted information (if any)
        """
        return self._information

    def parse_file(self, fname, file_content):
        """
        Parses the given file and returns the parsed file.
        """
        raise NotImplementedError

    def _add_info(self, fname, info_to_add):
        """
        Organize and add the supplied information in self.information
        attribute.

        :param fname:       Name of the file from which information is
                            extracted.
        :param info_to_add: list of ``Info`` instances to add.
        """
        for info in info_to_add:
            if not isinstance(info, self.supported_info_kinds):
                raise ValueError('The class {} is not present in '
                                 'supported information kinds of {}'.format(
                                    info.name,
                                    self.__class__.__name__))
            if not info.extractor:
                info.extractor = self
            if self._information.get(fname):
                if self._information[fname].get(info.name):
                    self._information[fname][info.name].append(info)
                else:
                    self._information[fname][info.name] = [info]
            else:
                self._information[fname] = {
                    info.name: [info]
                }

    def extract_information(self):
        """
        Extracts the information, saves in the object and returns it.
        """
        for fpath in self.target_files:
            with open(fpath, 'r') as f:
                pfile = self.parse_file(fpath, f.read())
                fname = os.path.relpath(fpath, self.directory)
                file_info = self.find_information(fname, pfile)
                if file_info:
                    self._add_info(fname, file_info)

        return self.information

    def find_information(self, fname, parsed_file):
        """
        Returns a list of ``Info`` instances.
        """
        raise NotImplementedError

    @staticmethod
    def retrieve_files(file_globs, directory):
        """
        Returns matched filenames acoording to the list of file globs and
        supported files of the extractor.
        """
        matches = []

        cwd = os.getcwd()
        os.chdir(directory)

        for g in file_globs:
            matches += glob(g)

        matched_files = [f for f in matches if not os.path.isdir(f)]
        os.chdir(cwd)

        return matched_files
