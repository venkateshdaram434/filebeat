from filebeat import TestCase

import os
import time
import json

# Additional tests: to be implemented
# * Check if registrar file can be configured, set config param
# * Check "updating" of registrar file
# * Check what happens when registrar file is deleted

class Test(TestCase):

    def test_registrar_file_content(self):
        # Check if registrar file is created correctly and content is as expected

        self.render_config_template(
            path=os.path.abspath(self.working_dir) + "/log/*"
        )
        os.mkdir(self.working_dir + "/log/")

        testfile =  self.working_dir + "/log/test.log"
        file = open(testfile, 'w')

        iterations = 5
        for n in range(0, iterations):
            file.write("hello world") # 11 chars
            file.write("\n") # 1 char


        file.close()

        proc = self.start_filebeat()

        time.sleep(10)
        proc.kill_and_wait()

        # Check that file exist
        dotFilebeat = self.working_dir + '/.filebeat'
        assert os.path.isfile(dotFilebeat) == True

        with open(dotFilebeat) as file:
            data = json.load(file)

        print data

        # Check that offset is set correctly
        logFileAbs = os.path.abspath(testfile)
        assert data[logFileAbs]['offset'] == iterations * (11 + 1)   # Hello world text plus newline

        # Check that right source field is inside
        assert data[logFileAbs]['source'] == logFileAbs

        # Check that inode is set correctly
        inode = os.stat(logFileAbs).st_ino
        assert data[logFileAbs]['inode'] == inode

        # Check that device is set correctly
        device = os.stat(logFileAbs).st_dev
        assert data[logFileAbs]['device'] == device

        # Check that no additional info is in the file
        assert len(data) == 1
        assert len(data[logFileAbs]) == 4


    def test_registrar_files(self):
        # Check that multiple files are put into registrar file

        self.render_config_template(
            path=os.path.abspath(self.working_dir) + "/log/*"
        )
        os.mkdir(self.working_dir + "/log/")

        testfile1 =  self.working_dir + "/log/test1.log"
        testfile2 =  self.working_dir + "/log/test2.log"
        file1 = open(testfile1, 'w')
        file2 = open(testfile2, 'w')

        iterations = 5
        for n in range(0, iterations):
            file1.write("hello world") # 11 chars
            file1.write("\n") # 1 char
            file2.write("goodbye world") # 11 chars
            file2.write("\n") # 1 char


        file1.close()
        file2.close()

        proc = self.start_filebeat()

        time.sleep(10)
        proc.kill_and_wait()

        # Check that file exist
        dotFilebeat = self.working_dir + '/.filebeat'
        assert os.path.isfile(dotFilebeat) == True

        with open(dotFilebeat) as file:
            data = json.load(file)

        # Check that 2 files are port of the registrar file
        assert len(data) == 2


