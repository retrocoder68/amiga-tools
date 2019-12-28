#!/usr/bin/env python3
#  ____________________________________________________________________________
# | chkrom.py - Check and possibly correct the Amiga ROM check sum etc.        |
# | Author: Skywalker a.k.a. J.Karlsson <j.karlsson@retrocoder.se>             |
# | Copyright (C) 2019 Skywalker. All rights reserved.                         |
# |____________________________________________________________________________|

import sys
import os
import argparse
import struct

if __name__ == "__main__":
  print("Amiga ROM checksum calculator")
  script_name = os.path.basename(sys.argv[0])
  parser = argparse.ArgumentParser(script_name)
  parser.add_argument("file", action="store", help="File to calculate checksum on")
  parser.add_argument("--extend", "-x", action="store_true", help="Fix length error by extending file to whole 32 bit words")
  parser.add_argument("--fix", "-f", action="store_true", help="Fix checksum error (Warning: will overwrite input file if no output file is specified)")
  parser.add_argument("--output", "-o", action="store", help="Output file name (Default: input file)")

  args = parser.parse_args()
  file_content = []
  sum = 0
  with open(args.file, "rb") as f:
    flen = os.path.getsize(args.file)

    while True:
      data = f.read(4)
      if not data: break
      value = struct.unpack(">I", data)[0]
      file_content.append(value)
      sum += value
      if sum >= pow(2, 32):
        sum -= pow(2,32)-1

  # Check ROM magic id
  magic = (file_content[0] >> 16)

    # Check file length
  dword_aligned = (flen % 4) == 0
  rom256k_aligned = (flen % pow(2, 18)) == 0
  kb_aligned = (flen % pow(2, 10)) == 0
  
  flen_index = int(flen/4 - 5)
  stored_len = file_content[flen_index]

  if not kb_aligned:
    print(f"Found file \"{args.file}\", length {flen} bytes")
  else:
    print(f"Found file \"{args.file}\", length {int(flen/1024)} kb")
  print(f"Magic id: 0x{magic:04X}")

  if magic != 0x1111 and magic != 0x1114:
    print("Warning: Unrecognized magic id: 0x{magic:X}")

  if magic == 0x1111 and flen != pow(2,18):
    print("Warning: File length does not match magic id: 0x{magic:X}")
  
  if magic == 0x1114 and flen != pow(2,19):
    print("Warning: File length does not match magic id: 0x{magic:X}")

  if not dword_aligned:
    print("Error: File length is not whole 32 bit words. Use option --extend to fix length error")
    
  if stored_len != flen:
    print("Error: File length does not match stored length. Use option --extend to fix length error")

  if not rom256k_aligned:
    print("Warning: File has unusual length, not evenly divisable by 256 kb")

  # Check sum
  res = "ok"
  if sum != pow(2, 32)-1:
    res = "incorrect"
  print(f"Checksum {res} (0x{(~sum)%(pow(2,32)):X})")

  err = (pow(2,32) - 1) - sum
  if err != 0:
    sum += err
    print(f"Err = 0x{err:X}, new checksum = 0x{sum:X}")

  file_changed = False
  output_file = args.output if args.output is not None else args.file

  if not dword_aligned and args.extend:
    file_content.extend([4-(flen % 4)])
    flen = len(file_content)
    file_changed = True

  if err != 0 and args.fix:
    if not dword_aligned and not args.extend:
      print("Error: cannot fix checksum, wrong file length")
      exit(-1)
    chksum_index = int(flen/4 - 6)
    chksum = file_content[chksum_index]
    chksum += err
    if chksum > pow(2,32):
      chksum -= pow(2,32) - 1
    file_content[chksum_index] = chksum
    file_changed = True
    print(f"Correction dword: 0x{file_content[chksum_index]:X}")
    
  # Write output file
  if file_changed:
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
