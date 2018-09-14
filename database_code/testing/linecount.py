import os

counter = 0
for root, dir_, files in os.walk('.'):
  for file in files:
    if file[-4:] == '.txt':
      filepath = os.path.join(root, file)
      print(filepath, end='\r', flush=True)
      with open(filepath) as f:
        for line in f:
          counter += 1

print(counter)