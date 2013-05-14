import unittest
import operator
import sys

import asl

class TestMessage (unittest.TestCase):
    def test_creation(self):
        m = asl.aslmsg(asl.ASL_TYPE_MSG)
        self.assertIsInstance(m, asl.aslmsg)

        m = asl.aslmsg(asl.ASL_TYPE_QUERY)
        self.assertIsInstance(m, asl.aslmsg)

        self.assertRaises(ValueError, asl.aslmsg, 42)
        self.assertRaises(TypeError, asl.aslmsg)

    def test_attributes(self):
        m = asl.aslmsg(asl.ASL_TYPE_MSG)
        self.assertIsInstance(m, asl.aslmsg)

        self.assertEqual(m.keys(), set())
        self.assertEqual(m.asdict(), {})

        m['foo'] = 'bar'
        m['baz'] = 'hello'

        self.assertEqual(m.keys(), {'foo', 'baz'})
        self.assertEqual(m.asdict(), {'foo': 'bar', 'baz': 'hello'})

        self.assertEqual(m['foo'], 'bar')
        self.assertEqual(m['baz'], 'hello')

        self.assertRaises(TypeError, operator.setitem, m, 'aap', 42)
        self.assertRaises(TypeError, operator.setitem, m, 42, 'aap')
        self.assertRaises(KeyError, operator.getitem, m, 'nokey')

        del m['baz']
        self.assertEqual(m.keys(), {'foo'})
        self.assertEqual(m.asdict(), {'foo': 'bar'})

        del m['nokey']
        self.assertEqual(m.keys(), {'foo'})
        self.assertEqual(m.asdict(), {'foo': 'bar'})

    @unittest.skipUnless(sys.version_info[0] == 3, "Python 3 tests")
    def test_no_bytes_attributes(self):
        m = asl.aslmsg(asl.ASL_TYPE_MSG)
        self.assertIsInstance(m, asl.aslmsg)

        self.assertRaises(TypeError, operator.setitem, m, b'aap', 'hello')
        self.assertRaises(TypeError, operator.setitem, m, 'aap', b'hello')
        self.assertRaises(TypeError, m.set_query, 'aap', b'hello', asl.ASL_QUERY_OP_EQUAL)
        self.assertRaises(TypeError, m.set_query, b'aap', 'hello', asl.ASL_QUERY_OP_EQUAL)

    @unittest.skipUnless(sys.version_info[0] == 2, "Python 2 tests")
    def test_unicode_attributes(self):
        m = asl.aslmsg(asl.ASL_TYPE_MSG)
        self.assertIsInstance(m, asl.aslmsg)

        m[b'aap'.decode('utf-8')] =  'hello'
        m['noot'] =  b'world'.decode('utf-8')

        self.assertEqual(m.asdict(), {'aap': 'hello', 'noot': 'world' })

        m.set_query(b'key1'.decode('utf-8'), 'value1', asl.ASL_QUERY_OP_EQUAL)
        m.set_query(b'key2'.decode('utf-8'), 'value2', asl.ASL_QUERY_OP_EQUAL)

        self.assertEqual(m.asdict(), {'aap': 'hello', 'noot': 'world', 'key1': 'value1', 'key2': 'value2' })

    def test_set_query(self):
        m = asl.aslmsg(asl.ASL_TYPE_QUERY)
        self.assertIsInstance(m, asl.aslmsg)

        m.set_query("foo", "bar", asl.ASL_QUERY_OP_EQUAL)
        self.assertEqual(m.keys(), {'foo'})

        self.assertRaises(TypeError, m.set_query, 42, "foo", asl.ASL_QUERY_OP_EQUAL)
        self.assertRaises(TypeError, m.set_query, "key", 42, asl.ASL_QUERY_OP_EQUAL)
        self.assertRaises(TypeError, m.set_query, "key", "key", "hello")

if __name__ == "__main__":
    unittest.main()
