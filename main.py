from pyswip import Prolog


## pyswip version to use: pip install git+https://github.com/yuce/pyswip@master#egg=pyswip
class FlagException(Exception):
    pass


def main():
    prolog = Prolog()

    ## DFS Functions
    def dfs_siblings(node, target, visited):
        visited.add(node)
        if node == target:
            return True

        query_result = list(prolog.query(f"siblings({node}, X)"))
        for res in query_result:
            sibling = res['X']
            if sibling not in visited and dfs_siblings(sibling, target, visited):
                return True
        return False

    def isParent(parent, child, visited=None) -> bool:
        if visited is None:
            visited = set()

        query_result = list(prolog.query(f"parent(X, {child})"))

        # Check if the parent is directly a parent of the child
        flag = False

        for res in query_result:
            parent_result = res['X']
            if parent_result == parent:
                flag = True
                break
        if flag:
            return flag
        else:
            visited.add(child)  # Mark the current child as visited
            # If not, check if there are any siblings and recursively check their parents
            siblings = findSiblings(child)
            for sibling in siblings:
                if sibling not in visited and isParent(parent, sibling, visited):
                    return True
        return False

    def findSiblings(child):
        visited = set()
        siblings = []

        def dfs(current_child):
            nonlocal visited, siblings
            visited.add(current_child)
            query_result = list(prolog.query(f"siblings(X, {current_child})"))

            for res in query_result:
                sibling = res['X']
                if sibling not in visited:
                    siblings.append(sibling)
                    dfs(sibling)

        dfs(child)  # Start DFS with the given child and no parent
        return siblings

    def findParent(child):
        parents = set()
        siblings = findSiblings(child)
        visited_siblings = set()

        current = list(prolog.query(f"parent(X,{child})"))

        for c in current:
            parent = c['X']
            if parent not in parents:
                parents.add(parent)

        def dfs(current_child):
            nonlocal parents
            visited_siblings.add(current_child)
            query_result = list(prolog.query(f"parent(X, {current_child})"))

            for res in query_result:
                parent = res['X']
                if parent not in parents:
                    parents.add(parent)
                if current_child not in visited_siblings:
                    dfs(current_child)

        for s in siblings:
            dfs(s)  # Start DFS with the given child and no parent
        return parents
    
    def findParentSiblings(parent):
        parent_siblings = set(findSiblings(parent))
        parent_siblings.add(parent)
        return parent_siblings

    def isPibling(pibling, child):
        piblings = set()
        parents = findParent(child)
        visited_parents = set(parents)

        temp = list(prolog.query(f"pibling(X,{child})"))

        for t in temp:
            piblings.add(t['X'])

        siblings = findSiblings(child)
        for s in siblings:
            temp = list(prolog.query(f"pibling(X,{s})"))
            for t in temp:
                piblings.add(t['X'])

        for parent in parents:
            parent_siblings = findSiblings(parent)
            piblings.update(parent_siblings)

        return pibling in piblings and pibling not in visited_parents

    def isGrandparent(grandparent, child):
        grandparents = set()

        siblings = findSiblings(child)
        test = list(prolog.query(f"grandparent(X,{child})"))

        piblings = set()

        temp = list(prolog.query(f"pibling(X,{child})"))
        for t in temp:
            piblings.add(t['X'])

        for s in siblings:
            temp = list(prolog.query(f"pibling(X,{s})"))
            for t in temp:
                piblings.add(t['X'])

        for p in piblings:
            temp = findParent(p)
            for t in temp:
                grandparents.add(t)

        for t in test:
            grandparents.add(t['X'])

        for s in siblings:
            temp = list(prolog.query(f"grandparent(X,{s})"))
            for t in temp:
                grandparents.add(t['X'])

        parents = findParent(child)
        for p in parents:
            test = findParent(p)
            for t in test:
                grandparents.add(t)

        if grandparent in grandparents:
            return True
        else:
            return False

    def findChildren(parent):

        children = set()

        temp = list(prolog.query(f"parent({parent},X)"))

        for t in temp:
            children.add(t['X'])
            temp2 = findSiblings(t['X'])

            for t2 in temp2:
                children.add(t2)

        return children

    ## Query Helpers
    def isSiblings(name1, name2):
        name1_siblings = list(prolog.query(f"siblings(X, {name1})."))
        name2_siblings = list(prolog.query(f"siblings(X, {name2})."))

        for n1 in name1_siblings:
            for n2 in name2_siblings:
                visited = set()
                if dfs_siblings(n1['X'], n2['X'], visited):
                    return True
            else:
                continue
            break
        else:
            return False

    def isCousin(name1, name2):

        parents1 = findParent(name1)
        parents2 = findParent(name2)

        if len(parents1) != 0 and len(parents2) != 0:
            for parent1 in parents1:
                for parent2 in parents2:
                    if isSiblings(parent1, parent2):
                        return True

        return False

    def isFemale(name):
        femaleList = set()
        temp = list(prolog.query("female(X)"))
        for t in temp:
            femaleList.add(t['X'])

        if name in femaleList:
            return True
        return False

    def isMale(name):
        maleList = set()
        temp = list(prolog.query("male(X)"))
        for t in temp:
            maleList.add(t['X'])

        if name in maleList:
            return True
        return False

    def isRelative(name1, name2): 
        if isSiblings(name1, name2):
            return True
        if isParent(name1, name2) or isParent(name2, name1):
            return True
        if isGrandparent(name1, name2) or isGrandparent(name2, name1):
            return True
        if isPibling(name1, name2) or isPibling(name2, name1):
            return True     
        if isCousin(name1, name2):
            return True   
        return False
        
    def hasRelationship(name1, name2):
        if isParent(name1, name2):
            return True
        elif isParent(name2, name1):
            return True
        elif isPibling(name1, name2):
            return True
        elif isPibling(name2, name1):
            return True
        elif isGrandparent(name1, name2):
            return True
        elif isGrandparent(name2, name1):
            return True
        elif isSiblings(name1, name2):
            return True
        elif isPartners(name1, name2):
            return True
        elif isPartners(name2, name1):
            return True
        else:
            return False

    def countParents(name):
        parents = set()
        temp = findParent(name)
        for t in temp:
            parents.add(t)
        return len(parents)

    def countMother(name):
        mother = set()
        temp = findParent(name)
        for t in temp:
            if isFemale(t):
                mother.add(t)
        return len(mother)

    def countFather(name):
        father = set()
        temp = findParent(name)
        for t in temp:
            if isMale(t):
                father.add(t)
        return len(father)

    def findPartner(name):
        parents = set()
        children = findChildren(name)
        parents.add(name)
        for c in children:
            temp = findParent(c)
            for t in temp:
                parents.add(t)
        return parents

    def findPartnerOnly(name):
        parents = set()
        children = findChildren(name)
        for c in children:
            temp = findParent(c)
            for t in temp:
                parents.add(t)
        return parents

    def isPartners(x, y):
        temp = findPartner(y)
        temp2 = findPartner(x)
        if x in temp or y in temp2:
            return True
        else:
            return False

    ## Base Rules Do not delete
    prolog.asserta("sib(-,-)")
    prolog.asserta("parent(-,-)")
    prolog.asserta("female(-)")
    prolog.asserta("male(-)")
    prolog.asserta("pibling(-,-)")
    prolog.assertz("siblings(X, Y) :- parent(Z, X), parent(Z, Y)")
    prolog.assertz("siblings(X,Y) :- sib(X,Y); sib(Y,X)")
    prolog.assertz("pibling(X,Y) :- parent(Z,Y), siblings(Z,X)")
    prolog.assertz("grandparent(X,Y) :- parent(Z,Y), parent(X,Z)")

    '''
    How to implement. 
    ## Register siblings ##
        prolog.asserta("sib(sibling,anothersibling)")
    ## Register parents ##
        prolog.asserta("parent(parent,child)")
    ## Register pibling ##
        prolog.asserta("pibling(pibling,child)")
    ## Register Grandparent ##
        prolog.asserta("grandparent(grandparent,child)")
    ## Register male ##
        prolog.asserta("male(male)")
    ## Register female ##
        prolog.asserta("female(female)")


    Example I want to register a sister, where x is a sister of y
        prolog.asserta("sib(x,y)")
        prolog.asserta("female(x)")

    Note: Do not Capitalize non-rule based assertions
    Example
        DO NOT prolog.asserta("sib(X,y)") <- This will make everyone the sibling of y


    How to use helper functions.
        1. I want to know if X any Y are siblings

        print(isSiblings("namehere","nameanother"))

        2. I want to get the siblings of X.

        print(findSiblings("namehere"))

    '''

    print("Hello! Type anything! /help for more info")

    while True:
        user_input = input("> ")
        user_input = user_input.lower()

        if user_input == "/exit":
            break

        ## This section is for statement prompts.
        temp = user_input.split(" ")
        if temp[-1].endswith('.'):
            temp[-1] = temp[-1][:-1]
            if len(temp) == 6:
                if temp[0] == temp[5]:
                    print("That's impossible!")
                elif all(keyword in user_input for keyword in ["is a brother of"]):

                    parents_temp_0 = findParent(temp[0])
                    parents_temp_2 = findParent(temp[2])
                    flag = False
                    for parent_temp_0 in parents_temp_0:
                        for parent_temp_2 in parents_temp_2:
                            if parent_temp_0 not in parents_temp_2 or parent_temp_2 not in parents_temp_0:
                                flag = True

                    if isFemale(temp[0]) or (hasRelationship(temp[0], temp[5]) and not isSiblings(temp[0], temp[5])):
                        print("That's impossible!")
                    elif flag and ((countFather(temp[0]) + countFather(temp[2]) > 1) or (
                            countMother(temp[0]) + countMother(temp[2]) > 1) or (
                                           countParents(temp[0]) + countParents(temp[2]) > 2)):
                        print("That's impossible!")
                    else:
                        prolog.assertz(f"male({temp[0]})")
                        prolog.assertz(f"sib({temp[0]}, {temp[5]})")
                        print("OK! I learned something.")

                elif all(keyword in user_input for keyword in ["is a sister of"]):
                    parents_temp_0 = findParent(temp[0])
                    parents_temp_2 = findParent(temp[2])
                    flag = False
                    for parent_temp_0 in parents_temp_0:
                        for parent_temp_2 in parents_temp_2:
                            if parent_temp_0 not in parents_temp_2 or parent_temp_2 not in parents_temp_0:
                                flag = True

                    if isMale(temp[0]) or (hasRelationship(temp[0], temp[5]) and not isSiblings(temp[0], temp[5])) or (
                            countFather(temp[0]) + countFather(temp[2]) > 1) or (
                            countMother(temp[0]) + countMother(temp[2]) > 1) or (
                            countParents(temp[0]) + countParents(temp[2]) > 2):
                        print("That's impossible!")
                    elif flag and ((countFather(temp[0]) + countFather(temp[2]) > 1) or (
                            countMother(temp[0]) + countMother(temp[2]) > 1) or (
                                           countParents(temp[0]) + countParents(temp[2]) > 2)):
                        print("That's impossible!")
                    else:
                        prolog.asserta(f"female({temp[0]})")
                        prolog.asserta(f"sib({temp[0]}, {temp[5]})")
                        print("OK! I learned something.")

                elif all(keyword in user_input for keyword in ["is the father of"]):
                    parents = findParent(temp[5])
                    father = ""
                    for p in parents:
                        if isMale(p):
                            father = p

                    if isFemale(temp[0]) or (hasRelationship(temp[0], temp[5]) and not isParent(temp[0], temp[5])) or (father != "" and father != temp[0]) or (countParents(temp[5]) == 2 and not isParent(temp[0], temp[5])):
                        print("That's impossible!")
                    else:
                        prolog.assertz(f"male({temp[0]})")
                        prolog.assertz(f"parent({temp[0]}, {temp[5]})")
                        print("OK! I learned something.")

                elif all(keyword in user_input for keyword in ["is the mother of"]):
                    parents = findParent(temp[5])
                    mother = ""
                    for p in parents:
                        if isFemale(p):
                            mother = p
                    if isMale(temp[0]) or (hasRelationship(temp[0], temp[5]) and not isParent(temp[0], temp[5])) or (mother != "" and mother != temp[0]) or (countParents(temp[5]) == 2 and not isParent(temp[0], temp[5])):
                        print("That's impossible!")
                    else:
                        prolog.assertz(f"female({temp[0]})")
                        prolog.assertz(f"parent({temp[0]}, {temp[5]})")
                        print("OK! I learned something.")

                elif all(keyword in user_input for keyword in ["is a grandmother of"]):
                    if isMale(temp[0]) or (hasRelationship(temp[0], temp[5]) and not isGrandparent(temp[0], temp[5])):
                        print("That's impossible!")
                    else:
                        prolog.assertz(f"female({temp[0]})")
                        prolog.assertz(f"grandparent({temp[0]}, {temp[5]})")
                        print("OK! I learned something.")

                elif all(keyword in user_input for keyword in ["is a grandfather of"]):
                    if isFemale(temp[0]) or (hasRelationship(temp[0], temp[5]) and not isGrandparent(temp[0], temp[5])):
                        print("That's impossible!")
                    else:
                        prolog.assertz(f"male({temp[0]})")
                        prolog.assertz(f"grandparent({temp[0]}, {temp[5]})")
                        print("OK! I learned something.")

                elif all(keyword in user_input for keyword in ["is a child of"]):
                    partners = findPartnerOnly(temp[5])
                    curr_child_parents = findParent(temp[0])

                    flag = False
                    if (len(curr_child_parents) != len(partners) and (len(partners) != 0 and len(curr_child_parents)!=0)):
                        flag = True
                    else:
                        if partners != curr_child_parents and (len(partners)!=0 and len(curr_child_parents) !=0):
                            flag = True

                    if hasRelationship(temp[0], temp[5]) and not isParent(temp[5], temp[0]) or countParents(
                            temp[0]) == 2 or (isFemale(temp[5]) and (countMother(temp[0]) > 0)) or (
                            isMale(temp[5]) and countFather(temp[0]) > 0):
                        print("That's impossible!")
                    elif flag:
                        print("That's impossible!")
                    else:
                        prolog.assertz(f"parent({temp[5]}, {temp[0]})")
                        print("OK! I learned something.")

                elif all(keyword in user_input for keyword in ["is a daughter of"]):

                    partners = findPartnerOnly(temp[5])
                    curr_child_parents = findParent(temp[0])

                    flag = False
                    if (len(curr_child_parents) != len(partners) and (len(partners) != 0 and len(curr_child_parents)!=0)):
                        flag = True
                    else:
                        if partners != curr_child_parents and (len(partners)!=0 and len(curr_child_parents) !=0):
                            flag = True

                    if isMale(temp[0]) or (
                            hasRelationship(temp[0], temp[5]) and not isParent(temp[5], temp[0])) or countParents(
                            temp[0]) == 2 or (isFemale(temp[5]) and (countMother(temp[0]) > 0)) or (
                            isMale(temp[5]) and countFather(temp[0]) > 0):
                        print("That's impossible!")
                    elif flag:
                        print("That's impossible!")
                    else:
                        prolog.assertz(f"female({temp[0]})")
                        prolog.assertz(f"parent({temp[5]}, {temp[0]})")
                        print("OK! I learned something.")

                elif all(keyword in user_input for keyword in ["is a son of"]):
                    partners = findPartnerOnly(temp[5])
                    curr_child_parents = findParent(temp[0])


                    flag = False
                    if (len(curr_child_parents) != len(partners) and (len(partners) != 0 and len(curr_child_parents)!=0)):
                        flag = True
                    else:
                        if partners != curr_child_parents and (len(partners)!=0 and len(curr_child_parents) !=0):
                            flag = True

                    if isFemale(temp[0]) or (
                            hasRelationship(temp[0], temp[5]) and not isParent(temp[5], temp[0])) or countParents(
                            temp[0]) == 2 or (isFemale(temp[5]) and (countMother(temp[0]) > 0)) or (
                            isMale(temp[5]) and countFather(temp[0]) > 0):
                        print("That's impossible!")
                    elif flag:
                        print("That's impossible!")
                    else:
                        prolog.assertz(f"male({temp[0]})")
                        prolog.assertz(f"parent({temp[5]}, {temp[0]})")
                        print("OK! I learned something.")

                elif all(keyword in user_input for keyword in ["is an uncle of"]):
                    if isFemale(temp[0]) or (hasRelationship(temp[0], temp[5]) and not isPibling(temp[0], temp[5])):
                        print("That's impossible!")
                    else:
                        prolog.assertz(f"male({temp[0]})")
                        prolog.assertz(f"pibling({temp[0]}, {temp[5]})")
                        print("OK! I learned something.")

                elif all(keyword in user_input for keyword in ["is an aunt of"]):
                    if isMale(temp[0]) or (hasRelationship(temp[0], temp[5]) and not isPibling(temp[0], temp[5])):
                        print("That's impossible!")
                    else:
                        prolog.assertz(f"female({temp[0]})")
                        prolog.assertz(f"pibling({temp[0]}, {temp[5]})")
                        print("OK! I learned something.")

                else:
                    print("Invalid prompt!")

            elif all(keyword in user_input for keyword in ["and", "are siblings"]) and len(temp) == 5:
                parents_temp_0 = findParent(temp[0])
                parents_temp_2 = findParent(temp[2])
                flag = False

                try:
                    for parent_temp_0 in parents_temp_0:
                        for parent_temp_2 in parents_temp_2:
                            if parent_temp_0 not in parents_temp_2 or parent_temp_2 not in parents_temp_0:
                                flag = True
                                raise FlagException  # Raise the custom exception to exit both loops
                except FlagException:
                    pass  # Continue with the rest of your code after the loops

                if hasRelationship(temp[0], temp[2]) and not isSiblings(temp[0], temp[2]) or temp[0] == temp[2]:
                    print("That's impossible!")
                elif flag and ((countFather(temp[0]) + countFather(temp[2]) > 1) or (
                        countMother(temp[0]) + countMother(temp[2]) > 1) or (
                                       countParents(temp[0]) + countParents(temp[2]) > 2)):
                    print("That's impossible!")
                else:
                    prolog.asserta(f"sib({temp[0]}, {temp[2]})")
                    print("OK! I learned something.")

            elif all(keyword in user_input for keyword in ["and", "are the parents of"]) and len(temp) == 8:
                if temp[0] == temp[2] or temp[0] == temp[7] or temp[2] == temp[7]:
                    print("That's impossible!")
                else:
                    parents_temp_7 = findParent(temp[7])
                    checker = 0
                    if len(parents_temp_7) != 0:
                        for parent in parents_temp_7:
                            if parent == temp[0] or parent == temp[2]:
                                checker += 1
                    if checker < len(parents_temp_7) or (hasRelationship(temp[0], temp[2]) and not isPartners(temp[0], temp[2])) or (hasRelationship(temp[0], temp[7]) and not isParent(temp[0], temp[7])) or (hasRelationship(temp[2], temp[7]) and not isParent(temp[2], temp[7])):
                        print("That's impossible!")
                    else:
                        prolog.assertz(f"parent({temp[0]}, {temp[7]})")
                        prolog.assertz(f"parent({temp[2]}, {temp[7]})")
                        print("OK! I learned something.")

            elif all(keyword in user_input for keyword in ["and", "are children of"]) and len(temp) >= 7:
                parent = temp[-1]
                if len(temp) > 7:
                    before_comma = [word.strip() for word in user_input.split(',')[:-1]]
                    after_and = user_input.split('and')[1].split(',')[0].split()[0].strip()
                    children_list = before_comma + [after_and]
                else:
                    children_list = [temp[0], temp[2]]

                valid = True 
                for child in children_list:
                    if child == temp[-1] or (hasRelationship(child, temp[-1]) and not isParent(temp[-1], child)):
                        valid = False
                    else:
                        parents_temp = findParent(child)
                        if len(parents_temp) == 2:
                            checker = 0
                            for p in parents_temp:
                                if p == temp[-1]:
                                    checker = 1
                            if checker == 0:
                                valid = False
                                break
                        elif len(parents_temp) == 1:
                            for p in parents_temp:
                                if p != temp[-1]:
                                    if len(findPartnerOnly(temp[-1])) > 0:
                                        valid = False
                            if not valid:
                                break


                if len(children_list) != len(set(children_list)) or not valid:
                    print("That's impossible!")
                else:
                    for child in children_list:
                        prolog.assertz(f"parent('{parent}', '{child}')")
                    print("OK! I learned something.")

            else:
                print("Invalid prompt! Check Syntax")

        ## This section is now for question prompts.
        elif temp[-1].endswith('?'):
            temp[-1] = temp[-1][:-1]
            if len(temp) == 6:
                if all(keyword in user_input for keyword in ["is", "a sister of"]):
                    if isFemale(temp[1]) and isSiblings(temp[1], temp[5]):
                        print("Yes!")
                    else:
                        print("No!")

                elif all(keyword in user_input for keyword in ["is", "a brother of"]):
                    if isMale(temp[1]) and isSiblings(temp[1], temp[5]):
                        print("Yes!")
                    else:
                        print("No!")

                elif all(keyword in user_input for keyword in ["is", "a grandmother of"]):
                    if isFemale(temp[1]) and isGrandparent(temp[1], temp[5]):
                        print("Yes!")
                    else:
                        print("No!")

                elif all(keyword in user_input for keyword in ["is", "a grandfather of"]):
                    if isMale(temp[1]) and isGrandparent(temp[1], temp[5]):
                        print("Yes!")
                    else:
                        print("No!")

                elif all(keyword in user_input for keyword in ["is", "a daughter of"]):
                    if isFemale(temp[1]) and isParent(temp[5], temp[1]):
                        print("Yes!")
                    else:
                        print("No!")

                elif all(keyword in user_input for keyword in ["is", "a son of"]):
                    if isMale(temp[1]) and isParent(temp[5], temp[1]):
                        print("Yes!")
                    else:
                        print("No!")

                elif all(keyword in user_input for keyword in ["is", "a child of"]):
                    if isParent(temp[5], temp[1]):
                        print("Yes!")
                    else:
                        print("No!")

                elif all(keyword in user_input for keyword in ["is", "an aunt of"]):
                    if isFemale(temp[1]) and isPibling(temp[1], temp[5]):
                        print("Yes!")
                    else:
                        print("No!")

                elif all(keyword in user_input for keyword in ["is", "an uncle of"]):
                    if isMale(temp[1]) and isPibling(temp[1], temp[5]):
                        print("Yes!")
                    else:
                        print("No!")

                elif "is" in user_input and "the mother of" in user_input and "who" not in user_input:
                    if isFemale(temp[1]) and isParent(temp[1], temp[5]):
                        print("Yes!")
                    else:
                        print("No!")

                elif "is" in user_input and "the father of" in user_input and "who" not in user_input:
                    if isMale(temp[1]) and isParent(temp[1], temp[5]):
                        print("Yes!")
                    else:
                        print("No!")

                elif all(keyword in user_input for keyword in ["who are the siblings of"]):
                    siblings = (findSiblings(temp[5]))
                    if len(siblings) == 0:
                        print(f"{temp[5]} has no siblings.")
                    else:
                        print(f"The sibling/s of {temp[5]} is/are ", end='')
                        if siblings:
                            print(', '.join(siblings), end='')
                        print()

                elif all(keyword in user_input for keyword in ["who are the sisters of"]):
                    siblings = (findSiblings(temp[5]))
                    sisters = set()

                    for s in siblings:
                        if isFemale(s):
                            sisters.add(s)
                    if len(sisters) == 0:
                        print(f"{temp[5]} has no sisters.")
                    else:
                        print(f"The sister/s of {temp[5]} is/are ", end='')
                        if sisters:
                            print(', '.join(sisters), end='')
                        print()

                elif all(keyword in user_input for keyword in ["who are the brothers of"]):
                    siblings = (findSiblings(temp[5]))
                    brothers = set()

                    for s in siblings:
                        if isMale(s):
                            brothers.add(s)
                    if len(brothers) == 0:
                        print(f"{temp[5]} has no brothers.")
                    else:
                        print(f"The brother/s of {temp[5]} is/are ", end='')
                        if brothers:
                            print(', '.join(brothers), end='')
                        print()

                elif all(keyword in user_input for keyword in ["who is the mother of"]):
                    parents = (findParent(temp[5]))
                    mother = ""
                    for p in parents:
                        if isFemale(p):
                            mother = p

                    if mother == "":
                        print(f"{temp[5]} has no mother.")
                    else:
                        print(f"The mother of {temp[5]} is {mother}.")

                elif all(keyword in user_input for keyword in ["who is the father of"]):
                    parents = (findParent(temp[5]))
                    father = ""
                    for p in parents:
                        if isMale(p):
                            father = p

                    if father == "":
                        print(f"{temp[5]} has no father.")
                    else:
                        print(f"The father of {temp[5]} is {father}.")

                elif all(keyword in user_input for keyword in ["who are the parents of"]):
                    parents = (findParent(temp[5]))
                    if len(parents) == 0:
                        print(f"{temp[5]} has no parents.")
                    else:
                        print(f"The parent/s of {temp[5]} is/are ", end='')
                        if parents:
                            print(', '.join(parents), end='')
                        print()

                elif all(keyword in user_input for keyword in ["who are the daughters of"]):
                    children = findChildren(temp[5])
                    daughters = list()
                    for c in children:
                        if isFemale(c):
                            daughters.append(c)

                    if len(daughters) == 0:
                        print(f"{temp[5]} has no daughters.")
                    else:
                        print(f"The daughter/s of {temp[5]} is/are ", end='')
                        if daughters:
                            print(', '.join(daughters), end='')
                        print()

                elif all(keyword in user_input for keyword in ["who are the sons of"]):
                    children = findChildren(temp[5])
                    sons = list()
                    for c in children:
                        if isMale(c):
                            sons.append(c)

                    if len(sons) == 0:
                        print(f"{temp[5]} has no sons.")
                    else:
                        print(f"The son/s of {temp[5]} is/are ", end='')
                        if sons:
                            print(', '.join(sons), end='')
                        print()

                elif all(keyword in user_input for keyword in ["who are the children of"]):
                    children = findChildren(temp[5])

                    if len(children) == 0:
                        print(f"{temp[5]} has no children.")
                    else:
                        print(f"The child/ren of {temp[5]} is/are ", end='')
                        if children:
                            print(', '.join(children), end='')
                        print()

            elif len(temp) == 5:
                if all(keyword in user_input for keyword in ["are", "and", "siblings"]):
                    if isSiblings(temp[1], temp[3]):
                        print("Yes!")
                    else:
                        print("No!")

                elif all(keyword in user_input for keyword in ["are", "and", "relatives"]):
                    #######################################################################
                    if isRelative(temp[1], temp[3]):
                        print("Yes!")
                    else:
                        print("No!")
                    #######################################################################

            elif len(temp) == 8:
                if all(keyword in user_input for keyword in ["are", "and", "the parents of"]):
                    if isParent(temp[1], temp[7]) and isParent(temp[3], temp[7]):
                        print("Yes!")
                    else:
                        print("No!")

                elif all(keyword in user_input for keyword in ["are", "and", "children of"]):
                    temp_parent = temp[-1]
                    children = [temp[1][:-1], temp[2][:-1], temp[4]]

                    flag = True
                    for c in children:
                        if not isParent(temp_parent, c):
                            flag = False
                            break
                    if flag:
                        print(f"They are the children of {temp_parent}.")
                    else:
                        print(f"They are not the children of {temp_parent}.")

            else:
                print("Invalid prompt!")

        ## This section is for help.
        elif user_input == "/help":
            print("/exit to exit the program")

        else:
            print("Invalid prompt!")


if __name__ == '__main__':
    main()
