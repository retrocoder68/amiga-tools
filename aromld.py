#!/usr/bin/env python3
#  ____________________________________________________________________________
# | aromld.py - Create an Amiga ROM file from binary files                     |
# | Author: Skywalker a.k.a. J.Karlsson <j.karlsson@retrocoder.se>             |
# | Copyright (C) 2019 Skywalker. All rights reserved.                         |
# |____________________________________________________________________________|

import sys
import os
import argparse
import struct

def calc_sum(file_content):
  sum = 0
  for value in file_content:
    sum += value
    if sum >= pow(2, 32):
      sum -= pow(2,32)-1
  return sum

if __name__ == "__main__":
  script_name = os.path.basename(sys.argv[0])
  parser = argparse.ArgumentParser(script_name)
  parser.add_argument("files", nargs='+', action="store", help="input file(s)")
  parser.add_argument("--large", "-l", action="store_true", help="Create a large (512 kb) rom file. Default is 256 kb.")
  parser.add_argument("--output", "-o", action="store", help="Output file name (Default: <INPUT FILE>.rom)")
  parser.add_argument("--quiet", "-q", action="store_true", help="Do not print messages (other than errors)")

  args = parser.parse_args()

  if not args.quiet:
    print("Amiga ROM file creator / linker")

  # Set ROM id
  file_content = []
  magic = 0x11144EF9 if args.large else 0x11114EF9
  file_content.append(magic)

  if not args.quiet:
    print(f"Reading files: {args.files}")
  for file in args.files:
    with open(file, "rb") as f:
      while True:
        data = f.read(4)
        if not data: break
        value = struct.unpack(">I", data)[0]
        file_content.append(value)

  # Check length and extend
  flen = len(file_content)
  
  if flen > pow(2,17):
    print("Error: ROM file will exceed 512 kb.")
    exit(-1)
  elif flen > pow(2, 16) and not args.large:
    print("Error: ROM file will exceed 256 kb. Use --large to create 512 kb ROM.")
    exit(-1)

  req_len = pow(2,16) if not args.large else pow(2,17)
  file_content.extend([0]*(req_len-flen))

  # Store file length
  len_index = int(req_len - 5)
  file_content[len_index] = req_len*4 # Store length in bytes, i.e. 4*dword length
  
  # Check sum
  sum = calc_sum(file_content)
  err = (pow(2,32) - 1) - sum
  if err != 0:
    sum += err

  chksum_index = int(req_len-6)
  chksum = file_content[chksum_index]
  chksum += err
  if chksum > pow(2,32):
    chksum -= pow(2,32) - 1
  file_content[chksum_index] = chksum

  # Write output file
  output_file = args.output if args.output is not None else args.files[0]+".rom"
  if not args.quiet:
    print(f"Writing file {output_file}")
  with open(output_file, "wb") as o:
    for b in file_content:
      lword = struct.pack(">I", b)
      o.write(lword)

#  ____________________________________________________________________________
# | This program is free software: you can redistribute it and/or modify       |
# | it under the terms of the GNU General Public License version 2             |
# | as published by the Free Software Foundation.                              |
# |                                                                            |
# | This program is distributed in the hope that it will be useful,            |
# | but WITHOUT ANY WARRANTY; without even the implied warranty of             |
# | MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the               |
# | GNU General Public License for more details.                               |
# |                                                                            |
# | You should have received a copy of the GNU General Public License          |
# | along with this program.  If not, see <http://www.gnu.org/licenses/>       |
# | or write to the Free Software Foundation, Inc.,                            |
# | 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.                |
# |____________________________________________________________________________|
