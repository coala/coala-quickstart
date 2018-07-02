from coalib.bears.LocalBear import LocalBear
from pathlib import Path


class QuickstartBear(LocalBear):

	def run(self, filename, file):
		max_line_length=0
		if not file is None:
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
