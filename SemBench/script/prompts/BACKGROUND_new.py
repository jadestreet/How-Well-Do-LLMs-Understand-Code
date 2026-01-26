####################################
# BACKGROUND INFORMATION
####################################
background_info = {
    "function_reachability": (
        "Function_reachability examines whether one function can transitively call another (i.e., if a call path exists)."
    ),
    "loop_reachability": (
        "Loop reachability examines whether a loop is executed during program execution based on its condition and structure. "
    ),
    "dominators": (
        "Statement x dominates statement y if every path passes statement y must go through statement x."
    ),
    "data_dependency": (
        "Variable x depends on variable y if the value of x is determined by the value of y."
    ),
    "liveness": (
        "Liveness analysis determines whether a variable’s value is used later in the program. "
    ),
    "dead_code": (        
        "Dead code consists of segments that are never executed, such as code following an unconditional return or unreachable branches. "
    )
}
