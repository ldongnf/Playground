#!/usr/bin/env python
#-*- coding: utf8 -*-

"""
module_name, package_name, ClassName, method_name, 
ExceptionName, function_name, GLOBAL_CONSTANT_NAME, 
global_var_name, instance_var_name, 
function_parameter_name, local_var_name
"""

import random

BOARD_LENGTH = 4
LEFT 	= 0
RIGHT 	= 1
UP 		= 2
DOWN 	= 3

moves = {"w" : UP , "a" : LEFT, "s" : DOWN, "d" : RIGHT}

def generate_board():
	board = [[0 for _ in xrange(6)] for _ in xrange(6)]
	
	empty_tiles = [(i, j) for i in xrange(1, BOARD_LENGTH + 1) for j in xrange(1, BOARD_LENGTH + 1)]
	empty_tiles = random.sample(empty_tiles, 6)
	
	for row, col in empty_tiles:
		board[row][col] = random.choice([2, 4])

	return board

def display_board(board):
	print "BOARD".rjust(15)
	for row in board[1 : BOARD_LENGTH + 1]:
		line = " "
		for tile in row[1 : BOARD_LENGTH + 1]:
			line += str(tile).rjust(4) + ','
		print line[:-1]

def move(board, direction):
	if direction == UP:
		for col in xrange(1, BOARD_LENGTH + 1):
			move = False
			for row in xrange(1, BOARD_LENGTH + 1):
				if not move:
					if board[row][col] == board[row+1][col] or board[row+1][col] == 0 or board[row][col] == 0:
						board[row][col] += board[row+1][col]
						move = True
				else:
					board[row][col] = board[row+1][col]

	elif direction == DOWN:		
		for col in xrange(1, BOARD_LENGTH + 1):
			move = False
			for row in xrange(BOARD_LENGTH, 0, -1):
				if not move:
					if board[row][col] == board[row-1][col] or board[row-1][col] == 0 or board[row][col] == 0:
						board[row][col] += board[row-1][col]
						move = True
				else:
					board[row][col] = board[row-1][col]

	elif direction == LEFT:
		for row in xrange(1, BOARD_LENGTH + 1):
			move = False
			for col in xrange(1, BOARD_LENGTH + 1):
				if not move:
					if board[row][col] == board[row][col+1] or board[row][col+1] == 0 or board[row][col] == 0:
						board[row][col] += board[row][col+1]
						move = True
				else:
					board[row][col] = board[row][col+1]

	elif direction == RIGHT:
		for row in xrange(1, BOARD_LENGTH + 1):
			move = False
			for col in xrange(BOARD_LENGTH, 0, -1):
				if not move:
					if board[row][col] == board[row][col-1] or board[row][col-1] == 0 or board[row][col] == 0:
						board[row][col] += board[row][col-1]
						move = True
				else:
					board[row][col] = board[row][col-1]
	
	empty_tiles = [(i, j) for i in xrange(1, BOARD_LENGTH + 1) for j in xrange(1, BOARD_LENGTH + 1) if board[i][j] == 0]
	
	if not empty_tiles:
		return [True, board]

	if len(empty_tiles) > 1:
		empty_tiles = random.sample(empty_tiles, 1)
	for row, col in empty_tiles:
		board[row][col] = random.choice([2, 4])
	
	return [False, board]

def game_res(board):
	for row in board[1 : BOARD_LENGTH + 1]:
		for tile in row[1 : BOARD_LENGTH + 1]:
			if tile == 1024:
				return True
	return False

if __name__=='__main__':
	board = generate_board()
	display_board(board)
	print
	while True:
		m = raw_input()
		[is_game_end, board] = move(board, moves[m])
		if is_game_end:
			break
		display_board(board)
	print game_res(board)

	
	
	
