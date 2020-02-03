import csv
import sys
import os
import tempfile
import argparse

# Handles our actual search and replace logic.
# Input is file handlers; this enables cleaner testing.
def replacer_guts(input, output, findval, replaceval, targetcols=None):

	if targetcols != None:
		targetcols = targetcols.split(",")
			
	reader = csv.DictReader(input, skipinitialspace=True)
	writer = csv.DictWriter(output, fieldnames=reader.fieldnames)	
	writer.writeheader()
	
	for row in reader:
		for col in row:
			if (targetcols == None) or (col in targetcols):
				row[col] = row[col].replace(findval, replaceval)
		writer.writerow(row)

# The outward-facing wrapper for the guts above. Invoke with paths to
# infile and outfile.
# If running as a module, remember paths are relative to module dir!
def replacer(infile, outfile, findval, replaceval, targetcols=None):
		
	with open(infile, "r") as input, open(outfile, "w+") as output:
		replacer_guts(input, output, findval, replaceval, targetcols)

# Quick and dirty unit tests for the replacer (or, specifically, for
# replacer_guts()).	Writes up some temporary file handlers, sends them
# to replacer_guts() and checks for an exact expected result.
def replacer_tests():
	
	# This could, it is admitted, have been done a lot more elegantly,
	# but it's more than sufficient for our purposes and I didn't want
	# to overthink this.
	
	# A list of input CSVs
	# Yes these input values are all identical
	test_data = ["a,b,c\r\nx,x,x\r\ny,y,y\r\nx,x,x\r\n",\
				 "a,b,c\r\nx,x,x\r\ny,y,y\r\nx,x,x\r\n",\
				 "a,b,c\r\nx,x,x\r\ny,y,y\r\nx,x,x\r\n"]
			
	# A corresponding list of replacer_guts() arguments.
	# NB: [0]: Find value [1]: Replace value [2]: Restrict to columns			
	test_args        = [["x", "z", "a"],\
						["x", "z", "b,c"],\
						["x", "z", None]]
	
	# A corresponding expected output CSV.
	expected_outputs = ["a,b,c\r\nz,x,x\r\ny,y,y\r\nz,x,x\r\n",\
						"a,b,c\r\nx,z,z\r\ny,y,y\r\nx,z,z\r\n",\
						"a,b,c\r\nz,z,z\r\ny,y,y\r\nz,z,z\r\n"]
						
	failcount = 0
	
	for i in range(0,len(test_data)):
	
		# Convenience declaration
		a = test_args[i]
	
		with tempfile.NamedTemporaryFile("r+") as testinput, tempfile.NamedTemporaryFile("r+") as testoutput:

			testinput.write(test_data[i])
			testinput.seek(0)
		
			replacer_guts(testinput, testoutput, a[0], a[1], a[2])
		
			testoutput.seek(0)
			result = testoutput.read()
		
			if expected_outputs[i] != result:
				print "A test case has failed. Details:"
				print "Input Data:"
				print test_data[i]
				print "Operation:"
				print "Find string: \"%s\"" %(a[0])
				print "Replace with: \"%s\"" %(a[1])
				if a[2] == None:
					a[2] = "All"
				print "Columns: \"%s\"" %(a[2])
				print "Expected Result:"
				print expected_outputs[i]
				print "Actual Result:"
				print result
				failcount += 1
				
	if failcount == 0:
		print "All tests passed!"
	else:
		print "%d of %d tests failed!" %(failcount, len(test_data))
		
# When running non-interactively, parse command line arguments and call replacer
if __name__ == "__main__":

	if (len(sys.argv) == 2 and sys.argv[1] == "--test"):
		replacer_tests()
		exit(0)

	parser = argparse.ArgumentParser(description="Find and replace values in a CSV file. Run with --test (and no other args) to unit test.",\
									 add_help=True)

	parser.add_argument("csv",\
						type=str,\
						metavar="PATH_TO_CSV",\
						help="CSV file to operate on")
					
	parser.add_argument("find",\
						type=str,\
						metavar="FINDVALUE",\
						help="String to find")
					
	parser.add_argument("replace",\
						type=str,\
						metavar="REPLACEVALUE",\
						help="String to replace")
					
	parser.add_argument("-c", "--column",\
						required=False,\
						type=str,\
						metavar="COLUMN_NAME",\
						help="Restrict operation to named column(s). Separate with commas.")

	parser.add_argument("-o", "--output",\
						required=False,\
						type=str,\
						metavar="FILENAME",\
						help="Name of file to output. Defaults to <input>_replaced.csv")
    
	args = parser.parse_args()
	
	# Handle default case for output filename.
	# Remove extension from input file if present and append "_replaced.csv".
	if args.output == None:
		args.output = "%s_replaced.csv" %(os.path.splitext(args.csv)[0])
	
	replacer(args.csv, args.output, args.find, args.replace, args.column)