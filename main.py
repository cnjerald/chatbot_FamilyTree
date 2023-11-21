from pyswip import Prolog, Functor, Variable

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

    def isGrandparent(grandparent,child):
        grandparents = set()

        siblings = findSiblings(child)
        test = list(prolog.query(f"grandparent(X,{child})"))

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

    ## Query Helpers
    def isSiblings(name1,name2):
        name1_siblings = list(prolog.query(f"siblings(X, {name1})."))
        name2_siblings = list(prolog.query(f"siblings(X, {name2})."))

        print(name1_siblings)
        print(name2_siblings)

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

    def isWoman(name):
        womanList = set()
        temp = list(prolog.query("woman(X)"))
        for t in temp:
            womanList.add(t['X'])

        if name in womanList:
            return True
        return False

    def isMan(name):
        manList = set()
        temp = list(prolog.query("man(X)"))
        for t in temp:
            manList.add(t['X'])

        if name in manList:
            return True
        return False


## Base Rules Do not delete
    prolog.asserta("sib(-,-)")
    prolog.asserta("parent(-,-)")
    prolog.asserta("woman(-)")
    prolog.asserta("man(-)")
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
    ## Register man ##
        prolog.asserta("man(man)")
    ## Register woman ##
        prolog.asserta("woman(woman)")
        
        
    Example I want to register a sister, where x is a sister of y
        prolog.asserta("sib(x,y)")
        prolog.asserta("woman(x)")
        
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
        user_input = input()
        user_input = user_input.lower()

        if user_input == "/exit":
            break

        ## This section is now for question prompts.
        if all(keyword in user_input for keyword in ["are","and","siblings?"]):
            temp = user_input.split(" ")
            if len(temp) == 5:
                if isSiblings(temp[1],temp[3]):
                    print("Yes!")
                else:
                    print("That's Impossible!")
            else:
                print("Im not sure... could you check your syntax?")

        elif all(keyword in user_input for keyword in ["is", "a sister of", "?"]):
            temp = user_input.split(" ")

            if len(temp) == 6:
                temp[5] = temp[5][:-1]
                temp[1]

                if isWoman(temp[1]):
                    if isSiblings(temp[1],temp[5]):
                        print("Yes!")
                    else:
                        print("That's Impossible!")
                else:
                    print("That's Impossible!")
            else:
                print("Im not sure... could you check your syntax?")

        elif all(keyword in user_input for keyword in ["is", "a brother of", "?"]):
            temp = user_input.split(" ")

            if len(temp) == 6:
                temp[5] = temp[5][:-1]
                temp[1]

                if isMan(temp[1]):
                    if isSiblings(temp[1],temp[5]):
                        print("Yes!")
                    else:
                        print("That's Impossible!")
                else:
                    print("That's Impossible!")
            else:
                print("Im not sure... could you check your syntax?")

        elif all(keyword in user_input for keyword in ["is", "the mother of", "?"]):
            temp = user_input.split(" ")

            if len(temp) == 6:
                temp[5] = temp[5][:-1]
                temp[1]

                if isWoman(temp[1]):
                    if isParent(temp[1],temp[5]):
                        print("Yes!")
                    else:
                        print("That's Impossible!")
                else:
                    print("That's Impossible!")
            else:
                print("Im not sure... could you check your syntax?")

        elif all(keyword in user_input for keyword in ["is", "the father of", "?"]):
            temp = user_input.split(" ")

            if len(temp) == 6:
                temp[5] = temp[5][:-1]
                temp[1]

                if isMan(temp[1]):
                    if isParent(temp[1],temp[5]):
                        print("Yes!")
                    else:
                        print("That's Impossible!")
                else:
                    print("That's Impossible!")
            else:
                print("Im not sure... could you check your syntax?")

        elif all(keyword in user_input for keyword in ["are", "and", "the parents of", "?"]):
            temp = user_input.split(" ")

            if len(temp) == 8:
                temp[7] = temp[7][:-1]
                if isParent(temp[1],temp[7]) and isParent(temp[3],temp[7]):
                    print("Yes!")
                else:
                    print("That's Impossible!")
            else:
                print("Im not sure... could you check your syntax?")

        elif all(keyword in user_input for keyword in ["is", "a grandmother of", "?"]):
            temp = user_input.split(" ")

            if len(temp) == 6:
                temp[5] = temp[5][:-1]
                temp[1]

                if isWoman(temp[1]):
                    if isGrandparent(temp[1],temp[5]):
                        print("Yes!")
                    else:
                        print("That's Impossible!")
                else:
                    print("That's Impossible!")
            else:
                print("Im not sure... could you check your syntax?")

        elif all(keyword in user_input for keyword in ["is", "a grandfather of", "?"]):
            temp = user_input.split(" ")

            if len(temp) == 6:
                temp[5] = temp[5][:-1]
                temp[1]

                if isMan(temp[1]):
                    if isGrandparent(temp[1],temp[5]):
                        print("Yes!")
                    else:
                        print("That's Impossible!")
                else:
                    print("That's Impossible!")
            else:
                print("Im not sure... could you check your syntax?")

        elif all(keyword in user_input for keyword in ["is", "a child of", "?"]):
            temp = user_input.split(" ")

            if len(temp) == 6:
                temp[5] = temp[5][:-1]
                temp[1]

                if isParent(temp[5],temp[1]):
                    print("Yes!")
                else:
                    print("That's Impossible!")

            else:
                print("Im not sure... could you check your syntax?")

        elif all(keyword in user_input for keyword in ["is", "a daughter of", "?"]):
            temp = user_input.split(" ")

            if len(temp) == 6:
                temp[5] = temp[5][:-1]
                if isWoman(temp[1]):
                    if isParent(temp[5],temp[1]):
                        print("Yes!")
                    else:
                        print("That's Impossible!")
                else:
                    print("That's Impossible!")
            else:
                print("Im not sure... could you check your syntax?")

        elif all(keyword in user_input for keyword in ["is", "a son of", "?"]):
            temp = user_input.split(" ")

            if len(temp) == 6:
                temp[5] = temp[5][:-1]
                if isMan(temp[1]):
                    if isParent(temp[5],temp[1]):
                        print("Yes!")
                    else:
                        print("That's Impossible!")
                else:
                    print("That's Impossible!")
            else:
                print("Im not sure... could you check your syntax?")

        elif all(keyword in user_input for keyword in ["is", "an uncle of", "?"]):
            temp = user_input.split(" ")

            if len(temp) == 6:
                temp[5] = temp[5][:-1]
                if isMan(temp[1]):
                    if isPibling(temp[1],temp[5]):
                        print("Yes!")
                    else:
                        print("That's Impossible!")
                else:
                    print("That's Impossible!")
            else:
                print("Im not sure... could you check your syntax?")

        elif all(keyword in user_input for keyword in ["is", "an aunt of", "?"]):
            temp = user_input.split(" ")

            if len(temp) == 6:
                temp[5] = temp[5][:-1]
                if isWoman(temp[1]):
                    if isPibling(temp[1],temp[5]):
                        print("Yes!")
                    else:
                        print("That's Impossible!")
                else:
                    print("That's Impossible!")
            else:
                print("Im not sure... could you check your syntax?")




        ## This section is for Statement Prompts
        elif all(keyword in user_input for keyword in ["and", "are siblings"]):
            temp = user_input.split(" ")

            if len(temp) == 5:
                prolog.asserta(f"sib({temp[0]}, {temp[2]})")
                print("OK! I learned something")
            else:
                print("Im not sure... could you check your syntax?")

        elif all(keyword in user_input for keyword in ["is a sister of"]):
            temp = user_input.split(" ")
            if len(temp) == 6:
                prolog.asserta(f"sib({temp[0]}, {temp[5]})")
                prolog.asserta(f"woman({temp[0]})")
                print("OK! I learned something")
            else:
                print("Im not sure... could you check your syntax?")

        elif all(keyword in user_input for keyword in ["is the mother of"]):
            temp = user_input.split(" ")
            if len(temp) == 6:
                prolog.assertz(f"parent({temp[0]}, {temp[5]})")
                prolog.assertz(f"woman({temp[0]})")
                print("OK! I learned something")
            else:
                print("Im not sure... could you check your syntax?")
        elif all(keyword in user_input for keyword in ["is a grandmother of"]):
            temp = user_input.split(" ")
            if len(temp) == 6:
                prolog.assertz(f"grandparent({temp[0]}, {temp[5]})")
                prolog.assertz(f"woman({temp[0]})")
                print("OK! I learned something")
            else:
                print("Im not sure... could you check your syntax?")
        elif all(keyword in user_input for keyword in ["is a child of"]):
            temp = user_input.split(" ")
            if len(temp) == 6:
                prolog.assertz(f"parent({temp[5]}, {temp[0]})")
                prolog.assertz(f"woman({temp[0]})")
                print("OK! I learned something")
            else:
                print("Im not sure... could you check your syntax?")
        elif all(keyword in user_input for keyword in ["is a daughter of"]):
            temp = user_input.split(" ")
            if len(temp) == 6:
                prolog.assertz(f"parent({temp[5]}, {temp[0]})")
                prolog.assertz(f"woman({temp[5]})")
                print("OK! I learned something")
            else:
                print("Im not sure... could you check your syntax?")
        elif all(keyword in user_input for keyword in ["is an uncle of"]):
            temp = user_input.split(" ")
            if len(temp) == 6:
                prolog.assertz(f"pibling({temp[0]}, {temp[5]})")
                prolog.assertz(f"man({temp[0]})")
                print("OK! I learned something")
            else:
                print("Im not sure... could you check your syntax?")
        elif all(keyword in user_input for keyword in ["is a brother of"]):
            temp = user_input.split(" ")
            if len(temp) == 6:
                prolog.assertz(f"sib({temp[0]}, {temp[5]})")
                prolog.assertz(f"man({temp[0]})")
                print("OK! I learned something")
            else:
                print("Im not sure... could you check your syntax?")
        elif all(keyword in user_input for keyword in ["is the father of"]):
            temp = user_input.split(" ")
            prolog.assertz(f"parent({temp[0]}, {temp[5]})")
            prolog.assertz(f"man({temp[0]})")
            print("OK! I learned something")
        elif all(keyword in user_input for keyword in ["and","are the parents of"]):
            temp = user_input.split(" ")
            if len(temp) == 8:
                prolog.assertz(f"parent({temp[0]}, {temp[7]})")
                prolog.assertz(f"parent({temp[2]}, {temp[7]})")
                print("OK! I learned something")
            else:
                print("Im not sure... could you check your syntax?")
        elif all(keyword in user_input for keyword in ["is a grandfather of"]):
            temp = user_input.split(" ")
            if len(temp) == 6:
                prolog.assertz(f"grandparent({temp[0]}, {temp[5]})")
                prolog.assertz(f"man({temp[0]})")
                print("OK! I learned something")
            else:
                print("Im not sure... could you check your syntax?")
        elif all(keyword in user_input for keyword in ["and","are children of"]):
            print("This is currently broken :I")
        elif all(keyword in user_input for keyword in ["is a son of"]):
            temp = user_input.split(" ")
            if len(temp) == 6:
                prolog.assertz(f"parent({temp[5]}, {temp[0]})")
                prolog.assertz(f"man({temp[0]})")
                print("OK! I learned something")
            else:
                print("Im not sure... could you check your syntax?")
        elif all(keyword in user_input for keyword in ["is an aunt of"]):
            temp = user_input.split(" ")
            if len(temp) == 6:
                prolog.assertz(f"pibling({temp[0]}, {temp[5]})")
                prolog.assertz(f"woman({temp[0]})")
                print("OK! I learned something")
            else:
                print("Im not sure... could you check your syntax?")

        ## This section is for help.
        elif user_input == "/help":
            print("/exit to exit the program")


if __name__ == '__main__':
    main()
    print("Exit Success.")
