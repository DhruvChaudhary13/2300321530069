def solve_knapsack(tasks, capacity):
    """
    Solves 0/1 Knapsack problem using Dynamic Programming.
    
    Args:
        tasks: List of tuples (task_id, duration, impact)
        capacity: Maximum mechanic hours available
    
    Returns:
        dict with selected_tasks, total_impact, total_duration
    """
    n = len(tasks)
    
    # DP table: rows = tasks, columns = capacity
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    
    # Track which items are selected
    selected = [[False] * (capacity + 1) for _ in range(n + 1)]
    
    # Fill DP table
    for i in range(1, n + 1):
        task_id, duration, impact = tasks[i - 1]
        for w in range(capacity + 1):
            if duration <= w:
                # Option 1: Include this task
                include = impact + dp[i - 1][w - duration]
                # Option 2: Exclude this task
                exclude = dp[i - 1][w]
                
                if include > exclude:
                    dp[i][w] = include
                    selected[i][w] = True
                else:
                    dp[i][w] = exclude
            else:
                dp[i][w] = dp[i - 1][w]
    
    # Backtrack to find selected tasks
    w = capacity
    selected_tasks = []
    total_duration = 0
    
    for i in range(n, 0, -1):
        if selected[i][w]:
            task_id, duration, impact = tasks[i - 1]
            selected_tasks.append({
                "task_id": task_id,
                "duration": duration,
                "impact": impact
            })
            w -= duration
            total_duration += duration
    
    return {
        "selected_tasks": list(reversed(selected_tasks)),
        "total_impact": dp[n][capacity],
        "total_duration": total_duration,
        "remaining_hours": capacity - total_duration
    }