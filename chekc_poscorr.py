#!/usr/bin/python3
import subprocess
import sys 

NIUPOS = "/dat/pysimrelease/pysim-5.0.0/tools/niupos_2004"

niopaths = sys.argv[1:]

for niopath in niopaths:
    cmd = f"{NIUPOS} {niopath} /dat/usercache/xiongzhang/projects/SubmissionCheck_workspace/Nio/* | sort -nr"
    print("-"*5, niopath, "-"*5)
    print(subprocess.getoutput(cmd))
