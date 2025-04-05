import time
import psutil

from hashiwokakero_cnf import HashiwokakeroCNF
from pysat_solver import PySATSolver
from astar_solver import AStarSolver
from backtracking_solver import BacktrackingSolver
from bruteforce_solver import BruteForceSolver

# Import các hàm từ utils.py
from utils import (
    choose_input_file,
    read_input_from_file,
    solution_to_text,
    write_output_to_file
)

def run_solver(name, solver_cls, cnf, grid, hashi_cnf):
    """
    Hàm tiện ích để chạy solver theo class (solver_cls) truyền vào,
    đo thời gian, bộ nhớ và trả về kết quả + thống kê để ghi ra file.
    """
    process = psutil.Process()
    start_time = time.time()
    start_mem = process.memory_info().rss

    solver = solver_cls(cnf)
    solution = solver.solve()

    end_time = time.time()
    end_mem = process.memory_info().rss

    duration_ms = (end_time - start_time) * 1000
    mem_used_mb = (end_mem - start_mem) / (1024 * 1024)

    output_lines = []
    if solution:
        output_lines.append(f"=== {name} solution ===")
        map_lines = solution_to_text(grid, solution, hashi_cnf.hash)
        output_lines.extend(map_lines)
        output_lines.append(f"Thời gian ({name}): {duration_ms:.4f} ms")
        output_lines.append(f"Memory usage ({name}): {mem_used_mb:.4f} MB\n")
    else:
        msg = f"No solution found ({name})."
        output_lines.append(msg)
        output_lines.append(f"Thời gian ({name}): {duration_ms:.4f} ms")
        output_lines.append(f"Memory usage ({name}): {mem_used_mb:.4f} MB\n")

    return output_lines


def main():
    # Bước 1: Cho người dùng chọn file input
    input_file = choose_input_file()
    if not input_file:
        return  # Không có file nào hoặc người dùng hủy

    # Bước 2: Đọc dữ liệu từ file
    grid = read_input_from_file(input_file)

    # Bước 3: Xây dựng CNF
    hashi_cnf = HashiwokakeroCNF(grid)
    cnf = hashi_cnf.get_cnf()

    # Menu để người dùng chọn thuật toán
    while True:
        print("Chọn thuật toán muốn giải (nhập số):")
        print("1. A*")
        print("2. pySAT")
        print("3. Backtracking")
        print("4. Brute Force")
        print("5. Giải tất cả (A*, pySAT, Backtracking, Brute Force)")
        print("0. Thoát")

        choice = input("Lựa chọn của bạn: ")

        # Chuỗi output để ghi ra file
        output_lines = []

        if choice == '1':
            # Giải bằng A*
            output_lines = run_solver("A*", AStarSolver, cnf, grid, hashi_cnf)
            break

        elif choice == '2':
            # Giải bằng pySAT
            output_lines = run_solver("pySAT", PySATSolver, cnf, grid, hashi_cnf)
            break

        elif choice == '3':
            # Giải bằng Backtracking
            output_lines = run_solver("Backtracking", BacktrackingSolver, cnf, grid, hashi_cnf)
            break

        elif choice == '4':
            # Giải bằng Brute Force
            output_lines = run_solver("Brute Force", BruteForceSolver, cnf, grid, hashi_cnf)
            break

        elif choice == '5':
            # Giải tất cả
            output_lines.extend(run_solver("A*", AStarSolver, cnf, grid, hashi_cnf))
            output_lines.extend(run_solver("pySAT", PySATSolver, cnf, grid, hashi_cnf))
            output_lines.extend(run_solver("Backtracking", BacktrackingSolver, cnf, grid, hashi_cnf))
            output_lines.extend(run_solver("Brute Force", BruteForceSolver, cnf, grid, hashi_cnf))
            break

        elif choice == '0':
            print("Đã thoát chương trình.")
            return
        else:
            print("Lựa chọn không hợp lệ. Vui lòng nhập lại.\n")
            continue

    # ------------ Ghi kết quả ra file ------------
    final_content = "\n".join(output_lines) + "\n"
    write_output_to_file(input_file, final_content)
    print("Kết quả đã được ghi ra file output tương ứng.")


if __name__ == "__main__":
    main()
