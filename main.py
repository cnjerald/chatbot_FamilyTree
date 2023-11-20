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
        visited = set()
        parents = set()
        siblings = findSiblings(child)
        visited_siblings = set()

        def dfs(current_child):
            nonlocal visited, parents
            visited_siblings.add(current_child)
            query_result = list(prolog.query(f"parent(X, {current_child})"))

            for res in query_result:
                parent = res['X']
                if parent not in visited:
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

        for parent in parents:
            parent_siblings = findSiblings(parent)
            piblings.update(parent_siblings)

        return pibling in piblings and pibling not in visited_parents



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

    def isBrother(brother_name,name):
        name1_siblings = list(prolog.query(f"siblings(X, {brother_name})."))
        name2_siblings = list(prolog.query(f"siblings(X, {name})."))
        maleList = list(prolog.query("man(X)"))
        found = any(f"{brother_name}" in d.values() for d in maleList)
        if found:
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
        else:
            return False

## Base

    prolog.assertz("man(X)")


## Sibling Chaining
    prolog.assertz("siblings(jerald, janine)")
    prolog.assertz("siblings(janine, jerald)")

    prolog.assertz("siblings(janine, bob)")
    prolog.assertz("siblings(bob, janine)")

    prolog.assertz("siblings(bob, john)")
    prolog.assertz("siblings(john, bob)")
    prolog.assertz("man(john)")

## Parent Chaining
    prolog.assertz("siblings(X, Y) :- parent(Z, X), parent(Z, Y)")
    prolog.asserta("parent(bob, test)")
    prolog.asserta("parent(bob, meow)")

    prolog.asserta("siblings(a,b)")
    prolog.asserta("siblings(b,a)")
    prolog.asserta("siblings(b,c)")
    prolog.asserta("siblings(c,b)")
    prolog.asserta("siblings(c,d)")
    prolog.asserta("siblings(d,c)")
    prolog.asserta("parent(wad,d)")
    prolog.asserta("siblings(x,wad)")
    prolog.asserta("siblings(tom,x)")
    prolog.asserta("siblings(james,x)")

    print("PARENT!", findParent("a"))
    print("PIBLING!",isPibling("james","c"))


    print(isParent("wad","a"))
    print(isSiblings("meow", "test"))
    print(isSiblings("a","d"))
    print(isBrother("janine","jerald"))
    print(isParent("bob","meow"))


    '''
    ## John is the brother of jerald. Need modify 66, 67.
        maleList = list(prolog.query("man(X)"))
    
        found = any("john" in d.values() for d in maleList)
        if found:
            for jerald_sibling in jerald_siblings:
                for john_sibling in john_siblings:
                    visited = set()
                    if dfs_brother(jerald_sibling['X'], john_sibling['X'], visited):
                        print("True")
                        break
                else:
                    continue
                break
            else:
                print("F")
        else:
            print("F")
    '''





    print("Hello! Type anything! /help for more info")

    while True:
        user_input = input()
        user_input = user_input.lower()

        if user_input == "/exit":
            break

        ## This section is now for question prompts.
        if all(keyword in user_input for keyword in ["are","and","siblings?"]): ## OK STABLE
            temp = user_input.split(" ")
            print(f"ONE : {temp[1]}")
            print(f"THREE : {temp[3]}")


        elif all(keyword in user_input for keyword in ["is", "a sister of", "?"]): ## NOT OK
            temp = user_input.split(" ")
            temp[5] = temp[5][:-1]
            result1 = list(prolog.query(f"siblings(X, {temp[5]})"))
            result2 = list(prolog.query(f"woman(X)"))  # Query to check if temp[1] is a woman
            if any(res['X'] == temp[1] for res in  result1) and any(res2['X'] == temp[1] for res2 in result2):
                print(f"{temp[1]} is a sister of {temp[5]}!")
            else:
                print("That's impossible!")


        ## This section is for Statement Prompts
        elif all(keyword in user_input for keyword in ["and", "are siblings"]):
            temp = user_input.split(" ")
            prolog.assertz(f"sibling({temp[0]}, {temp[2]})")
            print("OK! I learned something")

        elif all(keyword in user_input for keyword in ["is a sister of"]):
            temp = user_input.split(" ")
            prolog.assertz(f"sibling({temp[0]}, {temp[5]})")
            prolog.assertz(f"sibling({temp[5]}, {temp[0]})")
            prolog.assertz(f"woman({temp[0]})")
            print("OK! I learned something")

        elif all(keyword in user_input for keyword in ["is the mother of"]):
            temp = user_input.split(" ")
            prolog.assertz(f"parent({temp[0]}, {temp[5]})")
            prolog.assertz(f"woman({temp[0]})")
            print("OK! I learned something")
        elif all(keyword in user_input for keyword in ["is a grandmother of"]):
            temp = user_input.split(" ")
            prolog.assertz(f"grandparent({temp[0]}, {temp[5]})")
            prolog.assertz(f"woman({temp[0]})")
            print("OK! I learned something")
        elif all(keyword in user_input for keyword in ["is a child of"]):
            temp = user_input.split(" ")
            prolog.assertz(f"parent({temp[5]}, {temp[0]})")
            prolog.assertz(f"woman({temp[0]})")
            print("OK! I learned something")
        elif all(keyword in user_input for keyword in ["is a daughter of"]):
            temp = user_input.split(" ")
            prolog.assertz(f"parent({temp[5]}, {temp[0]})")
            prolog.assertz(f"woman({temp[5]})")
            print("OK! I learned something")
        elif all(keyword in user_input for keyword in ["is an uncle of"]):
            temp = user_input.split(" ")
            prolog.assertz(f"pibling({temp[0]}, {temp[5]})")
            prolog.assertz(f"man({temp[0]})")
            print("OK! I learned something")
        elif all(keyword in user_input for keyword in ["is a brother of"]):
            temp = user_input.split(" ")
            prolog.assertz(f"sibling({temp[0]}, {temp[5]})")
            prolog.assertz(f"man({temp[0]})")
            print("OK! I learned something")
        elif all(keyword in user_input for keyword in ["is the father of"]):
            temp = user_input.split(" ")
            prolog.assertz(f"parent({temp[0]}, {temp[5]})")
            prolog.assertz(f"man({temp[0]})")
            print("OK! I learned something")
        elif all(keyword in user_input for keyword in ["and","are the parents of"]):
            temp = user_input.split(" ")
            prolog.assertz(f"parent({temp[0]}, {temp[7]})")
            prolog.assertz(f"parent({temp[2]}, {temp[7]})")
            print("OK! I learned something")
        elif all(keyword in user_input for keyword in ["is a grandfather of"]):
            temp = user_input.split(" ")
            prolog.assertz(f"grandparent({temp[0]}, {temp[5]})")
            prolog.assertz(f"man({temp[0]})")
            print("OK! I learned something")
        elif all(keyword in user_input for keyword in ["and","are children of"]):
            print("This is currently broken :I")
        elif all(keyword in user_input for keyword in ["is a son of"]):
            temp = user_input.split(" ")
            prolog.assertz(f"parent({temp[5]}, {temp[0]})")
            prolog.assertz(f"man({temp[0]})")
            print("OK! I learned something")
        elif all(keyword in user_input for keyword in ["is an aunt of"]):
            temp = user_input.split(" ")
            prolog.assertz(f"pibling({temp[0]}, {temp[5]})")
            prolog.assertz(f"woman({temp[0]})")
            print("OK! I learned something")




        ## This section is for help.
        elif user_input == "/help":
            print("/exit to exit the program")


if __name__ == '__main__':
    main()
    print("Exit Success.")
