#!/usr/bin/env python3
"""Render một lá số từ file *_clean.txt thành HTML chuẩn aituvi_clone.

Dùng: python3 render_chart_html.py sample_charts_clean/hai_engine.txt out.html
  (tên file xuất chuẩn: la-so-<tên>.html/.png, theo user 2026-10-28; trước đó có hậu tố -lá mẫutuvi, đã bỏ)

RANH GIỚI ĐÃ CHỐT (user 2026-10-26):
aituvi_clone.html là DESIGN MOCKUP do user đề ra (Codex vẽ theo yêu
cầu), CHỈ để lấy vị trí + màu sắc, KHÔNG xét logic sao. Nội dung sao
trong mockup (lá mẫu mẫu) chỉ là dữ liệu minh họa, không phải chuẩn
để đối chiếu hay ghi đè engine.
- LẤY TỪ MOCKUP (vị trí + màu + công thức hiển thị): khung 800px,
  nền #FFFCF5, watermark assets/Trongdong.webp, font Inter + Charm,
  bảng màu khung, vị trí header/can-chi/tên cung/đại vận + T.,
  chính tinh 14.5px, VCD để trống, footer ĐV./Tràng Sinh/TH./LN.,
  Thiên Bàn 3 cột, legend-bar dưới đáy, CSS chống tràn .phu-col,
  công thức cân lượng + T.1-T.12 + TH. + LN.
  (nguyet_han_t1_t12_spec.md, can_luong_xuong_cot_spec.md).
- GIỮ CỦA ENGINE (logic an sao): vị trí sao, phân cột
  cát/hung theo LOAI_CAT/LOAI_HUNG của render_chart.py (Tướng Quân +
  Đẩu Quân = hung, Hoa Cái = cát), màu sao theo SAO_EL của engine
  (Thiên Đức = Thổ, Hồng Loan = Thủy), KHÔNG thêm Văn Tinh natal,
  KHÔNG hiển thị sao ĐV. (data vẫn còn trong file clean).
  THỨ TỰ SAO TRONG CỘT (user 2026-10-26, thay thứ tự file gốc):
  xếp theo hạng mạnh -> nhẹ trong từng cột (bảng hoàn chỉnh: cát
  47 sao, hung 36 sao), xem CAT_RANK/HUNG_RANK; 9 sao Lưu (L.)
  xếp cuối cột, sau mọi sao natal (mỗi nhóm vẫn theo hạng).
  Sao không có trong bảng (nếu còn) xếp cuối nhóm của nó.

CHỈNH SỬA SPEC ĐÃ PHÁT HIỆN KHI ĐỐI CHIẾU (ghi rõ, không lặng):
- LN. footer KHÔNG dùng spec §6.1 Lưu Thái Tuế (gốc = chi năm xem)
  nữa — user 2026-10-26 chỉ lại: LN. là Lưu Niên Đại Vận theo luật
  đã dạy 2026-10-23 (phu_tinh.ln_origin_for): năm thứ 1 của đại vận
  gốc = cung đại vận, năm thứ 2 = cung xung chiếu (+6), từ năm thứ 3
  gốc = V+6+(k-4)*D; tuổi xem < tuổi đại vận đầu của Mệnh (tiền vận)
  thì LN.MỆNH nằm ở cung Mệnh. Ví dụ kiểm chứng: lá mẫu 32 tuổi
  = năm 1 đại vận Hợi -> LN.MỆNH ở Hợi (không phải Ngọ như spec cũ);
  lá mẫu 5 tuổi < 6 (đại vận đầu Mệnh Thìn) -> LN.MỆNH ở Thìn.
  Spec §6.1 chỉ còn là tham khảo, không dùng cho footer LN. nữa.
- "Sao chính" để in đậm (spec/mockup không định nghĩa, chỉ cho flag
  bold từng sao trong build_clone.py): suy ra từ toàn bộ 12 cung mẫu
  Hải, khớp 100% không ngoại lệ — KHÔI/VIỆT, TẢ/HỮU, XƯƠNG/KHÚC,
  TỨ HÓA, KÌNH/ĐÀ, KHÔNG/KIẾP + THIÊN KHÔNG, HỎA/LINH. Cột trái đậm
  700 / thường 400, cột phải đậm 700 / thường 600 (đúng mockup).
- "Âm dương thuận lý": so Âm/Dương năm sinh với Âm/Dương cung
  Mệnh (Tân Biên: năm Dương + Mệnh Dương cung = thuận; lệch nhau
  = nghịch), khớp 9/9 mẫu TVN (8 batch + lá mẫu). Chỉ là dòng
  phụ trong Thiên Bàn.
- Badge Tuần/Triệt (user 2026-10-26, THAY vị trí mockup; ĐÍNH CHÍNH
  sau khi user bắt lỗi bản v2): Tuần/Triệt KHÔNG nằm trong 1 cung
  mà nằm GIỮA 2 cung của cặp, và LUÔN trên một đường biên NGANG
  của lưới. Cặp dọc -> giữa biên chung (mép dưới ô trên, giữa
  chiều rộng). Cặp ngang -> đầu biên chung phía Thiên Bàn, tức
  điểm giao với đường biên ngang của hàng đó (hàng trên -> góc
  dưới ô trái, hàng dưới -> góc trên ô trái), cùng hàng với badge
  cặp dọc. Vd lá mẫu: Triệt Ngọ–Mùi ở góc dưới ô Phu Thê,
  cùng hàng với Tuần Thân–Dậu ở cột Mệnh. Tuần = Triệt cùng cặp
  thì gộp 1 badge "Tuần – Triệt" (luật cũ của PIL renderer).
"""
import importlib.util
import os
import re
import sys
import unicodedata
from html import escape

HERE = __file__.rsplit("/", 1)[0]
REF_HTML = HERE + "/aituvi_ref/aituvi_clone.html"

# --- Reuse engine logic (không copy lại bảng) ---
spec_rc = importlib.util.spec_from_file_location("render_chart", HERE + "/render_chart.py")
rc = importlib.util.module_from_spec(spec_rc)
spec_rc.loader.exec_module(rc)

CAN = rc.CAN
CHI = rc.CHI
CAN_ABBR = rc.CAN_ABBR
CHI_EL = rc.CHI_EL
# Bảng màu Ngũ Hành chuẩn clone (thay bảng màu cũ của render_chart).
EL_COLOR_HEX = {"K": "#535862", "M": "#039855", "T": "#181D27",
                "H": "#EF4444", "O": "#F79009"}
# Thứ tự ô trong HTML clone (grid auto-placement sẽ đẩy Dậu/Tuất
# sang cột 4 nhờ #thien_ban chiếm 2x2 giữa — giữ nguyên thứ tự này).
CELL_ORDER = ["Tỵ", "Ngọ", "Mùi", "Thân", "Thìn", "Dậu",
              "Mão", "Tuất", "Dần", "Sửu", "Tý", "Hợi"]
GRID = rc.GRID
LABEL_SHORT = rc.LABEL_SHORT
# Tên cung ngắn cho footer LN (Phu Thê -> PHỐI, như clone).
LN_LIST = ["LN. MỆNH", "LN. PHỤ", "LN. PHÚC", "LN. ĐIỀN", "LN. QUAN",
           "LN. NÔ", "LN. DI", "LN. TẬT", "LN. TÀI", "LN. TỬ",
           "LN. PHỐI", "LN. HUYNH"]
# Sao chính in đậm (suy từ clone, xem docstring).
MAIN_STARS = {
    "thien khoi", "thien viet", "ta phu", "huu bat",
    "van xuong", "van khuc",
    "hoa loc", "hoa quyen", "hoa khoa", "hoa ky",
    "kinh duong", "da la", "dia khong", "dia kiep", "thien khong",
    "hoa tinh", "linh tinh",
}

# --- Cân lượng (can_luong_xuong_cot_spec.md, đơn vị chỉ) ---
WEIGHT_NAM = {
    "Giáp Tý": 12, "Ất Sửu": 9, "Bính Dần": 6, "Đinh Mão": 7,
    "Mậu Thìn": 12, "Kỷ Tỵ": 5, "Canh Ngọ": 9, "Tân Mùi": 8,
    "Nhâm Thân": 7, "Quý Dậu": 8, "Giáp Tuất": 15, "Ất Hợi": 9,
    "Bính Tý": 16, "Đinh Sửu": 8, "Mậu Dần": 8, "Kỷ Mão": 19,
    "Canh Thìn": 12, "Tân Tỵ": 6, "Nhâm Ngọ": 8, "Quý Mùi": 7,
    "Giáp Thân": 5, "Ất Dậu": 15, "Bính Tuất": 6, "Đinh Hợi": 16,
    "Mậu Tý": 15, "Kỷ Sửu": 7, "Canh Dần": 9, "Tân Mão": 12,
    "Nhâm Thìn": 10, "Quý Tỵ": 7, "Giáp Ngọ": 15, "Ất Mùi": 6,
    "Bính Thân": 5, "Đinh Dậu": 14, "Mậu Tuất": 14, "Kỷ Hợi": 9,
    "Canh Tý": 7, "Tân Sửu": 7, "Nhâm Dần": 9, "Quý Mão": 12,
    "Giáp Thìn": 8, "Ất Tỵ": 7, "Bính Ngọ": 13, "Đinh Mùi": 5,
    "Mậu Thân": 14, "Kỷ Dậu": 5, "Canh Tuất": 9, "Tân Hợi": 17,
    "Nhâm Tý": 5, "Quý Sửu": 7, "Giáp Dần": 12, "Ất Mão": 8,
    "Bính Thìn": 8, "Đinh Tỵ": 6, "Mậu Ngọ": 19, "Kỷ Mùi": 6,
    "Canh Thân": 8, "Tân Dậu": 16, "Nhâm Tuất": 10, "Quý Hợi": 7,
}
WEIGHT_THANG = {1: 6, 2: 7, 3: 18, 4: 9, 5: 5, 6: 16,
                7: 9, 8: 15, 9: 18, 10: 8, 11: 9, 12: 5}
WEIGHT_NGAY = {
    1: 5, 2: 10, 3: 8, 4: 15, 5: 16, 6: 15, 7: 8, 8: 16, 9: 8, 10: 16,
    11: 9, 12: 17, 13: 8, 14: 17, 15: 10, 16: 8, 17: 9, 18: 18, 19: 5,
    20: 15, 21: 10, 22: 9, 23: 8, 24: 9, 25: 15, 26: 18, 27: 7, 28: 8,
    29: 16, 30: 6,
}
WEIGHT_GIO = {"Tý": 16, "Sửu": 6, "Dần": 7, "Mão": 10, "Thìn": 9,
              "Tỵ": 16, "Ngọ": 10, "Mùi": 8, "Thân": 8, "Dậu": 9,
              "Tuất": 6, "Hợi": 6}


def tinh_can_luong(can_chi_nam, thang_am, ngay_am, gio_chi):
    tong = (WEIGHT_NAM[can_chi_nam] + WEIGHT_THANG[thang_am]
            + WEIGHT_NGAY[ngay_am] + WEIGHT_GIO[gio_chi])
    return (f"{tong // 10} lượng {tong % 10} chỉ" if tong % 10
            else f"{tong // 10} lượng chẵn")


# --- Nguyệt hạn / Tiểu hạn (nguyet_han spec) + Lưu Niên Đại Vận ---
KHOI_TIEU_HAN = {2: 4, 6: 4, 10: 4, 8: 10, 0: 10, 4: 10,
                 5: 7, 9: 7, 1: 7, 11: 1, 3: 1, 7: 1}


def tinh_thang_th(chi_sinh, chi_xem, is_nam, thang_am, gio_sinh):
    """Trả về (T{}, TH{}) theo chi (0=Tý..11=Hợi)."""
    khoi = KHOI_TIEU_HAN[chi_sinh]
    chieu = 1 if is_nam else -1
    tieu_xem = (khoi + chieu * (chi_xem - chi_sinh)) % 12
    t1 = (tieu_xem - (thang_am - 1) + (gio_sinh - 1)) % 12
    thang = {(t1 + m - 1) % 12: f"T.{m}" for m in range(1, 13)}
    th = {}
    for k in range(12):
        th[(khoi + chieu * k) % 12] = "TH. " + CHI[(chi_sinh + k) % 12]
    return thang, th


def tinh_ln(dai_van, menh_branch, tuoi_xem, direction):
    """LN. theo Lưu Niên Đại Vận (luật user dạy 2026-10-23, xem
    docstring): gốc LN.MỆNH theo năm thứ k trong đại vận hiện tại;
    tiền vận (tuổi < đại vận đầu của Mệnh) gốc = Mệnh.
    Trả về {chi_idx: 'LN. ...'}."""
    if tuoi_xem < dai_van[menh_branch]:
        goc = menh_branch
    else:
        dv_branch = None
        for br, start in dai_van.items():
            if start <= tuoi_xem < start + 10:
                dv_branch = br
                break
        if dv_branch is None:  # tuổi vượt khung: lấy đại vận muộn nhất
            dv_branch = max(dai_van.items(), key=lambda kv: kv[1])[0]
        k = tuoi_xem - dai_van[dv_branch] + 1
        from phu_tinh import ln_origin_for
        goc = ln_origin_for(dv_branch, direction, k)
    gi = CHI.index(goc)
    return {(gi + i) % 12: LN_LIST[i] for i in range(12)}


# 9 sao lưu cốt lõi (quyết Admin 2026-10-25, Tân Biên) — các L. khác
# (L. Hóa Khoa, L. Văn Khúc, L. Hồng Loan...) KHÔNG hiển thị.
CORE_LUU_BASE = {"Thái Tuế", "Tang Môn", "Bạch Hổ", "Thiên Khốc",
                 "Thiên Hư", "Thiên Mã", "Lộc Tồn", "Kình Dương",
                 "Đà La"}
# LN.Văn Tinh theo can năm sinh (Tân Biên §8.33) — thay Văn Tinh natal.
LN_VAN_TINH = {"Giáp": "Tỵ", "Ất": "Ngọ", "Bính": "Thân",
               "Đinh": "Dậu", "Mậu": "Thân", "Kỷ": "Dậu",
               "Canh": "Hợi", "Tân": "Tý", "Nhâm": "Dần",
               "Quý": "Mão"}


# Thứ tự phụ tinh trong cột (user 2026-10-26, bảng HOÀN CHỈNH:
# cát 47 sao, hung 36 sao, mạnh -> nhẹ; cát 1 mạnh nhất, hung 1
# hung nhất). Khóa dùng CHÍNH TẢ DATA (khác danh sách user ở 4
# chỗ: Tả Phù = Tả Phụ, Bác Sĩ = Bác Sỹ, Đẩu Quân = Đầu Quân,
# Thiên Hỷ đã thống nhất từ Hỉ/Hi). Tướng Quân ở cát 26 theo
# bảng mới nhất (đảo quyết hung 2026-10-25, xem LOAI_CAT).
# Luật sao Lưu (user 2026-10-26): 9 sao Lưu (L. core-9) xếp CUỐI
# cột, sau mọi sao natal — mỗi nhóm vẫn xếp theo hạng.
CAT_RANK = {n: i + 1 for i, n in enumerate([
    "Hóa Khoa", "Hóa Quyền", "Hóa Lộc", "Tả Phù", "Hữu Bật",
    "Thiên Khôi", "Thiên Việt", "Văn Xương", "Văn Khúc", "Lộc Tồn",
    "Thiên Mã", "Ân Quang", "Thiên Quý", "Tam Thai", "Bát Tọa",
    "Long Trì", "Phượng Các", "Thiên Quan", "Thiên Phúc", "Đào Hoa",
    "Hồng Loan", "Thiên Hỷ", "Giải Thần", "Thiên Giải", "Địa Giải",
    "Tướng Quân", "Quốc Ấn", "Phong Cáo", "Thai Phụ", "Văn Tinh",
    "Bác Sĩ", "Thiên Y", "Thanh Long", "Tấu Thư", "Hỷ Thần",
    "Lực Sĩ", "Hoa Cái", "Thiếu Dương", "Thiên Đức", "Nguyệt Đức",
    "Thiếu Âm", "Phúc Đức", "Long Đức", "Thiên Thọ", "Thiên Tài",
    "Thiên Trù", "Đường Phù"])}
HUNG_RANK = {n: i + 1 for i, n in enumerate([
    "Địa Không", "Địa Kiếp", "Hóa Kỵ", "Kình Dương", "Đà La",
    "Hỏa Tinh", "Linh Tinh", "Thiên Hình", "Đại Hao", "Tiểu Hao",
    "Thái Tuế", "Tang Môn", "Bạch Hổ", "Thiên Khốc", "Thiên Hư",
    "Kiếp Sát", "Thiên Diêu", "Cô Thần", "Quả Tú", "Phục Binh",
    "Phá Toái", "Lưu Hà", "Thiên Không", "Quan Phủ", "Quan Phù",
    "Điếu Khách", "Tuế Phá", "Tử Phù", "Trực Phù", "Bệnh Phù",
    "Phi Liêm", "Đẩu Quân", "Thiên Thương", "Thiên Sứ", "Thiên La",
    "Địa Võng"])}


def _is_luu(tok):
    """True nếu token là sao Lưu năm xem (tiền tố L.). LN.Văn Tinh
    KHÔNG tính là Lưu ở đây (nó là sao cố định theo can, xếp theo
    hạng natal như sao thường); "LN." không match "^L\\." vì ký tự
    thứ 2 là 'N' chứ không phải '.'."""
    return tok.strip().startswith("L.")


def _phu_rank(tok, rank):
    """Hạng của 1 token phụ tinh trong cột (bỏ grade, (grey),
    tiền tố L./LN., rồi qua disp để thống nhất tên hiển thị).
    Chỉ chuẩn hóa CHÍNH TẢ để tra hạng (Bác Sỹ/Lực Sỹ/Thiếu Hỉ
    là biến thể chép site cũ của Bác Sĩ/Lực Sĩ/Thiên Hỷ) — tên
    hiển thị trên lá vẫn giữ nguyên như file gốc."""
    t = tok
    t = t[:-6] if t.endswith("(grey)") else t
    t = re.sub(r"\s*\(.\)\s*$", "", t)
    t = re.sub(r"^(L\.|LN\.)\s*", "", t)
    t = disp(t).strip()
    t = (t.replace("Bác Sỹ", "Bác Sĩ").replace("Lực Sỹ", "Lực Sĩ")
          .replace("Thiếu Hỉ", "Thiên Hỷ").replace("Thiếu Hỷ", "Thiên Hỷ"))
    return rank.get(t, 999)


def disp(tok):
    """Tên hiển thị: Thiên Riêu -> Thiên Diêu (user 2026-10-26, đảo
    quyết 2026-10-24) + Thiên Hỉ/Thiên Hi -> Thiên Hỷ (1 sao, 2026-10-26)."""
    t = rc.disp_name(tok)
    return (t.replace("Thiên Hỉ", "Thiên Hỷ")
             .replace("Thiên Hi", "Thiên Hỷ"))


def star_color(tok):
    return EL_COLOR_HEX[rc.SAO_EL.get(rc.canon_name(tok), "T")]


def star_weight(tok, col):
    main = rc.canon_name(tok) in MAIN_STARS
    if col == "left":
        return "700" if main else "400"
    return "700" if main else "600"


def clean_tok(tok):
    grey = tok.endswith("(grey)")
    return (tok[:-6] if grey else tok), grey


def star_html(tok, col):
    t, grey = clean_tok(tok)
    color = "#A4A7AE" if grey else star_color(t)
    return (f'<div class="phu-tinh" style="color:{color};'
            f'font-weight:{star_weight(t, col)}">{escape(disp(t))}</div>')


def clone_css():
    """CSS verbatim từ aituvi_clone.html, chỉ đổi đường dẫn ảnh nền
    sang assets/ (file HTML này nằm ở root project, ảnh ở assets/),
    và tăng 1 size cho số đại vận + nhãn tháng theo yêu cầu user
    2026-10-26 (mockup gốc: đại vận 12px/18px, tháng 10.5px/14px
    top 15px — nay: đại vận 13px/19px, tháng 11.5px/15px top 16px,
    để số tháng vẫn nằm ngay dưới số đại vận)."""
    # Bản public: CSS tách riêng ra chart.css (chỉ lấy khối <style> của
    # mockup gốc, không kèm dữ liệu lá mẫu trong file mockup đó).
    css_path = os.path.join(HERE, "chart.css")
    if os.path.exists(css_path):
        css = open(css_path, encoding="utf-8").read()
    else:
        src = open(REF_HTML, encoding="utf-8").read()
        css = re.search(r"<style>(.*?)</style>", src, re.S).group(1)
    css = css.replace("url('Trongdong.webp')", "url('assets/Trongdong.webp')")
    # Dùng regex theo tên thuộc tính (không phụ thuộc indent) để khỏi
    # trượt như lần replace chuỗi trước.
    css = re.sub(r"(\.cung-daihan \{[^}]*?font-size: )12px;",
                 r"\g<1>13px;", css, count=1)
    css = re.sub(r"(\.cung-daihan \{[^}]*?line-height: )18px;",
                 r"\g<1>19px;", css, count=1)
    css = re.sub(r"(\.cung-thang \{[^}]*?top: )15px;",
                 r"\g<1>16px;", css, count=1)
    css = re.sub(r"(\.cung-thang \{[^}]*?font-size: )10\.5px;",
                 r"\g<1>11.5px;", css, count=1)
    css = re.sub(r"(\.cung-thang \{[^}]*?line-height: )14px;",
                 r"\g<1>15px;", css, count=1)
    return css


def clone_fonts_link():
    if os.path.exists(REF_HTML):
        src = open(REF_HTML, encoding="utf-8").read()
        m = re.search(r'(<link href="https://fonts\.googleapis\.com[^>]*>)', src)
        if m:
            return m.group(1)
    return ('<link href="https://fonts.googleapis.com/css2?'
            'family=Charm:wght@700&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">')


def main():
    src, out = sys.argv[1], sys.argv[2]
    header, palaces = rc.parse_clean(src)
    from phu_tinh import full_chart
    date, time_, gender = header["SINH"].split(" ")
    fc = full_chart(date, time_, gender)
    eng, inp = fc["engine"], fc["inp"]
    stems = rc.palace_stems(inp["year_stem"])
    dai_van = eng["dai_van"]
    than_branch = eng["than"]
    # TUAN/TRIET v4 kèm tên cung trong ngoặc — bỏ ngoặc trước khi
    # tách chi, để file cũ (không ngoặc) vẫn đọc đúng như trước.
    tuan = set(re.sub(r"\s*\([^)]*\)", "", header.get("TUAN", "")).split())
    triet = set(re.sub(r"\s*\([^)]*\)", "", header.get("TRIET", "")).split())

    spec_lap = importlib.util.spec_from_file_location("laplaso", HERE + "/lap-la-so.py")
    lap = importlib.util.module_from_spec(spec_lap)
    spec_lap.loader.exec_module(lap)
    yy, mm, dd = map(int, date.split("-"))
    _hh = int(time_.split(":")[0])
    _ys, _yb, lm, ld, day_gz = lap.birth_lunar(yy, mm, dd, _hh)
    day_stem = next(s for s in CAN if day_gz.startswith(s))
    day_gz = day_stem + " " + day_gz[len(day_stem):]
    hour = rc.hour_gz(day_stem, inp["hour_branch"])
    month = rc.month_gz(inp["year_stem"], inp["month"])
    nap, nap_el = rc.nap_am(inp["year_stem"], inp["year_branch"])
    cuc_el_code = {"Kim": "K", "Mộc": "M", "Thủy": "T", "Hỏa": "H",
                   "Thổ": "O"}[header["CUC"].split()[0]]
    rel = rc.cuc_relation(cuc_el_code, nap_el)
    amduong = "dương" if CAN.index(inp["year_stem"]) % 2 == 0 else "âm"
    amduong_txt = ("Âm " if amduong == "âm" else "Dương ") + (
        "Nam" if gender == "nam" else "Nữ")
    # 2026-10-26 (sửa theo Tân Biên + 9/9 mẫu TVN): thuận/nghịch so
    # Âm/Dương của NĂM SINH với Âm/Dương của CUNG MỆNH (chi Mệnh:
    # Tý/Dần/Thìn/Ngọ/Thân/Tuất dương, Sửu/Mão/Tỵ/Mùi/Dậu/Hợi âm),
    # KHÔNG phải can + giới như suy luận cũ (sai ở lá mẫu và
    # TEST01/02/05/06). Dòng "Âm Nam/Dương Nữ" ở trên giữ nguyên.
    menh_amduong = ("dương" if CHI.index(eng["menh"]) % 2 == 0
                    else "âm")
    thuan = (amduong == menh_amduong)
    amduong_line2 = "Âm dương thuận lý" if thuan else "Âm dương nghịch lý"
    # XEM dạng "Bính Ngọ 2026 45": năm xem + tuổi ở 2 token cuối.
    xem_toks = header["XEM"].split()
    xem_nam, xem_tuoi = xem_toks[-2], xem_toks[-1]
    xem_canchi = " ".join(xem_toks[:-2])
    xem_branch = xem_canchi.split()[-1]
    chi_sinh = CHI.index(inp["year_branch"])
    chi_xem = CHI.index(xem_branch)
    thang_lbl, th_lbl = tinh_thang_th(
        chi_sinh, chi_xem, gender == "nam", inp["month"],
        CHI.index(inp["hour_branch"]) + 1)
    ln_lbl = tinh_ln(dai_van, eng["menh"], int(xem_tuoi),
                     inp["direction"])
    can_luong = tinh_can_luong(
        f"{inp['year_stem']} {inp['year_branch']}",
        inp["month"], inp["day"], inp["hour_branch"])
    if header.get("CAN") and header["CAN"] != can_luong:
        print(f"WARN cân lượng header ({header['CAN']}) khác spec tính "
              f"({can_luong}) — dùng spec.", file=sys.stderr)

    # Badge Tuần/Triệt (user 2026-10-26): nằm giữa 2 cung của cặp,
    # chính giữa biên chung (xem docstring). Tuần = Triệt cùng cặp
    # thì gộp 1 badge "Tuần – Triệt" (luật cũ của PIL renderer).
    grid_pos = {}
    for rr in range(4):
        for cc in range(4):
            if GRID[rr][cc]:
                grid_pos[GRID[rr][cc]] = (rr, cc)

    def badge_for(branch):
        # 2026-10-26 (user chốt, thay vị trí mockup; ĐÍNH CHÍNH sau
        # khi user bắt lỗi bản v2): badge LUÔN nằm trên một đường
        # biên NGANG của lưới (không lơ lửng giữa chiều cao ô).
        # - Cặp dọc (cùng cột): badge giữa biên chung, tức mép dưới
        #   ô trên, giữa chiều rộng (Tuần Thân–Dậu của Diệu đã đúng
        #   kiểu này, giữ nguyên).
        # - Cặp ngang (cùng hàng): badge ở ĐẦU biên chung phía gần
        #   Thiên Bàn, tức điểm giao của biên dọc chung với đường
        #   biên ngang của hàng đó — cùng hàng với badge cặp dọc
        #   (vd Triệt Ngọ–Mùi của Diệu: góc dưới ô Phu Thê, trên
        #   đường biên hàng 1/2, cùng hàng với Tuần ở cột Mệnh).
        #   Hàng trên -> góc dưới ô trái; hàng dưới -> góc trên ô
        #   trái. Chỉ ô neo (trái/trên) mang badge.
        # Cặp không kề nhau (không xảy ra với cặp Tuần/Triệt chuẩn)
        # thì fallback mép dưới ô đầu CELL_ORDER.
        pairs = ([(tuan, "Tuần – Triệt")] if tuan == triet and len(tuan) == 2
                 else [(tuan, "Tuần"), (triet, "Triệt")])
        for pair, label in pairs:
            if len(pair) == 2 and branch in pair:
                b1, b2 = sorted(pair, key=lambda b: grid_pos[b])
                (r1, c1), (r2, c2) = grid_pos[b1], grid_pos[b2]
                if r1 == r2 and abs(c1 - c2) == 1:
                    if branch != b1:
                        return None
                    if r1 == 0:
                        return (label, "left: 100%; top: 100%; "
                                       "transform: translate(-50%, -50%);")
                    if r1 == 3:
                        return (label, "left: 100%; top: 0%; "
                                       "transform: translate(-50%, -50%);")
                    return (label, "left: 100%; top: 50%; "
                                   "transform: translate(-50%, -50%);")
                if c1 == c2 and abs(r1 - r2) == 1:
                    if branch != b1:
                        return None
                    return (label, "top: 100%; left: 50%; "
                                   "transform: translate(-50%, -50%);")
                rep = next(b for b in CELL_ORDER if b in pair)
                if branch != rep:
                    return None
                return (label, "bottom: -10px; left: 50%; "
                               "transform: translateX(-50%);")
        return None

    # --- Đồng bộ engine (user 2026-10-26, áp cho MỌI lá, không riêng lá nào):
    # (a) Bỏ Văn Tinh natal, thay bằng LN.Văn Tinh theo can năm sinh.
    for _p in palaces.values():
        _p["natal"] = [t for t in _p["natal"] if t.strip() != "Văn Tinh"]
    _vt_br = LN_VAN_TINH[inp["year_stem"]]
    if "LN.Văn Tinh" not in palaces[_vt_br]["natal"]:
        palaces[_vt_br]["natal"].append("LN.Văn Tinh")

    def fill_hoa_grade(tok, branch):
        """Tứ Hóa thiếu grade -> lấy grade của sao chủ nó hóa
        (host-grade, Admin chốt 2026-10-25); đã có grade thì giữ nguyên."""
        m = re.match(r"^(L\.\s*)?(Hóa Lộc|Hóa Quyền|Hóa Khoa|Hóa Kỵ)"
                     r"(\s*\((.)\))?$", tok.strip())
        if not m or m.group(4):
            return tok
        host = eng["tu_hoa"].get(m.group(2))
        if not host:
            return tok
        for h in (host, host.replace("Tả Phụ", "Tả Phù"),
                  host.replace("Tả Phù", "Tả Phụ")):
            g = fc["grades"].get((h, branch))
            if g:
                return f"{m.group(1) or ''}{m.group(2)} ({g})"
        return tok

    cells = []
    for branch in CELL_ORDER:
        p = palaces[branch]
        stem_br = stems[branch].split()
        abbr = f"{CAN_ABBR[stem_br[0]]}.{branch}"
        canchi_color = EL_COLOR_HEX[CHI_EL[branch]]
        chu = p["cung"].upper()
        # Phu Thê hiển thị PHU THÊ (không phải PHỐI) như clone.
        is_menh = p["cung"] == "Mệnh"
        cell_cls = "cung-cell is-menh-cell" if is_menh else "cung-cell"
        chu_cls = "cung-chu is-menh-chu" if is_menh else "cung-chu"
        than_html = '<span class="than-badge">Thân</span>' if branch == than_branch else ""
        b_idx = CHI.index(branch)
        ct = [t for t in p["chinh"] if t.strip() != "— VCD —"]
        ct_html = "".join(
            f'<p class="chinh-tinh" style="color:{star_color(t)};'
            f'font-weight:700">{escape(disp(t))}</p>' for t in ct)
        left, right = [], []
        # Chỉ natal + L. core-9, bỏ hẳn ĐV. (theo chi tiết UI mới) và
        # các L. ngoài core-9 (quyết Admin 2026-10-25).
        luu_core = []
        for tok in p["luu"]:
            base = tok[2:].strip() if tok.startswith("L.") else tok.strip()
            base = re.sub(r"\s*\([^)]*\)\s*$", "", base)
            if base in CORE_LUU_BASE:
                luu_core.append(tok)
        for tok in p["natal"] + luu_core:
            tok = fill_hoa_grade(tok, branch)
            (right if rc.classify(tok) == "hung" else left).append(tok)
        # 2026-10-26 (user chốt): mỗi cột xếp theo hạng mạnh -> nhẹ,
        # sao Lưu (L.) xếp cuối cột; sort ổn định nên sao không có
        # hạng giữ nguyên thứ tự gốc trong nhóm của nó.
        left.sort(key=lambda t: (_is_luu(t), _phu_rank(t, CAT_RANK)))
        right.sort(key=lambda t: (_is_luu(t), _phu_rank(t, HUNG_RANK)))
        left_html = "".join(star_html(t, "left") for t in left)
        right_html = "".join(star_html(t, "right") for t in right)
        dv_short = LABEL_SHORT.get(p["dvnhan"], "—")
        dv_lbl = f"ĐV. {dv_short}"
        dv_cls = "tieu-han is-active-dv" if dv_lbl == "ĐV. MỆNH" else "tieu-han"
        # Cung ĐV. MỆNH: số đại vận highlight cùng màu #B45309 như nhãn ĐV.
        daihan_style = (' style="color:#B45309;font-weight:700"'
                        if dv_lbl == "ĐV. MỆNH" else "")
        ln = ln_lbl[b_idx]
        ln_cls = "nguyet-han is-active-ln" if ln == "LN. MỆNH" else "nguyet-han"
        th = th_lbl[b_idx]
        th_cls = ("tieu-han-chi is-active-th"
                  if th == f"TH. {xem_branch}" else "tieu-han-chi")
        badge = badge_for(branch)
        badge_html = (f'<div class="tuan-triet-badge" style="{badge[1]}">'
                      f'{badge[0]}</div>' if badge else "")
        cells.append(f"""
    <div class="{cell_cls}">
      <div class="horoscope-inner">
        <div class="cung-header">
          <div class="cung-canchi" style="color:{canchi_color}">{abbr}</div>
          <div class="cung-chu-wrap"><span class="{chu_cls}">{chu}</span>{than_html}</div>
          <div class="cung-daihan">
            <span{daihan_style}>{dai_van[branch]}</span>
            <span class="cung-thang">{thang_lbl[b_idx]}</span>
          </div>
        </div>
        <div class="chinh-tinh-box">{ct_html}</div>
        <div class="phu-tinh-cols">
          <div class="phu-col">{left_html}</div>
          <div class="phu-col">{right_html}</div>
        </div>
        <div class="cung-footer">
          <div class="{dv_cls}">{dv_lbl}</div>
          <div class="trang-sinh">{escape(p["vong"])}</div>
          <div class="{ln_cls}">
            <span class="{th_cls}">{th}</span>
            <span>{ln}</span>
          </div>
        </div>
      </div>
      {badge_html}
    </div>""")
    cells_html = "\n".join(cells)

    # SVG Tam Hợp / Xung Chiếu: 4 điểm = tâm ô Mệnh/Tài/Quan/Di
    # clamp vào hộp Thiên Bàn, quy về viewBox 400x500 — với lá mẫu
    # ra đúng 4 điểm của clone (400,375 / 100,0 / 0,500 / 0,125).
    def svg_point(branch):
        rr, cc = grid_pos[branch]
        # Tọa độ tương đối theo đơn vị ô (CW=1, CH=1); hộp trung tâm
        # là x 1..3, y 1..3.
        cx = min(max(cc + 0.5, 1), 3)
        cy = min(max(rr + 0.5, 1), 3)
        return ((cx - 1) / 2 * 400, (cy - 1) / 2 * 500)
    by_cung = {p["cung"]: b for b, p in palaces.items()}
    m_b, t_b, q_b, d_b = (by_cung[k] for k in
                          ("Mệnh", "Tài Bạch", "Quan Lộc", "Thiên Di"))
    mp, tp, qp, dp = (svg_point(b) for b in (m_b, t_b, q_b, d_b))

    def pt(p):
        return f"{p[0]:g} {p[1]:g}"
    hh, mi = time_.split(":")
    tb_rows = f"""
        <div class="tb-row"><p class="tb-label">Họ tên</p><p class="tb-val tb-span-2">{escape(header.get("NGUOI", "Nam"))}</p></div>
        <div class="tb-row"><p class="tb-label">Năm</p><p class="tb-val">{yy}</p><p class="tb-val">{inp["year_stem"]} {inp["year_branch"]}</p></div>
        <div class="tb-row"><p class="tb-label">Tháng</p><div class="tb-val tb-flex-between"><span>{int(mm)}</span><span>({lm})</span></div><p class="tb-val">{month}</p></div>
        <div class="tb-row"><p class="tb-label">Ngày</p><div class="tb-val tb-flex-between"><span>{int(dd)}</span><span>({ld})</span></div><p class="tb-val">{day_gz}</p></div>
        <div class="tb-row"><p class="tb-label">Giờ</p><p class="tb-val">{int(hh)} giờ {mi} phút</p><p class="tb-val">{hour}</p></div>
        <div class="tb-row"><p class="tb-label">Năm xem</p><p class="tb-val">{xem_nam}</p><div class="tb-val tb-flex-col"><span>{xem_canchi}</span><span>{xem_tuoi} tuổi</span></div></div>
        <div class="tb-row"><p class="tb-label">Âm Dương</p><div class="tb-val tb-span-2 tb-flex-col"><span>{amduong_txt}</span><span>{amduong_line2}</span></div></div>
        <div class="tb-row"><p class="tb-label">Bản mệnh</p><p class="tb-val tb-span-2">{nap}</p></div>
        <div class="tb-row"><p class="tb-label">Cục</p><div class="tb-val tb-span-2 tb-flex-col"><span>{header["CUC"]}</span><span>{rel}</span></div></div>
        <div class="tb-row"><p class="tb-label">Cân lượng</p><p class="tb-val">{can_luong}</p></div>
        <div class="tb-row"><p class="tb-label">Chủ mệnh</p><p class="tb-val">{header["CHU_MENH"]}</p></div>
        <div class="tb-row"><p class="tb-label">Chủ thân</p><p class="tb-val">{header["CHU_THAN"]}</p></div>
        <div class="tb-row"><p class="tb-label">Lai nhân cung</p><p class="tb-val">{header["LAI_NHAN"]}</p></div>"""
    html = f"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<title>Lá Số Tử Vi - {escape(header.get("NGUOI", ""))}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{clone_fonts_link()}
<style>{clone_css()}</style>
</head>
<body>
<div id="horoscope-comp">
  <div class="grid-4x4">
{cells_html}
    <div id="thien_ban">
      <h1 class="tb-main-title">Lá Số Tử Vi</h1>
      <div class="tb-group">
{tb_rows}
      </div>
      <svg viewBox="0 0 400 500" preserveAspectRatio="none" style="position:absolute;inset:0;width:100%;height:100%;pointer-events:none">
        <line x1="{mp[0]:g}" y1="{mp[1]:g}" x2="{dp[0]:g}" y2="{dp[1]:g}" stroke="#DC2626" stroke-dasharray="4 3" style="stroke-width:1.1;opacity:0.42"/>
        <line x1="{mp[0]:g}" y1="{mp[1]:g}" x2="{tp[0]:g}" y2="{tp[1]:g}" stroke="#374151" style="stroke-width:1;opacity:0.25"/>
        <line x1="{mp[0]:g}" y1="{mp[1]:g}" x2="{qp[0]:g}" y2="{qp[1]:g}" stroke="#374151" style="stroke-width:1;opacity:0.25"/>
        <line x1="{tp[0]:g}" y1="{tp[1]:g}" x2="{qp[0]:g}" y2="{qp[1]:g}" stroke="#374151" style="stroke-width:1;opacity:0.25"/>
        <circle cx="{mp[0]:g}" cy="{mp[1]:g}" r="3" fill="#B45309" style="opacity:0.75"/>
        <circle cx="{dp[0]:g}" cy="{dp[1]:g}" r="2.5" fill="#DC2626" style="opacity:0.65"/>
        <circle cx="{tp[0]:g}" cy="{tp[1]:g}" r="2.5" fill="#374151" style="opacity:0.5"/>
        <circle cx="{qp[0]:g}" cy="{qp[1]:g}" r="2.5" fill="#374151" style="opacity:0.5"/>
      </svg>
    </div>
  </div>
  <div class="legend-bar">
    <div class="legend-left">
      <p>M: Miếu</p><p>V: Vượng</p><p>Đ: Đắc</p><p>B: Bình hòa</p><p>H: Hãm</p>
    </div>
    <div class="legend-right">
      <div class="swatch-item"><span class="swatch" style="background:#A4A7AE"></span><span>Kim</span></div>
      <div class="swatch-item"><span class="swatch" style="background:#12B76A"></span><span>Mộc</span></div>
      <div class="swatch-item"><span class="swatch" style="background:#181D27"></span><span>Thủy</span></div>
      <div class="swatch-item"><span class="swatch" style="background:#F04438"></span><span>Hỏa</span></div>
      <div class="swatch-item"><span class="swatch" style="background:#F79009"></span><span>Thổ</span></div>
    </div>
  </div>
</div>
</body>
</html>
"""
    open(out, "w", encoding="utf-8").write(html)
    print(f"saved {out}")


if __name__ == "__main__":
    main()
