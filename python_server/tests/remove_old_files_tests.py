import unittest
import tempfile
import time
import os
class RemoveOldFilesTestCases(unittest.TestCase):

    def test_remove_old_files(self):
        """
            create 6 files and add the datetime in its name,
            each file must be separate by 10 secs
            after use the function remove_old_files,
            before 30 sec that was create the last file
            in the end the path should only content 3 files
        """
        now = int(time.time())
        tmp_path = tempfile.mkdtemp()

        for i in range(6):
            new_date = i*1
            time.sleep(10)
            
            file = open(os.path.join(tmp_path, "%i_random.txt" % new_date), "w+")
            file.write("random")
            file.close()

        self.assertEquals(len(os.listdir(tmp_path)), 6)





if __name__ == "__main__":
    unittest.main()