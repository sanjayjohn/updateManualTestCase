#  NUnit Automation with updating existing Manual Test Cases

## Overview:

In the function.py script, there is a function called updateManualTestCase. The method will query for a test case, and if the manual test case exists, the method will update the test case to an automated one. This method should be used if you want to convert your manual test cases to automatic ones so that the old test cases can be used with the auto test log API. If the test case does not exist, the API will create test cases.

While parsing through the TestResult.xml results file, the updateManualTestCase method will be called, so that existing test cases with the same name as the class name in the xml document can converted to automated ones.

Note: The updateManualTestCase method can be used with any type of parser


### From Command Prompt:

1. Make sure pip was installed correctly with python on your machine by running the following command. It should output the pip version:

 `pip --version`

 Note: pip3 will work as well. Try `pip3 --version`

2. If pip is not installed, run the following command to install pip:

 `python -m -ensurepip --default-pip`

More information about downloading pip can be found at [https://packaging.python.org/tutorials/installing-packages/](https://packaging.python.org/tutorials/installing-packages/)

3. After you have ensured pip is installed, run the following commands individually :

`pip install requests`

`pip install beautifulsoup4`

`pip install lxml`

`pip install pybase64`

Note: If using pip3 run commands with pip3 instead e.g. `pip3 install requests`

These commands will install the necessary modules required to run the python scripts. The modules are used to send requests to the API, read json configuration files, parse xml documents, and upload files to qTest.


## Update Configuration File (conf.json):

**git\_url:** The shell script uses the url to clone a repository and send pull requests everytime it runs if -g input is used

**local\_repository:** The folder containing the Selenium C Sharp. The shell script will use this to know where to run the nunit tests. To run the nunit tests, the shell script looks for .dll file which is located in bin\Debug. For the script to work the local repository folder name must be the same as the .dll file that gets created when the project gets built.

**qtest\_api\_token:** The token used to authorize the connection to qTest Manager

**qtest\_url:** The personal url that is used to access QASymphony API

**project\_id:** The Project Id 

Open the conf.json file and update with your personal information. Enter your own qTest URL and API Token found in the qTest Manager Environment.

## Running Automation from Command Prompt:

Mac: `python3 functions.py`

Windows: `python functions.py`

This will parse the results in the TestResult.xml, and upload results to qTest. It will build test cases if they do not exist, and it will convert manual test cases to automatic ones if they already exist.


