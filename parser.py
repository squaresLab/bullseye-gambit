import json


class EcjNode:

    def __init__(self, string):
        self.data = string
        self.p = 1.0
        self.children = []
        self.visited = False
        self.parent = None


def list_obj_to_node(list_obj):

    if isinstance(list_obj, str):
        return EcjNode(list_obj)
    else:
        obj_type = list_obj[0]
        node = EcjNode(obj_type)

        if obj_type == 'R':
            # then we must randomize
            decision_prob = float(list_obj[1])
            defender_action_one = list_obj[2]
            defender_action_two = list_obj[3]

            node.p = decision_prob
            child1 = list_obj_to_node(defender_action_one)
            child1.parent = node
            child2 = list_obj_to_node(defender_action_two)
            child2.parent = node

            node.children.append(child1)
            node.children.append(child2)

        elif obj_type == ";":
            # this is sequence operator

            defender_action_one = list_obj[1]
            defender_action_two = list_obj[2]

            child1 = list_obj_to_node(defender_action_one)
            child1.parent = node
            child2 = list_obj_to_node(defender_action_two)
            child2.parent = node

            node.children.append(child1)
            node.children.append(child2)

        return node


def next_token_end(string, start):
    end_par = string.find(")", start)
    next_space = string.find(" ", start)

    if end_par == -1 and next_space == -1:
        return len(string)
    elif end_par == -1:
        return next_space
    elif next_space == -1:
        return end_par
    else:
        return min(next_space, end_par)


def translate(token):
    if token == "ChangePword":
        return "0"
    elif token == "FlashServers":
        return "1"
    elif token == "Throttle":
        return "2"
    elif token == "Wait":
        return "3"
    elif "ERC" in token:
        return token.split("|")[1]
    else:
        return token


def parse(string, start_index=0):

    if start_index == len(string):
        return

    first_char = string[start_index]

    if first_char == "(":
        parens = []
        end_index = start_index + 1

        while string[end_index] != ")":

            obj, end_index = parse(string, end_index)
            parens.append(obj)

        return parens, end_index + 1
    elif first_char == " ":
        return parse(string, start_index + 1)
    else:
        end = next_token_end(string, start_index)
        token = string[start_index:end]

        # print(token)
        return translate(token), end


def scenarioStringToList(scenario_string):
    ans = []

    string_arr = scenario_string.split(",")

    for s in string_arr:
        ans.append(float(s))

    return ans


if __name__ == '__main__':
    # print(parse("(; (b a) (c d))"))
    node = list_obj_to_node(parse("(R ERC[d4581030860394171213|0.0186435554|] (; FlashServers (R ERC[d4602435381355194647|0.4864864865|] ChangePword FlashServers)) (; Throttle (R ERC[d4602204756053502270|0.4736842105|] ChangePword FlashServers)))")[0])
    print(node)