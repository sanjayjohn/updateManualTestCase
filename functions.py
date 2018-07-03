import json
import pathlib
import requests
import time
import base64


def get_config():
    # Check to ensure the configuration file exists and is readable.
    try:
        path = pathlib.Path("conf.json")
        if path.exists() and path.is_file():
            with open(path) as config_file:
                try:
                    qtest_config = json.load(config_file)
                    return qtest_config
                except json.JSONDecodeError:
                    print("Error: Configuration file not in valid JSON format.")
        else:
            raise IOError
    except IOError:
        print("Error: Configuration file not found or inaccessible.")
        return -1
    except Exception as e:
        print("Error: Unexpected error loading configuration: " + str(e))
        return -1


def create_test_logs_json(runName, stepName, status, note, log, start, end):
    attachment = []
    if start is None:
        start = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    if end is None:
        end = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    if log is not '':
        value = {'name': stepName, 'content_type': 'application/json', 'data': log}
        attachment.append(value)
    body = {'exe_start_date': start,
            'exe_end_date': end,
            'note': note,
            'name': runName,
            'status': status,
            'automation_content': runName + '#' + stepName,
            'attachments': attachment,
            'module_names': [runName, stepName]
            }
    return body

def updateManualTestCase(className, methodName):
    qtest_config = get_config()
    api_token = qtest_config["qtest_api_token"]
    qTestUrl = qtest_config["qtest_url"]
    projectId = qtest_config["project_id"]
    baseUrl = '{}/api/v3/projects/{}/search'

    payload = {
      "object_type": "test-cases",
      "fields": [
        "*"
      ],
    "query": "'name' ~ " + className
    }

    key = '{}'
    key = key.format(api_token)
    headers = {'Content-Type': 'application/json',
               "Authorization": key}

    queryUrl = baseUrl.format(qTestUrl, projectId)
    testCaseID = None
    try:
        r = requests.post(queryUrl, data=json.dumps(payload), headers=headers)
        testCase = json.loads(r.content)
        testCaseID = testCase['items'][0]['id']
    except:
        print("Unable to find Test Case.")

    if testCaseID is not None:
        baseUrl = '{}/api/v3/projects/{}/test-cases/{}'
        testCaseUrl = baseUrl.format(qTestUrl, projectId, testCaseID)
        key = '{}'
        key = key.format(api_token)
        headers = {'Content-Type': 'application/json',
                   "Authorization": key}
        testCaseJson = None
        try:
            r = requests.get(testCaseUrl, headers=headers)
            testCaseJson = json.loads(r.content)
            # print(testCaseJson)
        except:
            print("Error: Unable to find Test Case.")

        if testCaseJson is not None:
            updateRequired = False
            for field in testCaseJson['properties']:
                if field['field_name'] == 'Automation' and field['field_value'] != '711':
                    field['field_value'] = '711'
                    field['field_value_name'] = 'Yes'
                    updateRequired = True
                if field['field_name'] == 'Automation Content' and field['field_value'] == '':
                    field['field_value'] = className + '#' + methodName
            # print(testCaseJson)
            if updateRequired:
                try:
                    r = requests.put(url=testCaseUrl, data=json.dumps(testCaseJson),
                                     headers=headers)
                    print(r.content)
                except:
                    print("Unable to update testcase")



def parse_xml():
    try:
        from BeautifulSoup import BeautifulSoup
    except ImportError:
        from bs4 import BeautifulSoup
    try:
        file = './TestResult.xml'
        xml = open(file)
    except:
        print('Error: Enter a valid file path argument or file not found or inaccessible')
        return -1
    body = []
    soup = BeautifulSoup(xml, 'xml')
    message = ''
    log = ''
    for tag in soup.find_all('test-case'):
        try:
            runName = tag['classname']
            stepName = tag['methodname']
        except:
            runName = tag['fullname']
            stepName = tag['name']
        updateManualTestCase(runName, stepName)
        status = tag['result']
        if tag.find('start-time') is not None and tag.find('end-time') is not None:
            start = tag['start-time']
            end = tag['end-time']
        else:
            start = None
            end = None
        if status == "Failed":
            status = "FAIL"
        elif status == "Passed":
            status = "PASS"
        else:
            status = "SKIP"
        if status == 'FAIL':
            if tag.find('stack-trace') is not None:
                log = tag.find('stack-trace').text
                log = base64.b64encode(bytes(log, 'utf-8'))
                log = log.decode('utf-8')
            if tag.find('message') is not None:
                message = tag.find('message').text
        else:
            message = ''
            log = ''
        value = create_test_logs_json(runName, stepName, status, message, log, start, end)
        body.append(value)
    return body


def post_all_tests():
    qtest_config = get_config()
    api_token = qtest_config["qtest_api_token"]
    qTestUrl = qtest_config["qtest_url"]
    projectId = qtest_config["project_id"]
    body = parse_xml()

    baseUrl = '{}/api/v3/projects/{}/auto-test-logs'

    testLogUrl = baseUrl.format(qTestUrl, projectId)
    try:
        update = 'update'
        if update == 'update':
            testCycle = get_test_cycle()
        else:
            testCycle = post_test_cycle()
    except:
        print("Error: Enter valid argument (true or false) to update existing test cycle or not")
        return -1
    payload = {
        'skipCreatingAutomationModule': False,
        'test_logs': body,
        'execution_date': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        'test_cycle': testCycle
    }

    key = '{}'
    key = key.format(api_token)
    headers = {'Content-Type': 'application/json',
           "Authorization": key}
    params = {'type': 'automation'}
    try:
        r = requests.post(testLogUrl, params=params, data=json.dumps(payload), headers=headers)
        print(r.text)
    except:
        print("Error: Unable to post data to qTest Manager API.")
        return -1

def post_test_cycle():
    qtest_config = get_config()
    api_token = qtest_config["qtest_api_token"]
    qTestUrl = qtest_config["qtest_url"]
    projectId = qtest_config["project_id"]

    baseUrl = '{}/api/v3/projects/{}/test-cycles/'

    testLogUrl = baseUrl.format(qTestUrl, projectId)
    payload = {
        "id": 1,
        "name": "Selenium Automated Tests",
        'last_modified_date': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    }

    key = '{}'
    key = key.format(api_token)
    headers = {'Content-Type': 'application/json',
           "Authorization": key}

    r = requests.post(testLogUrl, data=json.dumps(payload), headers=headers)
    string = json.loads(r.text)
    testcycleId = string.get("id")
    return testcycleId

def get_test_cycle():
    qtest_config = get_config()
    api_token = qtest_config["qtest_api_token"]
    qTestUrl = qtest_config["qtest_url"]
    projectId = qtest_config["project_id"]

    baseUrl = '{}/api/v3/projects/{}/test-cycles/'

    testLogUrl = baseUrl.format(qTestUrl, projectId)
    payload = {
        "id": 1,
        "name": "Features",
        'last_modified_date': time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
    }

    key = '{}'
    key = key.format(api_token)
    headers = {'Content-Type': 'application/json',
           "Authorization": key}

    r = requests.get(testLogUrl, data=json.dumps(payload), headers=headers)
    string = json.loads(r.text)
    testcycleId = None
    for attrib in string:
        name = attrib.get('name')
        if name == "Selenium Automated Tests":
            testcycleId = attrib.get('id')
    if testcycleId is None:
        testcycleId = post_test_cycle()
    return testcycleId

post_all_tests()
