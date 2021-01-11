# len 4
# player defender
# 0 [changePass],
# 1 [flash],
#
# 2 [throttle],
# 3 [wait],


# len 5
# player attacker
#
# 1 [phishEmployee],
# 2 [phishVendor],
#
# 3 [exploitPOS],
# 4 [exploitPay],
# 5 [exploitWeb]

def get_obs(a):
    obs_dict = {
        0: .2,
        1: .1,
        2: .1,
        3: .05,
        4: .05,
    }
    return obs_dict.get(a)


def apply_attacker_action(a, state):
    if a == 0:
        state["a_has_pay_pass"] = True
    elif a == 1:
        state["a_has_web_pass"] = True
    elif a == 2:
        if state["a_has_pay_pass"] or state["a_has_pay_exploit"]:
            state["a_has_pos_exploit"] = True
    elif a == 3:
        if state["a_has_web_pass"] or state["a_has_web_exploit"]:
            state["a_has_pay_exploit"] = True
    elif a == 4:
        state["a_has_web_exploit"] = True


# 0 [changePass],
# 1 [flash],
#
# 2 [throttle],
# 3 [wait],

def apply_defender_action(d, state):
    if d == 0:
        state["a_has_pay_pass"] = False
        state["a_has_web_pass"] = False
    elif d == 1:
        state["a_has_web_exploit"] = False
        state["a_has_pay_exploit"] = False
        state["a_has_pos_exploit"] = False
    elif d == 2:
        state["throttle"] = not state["throttle"]
    elif d == 3:
        pass


def get_defender_payoff(state):
    util = 0

    if state["a_has_pos_exploit"]:
        if state["throttle"]:
            util -= 5
        else:
            util -= 10

    if state["a_has_web_exploit"] or state["a_has_web_pass"]:
        if state["throttle"]:
            util -= 1
        else:
            util -= 2

    if state["a_has_pay_exploit"] or state["a_has_pay_pass"]:
        if state["throttle"]:
            util -= 3
        else:
            util -= 6

    if state["throttle"]:
        util -= 1

    return util


def get_attacker_payoff(state):
    sources = 0
    if state["a_has_web_exploit"] or state["a_has_web_pass"]:
        sources += 1
    if state["a_has_pay_exploit"] or state["a_has_pay_pass"]:
        sources += 1
    if state["a_has_pos_exploit"]:
        sources += 1

    if state["throttle"]:
        return sources
    else:
        return sources * 2


def get_fresh_state():
    state = {
        "a_has_pay_pass": False,
        "a_has_web_pass": False,

        "a_has_pay_exploit": False,
        "a_has_web_exploit": False,
        "a_has_pos_exploit": False,

        "throttle": False
    }

    return state


def get_attacker_vis_state_string(state):
    ans = ""+str(state["a_has_pay_pass"]) + str(state["a_has_web_pass"]) + str(state["a_has_pay_exploit"]) + str(state["a_has_web_exploit"]) + str(state["a_has_pos_exploit"])
    # print(ans)
    return ans


def get_payoff(d, a):

    p = 1

    defender_payoff = 0
    attacker_payoff = 0

    state = {
        "a_has_pay_pass": False,
        "a_has_web_pass": False,

        "a_has_pay_exploit": False,
        "a_has_web_exploit": False,
        "a_has_pos_exploit": False,

        "a_has_pay_logged": False,
        "a_has_web_logged": False,

        "a_has_web_disrupt": False,
        "a_has_pay_disrupt": False,
        "a_has_pos_disrupt": False,

        "a_exfiling": False,

        "camo": False,
        "throttle": False
    }

    timesteps = len(d)

    for t in range(timesteps):

        apply_attacker_action(a[t], state)
        apply_defender_action(d[t], state)

        p = p * (1-get_obs(a[t]))

        defender_payoff = defender_payoff + get_defender_payoff(state) * p
        attacker_payoff = attacker_payoff + get_attacker_payoff(state) * p

    return [defender_payoff, attacker_payoff]
