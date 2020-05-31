# ----------------------------------------------
# scan Anaconda/Python metadata for possible version mismatch problems
# Scan Version 0.0:
# only file/folders namets are processed (no any look inside files/folders)
# Prefix\Lib\site-packages names of *dist-info and *egg-info folders
# For Anaconda:
# Prefix\conda-meta - names of *.json files
# Prefix\pkgs - names of the folders
# There are no any attempts to repair, just read-only access. 
# ----------------------------------------------
import sys, os

# name of folder from lib\site-packages
# folders  
def metaDirSitePackages(lsTable, sDirName, sType) :
  # print("Dir : " , sDirName)
  lsSplit = sDirName.split('-')
  if lsSplit[-1] != "info" : 
     return

  # at the end of folders with metadata: either 'egg-info' or 'dist-info'
  # We have split by '-', so we always have "info" at the end and
  # ignore any other folder names

  lsSplit.pop(); # remove last item, which is always "info"

  arrVers = lsSplit.pop().split('.') # [VersItems , ('dist' or 'egg')] removed and returned
  sTail = arrVers.pop() # 'dist' or 'egg' from the end removed and returned to sTail
  sVers = '.'.join(arrVers)

  # different format for dist/egg
  # dist: only name sSplit[0], sVers is package version
  # egg: name in [0], version in [1], but in sVers we actually have splitted  channel name
  lsSplit.append(sVers)
  lsSplit.append(sTail + "-info")  # "dist-info" or "egg-info" postfix restore
  lsSplit.append(sType) 

  lsTable.append(lsSplit)
  # each row in lsTable is list with Name,Vers,.....,Info (strings)
  return
# end metaDirSitePackages


# scan folder for folder names
def metaDirScanForDir(lsTable, sPath, pfDoName, sType) :
  if (not os.path.isdir(sPath)) :
    print("Folder not found:" , sPath)
    return    

  with os.scandir(sPath) as st_dir :
    for itm in st_dir:
      if itm.is_dir() :
        pfDoName(lsTable, itm.name, sType)
# end metaDirScanForDir()


def metaDirScanForFile(lsTable, sPath, sExt, pfDoName, sType) :
  if (not os.path.isdir(sPath)) :
    print("Folder not found:" , sPath)
    return    

  with os.scandir(sPath) as st_dir:
    for itm in st_dir:
      if itm.is_file() :
        sName = itm.name
        if sName.casefold().endswith(sExt) :
           nLen = len(sName) - len(sExt)
           if sExt[0] != '.' :
             nLen -= 1
           sName = sName[0 : nLen]  # remove extension
           ##print("ForFile: " , sName)
           pfDoName(lsTable, sName, sType)
  # end with
# end metaDirScanForFile()



def metaDirPkgs(lsTable, sDirName, sType) :
 lsSplit = sDirName.split('-')
 #print(lsSplit) 
 if len(lsSplit) < 3:
   return

 sChannel = lsSplit.pop()
 sVers = lsSplit.pop() 

 # if name has '-' inside - it was splitted, join it back
 sName = '-'.join(lsSplit) if len(lsSplit) > 1 else lsSplit[0]
 
 lsSplit = [sName , sVers, sChannel, sType]
 lsTable.append(lsSplit)
# end


# return standard name for comparing from string in [0]
# package name with possible '-' inside name to '_', problem solved here:
# in conda-meta we have "anaconda-project", but in site-packages "anaconda_project"
# (same for other names).
# Minus translated to underscore for names in Lib\site-packages folder
# it is used not only as sorting key, but for compare also, see metaProcessTable
def metaGetKey(lsRow) :
  return lsRow[0].lower().replace("-" , "_")



# lsTable is list of rows
# row in lsTable list is also list, but with strings
# row[0] - package name
# row[1] - package version
# next is optional: channel name, only in Anaconda
# row[-1] - location code of the metadata at the end of row: LibSP, conda-meta, pkgs
def metaProcessTable(lsTable) :
  # sorting by case-insensitive package name: 
  #lsTable.sort(key = lambda arg: arg[0].casefold())
  lsTable.sort(key = metaGetKey)


  #print("Table:")
  #for lsRow in lsTable :
  #  print(lsRow)

  nCnt = len(lsTable) # rows in table
  nCnt -= 1 # see [idx+1] first if below
  nErrCnt = 0

  idx = 1
  while (idx < nCnt) :
    if metaGetKey(lsTable[idx]) != metaGetKey(lsTable[idx+1]) :
       idx += 1
       continue

    nSame = 2;
    while (idx + nSame <= nCnt) : 
      if metaGetKey(lsTable[idx]) == metaGetKey(lsTable[idx+nSame]) :
        nSame += 1
      else :
        break
 
    # check version in [1] for nSame items with same name in [0]    
    ism = 1
    while (ism < nSame) :
      if lsTable[idx][1].lower() == lsTable[idx+ism][1].lower() :
        ism += 1
      else :
        break

    if (ism < nSame) :   # versions are not the same
      nErrCnt += 1
      print("Version Mix:")
      for ism in range(idx, idx+nSame) :
         print (" " , lsTable[ism] )
       
    idx += nSame
  # end while(idx)


  if (nErrCnt > 0) :
    print("Version mix in metadata for" , nErrCnt, "package(s)")
  else :
    print("No version mixes found")
# end metaProcessTable()    



def metaProcessPrefix(sPref, bPkgs) :
  print(" --- Scan metadata for version mismatch ---\nPrefix:" , sPref)
  lsTable = []

  if (not os.path.isdir(sPref)) :
    print("Python prefix path not found:" , sPref)
    return    

  # folder available in both: Anaconda and pure python 
  sDir = "LibSP" 
  sPath = os.path.join(sPref, "Lib", "site-packages")  
  print(sDir, ":" , sPath)
  metaDirScanForDir(lsTable, sPath, metaDirSitePackages, sDir)
 
  # next two folders exixts in Anaconda, not in pure Python
  sDir = "conda-meta"
  sPath = os.path.join(sPref, sDir)  
  print(sDir, ":" , sPath)
  metaDirScanForFile(lsTable, sPath, "json", metaDirPkgs, sDir)

  # No need to scan 'pkgs' folder and also don't try to remove items there:
  # if "conda environment" for different package version created,
  # "hardlinks" are used inside actual "site-packages" folders.
  # Links are also used even nothing but single "base environment" exists.
  # Be careful, but code below can be uncommented, since it is all-read-only
  # (along with all code here).  
  
  if bPkgs :
    sDir = "pkgs"
    sPath = os.path.join(sPref, sDir)  
    print(sDir, " :" , sPath)
    metaDirScanForDir(lsTable, sPath, metaDirPkgs, sDir)

  # search for version mismatches:
  metaProcessTable(lsTable)
# end metaProcessPrefix()



if __name__ == '__main__':
  sPref = sys.prefix
  bPkgs = False
  nArgCnt = len(sys.argv)

  if nArgCnt >= 2 : 
    for idx in range(1, nArgCnt) :
      if (sys.argv[idx][0] == '-') :
        if (len(sys.argv[idx]) >= 2) : # at least one character after '-'
          if (sys.argv[idx][1] == 'p') :
            bPkgs = True
      else :
        # no minus, the only positional argument for now   
        sPref = sys.argv[idx]

  metaProcessPrefix(sPref, bPkgs)

# eof