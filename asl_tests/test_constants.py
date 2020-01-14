import unittest

import asl


class TestConstant(unittest.TestCase):
    def test_query_options(self):
        self.assertEqual(asl.ASL_QUERY_OP_CASEFOLD, 0x0010)
        self.assertEqual(asl.ASL_QUERY_OP_PREFIX, 0x0020)
        self.assertEqual(asl.ASL_QUERY_OP_SUFFIX, 0x0040)
        self.assertEqual(asl.ASL_QUERY_OP_SUBSTRING, 0x0060)
        self.assertEqual(asl.ASL_QUERY_OP_NUMERIC, 0x0080)
        self.assertEqual(asl.ASL_QUERY_OP_REGEX, 0x0100)
        self.assertEqual(asl.ASL_QUERY_OP_EQUAL, 0x0001)
        self.assertEqual(asl.ASL_QUERY_OP_GREATER, 0x0002)
        self.assertEqual(asl.ASL_QUERY_OP_GREATER_EQUAL, 0x0003)
        self.assertEqual(asl.ASL_QUERY_OP_LESS, 0x0004)
        self.assertEqual(asl.ASL_QUERY_OP_LESS_EQUAL, 0x0005)
        self.assertEqual(asl.ASL_QUERY_OP_NOT_EQUAL, 0x0006)
        self.assertEqual(asl.ASL_QUERY_OP_TRUE, 0x0007)

    def test_level_numbers(self):
        self.assertEqual(asl.ASL_LEVEL_EMERG, 0)
        self.assertEqual(asl.ASL_LEVEL_ALERT, 1)
        self.assertEqual(asl.ASL_LEVEL_CRIT, 2)
        self.assertEqual(asl.ASL_LEVEL_ERR, 3)
        self.assertEqual(asl.ASL_LEVEL_WARNING, 4)
        self.assertEqual(asl.ASL_LEVEL_NOTICE, 5)
        self.assertEqual(asl.ASL_LEVEL_INFO, 6)
        self.assertEqual(asl.ASL_LEVEL_DEBUG, 7)

    def test_level_names(self):
        self.assertEqual(asl.ASL_STRING_EMERG, "Emergency")
        self.assertEqual(asl.ASL_STRING_ALERT, "Alert")
        self.assertEqual(asl.ASL_STRING_CRIT, "Critical")
        self.assertEqual(asl.ASL_STRING_ERR, "Error")
        self.assertEqual(asl.ASL_STRING_WARNING, "Warning")
        self.assertEqual(asl.ASL_STRING_NOTICE, "Notice")
        self.assertEqual(asl.ASL_STRING_INFO, "Info")
        self.assertEqual(asl.ASL_STRING_DEBUG, "Debug")

    def test_standard_attributes(self):
        self.assertEqual(asl.ASL_KEY_TIME, "Time")
        self.assertEqual(asl.ASL_KEY_TIME_NSEC, "TimeNanoSec")
        self.assertEqual(asl.ASL_KEY_HOST, "Host")
        self.assertEqual(asl.ASL_KEY_SENDER, "Sender")
        self.assertEqual(asl.ASL_KEY_FACILITY, "Facility")
        self.assertEqual(asl.ASL_KEY_PID, "PID")
        self.assertEqual(asl.ASL_KEY_UID, "UID")
        self.assertEqual(asl.ASL_KEY_GID, "GID")
        self.assertEqual(asl.ASL_KEY_LEVEL, "Level")
        self.assertEqual(asl.ASL_KEY_MSG, "Message")
        self.assertEqual(asl.ASL_KEY_READ_UID, "ReadUID")
        self.assertEqual(asl.ASL_KEY_READ_GID, "ReadGID")
        self.assertEqual(asl.ASL_KEY_EXPIRE_TIME, "ASLExpireTime")
        self.assertEqual(asl.ASL_KEY_MSG_ID, "ASLMessageID")
        self.assertEqual(asl.ASL_KEY_SESSION, "Session")
        self.assertEqual(asl.ASL_KEY_REF_PID, "RefPID")
        self.assertEqual(asl.ASL_KEY_REF_PROC, "RefProc")
        self.assertEqual(asl.ASL_KEY_AUX_TITLE, "ASLAuxTitle")
        self.assertEqual(asl.ASL_KEY_AUX_UTI, "ASLAuxUTI")
        self.assertEqual(asl.ASL_KEY_AUX_URL, "ASLAuxURL")
        self.assertEqual(asl.ASL_KEY_AUX_DATA, "ASLAuxData")
        self.assertEqual(asl.ASL_KEY_OPTION, "ASLOption")
        self.assertEqual(asl.ASL_KEY_MODULE, "ASLModule")
        self.assertEqual(asl.ASL_KEY_SENDER_INSTANCE, "SenderInstance")
        self.assertEqual(asl.ASL_KEY_SENDER_MACH_UUID, "SenderMachUUID")
        self.assertEqual(asl.ASL_KEY_FINAL_NOTIFICATION, "ASLFinalNotification")
        self.assertEqual(asl.ASL_KEY_OS_ACTIVITY_ID, "OSActivityID")

    def test_message_types(self):
        self.assertEqual(asl.ASL_TYPE_UNDEF, 0xFFFFFFFF)
        self.assertEqual(asl.ASL_TYPE_MSG, 0)
        self.assertEqual(asl.ASL_TYPE_QUERY, 1)
        self.assertEqual(asl.ASL_TYPE_LIST, 2)
        self.assertEqual(asl.ASL_TYPE_FILE, 3)
        self.assertEqual(asl.ASL_TYPE_STORE, 4)
        self.assertEqual(asl.ASL_TYPE_CLIENT, 5)

    def test_match_directions(self):
        self.assertEqual(asl.ASL_MATCH_DIRECTION_FORWARD, 1)
        self.assertEqual(asl.ASL_MATCH_DIRECTION_REVERSE, -1)

    def test_open_options(self):
        self.assertEqual(asl.ASL_OPT_OPEN_WRITE, 0x00000001)
        self.assertEqual(asl.ASL_OPT_CREATE_STORE, 0x00000002)

        self.assertEqual(asl.ASL_OPT_STDERR, 0x00000001)
        self.assertEqual(asl.ASL_OPT_NO_DELAY, 0x00000002)
        self.assertEqual(asl.ASL_OPT_NO_REMOTE, 0x00000004)

    def test_format_options(self):
        self.assertEqual(asl.ASL_MSG_FMT_RAW, "raw")
        self.assertEqual(asl.ASL_MSG_FMT_STD, "std")
        self.assertEqual(asl.ASL_MSG_FMT_BSD, "bsd")
        self.assertEqual(asl.ASL_MSG_FMT_XML, "xml")
        self.assertEqual(asl.ASL_MSG_FMT_MSG, "msg")
        self.assertEqual(asl.ASL_TIME_FMT_SEC, "sec")
        self.assertEqual(asl.ASL_TIME_FMT_UTC, "utc")
        self.assertEqual(asl.ASL_TIME_FMT_LCL, "lcl")

    def test_encode_options(self):
        self.assertEqual(asl.ASL_ENCODE_NONE, 0)
        self.assertEqual(asl.ASL_ENCODE_SAFE, 1)
        self.assertEqual(asl.ASL_ENCODE_ASL, 2)
        self.assertEqual(asl.ASL_ENCODE_XML, 3)

    def test_filter_masks(self):
        self.assertEqual(asl.ASL_FILTER_MASK_EMERG, 0x01)
        self.assertEqual(asl.ASL_FILTER_MASK_ALERT, 0x02)
        self.assertEqual(asl.ASL_FILTER_MASK_CRIT, 0x04)
        self.assertEqual(asl.ASL_FILTER_MASK_ERR, 0x08)
        self.assertEqual(asl.ASL_FILTER_MASK_WARNING, 0x10)
        self.assertEqual(asl.ASL_FILTER_MASK_NOTICE, 0x20)
        self.assertEqual(asl.ASL_FILTER_MASK_INFO, 0x40)
        self.assertEqual(asl.ASL_FILTER_MASK_DEBUG, 0x80)

    def test_descriptor_types(self):
        self.assertEqual(asl.ASL_LOG_DESCRIPTOR_READ, 1)
        self.assertEqual(asl.ASL_LOG_DESCRIPTOR_WRITE, 2)

    def test_api_version(self):
        self.assertEqual(asl.ASL_API_VERSION, 20150225)


if __name__ == "__main__":
    unittest.main()
