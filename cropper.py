"""
	Date:
		01/18/2019 (add UPS, FedEx label handling) 0.6.0
		01/15/2019 (add comments)
		01/14/2019 (log output in all function/senario; organize log files by day, save to folder) 0.5.0
		01/11/2019 (log streaming output; log file naming and placing) 0.4.0
			(handle directory not exist exception) 0.3.1
		01/10/2019 (accepting single file, label no. input) 0.3.0
		01/09/2019 (input variation: accepting more inputs. espacially for specified page) 0.2.0
		01/08/2019 (try to add blank page detect: failed. getContexts, extractText: non works)	0.2.0
		01/04/2019 (created)	0.1.0
	Author: Zixuan Zhang
	Function: crop pdf files, save to 1 file
	Usage: 
		python3 cropper.py [-s fedex/ups/usps]	# default: usps
		python3 cropper.py -l file_list
		python3 cropper.py -d directory [-r]
		python3 cropper.py -f file_name [-n label_num]
"""

from PyPDF2 import PdfFileWriter, PdfFileReader
from copy import copy
import os
from optparse import OptionParser
import logging
import sys
import datetime

CURRENT_VERSION = '0.6.0'

def crop_other(inputFilePath):
	logging.info('cropping FedEx/UPS file: {}'.format(inputFilePath))	

	outputFilePath = inputFilePath[:-4]+'-cropped.pdf'
	inputFile = open(inputFilePath, 'rb')
	inputStream = PdfFileReader(inputFile, strict=False)
	outputStream = PdfFileWriter()

	for page in [inputStream.getPage(i) for i in range(inputStream.getNumPages())]:
		# if multiple pages, bigger/latter label cannot be created in if-clause. or the pages will be the same as latter
		# error will happen if the order changes
		label1 = page

		# critical coordinates
		center = (page.mediaBox.getUpperRight_x() / 2, page.mediaBox.getUpperRight_y() / 2)
		upper_left = (page.mediaBox.getUpperLeft_x() + 15, page.mediaBox.getUpperLeft_y() - 70)
		upper_right = (page.mediaBox.getUpperRight_x() - 15, page.mediaBox.getUpperRight_y() - 70)
		lower_right = (page.mediaBox.getLowerRight_x() - 15, page.mediaBox.getLowerRight_y() + 70)
		lower_left = (page.mediaBox.getLowerLeft_x() + 15, page.mediaBox.getLowerLeft_y() + 70)

		# left upper label
		label1.mediaBox.upperLeft = upper_left
		label1.mediaBox.upperRight = upper_right
		label1.mediaBox.lowerLeft = (upper_left[0], center[1])
		label1.mediaBox.lowerRight = (upper_right[0], center[1])

		outputStream.addPage(label1)

	with open(outputFilePath, "wb") as outputFile:
		outputStream.write(outputFile)

	logging.info('crop finished!')

	inputFile.close()

def crop(inputFilePath, indicator = [True, True, True, True]):
	logging.info('cropping file: {} for label #: {}'.format(inputFilePath, [label + 1 for label, indi in enumerate(indicator) if indi]))	

	outputFilePath = inputFilePath[:-4]+'-cropped.pdf'
	inputFile = open(inputFilePath, 'rb')
	inputStream = PdfFileReader(inputFile, strict=False)
	outputStream = PdfFileWriter()

	for page in [inputStream.getPage(i) for i in range(inputStream.getNumPages())]:
		# if multiple pages, bigger/latter label cannot be created in if-clause. or the pages will be the same as latter
		# error will happen if the order changes
		label1 = page
		label2 = copy(page)
		label3 = copy(page)
		label4 = copy(page)

		# critical coordinates
		center = (page.mediaBox.getUpperRight_x() / 2, page.mediaBox.getUpperRight_y() / 2)
		upper_left = (page.mediaBox.getUpperLeft_x() + 15, page.mediaBox.getUpperLeft_y() - 70)
		upper_right = (page.mediaBox.getUpperRight_x() - 15, page.mediaBox.getUpperRight_y() - 70)
		lower_right = (page.mediaBox.getLowerRight_x() - 15, page.mediaBox.getLowerRight_y() + 70)
		lower_left = (page.mediaBox.getLowerLeft_x() + 15, page.mediaBox.getLowerLeft_y() + 70)

		if indicator[0]:
			# left upper label
			label1.mediaBox.upperLeft = upper_left
			label1.mediaBox.upperRight = (center[0], upper_right[1])
			label1.mediaBox.lowerRight = center
			label1.mediaBox.lowerLeft = (lower_left[0], center[1])

		if indicator[1]:
			# right upper label
			label2.mediaBox.upperLeft = (center[0], upper_left[1])
			label2.mediaBox.upperRight = upper_right
			label2.mediaBox.lowerRight = (lower_right[0], center[1])
			label2.mediaBox.lowerLeft = center

		if indicator[2]:
			# right lower label
			label3.mediaBox.upperLeft = (upper_left[0], center[1])
			label3.mediaBox.upperRight = center
			label3.mediaBox.lowerRight = (center[0], lower_right[1])
			label3.mediaBox.lowerLeft = lower_left

		if indicator[3]:
			# left lower label
			label4.mediaBox.upperLeft = center
			label4.mediaBox.upperRight = (upper_right[0], center[1])
			label4.mediaBox.lowerRight = lower_right
			label4.mediaBox.lowerLeft = (center[0], lower_left[1])

		if indicator[0]:
			outputStream.addPage(label1)
		if indicator[1]:
			outputStream.addPage(label2)
		if indicator[2]:
			outputStream.addPage(label3)
		if indicator[3]:
			outputStream.addPage(label4)

		#how to get rid off white one
	with open(outputFilePath, "wb") as outputFile:
		outputStream.write(outputFile)

	logging.info('crop finished!')

	inputFile.close()

#批量处理当前目录下的所有PDF文件
'''for file in os.listdir('.'):
	if file[-4:]=='.pdf' or file[-4:]=='.PDF':
		op(file)'''

# Extract exist pdf file names from file list
def handle_file_list(file_list):
	files = []
	logging.info('handling file list: {}...'.format(file_list))
	with open(file_list, 'r') as infile:
		for row, line in enumerate(infile.readlines()):	# if the file is not very big
			line = line.strip()
			if not line:
				continue

			segs = line.split('\t')
			current_file_name = segs[0]

			# only handle pdf
			ext = os.path.splitext(current_file_name)[1]
			if ext in ('.pdf', '.PDF'):
				# pdf file must exist
				if os.path.isfile(current_file_name):
					indicator = [False, False, False, False]
					# no argument, default: crop all 4
					if len(segs) == 1:
						indicator = [True, True, True, True]
					else:
						label_to_be_print = segs[1].split(',')
						for num in label_to_be_print:
							num = int(num) - 1
							# not in range: error
							if num not in (0, 1, 2, 3):
								logger.error('label no. {} not exist!'.format(num + 1))
								raise IndexError(row, current_file_name, num + 1)
							indicator[num] = True

					file_info = [current_file_name, indicator]

					files.append(file_info)
				else:
					logging.error('{} in row {} not exist/not file!'.format(row, current_file_name))
					raise FileNotFoundError(row, current_file_name)
			else:
				logging.info('file {} not pdf: ignored'.format(current_file_name))
	logging.info('file names extracted.')

	return files

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

# Crop specified pdf file
def handle_file(filename, num_to_print):
	logging.info('handling page {} in file: {}'.format(num_to_print, filename))
	ext = os.path.splitext(filename)[1]
	if ext in ('.pdf', '.PDF'):
		if os.path.isfile(filename):
			indicator = [False, False, False, False]
			if num_to_print:
				if num_to_print in (1, 2, 3, 4):
					indicator[num_to_print - 1] = True
				else:
					logging.error('lable no. {} not exist!'.format(num_to_print))
					raise IndexError(num_to_print)
			else:
				indicator = [True, True, True, True]
			crop(filename, indicator)
		else:
			logging.error('{}: not exist / not file!'.format(filename))
			raise FileNotFoundError(filename)


def set_logger():
	folder = './logs'
	if not os.path.isdir(folder):
		os.makedirs(folder)
	module_name = os.path.splitext(os.path.basename(__file__))[0]
	date = datetime.datetime.now().strftime("%Y-%m-%d")
	log_file = '{}/[{}]{}.log'.format(folder, module_name, date)

	logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s', datefmt='%a, %d %b %Y %H:%M:%S', filename=log_file)
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
	parser.set_defaults(shipment_method = 'usps')
	#parser.add_option('-v', '-V', '--version', action="store", typ)
	parser.add_option('-l', '--file-list', type = 'string', dest = 'file_list', help = 'crop the pdf files listed in the FILELIST, with number indicating the label position. default: all', metavar = 'FILELIST')#File list: a file with some full file names, with one in each line.'
	parser.add_option('-d', '--dir', type = 'string', dest = 'directory', help = 'crop the pdf files under DIR. default: direct', metavar = 'DIR')
	parser.add_option('-r', '-R', '--recursive', action = "store_true", dest = 'recur', help = 'add files in all the sub-directories under DIR', metavar = 'DIR')
	parser.add_option('-f', '--file', type = "string", dest = 'file_name', help = 'crop the FILE', metavar = 'FILE')
	parser.add_option('-n', '--num', type = "int", dest = 'label_no_to_print', help = 'crop the Nth label of FILE', metavar = 'N')
	# parser.add_option('-s', '--shipment', type = "string", dest = 'shipment_method', help = 'use the SHIPMENT-METHOD of FedEx, UPS, or USPS', metavar = 'SHIPMENT-METHOD')

	(options, args) = parser.parse_args()

	if (options.file_list and options.directory) or (options.file_list and options.file_name) or (options.directory and options.file_name):
		parser.error("options cannot exist at the same time!")
	if options.recur and not options.directory:
		parser.error("options -r is only valid when -d is used!")
	if options.label_no_to_print and not options.file_name:
		parser.error("options -n is only valid when -f is used!")

	# default: directly under current directory
	if not options.directory and not options.file_list and not options.file_name:
		file_name = 'combined.pdf'
		logging.debug('crop default file: {}'.format(file_name))
		crop(file_name)
		# crop_fedex(file_name)
		sys.exit(0)
	
	if options.file_name:
		try:
			handle_file(options.file_name, options.label_no_to_print)
		except FileNotFoundError as fnfe:
			sys.exit(2)
		except IndexError as ie:
			sys.exit(2)

	elif options.directory:
		try:
			files = handle_directory(options.directory, options.recur)
			for file in files:
				crop(file)
		except NotADirectoryError as nade:
			#directory = nade.args[0]
			#print("error: {} not exist / not a valid directory!".format(directory))
			sys.exit(2)
		if not files:
			#print("error: {} does not have any pdf file!".format(options.directory))
			sys.exit(2)
	elif options.file_list:
		try:
			files = handle_file_list(options.file_list)
			for file in files:
				print(file)
				crop(file[0], file[1])	# content, indicator
		except FileNotFoundError as fnfe:
			#row, current_file_name = fnfe.args
			#print("error in line {}: {} not exist / not a valid pdf file!".format(row, current_file_name))
			sys.exit(2)
		except IndexError as ie:
			#row, current_file_name, num = ie.args
			#print("error in line {}: {} does not have label {}!".format(row, current_file_name, num))
			sys.exit(2)

if __name__ == '__main__':
	main()