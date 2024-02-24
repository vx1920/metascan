# ----------------------------------------------------------------------------------
# Scan Anaconda/Python metadata for possible module/version
# mismatch or duplication problems
# Search for names taking place in sys.path folders.
# For Windows Anaconda (if folders folders below are found in prefix):
# -- Prefix\conda-meta - names of *.json files
# -- Prefix\pkgs - names of the folders
# There are no any attempts to repair: just read-only access and report problems. 
# Simple check of file/folder name/version info from file/folder names.
# Only file/folders names are processed (no any look "inside")
# ---------------------------------------------------------------------------------
import sys, os

class CPtnMetaInfo :
  # class level variables (here: used as constants)
  sMetascanVersion = "0.0.2"
  sExtEggInfo  = "egg-info"
  sExtDistInfo = "dist-info"
  sTypeFile    = "FILE"
  sTypeFolder  = "FLDR"


  def __init__(self):
    self.lsFolders = []   # string array, item is full path to folder 
    self.lsTable   = []   # item: [ModuleName, Version , FullMetaInfo, FolderIndxInAbove]
    self.lsPosArgs = []   # array of positional arguments (no -)
    self.bPkgs = False
    self.bDetails  = False
    self.bDebugDump = False 
    self.sPref = ""
    self.sCurrDir = ""
    self.sFindMod = ""
    self.nErrCnt  = 0
    self.useMethod = None 
  # end __init__()


  def baseName(sName, sExt) :
    nLen = len(sName) - len(sExt)
    return sName[0 : nLen]  # name only


  # decode directory element type
  def dirItmType(self, dirItm) :
    sType = ""
    if dirItm.is_file() :
      sType = CPtnMetaInfo.sTypeFile
    if dirItm.is_dir() :
      sType = CPtnMetaInfo.sTypeFolder
    return sType


  # callback for name of folder/file from lib\site-packages and others:
  # "ModName-Version.dist-info" OR  "ModName-Version-Channel.egg-info" 
  # (-Channel is optional)  
  def doDirSitePackages(self, dirItm, nIdx) :
    #if not dirItm.is_dir() : # skip non-folder items
    #  return 0
    # above commented to allow scan files with .egg-info / .dist-info extensions

    sType = self.dirItmType(dirItm)
    sName = dirItm.name   # original name of file or folder
    # print("Dir : " , sDirName)
    sNormName = sName.casefold()
    lsSplit = sNormName.split('.')
    if len(lsSplit) < 2:
      return 0

    sExt = lsSplit.pop() # may have here ".egg-info" or ".dist-info" or smth else        
    if (sExt != CPtnMetaInfo.sExtDistInfo) and (sExt != CPtnMetaInfo.sExtEggInfo) :
      return 0 # ignore all folders other than (.egg | .dist) -info 

    sFolderName = '.'.join(lsSplit)  # no more ".extension" at the end, other dots restored
    # package name may have '-' (minus) inside name, but in egg/dist metadata folder
    # all these minuses in module name will be replaced with underscores.
    # Actual package name is available somewhere inside egg/dist folder,
    # see details in pip-list / conda-list 
    # In metadata folder name '-' (minus) treated strictly as separator (? is it true ?)
    lsSplit = sFolderName.split('-')
    if len(lsSplit) < 2:  # just name.dist_info, not name-vers.dist_info
      sModuleName = sFolderName
      sVers       = "0"
    else:
      sModuleName = lsSplit[0]
      sVers       = lsSplit[1]

    if (len(sVers) == 0) or (len(sModuleName) == 0): # egg/dist bad name
      print("ErrEmpty: Ver=<%s> Mod=<%s> Dir=<%s>" %
            (sVers, sModuleName, sDirName) )
      return 0

    # re-join possible parts of the name if it has '-' inside 
    # sModuleName = '-'.join(lsSplit) if len(lsSplit) > 1 else lsSplit[0]
    # ^^^ actually it never happen: minus in name will be replaced with inderscore 
    # in egg/dist folder name, pip/conda both are doing it
    self.lsTable.append([sModuleName, sVers, sName, sType, nIdx] )
    return 1
  # end metaDirSitePackages()


  # callback for processing Anaconda\pkgs folder items
  def doDirCondaPkgs(self, dirItm, nIdx) :
    if not dirItm.is_dir() : # skip non-folder items
      return 0

    sDirName = dirItm.name
    lsSplit = sDirName.split('-')
    #print(lsSplit) 
    if len(lsSplit) < 3:
      return 0

    sChannel = lsSplit.pop()
    sVers = lsSplit.pop() 

    # if name has '-' inside - it was splitted, join it back
    sName = '-'.join(lsSplit) if len(lsSplit) > 1 else lsSplit[0]
    self.lsTable.append( [sName , sVers, sDirName, CPtnMetaInfo.sTypeFolder, nIdx] )
    return 1
  # end doDirCondaPkgs()


  # callback for processing Anaconda\conda-meta folder items:
  # PackageName-Version-Hash.json files 
  def doDirCondaMeta(self, dirItm, nIdx) :
    if not dirItm.is_file() : # skip non-folder items
      return 0

    sFileName = dirItm.name
    #print("metaDirCondaMeta: [%d] %s" % (nIdx, sFileName))
    sExt = ".json"
    sName = sFileName.casefold()
    if not sName.endswith(sExt) :
      return  0 # just skip non .json files

    nLen = len(sName) - len(sExt)
    sName = sName[0 : nLen]  # normalized Name-Vers-Hash

    lsSplit = sName.split('-')
    lsSplit.pop()  # remove Hash from "Name-Version-Hash"
    sVers = lsSplit.pop() # remove and keep version 
    # Name may have '-' inside, so it was splitted, join it back conditionally
    sName = '-'.join(lsSplit) if len(lsSplit) > 1 else lsSplit[0]

    #print("metaDirCondaMeta: [%d] Name=[%s] Vers=[%s]" % (nIdx, sName, sVers))
    self.lsTable.append([sName, sVers, sFileName, CPtnMetaInfo.sTypeFile, nIdx] )
    return 1
  # end doDirCondaMeta()


  def doDirSameNames(self, dirItm, nIdx) :
    sType = self.dirItmType(dirItm)
    sName = dirItm.name
    self.lsTable.append( [sName, sType, nIdx] )
    return 1


  def addPathFolder(self, sPath) :
    nIdx = len(self.lsFolders)
    self.lsFolders.append(sPath)
    if self.bDetails :
      print("[%d] %s" % (nIdx, sPath))


  # general scan of some folder for any items: folder or file
  def metaDirScan(self, sPath, pfDoItem) :
    if (not os.path.isdir(sPath)) :
      #print("Folder not found:" , sPath)
      return     

    self.sCurrDir = sPath
    nIdx = len(self.lsFolders) # sPath folder index if it will be added
    nCnt = 0 # how many folders was processed properly
    with os.scandir(sPath) as st_dir :
      for itm in st_dir:
        nCnt += pfDoItem(self, itm, nIdx)

    if nCnt > 0 : # at least one item from this path added to the table
      self.addPathFolder(sPath)
  # end metaDirScan()


  def dumpTable(self, sTitle) :
    print("--- Dump metadata: %s ---" % (sTitle))
    for lsRow in self.lsTable :
      print(lsRow)
    print("--- End of dump: %s ---" % (sTitle))


  def printMixInfo(self, idx , nSame) :
    print("--- Version Mix for <%s>:" % (self.lsTable[idx][0]))
    # starting [nIdx] we have nSame items
    # first we sort self.lsTable it in-place by version
    # In each element: name [0], version in [1],
    # sort mixed elements by version before printing
    mixes = sorted(self.lsTable[idx : idx + nSame], reverse = True, key = lambda z: z[1])
    #print("MixSorted:" , mixes) 
    for itm in mixes:
      print("%s: %s" %
         (itm[3], os.path.join(self.lsFolders[ itm[4] ] , itm[2])) )
    self.nErrCnt += 1
  # end printMixInfo()


  # key-callback for lsTable sorting, list item passed here as an argument. 
  # Function returns 'standard/normalized' name of module for comparing.
  # Package name may have possible '-' (minus) inside name, while 
  # in some file/filder names it is replaced with '_' (underscore).
  def tableGetNKey(lsTableItem) :
    # lsTable item itself is also list with name in [0]
    return lsTableItem[0].casefold().replace("-" , "_")


  # Above tableGetNKey() is static function defined inside class, it does not have self
  # as an argument in definition.
  # Class name should be used instead of self to call this method, see examples below:
  def tableNKey(self, idx) :
    return CPtnMetaInfo.tableGetNKey(self.lsTable[idx])


  # Sorting will place same name modules together.
  # Normalized module name will be used for sorting key.
  def tableSortByModuleName(self) :
    self.lsTable.sort(key = CPtnMetaInfo.tableGetNKey)
    # simpler variant can be: self.lsTable.sort(key = lambda arg: arg[0].casefold())
    # but it will not cover minus/underscore equality as in 


  def tableMVers(self, idx) :
    sVers = self.lsTable[idx][1] # string with module version 
    return sVers.casefold()      # normalized lower case for comparison


  def countDistEgg(self, ii) : # inner function to play with above variables
    if self.lsTable[ii][2].endswith(CPtnMetaInfo.sExtEggInfo) :
      self.nEggInfo += 1
    if self.lsTable[ii][2].endswith(CPtnMetaInfo.sExtDistInfo) :
      self.nDistInfo += 1

  def metaProcessTable(self) :
    print("--- Scan metadata for version mismatch ---")
    self.tableSortByModuleName()
    if self.bDebugDump:
      self.dumpTable("Sorted Table")
    #return

    nCnt = len(self.lsTable) # rows in table
    nCnt -= 1 # comparison will take place for current and next element
    self.nErrCnt = 0
    idx = 0
    while (idx < nCnt) :
      if self.tableNKey(idx) != self.tableNKey(idx + 1) :
        idx += 1
        continue

      nSame = 2; # at least two same name items found, maybe we have more
      self.nDistInfo = 0
      self.nEggInfo  = 0
      self.countDistEgg(idx)
      self.countDistEgg(idx+1)

      while (idx + nSame <= nCnt) : 
        if (self.tableNKey(idx) == self.tableNKey(idx + nSame)) :
          self.countDistEgg(idx+nSame)
          nSame += 1
        else :
          break
 
      # complete same module name sequence found,
      # check do all of them have same version:
      ism = 1
      while (ism < nSame) :
        if self.tableMVers(idx) == self.tableMVers(idx + ism) :
          ism += 1
        else :  # version mismatch in same name module metadata items found
          break

      # if some module has both EggInfo and DistInfo: it is bad even versions are same:
      if (self.nDistInfo > 0 and self.nEggInfo > 0):
        ism = 1  # force report 

      if (ism < nSame):   # report version mix
        self.printMixInfo(idx, nSame)
     
      idx += nSame
    # end while(idx < nCnt) - entire table processing

    if (self.nErrCnt > 0) :
      print("--- Version mix in metadata for" , self.nErrCnt, "package(s)")
    else :
      print("--- No version mixes found")
  # end metaProcessTable()    


  # scan folders in sys.path, available in both: Anaconda and regular Python 
  def metaDirScanSysPath(self, pfDoItem) :
    for sPath in sys.path :
      self.metaDirScan(sPath, pfDoItem)


  def metaProcessVersionMix(self) :
    self.metaDirScanSysPath(CPtnMetaInfo.doDirSitePackages)
 
    # next two folders exixts in Anaconda, not in pure Python
    # metaDirScan safely doing nothing if no sPath folder found
    # It is the case when we have regular Python, not Anaconda
    sDir = "conda-meta"
    sPath = os.path.join(self.sPref, sDir)  
    self.metaDirScan(sPath, CPtnMetaInfo.doDirCondaMeta)

    # No need to scan 'pkgs' folder and also never try to remove items there:
    # "conda environment" for different package version creates
    # "links" (hard?) which are used inside actual "site-packages" folders.
    # Different environments may use different package versions, so
    # "version mix" can be legitimate.
    # Links are used even nothing but single "base environment" exists.
    # Normally unused items in pkgs can be removed by "conda clean --all",
    # so this folder included only into scan only optionally.
    if self.bPkgs :
      sDir  = "pkgs"
      sPath = os.path.join(self.sPref, sDir)  
      self.metaDirScan(sPath, CPtnMetaInfo.doDirCondaPkgs)

    # search for version mismatches:
    self.metaProcessTable()
  # end metaProcessVersionMix()


  # starting [nIdx] we have nSame items
  def printSameNames(self, idx , nSame) :
    print("--- Same name items <%s>:" % (self.lsTable[idx][0]))
    for ism in range(idx, idx + nSame) :
      itm = self.lsTable[ism]
      #print(itm)
      sPathName = os.path.join(self.lsFolders[ itm[2] ] , itm[0])
      print("%s: %s" % (itm[1] , sPathName) )
    self.nErrCnt += 1


  def metaProcessSameNames(self) :
    #print("--- metaProcessSameNames")
    self.metaDirScanSysPath(CPtnMetaInfo.doDirSameNames)
    self.tableSortByModuleName()
    #self.dumpTable("Sorted Table - metaProcessSameName")

    # dump same names from sorted table:
    nCnt = len(self.lsTable) # rows in table
    nCnt -= 1 # comparison will take place for current and next element
    self.nErrCnt = 0
    idx = 1
    while (idx < nCnt) :
      if self.tableNKey(idx) != self.tableNKey(idx + 1) :
        idx += 1
        continue

      nSame = 2 # at least two same name items found, maybe we have more
      while (self.tableNKey(idx + nSame - 1) == self.tableNKey(idx + nSame)) : 
        nSame += 1

      self.printSameNames(idx, nSame)
      idx += nSame
    # end while(idx < nCnt)
  # end metaProcessSameNames


  def doDirFindModule(self, dirItm, nIdx) :
    sName = dirItm.name
    if not sName.casefold().startswith(self.sFindMod) :
       return 0

    # name match:
    sType = self.dirItmType(dirItm)
    print("%s: %s" % (sType, os.path.join(self.sCurrDir, sName)) )
    return 0
  # end doDirFindModule()


  def metaProcessFindModule(self) :
    if len(self.lsPosArgs) < 2 :
      print("fnd: no search argument") 
      return

    self.sFindMod = self.lsPosArgs[1].casefold()
    self.metaDirScanSysPath(CPtnMetaInfo.doDirFindModule)
    return
  # end metaProcessFindModule()


  def metaSetupSmbFlag(self, cSmb) :
    cSmb = cSmb.lower()
    if (cSmb == 'p') :
      self.bPkgs = True
    elif (cSmb == 'v') :
      self.bDetails = True 
    elif (cSmb == 'd') :
      self.bDebugDump = True 
  # end metaSetupSmbFlag()


  def metaSetupArg(self, sArg) :
    nLng = len(sArg)
    if (sArg[0] != '-'):
      self.lsPosArgs.append(sArg)
      return

    if (sArg[0] == '-') and (nLng >= 2) :
      # ensured at least one character after '-', check it:
      for idx in range(1, nLng) : # use range(1,) to skip arrArg[0]
        self.metaSetupSmbFlag(sArg[idx])
  # end metaSetupArg()


  # More class level variables. 
  # There is no switch in Python, so name-to-function map will be used.
  # Member functions have to be already defined to add it
  # to the map and also class name qualifier not needed
  # (it will be undefined class name err if try to use it)
  mapSwitchFunc = {
    "mix" : metaProcessVersionMix,
    "sim" : metaProcessSameNames,
    "fnd" : metaProcessFindModule,
  }


  def metaSetup(self, arrArgs) :
    self.lsPosArgs = []
    self.bPkgs = False
    self.useMethod = CPtnMetaInfo.metaProcessVersionMix
    nArgCnt = len(arrArgs)
    if nArgCnt >= 2 : 
      for idx in range(1, nArgCnt) : # use range(1,) to skip arrArg[0]
        self.metaSetupArg(arrArgs[idx])

    # process positional arguments (no -) 
    # print("PosArgs:" , self.lsPosArgs) 
    if len(self.lsPosArgs) > 0 :
      self.useMethod = CPtnMetaInfo.mapSwitchFunc.get(
              self.lsPosArgs[0].casefold())

    #print("Method OK" if self.useMethod else "No method")
  # end metaSetup()


  def metaProcess(self) :
    if not self.useMethod :
      print("Invalid subcommand:" , self.lsPosArgs,
            "\nUse:  mix / sim / fnd name")
      return

    self.sPref = sys.prefix
    print("--- metascan version %s for prefix: %s" %
          (CPtnMetaInfo.sMetascanVersion, self.sPref)) 

    if (not os.path.isdir(self.sPref)) :
      print("Python prefix path not found:" , self.sPref)
      return    

    # self.useMethod from mapSwitchFunc is OK, call it
    self.useMethod(self)
  # end metaProcess()
# end class CPtnMetaInfo


def MyMain(arrArgs) :
  obj = CPtnMetaInfo()
  obj.metaSetup(arrArgs)
  obj.metaProcess()
# end MyMain()


if __name__ == '__main__' :
  MyMain(sys.argv)

# eof