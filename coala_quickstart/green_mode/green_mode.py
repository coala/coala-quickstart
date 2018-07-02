from pathlib import Path
import os
import yaml
import fnmatch
import itertools
from coalib.settings.Section import Section
from coalib.processes.Processing import get_file_dict, yield_ignore_ranges
from coala_quickstart.green_mode.QuickstartBear import QuickstartBear
from coala_quickstart.generation.Utilities import (
    split_by_language)

settings_key = 'green_mode_infinite_value_settings'


def get_contents(project_data):
	with open(project_data, 'r') as stream:
		try:
			return yaml.load(stream)
		except yaml.YAMLError:
			raise ValueError('{0} no found'.format(str(project_data)))


def append_to_contents(contents, key, values):
	if settings_key in contents:
		contents[settings_key].append({key: values})
	else:
		contents[settings_key] = [{key: values}]
	return contents


def dump_to_file(file, contents):
	with open (file, 'w+') as outfile:
		yaml.dump(contents, outfile, default_flow_style=False)


def initialize_project_data(dir, ignore_globs):
	files_dirs = os.listdir(dir)
	dir_name = dir[dir.rfind(os.sep)+1:]
	if dir_name in files_dirs:
		files_dirs.remove(dir[dir.rfind(os.sep)+1:])
	final_data = []

	for i in files_dirs:
		to_continue = False
		for glob in ignore_globs:
			if fnmatch.fnmatch(dir+i, glob):
				to_continue = True
		if to_continue is True:
			continue
		if os.path.isfile(dir+i):
			final_data.append(i)
		else:
			look_into_dir = dir+i+os.sep
			data = initialize_project_data(look_into_dir, ignore_globs)
			final_data.append({i: data})
	return final_data


def generate_complete_filename_list(contents, project_dir):
	prefix = project_dir + os.sep
	file_names_list = []
	for item in contents:
		if not isinstance(item, dict):
			file_names_list.append(prefix + item)
		else:
			file_names_list += generate_complete_filename_list(item[next(iter(item))], prefix+next(iter(item)))
	return file_names_list


def find_max_of_setting(setting, value, contents):
	found = False
	position = None
	for index, item in enumerate(contents[settings_key]):
		if isinstance(item, dict) and setting in item:
			found = True
			position = index
	if not found:
		contents[settings_key].append({setting: value})
		return contents
	else:
		current_val = contents[settings_key][position][setting]
	if value > current_val:
		contents[settings_key][position][setting] = value
	return contents


def find_min_of_setting(setting, value, contents):
	found = False
	for index, item in enumerate(contents[settings_key]):
		if isinstance(item, dict) and setting in item:
			found = True
			position = index
	if not found:
		contents[settings_key].append({setting: value})
		return contents
	else:
		current_val = contents[settings_key][position][setting]
	if value < current_val:
		contents[settings_key][position][setting] = value
	return contents


def run_quickstartbear(contents, project_dir):
	section = Section('green_mode')
	quickstartbear_obj = QuickstartBear(section, None)
	complete_filename_list = generate_complete_filename_list(contents['dir_structure'], project_dir)
	# complete_filename_list = ['/Users/ishansrivastava/Desktop/asking.py', '/Users/ishansrivastava/Desktop/mecasa.py']
	complete_file_dict = get_file_dict(complete_filename_list,
	                                   allow_raw_files=True)
	ignore_ranges = list(yield_ignore_ranges(complete_file_dict))
	find_max = ['max_lines_per_file', 'max_line_length']
	find_min = ['min_lines_per_file']
	max_lines_per_file = 0
	for key in complete_file_dict:
		return_val = quickstartbear_obj.execute(filename=key, file=complete_file_dict[key])
		# do some manipulation on return_val over here
		return_val = return_val[0]

		# return_val = {'setting_name': value, ...}
		if return_val is not None:
			for setting in find_max:
				contents = find_max_of_setting(setting, return_val[setting], contents)

			for setting in find_min:
				contents = find_min_of_setting(setting, return_val[setting], contents)

	return contents, ignore_ranges, complete_file_dict, complete_filename_list

def get_type_of_setting(setting, bear):
	__location__ = os.path.realpath(
	    os.path.join(os.getcwd(), os.path.dirname(__file__)))
	bear_settings = get_contents(os.path.join(__location__, 'bear_settings.yaml'))
	# print(bear_settings)
	for type_setting in bear_settings:
		for bear_names in bear_settings[type_setting]:
			# print("**************************")
			# print(bear_names, bear)
			if bear_names in str(bear):
				# print(bear_settings[type_setting][bear_names])
				if setting in bear_settings[type_setting][bear_names]:
					return type_setting, bear_settings[type_setting][bear_names][setting]


def some_badass_func_name(bears, bear_settings_obj, file_dict, ignore_ranges, contents, file_names):
	lang_files = split_by_language(file_names)
	lang_files =  {k.lower(): v for k, v in lang_files.items()}
	# print("%%%%%%%%%%%%%%%")
	print(lang_files, "\n****************************")
	# print(lang_files['html'])
	# for k in lang_files.items():
	# 	print(k)
	for lang in bears:
		for bear in bears[lang]:
			print(bear)
			section = Section('test-section')
			for settings in bear_settings_obj:
				if settings.bear == bear:
					# first get non optional settings
					non_op_set = settings.non_optional_settings
					# print(non_op_set.settings_bool, bear, non_op_set.settings_others)
			bool_options = [True, False]
			kwargs = {}
			kwargs['self'] = [bear]
			for setting in non_op_set.settings_bool:
				kwargs[setting] = bool_options
			for setting in non_op_set.settings_others:
				type_setting, values = get_type_of_setting(setting, bear)
				if type_setting == 'type2':
					for items in contents[settings_key]:
						for setting_name in items:
							if setting_name == setting:
								kwargs[setting_name] = [items[setting_name]]
				if type_setting == 'type3':
					kwargs[setting] = values
			# print("language:", lang)
			# print("files:", lang_files[lang.lower()])
			found_green = True
			for file in lang_files[lang.lower()]:
				kwargs['filename'] = [file]
				kwargs['file'] = [file_dict[file]]
				
				keys = list(kwargs)
				print('$$$$$$$$$$$$$$$$$$$$')
				print(kwargs)
				print("--------------------")
				print(itertools.product(*kwargs.values()))
				print('$$$$$$$$$$$$$$$$$$$$')
				# print(itertools.product(*map(kwargs.get, keys)))
				for vals in itertools.product(*kwargs.values()):
					print(dict(zip(kwargs, vals)))
					import ipdb
					ipdb.set_trace()
					ret_val = bear.execute(**dict(zip(kwargs, vals)))
				print("********************")
				for values in itertools.product(*map(kwargs.get, keys)):
					print("%%%%%%%%%")
					try:
						return_val = bear.execute(**dict(zip(keys, values)))
					except:
						print("some shit happened", bear)
						found_green = False
						return_val = None
					if not return_val == []:
						found_green = False
			if found_green is True:
				print("Yippee!!!", bear)


			# for file operations

				# split_by_lang()
				# for each file and file name check it
				# 	if result in ignore ranges



def green_mode(project_dir, ignore_globs, bears, bear_settings_obj):
	from coala_quickstart.green_mode.filename_operations import check_filename_prefix_postfix
	ignore_globs.append(project_dir+os.sep+'.git'+os.sep+'**')
	project_data = project_dir + os.sep + 'project_data.yaml'
	# Currently as a temporary measure, recreating the file at each run from
	# scratch.
	if os.path.isfile(project_data):
		os.remove(project_data)
	
	if not os.path.isfile(project_data):
		new_data = initialize_project_data(project_dir+os.sep, ignore_globs)
		data_to_dump = {'dir_structure': new_data}
		dump_to_file(project_data, data_to_dump)
	else:
		pass
		# Add steps to reuse this data and modify this file.
	# Operations before the running of QuickstartBear are done over here.
	# Do operations on filename over here.
	project_data_contents = get_contents(project_data)
	project_data_contents = check_filename_prefix_postfix(project_data_contents)
	
	# Run QuickstartBear
	project_data_contents, ignore_ranges, file_dict, file_names = run_quickstartbear(project_data_contents, project_dir)

	some_badass_func_name(bears, bear_settings_obj, file_dict, ignore_ranges, project_data_contents, file_names)

	# Final Dump.
	dump_to_file(project_data, project_data_contents)

	


