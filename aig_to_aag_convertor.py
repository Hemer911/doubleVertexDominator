import os
from os import listdir
# from os.path import isfile, join
from subprocess import call
if __name__ == "__main__":
    databasePath = "hwmcc20/aig/2019/beem/"
    for fileFullName in listdir(databasePath):
        filename, file_extension = os.path.splitext(fileFullName)
        if file_extension == "aag" : continue
        if filename + ".aag" in listdir(databasePath): continue
        print("converting " + filename + ":")
        call(['./aigtoaig',databasePath+filename+".aig",databasePath+filename+".aag"])