extends Node2D

const GRID_SIZE := 8
const CELL_SIZE := 64
const CANDY_TYPES := 6
const BOARD_OFFSET := Vector2(384, 104)  # Center 512x512 in 1280x720
const MARGIN := 4.0

const CANDY_TEXTURES: Array[Texture2D] = [
	preload("res://assets/sprites/candy_0.png"),
	preload("res://assets/sprites/candy_1.png"),
	preload("res://assets/sprites/candy_2.png"),
	preload("res://assets/sprites/candy_3.png"),
	preload("res://assets/sprites/candy_4.png"),
	preload("res://assets/sprites/candy_5.png"),
]

var grid: Array = []
var candy_nodes: Array = []
var selected := Vector2i(-1, -1)
var is_animating := false
var score := 0
var score_label: Label

var sfx_swap: AudioStreamPlayer
var sfx_match: AudioStreamPlayer
var sfx_no_match: AudioStreamPlayer
var sfx_cascade: AudioStreamPlayer
var sfx_refill: AudioStreamPlayer


func _ready() -> void:
	_init_sfx()
	_init_grid()
	_draw_board()
	_create_score_label()


func _init_sfx() -> void:
	sfx_swap = _make_sfx_player("res://assets/sfx/swap.ogg")
	sfx_match = _make_sfx_player("res://assets/sfx/match.ogg")
	sfx_no_match = _make_sfx_player("res://assets/sfx/no_match.ogg")
	sfx_cascade = _make_sfx_player("res://assets/sfx/cascade.ogg")
	sfx_refill = _make_sfx_player("res://assets/sfx/refill.ogg")


func _make_sfx_player(path: String) -> AudioStreamPlayer:
	var player := AudioStreamPlayer.new()
	player.stream = load(path)
	player.bus = &"Master"
	add_child(player)
	return player


func _init_grid() -> void:
	grid.resize(GRID_SIZE)
	candy_nodes.resize(GRID_SIZE)
	for x in GRID_SIZE:
		grid[x] = []
		candy_nodes[x] = []
		grid[x].resize(GRID_SIZE)
		candy_nodes[x].resize(GRID_SIZE)
		for y in GRID_SIZE:
			grid[x][y] = _random_candy_no_match(x, y)
			candy_nodes[x][y] = null


func _random_candy_no_match(x: int, y: int) -> int:
	var type := randi() % CANDY_TYPES
	var attempts := 0
	while _would_match(x, y, type) and attempts < CANDY_TYPES:
		type = (type + 1) % CANDY_TYPES
		attempts += 1
	return type


func _would_match(x: int, y: int, type: int) -> bool:
	if x >= 2 and grid[x - 1][y] == type and grid[x - 2][y] == type:
		return true
	if y >= 2 and grid[x][y - 1] == type and grid[x][y - 2] == type:
		return true
	return false


func _draw_board() -> void:
	# Board background
	var bg := ColorRect.new()
	bg.position = BOARD_OFFSET - Vector2(4, 4)
	bg.size = Vector2(GRID_SIZE * CELL_SIZE + 8, GRID_SIZE * CELL_SIZE + 8)
	bg.color = Color(0.12, 0.12, 0.18)
	add_child(bg)

	# All cells first (background layer)
	for x in GRID_SIZE:
		for y in GRID_SIZE:
			var cell := ColorRect.new()
			cell.position = _grid_to_pixel(Vector2i(x, y))
			cell.size = Vector2(CELL_SIZE, CELL_SIZE)
			if (x + y) % 2 == 0:
				cell.color = Color(0.2, 0.2, 0.27)
			else:
				cell.color = Color(0.23, 0.23, 0.3)
			add_child(cell)

	# All candies after (always on top of cells)
	for x in GRID_SIZE:
		for y in GRID_SIZE:
			_create_candy_node(x, y)


func _create_candy_node(x: int, y: int) -> void:
	if grid[x][y] < 0:
		return
	var candy := Sprite2D.new()
	candy.texture = CANDY_TEXTURES[grid[x][y]]
	candy.centered = false
	candy.position = _grid_to_pixel(Vector2i(x, y)) + Vector2(MARGIN, MARGIN)
	add_child(candy)
	candy_nodes[x][y] = candy


func _create_score_label() -> void:
	score_label = Label.new()
	score_label.position = Vector2(40, 30)
	score_label.text = "Score: 0"
	score_label.add_theme_font_size_override("font_size", 32)
	score_label.add_theme_color_override("font_color", Color.WHITE)
	add_child(score_label)


func _grid_to_pixel(cell: Vector2i) -> Vector2:
	return BOARD_OFFSET + Vector2(cell.x * CELL_SIZE, cell.y * CELL_SIZE)


func _pixel_to_grid(pixel: Vector2) -> Vector2i:
	var local := pixel - BOARD_OFFSET
	if local.x < 0 or local.y < 0:
		return Vector2i(-1, -1)
	var gx := int(local.x / CELL_SIZE)
	var gy := int(local.y / CELL_SIZE)
	if gx < GRID_SIZE and gy < GRID_SIZE:
		return Vector2i(gx, gy)
	return Vector2i(-1, -1)


func _input(event: InputEvent) -> void:
	if is_animating:
		return
	if not (event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_LEFT):
		return

	var cell := _pixel_to_grid(event.position)
	if cell == Vector2i(-1, -1):
		return

	if selected == Vector2i(-1, -1):
		selected = cell
		_highlight(cell, true)
	elif selected == cell:
		_highlight(cell, false)
		selected = Vector2i(-1, -1)
	elif _is_adjacent(selected, cell):
		_highlight(selected, false)
		_try_swap(selected, cell)
	else:
		_highlight(selected, false)
		selected = cell
		_highlight(cell, true)


func _is_adjacent(a: Vector2i, b: Vector2i) -> bool:
	return abs(a.x - b.x) + abs(a.y - b.y) == 1


func _highlight(cell: Vector2i, on: bool) -> void:
	var node: Sprite2D = candy_nodes[cell.x][cell.y]
	if node:
		node.modulate = Color(1.4, 1.4, 1.4) if on else Color.WHITE


func _try_swap(a: Vector2i, b: Vector2i) -> void:
	is_animating = true
	selected = Vector2i(-1, -1)

	sfx_swap.play()
	_swap_data(a, b)
	await _animate_swap(a, b)

	var matches := _find_matches()
	if matches.is_empty():
		# No match — swap back
		sfx_no_match.play()
		_swap_data(a, b)
		await _animate_swap(a, b)
	else:
		await _process_matches(matches, false)

	is_animating = false


func _swap_data(a: Vector2i, b: Vector2i) -> void:
	var tmp: int = grid[a.x][a.y]
	grid[a.x][a.y] = grid[b.x][b.y]
	grid[b.x][b.y] = tmp

	var tmp_node: Sprite2D = candy_nodes[a.x][a.y]
	candy_nodes[a.x][a.y] = candy_nodes[b.x][b.y]
	candy_nodes[b.x][b.y] = tmp_node


func _animate_swap(a: Vector2i, b: Vector2i) -> void:
	var node_a: Sprite2D = candy_nodes[a.x][a.y]
	var node_b: Sprite2D = candy_nodes[b.x][b.y]
	var pos_a := _grid_to_pixel(a) + Vector2(MARGIN, MARGIN)
	var pos_b := _grid_to_pixel(b) + Vector2(MARGIN, MARGIN)

	var tween := create_tween().set_parallel(true)
	tween.tween_property(node_a, "position", pos_a, 0.15)
	tween.tween_property(node_b, "position", pos_b, 0.15)
	await tween.finished


func _find_matches() -> Array[Vector2i]:
	var matched: Dictionary = {}

	# Horizontal
	for y in GRID_SIZE:
		var run := 1
		for x in range(1, GRID_SIZE):
			if grid[x][y] == grid[x - 1][y] and grid[x][y] >= 0:
				run += 1
			else:
				if run >= 3:
					for i in range(x - run, x):
						matched[Vector2i(i, y)] = true
				run = 1
		if run >= 3:
			for i in range(GRID_SIZE - run, GRID_SIZE):
				matched[Vector2i(i, y)] = true

	# Vertical
	for x in GRID_SIZE:
		var run := 1
		for y in range(1, GRID_SIZE):
			if grid[x][y] == grid[x][y - 1] and grid[x][y] >= 0:
				run += 1
			else:
				if run >= 3:
					for i in range(y - run, y):
						matched[Vector2i(x, i)] = true
				run = 1
		if run >= 3:
			for i in range(GRID_SIZE - run, GRID_SIZE):
				matched[Vector2i(x, i)] = true

	var result: Array[Vector2i] = []
	for key in matched:
		result.append(key)
	return result


func _process_matches(matches: Array[Vector2i], is_cascade: bool = false) -> void:
	if is_cascade:
		sfx_cascade.play()
	else:
		sfx_match.play()

	# Remove matched candies
	for cell in matches:
		var node: Sprite2D = candy_nodes[cell.x][cell.y]
		if node:
			node.queue_free()
			candy_nodes[cell.x][cell.y] = null
		grid[cell.x][cell.y] = -1

	score += matches.size() * 10
	score_label.text = "Score: %d" % score

	await get_tree().create_timer(0.1).timeout

	# Gravity
	await _apply_gravity()

	# Refill empty cells
	await _refill()
	sfx_refill.play()

	# Chain reaction
	var new_matches := _find_matches()
	if not new_matches.is_empty():
		await _process_matches(new_matches, true)


func _apply_gravity() -> void:
	var moves := []

	for x in GRID_SIZE:
		var write := GRID_SIZE - 1
		for y in range(GRID_SIZE - 1, -1, -1):
			if grid[x][y] >= 0:
				if write != y:
					grid[x][write] = grid[x][y]
					grid[x][y] = -1
					candy_nodes[x][write] = candy_nodes[x][y]
					candy_nodes[x][y] = null
					moves.append({
						node = candy_nodes[x][write],
						target = _grid_to_pixel(Vector2i(x, write)) + Vector2(MARGIN, MARGIN),
					})
				write -= 1

	if moves.is_empty():
		return

	var tween := create_tween().set_parallel(true)
	for m in moves:
		tween.tween_property(m.node, "position", m.target, 0.2)
	await tween.finished


func _refill() -> void:
	var drops := []

	for x in GRID_SIZE:
		var empty_count := 0
		for y in GRID_SIZE:
			if grid[x][y] < 0:
				empty_count += 1

		var drop_index := 0
		for y in GRID_SIZE:
			if grid[x][y] < 0:
				grid[x][y] = randi() % CANDY_TYPES
				_create_candy_node(x, y)
				var node: Sprite2D = candy_nodes[x][y]
				var target: Vector2 = node.position
				# Start above board, staggered by position
				node.position.y = BOARD_OFFSET.y - (empty_count - drop_index) * CELL_SIZE
				drops.append({node = node, target = target})
				drop_index += 1

	if drops.is_empty():
		return

	var tween := create_tween().set_parallel(true)
	for d in drops:
		tween.tween_property(d.node, "position", d.target, 0.25)
	await tween.finished
