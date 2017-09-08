#!/usr/bin/env python
#-*- coding: utf8 -*-
import copy
import pygame,sys
from pygame.locals import *

# tile Catagray
__BLACK_TILE__ = 1
__WHITE_TILE__ = -1
__EMPTY_TILE__ = 0

__FONT_SIZE__ = 16

# FPS
__FPS__ = 60

# graphic size
__WINDOW_WIDTH__  = 600
__WINDOW_HEIGHT__ = 600

__BOARD_WIDTH__ = 8
__BOARD_HEIGHT__ = 8

__BOX_SIZE__ = 50
__GAP_SIZE__ = 0 #8

__X_MARGIN__ = int((__WINDOW_WIDTH__ - (__BOARD_WIDTH__ * (__BOX_SIZE__ + __GAP_SIZE__))) / 2)
__Y_MARGIN__ = int((__WINDOW_HEIGHT__ - (__BOARD_HEIGHT__ * (__BOX_SIZE__ + __GAP_SIZE__))) / 2)

# color settings
#              R    G    B
WHITE		= (255, 255, 240)
BLACK		= (  0,   0,   0)
BLUE 		= (  0,   0, 255)
RED			= (250,   0,   0)
GREEN      	= (175, 221,  34)
BRIGHTBLUE 	= (  0,  50, 255)
BROWN      	= (174,  94,   0)
SKYBLUE		= (249, 214,  91)
GOLDEN		= (242, 190,  69)

BGCOLOR	= GOLDEN
EMPTY_COLOR = GREEN
TEXTCOLOR = BLACK
TEXTBGCOLOR1 = BGCOLOR
TEXTBGCOLOR2 = GREEN


class Player(object):
	def __init__(self, piece, search_depth=None, heuristics=None):
		self.piece = piece
		self.search_depth = search_depth 
		self.heuristics = heuristics
		self.next_move = None

	def think_next_move(self, board):
		tree = GameTree(self.piece, self.search_depth, board, self.heuristics)
		tree.generate_game_tree()
		self.next_move = tree.next_move

class GameTree(object):
	def __init__(self, piece, search_depth, board, heuristics):
		self.piece = piece
		self.search_depth = search_depth
		self.board = board
		self.heuristics = heuristics
		self.root = None
		self.next_move = None
	
	def generate_game_tree(self):
		# move [-1, -1] root [-2, -2] pass
		self.root = TreeNode(0, (-1, -1), self.board, self.piece, self.piece)
		self.alpha_beta_prunning(self.root, self.search_depth, True, -sys.maxint, sys.maxint, self.root.curr_piece)

		for child in self.root.children:
			if self.root.eval == child.eval:
				self.next_move = child.move

	def alpha_beta_prunning(self, root, depth, continue_generate, alpha, beta, player):
		if root and depth > 0 and continue_generate:
			children_nodes = self.generate_children(root)
			for child in children_nodes:
				if child.move == root.move:
					self.alpha_beta_prunning(child, depth-1, False, alpha, beta, player)
				else:
					self.alpha_beta_prunning(child, depth-1, True, alpha, beta, player)
				if root.curr_piece == player: #max
					root.eval = max(root.eval, child.eval)
					root.children.append(child)
					if root.eval >= beta:
						break
					alpha = max(alpha, root.eval)
				else:
					root.eval = min(root.eval, child.eval)
					root.children.append(child)
					if root.eval <= alpha:
						break
					beta = min(beta, root.eval)
		else:
			self.evaluation(root)
	
	def evaluation(self, node):
		val = 0
		heuristics = self.heuristics
		for i in xrange(8):
			for j in xrange(8):
				val += node.board.board[i][j] * heuristics[i][j]
		node.eval = val * node.root_player

	def generate_children(self, node):
		possible_move = node.board.get_possible_moves(node.curr_piece)
		children_nodes = []
		if possible_move:
			for next_move in sorted(possible_move.keys()):
				new_board = node.board.flip_tiles(next_move, possible_move[next_move], node.curr_piece)
				new_node =  TreeNode(node.depth+1, next_move, new_board, -node.curr_piece, node.root_player)
				children_nodes.append(new_node)
		else:
			new_board = copy.deepcopy(node.board)
			new_node =  TreeNode(node.depth+1, (-2, -2), new_board, -node.curr_piece, node.root_player)
			children_nodes.append(new_node)
		return children_nodes

class TreeNode(object):
	def __init__(self, depth, move, board, curr_piece, root_player):
		self.depth = depth
		self.move = move
		self.board = board
		self.curr_piece = curr_piece
		self.root_player = root_player
		self.eval = -sys.maxint if depth % 2 == 0 else sys.maxint
		self.children = []

class Board(object):
	def __init__(self, board=[]):
		self.board = board

	def reset_board(self):
		self.board = [[0 for i in xrange(8)] for j in xrange(8)]
		self.board[3][3] = -1
		self.board[3][4] = 1
		self.board[4][3] = 1
		self.board[4][4] = -1
	
	def get_board(self):
		return self.board

	def read_board_from_file(self, fname):
		self.board = []
		with open(fname, "rb") as input_file:
			for line in input_file:
				curr_line = []
				for tile in line:		
					if tile == "O":
						curr_line.append(__WHITE_TILE__)
					if tile == "X":
						curr_line.append(__BLACK_TILE__)
					if tile == "*":
						curr_line.append(__EMPTY_TILE__)
				self.board.append(curr_line)
		return True

	def provide_hint(self, curr_piece):
		possible_moves = self.get_possible_moves(curr_piece)
		return sorted(possible_moves.keys())

	def get_possible_moves(self, curr_piece):
		directions = [[-1, -1], [0, -1], [+1, -1], [-1, 0], [+1, 0], [-1, +1], [0, +1], [+1, +1]]
		possible_move = {} #{(2, 3):[[2, 7], [3, 4]], [2, 5]:[[], []]}
		for i in xrange(8):
			for j in xrange(8):
				if self.board[i][j] == 0:
					for direction in directions:
						row, col = i + direction[0], j + direction[1]
						if row >= 0 and row < 8 and col >= 0 and col < 8 and self.board[row][col] == - curr_piece:
							end = self.follow_direction(i, j, curr_piece, direction, self.board)
							if end:
								if (i, j) in possible_move:
									possible_move[(i, j)].append([end, direction])
								else:
									possible_move[(i, j)] = [[end, direction]]
		return possible_move

	def follow_direction(self, row, col, curr_piece, direction, board):
		x, y = row + direction[0], col + direction[1]
		while x >= 0 and x < 8 and y >= 0 and y < 8 and board[x][y] == - curr_piece:
			x += direction[0]
			y += direction[1]
		if x >= 0 and x < 8 and y >= 0 and y < 8 and board[x][y] == curr_piece:
			return [x, y]
		else:
			return None
	
	def update_new_board(self, piece, move):
		possible_moves = self.get_possible_moves(piece)
		if move not in possible_moves:
			return False
		else:
			self.board = self.flip_tiles(move, possible_moves[move], piece).board
			return True

	def flip_tiles(self, next_move, infos, curr_piece):
		new_board = Board(copy.deepcopy(self.board))
		for end_direction in infos:
			x, y = next_move[0], next_move[1]
			end, direction = end_direction[0], end_direction[1]
			end_x, end_y = end[0], end[1]
			while x != end_x or y != end_y:
				new_board.board[x][y] = curr_piece
				x += direction[0]
				y += direction[1]
		return new_board

	def is_game_end(self):
		possible_moves_black = self.get_possible_moves(__BLACK_TILE__)
		possible_moves_white = self.get_possible_moves(__WHITE_TILE__)

		if possible_moves_white or possible_moves_black:
			return False
		else:
			return True

	def display_board(self):
		print "0 0 1 2 3 4 5 6 7"
		for index, line in enumerate(self.board):
			row = str(index)+ " "
			for tile in line:
				if tile == __EMPTY_TILE__:
					row += "* "
				if tile == __WHITE_TILE__:
					row += "O "
				if tile == __BLACK_TILE__:
					row += "X "
			print row[:-1]

	def get_score(self):
		tile_black = 0
		tile_white = 0
		for row in self.board:
			for tile in row:
				if tile == __BLACK_TILE__:
					tile_black += 1
				if tile == __WHITE_TILE__:
					tile_white += 1
		return (tile_black, tile_white)

class Game:
	def __init__(self):
		self.heuristics_X = [
			[99, -8, 8, 6, 6, 8, -8, 99], 
			[-8, -24, -4, -3, -3, -4, -24, -8],
			[8, -4, 7, 4, 4, 7, -4, 8],
			[6, -3, 4, 0, 0, 4, -3, 6],
			[6, -3, 4, 0, 0, 4, -3, 6],
			[8, -4, 7, 4, 4, 7, -4, 8],
			[-8, -24, -4, -3, -3, -4, -24, -8],
			[99, -8, 8, 6, 6, 8, -8, 99]]

		self.heuristics_Y= [
			[4 ,-3 ,2 ,2 ,2 ,2 ,-3 ,4],
			[-3, -4, -1, -1, -1, -1, -4, -3],
			[2, -1, 1, 0 ,0 ,1 ,-1 ,2],
			[2, -1, 0, 1 ,1, 0,-1 ,2],
			[2, -1, 0, 1 ,1 ,0 ,-1 ,2],
			[2, -1, 1, 0,0 ,1 ,-1 ,2],
			[-3, -4, -1, -1 ,-1 ,-1 ,-4 ,-3],
			[4, -3, 2, 2 ,2, 2 ,-3 , 4]]

		self.history = []
		
		self.board = Board()
		self.board.reset_board()
		self.history.append(copy.deepcopy(self.board.board))

		pygame.init()
		self.FPS_CLOCK = pygame.time.Clock()
		self.DISPLAY_SURF = pygame.display.set_mode((__WINDOW_WIDTH__, __WINDOW_HEIGHT__))
		pygame.display.set_caption("Reversi")
		self.DISPLAY_SURF.fill(BGCOLOR)
		pygame.display.update()
		#self.draw_board(self.board)
		mode = self.get_mode()
		if mode == 1:
			self.single_mode()
		if mode == 2:
			self.bot_mode()

	def get_mode(self):
		self.DISPLAY_SURF.fill(BGCOLOR)
		FONT = pygame.font.Font('freesansbold.ttf', 16)
		BIGFONT = pygame.font.Font('freesansbold.ttf', 32)
		textSurf = FONT.render('Which game mode would you like to choose?', True, TEXTCOLOR, TEXTBGCOLOR1)
		textRect = textSurf.get_rect()
		textRect.center = (int(__WINDOW_WIDTH__ / 2), int(__WINDOW_HEIGHT__ / 2.5))

		xSurf = BIGFONT.render('SINGLE', True, TEXTCOLOR, TEXTBGCOLOR1)
		xRect = xSurf.get_rect()
		xRect.center = (int(__WINDOW_WIDTH__ / 2) - 60, int(__WINDOW_HEIGHT__ / 2.5) + 40)

		oSurf = BIGFONT.render('BOT', True, TEXTCOLOR, TEXTBGCOLOR1)
		oRect = oSurf.get_rect()
		oRect.center = (int(__WINDOW_WIDTH__ / 2) + 60, int(__WINDOW_HEIGHT__ / 2.5) + 40)

		while True:
			# Keep looping until the player has clicked on a color.
			for event in pygame.event.get(): # event handling loop
				if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
					pygame.quit()
					sys.exit()
				elif event.type == MOUSEBUTTONUP:
					mousex, mousey = event.pos
					if xRect.collidepoint( (mousex, mousey) ):
						return 1
					elif oRect.collidepoint( (mousex, mousey) ):
						return 2

	        # Draw the screen.
			self.DISPLAY_SURF.blit(textSurf, textRect)
			self.DISPLAY_SURF.blit(xSurf, xRect)
			self.DISPLAY_SURF.blit(oSurf, oRect)
			pygame.display.update()
			self.FPS_CLOCK.tick(__FPS__)

	def get_tile(self):
		self.DISPLAY_SURF.fill(BGCOLOR)
		FONT = pygame.font.Font('freesansbold.ttf', 16)
		BIGFONT = pygame.font.Font('freesansbold.ttf', 32)
		textSurf = FONT.render('Do you want to be white or black?', True, TEXTCOLOR, TEXTBGCOLOR1)
		textRect = textSurf.get_rect()
		textRect.center = (int(__WINDOW_WIDTH__ / 2), int(__WINDOW_HEIGHT__ / 2.5))

		xSurf = BIGFONT.render('White', True, TEXTCOLOR, TEXTBGCOLOR1)
		xRect = xSurf.get_rect()
		xRect.center = (int(__WINDOW_WIDTH__ / 2) - 60, int(__WINDOW_HEIGHT__ / 2.5) + 40)

		oSurf = BIGFONT.render('Black', True, TEXTCOLOR, TEXTBGCOLOR1)
		oRect = oSurf.get_rect()
		oRect.center = (int(__WINDOW_WIDTH__ / 2) + 60, int(__WINDOW_HEIGHT__ / 2.5) + 40)

		while True:
			# Keep looping until the player has clicked on a color.
			for event in pygame.event.get(): # event handling loop
				if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
					pygame.quit()
					sys.exit()
				elif event.type == MOUSEBUTTONUP:
					mousex, mousey = event.pos
					if xRect.collidepoint( (mousex, mousey) ):
						return [__WHITE_TILE__, __BLACK_TILE__]
					elif oRect.collidepoint( (mousex, mousey) ):
						return [__BLACK_TILE__, __WHITE_TILE__]

	        # Draw the screen.
			self.DISPLAY_SURF.blit(textSurf, textRect)
			self.DISPLAY_SURF.blit(xSurf, xRect)
			self.DISPLAY_SURF.blit(oSurf, oRect)
			pygame.display.update()
			self.FPS_CLOCK.tick(__FPS__)
		
	def single_mode(self):
		playerTile, computerTile = self.get_tile()
		#print playerTile,computerTile
		mouse_x = 0
		mouse_y = 0

		human = Player(playerTile)
		bot = Player(computerTile, 3, self.heuristics_X)
		#print "Human: %s, Computer: %s" % (human.piece, bot.piece)
		show_hint = False

		while True:
			mouse_clicked = False

			self.DISPLAY_SURF.fill(BGCOLOR)
			self.draw_board(self.board)
			
			self.display_score(human, bot)

			for event in pygame.event.get():
				if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
					pygame.quit()
					sys.exit()
				elif event.type == KEYUP and event.key == K_z:
					# regret func
					if len(self.history) >= 3:
						temp = self.history.pop()
						temp = self.history.pop()
						temp = self.history.pop()
						self.board = Board(temp)
						self.history.append(copy.deepcopy(self.board.board))
						pygame.display.update()
						continue
				elif event.type == KEYUP and event.key == K_x:
					show_hint = show_hint ^ True

				elif event.type == MOUSEBUTTONUP:
					mouse_x, mouse_y = event.pos
					mouse_clicked = True

			row, col = self.translate_pixel_to_box(mouse_x, mouse_y)
			possible_moves = self.board.provide_hint(human.piece)
			if show_hint:
				self.draw_hint(self.board, possible_moves)
			if row != None and col != None:
				if mouse_clicked == True:
					move = (row, col)
					

					if not possible_moves:
						bot.think_next_move(self.board)
						#print move,bot.next_move

						self.board.update_new_board(bot.piece, bot.next_move)
						
						self.history.append(copy.deepcopy(self.board.board))
						#self.board.display_board()
					else:

						if move in possible_moves:
							self.board.update_new_board(human.piece, move)
							self.history.append(copy.deepcopy(self.board.board))
							#self.board.display_board()

							bot.think_next_move(self.board)
							#print move,bot.next_move

							self.board.update_new_board(bot.piece, bot.next_move)
							self.history.append(copy.deepcopy(self.board.board))
							#self.board.display_board()
					
			pygame.time.wait(100)
			pygame.display.update()
			self.FPS_CLOCK.tick(__FPS__)

			if self.board.is_game_end():
				for event in pygame.event.get():
					if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
						pygame.quit()
						sys.exit()

	def bot_mode(self):
		bot_x = Player(__BLACK_TILE__, 3, self.heuristics_X)
		bot_y = Player(__WHITE_TILE__, 3, self.heuristics_Y)

		state = 1 # running -1 pause

		while True:
			self.DISPLAY_SURF.fill(BGCOLOR)
			self.draw_board(self.board)
			self.display_score(bot_x, bot_y)
			
			for event in pygame.event.get():
				if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
					pygame.quit()
					sys.exit() 
				elif event.type == KEYUP and event.key == K_SPACE:
					state = - state
			if state == -1:
				continue
			bot_x.think_next_move(self.board)
			#print move,bot.next_move

			self.board.update_new_board(bot_x.piece, bot_x.next_move)
			#self.board.display_board()
			pygame.display.update()
			pygame.time.wait(500)

			bot_y.think_next_move(self.board)
			#print move,bot.next_move

			self.board.update_new_board(bot_y.piece, bot_y.next_move)
			#self.board.display_board()
			self.FPS_CLOCK.tick(__FPS__)

			pygame.display.update()
			pygame.time.wait(500)
			if self.board.is_game_end():
				for event in pygame.event.get():
					if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
						pygame.quit()
						sys.exit() 

	def draw_board(self, board):
		half = int(__BOX_SIZE__ * 0.5)
		board = board.get_board()
		for row in xrange(__BOARD_HEIGHT__):
			for col in xrange(__BOARD_WIDTH__):
				left, top = self.translate_box_to_pixel(row, col)
				if board[row][col] == __EMPTY_TILE__:
					pygame.draw.rect(self.DISPLAY_SURF, EMPTY_COLOR, (left, top, __BOX_SIZE__, __BOX_SIZE__))
				if board[row][col] == __BLACK_TILE__:
					pygame.draw.rect(self.DISPLAY_SURF, EMPTY_COLOR, (left, top, __BOX_SIZE__, __BOX_SIZE__))
					pygame.draw.circle(self.DISPLAY_SURF, BLACK, (left + half, top + half), half - 3)
				if board[row][col] == __WHITE_TILE__:
					pygame.draw.rect(self.DISPLAY_SURF, EMPTY_COLOR, (left, top, __BOX_SIZE__, __BOX_SIZE__))
					pygame.draw.circle(self.DISPLAY_SURF, WHITE, (left + half, top + half), half - 3)
		
		# Draw grid lines of the board.
		for x in range(__BOARD_WIDTH__ + 1):
			# Draw the horizontal lines.
			startx = (x * __BOX_SIZE__) + __X_MARGIN__
			starty = __Y_MARGIN__
			endx = (x * __BOX_SIZE__) + __X_MARGIN__
			endy = __Y_MARGIN__ + (__BOARD_HEIGHT__ * __BOX_SIZE__)
			pygame.draw.line(self.DISPLAY_SURF, BLACK, (startx, starty), (endx, endy))
		
		for y in range(__BOARD_HEIGHT__ + 1):
        # Draw the vertical lines.
			startx = __X_MARGIN__
			starty = (y * __BOX_SIZE__) + __Y_MARGIN__
			endx = __X_MARGIN__ + (__BOARD_WIDTH__ * __BOX_SIZE__)
			endy = (y * __BOX_SIZE__) + __Y_MARGIN__
			pygame.draw.line(self.DISPLAY_SURF, BLACK, (startx, starty), (endx, endy))

	def draw_hint(self, board, possible_moves):
		half = int(__BOX_SIZE__ * 0.5)
		quarter = int(__BOX_SIZE__ * 0.25) 
		board = board.get_board()
		for move in possible_moves:
			left, top = self.translate_box_to_pixel(move[0], move[1])
			pygame.draw.rect(self.DISPLAY_SURF, RED, (left + quarter, top + quarter, __BOX_SIZE__ - half, __BOX_SIZE__ - half))

	def translate_box_to_pixel(self, row, col):
		left = col * (__BOX_SIZE__ + __GAP_SIZE__) + __X_MARGIN__
		top = row * (__BOX_SIZE__ + __GAP_SIZE__) + __Y_MARGIN__
		return (left, top)

	def translate_pixel_to_box(self, x, y):
		for row in xrange(__BOARD_HEIGHT__):
			for col in xrange(__BOARD_WIDTH__):
				left, top = self.translate_box_to_pixel(row, col)
				boxRect = pygame.Rect(left, top, __BOX_SIZE__, __BOX_SIZE__)
				# you can pass X and Y coordinates too and it will return True if the coordinates are inside
				if boxRect.collidepoint(x, y):
					return (row, col)
		return (None, None)

	def display_score(self, player1, player2):
		(x_score, y_score) = self.board.get_score()
		FONT = pygame.font.Font('freesansbold.ttf', __FONT_SIZE__)
		label = []
		label.append(FONT.render("Player1: %s" % ("Black" if player1.piece == __BLACK_TILE__ else "White"), True, TEXTCOLOR))
		label.append(FONT.render("Player2: %s" % ("Black" if player2.piece == __BLACK_TILE__ else "White"), True, TEXTCOLOR))
		
		label.append(FONT.render("BLACK Score: %d" % x_score, True, TEXTCOLOR))
		label.append(FONT.render("WHITE Score: %d" % y_score, True, TEXTCOLOR))
		
		for line in xrange(len(label)):
			self.DISPLAY_SURF.blit(label[line], 
				(10, __WINDOW_HEIGHT__ - 5.5 * __FONT_SIZE__ + (line * __FONT_SIZE__) + line * 5))

	def display_winner(self):
		FONT = pygame.font.Font('freesansbold.ttf', 16)
		BIGFONT = pygame.font.Font('freesansbold.ttf', 32)
		textSurf = FONT.render('Winner', True, TEXTCOLOR, TEXTBGCOLOR1)
		textRect = textSurf.get_rect()
		textRect.center = (int(__WINDOW_WIDTH__ / 2), int(__WINDOW_HEIGHT__ / 2))

		xSurf = BIGFONT.render('White', True, TEXTCOLOR, TEXTBGCOLOR1)
		xRect = xSurf.get_rect()
		xRect.center = (int(__WINDOW_WIDTH__ / 2) - 60, int(__WINDOW_HEIGHT__ / 2) + 40)

		oSurf = BIGFONT.render('Black', True, TEXTCOLOR, TEXTBGCOLOR1)
		oRect = oSurf.get_rect()
		oRect.center = (int(__WINDOW_WIDTH__ / 2) + 60, int(__WINDOW_HEIGHT__ / 2) + 40)

		while True:
	        # Keep looping until the player has clicked on a color.

			for event in pygame.event.get(): # event handling loop
				if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
					pygame.quit()
					sys.exit()
				elif event.type == MOUSEBUTTONUP:
			 		mousex, mousey = event.pos
					if xRect.collidepoint( (mousex, mousey) ):
						return [__WHITE_TILE__, __BLACK_TILE__]
					elif oRect.collidepoint( (mousex, mousey) ):
						return [__BLACK_TILE__, __WHITE_TILE__]

			# Draw the screen.
			self.DISPLAY_SURF.blit(textSurf, textRect)
			self.DISPLAY_SURF.blit(xSurf, xRect)
			self.DISPLAY_SURF.blit(oSurf, oRect)
			pygame.display.update()
			self.FPS_CLOCK.tick(__FPS__)

if __name__== "__main__":
	game = Game()

	







	
		

