# Engine lập lá số Tử Vi

Lập lá số Tử Vi từ ngày + giờ sinh dương lịch + giới tính, xuất ra
file text (`*_clean.txt`), HTML và PNG (khung 800px, có watermark trống đồng).

Luật an sao lấy từ sách Tử Vi (Tam Hợp Phái, Tân Biên) và đã đối chiếu
với lá mẫu; một vài điểm còn tranh cãi được đánh cờ trong code
(vd Chủ thân chi Hợi) chứ không giấu đi.

## Chạy nhanh

```bash
pip install -r requirements.txt
python3 -m playwright install chromium
python3 auto_chart.py 2000-06-15 12:00 nam "Vi Du" 2026 out
```

Kết quả trong thư mục `out`: `vi-du_clean.txt`, `la-so-vi-du.html`,
`la-so-vi-du.png`. Thiếu Playwright thì vẫn ra text + HTML, chỉ thiếu PNG.

Chạy nhiều lá bằng file CSV (header: `date,time,gender,name[,xem_year]`):

```bash
python3 auto_chart.py --csv vi-du.csv --xem 2026 --out out
```

Xem mẫu trong `vi-du.csv` — toàn dữ liệu giả, đừng dùng lá thật của
người khác khi chưa được đồng ý.

## File nào làm gì

- `lap-la-so.py` — khung chính tinh, đại vận, Tuần/Triệt.
- `phu_tinh.py` + `work_phu_tinh/` — lắp phụ tinh, Tứ Hóa, sao lưu.
- `lich_vn.py` — đổi dương lịch sang âm lịch Việt Nam
  (thuật toán Hồ Ngọc Đức, vendored, xem ghi chú trong file).
- `gen_clean_from_engine.py` — xuất file text dạng clean.
- `render_chart_html.py` — vẽ HTML lá số; `chart.css` là CSS của khung
  lá số (tách riêng, không kèm dữ liệu mẫu); `render_chart.py` là
  renderer PIL cũ mà HTML renderer vẫn dùng bảng phân loại cát/hung.
- `auto_chart.py` — chạy 1 lệnh từ ngày/giờ/giới ra cả 3 định dạng.

## Lưu ý

- Font Inter + Charm khi render HTML hiện load từ Google Fonts nên
  cần mạng lúc render; bản web nên đóng gói font local.
- Ngày sinh mặc định hiểu là dương lịch; năm xem mặc định là năm hiện tại.
- Đây là công cụ lập lá số, không phải công cụ luận giải.
