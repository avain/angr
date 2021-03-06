import nose
import angr
from simuvex.s_type import SimTypePointer, SimTypeFunction, SimTypeChar, SimTypeInt
from angr.surveyors.caller import Callable
from angr.errors import AngrCallableMultistateError

import logging
l = logging.getLogger("angr_tests")

import os
location = str(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../binaries/tests'))

addresses_fauxware = {
    'armel': 0x8524,
    'armhf': 0x104c9,   # addr+1 to force thumb
    'i386': 0x8048524,
    'mips': 0x400710,
    'mipsel': 0x4006d0,
    'ppc': 0x1000054c,
    'ppc64': 0x10000698,
    'x86_64': 0x400664
}

addresses_manysum = {
    'armel': 0x1041c,
    'armhf': 0x103bd,
    'i386': 0x80483d8,
    'mips': 0x400704,
    'mipsel': 0x400704,
    'ppc': 0x10000418,
    'ppc64': 0x10000500,
    'x86_64': 0x4004ca
}

def run_fauxware(arch):
    addr = addresses_fauxware[arch]
    p = angr.Project(location + '/' + arch + '/fauxware')
    charstar = SimTypePointer(p.arch, SimTypeChar())
    prototype = SimTypeFunction((charstar, charstar), SimTypeInt(p.arch.bits, False))
    authenticate = p.factory.callable(addr, prototype=prototype, toc=0x10018E80 if arch == 'ppc64' else None, concrete_only=True)
    nose.tools.assert_equal(authenticate("asdf", "SOSNEAKY").model.value, 1)
    nose.tools.assert_raises(AngrCallableMultistateError, authenticate, "asdf", "NOSNEAKY")

def run_manysum(arch):
    addr = addresses_manysum[arch]
    p = angr.Project(location + '/' + arch + '/manysum')
    inttype = SimTypeInt(p.arch.bits, False)
    prototype = SimTypeFunction([inttype]*11, inttype)
    sumlots = Callable(p, addr, prototype=prototype)
    result = sumlots(1,2,3,4,5,6,7,8,9,10,11)
    nose.tools.assert_false(result.symbolic)
    nose.tools.assert_equal(result.model.value, sum(xrange(12)))

def test_fauxware():
    for arch in addresses_fauxware:
        yield run_fauxware, arch

def test_manysum():
    for arch in addresses_manysum:
        yield run_manysum, arch

if __name__ == "__main__":
    for func, march in test_fauxware():
        print 'testing ' + march
        func(march)
    for func, march in test_manysum():
        print 'testing ' + march
        func(march)
