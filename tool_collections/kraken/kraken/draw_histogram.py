#!/usr/bin/env python
#
# TODO:
# Sometimes the alignment of the labels isn't right because trailing zeros are
# dropped, e.g. 6.50 becomes "6.5". See:
#   $ awk '{print length($1)}' /usr/share/dict/words | histogram.py -l 24
# 
# General strategy:
# Separate the truncation of long decimals and computing of label width. Decide
# which decimal place to round to, and THEN make the label strings and find the
# widest.
# 
# Rounding:
# Allow user to set number of significant digits to keep, and use a default.
# if highest_radix < keep_digits:
#   Round to the (highest_radix - sig_digits) decimal place
# else:
#   Round to whole number
# Examples (sig_digits = 4):                 max     min     round to
#   max    min         round to            22134   3.40     22134        3
#   100    10.0913     100.0     10.1        0.5   0.00098      0.5000   0.0001
#
# Precompute labels:
# Just create all the label strings beforehand and store in a second dict. Find
# the widest width that way. Also, this will move the code to be adaptable to
# arbitrary labels later (like the timestamps in upanalyze)
#
# Switching to integers:
# E.g. I don't want to show the decimal place in a 10-step range of 0 to 901
# (bin_size of 90.1) but I want to show it in a 6-step range of 0 to 15
# (bin_size of 2.5).
# However I do this, it should definitely be controllable by the user.
# 
import os
import sys
import math
import subprocess
import distutils.spawn
from optparse import OptionParser

DEFAULT_LINES = 24
DEFAULT_COLUMNS = 80

OPT_DEFAULTS = {'file':'', 'lines':0, 'width':0, 'sig_digits':4, 'dummy':False,
  'debug':False}
USAGE = """USAGE: cat data | %prog [options]
      %prog [options] -f data.txt"""
DESCRIPTION = """Print a quick histogram of the input data. Input format is one
number per line. If more than one value per line is encountered, it will split
on whitespace and take the first value. The histogram will be of the frequency
of the numbers."""
EPILOG = """Caution: It holds the entire dataset in memory, as a list."""

def main():

  parser = OptionParser(usage=USAGE, description=DESCRIPTION, epilog=EPILOG)

  parser.add_option('-f', '--file', dest='file',
    default=OPT_DEFAULTS.get('file'),
    help='Read from the given file instead of stdin.')
  parser.add_option('-l', '--lines', dest='lines', type='int',
    default=OPT_DEFAULTS.get('lines'),
    help='Height of the printed histogram, in lines. Default is the current '
    +'height of the terminal.')
  parser.add_option('-w', '--width', dest='width', type='int',
    default=OPT_DEFAULTS.get('width'),
    help='Width of the printed histogram, in columns (characters). Default is '
    +'the current width of the terminal.')
  parser.add_option('-s', '--sig-digits', dest='sig_digits', type='int',
    default=OPT_DEFAULTS.get('sig_digits'),
    help='Number of significant digits to keep in bin labels. Extra digits '
    +'below the decimal will be rounded away, but not ones above the decimal.')
  parser.add_option('-D', '--dummy', dest='dummy', action='store_const',
    const=not OPT_DEFAULTS.get('dummy'), default=OPT_DEFAULTS.get('dummy'),
    help='Use dummy data: a random range of floats between 0.0 and 10.0, '
    +'including those two values.')
  parser.add_option('-d', '--debug', dest='debug', action='store_const',
    const=not OPT_DEFAULTS.get('debug'), default=OPT_DEFAULTS.get('debug'),
    help='Debug mode.')

  (options, arguments) = parser.parse_args()

  debug = options.debug

  (lines, columns) = term_size(DEFAULT_LINES, DEFAULT_COLUMNS)
  if options.lines > 0:
    lines = options.lines
  if options.width > 0:
    columns = options.width

  if options.dummy:
    input = dummy_data()
  elif options.file:
    input = open(options.file, 'r')
  else:
    input = sys.stdin

  # read data into list, find min and max
  data = []
  minimum = ''
  maximum = 0
  line_num = 0
  integers = True
  for line in input:
    line_num+=1
    fields = line.split()
    if not fields:
      continue
    try:
      value = int(fields[0])
    except ValueError:
      try:
        value = float(fields[0])
        integers = False
      except ValueError:
        sys.stderr.write("Warning: Non-number encountered on line "
          +str(line_num)+': "'+line.rstrip('\r\n')+'"\n')
        continue
    data.append(value)
    minimum = min(minimum, value)
    maximum = max(maximum, value)

  if type(input) == file:
    input.close()

  if not data:
    sys.exit(0)

  # calculate bin size
  if maximum == minimum:
    fail("There is no variation: all values == "+str(maximum))
  if integers:
    bin_size = int(round(float(maximum - minimum)/lines))
    if bin_size < 1:
      bin_size = 1
    num_bins = int(math.ceil(float(maximum - minimum)/bin_size))
  else:
    bin_size = (maximum - minimum)/lines
    num_bins = lines
  if debug:
    print ("integers = "+str(integers)+", "+str(minimum)+" to "+str(maximum)
      +", step "+str(bin_size))

  # tally histogram bin totals, store in list
  totals = [0] * num_bins
  for value in data:
    bin_index = int((value-minimum)/bin_size)
    # put maximum values into last bin
    if bin_index == num_bins:
      bin_index = num_bins - 1
    totals[bin_index] = totals[bin_index] + 1

  bin_nums = [(i + 1) * bin_size + minimum for i in range(num_bins)]
  if debug:
    for bin_index in range(len(totals)):
      print (str(bin_index)+" ("+str(bin_nums[bin_index])+"):\t"
        +str(totals[bin_index]))

  # create the bin labels
  round_digit = get_round_digit(bin_nums, options.sig_digits)
  (bin_labels, max_width) = get_bin_labels(bin_nums, round_digit)

  # what is the largest bin total?
  max_total = 0
  for total in totals:
    max_total = max(total, max_total)

  # print the histogram
  if debug:
    sys.stdout.write(
      "columns: "+str(columns)
      +", round_digit: "+str(round_digit)
      +", max_width: "+str(max_width)
      +"\n"
    )
  max_bar = columns - max_width - len(": ")
  for bin_index in range(num_bins):
    bar_width = int(totals[bin_index]/float(max_total) * max_bar)
    print bin_labels[bin_index] + ": " + "*" * bar_width



def term_size(default_lines=None, default_columns=None):
  """Get current terminal width, using stty command. If stty isn't available,
  or if it gives an error, return the default."""
  if not distutils.spawn.find_executable('stty'):
    return default
  devnull = open(os.devnull, 'wb')
  try:
    output = subprocess.check_output(['stty', 'size'], stderr=devnull)
  except OSError:
    devnull.close()
    return (default_lines, default_columns)
  except subprocess.CalledProcessError:
    devnull.close()
    return (default_lines, default_columns)
  devnull.close()
  try:
    (lines, columns) = output.split()
    return (int(lines), int(columns))
  except ValueError:
    return (default_lines, default_columns)


def get_round_digit(bin_nums, sig_digits):
  """Figure out which place to round to (returning a number that can be used as
  the second argument to round()). It will round such that sig_digits of the
  largest bin label in hist are kept, but if that result is negative, it will
  return a 0 instead (only round below the decimal)."""
  round_digit = 0

  integers = True
  highest_radix = -1000
  for bin_num in bin_nums:
    if isinstance(bin_num, float):
      integers = False
    highest_radix = max(radix_dist(bin_num), highest_radix)
  round_digit = sig_digits - highest_radix - 1

  if integers:
    round_digit = 0
  else:
    round_digit = max(round_digit, 0)
  return round_digit


def get_bin_labels(bin_nums, round_digit):
  """Creates bin labels with proper rounding, returns them in a list, as well as
  the longest string length of the labels."""
  max_width = 0
  max_decimals = 0
  bin_labels = []
  for bin_num in bin_nums:
    if round_digit == 0:
      bin_label = str(int(bin_num))
    else:
      bin_label = str(round(bin_num, round_digit))
    if '.' in bin_label:
      decimals = len(bin_label) - bin_label.index('.') - 1
      max_decimals = max(decimals, max_decimals)
    max_width = max(len(bin_label), max_width)
    bin_labels.append(bin_label)

  # Align the decimal point of all the numbers by left-padding with spaces
  # and right-padding with zeros
  for bin_index in range(len(bin_labels)):
    bin_label = bin_labels[bin_index]
    if '.' in bin_label:
      decimals = len(bin_label) - bin_label.index('.') - 1
      if decimals < max_decimals:
        bin_label += '0' * (max_decimals - decimals)
    spaces_needed = max_width - len(bin_label)
    bin_labels[bin_index] = ' ' * spaces_needed + bin_label

  return (bin_labels, max_width)


def radix_dist(num):
  """Return the "magnitude" of a decimal number: How far away from the radix
  (the decimal) its most significant digit is. Or, how many zeroes appear in it
  when rounded to the nearest tens (including the zero before the radix).
  Negative numbers mean to the right of the decimal, positive to the left."""
  import math
  if num == 0:
    return 0
  else:
    return int(math.floor(math.log10(abs(num))))


def dummy_data():
  import random
  dummy = [str(random.random()*10)[:4] for i in range(8)]
  dummy.append("0.0")
  dummy.append("10.0")
  return dummy


def fail(message):
  sys.stderr.write(message+"\n")
  sys.exit(1)

if __name__ == "__main__":
  main()
