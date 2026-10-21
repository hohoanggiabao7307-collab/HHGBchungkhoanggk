
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import imageio_ffmpeg

from pathlib import Path
from matplotlib.animation import FuncAnimation, FFMpegWriter
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D

# ===== CẤU HÌNH =====
BASE_DIR = Path(__file__).resolve().parent.parent
CSV_FILE = BASE_DIR / "abc-2.csv"
OUTPUT_FILE = BASE_DIR / "bien_dong_gia.mp4"

VIDEO_SECONDS = 180
FPS = 15

YELLOW = "#FFD700"
BLUE = "#2196F3"
PURPLE = "#A855F7"
RED = "#F44336"
GREEN = "#22C55E"
BG = "#111827"
TEXT = "#E5E7EB"
GRID = "#374151"

# ===== ĐỌC DỮ LIỆU =====
if not CSV_FILE.exists():
    raise FileNotFoundError(f"Không tìm thấy CSV: {CSV_FILE}")

df = pd.read_csv(CSV_FILE, header=None)
P = df.to_numpy(dtype=float)

# Cột cuối cùng là giá đóng cửa
close = P[:, -1]
n = len(close)

print("Số phiên trong CSV:", n)

if n < 2:
    raise ValueError("CSV cần có ít nhất 2 phiên.")

day = np.arange(1, n + 1)

# Giá tham chiếu = giá đóng cửa phiên trước
reference = np.empty(n)
reference[0] = close[0]
reference[1:] = close[:-1]

floor = reference * 0.90
ceiling = reference * 1.10

def get_color(i):
    p = close[i]
    ref = reference[i]

    if np.isclose(p, ref, atol=1e-6, rtol=0):
        return YELLOW
    elif np.isclose(p, floor[i], atol=1e-6, rtol=0):
        return BLUE
    elif np.isclose(p, ceiling[i], atol=1e-6, rtol=0):
        return PURPLE
    elif p < ref:
        return RED
    else:
        return GREEN

# Chênh lệch giá đóng cửa giữa hai phiên
change = np.zeros(n)
change[1:] = close[1:] - close[:-1]

# ===== THIẾT LẬP BIỂU ĐỒ =====
plt.rcParams["font.family"] = ["DejaVu Sans", "Arial", "sans-serif"]

fig, (ax1, ax2) = plt.subplots(
    2, 1,
    figsize=(14, 8),
    gridspec_kw={"height_ratios": [2.2, 1]}
)

fig.patch.set_facecolor(BG)
fig.subplots_adjust(
    left=0.09, right=0.77,
    top=0.90, bottom=0.12, hspace=0.32
)

for ax in (ax1, ax2):
    ax.set_facecolor(BG)
    ax.tick_params(colors=TEXT)
    ax.spines["bottom"].set_color(GRID)
    ax.spines["left"].set_color(GRID)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, color=GRID, alpha=0.45)
    ax.set_axisbelow(True)

# ===== BIỂU ĐỒ GIÁ ĐÓNG CỬA =====
ax1.set_title(
    "BIẾN ĐỘNG GIÁ ĐÓNG CỬA",
    color="white", fontsize=15, fontweight="bold"
)
ax1.set_ylabel("Giá đóng cửa", color=TEXT)
ax1.set_xlim(1, n)

low = min(close.min(), floor.min())
high = max(close.max(), ceiling.max())
span = max(high - low, 1)
ax1.set_ylim(low - span * 0.08, high + span * 0.08)

ref_line, = ax1.plot([], [], color=YELLOW, lw=1.1)
floor_line, = ax1.plot([], [], color=BLUE, lw=1.0)
ceil_line, = ax1.plot([], [], color=PURPLE, lw=1.0)

price_line = LineCollection([], linewidths=2.4)
ax1.add_collection(price_line)

dots, = ax1.plot(
    [], [], linestyle="None",
    marker="o", color="white", markersize=3
)

legend_price = [
    Line2D([0], [0], color=YELLOW, lw=2,
           label="Bằng giá tham chiếu"),
    Line2D([0], [0], color=BLUE, lw=2,
           label="Bằng giá sàn (90%)"),
    Line2D([0], [0], color=PURPLE, lw=2,
           label="Bằng giá trần (110%)"),
    Line2D([0], [0], color=RED, lw=2,
           label="Dưới tham chiếu"),
    Line2D([0], [0], color=GREEN, lw=2,
           label="Trên tham chiếu"),
]

ax1.legend(
    handles=legend_price,
    loc="upper left", bbox_to_anchor=(1.015, 1),
    facecolor="#1F2937", edgecolor=GRID,
    labelcolor=TEXT, fontsize=8
)

# ===== BIỂU ĐỒ TĂNG/GIẢM GIÁ =====
ax2.set_title(
    "MỨC TĂNG / GIẢM GIÁ ĐÓNG CỬA",
    color="white", fontsize=11, fontweight="bold"
)
ax2.set_ylabel("Chênh lệch giá", color=TEXT)
ax2.set_xlabel("Phiên giao dịch", color=TEXT)
ax2.set_xlim(0.5, n + 0.5)

max_change = max(float(np.abs(change).max()), 1.0)
ax2.set_ylim(-max_change * 1.15, max_change * 1.15)
ax2.axhline(0, color=TEXT, lw=0.8)

legend_change = [
    Line2D([0], [0], color=GREEN, lw=5,
           label="Tăng so với phiên trước"),
    Line2D([0], [0], color=RED, lw=5,
           label="Giảm so với phiên trước"),
]

ax2.legend(
    handles=legend_change,
    loc="upper left", bbox_to_anchor=(1.015, 1),
    facecolor="#1F2937", edgecolor=GRID,
    labelcolor=TEXT, fontsize=8
)

status = fig.text(0.09, 0.945, "", color=TEXT, fontsize=10)

fig.text(
    0.5, 0.035,
    "Biểu đồ dưới là mức tăng/giảm giá, không phải volume.",
    color="#9CA3AF", fontsize=8, ha="center"
)

# Tạo cột đúng một lần
bar_colors = [
    GREEN if change[j] >= 0 else RED
    for j in range(n)
]

bars = ax2.bar(
    day, np.zeros(n),
    color=bar_colors, width=0.8
)

# ===== HOẠT ẢNH =====
total_frames = VIDEO_SECONDS * FPS

def update(frame):
    # Hiển thị tiến trình từ phiên đầu đến phiên cuối
    i = min(n, int((frame + 1) * n / total_frames))
    i = max(1, i)

    x = day[:i]

    ref_line.set_data(x, reference[:i])
    floor_line.set_data(x, floor[:i])
    ceil_line.set_data(x, ceiling[:i])
    dots.set_data(x, close[:i])

    # Nối giá đóng cửa của các phiên liên tiếp
    if i >= 2:
        points = np.column_stack(
            (day[:i], close[:i])
        ).reshape(-1, 1, 2)

        segments = np.concatenate(
            [points[:-1], points[1:]], axis=1
        )

        price_line.set_segments(segments)
        price_line.set_color([
            get_color(j) for j in range(1, i)
        ])
    else:
        price_line.set_segments([])

    # Chỉ cập nhật các cột có sẵn
    for j, bar in enumerate(bars):
        if j < i:
            bar.set_height(change[j])
            bar.set_visible(True)
        else:
            bar.set_visible(False)

    status.set_text(
        f"Phiên {i}/{n} | "
        f"Giá đóng cửa: {close[i - 1]:,.2f}"
    )

    return (
        ref_line, floor_line, ceil_line,
        price_line, dots, status
    )

# ===== XUẤT MP4 =====
ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
plt.rcParams["animation.ffmpeg_path"] = ffmpeg_path

animation = FuncAnimation(
    fig,
    update,
    frames=range(total_frames),
    interval=1000 / FPS,
    blit=False,
    repeat=False
)

writer = FFMpegWriter(fps=FPS, bitrate=1800)

try:
    print(f"Đang xuất video {VIDEO_SECONDS} giây...")
    print(f"Tổng số khung hình: {total_frames}")

    animation.save(
        str(OUTPUT_FILE),
        writer=writer,
        dpi=80
    )

    print("ĐÃ XUẤT VIDEO THÀNH CÔNG!")
    print("Đường dẫn:", OUTPUT_FILE)
    print("Số phiên:", n)
    print("Thời lượng dự kiến:", VIDEO_SECONDS, "giây")

except Exception:
    import traceback
    print("LỖI KHI XUẤT VIDEO:")
    traceback.print_exc()

finally:
    plt.close(fig)
