#!/user/bin/env python
	
import json
import sys
import time
from types import *

all_class_list = []

def cpp_type(value):
	if type(value) is IntType:
		return 'int'
	elif type(value) is FloatType:
		return 'double'
	elif type(value) is BooleanType:
		return 'bool'
	elif type(value) is UnicodeType:
		return 'std::string'
	elif type(value) is ListType:
		return 'std::vector'
	else:
		pass
def generate_includes_h(classname):
	includes = ['"' + classname + '.h"', '"json/json.h"', '<iostream>', '<fstream>', '<string>', '<vector>']
	return includes

def generate_includes_cpp(classname):
	includes = ['"' + classname + '.h"']
	return includes

def generate_header(classname, includes):
	header = open(classname + '.h', 'wb')
	header.write('/*\n - {}.h -\n'.format(classname))
	header.write('\n Do not edit\n Generated by script\n\n*/\n')
	header.write('#ifndef __{}_H__\n'.format(classname.upper()))
	header.write('#define __{}_H__\n'.format(classname.upper()))
	for ele in includes:
		header.write('#include {}\n'.format(ele))
	header.write('\n')
	for obj in all_class_list:
		for cls in obj:
			header.write('class {}\n'.format(cls))
			header.write('{\n')
			header.write('public:\n')
		
			header.write('\t' + cls + '(){};\n')
			header.write('\t' + cls + '(Json::Value root);\n')
			header.write('\t' + cls + '(const char* configFileName);\n')
			header.write('\tvirtual ~' + cls + '();\n\n')
			for member in obj[cls]:
				for tp in member:
					header.write('\t' + tp + ' get' + member[tp]['value'].capitalize() + '() const{\n')
					header.write('\t\treturn _' + member[tp]['value'] + ';\n\t}\n')

			header.write('\nprivate:\n')
			for member in obj[cls]:
				for tp in member:
					header.write('\t{} _{};\n'.format(tp, member[tp]['value']))
	
			header.write('};\n\n')
	header.write('#endif')

# jsoncpp type methods
type_methods = {'int':'asInt', 'bool':'asBool', 'double':'asDouble', 'std::string':'asString'}
def common_statement(t, v):
	return '_{} = root["{}"].{}();'.format(v, v, type_methods[t])

def object_statement(t,v):
	return '_{} = {}(root["{}"]);'.format(v, t, v)

def vector_statement(t, v, m):
	stats = []
	temp = 't_'+ v
	stats.append('const Json::Value {} = root[\"{}\"];'.format(temp, v))
	stats.append('for (unsigned int i = 0; i < {}.size(); ++i)'.format(temp))

	if m in type_methods.keys():
		stats.append('\t_{}.push_back({}[i].{}());'.format(v, temp, type_methods[m]))
	else:
		stats.append('\t_{}.push_back({}({}[i]));'.format(v, m, temp))
	return stats

def generate_constructor(cls, ls, f):
	f.write('{}::{}(Json::Value root)\n'.format(cls, cls))
	f.write('{\n\n')

	for member in ls:
		for kind in member:
			if(member[kind]['mark'] is "C_nico"):
				f.write('\t'+common_statement(kind, member[kind]['value'])+'\n')
			elif(member[kind]['mark'] is "O_nico"):
				f.write('\t'+object_statement(kind, member[kind]['value'])+'\n')
			else:
				f.write('\n')
				for line in vector_statement(kind, member[kind]['value'], member[kind]['mark']):
					f.write('\t'+line+'\n')
				f.write('\n')
	f.write('\n}\n\n')

	f.write('{}::{}(const char* configFileName)\n'.format(cls, cls))
	f.write('{\n')
	f.write('\tstd::ifstream json(configFileName);\n')
	f.write('\tJson::Value root;\n')
	f.write('\tJson::Reader reader;\n')
	f.write('\tbool parsingSuccessful = reader.parse(json, root);\n')
	f.write('\tif (!parsingSuccessful)\n')
	f.write('\t{\n')
	f.write('\t\tstd::cout<<"Parsing Error! - Invalid JSON Data"<<std::endl;\n')
	f.write('\t\treturn;\n')
	f.write('\t}\n\n')
	for member in ls:
		for kind in member:
			if(member[kind]['mark'] is "C_nico"):
				f.write('\t'+common_statement(kind, member[kind]['value'])+'\n')
			elif(member[kind]['mark'] is "O_nico"):
				f.write('\t'+object_statement(kind, member[kind]['value'])+'\n')
			else:
				f.write('\n')
				for line in vector_statement(kind, member[kind]['value'], member[kind]['mark']):
					f.write('\t'+line+'\n')
				f.write('\n')
	f.write('\n}\n\n')

	f.write('{}::~{}()'.format(cls, cls) + '\n{\n\n}\n\n')

def generate_source(classname, includes):
	source = open(classname + '.cpp', 'wb')
	source.write('/*\n - {}.cpp -\n'.format(classname))
	source.write('\n Do not edit\n Generated by script\n\n*/\n')
	for ele in includes:
		source.write('#include {}\n'.format(ele))
	source.write('\n')
	for obj in all_class_list:
		for cls in obj:
			generate_constructor(cls, obj[cls], source)

def get_vector_type(data, parent_key):
	guess_type = int
	for ele in data:
		if(type(ele) is not guess_type):
			guess_type = None
			break
	if(guess_type != None):
		return "int"

	guess_type = float
	for ele in data:
		if(type(ele) is int):
			continue
		elif(type(ele) is not guess_type):
			guess_type = None
			break
	if(guess_type != None):
		return "double"

	guess_type = bool
	for ele in data:
		if(type(ele) is not guess_type):
			guess_type = None
			break
	if(guess_type != None):
		return "bool"

	guess_type = unicode
	for ele in data:
		if(type(ele) is not guess_type):
			guess_type = None
			break
	if(guess_type != None):
		return "std::string"

	guess_type = str
	for ele in data:
		if(type(ele) is not guess_type):
			guess_type = None
			break
	if(guess_type != None):
		return "std::string"

	guess_type = dict
	for ele in data:
		if(type(ele) is guess_type):
			find_object(ele, parent_key)
			return parent_key

	guess_type = list
	for ele in data:
		if(type(ele) is guess_type):
			guess_type = ("std::vector<%s > " %(get_vector_type(ele, parent_key)))
			return guess_type

def find_object(data, classname):
	member_table = []
	for key in data:
		member = {}
		var_type = ""
		var_type = ""
		mark = "C_nico"

		if(type(data[key]) is dict):
			var_type = key[0].upper() + key[1:]
			find_object(data[key], var_type)
			mark = "O_nico"
		elif(type(data[key]) is int):
			var_type = "int"
		elif(type(data[key]) is float):
			var_type = "double"
		elif(type(data[key]) is str or type(data[key]) is unicode):
			var_type = "std::string"
		elif(type(data[key]) is list):
			arr_type = get_vector_type(data[key], key[0].upper() + key[1:])
			var_type = ("std::vector<%s >" %(arr_type))
			mark = arr_type
		elif(type(data[key]) is bool):
			var_type = "bool"
		else:
			assert(False)
		var_name = key
		member[var_type] = {}
		member[var_type]["value"] = var_name
		member[var_type]["mark"] = mark
		member_table.append(member)
	class_object = {}
	class_object[classname] = member_table
	all_class_list.append(class_object)
	return

def main(filename):
	start = time.clock()
	classname = filename.split('.')[0]
	try:
		with open(filename) as f:
			content = f.read()
			f.close()
	except IOError:
		print "Can't open/read file."
		return
	data = json.loads(content)
	find_object(data, classname[0].upper() + classname[1:])
	print "Total class generated : ", len(all_class_list)

	includes_h = generate_includes_h(classname)
	includes_cpp = generate_includes_cpp(classname)

	generate_header(classname, includes_h)
	generate_source(classname, includes_cpp)
	end = time.clock()
	print "Success in : %f s" % (end - start)

if __name__ == '__main__':
	if len(sys.argv) != 2:
		print 'Usage: {} <json file>'.format(sys.argv[0])
		sys.exit(1)
	main(sys.argv[1])

