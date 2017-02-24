import unittest
import sys
import os
import platform
from distutils.version import LooseVersion

import asl

try:
    long
except NameError:
    long = int

class TestASLClient (unittest.TestCase):
    def test_basic_creation(self):
        cli = asl.aslclient("ident", "facility", 0)
        self.assertIsInstance(cli, asl.aslclient)

        self.assertRaises(TypeError, asl.aslclient, "ident")
        self.assertRaises(TypeError, asl.aslclient, "ident", "faclity", "option")
        self.assertRaises(TypeError, asl.aslclient, "ident", "faclity", 0, "extra")
        self.assertRaises(TypeError, asl.aslclient, "ident", 42, 0)
        self.assertRaises(TypeError, asl.aslclient, 32, "facility", 42)

    def test_filter(self):
        cli = asl.aslclient("ident", "facility", 0)
        self.assertIsInstance(cli, asl.aslclient)

        f = cli.set_filter(250)
        self.assertIsInstance(f, (int, long))

        f = cli.set_filter(f)
        self.assertEqual(f, 250)

        self.assertRaises(TypeError, cli.set_filter, "debug")

        cli.close()
        self.assertRaises(ValueError, cli.set_filter, 0)

    def test_context(self):

        with asl.aslclient("ident", "facility", 0) as cli:
            self.assertIsInstance(cli, asl.aslclient)

        self.assertRaises(ValueError, cli.set_filter, 0)

    def test_log(self):
        cli = asl.aslclient("ident", "facility", 0)
        self.assertIsInstance(cli, asl.aslclient)

        # Can't easily verify...
        cli.log(None, asl.ASL_LEVEL_NOTICE, "hello world")

        self.assertRaises(TypeError, cli.log, "hello", asl.ASL_LEVEL_NOTICE, "hello world")

        msg = asl.aslmsg(asl.ASL_TYPE_MSG)
        cli.log(msg, asl.ASL_LEVEL_NOTICE, "hello world")

        self.assertRaises(TypeError, cli.log, msg, asl.ASL_LEVEL_NOTICE, "hello world %s", "extra")
        self.assertRaises(TypeError, cli.log, msg, asl.ASL_LEVEL_NOTICE)

    def test_send(self):
        cli = asl.aslclient("ident", "facility", 0)
        self.assertIsInstance(cli, asl.aslclient)

        msg = asl.aslmsg(asl.ASL_TYPE_MSG)
        msg[asl.ASL_KEY_MSG] = "Breaking attempt!"

        cli.send(msg)

        self.assertRaises(TypeError, cli.send, None)
        self.assertRaises(TypeError, cli.send, "hello")

    @unittest.skipUnless(sys.version_info[0] == 3, "Python 3 tests")
    def test_no_bytes(self):
        self.assertRaises(TypeError, asl.aslclient, "ident", b"faclity", 0)
        self.assertRaises(TypeError, asl.aslclient, b"ident", "faclity", 0)

        cli = asl.aslclient("ident", "facility", 0)
        self.assertIsInstance(cli, asl.aslclient)

        self.assertRaises(TypeError, cli.log, None, asl.ASL_LEVEL_NOTICE, b"hello world")

    @unittest.skipUnless(sys.version_info[0] == 2, "Python 2 tests")
    def test_with_unicode(self):
        cli = asl.aslclient(b"ident".decode('utf-8'), "facility", 0)
        self.assertIsInstance(cli, asl.aslclient)

        cli = asl.aslclient(b"ident", "facility".decode('utf-8'), 0)
        self.assertIsInstance(cli, asl.aslclient)

        cli.log(None, asl.ASL_LEVEL_NOTICE, b"hello world".decode('utf-8'))

    def test_add_remove(self):
        self.assertRaises(OSError, os.fstat, 99)

        cli = asl.aslclient("ident", "facility", 0)
        self.assertIsInstance(cli, asl.aslclient)

        cli.add_log_file(99)
        cli.remove_log_file(99)
        #self.assertRaises(OSError, cli.add_log_file, 99)
        #self.assertRaises(OSError, cli.remove_log_file, 99)

        cli.add_log_file(2)
        cli.remove_log_file(2)
        cli.remove_log_file(2)
        #self.assertRaises(OSError, cli.remove_log_file, 2)

    def test_search(self):
        cli = asl.aslclient("ident", "facility", 0)
        self.assertIsInstance(cli, asl.aslclient)

        msg = asl.aslmsg(asl.ASL_TYPE_QUERY)
        msg.set_query(asl.ASL_KEY_FACILITY, "com.apple.console", asl.ASL_QUERY_OP_EQUAL)

        info = None
        for info in cli.search(msg):
            self.assertIsInstance(info, asl.aslmsg)

        self.assertIsNot(info, None)

        msg = asl.aslmsg(asl.ASL_TYPE_QUERY)
        msg.set_query(asl.ASL_KEY_FACILITY, "com.apple.nosuchapp", asl.ASL_QUERY_OP_EQUAL)
        self.assertEqual(list(cli.search(msg)), [])

        msg = asl.aslmsg(asl.ASL_TYPE_QUERY)
        msg.set_query(asl.ASL_KEY_FACILITY, "com.apple.console", asl.ASL_QUERY_OP_EQUAL)
        self.assertNotEqual(list(cli.search(msg)), [])

    @unittest.skipUnless(LooseVersion(platform.mac_ver()[0]) >= LooseVersion("10.8"), "Requires OSX 10.8")
    def test_redirection(self):
        cli = asl.aslclient("ident", "facility", 0)
        self.assertIsInstance(cli, asl.aslclient)

        fd = os.open("/dev/null", os.O_WRONLY)

        cli.log_descriptor(None, asl.ASL_LEVEL_NOTICE, fd, asl.ASL_LOG_DESCRIPTOR_WRITE)

        self.assertRaises(ValueError, cli.log_descriptor, None, asl.ASL_LEVEL_NOTICE, fd, 44)
        self.assertRaises(TypeError, cli.log_descriptor, "u", asl.ASL_LEVEL_NOTICE, fd, asl.ASL_LOG_DESCRIPTOR_WRITE)

        #

        cli = asl.aslclient("ident", "facility", 0)
        self.assertIsInstance(cli, asl.aslclient)

        fd = os.open("/dev/null", os.O_WRONLY)

        msg = asl.aslmsg(asl.ASL_TYPE_MSG)
        msg[asl.ASL_KEY_FACILITY] = "com.apple.console"
        cli.log_descriptor(msg, asl.ASL_LEVEL_NOTICE, fd, asl.ASL_LOG_DESCRIPTOR_WRITE)

    @unittest.skipUnless(LooseVersion(platform.mac_ver()[0]) < LooseVersion("10.8"), "Requires OSX 10.8")
    def test_no_redirection(self):
        cli = asl.aslclient("ident", "facility", 0)
        self.assertIsInstance(cli, asl.aslclient)

        self.assertFalse(hasattr(cli, 'log_descriptor'))

    @unittest.skipUnless(LooseVersion(platform.mac_ver()[0]) >= LooseVersion("10.7"), "Requires OSX 10.7")
    def test_open_from_file(self):
        try:
            fd = os.open("asl.log", os.O_RDWR|os.O_CREAT, 0o660)
            cli = asl.open_from_file(fd, "ident", "facility")
            self.assertIsInstance(cli, asl.aslclient)

            #

            fd = os.open("asl.log", os.O_RDONLY, 0o660)
            self.assertRaises(OSError, asl.open_from_file, fd, "ident", "facility")

        finally:
            if os.path.exists("asl.log"):
                os.unlink("asl.log")

    @unittest.skipUnless(LooseVersion(platform.mac_ver()[0]) < LooseVersion("10.7"), "Requires OSX 10.7")
    def test_no_open_from_file(self):
        self.assertFalse(hasattr(asl, 'open_from_file'))

if __name__ == "__main__":
    unittest.main()
