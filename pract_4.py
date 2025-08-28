resources = {
    1: "Basics of Python",
    2: "Data Structures",
    3: "Algorithms",
    4: "Databases",
    5: "Machine Learning",
    6: "Deep Learning"
}


def recommend_path(current_level, goal_level):
    path = []
    while current_level < goal_level:
        next_level = current_level + 1
        path.append(resources[next_level])
        current_level = next_level
    return path


if __name__ == "__main__":
    current = int(input("Enter your current knowledge level (1-6): "))
    goal = int(input("Enter your target knowledge level (1-6): "))

    if current >= goal:
        print("You have already reached or exceeded your goal!")
    else:
        plan = recommend_path(current, goal)
        print("\nRecommended Learning Path:")
        for step, res in enumerate(plan, 1):
            print(f" Step {step}: {res}")

