import os
import subprocess
import sys

for root, dir_, files in os.walk(sys.argv[1]):
	for file in files:
		if file[-3:] == '.gz':
			filepath = os.path.join(root, file)
			print('Unzipping: ', filepath)
			subprocess.check_output(['gzip', '-d', filepath])

		if file[-4:] == '.zip':
			filepath = os.path.join(root, file)
			print('Unzipping: ', filepath)
			subprocess.check_output(['unzip', '-f', filepath, '-d', root])



