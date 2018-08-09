import os
from copy import deepcopy

from coala_quickstart.green_mode.green_mode import (
    append_to_contents)


class Node:
    def __init__(self, character, parent=None):
        self.count = 1
        self.character = character
        self.children = {}
        self.parent = parent

    def insert(self, string, idx):
        if idx >= len(string):
            return
        code = ord(string[idx])  # ASCII code
        ch = string[idx]
        if ch in self.children:
            self.children[ch].count += 1
        else:
            self.children[ch] = Node(string[idx], self)
        self.children[ch].insert(string, idx+1)


class Trie:
    """
    Creates a Trie data structure for storing names of files.
    """

    def __init__(self):
        self.root = Node('')

    def insert(self, string):
        self.root.insert(string, 0)

    # Just a wrapper function.
    def get_prefixes(self, min_length, min_files):
        # Pair of prefix, and frequency.
        # Prefixes shorter than min_length are not stored.
        self.prefixes = {}
        self._discover_prefixes(self.root, [], min_length, 0, min_files)
        # Return the prefixes in sorted order.
        return sorted(self.prefixes.items(), key=lambda x: (x[1], x[0]),
                      reverse=True)

    # Do a dfa search on the trie.
    # Discovers the prefixes in the trie and stores them in the self.prefixes
    # dictionary.
    def _discover_prefixes(self, node, prefix, min_length, len, min_files):
        if node.count < min_files and node.character != '':
            return
        if len >= min_length:
            current_prefix = ''.join(prefix)+node.character
            to_delete = []
            for i in self.prefixes:
                if i in current_prefix:  # pragma: no cover
                    to_delete.append(i)
            for i in to_delete:
                self.prefixes.pop(i)
            self.prefixes[''.join(prefix)+node.character] = node.count
        orig_prefix = deepcopy(prefix)
        for ch, ch_node in node.children.items():
            prefix.append(node.character)
            if (not ch_node.count < node.count) or orig_prefix == []:
                self._discover_prefixes(ch_node, prefix, min_length, len+1,
                                        min_files)
            prefix.pop()


def get_files_list(contents):
    """
    Generates a list which contains only files from
    the entire project from the directory and file
    structure written to '.project_data.yaml'.
    :param contents:
        The python object containing the file and
        directory structure written to '.project_data.yaml'.
    :return:
        The list of all the files in the project.
    """
    file_names_list = []
    for item in contents:
        if not isinstance(item, dict):
            file_names_list.append(item)
        else:
            file_names_list += get_files_list(
                item[next(iter(item))])
    return file_names_list


def check_filename_prefix_postfix(contents, min_length_of_prefix=6,
                                  min_files_for_prefix=5):
    """
    Checks whether the project has some files with filenames
    having certain prefix or postfix.
    :param contents:
        The python object containing the file and
        directory structure written to '.project_data.yaml'.
    :param min_length_of_prefix:
        The minimum length of prefix for it green_mode to
        consider as a valid prefix.
    :param min_files_for_prefix:
        The minimum amount of files a prefix to match against
        for green_mode to consider it as a valid prefix.
    :return:
        Update contents value with the results found out
        from the file/directory structure in .project_data.yaml.
    """
    file_names_list = get_files_list(contents['dir_structure'])
    file_names_list = [os.path.splitext(os.path.basename(x))[
                                        0] for x in file_names_list]
    file_names_list_reverse = [os.path.splitext(
        x)[0][::-1] for x in file_names_list]
    trie = Trie()
    for file in file_names_list:
        trie.insert(file)
    prefixes = trie.get_prefixes(min_length_of_prefix, min_files_for_prefix)
    trie_reverse = Trie()
    for file in file_names_list_reverse:
        trie_reverse.insert(file)
    suffixes = trie_reverse.get_prefixes(
        min_length_of_prefix, min_files_for_prefix)
    if len(suffixes) == 0:
        suffixes = [('', 0)]
    if len(prefixes) == 0:
        prefixes = [('', 0)]
    prefix_list, suffix_list = [], []
    for prefix, freq in prefixes:
        prefix_list.append(prefix)
    for suffix, freq in suffixes:
        suffix_list.append(suffix[::-1])
    contents = append_to_contents(contents, 'filename_prefix', prefix_list)
    contents = append_to_contents(contents, 'filename_suffix', suffix_list)

    return contents
