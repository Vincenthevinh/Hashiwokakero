from pysat.card import CardEnc
from collections import defaultdict

class HashiwokakeroCNF:
    def __init__(self, grid):
        self.id = 1
        self.grid = grid
        self.islands = []
        self.cnf = []
        self.hash = {}
        self.neighbors = {
            (i, j): [] for i in range(len(grid)) for j in range(len(grid[0]))
        }
        self.encode_constraints()

    def encode_constraints(self):
        """Encodes all necessary constraints into CNF."""
        directions = [(-1, 0), (1, 0), (0, 1), (0, -1)]

        # Khởi tạo biến (bridge) và thêm ràng buộc "X2 => X1" (tức không thể có 2 cầu nếu không có 1 cầu)
        for i in range(len(self.grid)):
            for j in range(len(self.grid[0])):
                if self.grid[i][j] > 0:
                    self.islands.append((i, j))
                    for dx, dy in directions:
                        nx, ny = i + dx, j + dy
                        while 0 <= nx < len(self.grid) and 0 <= ny < len(self.grid[0]):
                            if self.grid[nx][ny] > 0:
                                if ("X1", (i, j), (nx, ny)) not in self.hash:
                                    self.hash[("X1", (i, j), (nx, ny))] = self.hash[("X1", (nx, ny), (i, j))] = self.id
                                    self.hash[("X2", (i, j), (nx, ny))] = self.hash[("X2", (nx, ny), (i, j))] = (self.id + 1)

                                    # Thêm mệnh đề (¬X2 ∨ X1), tương đương X2 => X1
                                    self.cnf.append([-(self.id + 1), self.id])
                                    self.neighbors[(i, j)].append((nx, ny))

                                    self.id += 2
                                break
                            nx += dx
                            ny += dy

        # Constraint 3: Không cho phép cầu giữa các đảo sát nhau
        for i, j in self.islands:
            for nx, ny in self.neighbors[(i, j)]:
                # Nếu khoảng cách chỉ 1 ô (liền kề), không được xây cầu
                if abs(nx - i) == 1 or abs(ny - j) == 1:
                    self.cnf.append([-self.hash[("X1", (i, j), (nx, ny))]])

        # Constraint 4: Không cho phép cầu cắt nhau
        added = set()
        for i, j in self.islands:
            for z, k in self.islands:
                for x1 in self.neighbors[(i, j)]:
                    for x2 in self.neighbors[(z, k)]:
                        vector1 = (x1[0] - i, x1[1] - j)  # Hướng cầu (i,j)->x1
                        vector2 = (x2[0] - z, x2[1] - k)  # Hướng cầu (z,k)->x2

                        # Kiểm tra 1 cầu ngang, 1 cầu dọc => có thể cắt nhau
                        if not (vector1[0] == 0 and vector2[0] == 0) and not (vector1[1] == 0 and vector2[1] == 0):
                            # TH cầu (i,j)->x1 là ngang => vector1[0] == 0
                            if vector1[0] == 0:
                                # Kiểm tra xem (z,k)->x2 cắt với (i,j)->x1
                                if (x2[0] - i) * (z - i) < 0 and (j - k) * (x1[1] - k) < 0:
                                    sorted_cross = tuple(sorted([(i, j), (z, k), (x1[0], x1[1]), (x2[0], x2[1])]))
                                    if sorted_cross not in added:
                                        added.add(sorted_cross)
                                        self.cnf.append([
                                            -self.hash[("X1", (i, j), (x1[0], x1[1]))],
                                            -self.hash[("X1", (z, k), (x2[0], x2[1]))]
                                        ])
                            # TH cầu (i,j)->x1 là dọc => vector1[1] == 0
                            else:
                                if (i - z) * (x1[0] - z) < 0 and (k - j) * (x2[1] - j) < 0:
                                    sorted_cross = tuple(sorted([(i, j), (z, k), (x1[0], x1[1]), (x2[0], x2[1])]))
                                    if sorted_cross not in added:
                                        added.add(sorted_cross)
                                        self.cnf.append([
                                            -self.hash[("X1", (i, j), (x1[0], x1[1]))],
                                            -self.hash[("X1", (z, k), (x2[0], x2[1]))]
                                        ])

        # Constraint 5: Tổng số cầu phải bằng số trên đảo
        directions = [(-1, 0), (1, 0), (0, 1), (0, -1)]
        for i, j in self.islands:
            bridge_vars = []
            for dx, dy in directions:
                nx, ny = i + dx, j + dy
                while 0 <= nx < len(self.grid) and 0 <= ny < len(self.grid[0]):
                    if self.grid[nx][ny] > 0:
                        if ("X1", (i, j), (nx, ny)) in self.hash:
                            bridge_vars.append(self.hash[("X1", (i, j), (nx, ny))])
                            bridge_vars.append(self.hash[("X2", (i, j), (nx, ny))])
                        break
                    nx += dx
                    ny += dy

            if bridge_vars:
                cnf_card = CardEnc.equals(
                    lits=bridge_vars,
                    bound=self.grid[i][j],
                    top_id=self.id + 1,
                    encoding=1,
                )
                max_id = max(abs(lit) for clause in cnf_card for lit in clause)
                self.id = max(max_id + 2, self.id)
                self.cnf.extend(cnf_card)

    def get_cnf(self):
        return self.cnf
