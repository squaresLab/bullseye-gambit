import gambit
import sim
from decimal import *
import parser


def change_base(x, b, digits=0):

    ans = []

    done = False

    while not done:
        remainder = x % b
        quotient = x / b
        ans.insert(0, remainder)
        x = quotient
        if x == 0:
            done = True

    padding = digits - len(ans)
    if padding > 0:
        for _ in range(padding):
            ans.insert(0, 0)

    return ans


def build_game():
    timesteps = 3
    num_defender_actions = 4
    num_attacker_actions = 5

    rows = num_defender_actions**timesteps
    cols = num_attacker_actions**timesteps

    g = gambit.Game.new_table([rows, cols])

    # set all of the payoffs
    for d in range(rows):
        for a in range(cols):
            payoff = sim.get_payoff(change_base(d, num_defender_actions, timesteps), change_base(a, num_attacker_actions, timesteps))
            g[d, a][0] = Decimal(payoff[0])
            g[d, a][1] = Decimal(payoff[1])

    return g


def check_type(val):
    if isinstance(val, gambit.lib.libgambit.Decimal) or isinstance(val, Decimal):
        return val
    else:
        return gambit.Decimal.from_float(val)


def build_game_tree_br(defender_ecj_string):
    defender_ecj_parsed = parser.list_obj_to_node(parser.parse(defender_ecj_string)[0])
    return build_game_tree(defender_ecj_parsed)


def build_game_tree(defender_ecj_obj=None):
    p = 1

    TIMESTEPS = 2

    num_defender_actions = 3
    num_attacker_actions = 5

    g = gambit.Game.new_tree()

    g.title = "bullseye"

    defender = g.players.add("defender")
    attacker = g.players.add("attacker")

    chance = g.players.chance
    chance.label = "nature"

    defender_memory = {}
    attacker_memory = {}

    def fill_defender_moves(node, stateprime, p, t, defender_payoff, attacker_payoff, def_hist, attacker_hist, forced_defender):

        if forced_defender is None:

            t += 1

            if def_hist in defender_memory:
                move = node.append_move(defender_memory[def_hist])
            else:
                move = node.append_move(defender, num_defender_actions)
                defender_memory[def_hist] = move

            attacknodes = node.children
            for j in range(len(attacknodes)):

                def_histp = def_hist + str(j)
                # print(def_histp)

                node = attacknodes[j]
                stateprime2 = stateprime.copy()
                sim.apply_defender_action(j, stateprime2)

                # defender_payoff = defender_payoff + sim.get_defender_payoff(stateprime2) * p

                attacker_inst_payoff = sim.get_attacker_payoff(stateprime2)

                attacker_payoff_prime = attacker_payoff + attacker_inst_payoff * p
                defender_payoff_prime = -1 * attacker_payoff_prime

                if t >= TIMESTEPS:
                    outcome = g.outcomes.add("oc")
                    outcome[0] = check_type(defender_payoff_prime)
                    outcome[1] = check_type(attacker_payoff_prime)
                    node.outcome = outcome
                    # print(stateprime2)
                    # print(attacker_inst_payoff)
                    # print (check_type(defender_payoff))
                    # print (check_type(attacker_payoff))
                else:
                    fill_attacker_moves(node, stateprime2, p, t, defender_payoff_prime, attacker_payoff_prime, def_histp, attacker_hist, forced_defender)
        else:
            # lock defender move to find best response

            if forced_defender.visisted:
                fill_defender_moves(node, stateprime, p, t, defender_payoff, attacker_payoff, def_hist,
                                    attacker_hist, forced_defender.parent)

            if forced_defender.data == "R":
                decision_prob = forced_defender.p
                defender_action_one = forced_defender.children[0]
                defender_action_two = forced_defender.children[1]
                forced_defender.visited = True

                move = node.append_move(chance, 2)

                action_one_node = node.children[0]
                action_one_node.prior_action.prob = decision_prob

                fill_defender_moves(action_one_node, stateprime, p, t, defender_payoff, attacker_payoff, def_hist,
                                    attacker_hist, defender_action_one)

                action_two_node = node.children[1]
                action_two_node.prior_action.prob = 1 - decision_prob

                fill_defender_moves(action_two_node, stateprime, p, t, defender_payoff, attacker_payoff, def_hist,
                                    attacker_hist, defender_action_two)

            elif forced_defender.data == ";":
                # this is sequence operator
                defender_action_one = forced_defender.children[0]
                defender_action_two = forced_defender.children[1]

                if not defender_action_one.visited:
                    fill_defender_moves(node, stateprime, p, t, defender_payoff, attacker_payoff, def_hist,
                                        attacker_hist, defender_action_one)
                elif not defender_action_two.visited:
                    fill_defender_moves(node, stateprime, p, t, defender_payoff, attacker_payoff, def_hist,
                                        attacker_hist, defender_action_two)
                else:
                    forced_defender.visited = True
                    fill_defender_moves(node, stateprime, p, t, defender_payoff, attacker_payoff, def_hist,
                                        attacker_hist, forced_defender.parent)
            else:
                # then this is a simple tactic
                t += 1

                defender_tactic = int(forced_defender.data)

                def_histp = def_hist + str(defender_tactic)

                stateprime2 = stateprime.copy()
                sim.apply_defender_action(defender_tactic, stateprime2)

                # defender_payoff = defender_payoff + sim.get_defender_payoff(stateprime2) * p

                attacker_inst_payoff = sim.get_attacker_payoff(stateprime2)

                attacker_payoff_prime = attacker_payoff + attacker_inst_payoff * p
                defender_payoff_prime = -1 * attacker_payoff_prime

                if t >= TIMESTEPS:
                    outcome = g.outcomes.add("oc")
                    outcome[0] = check_type(defender_payoff_prime)
                    outcome[1] = check_type(attacker_payoff_prime)
                    node.outcome = outcome
                    # print(stateprime2)
                    # print(attacker_inst_payoff)
                    # print (check_type(defender_payoff))
                    # print (check_type(attacker_payoff))
                else:
                    # backup in the tree since we just visited a leaf
                    parent = forced_defender.parent
                    forced_defender.visited = True
                    fill_attacker_moves(node, stateprime2, p, t, defender_payoff_prime, attacker_payoff_prime,
                                        def_histp, attacker_hist, parent)

    def fill_attacker_moves(node, state, p, t, defender_payoff, attacker_payoff, def_hist, attacker_hist, forced_defender):

        attacker_hist_prime_state = attacker_hist + sim.get_attacker_vis_state_string(state)

        if attacker_hist_prime_state in attacker_memory:
            move = node.append_move(attacker_memory[attacker_hist_prime_state])
        else:
            move = node.append_move(attacker, num_attacker_actions)
            attacker_memory[attacker_hist_prime_state] = move

        defnodes = node.children
        for i in range(len(defnodes)):
            node = defnodes[i]

            node.label = "attacker played " + str(i)

            stateprime = state.copy()
            sim.apply_attacker_action(i, stateprime)

            attacker_hist_prime = attacker_hist_prime_state + str(i)
            attacker_memory[attacker_hist_prime] = move

            # print(attacker_hist_prime)

            p_prime = p * (1 - sim.get_obs(i))

            fill_defender_moves(node, stateprime, p_prime, t, defender_payoff, attacker_payoff, def_hist, attacker_hist_prime, forced_defender)

    state = sim.get_fresh_state()

    timestep = 0

    node = g.root

    fill_attacker_moves(node, state, p, timestep, 0, 0, "", "", defender_ecj_obj)

    return g


if __name__ == '__main__':
    # g = build_game()
    # solver = gambit.nash.ExternalLCPSolver()
    # s = solver.solve(g)
    #
    # print s

    g = build_game_tree()
    solver = gambit.nash.ExternalLPSolver()
    s = solver.solve(g)

    print (s[0].payoff(g.players[0]))
    print (s[0].payoff(g.players[1]))

    print(s[0][g.players[0]])

    # print g.write()
    #
    # text_file = open("test2.efg", "w")
    # n = text_file.write(g.write())
    # text_file.close()
