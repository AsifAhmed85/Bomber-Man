import Processor

EXPLOSION_RADIUS = 4


class Player:
    def __init__(self, map_data: "Processor.MapData", name=None):
        if name is None:
            self.name = "Unnamed"
        else:
            self.name = name

        self.map_data = map_data
        self.over = False
        self.success = True
        self.reset = False
        self.index = -1

    def play(self):

        while not self.over:

            self.move()
            while not self.reset:
                pass

            self.reset = False

    def can_move(self, map, x, y, d_x, d_y, ox, oy):
        stop = ['I', 'W']
        if y + d_y < 0 or y + d_y >= len(map) or x + d_x < 0 or x + d_x >= len(map[0]):
            return False
        elif map[y + d_y][x + d_x] == 'I' or map[y + d_y][x + d_x] == 'W':
            return False
        elif map[y + d_y * 1][x + d_x * 1] == 'B':
            return False
        elif ox == x + d_x and oy == y + d_y:
            return False
        return 1 <= y + d_y < len(map) -1 and 1 <= x + d_x < len(map[0]) -1

    def in_danger(self, map, x, y, ox, oy):
        up, down, left, right = True, True, True, True
        stop = ['I', 'W']
        bomb_dis = 0
        count = 0
        for i in range(1, EXPLOSION_RADIUS + 1):
            if down:
                if y + i >= len(map) or map[y + i][x] in stop or (y + i == oy and x == ox):
                    down = False
                elif map[y + i][x] == 'B':
                    bomb_dis += i
                    count += 1
            if up:
                if y - i < 0 or map[y - i][x] in stop or (y - i == oy and x == ox):
                    up = False
                elif map[y - i][x] == 'B':
                    bomb_dis += i
                    count += 1
            if right:
                if x + i >= len(map[0]) or map[y][x + i] in stop or (y == oy and x + i == ox):
                    left = False
                elif map[y][x + i] == 'B':
                    bomb_dis += i
                    count += 1
            if left:
                if x - i < 0 or map[y][x - i] in stop or (y == oy and x - i == ox):
                    left = False
                elif map[y][x - i] == 'B':
                    bomb_dis += i
                    count += 1
        return [bomb_dis, count]  # nothing

    def enemy_in_range(self, map, x, y, ox, oy):
        up, down, left, right = True, True, True, True
        stop = ['I', 'W']
        bomb_size = self.map_data.get_self_data(self)["bomb_size"]
        for i in range(1, bomb_size + 1):
            if down:
                if y + i >= len(map) or map[y + i][x] in stop:
                    down = False
                elif y + i == oy and x == ox:
                    return [i, 1]
            if up:
                if y - i < 0 or map[y - i][x] in stop:
                    up = False
                elif y - i == oy and x == ox:
                    return [i, 1]
            if right:
                if x + i >= len(map[0]) or map[y][x + i] in stop:
                    left = False
                elif y == oy and x + i == ox:
                    return [i, 1]
            if left:
                if x - i < 0 or map[y][x - i] in stop:
                    left = False
                elif y == oy and x - i == ox:
                    return [i, 1]
        return [0, 0]  # nothing

    def wall_in_range(self, map, x, y, ox, oy):
        up, down, left, right = True, True, True, True
        count = 0
        wall_dis = 0
        bomb_size = self.map_data.get_self_data(self)["bomb_size"]
        for i in range(1, bomb_size + 1):
            if down:
                if y + i >= len(map) or map[y + i][x] == 'I' or (y + i == oy and x == ox):
                    down = False
                elif map[y + i][x] == 'W':
                    count += 1
                    wall_dis += i
            if up:
                if y - i < 0 or map[y - i][x] == 'I' or (y - i == oy and x == ox):
                    up = False
                elif map[y - i][x] == 'W':
                    count += 1
                    wall_dis += i
            if right:
                if x + i >= len(map[0]) or map[y][x + i] == 'I' or (y == oy and x + i == ox):
                    left = False
                elif map[y][x + i] == 'W':
                    count += 1
                    wall_dis += i
            if left:
                if x - i < 0 or map[y][x - i] == 'I' or (y == oy and x - i == ox):
                    left = False
                elif map[y][x - i] == 'W':
                    count += 1
                    wall_dis += i

        return [wall_dis, count]

    def dis_bonus_avg(self, map, x, y):
        up, down, left, right = True, True, True, True
        bonus = ['W', '+', '0']
        count = 0
        dis = 0
        for i in range(len(map)):
            if down:
                if y + i >= len(map):
                    down = False
                elif map[y + i][x] in bonus:
                    dis += i
                    count += 1
            if up:
                if y - i < 0:
                    up = False
                elif map[y - i][x] in bonus:
                    dis += i
                    count += 1
        for i in range(len(map[0])):
            if right:
                if x + i >= len(map[0]):
                    left = False
                elif map[y][x + i] in bonus:
                    dis += i
                    count += 1
            if left:
                if x - i < 0:
                    left = False
                elif map[y][x - i] in bonus:
                    dis += i
                    count += 1
        return dis / (count + 1)

    def hero(self, node):

        bomb_dis = -self.in_danger(node.map_data, node.x, node.y, node.ox, node.oy)[0]
        bomb_count = self.in_danger(node.map_data, node.x, node.y, node.ox, node.oy)[1]
        bonus_dis = - self.dis_bonus_avg(node.map_data, node.x, node.y)
        enemy_dis = self.enemy_in_range(node.map_data, node.x, node.y, node.ox, node.oy)[0]
        enemy_count = self.enemy_in_range(node.map_data, node.x, node.y, node.ox, node.oy)[1]
        wall_dis = self.wall_in_range(node.map_data, node.x, node.y, node.ox, node.oy)[0]
        wall_count = self.wall_in_range(node.map_data, node.x, node.y, node.ox, node.oy)[1]
        if node.map_data[node.y][node.x] == 'B':
            bomb_dis -= 1;
            bomb_count += 1

        print("bomb : {0}, bonus : {1}, enemy : {2}, wall : {3}".format(bomb_count, bonus_dis, enemy_count, wall_count))
        print(2000.0 / (bomb_dis - 1) * bomb_count + bonus_dis + 100.0 / (enemy_dis + 1) * enemy_count + 200.0 / (
                wall_dis + 1) * wall_count)

        node.value = 2000.0 / (bomb_dis - 1) * bomb_count + bonus_dis + 100.0 / (
                enemy_dis + 1) * enemy_count + 200.0 / (
                             wall_dis + 1) * wall_count
        return node.value

    def move(self):
        my_info = self.map_data.get_self_data(self)
        [y, x] = my_info["coordinate"]
        my_index = my_info["index"]
        if my_index == 1:
            opponent_index = 2
        else:
            opponent_index = 1
        opponent_info = self.map_data.get_player_data(opponent_index)
        [oy, ox] = opponent_info["coordinate"]

        up, down, left, right = None, None, None, None
        current_score, up_score, down_score, left_score, right_score = None, None, None, None, None
        map = self.map_data.get_full_map()
        current = Node(map, x, y, oy, ox)
        current_score = self.hero(current)
        if self.can_move(map, x, y, 0, -1, ox, oy):
            print("IN UP")
            up = Node(map, x, y - 1, oy, ox)
            up_score = self.hero(up)
        if self.can_move(map, x, y, 0, 1, ox, oy):
            print("IN DOWN")
            down = Node(map, x, y + 1, oy, ox)
            down_score = self.hero(down)
        if self.can_move(map, x, y, -1, 0, ox, oy):
            print("IN LEFT")
            left = Node(map, x - 1, y, oy, ox)
            left_score = self.hero(left)
        if self.can_move(map, x, y, 1, 0, ox, oy):
            print("IN RIGHT")
            right = Node(map, x + 1, y, oy, ox)
            right_score = self.hero(right)
        if up_score is None:
            up_score = float("-inf")
        if down_score is None:
            down_score = float("-inf")
        if left_score is None:
            left_score = float("-inf")
        if right_score is None:
            right_score = float("-inf")

        max_score = max(current_score, up_score, down_score, left_score, right_score)
        direction = None
        if max_score == current_score:
            print("Bomb")
            self.map_data.schedule_bomb(self)
            return
        elif max_score == up_score:
            direction = 'N'
        elif max_score == down_score:
            direction = 'S'
        elif max_score == left_score:
            direction = 'W'
        elif max_score == right_score:
            direction = 'E'
        print("My coodinate ", end=' ')
        print(my_info["coordinate"])
        if direction is not None:
            print(direction)

            self.map_data.schedule_move(self, direction)

        else:
            print("Skip turn")
            self.map_data.skip_turn(self)


class Node:

    def __init__(self, map_data, x, y, ox, oy):
        self.map_data = map_data
        self.x = x
        self.y = y
        self.ox = ox
        self.oy = oy
        self.value = None
