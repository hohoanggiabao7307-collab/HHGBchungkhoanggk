import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# ============================================================
# IN BẢNG RA TERMINAL
# ============================================================
def in_bang(tieu_de, bang):
    if isinstance(bang, pd.Series):
        bang = bang.to_frame()

    print(f"\n{tieu_de.center(100)}")

    if bang.empty:
        print("Không có dữ liệu.")
        return

    bang = bang.copy()

    # Chuyển dữ liệu sang chuỗi và căn giữa các cột
    bang = bang.astype(str)

    ten_cot = [str(bang.index.name or "STT")] + [
        str(cot) for cot in bang.columns
    ]

    du_lieu = []
    for chi_so, dong in bang.iterrows():
        du_lieu.append([str(chi_so)] + [str(x) for x in dong])

    # Tính độ rộng từng cột
    do_rong = []
    for j, ten in enumerate(ten_cot):
        cac_gia_tri = [dong[j] for dong in du_lieu]
        do_rong.append(max([len(ten)] + [len(x) for x in cac_gia_tri]))

    # In bảng có đường viền
    duong_ke = "+" + "+".join("-" * (r + 2) for r in do_rong) + "+"

    print(duong_ke)
    print("|" + "|".join(
        f" {ten.center(do_rong[i])} "
        for i, ten in enumerate(ten_cot)
    ) + "|")
    print(duong_ke)

    for dong in du_lieu:
        print("|" + "|".join(
            f" {gia_tri.center(do_rong[i])} "
            for i, gia_tri in enumerate(dong)
        ) + "|")

    print(duong_ke)


# ============================================================
# ĐỌC VÀ KIỂM TRA DỮ LIỆU
# ============================================================

df = pd.read_csv("abc-2.csv", header=None)
P = df.to_numpy(dtype=float)

in_bang("KÍCH THƯỚC DỮ LIỆU", pd.Series({
    "Số dòng": df.shape[0],
    "Số cột": df.shape[1]
}))

in_bang("5 DÒNG ĐẦU TIÊN CỦA DỮ LIỆU", df.head())

in_bang("THỐNG KÊ TỔNG QUAN DỮ LIỆU", df.describe())

in_bang("SỐ GIÁ TRỊ THIẾU THEO CỘT", df.isna().sum())


# ============================================================
# XỬ LÝ CÂU 1
# ============================================================

# Tạo ngày cho 365 dòng
# Tạm quy ước dòng đầu tiên là ngày 01/01/2025
dates = pd.date_range(
    start="2025-01-01",
    periods=365,
    freq="D"
)

# Chuyển 7 cột giá thành một cột giá dài
# Mỗi ngày có 7 mức giá
prices = df.to_numpy().ravel()

data = pd.DataFrame({
    "Ngày": np.repeat(dates, 7),
    "Giá": prices
})

data["Tháng"] = data["Ngày"].dt.month

# Thống kê giá theo tháng
monthly = data.groupby("Tháng")["Giá"].agg(
    Giá_trung_bình="mean",
    Độ_lệch_chuẩn="std",
    Giá_thấp_nhất="min",
    Giá_cao_nhất="max"
)

# Tính biên độ giá theo tháng
monthly["Biên độ"] = (
    monthly["Giá_cao_nhất"] - monthly["Giá_thấp_nhất"]
)

in_bang("BẢNG THỐNG KÊ GIÁ THEO THÁNG", monthly.round(2))

# Xác định tháng có biên độ giá lớn nhất
thang_max = monthly["Biên độ"].idxmax()
bien_do_max = monthly.loc[thang_max, "Biên độ"]

print("\n" + "=" * 60)
print(f"THÁNG CÓ BIÊN ĐỘ GIÁ LỚN NHẤT: THÁNG {thang_max}".center(60))
print(f"BIÊN ĐỘ GIÁ: {bien_do_max:.2f} VNĐ".center(60))
print("=" * 60)

# Vẽ biểu đồ cột giá trung bình mỗi tháng
plt.figure(figsize=(10, 5))
plt.bar(
    monthly.index,
    monthly["Giá_trung_bình"],
    color="steelblue"
)
plt.title("Giá trung bình theo tháng")
plt.xlabel("Tháng")
plt.ylabel("Giá (VNĐ)")
plt.xticks(range(1, 13))
plt.grid(axis="y", linestyle="--", alpha=0.4)
plt.tight_layout()
plt.show()

# Vẽ Boxplot giá mỗi tháng
box_data = [
    data.loc[data["Tháng"] == thang, "Giá"]
    for thang in range(1, 13)
]

plt.figure(figsize=(12, 6))
plt.boxplot(box_data, tick_labels=range(1, 13))
plt.title("Phân bố giá theo tháng")
plt.xlabel("Tháng")
plt.ylabel("Giá (VNĐ)")
plt.grid(axis="y", linestyle="--", alpha=0.4)
plt.tight_layout()
plt.show()

# In 5 dòng đầu tiên
in_bang("5 DÒNG ĐẦU TIÊN CỦA TỪNG CỘT", df.head())

# Tương quan giữa 7 cột
in_bang("MA TRẬN TƯƠNG QUAN GIỮA 7 CỘT", df.corr().round(3))

# Giá trị dòng đầu tiên
in_bang("GIÁ TRỊ DÒNG ĐẦU TIÊN", df.iloc[0])

# KẾT LUẬN CÂU 1
# Giá trị trung bình tăng từ tháng 1 đến tháng 3.
# Giá trị trung bình giảm từ tháng 4 đến tháng 5.
# Trong tháng 11 có biên độ giá lớn nhất theo kết quả tính toán.
# Phần Boxplot cho thấy mức độ phân tán giá khác nhau giữa các tháng.


# ============================================================
# XỬ LÝ CÂU 2
# ============================================================

# Xác định quý từ tháng
data["Quý"] = ((data["Tháng"] - 1) // 3) + 1

quarterly = data.groupby("Quý")["Giá"].agg(
    Giá_trung_bình="mean",
    Độ_lệch_chuẩn="std",
    Giá_thấp_nhất="min",
    Giá_cao_nhất="max"
)

# Tính biên độ giá theo quý
quarterly["Biên độ"] = (
    quarterly["Giá_cao_nhất"] - quarterly["Giá_thấp_nhất"]
)

in_bang("BẢNG THỐNG KÊ GIÁ THEO QUÝ", quarterly.round(2))

# Vẽ biểu đồ biên độ giá theo quý
plt.figure(figsize=(8, 5))
plt.bar(
    quarterly.index,
    quarterly["Biên độ"],
    color="orange"
)
plt.title("Biên độ giá theo từng quý")
plt.xlabel("Quý")
plt.ylabel("Biên độ giá (VNĐ)")
plt.xticks([1, 2, 3, 4], ["Quý 1", "Quý 2", "Quý 3", "Quý 4"])
plt.grid(axis="y", linestyle="--", alpha=0.4)
plt.tight_layout()
plt.show()

# Xác định quý có biên độ giá lớn nhất
quy_max = quarterly["Biên độ"].idxmax()
bien_do_quy_max = quarterly.loc[quy_max, "Biên độ"]

print("\n" + "=" * 60)
print(f"QUÝ CÓ BIÊN ĐỘ GIÁ LỚN NHẤT: QUÝ {quy_max}".center(60))
print(f"BIÊN ĐỘ GIÁ: {bien_do_quy_max:.2f} VNĐ".center(60))
print("=" * 60)

print("\n" + "=" * 65)
print("ĐÁNH GIÁ CÂU 2".center(65))
print("=" * 65)
print("Giá có sự biến động khác nhau giữa các quý.")
print("Quý có biên độ giá lớn nhất cho thấy khoảng cách giữa")
print("giá cao nhất và giá thấp nhất trong quý đó lớn nhất.")
print("Nhìn chung, mức độ biến động giá giữa các quý không đồng đều.")


# ============================================================
# XỬ LÝ CÂU 3
# ============================================================

gia_dong_cua = P[:, 6]
ket_qua = []

for i in range(1, len(P)):
    gia_tham_chieu = gia_dong_cua[i - 1]
    gia_san = gia_tham_chieu * 0.9
    gia_tran = gia_tham_chieu * 1.1
    gia_hom_nay = gia_dong_cua[i]

    # Chỉ xét giá cuối ngày ở cột thứ 7
    if (
        np.isclose(gia_hom_nay, gia_san, rtol=0, atol=1e-6)
        or np.isclose(gia_hom_nay, gia_tran, rtol=0, atol=1e-6)
        or np.isclose(gia_hom_nay, gia_tham_chieu, rtol=0, atol=1e-6)
    ):
        if np.isclose(gia_hom_nay, gia_san, rtol=0, atol=1e-6):
            loai = "Giá sàn"
        elif np.isclose(gia_hom_nay, gia_tran, rtol=0, atol=1e-6):
            loai = "Giá trần"
        else:
            loai = "Giá tham chiếu"

        ket_qua.append({
            "Ngày giao dịch": i + 1,
            "Giá tham chiếu": gia_tham_chieu,
            "Giá sàn": gia_san,
            "Giá trần": gia_tran,
            "Giá cuối ngày": gia_hom_nay,
            "Loại bất thường": loai
        })

df_ket_qua = pd.DataFrame(ket_qua)

# Làm tròn các cột giá để hiển thị dễ đọc
if not df_ket_qua.empty:
    for cot in [
        "Giá tham chiếu",
        "Giá sàn",
        "Giá trần",
        "Giá cuối ngày"
    ]:
        df_ket_qua[cot] = df_ket_qua[cot].map(
            lambda x: f"{x:.2f}"
        )

in_bang("CÁC NGÀY GIAO DỊCH CÓ YẾU TỐ BẤT THƯỜNG", df_ket_qua)

print("\n" + "=" * 60)
print(f"TỔNG SỐ NGÀY BẤT THƯỜNG: {len(df_ket_qua)}".center(60))
print("=" * 60)



# ============================================================
# XỬ LÝ CÂU 4
# ============================================================

# Xác định quý cho từng ngày giao dịch
data["Quý"] = ((data["Tháng"] - 1) // 3) + 1

# Lấy giá của 2 quý đầu năm (Quý 1 và Quý 2)
gia_2_quy_dau = data.loc[
    data["Quý"].isin([1, 2]), "Giá"
]

# Lấy giá của 2 quý cuối năm (Quý 3 và Quý 4)
gia_2_quy_cuoi = data.loc[
    data["Quý"].isin([3, 4]), "Giá"
]

# Vẽ tổ chức đồ phân bố giá của 2 quý đầu năm
plt.figure(figsize=(10, 5))
plt.hist(
    gia_2_quy_dau,
    bins=20,
    color="steelblue",
    edgecolor="black"
)
plt.title("Phân bố giá của 2 quý đầu năm (Quý 1 và Quý 2)")
plt.xlabel("Giá (VNĐ)")
plt.ylabel("Tần suất")
plt.grid(axis="y", linestyle="--", alpha=0.4)
plt.tight_layout()
plt.show()

# Vẽ tổ chức đồ phân bố giá của 2 quý cuối năm
plt.figure(figsize=(10, 5))
plt.hist(
    gia_2_quy_cuoi,
    bins=20,
    color="orange",
    edgecolor="black"
)
plt.title("Phân bố giá của 2 quý cuối năm (Quý 3 và Quý 4)")
plt.xlabel("Giá (VNĐ)")
plt.ylabel("Tần suất")
plt.grid(axis="y", linestyle="--", alpha=0.4)
plt.tight_layout()
plt.show()

# In thống kê mô tả để so sánh hai nhóm quý
thong_ke_cau_4 = pd.DataFrame({
    "2 quý đầu năm": gia_2_quy_dau.describe(),
    "2 quý cuối năm": gia_2_quy_cuoi.describe()
})

in_bang("SO SÁNH PHÂN BỐ GIÁ CỦA HAI QUÝ ĐẦU NĂM VÀ HAI QUÝ CUỐI NĂM",
        thong_ke_cau_4.round(2))



# ============================================================
# XỬ LÝ CÂU 5
# ============================================================

# Tính giá cao nhất và thấp nhất của từng ngày
gia_moi_ngay = pd.DataFrame({
    "Ngày": dates,
    "Giá thấp nhất": P.min(axis=1),
    "Giá cao nhất": P.max(axis=1)
})

# Tính biên độ dao động giá từng ngày
gia_moi_ngay["Biên độ"] = (
    gia_moi_ngay["Giá cao nhất"] - gia_moi_ngay["Giá thấp nhất"]
)

# Tìm ngày có biên độ dao động lớn nhất
vi_tri_max = gia_moi_ngay["Biên độ"].idxmax()
ngay_max = gia_moi_ngay.loc[vi_tri_max, "Ngày"]
gia_thap_nhat = gia_moi_ngay.loc[vi_tri_max, "Giá thấp nhất"]
gia_cao_nhat = gia_moi_ngay.loc[vi_tri_max, "Giá cao nhất"]
bien_do_max = gia_moi_ngay.loc[vi_tri_max, "Biên độ"]

# In bảng các ngày có biên độ lớn nhất
bang_cau_5 = gia_moi_ngay.loc[
    gia_moi_ngay["Biên độ"] == bien_do_max
].copy()

bang_cau_5["Ngày"] = bang_cau_5["Ngày"].dt.strftime("%d/%m/%Y")

in_bang("NGÀY CÓ BIÊN ĐỘ DAO ĐỘNG GIÁ LỚN NHẤT",
        bang_cau_5.round(2).set_index("Ngày"))

# In kết quả
print("\n" + "=" * 65)
print("ĐÁNH GIÁ CÂU 5".center(65))
print("=" * 65)
print(f"Ngày xảy ra: {ngay_max.strftime('%d/%m/%Y')}")
print(f"Giá thấp nhất trong ngày: {gia_thap_nhat:.2f} VNĐ")
print(f"Giá cao nhất trong ngày: {gia_cao_nhat:.2f} VNĐ")
print(f"Biên độ dao động lớn nhất: {bien_do_max:.2f} VNĐ")
print("=" * 65)

# Vẽ biểu đồ đường giá trung bình theo ngày
gia_trung_binh_ngay = P.mean(axis=1)

plt.figure(figsize=(12, 5))
plt.plot(
    dates,
    gia_trung_binh_ngay,
    color="steelblue",
    linewidth=1
)
plt.title("Xu hướng biến động giá trong năm")
plt.xlabel("Ngày")
plt.ylabel("Giá trung bình (VNĐ)")
plt.grid(True, linestyle="--", alpha=0.4)
plt.tight_layout()
plt.show()

# KẾT LUẬN CÂU 5
print("\nNHẬN XÉT:")
print("Biểu đồ thể hiện xu hướng biến động giá trong cả năm.")
print("Biên độ dao động lớn nhất được xác định bằng giá cao nhất")
print("trừ giá thấp nhất trong cùng một ngày.")
print(f"Biên độ lớn nhất là {bien_do_max:.2f} VNĐ,")
print(f"xảy ra vào ngày {ngay_max.strftime('%d/%m/%Y')}.")



# ============================================================
# XỬ LÝ CÂU 6
# ============================================================
print("\n" + "=" * 60)
print("GIẢI THÍCH ĐƯỜNG MÀU XANH TRÊN BIỂU ĐỒ".center(60))
print("=" * 60)

print("Một đoạn thẳng có quỹ đạo đi xuống nhưng vẫn có thể được tô màu xanh.")
print("Theo đề, đường đi xuống cho biết giá ở thời điểm sau thấp hơn thời điểm trước.")
print("Tuy nhiên, màu xanh có thể được quy định dựa trên việc giá")
print("nằm trên mức giá tham chiếu, chứ không dựa vào chiều tăng giảm.")
print("Vì vậy, dù giá đang giảm, đoạn thẳng vẫn màu xanh nếu giá")
print("đáp ứng điều kiện tô màu xanh của biểu đồ.")
print("=" * 60)