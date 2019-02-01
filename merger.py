"""
	Date:
		01/15/2019 (add comments)
		01/14/2019 (log output in all function/senario; organize log files by day, save to folder; 1 log per day) 0.5.0
		01/11/2019 (exe; log streaming output; log file naming and placing) 0.4.0
					(handle directory not exist exception) 0.3.1
		01/08/2019 (update optget module to optparse)	0.3.0
		01/07/2019 (input variation: accepting more inputs)  0.2.0
		01/04/2019 (created, prototype, critical function) 0.1.0
	Author: Zixuan Zhang
	Function: merge multiply pdf files to one
	Usage: 
		python3 merger.py
		python3 merger.py -f file_list
		python3 merger.py -d directory [-r]
"""

from PyPDF2 import PdfFileMerger
import os
import logging
from optparse import OptionParser
import glob
import sys
import datetime

CURRENT_VERSION = '0.5.0'

# Merge pdf files, output to "combined.pdf" file
def merge(files):
	merger = PdfFileMerger(strict=False)

	inputs = []

	for pdf in files:
		inputs.append(open(pdf, 'rb'))

	logging.info('start merging...') 

	for content in inputs:
		merger.append(content)

	with open("combined.pdf", "wb") as output:
		merger.write(output)

	for content in inputs:
		content.close()

	logging.info('finished!') 

# Extract exist pdf file names from file list
def handle_file_list(file_list):
	result = []
	logging.info('handling file list: {}...'.format(file_list))
	with open(file_list, 'r') as infile:
		for row, line in enumerate(infile.readlines()):	# if the file is not very big
			current_file_name = line.strip()
			if not current_file_name:
				continue
			# only handle pdf
			ext = os.path.splitext(current_file_name)[1]
			if ext in ('.pdf', '.PDF'):
				# pdf file must exist
				if os.path.isfile(current_file_name):
					result.append(current_file_name)
				else:
					logging.error('{} in row {} not exist/not file!'.format(row, current_file_name))
					raise FileNotFoundError(row, current_file_name)
			else:
				logging.info('file {} not pdf: ignored'.format(current_file_name))
	logging.info('file names extracted.')

	return result

# Extract pdf file names under the directory
def handle_directory(directory, recur):
	result = []
	
	logging.info('{} handling directory: {}'.format('recursively' if recur else 'directly', directory))

	if not os.path.isdir(directory):
		logging.error('{}: not exist/not a directory!'.format(directory))
		raise NotADirectoryError(directory)

	if not recur:
		result.extend(glob.glob(os.path.join(directory, "*.pdf")))
	else:
		for root, dirs, files in os.walk(directory):
			for file in files:
				ext = os.path.splitext(file)[1]
				if ext in ('.pdf', '.PDF'):
					full_name = os.path.join(root, file)
					result.append(full_name)
				else:
					logging.info('file {} not pdf: ignored'.format(full_name))

	logging.info('file names extracted.')

	return result

def set_logger():
	folder = './logs'
	if not os.path.isdir(folder):
		os.makedirs(folder)
	module_name = os.path.splitext(os.path.basename(__file__))[0]
	date = datetime.datetime.now().strftime("%Y-%m-%d")
	log_file = '{}/[{}]{}.log'.format(folder, module_name, date)

	logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', filename=log_file)	# default file mode: a
	console=logging.StreamHandler()
	console.setLevel(logging.INFO)
	formatter=logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
	console.setFormatter(formatter)
	logging.getLogger('').addHandler(console)

def main():
	files = []
	set_logger()

	usage = 'usage: %prog [-options <argument>]'
	parser = OptionParser(usage = usage, version = '%prog {}'.format(CURRENT_VERSION))
	parser.set_defaults(recur = False)
	#parser.add_option('-v', '-V', '--version', action="store", typ)
	parser.add_option('-l', '--file-list', type = 'string', dest = 'file_list', help = 'merge the pdf files listed in the FILELIST', metavar = 'FILELIST')#File list: a file with some full file names, with one in each line.'
	parser.add_option('-d', '--dir', type = 'string', dest = 'directory', help = 'merge the pdf files under DIR. default: direct', metavar = 'DIR')
	parser.add_option('-r', '-R', '--recursive', action = "store_true", dest = 'recur', help = 'add files in all the sub-directories under DIR', metavar = 'DIR')

	(options, args) = parser.parse_args()

	if options.recur and not options.directory:
		parser.error("options -r is only valid when -d is used!")
	if options.file_list and options.directory:
		parser.error("options -l and -d cannot exist at the same time!")

	# default: directly under current directory
	if not options.directory and not options.file_list:
		options.directory = '.'
		options.recur = False
	
	if options.directory:
		try:
			files = handle_directory(options.directory, options.recur)
		except NotADirectoryError as nade:
			#directory = nade.args[0]
			#print("error: {} not exist / not a valid directory!".format(directory))
			sys.exit(2)
		if not files:
			logging.error('error: {} does not have any pdf file!'.format(options.directory))
			sys.exit(2)
	elif options.file_list:
		try:
			files = handle_file_list(options.file_list)
		except FileNotFoundError as fnfe:
			#row, current_file_name = fnfe.args
			#print("error in line {}: {} not exist / not a valid pdf file!".format(row, current_file_name))
			sys.exit(2)

	logging.debug(files)

	merge(files)

if __name__ == '__main__':
	main()