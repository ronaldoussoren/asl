import unittest
import platform
import os
import sys
from distutils.version import LooseVersion

import asl

try:
    long
except NameError:
    long = int

class TestMiscFunctions (unittest.TestCase):
    def test_mask(self):
        self.assertEqual(asl.ASL_FILTER_MASK(1), 1<<1)
        self.assertEqual(asl.ASL_FILTER_MASK(2), 1<<2)
        self.assertEqual(asl.ASL_FILTER_MASK(8), 1<<8)

    def test_upto(self):
        self.assertEqual(asl.ASL_FILTER_MASK_UPTO(0), 1)
        self.assertEqual(asl.ASL_FILTER_MASK_UPTO(1), 3)
        self.assertEqual(asl.ASL_FILTER_MASK_UPTO(8), 511)

    def test_aliases(self):
        self.assertIs(asl.asl_new, asl.aslmsg)
        self.assertIs(asl.asl_open, asl.aslclient)


    @unittest.skipUnless(LooseVersion(platform.mac_ver()[0]) < LooseVersion("10.7"), "Requires OSX 10.7")
    def test_no_aux(self):
        self.assertFalse(hasattr(asl, 'create_auxiliary_file'))
        self.assertFalse(hasattr(asl, 'close_auxiliary_file'))
        self.assertFalse(hasattr(asl, 'log_auxiliary_location'))

    @unittest.skipUnless(LooseVersion(platform.mac_ver()[0]) >= LooseVersion("10.7"), "Requires OSX 10.7")
    def test_create_auxiliary_file(self):
        msg = asl.aslmsg(asl.ASL_TYPE_MSG)
        msg[asl.ASL_KEY_MSG] = 'hello world'

        fd = asl.create_auxiliary_file(msg, 'title', None)
        self.assertIsInstance(fd, (int, long))
        os.write(fd, b'hello world\n')
        asl.close_auxiliary_file(fd)

        self.assertRaises(OSError, os.write, fd, b'Done')

        msg = asl.aslmsg(asl.ASL_TYPE_MSG)
        msg[asl.ASL_KEY_MSG] = 'hello world'

        fd = asl.create_auxiliary_file(msg, 'title', 'public.text')
        self.assertIsInstance(fd, (int, long))
        os.write(fd, b'hello world\n')
        asl.close_auxiliary_file(fd)

        msg = asl.aslmsg(asl.ASL_TYPE_MSG)
        msg[asl.ASL_KEY_MSG] = 'hello world'

        self.assertRaises(TypeError, asl.create_auxiliary_file, 'foo', 'title', None)
        self.assertRaises(TypeError, asl.create_auxiliary_file, None, 42, None)
        self.assertRaises(TypeError, asl.create_auxiliary_file, None, 'title', 42)

    @unittest.skipUnless(LooseVersion(platform.mac_ver()[0]) >= LooseVersion("10.7") and sys.version_info[0] == 3, "Requires OSX 10.7, Python 3 test")
    def test_no_bytes(self):
        msg = asl.aslmsg(asl.ASL_TYPE_MSG)
        msg[asl.ASL_KEY_MSG] = 'hello world'
        self.assertRaises(TypeError, asl.create_auxiliary_file, None, b'title', None)
        self.assertRaises(TypeError, asl.create_auxiliary_file, None, 'title', b'public.text')

        msg = asl.aslmsg(asl.ASL_TYPE_MSG)
        msg[asl.ASL_KEY_MSG] = 'hello world'
        self.assertRaises(TypeError, asl.log_auxiliary_location, msg, b'title', 'public.txt', 'http://www.python.org/')
        self.assertRaises(TypeError, asl.log_auxiliary_location, msg, 'title', b'public.txt', 'http://www.python.org/')
        self.assertRaises(TypeError, asl.log_auxiliary_location, msg, 'title', 'public.txt', b'http://www.python.org/')

    @unittest.skipUnless(LooseVersion(platform.mac_ver()[0]) >= LooseVersion("10.7") and sys.version_info[0] == 2, "Requires OSX 10.7, Python 2 test")
    def test_with_unicode(self):
        msg = asl.aslmsg(asl.ASL_TYPE_MSG)
        msg[asl.ASL_KEY_MSG] = 'hello world'

        fd = asl.create_auxiliary_file(msg, b'title'.decode('utf-8'), 'public.text')
        self.assertIsInstance(fd, (int, long))
        os.write(fd, b'hello world\n')
        asl.close_auxiliary_file(fd)

        msg = asl.aslmsg(asl.ASL_TYPE_MSG)
        msg[asl.ASL_KEY_MSG] = 'hello world'

        fd = asl.create_auxiliary_file(msg, 'title', b'public.text'.decode('utf-8'))
        self.assertIsInstance(fd, (int, long))
        os.write(fd, b'hello world\n')
        asl.close_auxiliary_file(fd)

        msg = asl.aslmsg(asl.ASL_TYPE_MSG)
        msg[asl.ASL_KEY_MSG] = 'hello world'
        asl.log_auxiliary_location(msg, b'title'.decode('utf-8'), 'public.text', 'http://www.python.org/')

        msg = asl.aslmsg(asl.ASL_TYPE_MSG)
        msg[asl.ASL_KEY_MSG] = 'hello world'
        asl.log_auxiliary_location(msg, 'title', b'public.text'.decode('utf-8'), 'http://www.python.org/')

        msg = asl.aslmsg(asl.ASL_TYPE_MSG)
        msg[asl.ASL_KEY_MSG] = 'hello world'
        asl.log_auxiliary_location(msg, 'title', 'public.text', b'http://www.python.org/'.decode('utf-8'))


    @unittest.skipUnless(LooseVersion(platform.mac_ver()[0]) >= LooseVersion("10.7"), "Requires OSX 10.7")
    def test_log_auxiliary_location(self):
        msg = asl.aslmsg(asl.ASL_TYPE_MSG)
        msg[asl.ASL_KEY_MSG] = 'hello world'
        asl.log_auxiliary_location(msg, 'title', 'public.text', 'http://www.python.org/')

        msg = asl.aslmsg(asl.ASL_TYPE_MSG)
        msg[asl.ASL_KEY_MSG] = 'hello world'
        asl.log_auxiliary_location(msg, 'title', None, 'http://www.python.org/')

        msg = asl.aslmsg(asl.ASL_TYPE_MSG)
        msg[asl.ASL_KEY_MSG] = 'hello world'
        self.assertRaises(TypeError, asl.log_auxiliary_location, msg, 'title', None, None)
        self.assertRaises(TypeError, asl.log_auxiliary_location, msg, 'title', None, 42)
        self.assertRaises(TypeError, asl.log_auxiliary_location, msg, 'title', 42, 'http://www.python.org')
        self.assertRaises(TypeError, asl.log_auxiliary_location, msg, 42, None, 'http://www.python.org')



if __name__ == "__main__":
    unittest.main()
