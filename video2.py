import imageio_ffmpeg
import matplotlib
from pathlib import Path
import sys
import numpy as np
import pandas as pd
matplotlib.rcParams["animation.ffmpeg_path"] = imageio_ffmpeg.get_ffmpeg_exe()

# Không cần cửa sổ đồ họa khi chỉ xuất video
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, FFMpegWriter
from matplotlib.ticker import FuncFormatter
from matplotlib.patches import Rectangle

# -------------------- CẤU HÌNH --------------------
BASE_DIR = Path(__file__).resolve().parent
CSV_FILE = BASE_DIR / "abc-2.csv"
OUTPUT_FILE = BASE_DIR / "bien_dong_gia_2_phut.mp4"

VIDEO_SECONDS = 120
FPS = 5                   # 5 FPS = 600 khung hình, nhanh hơn 10/30 FPS
N_FRAMES = VIDEO_SECONDS * FPS
DAYS_PER_CANDLE = 5
DPI = 80                  # Độ phân giải vừa phải để xuất nhanh hơn
BITRATE = 1800

BG = "#080b10"
FG = "#f2f4f8"
GRID = "#28313d"
GREEN = "#00c853"
RED = "#ff3344"
YELLOW = "#ffd400"        # Giá tham chiếu
BLUE = "#00a6ff"          # Giá sàn
PURPLE = "#b56bff"        # Giá trần

# -------------------- KIỂM TRA FFmpeg --------------------
if not CSV_FILE.exists():
    raise FileNotFoundError(
        f"Không tìm thấy file dữ liệu:\n{CSV_FILE}\n"
        "Hãy đặt abc-2.csv cùng thư mục với file Python."
    )

if not matplotlib.animation.writers.is_available("ffmpeg"):
    raise RuntimeError(
        "Matplotlib không tìm thấy FFmpeg.\n"
        "Hãy cài FFmpeg, thêm vào PATH rồi khởi động lại VS Code."
    )

# -------------------- ĐỌC DỮ LIỆU --------------------
raw = pd.read_csv(CSV_FILE, header=None).apply(pd.to_numeric, errors="coerce")
raw = raw.dropna(how="all").dropna(axis=1, how="all")

if raw.shape != (365, 7):
    raise ValueError(
        f"Cần file CSV có 365 hàng x 7 cột, nhưng nhận được {raw.shape}."
    )

prices_raw = raw.to_numpy(dtype=float)
if not np.isfinite(prices_raw).all():
    raise ValueError("CSV có ô trống hoặc giá trị không hợp lệ.")

if np.any(prices_raw <= 0):
    raise ValueError("Dữ liệu giá phải lớn hơn 0.")

print("Đã đọc dữ liệu: 365 ngày x 7 mức giá.", flush=True)
print("Đang chuẩn bị biểu đồ...", flush=True)

# Giả định cột cuối cùng là giá đóng cửa của mỗi ngày.
# Ngày đầu tiên không có ngày trước đó trong file, nên dùng mức giá đầu tiên
# của ngày đầu làm giá tham chiếu khởi tạo. Từ ngày 2 trở đi dùng đóng cửa hôm trước.
prices = np.empty_like(prices_raw)
reference = np.empty(365, dtype=float)
floor_price = np.empty(365, dtype=float)
ceiling_price = np.empty(365, dtype=float)

previous_close = float(prices_raw[0, 0])
for day in range(365):
    reference[day] = previous_close
    floor_price[day] = previous_close * 0.90
    ceiling_price[day] = previous_close * 1.10

    # Giữ các mức giá trong biên độ +/-10% theo quy ước mô phỏng.
    # Lưu ý: nếu giá CSV vượt biên thì giá dùng để vẽ sẽ bị giới hạn ở biên.
    prices[day] = np.clip(
        prices_raw[day], floor_price[day], ceiling_price[day]
    )
    previous_close = float(prices[day, -1])

# Đường xu hướng sử dụng giá đóng cửa từng ngày (cột cuối), không phải trung bình 7 cột.
daily_price = prices[:, -1]
days = np.arange(1, 366)

# -------------------- GỘP THÀNH 73 CỤM NẾN --------------------
candles = []
for start in range(0, 365, DAYS_PER_CANDLE):
    end = min(start + DAYS_PER_CANDLE, 365)
    block = prices[start:end, :].reshape(-1)

    open_price = float(prices[start, 0])
    close_price = float(prices[end - 1, -1])
    high_price = float(np.max(block))
    low_price = float(np.min(block))
    candle_ref = float(reference[start])

    candles.append({
        "x": (start + 1 + end) / 2,
        "open": open_price,
        "close": close_price,
        "high": high_price,
        "low": low_price,
        "ref": candle_ref,
    })

# -------------------- TẠO HAI BIỂU ĐỒ --------------------
plt.rcParams["font.family"] = "DejaVu Sans"
fig, (ax_candle, ax_trend) = plt.subplots(
    2, 1,
    figsize=(12, 7),
    sharex=True,
    gridspec_kw={"height_ratios": [1, 1.15], "hspace": 0.12},
)
fig.patch.set_facecolor(BG)

for ax in (ax_candle, ax_trend):
    ax.set_facecolor(BG)
    ax.tick_params(colors=FG, labelsize=8)
    for spine in ax.spines.values():
        spine.set_color("#647080")
    ax.grid(True, color=GRID, linewidth=0.45, alpha=0.65)
    ax.set_axisbelow(True)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda value, _: f"{value:,.0f}"))

ax_candle.set_title("BIỂU ĐỒ NẾN (mỗi nến đại diện 5 ngày)", color=FG, fontsize=10, pad=7)
ax_trend.set_title("XU HƯỚNG GIÁ TRONG 365 NGÀY", color=FG, fontsize=10, pad=7)
ax_candle.set_ylabel("Giá (VND)", color=FG)
ax_trend.set_ylabel("Giá (VND)", color=FG)
ax_trend.set_xlabel("Ngày giao dịch", color=FG)

all_min = min(float(prices.min()), float(floor_price.min()))
all_max = max(float(prices.max()), float(ceiling_price.max()))
pad = max((all_max - all_min) * 0.07, all_max * 0.01)
for ax in (ax_candle, ax_trend):
    ax.set_xlim(0, 366)
    ax.set_ylim(max(0, all_min - pad), all_max + pad)

# Đường giá biểu đồ dưới, chỉ hiện dần khi video chạy.
line_price, = ax_trend.plot([], [], color=FG, linewidth=1.45, label="Giá đóng cửa")
line_ref, = ax_trend.plot([], [], color=YELLOW, linewidth=1.0, label="Giá tham chiếu")
line_floor, = ax_trend.plot([], [], color=BLUE, linewidth=1.0, label="Giá sàn (90%)")
line_ceiling, = ax_trend.plot([], [], color=PURPLE, linewidth=1.0, label="Giá trần (110%)")

legend = ax_trend.legend(
    loc="upper left", ncol=4, fontsize=7, framealpha=0.75,
    facecolor="#10151d", edgecolor="#647080"
)
for text_item in legend.get_texts():
    text_item.set_color(FG)

# Nến được tạo sẵn một lần, sau đó chỉ bật dần khi tiến trình đến cụm tương ứng.
candle_artists = []
for candle in candles:
    x = candle["x"]
    opn = candle["open"]
    close = candle["close"]
    high = candle["high"]
    low = candle["low"]

    # Chỉ dùng hai màu nến theo quy ước: xanh khi đóng cửa trên tham chiếu,
    # đỏ khi đóng cửa dưới tham chiếu. Giá sàn/trần được thể hiện ở biểu đồ dưới.
    color = GREEN if close >= candle["ref"] else RED

    wick, = ax_candle.plot(
        [x, x], [low, high], color=color, linewidth=0.9,
        solid_capstyle="round", visible=False, zorder=2
    )
    body_bottom = min(opn, close)
    body_height = max(abs(close - opn), all_max * 0.001)
    body = Rectangle(
        (x - 1.25, body_bottom), 2.5, body_height,
        facecolor=color, edgecolor=color, linewidth=0.6,
        visible=False, zorder=3
    )
    ax_candle.add_patch(body)
    candle_artists.append((wick, body))

title = fig.suptitle(
    "MÔ PHỎNG BIẾN ĐỘNG GIÁ CHỨNG KHOÁN",
    color=FG, fontsize=13, fontweight="bold", y=0.985
)
progress_text = fig.text(
    0.5, 0.015, "Đang chuẩn bị...", ha="center", color=FG, fontsize=8
)
fig.subplots_adjust(left=0.10, right=0.97, top=0.92, bottom=0.08)

def update(frame):
    # Chuyển 600 khung hình thành tiến trình từ ngày 1 đến ngày 365.
    day_count = min(365, int(frame * 365 / max(N_FRAMES - 1, 1)) + 1)

    # Hiện các cụm nến tương ứng với số ngày đã đi qua.
    visible_candles = min(len(candles), int(np.ceil(day_count / DAYS_PER_CANDLE)))
    for index, (wick, body) in enumerate(candle_artists):
        is_visible = index < visible_candles
        wick.set_visible(is_visible)
        body.set_visible(is_visible)

    x = days[:day_count]
    line_price.set_data(x, daily_price[:day_count])
    line_ref.set_data(x, reference[:day_count])
    line_floor.set_data(x, floor_price[:day_count])
    line_ceiling.set_data(x, ceiling_price[:day_count])

    progress_text.set_text(
        f"Ngày {day_count}/365  |  Cụm nến {visible_candles}/73"
    )
    return (
        [line_price, line_ref, line_floor, line_ceiling,
         progress_text, title]
        + [artist for pair in candle_artists for artist in pair]
    )

ani = FuncAnimation(
    fig,
    update,
    frames=N_FRAMES,
    interval=1000 / FPS,
    blit=False,
    repeat=False,
)

writer = FFMpegWriter(
    fps=FPS,
    bitrate=BITRATE,
    metadata={"title": "Mô phỏng biến động giá chứng khoán 365 ngày"},
)

def report_progress(current_frame, total_frames):
    # In tiến độ mỗi khoảng 5% để không phải đoán chương trình có bị treo hay không.
    if current_frame == 0 or current_frame + 1 == total_frames:
        percent = int((current_frame + 1) * 100 / total_frames)
        print(f"Đang xuất video: {percent}% ({current_frame + 1}/{total_frames} khung hình)", flush=True)
    else:
        previous_percent = int(current_frame * 100 / total_frames)
        current_percent = int((current_frame + 1) * 100 / total_frames)
        if current_percent > previous_percent and current_percent % 5 == 0:
            print(f"Đang xuất video: {current_percent}%", flush=True)

try:
    print(
        f"Bắt đầu xuất video: {VIDEO_SECONDS} giây, {FPS} FPS, "
        f"{N_FRAMES} khung hình, DPI={DPI}.",
        flush=True,
    )
    ani.save(
        OUTPUT_FILE,
        writer=writer,
        dpi=DPI,
        progress_callback=report_progress,
    )
finally:
    plt.close(fig)

print(f"\nĐÃ XUẤT VIDEO THÀNH CÔNG:\n{OUTPUT_FILE}", flush=True)
print(f"Thời lượng: {VIDEO_SECONDS} giây | FPS: {FPS} | Khung hình: {N_FRAMES}", flush=True)