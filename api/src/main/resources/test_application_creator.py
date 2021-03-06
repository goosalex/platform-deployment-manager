"""
Name:       test_application_creator.py
Purpose:    Unit tests for the hbase package registrar
            Run with main(), the easiest way is "nosetests test_*.py"
Author:     PNDA team

Created:    21/03/2016

Copyright (c) 2016 Cisco and/or its affiliates.

This software is licensed to you under the terms of the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at http://www.apache.org/licenses/LICENSE-2.0

The code, technical concepts, and all information contained herein, are the property of Cisco Technology, Inc.
and/or its affiliated entities, under various laws including copyright, international treaties, patent,
and/or contract. Any use of the material herein must be in accordance with the terms of the License.
All rights not expressly granted by the License are reserved.

Unless required by applicable law or agreed to separately in writing, software distributed under the
License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied.
"""

import unittest
from datetime import datetime
from mock import patch, mock_open
from application_creator import ApplicationCreator
from exceptiondef import FailedValidation, FailedCreation


class ApplicationCreatorTests(unittest.TestCase):

    config = {'stage_root': 'stage', 'plugins_path': 'plugins'}
    environment = {
        'webhdfs_host': 'webhdfshost',
        'webhdfs_port': 'webhdfsport',
        'name_node': 'namenode',
        'oozie_uri': 'oozie',
        'cluster_private_key': 'keyfile.pem',
        'cluster_root_user': 'root_user',
        'yarn_node_managers': 'nm1,nm2',
        'hbase_rest_server': 'hbasehost',
        'hbase_rest_port': '123',
        'hive_server': 'hivehost',
        'hive_port': '124',
        'opentsdb': '1.2.3.5:1234'
    }
    service = 'ns'
    package_metadata = {
        "component_types": {
            "sparkStreaming": {
                "componentC": {
                    "component_detail": {
                        "properties.json": {
                            "property1": "1",
                            "property2": "two"
                        }
                    },
                    "component_path": "test_package-1.0.2/sparkStreaming/componentC",
                    "component_name": "componentC"
                }
            },
            "oozie": {
                "componentA": {
                    "component_detail": {
                        "properties.json": {
                            "property3": "3",
                            "property4": "four"
                        }
                    },
                    "component_path": "test_package-1.0.2/oozie/componentA",
                    "component_name": "componentA"
                },
                "componentB": {
                    "component_detail": {
                        "hdfs.json": {},
                        "hbase.json": {},
                        "opentsdb.json": {},
                        "properties.json": {}
                    },
                    "component_path": "test_package-1.0.2/oozie/componentB",
                    "component_name": "componentB"
                }
            }
        },
        "package_name": "test_package-1.0.2"
    }

    package_metadata_2 = {
        "component_types": {
            "oozie": {
                "componentA": {
                    "component_detail": {
                        "coordinator.xml": {}
                    },
                    "component_path": "test_package-1.0.2/oozie/componentA",
                    "component_name": "componentA"
                }
            }
        },
        "package_name": "test_package-1.0.3"
    }

    property_overrides = {
        'oozie': {
            'componentA': {
                'property3': '3',
                'property4': 'nine'
            }
        },
        'sparkStreaming': {
            'componentC': {
                'property1': '11',
                'property2': 'twelve'
            }
        }
    }

    create_data = {
        'sparkStreaming': [{
            'stop_cmds': ['sudo initctl stop ns-aname-componentC\n'],
            'descriptors': {},
            'start_cmds': ['sudo initctl start ns-aname-componentC\n'],
            'ssh': ['sudo initctl stop ns-aname-componentC\n', 'sudo rm -rf /opt/ns/aname/componentC\n', 'sudo rm  /etc/init/ns-aname-componentC.conf\n'],
            'component_job_name': 'aname-componentC-job',
            'component_name': 'componentC'
        }],
        'oozie': [{
            'descriptors': {},
            'component_hdfs_root': '/user/aname/componentA',
            'job_handle': 'someid1',
            'component_job_name': 'aname-componentA-job',
            'component_name': 'componentA'
        }, {
            'descriptors': {
                'hdfs.json': []
            },
            'component_hdfs_root': '/user/aname/componentB',
            'job_handle': 'someid2',
            'component_job_name': 'aname-componentB-job',
            'component_name': 'componentB'
        }]
    }

    @patch('starbase.Connection')
    @patch('pyhs2.connect')
    @patch('datetime.datetime')
    @patch('os.system')
    @patch('deployer_utils.exec_ssh')
    @patch('requests.put')
    @patch('requests.post')
    @patch('deployer_utils.HDFS')
    @patch('spur.ssh')
    @patch('application_creator.shutil')
    @patch('application_creator.os')
    @patch('application_creator.tarfile')
    # pylint: disable=unused-argument
    def test_create_application(self, tar_mock, os_mock, shutil_mock, spur_ssh,
                                hdfs_client_mock, post_mock, put_mock, exec_ssh_mock,
                                os_sys_mock, dt_mock, hive_mock, hbase_mock):
        dt_mock.utcnow.return_value = (datetime(2013, 01, 01))

        class Resp(object):
            status_code = 201

            def json(self):
                return {'id': 'someid'}

        post_mock.return_value = Resp()
        with patch("__builtin__.open", mock_open(read_data="[]")):
            creator = ApplicationCreator(self.config, self.environment, self.service)
            creator.create_application('abcd', self.package_metadata, 'aname', self.property_overrides)
        print post_mock.call_args_list
        # pylint: disable=line-too-long
        post_mock.assert_any_call('oozie/v1/jobs', data='<?xml version="1.0" encoding="UTF-8" ?><configuration><property><name>environment_cluster_private_key</name><value>keyfile.pem</value></property><property><name>environment_webhdfs_host</name><value>webhdfshost</value></property><property><name>environment_opentsdb</name><value>1.2.3.5:1234</value></property><property><name>environment_yarn_node_managers</name><value>nm1,nm2</value></property><property><name>environment_webhdfs_port</name><value>webhdfsport</value></property><property><name>environment_hbase_rest_server</name><value>hbasehost</value></property><property><name>environment_oozie_uri</name><value>oozie</value></property><property><name>environment_hbase_rest_port</name><value>123</value></property><property><name>environment_cluster_root_user</name><value>root_user</value></property><property><name>environment_hive_port</name><value>124</value></property><property><name>environment_name_node</name><value>namenode</value></property><property><name>environment_hive_server</name><value>hivehost</value></property><property><name>component_property3</name><value>3</value></property><property><name>component_property4</name><value>nine</value></property><property><name>component_application</name><value>aname</value></property><property><name>component_name</name><value>componentA</value></property><property><name>component_job_name</name><value>aname-componentA-job</value></property><property><name>component_hdfs_root</name><value>/user/aname/componentA</value></property><property><name>deployment_start</name><value>2013-01-01T00:02Z</value></property><property><name>deployment_end</name><value>2013-01-08T00:02Z</value></property><property><name>user.name</name><value>hdfs</value></property><property><name>oozie.use.system.libpath</name><value>true</value></property><property><name>oozie.libpath</name><value>/user/deployment/platform</value></property><property><name>oozie.wf.application.path</name><value>namenode/user/aname/componentA</value></property></configuration>', headers={'Content-Type': 'application/xml'})
        post_mock.assert_any_call('oozie/v1/jobs', data='<?xml version="1.0" encoding="UTF-8" ?><configuration><property><name>environment_cluster_private_key</name><value>keyfile.pem</value></property><property><name>environment_webhdfs_host</name><value>webhdfshost</value></property><property><name>environment_opentsdb</name><value>1.2.3.5:1234</value></property><property><name>environment_yarn_node_managers</name><value>nm1,nm2</value></property><property><name>environment_webhdfs_port</name><value>webhdfsport</value></property><property><name>environment_hbase_rest_server</name><value>hbasehost</value></property><property><name>environment_oozie_uri</name><value>oozie</value></property><property><name>environment_hbase_rest_port</name><value>123</value></property><property><name>environment_cluster_root_user</name><value>root_user</value></property><property><name>environment_hive_port</name><value>124</value></property><property><name>environment_name_node</name><value>namenode</value></property><property><name>environment_hive_server</name><value>hivehost</value></property><property><name>component_application</name><value>aname</value></property><property><name>component_name</name><value>componentB</value></property><property><name>component_job_name</name><value>aname-componentB-job</value></property><property><name>component_hdfs_root</name><value>/user/aname/componentB</value></property><property><name>deployment_start</name><value>2013-01-01T00:02Z</value></property><property><name>deployment_end</name><value>2013-01-08T00:02Z</value></property><property><name>user.name</name><value>hdfs</value></property><property><name>oozie.use.system.libpath</name><value>true</value></property><property><name>oozie.libpath</name><value>/user/deployment/platform</value></property><property><name>oozie.wf.application.path</name><value>namenode/user/aname/componentB</value></property></configuration>', headers={'Content-Type': 'application/xml'})

        put_mock.assert_any_call('oozie/v1/job/someid?action=suspend')

        exec_ssh_mock.assert_any_call('localhost', 'root_user', 'keyfile.pem', ['mkdir -p /tmp/ns/aname/componentC', 'sudo mkdir -p /opt/ns/aname/componentC'])
        exec_ssh_mock.assert_any_call('nm1', 'root_user', 'keyfile.pem', ['mkdir -p /tmp/ns/aname/componentC'])
        exec_ssh_mock.assert_any_call('nm1', 'root_user', 'keyfile.pem', ['sudo mkdir -p /opt/ns/aname/componentC', 'sudo mv /tmp/ns/aname/componentC/log4j.properties /opt/ns/aname/componentC/log4j.properties'])
        exec_ssh_mock.assert_any_call('nm2', 'root_user', 'keyfile.pem', ['mkdir -p /tmp/ns/aname/componentC'])
        exec_ssh_mock.assert_any_call('nm2', 'root_user', 'keyfile.pem', ['sudo mkdir -p /opt/ns/aname/componentC', 'sudo mv /tmp/ns/aname/componentC/log4j.properties /opt/ns/aname/componentC/log4j.properties'])
        exec_ssh_mock.assert_any_call('localhost', 'root_user', 'keyfile.pem', ['sudo cp /tmp/ns/aname/componentC/upstart.conf /etc/init/ns-aname-componentC.conf', 'sudo cp /tmp/ns/aname/componentC/* /opt/ns/aname/componentC', 'sudo chmod a+x /opt/ns/aname/componentC/yarn-kill.py', 'cd /opt/ns/aname/componentC && sudo jar uf *.jar application.properties', 'sudo rm -rf /tmp/ns/aname/componentC'])

    @patch('starbase.Connection')
    @patch('pyhs2.connect')
    @patch('datetime.datetime')
    @patch('os.system')
    @patch('deployer_utils.exec_ssh')
    @patch('requests.put')
    @patch('requests.post')
    @patch('deployer_utils.HDFS')
    @patch('spur.ssh')
    @patch('application_creator.shutil')
    @patch('application_creator.os')
    @patch('application_creator.tarfile')
    # pylint: disable=unused-argument
    def test_fail_create_application(self, tar_mock, os_mock, shutil_mock, spur_ssh,
                                     hdfs_client_mock, post_mock, put_mock, exec_ssh_mock,
                                     os_sys_mock, dt_mock, hive_mock, hbase_mock):
        dt_mock.utcnow.return_value = (datetime(2013, 01, 01))

        class Resp(object):
            status_code = 400
            headers = {'oozie-error-message': 'oozie error!'}

            def json(self):
                return {'id': 'someid'}

        post_mock.return_value = Resp()
        with patch("__builtin__.open", mock_open(read_data="[]")):
            creator = ApplicationCreator(self.config, self.environment, self.service)
            self.assertRaises(FailedCreation, creator.create_application, 'abcd', self.package_metadata_2, 'aname', self.property_overrides)

    @patch('starbase.Connection')
    @patch('pyhs2.connect')
    @patch('datetime.datetime')
    @patch('os.system')
    @patch('deployer_utils.exec_ssh')
    @patch('requests.put')
    @patch('requests.post')
    @patch('deployer_utils.HDFS')
    @patch('spur.ssh')
    @patch('application_creator.shutil')
    @patch('application_creator.os')
    @patch('application_creator.tarfile')
    # pylint: disable=unused-argument
    def test_app_name_fail(self, tar_mock, os_mock, shutil_mock, spur_ssh,
                           hdfs_client_mock, post_mock, put_mock, exec_ssh_mock,
                           os_sys_mock, dt_mock, hive_mock, hbase_mock):

        class Resp(object):
            status_code = 201

            def json(self):
                return {'id': 'someid'}

        post_mock.return_value = Resp()

        with patch("__builtin__.open", mock_open(read_data="[]")):
            creator = ApplicationCreator(self.config, self.environment, self.service)
            try:
                creator.create_application('abcd', self.package_metadata, 'with&oddchar', self.property_overrides)
                self.assertFail('Expected FailedCreation exception but was not thrown')
            except FailedCreation as ex:
                self.assertEqual(ex.msg, 'Application name with&oddchar may only contain a-z A-Z 0-9 - _')

    @patch('starbase.Connection')
    @patch('pyhs2.connect')
    @patch('datetime.datetime')
    @patch('os.system')
    @patch('deployer_utils.exec_ssh')
    @patch('requests.put')
    @patch('requests.post')
    @patch('deployer_utils.HDFS')
    @patch('spur.ssh')
    @patch('application_creator.shutil')
    @patch('application_creator.os')
    @patch('application_creator.tarfile')
    # pylint: disable=unused-argument
    def test_app_name_ok(self, tar_mock, os_mock, shutil_mock, spur_ssh,
                         hdfs_client_mock, post_mock, put_mock, exec_ssh_mock,
                         os_sys_mock, dt_mock, hive_mock, hbase_mock):

        class Resp(object):
            status_code = 201

            def json(self):
                return {'id': 'someid'}

        post_mock.return_value = Resp()

        with patch("__builtin__.open", mock_open(read_data="[]")):
            creator = ApplicationCreator(self.config, self.environment, self.service)
            creator.create_application('abcd', self.package_metadata, 'test-app', self.property_overrides)

    @patch('deployer_utils.exec_ssh')
    @patch('requests.put')
    def test_start_application(self, put_mock, exec_ssh_mock):
        creator = ApplicationCreator(self.config, self.environment, self.service)
        creator.start_application('name', self.create_data)
        exec_ssh_mock.assert_any_call('localhost', 'root_user', 'keyfile.pem', ['sudo initctl start ns-aname-componentC\n'])
        put_mock.assert_any_call('oozie/v1/job/someid1?action=resume')
        put_mock.assert_any_call('oozie/v1/job/someid2?action=resume')
        put_mock.assert_any_call('oozie/v1/job/someid1?action=start')
        put_mock.assert_any_call('oozie/v1/job/someid2?action=start')

    @patch('deployer_utils.exec_ssh')
    @patch('requests.put')
    def test_stop_application(self, put_mock, exec_ssh_mock):
        creator = ApplicationCreator(self.config, self.environment, self.service)
        creator.stop_application('name', self.create_data)
        exec_ssh_mock.assert_any_call('localhost', 'root_user', 'keyfile.pem', ['sudo initctl stop ns-aname-componentC\n'])
        put_mock.assert_any_call('oozie/v1/job/someid1?action=suspend')
        put_mock.assert_any_call('oozie/v1/job/someid2?action=suspend')

    def test_validate_package(self):
        creator = ApplicationCreator(self.config, self.environment, self.service)
        result = {}
        try:
            creator.validate_package(self.package_metadata['package_name'], self.package_metadata)
        except FailedValidation as ex:
            result = ex.msg

        expected_report = {
            'oozie': {
                'componentA': ['missing file workflow.xml'],
                'componentB': ['missing file workflow.xml']},
            'sparkStreaming': {
                'componentC': ['missing file yarn-kill.py',
                               'missing file application.properties',
                               'missing file upstart.conf',
                               'missing file log4j.properties']}}
        self.assertEqual(result, expected_report)

    def test_invalid_package(self):
        creator = ApplicationCreator(self.config, self.environment, self.service)
        try:
            creator.validate_package('test_package-1.0.2a', {"package_name": "test_package-1.0.2"})
            self.assertFail('Expected FailedValidation exception')
        except FailedValidation as ex:
            self.assertEqual(ex.msg, 'package name must match name of enclosed folder but found test_package-1.0.2a and test_package-1.0.2')

        try:
            creator.validate_package('test_package-1.0', {"package_name": "test_package-1.0"})
            self.assertFail('Expected FailedValidation exception')
        except FailedValidation as ex:
            self.assertEqual(ex.msg, 'version must be a three part major.minor.patch e.g. 1.2.3 but found 1.0')

        try:
            creator.validate_package('test_package=1.0.2', {"package_name": "test_package=1.0.2"})
            self.assertFail('Expected FailedValidation exception')
        except FailedValidation as ex:
            self.assertEqual(ex.msg, 'package name must be of the form name-version e.g. name-version.1.2.3 but found test_package=1.0.2')

        creator.validate_package('test-package-1.0.2', {"package_name": "test-package-1.0.2", "component_types": {}})

    # pylint: disable=unused-argument
    @patch('deployer_utils.exec_ssh')
    @patch('requests.put')
    @patch('os.path.isdir')
    @patch('os.rmdir')
    def test_destroy_application(self, rmdir_mock, isdir_mock, put_mock, exec_ssh_mock):
        isdir_mock.return_value = True
        creator = ApplicationCreator(self.config, self.environment, self.service)
        creator.destroy_application('name', self.create_data)
        print exec_ssh_mock.call_args_list
        exec_ssh_mock.assert_any_call('localhost', 'root_user', 'keyfile.pem', [
            'sudo initctl stop ns-aname-componentC\n', 'sudo rm -rf /opt/ns/aname/componentC\n', 'sudo rm  /etc/init/ns-aname-componentC.conf\n'])

        put_mock.assert_any_call('oozie/v1/job/someid1?action=kill')
        put_mock.assert_any_call('oozie/v1/job/someid2?action=kill')

    # pylint: disable=line-too-long
    @patch('subprocess.check_output')
    def test_get_runtime_details(self, subprocess_mock):
        subprocess_mock.return_value = '''Total number of applications (application-types: [] and states: [SUBMITTED, ACCEPTED, RUNNING]):1
                Application-Id	    Application-Name	    Application-Type	      User	     Queue	             State	       Final-State	       Progress	                       Tracking-URL
application_1455877292606_13009	             aname-componentA-job	               SPARK	      hdfs	 root.hdfs	           RUNNING	         UNDEFINED	            10%	           http://psm-cdh-dn0:51739
application_1455877292606_13010	             aname-componentC-job	               SPARK	      hdfs	 root.hdfs	           RUNNING	         UNDEFINED	            10%	           http://psm-cdh-dn0:51739'''
        creator = ApplicationCreator(self.config, self.environment, self.service)
        result = creator.get_application_runtime_details('name', self.create_data)
        self.assertEqual(result, {'yarn_ids': [{'component': 'componentA', 'type': 'oozie', 'yarn-id': 'application_1455877292606_13009'},
                                               {'component': 'componentC', 'type': 'sparkStreaming', 'yarn-id': 'application_1455877292606_13010'}]})
