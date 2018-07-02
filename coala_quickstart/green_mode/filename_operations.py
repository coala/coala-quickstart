import os
from coala_quickstart.green_mode.green_mode import append_to_contents

def get_files_list(contents):
	file_names_list = []
	for item in contents:
		if not isinstance(item, dict):
			file_names_list.append(item)
		else:
			file_names_list += get_files_list(item[next(iter(item))])
	return file_names_list

def check_filename_prefix_postfix(contents):
	file_names_list = get_files_list(contents['dir_structure'])
	file_names_list_reverse = [os.path.splitext(x)[0][::-1] for x in file_names_list]
	# Both prefix and postfix are assumed to be minimum 4 chars long
	list_prefix = []
	list_suffix = []
	while(True):
		prefix = os.path.commonprefix(file_names_list)
		suffix = os.path.commonprefix(file_names_list_reverse)
		if len(prefix) < 4 and len(suffix) < 4:
			break
		if len(prefix) < 4:
			continue
		else:
			list_prefix.append(prefix)
		if len(suffix) < 4:
			continue
		else:
			list_suffix.append(suffix)
		# else, do some checks over here
		# same prefix files can be within same directory
		   # in this case add this setting to the directory
		# have same extension
		   # create extensions list and it to that
		# can be n amount of those in each directory
		   # no checks possible
	if len(list_suffix) == 0:
		list_suffix = ['']
	if len(list_prefix) == 0:
		list_prefix = ['']
	contents = append_to_contents(contents, 'filename_prefix', list_prefix)
	contents = append_to_contents(contents, 'filename_suffix', list_suffix)
	return contents
