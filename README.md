# InvisibilityCloak
Proof-of-concept obfuscation toolkit for C# post-exploitation tools. This will perform the below actions for a C# visual studio project.

* Change the tool name
* Change the project GUID
* Obfuscate compatible strings in source code files based on obfuscation method entered by user
* Removes one-line comments (e.g. // this is a comment)
* Remove PDB string option for compiled release .NET assembly

**Blog Post:** https://securityintelligence.com/posts/invisibility-cloak-obfuscate-c-tools-evade-signature-based-detection

## String Candidates Not Obfuscated
The below string candidates are not included in obfuscation
* Strings less than 3 characters
* Strings using string interpolation (e.g., `Console.WriteLine($"Hello, {name}! Today is {date.DayOfWeek}, it's {date:HH:mm} now.");`)
* Case statements as they need to be static values
* Const vars as they need to be static values
* Strings in method signatures as they need to be static values
* Line with `" => "` as used in switch statement and needs to be static value.
* ` is ` in an if statement when doing comparison as the values compared must be static
* Strings within Regexes
* Override strings as they need to be static values
* The below random edge cases for strings, as they have caused issues when encoding/decoding
  * String starting with or ending with `'`
  * `""'` in the line
  * `+ @"` in the line
  * `"""` in the line
  * `""` in the line
  * `Encoding.Unicode.GetString` in the line
  * `Encoding.Unicode.GetBytes` in the line
  * `Encoding.ASCII.GetBytes` in the line
  * Line starting with `"` and ending with `")]`. This is typically used for command line switches and needs to be static value.

## Support Information
* Windows
* Linux (Debian-based systems)
* Python3

## Arguments/Options

* `-d, --directory` - directory where your visual studio project is located
* `-m, --method` - obfuscation method (base64, rot13, reverse)
* `-n, --name` - name of your new tool
* `-h, --help` - help menu
* `--version` - get version of tool

## Usage/Examples

### Run InvisibilityCloak with string obfuscation

**Base64 String Obfuscation**

`python InvisibilityCloak.py -d /path/to/project -n "TotallyLegitTool" -m base64`

`python InvisibilityCloak.py -d C:\path\to\project -n "TotallyLegitTool" -m base64`

**ROT13 String Obfuscation**

`python InvisibilityCloak.py -d /path/to/project -n "TotallyLegitTool" -m rot13`

`python InvisibilityCloak.py -d C:\path\to\project -n "TotallyLegitTool" -m rot13`

**Reverse String Obfuscation**

`python InvisibilityCloak.py -d /path/to/project -n "TotallyLegitTool" -m reverse`

`python InvisibilityCloak.py -d C:\path\to\project -n "TotallyLegitTool" -m reverse`

### Run InvisibilityCloak without string obfuscation

`python InvisibilityCloak.py -d /path/to/project -n "TotallyLegitTool"`

`python InvisibilityCloak.py -d C:\path\to\project -n "TotallyLegitTool"`

## Signature-Based Detection Statistics

The below table shows the signature-based detection statistics between the unobfuscated and obfuscated versions of 20 popular public C# tools with InvisibilityCloak.

**This is specifically for Microsoft Defender (free version), and accurate as of April 14th, 2022.**

| Tool      | Link | Unobfuscated | Obfuscated w/ InvisibilityCloak |
| ----------- | ----------- | ----------- | ----------- |
| ADCSPwn   | https://github.com/bats3c/ADCSPwn        | **Detected**        | Not Detected         |
| Certify      | https://github.com/GhostPack/Certify       | **Detected**       | Not Detected      |
| Farmer   | https://github.com/mdsecactivebreach/Farmer        | **Detected**        | Not Detected         |
| Rubeus      | https://github.com/GhostPack/Rubeus       | **Detected**       | **Detected**       |
| SafetyKatz   | https://github.com/GhostPack/SafetyKatz        | **Detected**        | Not Detected         |
| Seatbelt      | https://github.com/GhostPack/Seatbelt       | **Detected**       | Not Detected        |
| SharpClipboard   | https://github.com/slyd0g/SharpClipboard        | Not Detected        | Not Detected         |
| SharPersist      | https://github.com/mandiant/SharPersist       | Not Detected       | Not Detected        |
| SharpExec   | https://github.com/anthemtotheego/SharpExec        | **Detected**        | Not Detected         |
| SharpGPOAbuse      | https://github.com/FSecureLABS/SharpGPOAbuse       | **Detected**       | Not Detected        |
| SharpHound   | https://github.com/BloodHoundAD/SharpHound        | Not Detected        | Not Detected         |
| SharpLogger      | https://github.com/djhohnstein/SharpLogger       | **Detected**       | Not Detected        |
| SharpMove   | https://github.com/0xthirteen/SharpMove        | **Detected**        | Not Detected         |
| SharpRDP      | https://github.com/0xthirteen/SharpRDP       | **Detected**       | **Detected**       |
| SharpSecDump   | https://github.com/G0ldenGunSec/SharpSecDump        | **Detected**        | Not Detected         |
| SharpUp      | https://github.com/GhostPack/SharpUp       | Not Detected       | Not Detected        |
| SharpView   | https://github.com/tevora-threat/SharpView        | **Detected**        | Not Detected         |
| SharpWMI      | https://github.com/GhostPack/SharpWMI       | **Detected**       | Not Detected        |
| StandIn   | https://github.com/xforcered/StandIn        | **Detected**        | Not Detected         |
| WireTap   | https://github.com/djhohnstein/WireTap        | Not Detected        | Not Detected         |

## Compiled C# Tool Size Statistics

The below table shows the file sizes of 20 popular public C# tools between the unobfucated and obfuscated versions using InvisibilityCloak with various string obfuscation methods.

| Tool      | Link | Unobfuscated | ROT13 String Obfuscation | Base64 String Obfuscation | Reverse String Obfuscation |
| ----------- | ----------- | ----------- | ----------- | ----------- | ----------- |
| ADCSPwn   | https://github.com/bats3c/ADCSPwn        | 718 KB        | 728 KB         | 722 KB         | 720 KB         |
| Certify      | https://github.com/GhostPack/Certify       | 170 KB        | 198 KB      | 178 KB         | 176 KB         |
| Farmer   | https://github.com/mdsecactivebreach/Farmer        | 13 KB         | 17 KB          | 14 KB         | 13 KB         |
| Rubeus      | https://github.com/GhostPack/Rubeus       | 418 KB        | 605 KB       | 469 KB         | 455 KB         |
| SafetyKatz   | https://github.com/GhostPack/SafetyKatz        | 714 KB        | 716 KB          | 948 KB         | 715 KB         |
| Seatbelt      | https://github.com/GhostPack/Seatbelt       | 543 KB       | 904 KB         | 618 KB         | 608 KB         |
| SharpClipboard   | https://github.com/slyd0g/SharpClipboard        | 6 KB         | 7 KB          | 6 KB         | 7 KB         |
| SharPersist      | https://github.com/mandiant/SharPersist       | 231 KB      | 281 KB         | 248 KB         | 243 KB         |
| SharpExec   | https://github.com/anthemtotheego/SharpExec        | 30 KB         | 57 KB          | 36 KB         | 34 KB         |
| SharpGPOAbuse      | https://github.com/FSecureLABS/SharpGPOAbuse       | 70 KB       | 98 KB         | 79 KB         | 76 KB         |
| SharpHound   | https://github.com/BloodHoundAD/SharpHound        | 880 KB         | 897 KB         | 885 KB         | 883 KB         |
| SharpLogger      | https://github.com/djhohnstein/SharpLogger       | 19 KB        | 27 KB         | 20 KB         | 20 KB         |
| SharpMove   | https://github.com/0xthirteen/SharpMove        | 41 KB         | 100 KB          | 50 KB         | 49 KB         |
| SharpRDP      | https://github.com/0xthirteen/SharpRDP       | 322 KB       | 346 KB       | 326 KB         | 325 KB         |
| SharpSecDump   | https://github.com/G0ldenGunSec/SharpSecDump        | 42 KB         | 55 KB         | 45 KB         | 43 KB         |
| SharpUp      | https://github.com/GhostPack/SharpUp       | 35 KB        | 50 KB        | 40 KB         | 39 KB         |
| SharpView   | https://github.com/tevora-threat/SharpView        | 719 KB         | 856 KB         | 742 KB         | 738 KB         |
| SharpWMI      | https://github.com/GhostPack/SharpWMI       | 53 KB        | 92 KB        | 62 KB         | 61 KB         |
| StandIn   | https://github.com/xforcered/StandIn        | 162 KB         | 294 KB       | 197 KB         | 189 KB         |
| WireTap   | https://github.com/djhohnstein/WireTap        | 282 KB        | 292 KB         | 285 KB         | 284 KB         |



## Roadmap

* Add support for C# projects with multiple C# project files (multi-project solutions)
* Obfuscation support for variable names and method names
