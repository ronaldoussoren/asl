import unittest
import platform

import asl

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


    @unittest.skipUnless(platform.mac_ver()[0] < "10.7", "Requires OSX 10.7")
    def test_no_aux(self):
        self.assertFalse(hasattr(asl, 'create_auxiliary_file'))
        self.assertFalse(hasattr(asl, 'close_auxiliary_file'))
        self.assertFalse(hasattr(asl, 'log_auxiliary_location'))

    @unittest.skipUnless(platform.mac_ver()[0] >= "10.7", "Requires OSX 10.7")
    def test_create_auxiliary_file(self):
        self.fail()

    @unittest.skipUnless(platform.mac_ver()[0] >= "10.7", "Requires OSX 10.7")
    def test_log_auxiliary_location(self):
        self.fail()


if __name__ == "__main__":
    unittest.main()
