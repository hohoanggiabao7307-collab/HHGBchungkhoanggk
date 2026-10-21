import streamlit as st

st.set_page_config(
    page_title="Mô phỏng giá chứng khoán",
    layout="wide"
)

st.title("Mô phỏng biến động giá chứng khoán")
st.write(
    "Ứng dụng phân tích dữ liệu bằng Python, "
    "Pandas, NumPy và Matplotlib."
)

st.success("Ứng dụng Streamlit đã khởi chạy thành công!")

import streamlit as st
from pathlib import Path

video_path = Path(__file__).parent / "bien_dong_gia.mp4"

st.subheader("Video mô phỏng biến động giá chứng khoán")

if video_path.exists():
    st.video(str(video_path))
else:
    st.error("Không tìm thấy file bien_dong_gia.mp4")
