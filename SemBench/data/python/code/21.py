# 21.py — Sudoku solver with backtracking and helpers
# Provides: parse_board, is_valid, find_empty, solve, format_board
from typing import List, Optional, Tuple

Board = List[List[int]]

def parse_board(lines: List[str]) -> Board:
    board: Board = []
    for line in lines:
        row = []
        for ch in line.strip():
            if ch == '.':
                row.append(0)
            elif ch.isdigit():
                row.append(int(ch))
        if len(row) == 9:
            board.append(row)
    if len(board) != 9:
        raise ValueError("invalid board")
    return board

def is_valid(board: Board, r: int, c: int, val: int) -> bool:
    # row check
    for j in range(9):
        if board[r][j] == val:
            return False
    # col check
    for i in range(9):
        if board[i][c] == val:
            return False
    # 3x3 box
    br, bc = (r // 3) * 3, (c // 3) * 3
    for i in range(br, br + 3):
        for j in range(bc, bc + 3):
            if board[i][j] == val:
                return False
    return True

def find_empty(board: Board) -> Optional[Tuple[int, int]]:
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return (i, j)
    return None

def solve(board: Board) -> bool:
    pos = find_empty(board)
    if pos is None:
        return True
    r, c = pos
    for val in range(1, 10):
        if is_valid(board, r, c, val):
            board[r][c] = val
            if solve(board):
                return True
            board[r][c] = 0
    return False

def format_board(board: Board) -> str:
    out = []
    for i, row in enumerate(board):
        if i % 3 == 0 and i != 0:
            out.append("------+-------+------")
        parts = []
        for j, v in enumerate(row):
            if j % 3 == 0 and j != 0:
                parts.append("|")
            parts.append(str(v) if v != 0 else ".")
        out.append(" ".join(parts))
    return "\n".join(out)
