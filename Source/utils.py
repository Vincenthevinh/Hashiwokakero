import os

def choose_input_file():
    """
    Liệt kê tất cả file trong thư mục Inputs/ 
    và yêu cầu người dùng chọn một file để đọc.
    
    Trả về đường dẫn đầy đủ của file được chọn.
    """
    folder = "Inputs"
    files = [f for f in os.listdir(folder) if f.endswith(".txt")]
    if not files:
        print("Không tìm thấy file .txt nào trong thư mục Inputs/")
        return None
    
    print("Các file có trong thư mục Inputs/:")
    for idx, f in enumerate(files, start=1):
        print(f"{idx}. {f}")

    while True:
        choice = input("Nhập số thứ tự của file bạn muốn dùng: ")
        if choice.isdigit():
            choice_idx = int(choice)
            if 1 <= choice_idx <= len(files):
                selected_file = files[choice_idx - 1]
                print(f"Bạn đã chọn: {selected_file}")
                return os.path.join(folder, selected_file)
        print("Lựa chọn không hợp lệ, vui lòng thử lại.")


def read_input_from_file(filename):
    """
    Đọc file 'filename' và chuyển nội dung thành một danh sách các hàng (grid).
    """
    grid = []
    with open(filename, 'r') as file:
        for line in file:
            # Tách bằng ',' và loại bỏ khoảng trắng dư thừa
            row = list(map(int, [x.strip() for x in line.strip().split(',')]))
            grid.append(row)
    return grid


def solution_to_text(grid, solution, hash_dict):
    """
    Trả về danh sách các dòng (list of strings) mô tả lưới kèm các cầu.
    Mỗi phần tử trong danh sách là 1 dòng (string).
    """
    rows, cols = len(grid), len(grid[0])
    display_grid = [["0" for _ in range(cols)] for _ in range(rows)]
    
    # Đặt các đảo vào lưới hiển thị
    for i in range(rows):
        for j in range(cols):
            if grid[i][j] > 0:
                display_grid[i][j] = str(grid[i][j])
    
    # Thêm cầu vào lưới hiển thị
    for (key, var) in hash_dict.items():
        # key = ("X1"/"X2", (x1,y1), (x2,y2))
        if var in solution:
            (x1, y1), (x2, y2) = key[1], key[2]
            if x1 == x2:  # Cầu ngang
                bridge_char = '-' if key[0] == "X1" else '='
                for y in range(min(y1, y2) + 1, max(y1, y2)):
                    display_grid[x1][y] = bridge_char
            else:  # Cầu dọc
                bridge_char = '|' if key[0] == "X1" else '$'
                for x in range(min(x1, x2) + 1, max(x1, x2)):
                    display_grid[x][y1] = bridge_char
    
    # Tạo list các dòng (string) để trả về
    lines = []
    for row in display_grid:
        lines.append(" ".join(row))
    return lines


def write_output_to_file(input_filepath, content):
    """
    Ghi 'content' vào file trong thư mục Outputs/ với tên
    thay 'input' thành 'output'. 
    Ví dụ:
      input_filepath = "Inputs/input1.txt"
      -> output_filepath = "Outputs/output1.txt"
    """
    filename = os.path.basename(input_filepath)
    output_filename = filename.replace("input", "output")

    output_folder = "Outputs"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    output_path = os.path.join(output_folder, output_filename)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Đã ghi kết quả vào file: {output_path}")
