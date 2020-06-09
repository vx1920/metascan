# ----------------------------------------------------------------------
# Read Anaconda metadata to find Anaconda-installed packages
# ----------------------------------------------------------------------
import sys, os

# there are case and minus/underscore mismatces in metadata vs real package names,
# so translation done before place to dictionary and check if exist 
def rdCndNormalName(sName) :
  return sName.lower().replace("-" , "_")


def rdCndAddToDict(dct, sNameVers) :
 lsSplit = sNameVers.split('-')
 if len(lsSplit) < 3:
   return

 sChannel = lsSplit.pop()
 sVers = lsSplit.pop() 

 # if name-vers were splitted, join it back
 sName = '-'.join(lsSplit) if len(lsSplit) > 1 else lsSplit[0]
 sFullVers = '-'.join([sVers, sChannel])
 dct[ rdCndNormalName(sName) ] = sFullVers
# end


def rdCndIsNameIn(dct, sName) :
  return True if rdCndNormalName(sName) in dct else False 


def rdCndScanForFiles(sPath, sExt) :
  dct = {} # new empty dictionary
  if (not os.path.isdir(sPath)) :
    #print("Folder not found:" , sPath)
    return dct   

  with os.scandir(sPath) as st_dir:
    for itm in st_dir:
      if itm.is_file() :
        sName = itm.name
        if sName.casefold().endswith(sExt) :
           nLen = len(sName) - len(sExt)
           if sExt[0] != '.' :
             nLen -= 1
           sName = sName[0 : nLen]  # remove .extension
           ##print("ForFile: " , sName)
           rdCndAddToDict(dct, sName)
  # end with

  return dct
# end dctDirScanForFile()


def rdCndGetNames() :
  sPath = os.path.join(sys.prefix, "conda-meta")  
  return rdCndScanForFiles(sPath, "json")


if __name__ == '__main__':
  print("rdcndmet: Anaconda package names from metadata")
  dct = rdCndGetNames()
  for sKey, sVal in dct.items():
    print("%s : %s" % (sKey, sVal))

# eof