#!/usr/bin/env python3
"""Render một lá số từ file *_clean.txt thành ảnh lưới 4x4 (v4).
Dùng: python3 render_chart.py sample_charts_clean/tao_clean.txt out.png
Học theo mẫu tuviluangiai.vn (lá #444056 của user):
- Header mỗi ô: can-chi viết tắt TRÁI, tên cung GIỮA (màu theo ngũ hành
  của chi), năm đại hạn PHẢI.
- Dòng 2: nhãn ngũ hành của chi (+/- theo âm/dương chi, chữ đen) + chính
  tinh in đậm màu theo ngũ hành của sao.
- 2 cột: trái = cát (●), phải = hung (▲); màu chữ = ngũ hành của sao
  (Kim xám, Mộc xanh lá, Thủy đen, Hỏa đỏ, Thổ cam); sao L./ĐV. xếp
  chung vào 2 cột theo cát/hung (thứ tự: natal -> L. -> ĐV.).
- Dải cuối ô GHIM đáy ô: "ĐV. X" trái, tên vòng giữa, "LN. X" phải.
- Ô giữa: bảng key-value (nhãn đen, giá trị xanh dương) như mẫu.
Bảng ngũ hành sao: lasotuvi-repo/Sao.py (saoNguHanh) + 6 chỗ mẫu khác
repo (đã zoom 3x xác nhận): Thiên Phúc/Thiên Đức -> Thổ, Thiên La -> Kim,
Tam Thai -> Thủy, Bát Tọa -> Mộc, Thiên Không -> Hỏa.
KHÔNG copy: chỉ số "Th.N" của mẫu (quy tắc chưa rõ, Ngọ=1...Tỵ=12);
dấu +/- trước tên chính tinh (4 ca khớp Nam/Bắc đẩu nhưng Tử Vi là
"Đế tinh" không khớp pattern nên bỏ, tránh ghi sai).
"""
import importlib.util
import re
import sys
import unicodedata

from PIL import Image, ImageDraw, ImageFont

# Font Noto Sans (kiểu AItuvi: sans hiện đại, dấu tiếng Việt gọn hơn DejaVu).
NOTO_DIR = "/usr/share/fonts/truetype/noto/"
F_REG = NOTO_DIR + "NotoSans-Regular.ttf"
F_BOLD = NOTO_DIR + "NotoSans-Bold.ttf"
F_TITLE = NOTO_DIR + "NotoSans-Bold.ttf"  # tiêu đề sans đậm (kiểu AItuvi)

GRID = [
    ["Tỵ", "Ngọ", "Mùi", "Thân"],
    ["Thìn", None, None, "Dậu"],
    ["Mão", None, None, "Tuất"],
    ["Dần", "Sửu", "Tý", "Hợi"],
]

LABEL_FULL = {
    "MỆNH": "Mệnh", "HUYNH": "Huynh Đệ", "PHU": "Phu Thê",
    "TỬ": "Tử Nữ", "TÀI": "Tài Bạch", "TẬT": "Tật Ách",
    "DI": "Thiên Di", "NÔ": "Nô Bộc", "QUAN": "Quan Lộc",
    "ĐIỀN": "Điền Trạch", "PHÚC": "Phúc Đức", "PHỤ": "Phụ Mẫu",
    "PHỐI": "Phu Thê",
}
# Tên rút gọn cho dải cuối ô (theo mẫu, kể cả PHỐI cho Phu Thê).
LABEL_SHORT = {
    "Mệnh": "MỆNH", "Huynh Đệ": "HUYNH", "Phu Thê": "PHỐI",
    "Tử Nữ": "TỬ", "Tài Bạch": "TÀI", "Tật Ách": "TẬT",
    "Thiên Di": "DI", "Nô Bộc": "NÔ", "Quan Lộc": "QUAN",
    "Điền Trạch": "ĐIỀN", "Phúc Đức": "PHÚC", "Phụ Mẫu": "PHỤ",
}
CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
CAN_ABBR = {"Giáp": "G", "Ất": "Ấ", "Bính": "B", "Đinh": "Đ", "Mậu": "M",
            "Kỷ": "K", "Canh": "C", "Tân": "T", "Nhâm": "N", "Quý": "Q"}
CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
       "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
CHI_EL = {"Tý": "T", "Sửu": "O", "Dần": "M", "Mão": "M", "Thìn": "O",
          "Tỵ": "H", "Ngọ": "H", "Mùi": "O", "Thân": "K", "Dậu": "K",
          "Tuất": "O", "Hợi": "T"}
CHI_YANG = {"Tý": 1, "Sửu": -1, "Dần": 1, "Mão": -1, "Thìn": 1, "Tỵ": -1,
            "Ngọ": 1, "Mùi": -1, "Thân": 1, "Dậu": -1, "Tuất": 1, "Hợi": -1}
# Màu ngũ hành theo legend mẫu: Kim xám, Mộc xanh lá, Thủy đen, Hỏa đỏ,
# Thổ cam.
EL_COLOR = {"K": (88, 88, 88), "M": (27, 122, 61), "T": (35, 32, 26),
            "H": (200, 0, 0), "O": (194, 87, 11)}
EL_NAME = {"K": "Kim", "M": "Mộc", "T": "Thủy", "H": "Hỏa", "O": "Thổ"}

SAO_EL = {
    "an quang": "M",
    "bac sy": "T",
    "bach ho": "K",
    "bat toa": "M",
    "benh": "H",
    "benh phu": "O",
    "co than": "O",
    "cu mon": "T",
    "da la": "K",
    "dai hao": "H",
    "dao hoa": "M",
    "dau quan": "H",
    "de vuong": "K",
    "dia giai": "O",
    "dia khong": "H",
    "dia kiep": "H",
    "dia vong": "O",
    "dieu khach": "H",
    "duong": "M",
    "duong phu": "M",
    "giai than": "M",
    "hoa cai": "K",
    "hoa khoa": "T",
    "hoa ky": "T",
    "hoa loc": "M",
    "hoa quyen": "T",
    "hoa tinh": "H",
    "hong loan": "T",
    "huu bat": "O",
    "hy than": "H",
    "kiep sat": "H",
    "kinh duong": "K",
    "lam quan": "K",
    "liem trinh": "H",
    "linh tinh": "H",
    "loc ton": "O",
    "long duc": "T",
    "long tri": "T",
    "luc si": "H",
    "luu ha": "T",
    "mo": "O",
    "moc duc": "T",
    "nguyet duc": "H",
    "pha quan": "T",
    "pha toai": "H",
    "phi liem": "H",
    "phong cao": "O",
    "phuc binh": "H",
    "phuc duc": "O",
    "phuong cac": "O",
    "qua tu": "O",
    "quan doi": "K",
    "quan phu": "H",
    "quoc an": "O",
    "suy": "T",
    "ta phu": "O",
    "tam thai": "T",
    "tang mon": "M",
    "tau thu": "K",
    "thai": "O",
    "thai am": "T",
    "thai duong": "H",
    "thai phu": "K",
    "thai tue": "H",
    "tham lang": "T",
    "thanh long": "T",
    "that sat": "K",
    "thien co": "M",
    "thien dong": "T",
    "thien duc": "O",
    "thien giai": "H",
    "thien hinh": "H",
    "thien hu": "T",
    "thien hy": "T",
    "thien khoc": "T",
    "thien khoi": "H",
    "thien khong": "H",
    "thien la": "K",
    "thien luong": "M",
    "thien ma": "H",
    "thien phu": "O",
    "thien phuc": "O",
    "thien quan": "H",
    "thien quy": "O",
    "thien rieu": "T",
    "thien su": "T",
    "thien tai": "O",
    "thien tho": "O",
    "thien thuong": "O",
    "thien tru": "O",
    "thien tuong": "T",
    "thien viet": "H",
    "thien y": "T",
    "thieu am": "T",
    "thieu duong": "H",
    "tieu hao": "H",
    "trang sinh": "T",
    "truc phu": "K",
    "tu": "H",
    "tu phu": "K",
    "tu vi": "O",
    "tue pha": "H",
    "tuong quan": "M",
    "tuyet": "O",
    "van khuc": "T",
    "van tinh": "H",
    "van xuong": "K",
    "vu khuc": "K"
}

# saoLoai từ lasotuvi/Sao.py: tốt < 10, xấu > 10 (dùng chia 2 cột cát/hung).
LOAI_CAT = {
"an quang", "bac sy", "thanh long", "tau thu", "long tri", "phuong cac",
"thien quy", "hoa loc", "thien ma", "quan doi", "duong phu",
"phong cao", "hoa quyen", "thieu duong", "thieu am", "long duc", "phuc duc",
"trang sinh", "de vuong", "thien duc", "nguyet duc", "thien y", "thien hy",
"thien giai", "dia giai", "giai than", "thien tho", "thien quan", "thien phuc",
"thien tru", "hoa khoa", "van xuong", "van khuc", "thien khoi",
"thien viet", "quoc an", "thai phu", "van tinh", "lam quan", "tam thai",
"bat toa", "dao hoa", "hong loan", "luc si", "ta phu",
"huu bat", "thien tai", "duong", "hy than", "loc ton",
# 2026-10-25 (user phán, lá Thoa): Hoa Cái là phụ cát tinh,
# trước đây xếp nhầm cột hung.
"hoa cai",
# 2026-10-26 (user đưa bảng cát hoàn chỉnh 47 sao): Tướng Quân ở
# cát hạng 26 — ĐẢO quyết 2026-10-25 (khi đó phán Tướng Quân +
# Đẩu Quân là hung). Đẩu Quân vẫn giữ ở hung; chỉ Tướng Quân
# chuyển sang cát theo list mới nhất. Nếu user chỉ định xếp hạng
# mà vẫn giữ Tướng Quân hung thì chuyển lại 1 dòng.
"tuong quan",
}
LOAI_HUNG = {
"thai tue", "thien hinh", "tang mon", "quan phu", "tu phu", "tue pha",
"bach ho", "dieu khach", "tieu hao", "benh phu", "dai hao", "phuc binh",
"suy", "benh", "tu", "tuyet", "thien khoc", "thien hu", "thien thuong",
"phi liem",  # mẫu đặt cột hung (repo loai 2 = chung, không phải cát)
"thien su", "thien la", "dia vong", "pha toai", "luu ha", "co than",
"qua tu", "thien rieu", "hoa ky", "moc duc", "thai", "da la",
"kinh duong", "dia khong", "dia kiep", "linh tinh", "hoa tinh", "kiep sat",
"thien khong", "truc phu",
# 2026-10-25 (user phán, lá lá mẫu): Đẩu Quân là hung (Tướng Quân
# đã chuyển sang cát theo bảng 2026-10-26, xem LOAI_CAT).
"dau quan",
}
ALIAS = {"thien dieu": "thien rieu", "thieu hi": "thien hy",
         "thieu hy": "thien hy", "luc sy": "luc si", "thien hi": "thien hy",
         "bac si": "bac sy"}
DV_ABBR = {"h loc": "hoa loc", "h quyen": "hoa quyen", "h khoa": "hoa khoa",
           "h ky": "hoa ky", "k duong": "kinh duong", "t khoi": "thien khoi",
           "t viet": "thien viet", "t ma": "thien ma", "khuc": "van khuc",
           "xuong": "van xuong"}


def canon_name(tok):
    """Chuẩn hóa token sao -> tên tra bảng (bỏ grade, (grey), tiền tố).
    Thứ tự: bỏ (grey) TRƯỚC rồi mới bỏ grade — token kiểu
    "Đà La (H)(grey)" ở file chép cũ mà bỏ grade trước thì grade
    nằm giữa, không khớp cuối chuỗi nên sót lại "(H)", tra bảng
    thành unknown, rơi nhầm sang cột cát."""
    s = tok
    s = s[:-6] if s.endswith("(grey)") else s
    s = re.sub(r"\s*\(.\)\s*$", "", s)
    s = re.sub(r"^(L\.|ĐV\.|LN\.)\s*", "", s)  # 2026-10-25: thêm LN. (LN.Văn Tinh)
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    s = s.lower().strip().replace("đ", "d")
    s = DV_ABBR.get(s, s)
    return ALIAS.get(s, s)


def classify(tok):
    n = canon_name(tok)
    if n in LOAI_CAT:
        return "cat"
    if n in LOAI_HUNG:
        return "hung"
    return "unknown"


def element_color(tok):
    return EL_COLOR[SAO_EL.get(canon_name(tok), "T")]


def parse_clean(path):
    header = {}
    palaces = {}
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        m = re.match(r"^([A-Z_]+): (.*)$", line)
        if m and not line.startswith("#"):
            header[m.group(1)] = m.group(2)
            continue
        m = re.match(r"^(\d+)\. (\S+) \((\d+)\) (\S+) (\S+) \(Tháng (\d+)\): (.*)$", line)
        if m and m.group(2) in LABEL_FULL:
            ver = 4
            ordinal, cung, branch, rest = int(m.group(1)), m.group(2), m.group(5), m.group(7)
            van_start, thang, can_cung = int(m.group(3)), int(m.group(6)), m.group(4)
        else:
            m = re.match(r"^(\d+)\. (\S+) \((\d+)\) (\S+) \(Tháng (\d+)\): (.*)$", line)
            if m and m.group(2) in LABEL_FULL:
                ver = 3
                ordinal, cung, branch, rest = int(m.group(1)), m.group(2), m.group(4), m.group(6)
                van_start, thang, can_cung = int(m.group(3)), int(m.group(5)), ""
            else:
                m = re.match(r"^(\S+) \((\d+)\) (\S+) \(Tháng (\d+)\): (.*)$", line)
                if m and m.group(1) in LABEL_FULL:
                    ver = 2
                    cung, branch, rest = m.group(1), m.group(3), m.group(5)
                    ordinal, van_start, thang, can_cung = None, None, int(m.group(4)), ""
                else:
                    m = re.match(r"^(\S+) (\S+): (.*)$", line)
                    if not m or m.group(1) not in LABEL_FULL:
                        continue
                    ver = 1
                    cung, branch, rest = m.group(1), m.group(2), m.group(3)
                    ordinal, van_start, thang, can_cung = None, None, None, ""
        parts = [p.strip() for p in rest.split("|")]
        while len(parts) < 10:
            parts.append("")
        if ver in (3, 4):
            chinh, natal, luu, vong, dvnhan, lnnhan = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
            dat, tam, xung, nhi = parts[6], parts[7], parts[8], parts[9]
            dv = []
        else:
            chinh, natal, luu, dv, vong, dvnhan, lnnhan = parts[:7]
            dat, tam, xung, nhi = "", "", "", ""
            dv = [t.strip() for t in dv.split(",") if t.strip()]
        if chinh.strip() == "(Vô chính diệu)":
            chinh = "— VCD —"
        dvnhan = dvnhan.strip().removeprefix("ĐV.")
        lnnhan = lnnhan.strip().removeprefix("LN.")
        palaces[branch] = {
            "cung": LABEL_FULL[cung],
            "chinh": [t.strip() for t in chinh.split(",") if t.strip()],
            "natal": [t.strip() for t in re.split(r"[,;]", natal)
                       if t.strip() and t.strip() not in ("—", "(không có)")],
            "luu": [t.strip() for t in luu.split(",")
                    if t.strip() and t.strip() != "(không có)"],
            "dv": dv,
            "vong": vong.strip(),
            "dvnhan": LABEL_FULL.get(dvnhan, dvnhan),
            "lnnhan": LABEL_FULL.get(lnnhan, lnnhan),
            "ordinal": ordinal,
            "van_start": van_start,
            "thang": thang,
            "can_cung": can_cung,
            "dat": dat,
            "tam": tam,
            "xung": xung,
            "nhi": nhi,
        }
    return header, palaces


def palace_stems(year_stem):
    start = {"Giáp": "Bính", "Kỷ": "Bính", "Ất": "Mậu", "Canh": "Mậu",
             "Bính": "Canh", "Tân": "Canh", "Đinh": "Nhâm", "Nhâm": "Nhâm",
             "Mậu": "Giáp", "Quý": "Giáp"}[year_stem]
    si = CAN.index(start)
    out = {}
    for i, branch in enumerate(["Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi",
                                "Thân", "Dậu", "Tuất", "Hợi", "Tý", "Sửu"]):
        out[branch] = CAN[(si + i) % 10] + " " + branch
    return out


def month_gz(year_stem, lunar_month):
    """Can-chi tháng âm lịch (Ngũ Hổ Độn: tháng Giêng = Dần)."""
    start = {"Giáp": "Bính", "Kỷ": "Bính", "Ất": "Mậu", "Canh": "Mậu",
             "Bính": "Canh", "Tân": "Canh", "Đinh": "Nhâm", "Nhâm": "Nhâm",
             "Mậu": "Giáp", "Quý": "Giáp"}[year_stem]
    si = CAN.index(start)
    stem = CAN[(si + lunar_month - 1) % 10]
    branch = CHI[(lunar_month + 1) % 12]
    return stem + " " + branch


def hour_gz(day_stem, hour_branch):
    """Can-chi giờ (Ngũ Tý Độn: giờ Tý khởi theo can ngày)."""
    start = {"Giáp": "Giáp", "Kỷ": "Giáp", "Ất": "Bính", "Canh": "Bính",
             "Bính": "Mậu", "Tân": "Mậu", "Đinh": "Canh", "Nhâm": "Canh",
             "Mậu": "Nhâm", "Quý": "Nhâm"}[day_stem]
    si = CAN.index(start)
    bi = CHI.index(hour_branch)
    return CAN[(si + bi) % 10] + " " + hour_branch


NAP_AM = [
    ("Hải Trung Kim", "K"), ("Lư Trung Hỏa", "H"), ("Đại Lâm Mộc", "M"),
    ("Lộ Bàng Thổ", "O"), ("Kiếm Phong Kim", "K"), ("Sơn Đầu Hỏa", "H"),
    ("Giản Hạ Thủy", "T"), ("Thành Đầu Thổ", "O"), ("Bạch Lạp Kim", "K"),
    ("Dương Liễu Mộc", "M"), ("Tuyền Trung Thủy", "T"), ("Ốc Thượng Thổ", "O"),
    ("Tích Lịch Hỏa", "H"), ("Tùng Bách Mộc", "M"), ("Trường Lưu Thủy", "T"),
    ("Sa Trung Kim", "K"), ("Sơn Hạ Hỏa", "H"), ("Bình Địa Mộc", "M"),
    ("Bích Thượng Thổ", "O"), ("Kim Bạch Kim", "K"), ("Phúc Đăng Hỏa", "H"),
    ("Thiên Hà Thủy", "T"), ("Đại Dịch Thổ", "O"), ("Thoa Xuyến Kim", "K"),
    ("Tang Đố Mộc", "M"), ("Đại Khê Thủy", "T"), ("Sa Trung Thổ", "O"),
    ("Thiên Thượng Hỏa", "H"), ("Thạch Lựu Mộc", "M"), ("Đại Hải Thủy", "T"),
]


def nap_am(year_stem, year_branch):
    si, bi = CAN.index(year_stem), CHI.index(year_branch)
    for n in range(60):
        if n % 10 == si and n % 12 == bi:
            return NAP_AM[n // 2]
    return ("?", "T")


SINH_NEXT = {"M": "H", "H": "O", "O": "K", "K": "T", "T": "M"}
KHAC_NEXT = {"M": "O", "O": "T", "T": "H", "H": "K", "K": "M"}


def cuc_relation(cuc_el, menh_el):
    if cuc_el == menh_el:
        return "Cục Mệnh tương hòa"
    if SINH_NEXT[cuc_el] == menh_el:
        return f"Cục sinh Mệnh {EL_NAME[menh_el]}"
    if SINH_NEXT[menh_el] == cuc_el:
        return f"Mệnh sinh Cục {EL_NAME[cuc_el]}"
    if KHAC_NEXT[cuc_el] == menh_el:
        return f"Cục khắc Mệnh {EL_NAME[menh_el]}"
    return f"Mệnh khắc Cục {EL_NAME[cuc_el]}"


# Tên hiển thị: user chốt 2026-10-24 — "Thiên Riêu" là tên dùng phổ biến,
# "Thiên Diêu" hiếm. Engine vẫn ghi "Thiên Diêu" (tên tvl), chỉ đổi lúc vẽ.
# (Màu/tra bảng vẫn dùng tên gốc, không đổi.)
DISPLAY_NAMES = {"Thiên Riêu": "Thiên Diêu",  # 2026-10-26 user đảo lại: hiển thị Thiên Diêu (trước đó 2026-10-24 chốt Riêu, nay bỏ)
                 "Trục Phù": "Trực Phù",  # 2026-10-26 user chốt theo sách: Trực Phù (值符) mới đúng, "Trục" chỉ là đọc sai chữ ự thành ụ khi zoom/OCR ảnh
                 "Tử Phủ": "Tử Phù"}  # 2026-10-26 user chốt: sao vòng Thái Tuế là Tử Phù, không phải Tử Phủ ("Tử Phủ" trong sách chỉ là tên gọi tắt của tổ hợp Tử Vi + Thiên Phủ, vd "Tử Phủ đồng cung"); data hiện tại vốn đã ghi Tử Phù, đây là lưới an toàn cho file chép site sau này


def disp_name(tok):
    for a, b in DISPLAY_NAMES.items():
        tok = tok.replace(a, b)
    return tok


def draw_col_tokens(draw, x, y, items, font, max_w, lh, grey_color):
    """items: [(text, kind)] — MỖI token 1 dòng riêng (không dồn 2 sao
    1 dòng, không dấu phẩy); màu theo ngũ hành, token mờ vẽ xám nhạt.
    Trả về y sau dòng cuối."""
    for text, kind in items:
        grey = text.endswith("(grey)")
        t = text[:-6] if grey else text
        c = grey_color if grey else element_color(t)
        draw.text((x, y), disp_name(t), font=font, fill=c)
        y += lh
    return y


def draw_label_value(draw, tx, y, label, value, value_x, max_w, font, lh,
                     label_color, value_color):
    """Vẽ 1 hàng key-value; value wrap theo từ, dòng tiếp nối tại value_x."""
    draw.text((tx, y), label, font=font, fill=label_color)
    vw = max_w - (value_x - tx)
    words, lines, cur = value.split(" "), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if draw.textlength(trial, font=font) <= vw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    lines.append(cur)
    for i, ln in enumerate(lines):
        draw.text((value_x, y + i * lh), ln, font=font, fill=value_color)
    return y + len(lines) * lh


def main():
    src, out = sys.argv[1], sys.argv[2]
    _size = sys.argv[3] if len(sys.argv) > 3 else "1800x1800"
    W, H = (int(v) for v in _size.lower().split("x"))
    CW, CH = W // 4, H // 4
    header, palaces = parse_clean(src)
    # (c) quyết Admin 25/10: render mặc định chỉ hiện 9 sao lưu cốt lõi
    # (core-9, theo Tân Biên); --luu full để hiện đủ; sao ĐV. đã bỏ
    # theo quyết Admin 25/10 (mặc định ẩn; --dv on để hiện lại với
    # file cũ còn dv). Data/text vẫn giữ đủ sao lưu (không mất dữ
    # liệu, để AI + đối chiếu tvl); sao ĐV. thì bỏ khỏi data luôn
    # (luu.py trả dv rỗng). LN.Văn Tinh nằm ở tầng Natal nên không
    # bị lọc lưu này ảnh hưởng.
    _CORE_LUU_BASE = {"Thái Tuế", "Tang Môn", "Bạch Hổ", "Thiên Khốc",
                      "Thiên Hư", "Thiên Mã", "Lộc Tồn", "Kình Dương",
                      "Đà La"}
    _luu_mode, _dv_on, _a = "core", False, sys.argv[4:]
    _i = 0
    while _i < len(_a):
        if _a[_i] == "--luu" and _i + 1 < len(_a):
            _luu_mode, _i = _a[_i + 1], _i + 2
        elif _a[_i] == "--dv" and _i + 1 < len(_a):
            _dv_on, _i = (_a[_i + 1] != "off"), _i + 2
        else:
            _i += 1
    if _luu_mode == "core":
        for _p in palaces.values():
            _p["luu"] = [t for t in _p["luu"]
                         if (t[2:].strip() if t.startswith("L.")
                             else t.strip()) in _CORE_LUU_BASE]
    if not _dv_on:
        for _p in palaces.values():
            _p["dv"] = []
    from phu_tinh import full_chart
    date, time_, gender = header["SINH"].split(" ")
    fc = full_chart(date, time_, gender)
    eng, inp = fc["engine"], fc["inp"]
    stems = palace_stems(inp["year_stem"])
    dai_van = eng["dai_van"]
    than_branch = eng["than"]
    tuan = set(header.get("TUAN", "").split())
    triet = set(header.get("TRIET", "").split())

    # Can-chi ngày (từ lap-la-so) + can-chi giờ.
    spec = importlib.util.spec_from_file_location(
        "laplaso", "lap-la-so.py")
    lap = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(lap)
    yy, mm, dd = map(int, date.split("-"))
    _hh = int(time_.split(":")[0])
    _ys, _yb, lm, ld, day_gz = lap.birth_lunar(yy, mm, dd, _hh)
    day_stem = next(s for s in CAN if day_gz.startswith(s))
    day_gz = day_stem + " " + day_gz[len(day_stem):]
    hour = hour_gz(day_stem, inp["hour_branch"])
    month = month_gz(inp["year_stem"], inp["month"])
    nap, nap_el = nap_am(inp["year_stem"], inp["year_branch"])
    cuc_el = header["CUC"].split()[0]
    cuc_el_code = {"Kim": "K", "Mộc": "M", "Thủy": "T", "Hỏa": "H",
                   "Thổ": "O"}[cuc_el]
    rel = cuc_relation(cuc_el_code, nap_el)
    amduong = "dương" if CAN.index(inp["year_stem"]) % 2 == 0 else "âm"
    amduong_txt = ("Âm " if amduong == "âm" else "Dương ") + (
        "Nam" if gender == "nam" else "Nữ")
    xem_parts = header["XEM"].rsplit(" ", 1)

    unknown = set()
    for p in palaces.values():
        for tok in p["natal"] + p["luu"] + p["dv"]:
            if classify(tok) == "unknown":
                unknown.add(tok)
    if unknown:
        print("WARN chưa phân loại được:", sorted(unknown), file=sys.stderr)

    # Pill Tuần/Triệt NẰM TRÊN TRỤC (đường biên chung 2 cung, như mẫu):
    # hộp đen chữ trắng, cao 24, đỉnh ở biên - 8 (lọt khe giữa dải cuối hàng
    # trên và header hàng dưới, không đụng nội dung ô). Cặp ngang hàng 0
    # thì đặt ở biên dưới của cặp (tránh tràn mép ảnh). Cặp không kề nhau
    # (lý thuyết không xảy ra vì Tuần/Triệt luôn 2 chi liên tiếp) thì fallback
    # badge trong ô.
    grid_pos = {}
    for rr in range(4):
        for cc in range(4):
            if GRID[rr][cc]:
                grid_pos[GRID[rr][cc]] = (rr, cc)

    def border_pill(branches):
        """Trả về (cx, top_y) của pill trên biên chung, hoặc None."""
        if len(branches) != 2:
            return None
        b1, b2 = sorted(branches)
        if b1 not in grid_pos or b2 not in grid_pos:
            return None
        r1, c1 = grid_pos[b1]
        r2, c2 = grid_pos[b2]
        if r1 == r2 and abs(c1 - c2) == 1:
            # Cặp ngang: pill giữa biên dọc chung.
            cx = (min(c1, c2) + 1) * CW
            top = r1 * CH - 11 if r1 > 0 else (r1 + 1) * CH - 11
            return (cx, top)
        if c1 == c2 and abs(r1 - r2) == 1:
            # Cặp dọc: pill giữa biên ngang chung.
            cx = c1 * CW + CW // 2
            top = (min(r1, r2) + 1) * CH - 11
            return (cx, top)
        return None

    pills = []          # (text, cx, top_y)
    spanned = set()     # các chi đã có pill chung (không vẽ badge riêng)
    pill_h = 28
    if set(tuan) == set(triet) and len(tuan) == 2:
        g = border_pill(tuan)
        if g:
            pills.append(("Tuần – Triệt", g[0], g[1]))
            spanned |= set(tuan)
    if not pills:
        for branches, label in ((tuan, "Tuần"), (triet, "Triệt")):
            g = border_pill(branches)
            if g:
                pills.append((label, g[0], g[1]))
                spanned |= set(branches)

    unknown = set()
    for p in palaces.values():
        for tok in p["natal"] + p["luu"] + p["dv"]:
            if classify(tok) == "unknown":
                unknown.add(tok)
    if unknown:
        print("WARN chưa phân loại được:", sorted(unknown), file=sys.stderr)

    img = Image.new("RGB", (W, H), (253, 251, 247))
    d = ImageDraw.Draw(img)
    # Chế độ "spec": thử bộ cỡ chữ GPT/Claude gợi ý theo mẫu B (Aituvi)
    # — gọi render_chart.py <src> <out> <WxH> spec. Chỉ đổi cỡ/bước,
    # không đổi bố cục; mặc định (không có "spec") giữ nguyên bản v4.
    SPEC = len(sys.argv) > 4 and sys.argv[4] == "spec"
    f_head = ImageFont.truetype(F_BOLD, 26 if CW < 400 else 28)
    f_head_reg = ImageFont.truetype(F_REG, 26 if CW < 400 else 28)
    f_small = ImageFont.truetype(F_REG, 17 if CW < 400 else 20)
    f_chinh = ImageFont.truetype(F_BOLD, 26)
    head_step, chinh_step, gap, tok_step = 36, 28, 24, 23
    if SPEC:
        f_head = ImageFont.truetype(F_BOLD, 21)
        f_head_reg = ImageFont.truetype(F_REG, 21)
        f_small = ImageFont.truetype(F_REG, 19)
        f_chinh = ImageFont.truetype(F_BOLD, 22)
        head_step, chinh_step, gap, tok_step = 26, 28, 26, 26
    # Sao phụ tinh (cột token) vẽ Bold cho dễ đọc (user 2026-10-24);
    # đã đo token dài nhất "Kình Dương (H)" = 139px < col_w 146 nên không tràn.
    f_star = ImageFont.truetype(F_BOLD, 18 if CW < 400 else 21)
    f_badge = ImageFont.truetype(F_BOLD, 20)
    f_than = ImageFont.truetype(F_BOLD, 16 if CW < 400 else 18)
    f_center_t = ImageFont.truetype(F_TITLE, 44)
    f_center = ImageFont.truetype(F_REG, 24)
    f_center_sm = ImageFont.truetype(F_REG, 20)
    center_lh, title_step = 38, 60
    if SPEC:
        f_star = ImageFont.truetype(F_REG, 20)
        f_center_t = ImageFont.truetype(F_TITLE, 32)
        f_center = ImageFont.truetype(F_REG, 22)
        f_center_sm = ImageFont.truetype(F_REG, 19)
        center_lh, title_step = 32, 48
    BLACK = (35, 32, 26)
    GREY = (110, 110, 110)
    LGREY = (170, 170, 170)
    BLUE = (26, 82, 118)
    BRONZE = (161, 98, 7)
    LINE = (216, 210, 196)
    MENH_BG = (251, 243, 223)

    for r in range(4):
        for c in range(4):
            branch = GRID[r][c]
            if branch is None:
                continue
            x0, y0 = c * CW, r * CH
            p = palaces[branch]
            if p["cung"] == "Mệnh":
                d.rectangle([x0, y0, x0 + CW - 1, y0 + CH - 1],
                            fill=MENH_BG, outline=BRONZE, width=3)
            else:
                d.rectangle([x0, y0, x0 + CW - 1, y0 + CH - 1],
                            outline=LINE, width=2)
            x, y = x0 + 16, y0 + 16
            wmax = CW - 32
            col_w = (wmax - 12) // 2
            # Header 3 phần: can-chi trái, tên cung giữa (màu theo chi),
            # năm đại hạn phải.
            stem_br = stems[branch].split()
            abbr = f"{CAN_ABBR[stem_br[0]]}.{branch}"
            d.text((x, y + 4), abbr, font=f_small, fill=BLACK)
            nm = p["cung"].upper()
            nw = d.textlength(nm, font=f_head)
            if branch == than_branch:
                # Badge Thân nền đỏ chữ trắng (kiểu AItuvi), căn giữa
                # cả cụm tên+badge — KHÔNG ghi chữ "Thân cư" vào cột
                # phụ tinh (user chốt 2026-10-24).
                _bt = "Thân"
                _bw = d.textlength(_bt, font=f_than) + 12
                _nx = x0 + (CW - nw - 6 - _bw) // 2
                d.text((_nx, y), nm, font=f_head,
                       fill=EL_COLOR[CHI_EL[branch]])
                _bx = _nx + nw + 6
                d.rectangle([_bx, y + 2, _bx + _bw, y + 26],
                            fill=(211, 47, 47))
                _tw2 = d.textlength(_bt, font=f_than)
                d.text((_bx + (_bw - _tw2) // 2, y + 4), _bt,
                       font=f_than, fill="white")
            else:
                d.text((x0 + (CW - nw) // 2, y), nm, font=f_head,
                       fill=EL_COLOR[CHI_EL[branch]])
            age = str(dai_van[branch])
            aw = d.textlength(age, font=f_head_reg)
            d.text((x0 + CW - 16 - aw, y), age, font=f_head_reg,
                   fill=BLACK)
            y += head_step
            # Dòng 2: nhãn ngũ hành chi (+/- âm/dương, chữ đen) + chính tinh.
            el_label = ("+" if CHI_YANG[branch] == 1 else "-") + EL_NAME[
                CHI_EL[branch]]
            d.text((x, y + 2), el_label, font=f_small, fill=BLACK)
            chinh_x = x + (64 if CW < 400 else 110)
            if p["chinh"]:
                for t in p["chinh"]:
                    d.text((chinh_x, y), disp_name(t), font=f_chinh,
                           fill=element_color(t))
                    y += chinh_step
            else:
                d.text((chinh_x, y), "— VCD —", font=f_chinh, fill=GREY)
                y += chinh_step
            y += gap
            if branch not in spanned:
                tt = None
                if branch in tuan and branch in triet:
                    tt = "Tuần – Triệt"
                elif branch in tuan:
                    tt = "Tuần"
                elif branch in triet:
                    tt = "Triệt"
                if tt:
                    tw = d.textlength(tt, font=f_badge)
                    px, py = 8, 4
                    d.rectangle([x, y, x + tw + 2 * px, y + pill_h],
                                fill=BLACK)
                    d.text((x + px, y + py), tt, font=f_badge, fill="white")
                    y += pill_h + 6
            # 2 cột gộp: natal -> L. -> ĐV. theo từng cột cát/hung.
            left_items, right_items = [], []
            for section in (p["natal"], p["luu"], p["dv"]):
                for tok in section:
                    (right_items if classify(tok) == "hung"
                     else left_items).append((tok, classify(tok)))
            y_left = y
            if left_items:
                y_left = draw_col_tokens(d, x, y_left, left_items, f_star,
                                         col_w, tok_step, LGREY)
            y_right = y
            if right_items:
                y_right = draw_col_tokens(d, x + col_w + 12, y_right,
                                          right_items, f_star,
                                          col_w, tok_step, LGREY)
            # Dải cuối GHIM đáy ô: ĐV. trái, vòng giữa, LN. phải.
            strip_y = y0 + CH - 32
            # Pre-vận (chưa vào đại vận đầu): nhãn rỗng -> gạch ngang,
            # không crash. Lá thường có nhãn nên không đổi gì.
            dv_s = f"ĐV. {LABEL_SHORT.get(p['dvnhan'], '—')}"
            ln_s = f"LN. {LABEL_SHORT.get(p['lnnhan'], '—')}"
            d.text((x, strip_y), dv_s, font=f_small, fill=BLACK)
            vw = d.textlength(p["vong"], font=f_small)
            d.text((x0 + (CW - vw) // 2, strip_y), p["vong"],
                   font=f_small, fill=BLACK)
            lw = d.textlength(ln_s, font=f_small)
            d.text((x0 + CW - 16 - lw, strip_y), ln_s, font=f_small,
                   fill=BLACK)

    # Ô giữa (2x2): bảng key-value như mẫu.
    cx, cy = CW, CH
    d.rectangle([cx, cy, cx + 2 * CW - 1, cy + 2 * CH - 1],
                outline=BRONZE, width=3)
    y = cy + 56
    tx = cx + 80
    cw = 2 * CW - 160
    _tw = d.textlength("LÁ SỐ TỬ VI", font=f_center_t)
    d.text((cx + CW - _tw // 2, y), "LÁ SỐ TỬ VI", font=f_center_t,
           fill=BLACK)
    y += title_step
    hh, mi = time_.split(":")
    rows = [
        ("Họ tên:", header.get("NGUOI", "Nam")),
        ("Năm:", f"{yy} {inp['year_stem']} {inp['year_branch']}"),
        ("Tháng:", f"{int(mm)} ({lm}) {month}"),
        ("Ngày:", f"{int(dd)} ({ld}) {day_gz}"),
        ("Giờ:", f"{int(hh)} giờ {mi} phút {hour}"),
        ("Năm xem:", f"{xem_parts[0]}, {xem_parts[1]} tuổi"),
        ("Âm dương:", amduong_txt),
        ("Bản mệnh:", f"{nap} – {header['CUC']} ({rel})"),
        ("Cân lượng:", header["CAN"]),
        ("Chủ mệnh:", header["CHU_MENH"]),
        ("Chủ thân:", header["CHU_THAN"]),
        ("Lai nhân cung:", header["LAI_NHAN"]),
    ]
    value_x = tx + 210
    for idx, (label, value) in enumerate(rows):
        y = draw_label_value(d, tx, y, label, value, value_x, cw, f_center,
                             center_lh, BLACK, BLUE)
        if idx in (4, 7):
            d.line([(tx, y + 2), (tx + cw, y + 2)], fill=BRONZE, width=1)
            y += 8
    y += 12
    # Legend ngũ hành (ô vuông màu như mẫu).
    sq = 18
    lx = tx
    for code in ("K", "M", "T", "H", "O"):
        d.rectangle([lx, y + 4, lx + sq, y + 4 + sq], fill=EL_COLOR[code])
        lx += sq + 6
        lab = EL_NAME[code]
        d.text((lx, y), lab, font=f_center_sm, fill=BLACK)
        lx += d.textlength(lab, font=f_center_sm) + 18
    y += 28
    d.text((tx, y), "M: Miếu • V: Vượng • Đ: Đắc • B: Bình • H: Hãm",
           font=f_center_sm, fill=GREY)

    # Vòng 12 địa chi sát mép trong ô giữa (như mẫu) + đường tam hợp /
    # xung neo ở TÂM NHÃN CHI của cung tương ứng (user chốt 15:35 — v4.6
    # neo mép ngoài là hiểu ngược). Nhãn góc (Mão, Ngọ, Tý, Dậu) sát góc;
    # nhãn giữa canh giữa slot. Nhãn vẽ sau đường để chữ đè lên đường.
    f_ring = ImageFont.truetype(F_REG, 19 if SPEC else 24)
    _cx0, _cy0 = CW, CH
    _slot_x = [_cx0 + (i + 0.5) * (2 * CW) / 4 for i in range(4)]
    _mid_x = [_cx0 + CW // 2, _cx0 + CW + CW // 2]  # tâm PHÚC/ĐIỀN, TỬ/TÀI
    _slot_y = [_cy0 + (i + 0.5) * CH for i in range(2)]
    _ring = {}  # chi -> (draw_x, draw_y, center_x, center_y)
    def _put(br, edge, idx, align):
        w = d.textlength(br, font=f_ring)
        if edge == "top":
            dx = (_cx0 + 12 if align == "left" else
                  _cx0 + 2 * CW - 12 - w if align == "right" else
                  _mid_x[idx - 1] - w // 2)
            dy = _cy0 + 12
        elif edge == "bottom":
            dx = (_cx0 + 12 if align == "left" else
                  _cx0 + 2 * CW - 12 - w if align == "right" else
                  _mid_x[idx - 1] - w // 2)
            dy = _cy0 + 2 * CH - 12 - 24
        elif edge == "right":
            dx = _cx0 + 2 * CW - 12 - w
            dy = _slot_y[idx] - 12
        else:
            dx = _cx0 + 12
            dy = _slot_y[idx] - 12
        _ring[br] = (dx, dy, dx + w // 2, dy + 12)
    # Vòng 12 chi (user phán 2026-10-24 16:28): bản theo giới tính này
    # mới ĐÚNG (khớp tvl) — bắt đầu Mão ở góc trên-trái, đi thuận (+1)
    # cho Nam, nghịch (-1) cho Nữ. Tài liệu tiểu hạn user gửi 16:23 chỉ
    # để check thêm (cách đếm tiểu hạn), KHÔNG phải để thay vòng này:
    # bản v4 đổi sang vòng tiểu hạn (khởi theo tam hợp + chiều theo
    # can/giới) là SAI, đã trả lại bản này.
    if gender == "nữ":
        _top = ["Mão", "Dần", "Sửu", "Tý"]
        _right = ["Hợi", "Tuất"]
        _bottom = ["Ngọ", "Mùi", "Thân", "Dậu"]
        _left = ["Thìn", "Tỵ"]
    else:
        _top = ["Mão", "Thìn", "Tỵ", "Ngọ"]
        _right = ["Mùi", "Thân"]
        _bottom = ["Tý", "Hợi", "Tuất", "Dậu"]
        _left = ["Dần", "Sửu"]
    for _i, _b in enumerate(_top):
        _put(_b, "top", _i,
             "left" if _i == 0 else "right" if _i == 3 else "center")
    for _i, _b in enumerate(_right):
        _put(_b, "right", _i, "right")
    for _i, _b in enumerate(_bottom):
        _put(_b, "bottom", _i,
             "left" if _i == 0 else "right" if _i == 3 else "center")
    for _i, _b in enumerate(_left):
        _put(_b, "left", _i, "left")
    by_cung = {p["cung"]: b for b, p in palaces.items()}
    if all(k in by_cung for k in ("Mệnh", "Tài Bạch", "Quan Lộc",
                                   "Thiên Di")):
        def _inner(br):
            rr, cc = grid_pos[br]
            cx = cc * CW + CW // 2
            cy = rr * CH + CH // 2
            return (min(max(cx, CW), 3 * CW),
                    min(max(cy, CH), 3 * CH))
        _m, _t, _q, _d = (_inner(by_cung[k]) for k in
                          ("Mệnh", "Tài Bạch", "Quan Lộc", "Thiên Di"))
        for _a, _b in ((_m, _t), (_t, _q), (_q, _m)):
            d.line([_a, _b], fill=(175, 165, 205), width=2)
        d.line([_m, _d], fill=(235, 180, 145), width=2)
    for _br, (_dx, _dy, _ccx, _ccy) in _ring.items():
        d.text((_dx, _dy), _br, font=f_ring, fill=BLACK)

    # Pill Tuần/Triệt chung trên trục biên (hộp đen chữ trắng, như mẫu).
    for text, cx, top in pills:
        tw = d.textlength(text, font=f_badge)
        x1, x2 = cx - tw // 2 - 10, cx + tw // 2 + 10
        d.rectangle([x1, top, x2, top + pill_h], fill=BLACK)
        d.text((cx - tw // 2, top + 4), text, font=f_badge, fill="white")


    img.save(out)
    print(f"saved {out} ({W}x{H})")


if __name__ == "__main__":
    main()
