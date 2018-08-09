from coalib.bears.LocalBear import LocalBear


class QuickstartBear(LocalBear):
    """
    A bear to parse out the file_dict and return
    values of settings that can take an infinite
    set of values and can be determined easily
    by looking at the file contents.
    """

    def run(self, filename, file):
        """
        :return:
            A list containing a dict of setting name as
            key and the appropriate value guessed by the bear.
        """
        max_line_length = 0
        if file:
            for line in file:
                length = len(line)
                if length > max_line_length:
                    max_line_length = length

            return_val = dict()
            return_val['max_line_length'] = max_line_length
            return_val['max_lines_per_file'] = len(file)
            return_val['min_lines_per_file'] = len(file)
            return [return_val]
        else:
            return [None]
