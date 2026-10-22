def generate_plan(msg, context):

    if "7-day" in msg.lower():
        return """
Day 1: Arrays revision
Day 2: Strings
Day 3: Two Pointers
Day 4: Sliding Window
Day 5: DP basics
Day 6: Graphs
Day 7: Mock test
"""

    return """
Week 1: Basics
Week 2: Medium Problems
Week 3: DP + Graphs
Week 4: Contest + Revision
"""