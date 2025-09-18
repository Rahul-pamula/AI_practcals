class FamilyTree:
    def __init__(self):
        self.tree = {}
        self.relationships = {}
        self.gender = {}

    def add_person(self, name, gender):
        self.gender[name] = gender.lower()

    def add_relationship(self, parent, children):
        if parent not in self.tree:
            self.tree[parent] = []
        for child in children:
            if child not in self.tree[parent]:
                self.tree[parent].append(child)
            self.relationships[child] = parent

    def find_all_relations(self, relation_type):
        results = []
        if relation_type == "father":
            for father, children in self.tree.items():
                for child in children:
                    results.append(f"father({father},{child})")
        elif relation_type == "son":
            for child, parent in self.relationships.items():
                if self.gender.get(child) == 'male':
                    results.append(f"son({child},{parent})")
        elif relation_type == "daughter":
            for child, parent in self.relationships.items():
                if self.gender.get(child) == 'female':
                    results.append(f"daughter({child},{parent})")
        elif relation_type == "siblings":
            for parent, children in self.tree.items():
                for i in range(len(children)):
                    for j in range(i + 1, len(children)):
                        results.append(f"siblings({children[i]},{children[j]})")
        elif relation_type == "brother":
            for parent, children in self.tree.items():
                for i in range(len(children)):
                    for j in range(i + 1, len(children)):
                        if (self.gender.get(children[i]) == 'male' and 
                            self.gender.get(children[j]) == 'male'):
                            results.append(f"brother({children[i]},{children[j]})")
                            results.append(f"brother({children[j]},{children[i]})")
        elif relation_type == "sister":
            for parent, children in self.tree.items():
                for i in range(len(children)):
                    for j in range(i + 1, len(children)):
                        if (self.gender.get(children[i]) == 'female' and 
                            self.gender.get(children[j]) == 'female'):
                            results.append(f"sister({children[i]},{children[j]})")
                            results.append(f"sister({children[j]},{children[i]})")
        elif relation_type == "cousins":
            all_people = list(set(list(self.tree.keys()) + list(self.relationships.keys())))
            for person1 in all_people:
                for person2 in all_people:
                    if person1 != person2 and self.are_cousins(person1, person2):
                        results.append(f"cousins({person1},{person2})")
        elif relation_type == "uncle":
            for person in self.relationships.keys():
                parent = self.relationships.get(person)
                if parent and parent in self.relationships:
                    grandparent = self.relationships[parent]
                    for sibling in self.tree.get(grandparent, []):
                        if sibling != parent and self.gender.get(sibling) == 'male':
                            results.append(f"uncle({sibling},{person})")
        elif relation_type == "aunt":
            for person in self.relationships.keys():
                parent = self.relationships.get(person)
                if parent and parent in self.relationships:
                    grandparent = self.relationships[parent]
                    for sibling in self.tree.get(grandparent, []):
                        if sibling != parent and self.gender.get(sibling) == 'female':
                            results.append(f"aunt({sibling},{person})")
        elif relation_type == "grandfather":
            for child, parent in self.relationships.items():
                if parent in self.relationships:
                    grandfather = self.relationships[parent]
                    if self.gender.get(grandfather) == 'male':
                        results.append(f"grandfather({grandfather},{child})")
        elif relation_type == "grandmother":
            for child, parent in self.relationships.items():
                if parent in self.relationships:
                    grandmother = self.relationships[parent]
                    if self.gender.get(grandmother) == 'female':
                        results.append(f"grandmother({grandmother},{child})")
        elif relation_type == "grandson":
            for child, parent in self.relationships.items():
                if parent in self.relationships:
                    grandfather = self.relationships[parent]
                    if self.gender.get(child) == 'male':
                        results.append(f"grandson({child},{grandfather})")
        elif relation_type == "granddaughter":
            for child, parent in self.relationships.items():
                if parent in self.relationships:
                    grandfather = self.relationships[parent]
                    if self.gender.get(child) == 'female':
                        results.append(f"granddaughter({child},{grandfather})")
        elif relation_type == "descendant":
            all_people = list(set(list(self.tree.keys()) + list(self.relationships.keys())))
            for person1 in all_people:
                for person2 in all_people:
                    if person1 != person2 and self.is_descendant(person1, person2):
                        results.append(f"descendant({person1},{person2})")
        return list(set(results))

    def are_cousins(self, person1, person2):
        parent1 = self.relationships.get(person1)
        parent2 = self.relationships.get(person2)
        if not parent1 or not parent2 or parent1 == parent2:
            return False
        return self.are_siblings(parent1, parent2)

    def are_siblings(self, person1, person2):
        for parent, children in self.tree.items():
            if person1 in children and person2 in children and person1 != person2:
                return True
        return False

    def is_descendant(self, descendant, ancestor):
        current = descendant
        while current in self.relationships:
            parent = self.relationships[current]
            if parent == ancestor:
                return True
            current = parent
        return False

    def display_tree(self):
        print("\nFamily Tree:")
        print("-" * 40)
        for parent, children in self.tree.items():
            gender_symbol = "♂" if self.gender.get(parent) == 'male' else "♀"
            print(f"{parent} {gender_symbol} -> {', '.join(children)}")
        print("-" * 40)

def main():
    family = FamilyTree()
    print("Family Relationship Builder")
    print("=" * 50)
    
    while True:
        print("\nOptions:")
        print("1. Add a person with gender")
        print("2. Add parent-child relationship")
        print("3. Find all relations of a type")
        print("4. Display family tree")
        print("5. Exit")
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            name = input("Enter person's name: ").strip()
            if not name:
                print("Name cannot be empty!")
                continue
            gender = input("Enter gender (male/female): ").strip().lower()
            if gender not in ['male', 'female']:
                print("Gender must be 'male' or 'female'!")
                continue
            family.add_person(name, gender)
            print(f"Added {name} ({gender})")

        elif choice == "2":
            parent = input("Enter parent's name: ").strip()
            if not parent:
                print("Parent's name cannot be empty!")
                continue
            if parent not in family.gender:
                print(f"{parent} not found! Please add this person first.")
                continue
            
            children_input = input("Enter children (comma separated): ").strip()
            if not children_input:
                print("At least one child is required!")
                continue
            
            children = [child.strip() for child in children_input.split(',') if child.strip()]
            
            missing_children = [child for child in children if child not in family.gender]
            if missing_children:
                print(f"These children are not registered: {', '.join(missing_children)}")
                print("Please add them first using option 1.")
                continue
            
            family.add_relationship(parent, children)
            print(f"Added {parent} as parent of: {', '.join(children)}")

        elif choice == "3":
            if not family.tree:
                print("Family tree is empty! Add some relationships first.")
                continue

            print("\nAvailable relations: father, mother, son, daughter, siblings, brother, sister,")
            print("cousins, uncle, aunt, grandfather, grandmother, grandson, granddaughter, descendant")
            relation_type = input("Enter relation type: ").strip().lower()

            if relation_type not in ['father', 'mother', 'son', 'daughter', 'siblings', 'brother', 'sister',
                                   'cousins', 'uncle', 'aunt', 'grandfather', 'grandmother', 'grandson',
                                   'granddaughter', 'descendant']:
                print("Invalid relation type!")
                continue

            results = family.find_all_relations(relation_type)
            if results:
                print(f"\nAll {relation_type} relations:")
                for r in sorted(results):
                    print(r)
                print(f"Total: {len(results)} relations found")
            else:
                print(f"No {relation_type} relations found!")

        elif choice == "4":
            if not family.tree:
                print("Family tree is empty!")
            else:
                family.display_tree()

        elif choice == "5":
            print("Goodbye!")
            break

        else:
            print("Invalid choice! Please enter 1-5.")

if __name__ == "__main__":
    main()
