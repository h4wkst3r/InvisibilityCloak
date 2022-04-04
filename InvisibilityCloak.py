#!/usr/bin/env python3
"""
SYNOPSIS

	InvisibilityCloak [-h, --help] [--version] [-m, --method] [-d, --directory] [-n, --name]

DESCRIPTION

	C# Tool Obfuscator

SUPPORTED OBFUSCATION METHODS

	base64 - Base64 encode all strings within project and have them decoded at runtime
	rot13 - Rotate each character in string by 13
	reverse - Reverse all strings within project and have them re-reversed at runtime
	

EXAMPLES

        ==Run InvisibilityCloak with string obfuscation==
        
	InvisibilityCloak.py -d C:\path\\to\project -n "TotallyLegitTool" -m base64
	InvisibilityCloak.py -d C:\path\\to\project -n "TotallyLegitTool" -m rot13
	InvisibilityCloak.py -d C:\path\\to\project -n "TotallyLegitTool" -m reverse


	==Run InvisibilityCloak without string obfuscation==
	
	InvisibilityCloak.py -d C:\path\\to\project -n "TotallyLegitTool"


AUTHOR

	Brett Hawkins (@h4wkst3r)

LICENSE

	Apache 2.0 License
	http://www.apache.org/licenses/LICENSE-2.0

VERSION

	0.3

"""

import sys, os, traceback, optparse, re, base64, uuid, codecs
from shutil import copyfile


# method to generate a new project GUID
def replaceGUIDAndToolName(theDirectory, theName):

	print("")
	print("[*] INFO: Generating new GUID for C# project")

	# generate a new GUID
	newGUID = str(uuid.uuid4())
	print("[*] INFO: New project GUID is " + newGUID)

	slnFile = ""
	csProjFile = ""
	global currentToolName
	currentToolName = ""
	assemblyInfoFile = ""
	csProjFileCount =0
	
	# iterate through the project to find the VS solution file and the C# project file. also grab the path to assembly info file
	for r, d, f in os.walk(theDirectory):
		for file in f:
			if file.endswith(".sln"):
				slnFile = os.path.join(r,file)
				currentToolName = file
			elif file.endswith(".csproj"):
				csProjFile = os.path.join(r,file)
				csProjFileCount += 1
			elif "AssemblyInfo.cs" in file:
				assemblyInfoFile = os.path.join(r,file)

	# if there is more than 1 C# project in the directory, display message and exit
	if csProjFileCount > 1:
		print("")
		print("[-] ERROR: Currently this tool only supports having one C# project file to modify. The project directory you provided has " + str(csProjFileCount))
		print("")
		sys.exit(0)

	print("[*] INFO: Changing C# project GUID in below files:")
	print("")
	print(slnFile)
	print(csProjFile)
	print (assemblyInfoFile)
	print("")

	# capture current tool name based on VS sln file name
	currentToolName = currentToolName.replace(".sln", "")

	# initialize this to random sha256 hash so there is no match initially (sha256 hash of "test")
	currentGUID = "f2ca1bb6c7e907d06dafe4687e579fce76b37e4e93b7605022da52e6ccc26fd2"

	# change the GUID and tool name in the sln file
	copyfile(slnFile,slnFile + "_copy")
	openSLNFile = open(slnFile, 'r')
	openCopySLNFile = open(slnFile + "_copy", "w")
	slnLines = openSLNFile.readlines()
	for line in slnLines:

		# if it is the line that defines project files, then get current guid and tool name and replace
		if "Project(" in line:
			lineSplit =  line.split(", ")
			currentGUID = lineSplit[2].replace("\"","").strip()
			line = line.replace(currentGUID, "{" + newGUID + "}")
			line = line.replace(currentToolName, theName)
			openCopySLNFile.write(line)

		# if the current guid is present, then replace it with the new guid
		elif currentGUID in line:
			line = line.replace(currentGUID, "{" + newGUID + "}")
			openCopySLNFile.write(line)

		# if it is a line that does not contain the current guid, then leave line alone
		else:
			openCopySLNFile.write(line)

	openSLNFile.close()
	openCopySLNFile.close()
	os.remove(slnFile)
	os.rename(slnFile + "_copy",slnFile)


	# change the GUID and tool name in the C# proj file
	copyfile(csProjFile,csProjFile + "_copy")
	openCSProjFile = open(csProjFile, 'r')
	openCopyCSProjFile = open(csProjFile + "_copy", "w")
	csProjLines = openCSProjFile.readlines()
	
	print("")
	print("[*] INFO: Removing PDB string in C# project file")
	print("")
	for line in csProjLines:

		# if the line has the current tool name or old guid, then replace it
		line = line.replace(currentGUID, "{" + newGUID + "}")

		# replace any line in C# project file that has old tool name, except for nuget package reference or references to application icons
		if "<PackageReference Include=" not in line and "<ApplicationIcon>" not in line:
                        line = re.sub('(?i)'+re.escape(currentToolName), lambda m: theName, line)

                # remove the pdb string options from C# project file
		line = line.replace("<DebugType>pdbonly</DebugType>","<DebugType>none</DebugType>")
		line = line.replace("<DebugType>full</DebugType>","<DebugType>none</DebugType>")
		openCopyCSProjFile.write(line)

	openCSProjFile.close()
	openCopyCSProjFile.close()
	os.remove(csProjFile)
	os.rename(csProjFile + "_copy",csProjFile)


	# change the info in the assemblyinfo file for the tool that will be compiled to be new tool name
	if os.path.exists(assemblyInfoFile):
		copyfile(assemblyInfoFile,assemblyInfoFile + "_copy")
		openAssemblyInfoFile = open(assemblyInfoFile, 'r')
		openCopyAssemblyInfoFile = open(assemblyInfoFile + "_copy", "w")
		assemblyInfLines = openAssemblyInfoFile.readlines()
		for line in assemblyInfLines:
			line = line.replace(currentToolName, theName)
			tempGUID = currentGUID
			tempGUID = tempGUID.replace("{","")
			tempGUID = tempGUID.replace("}","")
			tempGUID = tempGUID.lower()
			line = line.replace(tempGUID, newGUID)
			openCopyAssemblyInfoFile.write(line)

		openAssemblyInfoFile.close()
		openCopyAssemblyInfoFile.close()
		os.remove(assemblyInfoFile)
		os.rename(assemblyInfoFile + "_copy",assemblyInfoFile)


	# rename any directories of files of the current tool name with new one
	for r, d, f in os.walk(theDirectory):
		for file in f:
			if file == currentToolName + ".sln":
				print("[*] INFO: Renaming " + currentToolName + ".sln to " + theName + ".sln")
				theFile = os.path.join(r,file)
				newFile = theFile.replace(currentToolName + ".sln", theName + ".sln")
				os.rename(theFile, newFile)
			elif file == currentToolName + ".csproj":
				print("[*] INFO: Renaming " + currentToolName + ".csproj to " + theName + ".csproj")
				theFile = os.path.join(r,file)
				newFile = theFile.replace(currentToolName + ".csproj", theName + ".csproj")
				os.rename(theFile,newFile)
			elif currentToolName in file and file.endswith(".cs"):
				theFile = os.path.join(r,file)
				newFile = file.replace(currentToolName, theName)
				newFullFile = theFile.replace(file, newFile)
				print("[*] INFO: Renaming " + theFile + " to " + newFullFile)
				os.rename(theFile,newFullFile)

	origWorkingDir = os.getcwd()
	os.chdir(theDirectory)
	if os.path.isfile(currentToolName) or os.path.exists(theDirectory + "\\" + currentToolName):
                os.rename(currentToolName, theName)
	os.chdir(origWorkingDir)

	print("")
	print("[+] SUCCESS: New GUID of " + newGUID + " was generated and replaced in your project")
	print("[+] SUCCESS: New tool name of " + theName + " was replaced in project")
	print("")


# method to reverse a given string
def reverseString(s): 
  str = "" 
  for i in s: 
    str = i + str
  return str


# method to determine if line is part of a method signature (can't have dynamic strings in method singature)
def isLineMethodSignature(theLine):
	if ("public" in theLine or "private" in theLine) and "string" in theLine and "=" in theLine and "(" in theLine and ")" in theLine:
		return 1
	else:
		return 0

# method to determine if ok to proceed with string obfuscation
def canProceedWithObfuscation(theLine, theItem):

	# only obfuscate string if greater than 2 chars
	if len(theItem) <= 2 :
		return 0
	# don't obfuscate string if using string interpolation
	elif "$\"" in theItem or "=$" in theLine or "= $" in theLine or "$@" in theLine or "String.Format(" in theLine or "string.Format(" in theLine:
		return 0
	# can't obfuscate case statements as they need to be static values
	elif theLine.strip().startswith("case") == 1:
		return 0
	# can't obfuscate const vars
	elif "const string " in theLine or "const static string" in theLine:
		return 0
	# can't obfuscate strings being compared with "is" as they must be static
	elif ("if(" in theLine or "if (" in theLine) and " is \"" in theLine:
		return 0
	# can't obfuscate strings in method signatures
	elif isLineMethodSignature(theLine) == 1:
		return 0 
	# obfuscating strings in regexes has been problematic
	elif "new Regex" in theLine or "Regex" in theLine:
		return 0
	# obfuscating unicode strings has been problematic
	elif "Encoding.Unicode.GetString" in theLine:
		return 0
	# obfuscating occurrence of this has been problematic
	elif "Encoding.ASCII.GetBytes" in theLine:
		return 0
	# can't obfuscate override strings
	elif "public override string" in theLine or "private override string" in theLine:
		return 0
	# don't obfuscate string that starts with or ends with '
	elif theItem.startswith("'") == 1 or theItem.endswith("'") == 1:
		return 0
	# random edge case issue with ""' in line
	elif "\"\"\'" in theLine:
		return 0
	# random edge case issue
	elif "+ @\"" in theLine or "+@\"" in theLine:
		return 0
	# random edge case issue (""" in the line)
	elif "\"\"\"" in theLine:
		return 0
	# random edge case issue ("" in the line)
	elif "\"\"" in theLine:
		return 0
	# random edge case issue (" => " in the line in switch statement)
	elif "\" => \"" in theLine or "\"=>\"" in theLine :
		return 0
	# random edge case issue (" at start of line and ending in "])). this indicates a command line switch that needs to be static
	elif theLine.strip().startswith("\"") == 1 and theLine.strip().endswith("\")]"):
		return 0
	# otherwise, it is ok to proceed with string obfuscation
	else:
		return 1


# method to obfuscate strings based on method entered by user
def stringObfuscate(theFile, theName, theObfMethod):

	if theObfMethod == "base64":
		print("[*] INFO: Performing base64 obfuscation on strings in " + theFile)

	if theObfMethod == "rot13":
		print("[*] INFO: Performing rot13 obfuscation on strings in " + theFile)

	if theObfMethod == "reverse":
		print("[*] INFO: Performing reverse obfuscation on strings in " + theFile)

	# make copy of source file that modifications will be written to
	copyfile(theFile,theFile + "_copy")
	fIn = open(theFile, 'r')
	fInCopy = open(theFile + "_copy", "w")
	
	index = -1
	theLines = fIn.readlines() # get all lines in the source code file

	# manipulate first line of the source code file as appropriate
	if theLines[0].startswith("#define") == 1:
		theLines[0] = theLines[0].replace("using System.Text;","")
		theLines[0] = theLines[0].replace("using System.Linq;","")
		theLines[0] = theLines[0].replace("using System;","")
		theLines[0] = theLines[0] + "\r\nusing System.Text;\r\nusing System.Linq;\r\nusing System;\r\n"
	elif theLines[0].startswith("#define") == 0:
		theLines[0] = theLines[0].replace("using System.Text;","")
		theLines[0] = theLines[0].replace("using System.Linq;","")
		theLines[0] = theLines[0].replace("using System;","")
		theLines[0] = "//start\r\nusing System.Text;\r\nusing System.Linq;\r\nusing System;\r\n" + theLines[0]

	# iterate through all of the lines in the source code file
	for line in theLines:
		index += 1
		stringsInLine = ""


		if "$\"" not in line and line.strip().startswith("[") == 0:
			strippedLine = line

			if index >= 2:
				if theLines[index-2].strip().startswith("[") == 0 and theLines[index-3].strip().startswith("[") == 0:
					substringCount = strippedLine.count("\\" + "\"")
			else:
				substringCount = strippedLine.count("\\" + "\"")
			

			# if the line has an embedded string (\"something\"), handle it
			if substringCount >= 2 and "@" not in strippedLine and "\"" + "\\\\" + "\"" not in strippedLine and "public override string" not in strippedLine and "\\\\" + "\"\"" not in strippedLine and "String.Format(" not in strippedLine and "string.Format(" not in strippedLine:
				strippedLine = strippedLine.replace("\\" + "\"", "++====THISGETSREPLACED====++")

			# find all strings in the line and add to an array
			stringsInLine = re.findall(r'"([^"]*)"', strippedLine)


		# if there are strings in the line, then replace them appropriately
		if len(stringsInLine) > 0:
			strippedLine = strippedLine.replace(currentToolName,theName) # replace occurrence of old tool name with new
			for theItem in stringsInLine:

				# determine whether can proceed with string obfuscation
				if canProceedWithObfuscation(line,theItem):
					theString = theItem

					# if string obfuscation method is base64
					if theObfMethod == "base64":
						base64EncodedString = base64.b64encode(theString.encode("utf-8"))
						theBase64String = str(base64EncodedString)
						theBase64String = theBase64String.replace("b'","")
						theBase64String = theBase64String.replace("'","")

						# if the line has escaped strings (e.g., \r, \t, etc.)
						if "\\r" in strippedLine or "\\n" in strippedLine or "\\t" in strippedLine or "\"" in strippedLine or "\'" in strippedLine:
							if "++====THISGETSREPLACED====++" in strippedLine:
								strippedLine = strippedLine.replace("++====THISGETSREPLACED====++","\\" + "\"") # remove placeholder strings
								strippedLine = strippedLine.replace("\"" + theString + "\"", "Encoding.UTF8.GetString(Convert.FromBase64String(@" + "\"" + theBase64String + "\"" + "))")
							else:
								strippedLine = strippedLine.replace("\"" + theString + "\"", "Encoding.UTF8.GetString(Convert.FromBase64String(" + "\"" + theBase64String + "\"" + "))")

							strippedLine = strippedLine.replace("@Encoding.UTF8.GetString(Convert.FromBase64String", "Encoding.UTF8.GetString(Convert.FromBase64String")
							strippedLine = strippedLine.replace("$Encoding.UTF8.GetString(Convert.FromBase64String", "Encoding.UTF8.GetString(Convert.FromBase64String")

						# if the line does not have escaped strings
						else:
							strippedLine = strippedLine.replace("++====THISGETSREPLACED====++","\\" + "\"") # remove placeholder strings
							strippedLine = strippedLine.replace("\"" + theString + "\"", "Encoding.UTF8.GetString(Convert.FromBase64String(@" + "\"" + theBase64String + "\"" + "))")
							strippedLine = strippedLine.replace("@Encoding.UTF8.GetString(Convert.FromBase64String", "Encoding.UTF8.GetString(Convert.FromBase64String")
							strippedLine = strippedLine.replace("$Encoding.UTF8.GetString(Convert.FromBase64String", "Encoding.UTF8.GetString(Convert.FromBase64String")
							

					# if string obfuscation method is rot13
					if theObfMethod == "rot13":
						rot13String = codecs.encode(theString, "rot_13")

						# if the line has escaped strings
						if "\\r" in strippedLine or "\\n" in strippedLine or "\\t" in strippedLine or "\"" in strippedLine or "\'" in strippedLine:
							if "++====THISGETSREPLACED====++" in strippedLine and "\"" not in strippedLine and "\'" not in strippedLine:
								strippedLine = strippedLine.replace("\"" + theString + "\"", "new string(@" + "\"" + rot13String + "\"" + ".Select(xAZ => (xAZ >= 'a' && xAZ <= 'z') ? (char)((xAZ - 'a' + 13) % 26 + 'a') : ((xAZ >= 'A' && xAZ <= 'Z') ? (char)((xAZ - 'A' + 13) % 26 + 'A') : xAZ)).ToArray())")
							else:
								strippedLine = strippedLine.replace("\"" + theString + "\"", "new string(" + "\"" + rot13String + "\"" + ".Select(xAZ => (xAZ >= 'a' && xAZ <= 'z') ? (char)((xAZ - 'a' + 13) % 26 + 'a') : ((xAZ >= 'A' && xAZ <= 'Z') ? (char)((xAZ - 'A' + 13) % 26 + 'A') : xAZ)).ToArray())")

							strippedLine = strippedLine.replace("\\e", "\\\\e")
							strippedLine = strippedLine.replace("\\g", "\\\\g")
							strippedLine = strippedLine.replace("\\\\\\e", "\\\\e")
							strippedLine = strippedLine.replace("\\\\\\g", "\\\\g") 
							strippedLine = strippedLine.replace("\\\\\\\\e", "\\\\e")
							strippedLine = strippedLine.replace("\\\\\\\\g", "\\\\g") 
							strippedLine = strippedLine.replace("++====THISGETSREPLACED====++","\\" + "\"") # remove placeholder strings
							strippedLine = strippedLine.replace("++====GUVFTRGFERCYNPRQ====++","\\" + "\"") # remove placeholder strings
							strippedLine = strippedLine.replace("@new string(", "new string(@")
							strippedLine = strippedLine.replace("$new string(", "new string(")

						# if the line does not have escaped strings
						else:
							strippedLine = strippedLine.replace("\"" + theString + "\"", "new string(@" + "\"" + rot13String + "\"" + ".Select(xAZ => (xAZ >= 'a' && x <= 'z') ? (char)((xAZ - 'a' + 13) % 26 + 'a') : ((xAZ >= 'A' && xAZ <= 'Z') ? (char)((xAZ - 'A' + 13) % 26 + 'A') : xAZ)).ToArray())")
							strippedLine = strippedLine.replace("++====THISGETSREPLACED====++","\\" + "\"") # remove placeholder strings
							strippedLine = strippedLine.replace("++====GUVFTRGFERCYNPRQ====++","\\" + "\"") # remove placeholder strings
							strippedLine = strippedLine.replace("@new string(", "new string(@")
							strippedLine = strippedLine.replace("$new string(", "new string(")


					# if string obfuscation method is reverse
					if theObfMethod == "reverse":
						reversedString = reverseString(theString)

						# if the line has escaped strings (e.g., \r, \t, etc.)
						if "\\r" in strippedLine or "\\n" in strippedLine or "\\t" in strippedLine or "\"" in strippedLine or "\'" in strippedLine:
							if "++====THISGETSREPLACED====++" in strippedLine:
								strippedLine = strippedLine.replace("\"" +theString + "\"", "new string(@" + "\"" + reversedString + "\"" + ".ToCharArray().Reverse().ToArray())")
							else:
								strippedLine = strippedLine.replace("\"" +theString + "\"", "new string(" + "\"" + reversedString + "\"" + ".ToCharArray().Reverse().ToArray())")

							strippedLine = strippedLine.replace("r\\", "r\\\\")
							strippedLine = strippedLine.replace("t\\", "t\\\\")
							strippedLine = strippedLine.replace("n\\", "n\\\\")
							strippedLine = strippedLine.replace("r\\\\\\", "r\\\\")
							strippedLine = strippedLine.replace("n\\\\\\", "n\\\\")
							strippedLine = strippedLine.replace("t\\\\\\", "t\\\\")
							strippedLine = strippedLine.replace("++====DECALPERSTEGSIHT====++","\"\"") # remove placeholder strings
							strippedLine = strippedLine.replace("++====THISGETSREPLACED====++","\\" + "\"") # remove placeholder strings
							strippedLine = strippedLine.replace("@new string(", "new string(@")
							strippedLine = strippedLine.replace("$new string(", "new string(")
							strippedLine = strippedLine.replace("r\\\\\\", "r\\\\")
							strippedLine = strippedLine.replace("n\\\\\\", "n\\\\")
							strippedLine = strippedLine.replace("t\\\\\\", "t\\\\")

						# if the line does not have escaped strings
						else:
							strippedLine = strippedLine.replace("\"" + theString + "\"", "new string(@" + "\"" + reversedString + "\"" + ".ToCharArray().Reverse().ToArray())")
							strippedLine = strippedLine.replace("++====DECALPERSTEGSIHT====++","\"\"") # remove placeholder strings
							strippedLine = strippedLine.replace("++====THISGETSREPLACED====++","\\" + "\"") # remove placeholder strings
							strippedLine = strippedLine.replace("@new string(", "new string(@")
							strippedLine = strippedLine.replace("$new string(", "new string(")

			strippedLine = strippedLine.replace("++====THISGETSREPLACED====++","") # remove any placeholder string that wasn't a string candidate originally
			fInCopy.write(strippedLine)

		# remove duplicate libraries for ones that are included for string deobfuscation
		elif "using System.Linq;" in line and "//start" not in line and "#define" not in line:
			line = line.replace("using System.Linq;", "")

		elif "using System.Text;" in line and "//start" not in line and "#define" not in line:
			line = line.replace("using System.Text;", "")

		elif "using System;" in line and "//start" not in line and "#define" not in line:
			line = line.replace("using System;", "")

		# replace namepace of old tool name to new tool name
		elif "namespace" in line and currentToolName in line:
			line = line.replace(currentToolName, theName)		
			fInCopy.write(line)

		# if class currently has old tool name in it, replace it
		elif "class " + currentToolName in line:
			line = line.replace(currentToolName, theName)
			fInCopy.write(line)

		# if line is a standard one-line comment (e.g., // something), delete it
		elif line.strip().startswith("//") and "//start\r\nusing System.Text;\r\nusing System.Linq;\r\n" not in line and "*/" not in line and "/*" not in line:
			fInCopy.write("")

		# if using library in class that has old tool name in it, replace it
		elif line.strip().startswith("using") and currentToolName in line:
			line = line.replace(currentToolName,theName)
			fInCopy.write(line)

		# replace constructor name if it has current tool name init
		elif line.strip().startswith("public" + currentToolName):
			line = line.replace(currentToolName,theName)
			fInCopy.write(line)

		# replace any occurrence of current tool name in source code
		elif currentToolName in line:
			line = line.replace(currentToolName,theName)
			fInCopy.write(line)

		# last catch for any of the placeholder strings that need removed
		elif "++====THISGETSREPLACED====++" in line:
			line = line.replace("++====THISGETSREPLACED====++","")
			fInCopy.write(line)		

		# if no modifications need done to the line
		else:
			fInCopy.write(line)
 
	# close file streams and replace old source file with new modified one
	fIn.close()
	fInCopy.close()
	os.remove(theFile)
	os.rename(theFile + "_copy",theFile)


# main method
def main(theObfMethod, theDirectory, theName):

	print("""
,                 .     .   .        ,-. .         ,   
|         o     o |   o | o |       /    |         |   
| ;-. . , . ,-. . |-. . | . |-  . . |    | ,-. ,-: | , 
| | | |/  | `-. | | | | | | |   | | \    | | | | | |<  
' ' ' '   ' `-' ' `-' ' ' ' `-' `-|  `-' ' `-' `-` ' ` 
                                `-'                    
""")

	print("====================================================")
	print("[*] INFO: String obfuscation method: " + theObfMethod)
	print("[*] INFO: Directory of C# project: " + theDirectory)
	print("[*] INFO: New tool name: " + theName)
	print("====================================================")

	# generate new GUID for C# project and replace tool name
	replaceGUIDAndToolName(theDirectory, theName)
    
    # if user wants to obfuscate strings, then proceed
	if theObfMethod != "":
                for r, d, f in os.walk(theDirectory):
                    for file in f:
                        if file.endswith(".cs") and "AssemblyInfo.cs" not in file:
                            stringObfuscate(os.path.join(r, file), theName, theObfMethod)

	print("")
	print("[+] SUCCESS: Your new tool \"" + theName +  "\" now has the invisibility cloak applied.")
	print("")


if __name__ == '__main__':
	try:
		parser = optparse.OptionParser(formatter=optparse.TitledHelpFormatter(), usage=globals()['__doc__'], version='0.3')
		parser.add_option('-m', '--method', dest='obfMethod',help='string obfuscation method')
		parser.add_option('-d', '--directory', dest='directory',help='directory of C# project')
		parser.add_option('-n', '--name', dest='name',help='new tool name')
		(options, args) = parser.parse_args()

		# if directory or name or not specified, display help and exit
		if (options.directory == None or options.name == None):
			print("")
			print("[-] ERROR: You must supply directory of C# project and new name for tool.")
			print("")
			parser.print_help()
			sys.exit(0)

		# if obfuscation method is not supported method, display help and exit
		if (options.obfMethod != None and (options.obfMethod != "base64" and options.obfMethod != "rot13" and options.obfMethod != "reverse")):
			print("")
			print("[-] ERROR: You must supply a supported string obfuscation method")
			print("")
			parser.print_help()
			sys.exit(0)

		# if directory provided does not exist, display message and exit
		doesDirExist = os.path.isdir(options.directory)
		if doesDirExist == 0:
			print("")
			print("[-] ERROR: Directory provided does not exist. Please check the path you are providing")
			print("")
			sys.exit(0)

		# initialize variables        
		theObfMethod = options.obfMethod
		theDirectory = options.directory
		theName = options.name
        
                # if no obfuscation method supplied
		if theObfMethod == None:
			theObfMethod = ""

		# proceed to main method
		main(theObfMethod, theDirectory, theName)

	except KeyboardInterrupt: # Ctrl-C
		raise
	except SystemExit: # sys.exit()
		raise
	except FileNotFoundError:
		raise
		traceback.print_exc()
		os._exit(1)
	except Exception:
		print("")
		print("[-] ERROR: Unexpected exception")
		print("")
		raise
		traceback.print_exc()
		os._exit(1)
