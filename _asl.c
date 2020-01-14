/*
 * Bindings to the ASL library on Mac OS X
 */
#include "Python.h"
#include <asl.h>

typedef struct {
    PyObject_HEAD

    aslclient value;
} ASLClientObject;

typedef struct {
    PyObject_HEAD

    aslmsg value;
    int owned;
} ASLMessageObject;

typedef struct {
    PyObject_HEAD

    aslresponse value;
} ASLResponseObject;


static PyObject* new_response(aslresponse value);
static PyObject* new_message(aslmsg value, int owned);
static PyObject* new_client(aslclient value);


/* Response type */

static void response_dealloc(PyObject* self);
static PyObject* response_iter(PyObject* self);
static PyObject* response_iternext(PyObject* self);

static PyTypeObject ASLResponseType = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    .tp_name        = "asl.aslresponse",
    .tp_basicsize   = sizeof(ASLResponseObject),
    .tp_itemsize    = 0,
    .tp_getattro    = PyObject_GenericGetAttr,
    .tp_setattro    = PyObject_GenericSetAttr,
    .tp_flags       = Py_TPFLAGS_DEFAULT,
    .tp_iter        = response_iter,
    .tp_iternext    = response_iternext,
    .tp_dealloc     = response_dealloc,
};

static PyObject*
new_response(aslresponse response)
{
    ASLResponseObject* result = PyObject_New(ASLResponseObject, &ASLResponseType);
    if (result == NULL) {
        aslresponse_free(response);
        return NULL;
    }

    result->value = response;
    return (PyObject*)result;
}

static void
response_dealloc(PyObject* self)
{
    ASLResponseObject* r = (ASLResponseObject*)self;

    aslresponse_free(r->value);
    PyObject_DEL(self);
}

static PyObject*
response_iter(PyObject* self)
{
    Py_INCREF(self);
    return self;
}

static PyObject*
response_iternext(PyObject* self)
{
    ASLResponseObject* r = (ASLResponseObject*)self;
    aslmsg msg = aslresponse_next(r->value);

    if (msg == NULL) {
        /* End of iteration */
        return NULL;
    } else {
        return new_message(msg, 0);
    }
}


/* Message type */

#define ASLMessage_Check(object) PyObject_TypeCheck((object), &ASLMessageType)
#define ASLMessage_GET(object) (((ASLMessageObject*)(object))->value)

static PyObject* message_new(PyTypeObject* cls, PyObject* args, PyObject* kwds);
static void message_dealloc(PyObject* self);
static PyObject* message_keys(PyObject* self);
static PyObject* message_asdict(PyObject* self);
static PyObject* message_set_query(PyObject* self, PyObject* args, PyObject* kwds);
static PyObject* message_getitem(PyObject* self, PyObject* key);
static int message_setitem(PyObject* self, PyObject* key, PyObject* value);


static PyMethodDef message_methods[] = {
    {
        "keys",
        (PyCFunction)message_keys,
        METH_NOARGS,
        "List of message attributes",
    },
    {
        "asdict",
        (PyCFunction)message_asdict,
        METH_NOARGS,
        "Dict with all attribute names and values",
    },
    {
        "set_query",
        (PyCFunction)message_set_query,
        METH_VARARGS|METH_KEYWORDS,
        "Set a query element",
    },
    { 0, 0, 0, 0 } /* SENTINEL */
};

static PyMappingMethods message_mapping = {
    /* No __len__ because it is expensive to calculate the number of attributes */
    .mp_length = NULL,
    .mp_subscript = message_getitem,
    .mp_ass_subscript = message_setitem,
};


static PyTypeObject ASLMessageType = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    .tp_name        = "asl.aslmsg",
    .tp_basicsize   = sizeof(ASLMessageObject),
    .tp_itemsize    = 0,
    .tp_getattro    = PyObject_GenericGetAttr,
    .tp_setattro    = PyObject_GenericSetAttr,
    .tp_flags       = Py_TPFLAGS_DEFAULT,
    .tp_dealloc     = message_dealloc,
    .tp_methods        = message_methods,
    .tp_new        = message_new,
    .tp_as_mapping  = &message_mapping,
};

static PyObject*
new_message(aslmsg msg, int owned)
{
    ASLMessageObject* result = PyObject_New(ASLMessageObject, &ASLMessageType);
    if (result == NULL) {
        asl_free(msg);
        return NULL;
    }

    result->value = msg;
    result->owned = owned;
    return (PyObject*)result;
}

static PyObject*
message_new(PyTypeObject* cls, PyObject* args, PyObject* kwds)
{
static char* kw_args[] = { "type", NULL };
    uint32_t type;
    aslmsg msg;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "I", kw_args, (unsigned int*)&type)) {
        return NULL;
    }

    if (type != ASL_TYPE_MSG && type != ASL_TYPE_QUERY) {
        PyErr_SetString(PyExc_ValueError, "Invalid message type");
        return NULL;
    }

    msg = asl_new(type);
    if (msg == NULL) {
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL;
    }

    return new_message(msg, 1);
}



static void
message_dealloc(PyObject* self)
{
    ASLMessageObject* r = (ASLMessageObject*)self;

    if (r->owned) {
        asl_free(r->value);
    }
    PyObject_DEL(self);
}

static PyObject*
message_getitem(PyObject* self, PyObject* key)
{
    ASLMessageObject* r = (ASLMessageObject*)self;
    PyObject* bytes = NULL;
    const char* c_key;
    const char* c_value;

    if (PyUnicode_Check(key)) {
        bytes = PyUnicode_AsUTF8String(key);
        if (bytes == NULL) {
            return NULL;
        }

        c_key = PyBytes_AsString(bytes);
        if (c_key == NULL) {
            Py_XDECREF(bytes);
            return NULL;
        }

    } else {
        PyErr_SetObject(PyExc_KeyError, key);
        return NULL;
    }

    c_value = asl_get(r->value, c_key);
    if (c_value == NULL) {
        PyErr_SetString(PyExc_KeyError, c_key);
        Py_XDECREF(bytes);
        return NULL;
    }

    Py_XDECREF(bytes);
    return Py_BuildValue("s", c_value);
}

static int
message_setitem(PyObject* self, PyObject* key, PyObject* value)
{
    ASLMessageObject* r = (ASLMessageObject*)self;
    PyObject* key_bytes = NULL;
    PyObject* value_bytes = NULL;
    const char* c_key;
    const char* c_value;

    if (PyUnicode_Check(key)) {
        key_bytes = PyUnicode_AsUTF8String(key);
        if (key_bytes == NULL) {
            return -1;
        }

        c_key = PyBytes_AsString(key_bytes);
        if (c_key == NULL) {
            Py_XDECREF(key_bytes);
            return -1;
        }

    } else {
        PyErr_Format(PyExc_TypeError, "Expecting a string, got instance of '%s'", Py_TYPE(key)->tp_name);
        return -1;
    }

    if (value == NULL) {
        if (asl_unset(r->value, c_key) != 0) {
            PyErr_SetFromErrno(PyExc_OSError);
            Py_XDECREF(key_bytes);
            return -1;
        }
        Py_XDECREF(key_bytes);
        return 0;
    }

    if (PyUnicode_Check(value)) {
        value_bytes = PyUnicode_AsUTF8String(value);
        if (value_bytes == NULL) {
            Py_XDECREF(key_bytes);
            return -1;
        }
        c_value = PyBytes_AsString(value_bytes);;
        if (c_value == NULL) {
            Py_XDECREF(key_bytes);
            Py_XDECREF(value_bytes);
            return -1;
        }

    } else {
        PyErr_Format(PyExc_TypeError, "Expecting a string, got instance of '%s'", Py_TYPE(value)->tp_name);
        Py_XDECREF(key_bytes);
        return -1;
    }

    if (asl_set(r->value, c_key, c_value) != 0) {
        PyErr_SetFromErrno(PyExc_OSError);
        Py_XDECREF(key_bytes);
        Py_XDECREF(value_bytes);
        return -1;
    }
    Py_XDECREF(key_bytes);
    Py_XDECREF(value_bytes);
    return 0;
}


static PyObject*
message_keys(PyObject* self)
{
    ASLMessageObject* r = (ASLMessageObject*)self;
    PyObject* result;
    uint32_t n = 0;
    const char* key;

    result = PySet_New(NULL);
    if (r == NULL) {
        return NULL;
    }

    while (1) {
        PyObject* o;

        key = asl_key(r->value, n++);
        if (key == NULL) {
            break;
        }

        o = PyUnicode_FromString(key);
        if (o == NULL) {
            Py_DECREF(result);
            return NULL;
        }

        if (PySet_Add(result, o) < 0) {
            Py_DECREF(o);
            return NULL;
        }

        Py_DECREF(o);
    }
    return result;
}

static PyObject*
message_asdict(PyObject* self)
{
    ASLMessageObject* r = (ASLMessageObject*)self;
    PyObject* result;
    uint32_t n = 0;
    const char* key;

    result = PyDict_New();
    if (r == NULL) {
        return NULL;
    }

    while (1) {
        PyObject* o;
        const char* value;


        key = asl_key(r->value, n++);
        if (key == NULL) {
            break;
        }

        value = asl_get(r->value, key);
        if (value == NULL) {
            /* Shouldn't happen */
            PyErr_SetFromErrno(PyExc_OSError);
            Py_DECREF(result);
            return NULL;
        }


        o = PyUnicode_FromString(value);
        if (o == NULL) {
            Py_DECREF(result);
            return NULL;
        }

        if (PyDict_SetItemString(result, key, o) < 0) {
            Py_DECREF(o);
            return NULL;
        }

        Py_DECREF(o);
    }
    return result;
}

static PyObject*
message_set_query(PyObject* self, PyObject* args, PyObject* kwds)
{
    static char* kw_list[] = { "key", "value", "operation", NULL };
    ASLMessageObject* r = (ASLMessageObject*)self;
    const char* key;
    const char* value;
    uint32_t op;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "ssI", kw_list, &key, &value, &op)) {
        return NULL;
    }

    if (asl_set_query(r->value, key, value, op) != 0) {
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}


/* Client type */

static PyObject* client_new(PyTypeObject* cls, PyObject* args, PyObject* kwds);
static void client_dealloc(PyObject* self);
static PyObject* client_add_log_file(PyObject* self, PyObject* args, PyObject* kwds);
static PyObject* client_remove_log_file(PyObject* self, PyObject* args, PyObject* kwds);
static PyObject* client_set_filter(PyObject* self, PyObject* args, PyObject* kwds);
static PyObject* client_log(PyObject* self, PyObject* args, PyObject* kwds);
static PyObject* client_send(PyObject* self, PyObject* args, PyObject* kwds);
static PyObject* client_search(PyObject* self, PyObject* args, PyObject* kwds);
#if (MAC_OS_X_VERSION_MAX_ALLOWED >= MAC_OS_X_VERSION_10_8)
static PyObject* client_log_descriptor(PyObject* self, PyObject* args, PyObject* kwds);
#endif
static PyObject* client_close(PyObject* self);
static PyObject* client_enter(PyObject* self);
static PyObject* client_exit(PyObject* self, PyObject* args);

static PyMethodDef client_methods[] = {
    {
        "add_log_file",
        (PyCFunction)client_add_log_file,
        METH_VARARGS|METH_KEYWORDS,
        NULL,
    },
    {
        "remove_log_file",
        (PyCFunction)client_remove_log_file,
        METH_VARARGS|METH_KEYWORDS,
        NULL,
    },
    {
        "set_filter",
        (PyCFunction)client_set_filter,
        METH_VARARGS|METH_KEYWORDS,
        NULL,
    },
    {
        "log",
        (PyCFunction)client_log,
        METH_VARARGS|METH_KEYWORDS,
        NULL,
    },
    {
        "send",
        (PyCFunction)client_send,
        METH_VARARGS|METH_KEYWORDS,
        NULL,
    },
    {
        "search",
        (PyCFunction)client_search,
        METH_VARARGS|METH_KEYWORDS,
        NULL,
    },
#if (MAC_OS_X_VERSION_MAX_ALLOWED >= MAC_OS_X_VERSION_10_8)
    {
        "log_descriptor",
        (PyCFunction)client_log_descriptor,
        METH_VARARGS|METH_KEYWORDS,
        NULL,
    },
#endif
    {
        "close",
        (PyCFunction)client_close,
        METH_NOARGS,
        NULL,
    },
    {
        "__enter__",
        (PyCFunction)client_enter,
        METH_NOARGS,
        NULL,
    },
    {
        "__exit__",
        (PyCFunction)client_exit,
        METH_VARARGS,
        NULL,
    },

    { 0, 0, 0, 0 } /* SENTINEL */
};

static PyTypeObject ASLClientType = {
    PyVarObject_HEAD_INIT(&PyType_Type, 0)
    .tp_name        = "asl.aslclient",
    .tp_basicsize   = sizeof(ASLClientObject),
    .tp_itemsize    = 0,
    .tp_getattro    = PyObject_GenericGetAttr,
    .tp_setattro    = PyObject_GenericSetAttr,
    .tp_flags       = Py_TPFLAGS_DEFAULT,
    .tp_dealloc     = client_dealloc,
    .tp_methods        = client_methods,
    .tp_new        = client_new,
};

static PyObject*
new_client(aslclient cli)
{
    ASLClientObject* result = PyObject_New(ASLClientObject, &ASLClientType);
    if (result == NULL) {
        asl_close(cli);
        return NULL;
    }

    result->value = cli;
    return (PyObject*)result;
}

static PyObject*
client_new(PyTypeObject* cls, PyObject* args, PyObject* kwds)
{
static char* kw_args[] = { "ident", "facility", "options", NULL };
    const char* ident;
    const char* facility;
    uint32_t opts;
    aslclient cli;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "zsI", kw_args, &ident, &facility, &opts)) {
        return NULL;
    }

    cli = asl_open(ident, facility, opts);
    if (cli == NULL) {
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL;
    }

    return new_client(cli);
}

static void
client_dealloc(PyObject* self)
{
    ASLClientObject* r = (ASLClientObject*)self;

    if (r->value) {
        asl_close(r->value);
    }
    PyObject_DEL(self);
}

static PyObject*
client_add_log_file(PyObject* self, PyObject* args, PyObject* kwds)
{
    static char* kw_list[] = { "fd", NULL };
        ASLClientObject* r = (ASLClientObject*)self;
    int fd;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "i", kw_list, &fd)) {
        return NULL;
    }

    if (r->value == NULL) {
        PyErr_SetString(PyExc_ValueError, "Client is closed");
        return NULL;
    }

    if (asl_add_log_file(r->value, fd) != 0) {
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
client_remove_log_file(PyObject* self, PyObject* args, PyObject* kwds)
{
    static char* kw_list[] = { "fd", NULL };
        ASLClientObject* r = (ASLClientObject*)self;
    int fd;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "i", kw_list, &fd)) {
        return NULL;
    }

    if (r->value == NULL) {
        PyErr_SetString(PyExc_ValueError, "Client is closed");
        return NULL;
    }

    if (asl_remove_log_file(r->value, fd) != 0) {
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
client_set_filter(PyObject* self, PyObject* args, PyObject* kwds)
{
    static char* kw_list[] = { "filter", NULL };
        ASLClientObject* r = (ASLClientObject*)self;
    int filter;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "i", kw_list, &filter)) {
        return NULL;
    }

    if (r->value == NULL) {
        PyErr_SetString(PyExc_ValueError, "Client is closed");
        return NULL;
    }

    filter = asl_set_filter(r->value, filter);
    return Py_BuildValue("i", filter);
}

static PyObject*
client_close(PyObject* self)
{
        ASLClientObject* r = (ASLClientObject*)self;
    if (r->value != NULL) {
        asl_close(r->value);
        r->value = NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
client_enter(PyObject* self)
{
        ASLClientObject* r = (ASLClientObject*)self;
    if (r->value == NULL) {
        PyErr_SetString(PyExc_ValueError, "Client is closed");
        return NULL;
    }
    Py_INCREF(self);
    return self;
}

static PyObject*
client_exit(PyObject* self, PyObject* args)
{
        ASLClientObject* r = (ASLClientObject*)self;
    PyObject* exc_type;
    PyObject* exc_val;
    PyObject* exc_tb;

    if (!PyArg_ParseTuple(args, "OOO", &exc_type, &exc_val, &exc_tb)) {
        return NULL;
    }

    if (r->value != NULL) {
        asl_close(r->value);
        r->value = NULL;
    }

    Py_INCREF(Py_False);
    return Py_False;
}

static PyObject*
client_send(PyObject* self, PyObject* args, PyObject* kwds)
{
    static char* kw_list[] = { "msg", NULL };
        ASLClientObject* r = (ASLClientObject*)self;
    PyObject* msg;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!", kw_list, &ASLMessageType, &msg)) {
        return NULL;
    }

    if (r->value == NULL) {
        PyErr_SetString(PyExc_ValueError, "Client is closed");
        return NULL;
    }

    if (asl_send(r->value, ASLMessage_GET(msg)) != 0) {
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
client_search(PyObject* self, PyObject* args, PyObject* kwds)
{
    static char* kw_list[] = { "msg", NULL };
        ASLClientObject* r = (ASLClientObject*)self;
    PyObject* msg;
    aslresponse resp;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!", kw_list, &ASLMessageType, &msg)) {
        return NULL;
    }

    if (r->value == NULL) {
        PyErr_SetString(PyExc_ValueError, "Client is closed");
        return NULL;
    }

    resp = asl_search(r->value, ASLMessage_GET(msg));
    if (resp == NULL) {
        /* It is not possible to detect the difference between 'no results'
         * and 'invalid query'.
         */
        PyObject* res;
        PyObject* tmp = PyTuple_New(0);
        if (tmp == NULL) {
            return NULL;
        }
        res = PyObject_GetIter(tmp);
        Py_DECREF(tmp);
        return res;
    }

    return new_response(resp);
}

static PyObject*
client_log(PyObject* self, PyObject* args, PyObject* kwds)
{
    static char* kw_list[] = { "msg", "level", "text", NULL };
        ASLClientObject* r = (ASLClientObject*)self;
    PyObject* msg;
    int level;
    const char* text;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "Ois", kw_list, &msg, &level, &text)) {
        return NULL;
    }

    if (msg != Py_None && !ASLMessage_Check(msg)) {
        PyErr_Format(PyExc_TypeError, "Expected aclmsg instance or None, got instance of '%s'",
                Py_TYPE(msg)->tp_name);
        return NULL;
    }

    if (r->value == NULL) {
        PyErr_SetString(PyExc_ValueError, "Client is closed");
        return NULL;
    }

    if (asl_log(r->value, msg == Py_None ? NULL : ASLMessage_GET(msg), level, "%s", text) != 0) {
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

#if (MAC_OS_X_VERSION_MAX_ALLOWED >= MAC_OS_X_VERSION_10_8)
static PyObject*
client_log_descriptor(PyObject* self, PyObject* args, PyObject* kwds)
{
    static char* kw_list[] = { "msg", "level", "fd", "fd_type", NULL };
        ASLClientObject* r = (ASLClientObject*)self;
    PyObject* msg;
    int level;
    int fd;
    int fd_type;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "Oiii", kw_list, &msg, &level, &fd, &fd_type)) {
        return NULL;
    }

    if (msg != Py_None && !ASLMessage_Check(msg)) {
        PyErr_Format(PyExc_TypeError, "Expected aclmsg instance or None, got instance of '%s'",
                Py_TYPE(msg)->tp_name);
        return NULL;
    }

    if (r->value == NULL) {
        PyErr_SetString(PyExc_ValueError, "Client is closed");
        return NULL;
    }

    if (fd_type != ASL_LOG_DESCRIPTOR_WRITE && fd_type != ASL_LOG_DESCRIPTOR_READ) {
        PyErr_SetString(PyExc_ValueError, "Invalid fd_type");
        return NULL;
    }

    if (asl_log_descriptor(r->value, msg == Py_None ? NULL : ASLMessage_GET(msg), level, fd, fd_type) != 0) {
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL;
    }
    Py_INCREF(Py_None);
    return Py_None;
}
#endif


/* Global functions */

#if (MAC_OS_X_VERSION_MAX_ALLOWED >= MAC_OS_X_VERSION_10_7)
static PyObject*
log_auxiliary_location(PyObject* self __attribute__((__unused__)), PyObject* args, PyObject* kwds)
{
static char* kw_list[] = { "msg", "title", "uti", "url", NULL };

    PyObject* msg;
    char* title;
    char* uti;
    char* url;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!szs", kw_list, &ASLMessageType, &msg, &title, &uti, &url)) {
        return NULL;
    }

    if (asl_log_auxiliary_location(ASLMessage_GET(msg), title, uti, url) != 0) {
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
create_auxiliary_file(PyObject* self __attribute__((__unused__)), PyObject* args, PyObject* kwds)
{
static char* kw_list[] = { "msg", "title", "uti", NULL };

    PyObject* msg;
    char* title;
    char* uti;
    int fd;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "O!sz", kw_list, &ASLMessageType, &msg, &title, &uti)) {
        return NULL;
    }

    if (asl_create_auxiliary_file(ASLMessage_GET(msg), title, uti, &fd) != 0) {
        return NULL;
    }

    return Py_BuildValue("i", fd);
}

static PyObject*
close_auxiliary_file(PyObject* self __attribute__((__unused__)), PyObject* args, PyObject* kwds)
{
static char* kw_list[] = { "fd", NULL };

    int fd;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "i", kw_list, &fd)) {
        return NULL;
    }

    if (asl_close_auxiliary_file(fd)) {
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL;
    }

    Py_INCREF(Py_None);
    return Py_None;
}

static PyObject*
open_from_file(PyObject* self __attribute__((__unused__)), PyObject* args, PyObject* kwds)
{
static char* kw_list[] = { "fd", "ident", "facility", NULL };

    int fd;
    const char* ident;
    const char* facility;
    aslclient cli;

    if (!PyArg_ParseTupleAndKeywords(args, kwds, "izs", kw_list, &fd, &ident, &facility)) {
        return NULL;
    }

    cli = asl_open_from_file(fd, ident, facility);
    if (cli == NULL) {
        PyErr_SetFromErrno(PyExc_OSError);
        return NULL;
    }

    return new_client(cli);
}
#endif


static PyMethodDef mod_methods[] = {
#if (MAC_OS_X_VERSION_MAX_ALLOWED >= MAC_OS_X_VERSION_10_7)
    {
        "log_auxiliary_location",
        (PyCFunction)log_auxiliary_location,
        METH_VARARGS|METH_KEYWORDS,
        NULL
    },
    {
        "create_auxiliary_file",
        (PyCFunction)create_auxiliary_file,
        METH_VARARGS|METH_KEYWORDS,
        NULL
    },
    {
        "close_auxiliary_file",
        (PyCFunction)close_auxiliary_file,
        METH_VARARGS|METH_KEYWORDS,
        NULL
    },
    {
        "open_from_file",
        (PyCFunction)open_from_file,
        METH_VARARGS|METH_KEYWORDS,
        NULL
    },
#endif

    { 0, 0, 0, 0 } /* SENTINEL */
};


/* Module init */

static PyModuleDef aslmodule = {
    PyModuleDef_HEAD_INIT,
    "asl._asl",
    NULL,
    -1,
    mod_methods, NULL, NULL, NULL, NULL
};

PyMODINIT_FUNC
PyInit__asl(void)
{
    PyObject* m;

    m = PyModule_Create(&aslmodule);
    if (m == NULL) {
        return NULL;
    }

    if (PyType_Ready(&ASLResponseType) < 0) {
        return NULL;
    }
    if (PyType_Ready(&ASLMessageType) < 0) {
        return NULL;
    }
    if (PyType_Ready(&ASLClientType) < 0) {
        return NULL;
    }

#if (MAC_OS_X_VERSION_MAX_ALLOWED >= MAC_OS_X_VERSION_10_8) && (MAC_OS_X_VERSION_MIN_REQUIRED < MAC_OS_X_VERSION_10_8)
    if (asl_log_descriptor == NULL) {
        if (PyDict_DelItemString(ASLClientType.tp_dict, "log_descriptor") < 0) {
            return NULL;
        }
    }
#endif

#if (MAC_OS_X_VERSION_MAX_ALLOWED >= MAC_OS_X_VERSION_10_7) && (MAC_OS_X_VERSION_MIN_REQUIRED < MAC_OS_X_VERSION_10_7)
    if (asl_create_auxiliary_file == NULL) {
        if (PyDict_DelItemString(PyModule_GetDict(m), "create_auxiliary_file") < 0) {
            return NULL;
        }
        if (PyDict_DelItemString(PyModule_GetDict(m), "close_auxiliary_file") < 0) {
            return NULL;
        }
    }
    if (asl_log_auxiliary_location == NULL) {
        if (PyDict_DelItemString(PyModule_GetDict(m), "log_auxiliary_location") < 0) {
            return NULL;
        }
    }
    if (asl_open_from_file == NULL) {
        if (PyDict_DelItemString(PyModule_GetDict(m), "open_from_file") < 0) {
            return NULL;
        }
    }
#endif

    if (PyModule_AddObject(m, "aslresponse", (PyObject*)&ASLResponseType) < 0) {
        return NULL;
    }
    if (PyModule_AddObject(m, "aslmsg", (PyObject*)&ASLMessageType) < 0) {
        return NULL;
    }
    if (PyModule_AddObject(m, "aslclient", (PyObject*)&ASLClientType) < 0) {
        return NULL;
    }

    return m;
}
