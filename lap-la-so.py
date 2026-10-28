#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Lập lá số Tử Vi từ dữ liệu âm lịch + giờ sinh.
Công thức lấy từ sách trong kho KB (Tam Hợp Phái 1, Tân Biên),
KHÔNG suy ngược từ lá số mẫu. Dùng để kiểm chứng: chạy lá số
Quý Hợi 1983, tháng 8, ngày 16, giờ Tỵ rồi đối chiếu với lá số mẫu.

Quy ước chỉ số: Tý=0, Sửu=1, Dần=2, Mão=3, Thìn=4, Tỵ=5,
Ngọ=6, Mùi=7, Thân=8, Dậu=9, Tuất=10, Hợi=11.
Can: Giáp=0, Ất=1, Bính=2, Đinh=3, Mậu=4, Kỷ=5, Canh=6, Tân=7, Nhâm=8, Quý=9.
"""

CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ", "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
CAN = ["Giáp", "Ất", "Bính", "Đinh", "Mậu", "Kỷ", "Canh", "Tân", "Nhâm", "Quý"]
CHI_IDX = {c: i for i, c in enumerate(CHI)}
CAN_IDX = {c: i for i, c in enumerate(CAN)}

# Chủ mệnh / Chủ thân theo chi năm sinh — Tam Hợp Phái 1 §36/§37
# (quyết §36: "Tử thuộc tham lang sửu hợi cửa dần tuất sinh ra thuộc
# lộc tồn, Mão dậu thuộc văn tị vị vũ thìn thân liêm ở lại ngọ phá quân";
# §37: "Tí ngọ an thân linh hỏa tinh sửu vị thiên tướng dần thân lương,
# Mão dậu thiên đồng thân chủ là tị hợi thiên cơ thìn tuất xương").
# Kiểm chứng 2026-10-23: khớp 11/12 lá mẫu đã lưu (text-app +
# tuviluangiai.vn; các chi Hợi/Tỵ/Dậu/Mão/Thân/Tuất/Sửu/Ngọ/Mùi qua
# lá mẫu + Dần/Thìn qua tuviluangiai.vn); chi Tý chỉ có sách, chưa có
# lá mẫu. Ngoại lệ duy nhất: AItuvi cho lá mẫu (Hợi) Chủ thân
# Thiên Tướng thay vì Thiên Cơ, và 2 lá AItuvi năm Mão cũng lệch bảng
# — AItuvi coi như ngoại lệ chưa rõ luật, không theo nó (quyết user
# 2026-10-23: theo phe tuviluangiai.vn + sách). Chủ thân Hợi đang
# tranh cãi (Cơ theo bảng vs Tướng theo AItuvi/repo): engine vẫn trả
# Thiên Cơ theo bảng, kèm cờ chu_than_tranh_cai=True.
CHU_MENH = {"Tý": "Tham Lang", "Sửu": "Cự Môn", "Dần": "Lộc Tồn",
            "Mão": "Văn Khúc", "Thìn": "Liêm Trinh", "Tỵ": "Vũ Khúc",
            "Ngọ": "Phá Quân", "Mùi": "Vũ Khúc", "Thân": "Liêm Trinh",
            "Dậu": "Văn Khúc", "Tuất": "Lộc Tồn", "Hợi": "Cự Môn"}
# ĐỔI 2026-10-23: Tý Hỏa Tinh (sách §37) → Linh Tinh (2 site: tuviluangiai.vn
# + tuvuvietnam.vn đều ghi Linh Tinh cho lá Tý; Ngọ vẫn Hỏa Tinh theo cả sách
# lẫn tvl lá mẫu — pattern có thể là tách cặp Hỏa/Linh theo âm/dương chi
# (Tý âm→Linh, Ngọ dương→Hỏa), nhưng mới chỉ có bằng chứng ở 2 chi này).
CHU_THAN = {"Tý": "Linh Tinh", "Sửu": "Thiên Tướng", "Dần": "Thiên Lương",
            "Mão": "Thiên Đồng", "Thìn": "Văn Xương", "Tỵ": "Thiên Cơ",
            "Ngọ": "Hỏa Tinh", "Mùi": "Thiên Tướng", "Thân": "Thiên Lương",
            "Dậu": "Thiên Đồng", "Tuất": "Văn Xương", "Hợi": "Thiên Cơ"}


def hour_branch(hh, mm):
    """Chi giờ từ giờ dương (phút): Tý 23-1h, Sửu 1-3h, Dần 3-5h..."""
    h = hh + mm / 60.0
    return CHI[int((h + 1) // 2) % 12]


def solar_to_lunar(y, m, d):
    """Dương lịch -> (can năm, chi năm, tháng âm, ngày âm, can chi ngày).
    Ưu tiên lịch Việt lich_vn.py (thuật toán Hồ Ngọc Đức, múi giờ +7,
    vendored từ repo lasotuvi MIT) — đã kiểm 8/8 cặp ngày đã biết, kể cả
    vụ lá mẫu mà sxtwl (lịch Trung Quốc) lệch 1 ngày. Fallback sxtwl
    trong .venv-lunar nếu thiếu file lich_vn.
    Lưu ý: can chi năm lấy theo năm âm lịch."""
    try:
        import os, sys
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        from lich_vn import S2L, jdFromDate
        ld, lm, ly, _leap = S2L(d, m, y, 7)
        can_nam = CAN[(ly + 6) % 10]
        chi_nam = CHI[(ly + 8) % 12]
        jd = jdFromDate(d, m, y)
        return (can_nam, chi_nam, lm, ld,
                CAN[(jd + 9) % 10] + CHI[(jd + 1) % 12])
    except ImportError:
        import sxtwl
        day = sxtwl.fromSolar(y, m, d)
        yg = day.getYearGZ()
        dg = day.getDayGZ()
        return (CAN[yg.tg], CHI[yg.dz], day.getLunarMonth(),
                day.getLunarDay(), CAN[dg.tg] + CHI[dg.dz])


def birth_lunar(y, m, d, hh):
    """Âm lịch cho NGÀY SINH (khác solar_to_lunar thuần túy):
    giờ Tý 23:00-24:00 thuộc về ngày hôm sau, nên đổi sang dương
    lịch ngày hôm sau rồi mới đổi ra âm lịch. Kiểm chứng 2026-10-26:
    sinh 1990-01-15 23:30, TVN tính âm 20 Tân Tỵ (không phải âm 19
    Canh Thìn như đổi thẳng ngày 15). Giờ Tý 00:00-01:00 KHÔNG đổi
    (ngày bắt đầu từ 23h hôm trước chính là ngày dương đó; lá mẫu
    00:30 đã kiểm với tvl theo cách cũ). Tháng/năm âm ở biên (cuối
    tháng/năm âm) được xử lý qua ngày dương hôm sau nên tự đúng,
    nhưng chưa có mẫu TVN trực tiếp cho trường hợp biên đó."""
    if hh == 23:
        import datetime
        nd = datetime.date(y, m, d) + datetime.timedelta(days=1)
        return solar_to_lunar(nd.year, nd.month, nd.day)
    return solar_to_lunar(y, m, d)

# Ngũ Hổ Độn: thiên can của cung Dần theo can năm (Tam Hợp, pdf 036)
HO_DON_DAN = {"Giáp": "Bính", "Kỷ": "Bính",
              "Ất": "Mậu", "Canh": "Mậu",
              "Bính": "Canh", "Tân": "Canh",
              "Đinh": "Nhâm", "Nhâm": "Nhâm",
              "Mậu": "Giáp", "Quý": "Giáp"}

# Bảng lập Cục §7 Tân Biên: hàng = nhóm chi cung Mệnh, cột = nhóm can năm
CUC_TABLE = {
    ("Tý", "Sửu"):       ["Thủy", "Hỏa", "Thổ", "Mộc", "Kim"],
    ("Dần", "Mão", "Tuất", "Hợi"): ["Hỏa", "Thổ", "Mộc", "Kim", "Thủy"],
    ("Thìn", "Tỵ"):      ["Mộc", "Kim", "Thủy", "Hỏa", "Thổ"],
    ("Ngọ", "Mùi"):      ["Thổ", "Mộc", "Kim", "Thủy", "Hỏa"],
    ("Thân", "Dậu"):     ["Kim", "Thủy", "Hỏa", "Thổ", "Mộc"],
}
STEM_GROUP = ["Giáp Kỷ", "Ất Canh", "Bính Tân", "Đinh Nhâm", "Mậu Quý"]
CUC_NUM = {"Thủy": 2, "Mộc": 3, "Kim": 4, "Thổ": 5, "Hỏa": 6}

# Nạp âm 60 Giáp Tý: 30 cặp, thứ tự theo vòng can chi
NAP_AM = ["Kim", "Hỏa", "Mộc", "Thổ", "Kim", "Hỏa", "Thủy", "Thổ", "Kim", "Mộc",
          "Thủy", "Thổ", "Hỏa", "Mộc", "Thủy", "Kim", "Hỏa", "Mộc", "Thổ", "Kim",
          "Hỏa", "Thủy", "Thổ", "Kim", "Mộc", "Thủy", "Thổ", "Hỏa", "Mộc", "Thủy"]


def nap_am(can, chi):
    """Ngũ hành nạp âm của một trụ can chi."""
    for n in range(60):
        if CAN[n % 10] == can and CHI[n % 12] == chi:
            return NAP_AM[n // 2]
    raise ValueError(f"Không tìm thấy nạp âm cho {can}{chi}")


def palace_stem(branch, year_stem):
    """Thiên can của một cung theo Ngũ Hổ Độn.
    SỬA 22/10 (phát hiện từ lá mẫu Tân Mão): phải lấy hiệu chi mod 12
    trước rồi mới mod 10, vì vòng chi 12 cung và vòng can 10 can lệch
    nhau. Bản cũ thiếu mod 12 nên can cung Tý/Sửu sai lệch 2
    (vd năm Tân: Tý tính Mậu thay vì Canh, Sửu tính Kỷ thay vì Tân),
    làm Lai nhân của lá mẫu ra Phụ Mẫu thay vì Huynh Đệ."""
    dan_stem = CAN_IDX[HO_DON_DAN[year_stem]]
    steps = (CHI_IDX[branch] - CHI_IDX["Dần"]) % 12
    return CAN[(dan_stem + steps) % 10]


SINH = {"Mộc": "Hỏa", "Hỏa": "Thổ", "Thổ": "Kim", "Kim": "Thủy", "Thủy": "Mộc"}
KHAC = {"Mộc": "Thổ", "Thổ": "Thủy", "Thủy": "Hỏa", "Hỏa": "Kim", "Kim": "Mộc"}


def menh_cuc_relation(menh_elem, cuc_elem):
    """Quan hệ ngũ hành giữa Mệnh (nạp âm năm) và Cục, theo cách ghi
    trong header lá số app: Mệnh sinh/khắc Cục, Cục sinh/khắc Mệnh,
    hoặc bình hòa khi cùng hành."""
    if menh_elem == cuc_elem:
        return "bình hòa"
    if SINH[menh_elem] == cuc_elem:
        return "Mệnh sinh Cục"
    if KHAC[menh_elem] == cuc_elem:
        return "Mệnh khắc Cục"
    if SINH[cuc_elem] == menh_elem:
        return "Cục sinh Mệnh"
    if KHAC[cuc_elem] == menh_elem:
        return "Cục khắc Mệnh"
    return "?"


def lai_nhan_cung(menh, year_stem):
    """Lai nhân cung: cung có thiên can trùng can năm sinh.
    Nếu có 2 cung trùng (chỉ xảy ra với can Tân, Nhâm), lấy chi đầu tiên
    theo thứ tự chi Tý→Hợi (quét chi từ Tý lên, không đếm từ Mệnh).
    ĐỔI LUẬT 2026-10-23: luật cũ (đếm nghịch từ Mệnh) chỉ dựa trên 1 ca
    2-ứng-viên thật (2 lá mẫu) + bản text-app lá mẫu (Gemini); 3 ca phân biệt
    trên tuviluangiai.vn đều đi ngược luật cũ (lá mẫu Nhâm→Phụ Mẫu,
    1982 Nhâm→Tử Nữ, 2002 Nhâm→Phu Thê) và đều khớp luật quét-từ-Tý
    (Nhâm→Tý, Tân→Sửu). Sau đổi luật: khớp tvl 11/11 lá sạch gia đình
    (lá mẫu sửa Điền→Phụ, 10 lá còn lại không đổi) + 5/5 lá thăm dò."""
    cung_names = ["Mệnh", "Huynh Đệ", "Phu Thê", "Tử Nữ", "Tài Bạch",
                  "Tật Ách", "Thiên Di", "Nô Bộc", "Quan Lộc", "Điền Trạch",
                  "Phúc Đức", "Phụ Mẫu"]
    menh_idx = CHI_IDX[menh]
    branch_to_name = {CHI[(menh_idx - i) % 12]: name
                      for i, name in enumerate(cung_names)}
    for branch in CHI:
        if palace_stem(branch, year_stem) == year_stem:
            return branch_to_name[branch], branch
    return None, None


def menh_than(month, hour_branch):
    """Cung Mệnh / Thân từ tháng sinh (âm lịch) và giờ sinh.
    Tam Hợp pdf 035: từ Dần thuận đếm đến tháng sinh; từ cung đó
    khởi giờ Tý, nghịch đếm đến giờ sinh = Mệnh; thuận đếm = Thân."""
    month_palace = (CHI_IDX["Dần"] + month - 1) % 12
    hour = CHI_IDX[hour_branch]
    menh = (month_palace - hour) % 12
    than = (month_palace + hour) % 12
    return CHI[menh], CHI[than]


def cuc_from_table(menh_branch, year_stem):
    for group, row in CUC_TABLE.items():
        if menh_branch in group:
            for gi, gname in enumerate(STEM_GROUP):
                if year_stem in gname:
                    return row[gi]
    raise ValueError("Không tìm thấy cục")


# --- An Tử Vi: 2 cách độc lập từ sách -------------------------------
# Cách 1: bảng Tân Biên (Thổ ngũ cục), chép từ bản lai, bố cục lưới:
#   hàng 1: Tỵ Ngọ Mùi Thân | hàng 2: Thìn . . Dậu
#   hàng 3: Mão . . Tuất   | hàng 4: Dần Sửu Tý Hợi
TAN_BIEN_THO_TABLE = {
    "Tỵ": [8, 20, 24], "Ngọ": [1, 13, 25, 29], "Mùi": [6, 18, 30], "Thân": [11, 23],
    "Thìn": [3, 15, 19, 27], "Dậu": [16, 28],
    "Mão": [10, 14, 22], "Tuất": [21],
    "Dần": [5, 9, 17], "Sửu": [4, 12], "Tý": [7], "Hợi": [2, 26],
}

# Bảng Kim chép từ Tân Biên §8.1 (lưới 4x4, ô giữa là tên cục).
# LƯU Ý (22/10): bản OCR ghi "21" ở cả ô Mùi lẫn ô Thìn, và thiếu ngày 24.
# Chuỗi bước +5,-3,+1,-2 lặp (khởi Hợi ngày 1) cho: ngày 21 -> Thìn,
# ngày 24 -> Mùi, khớp đủ 30 ngày không trùng — nên ô Mùi ghi 24, không
# phải 21. Đã kiểm chứng: Kim ngày 2 -> Thìn (lá mẫu, app khớp).
TAN_BIEN_KIM_TABLE = {
    "Tỵ": [6, 16, 19, 25], "Ngọ": [10, 20, 23, 29], "Mùi": [14, 24, 27], "Thân": [18, 28],
    "Thìn": [2, 12, 15, 21], "Dậu": [22],
    "Mão": [8, 11, 17], "Tuất": [26],
    "Dần": [4, 7, 13], "Sửu": [3, 9], "Tý": [5], "Hợi": [1, 30],
}

# Bảng Hỏa chép từ Tân Biên §8.1 (cùng cách đọc lưới như bảng Kim).
TAN_BIEN_HOA_TABLE = {
    "Tỵ": [10, 24, 29], "Ngọ": [2, 16, 30], "Mùi": [8, 22], "Thân": [14, 28],
    "Thìn": [4, 18, 23], "Dậu": [1, 20],
    "Mão": [12, 17, 27], "Tuất": [7, 26],
    "Dần": [6, 11, 21], "Sửu": [5, 15, 25], "Tý": [9, 19], "Hợi": [3, 13],
}

TAN_BIEN_TABLES = {"Thổ": TAN_BIEN_THO_TABLE, "Kim": TAN_BIEN_KIM_TABLE,
                   "Hỏa": TAN_BIEN_HOA_TABLE}

# Cách 2: công thức Tam Hợp (pdf 038-042): ngày chia cục = thương q, dư r.
#   r = 0: từ Dần thuận đếm q (Dần tính là 1) -> Dần + q - 1
#   r > 0: từ cung khởi của cục + r, thuận đếm q (cung khởi tính là 1)
#   -> khởi + r + q - 1. Khởi theo tinh hoa: Thủy Sửu, Mộc Thìn,
#   Kim Hợi, Thổ Ngọ, Hỏa Dậu.
#   GIỚI HẠN ĐÃ BIẾT (22/10): công thức này SAI với Thổ ngày 9 (dư 4) —
#   cho Tuất trong khi bảng Tân Biên và app đều ra Dần; và SAI với
#   Kim ngày 2 — cho Tý trong khi bảng Tân Biên và app đều ra Thìn.
#   Nó chỉ khớp bảng ở Thủy (Tử = Sửu + ngày//2, đã đối chiếu đủ 30 ngày)
#   và Mộc (nhánh r = 0, 1; nhánh r = 2 lấy từ bảng). Vì vậy build_chart
#   ưu tiên bảng; công thức chỉ còn là fallback cho Thủy/Mộc.
KHOI_CUC = {"Thủy": "Sửu", "Mộc": "Thìn", "Kim": "Hợi", "Thổ": "Ngọ", "Hỏa": "Dậu"}


def tu_vi_tan_bien_table(day, cuc):
    table = TAN_BIEN_TABLES.get(cuc)
    if table is None:
        return None  # Thủy/Mộc dùng công thức đã đối chiếu đủ bảng
    for palace, days in table.items():
        if day in days:
            return palace
    return None


def tu_vi_tam_hop_formula(day, cuc):
    q, r = divmod(day, CUC_NUM[cuc])
    if r == 0:
        return CHI[(CHI_IDX["Dần"] + q - 1) % 12]
    khoi = CHI_IDX[KHOI_CUC[cuc]]
    return CHI[(khoi + r + q - 1) % 12]


def tu_vi_lasotuvi_formula(day, cuc_num):
    """Thuật toán an Tử Vi từ repo lasotuvi (MIT, doanguyen, hàm timTuVi
    trong AmDuong.py) — đã đối chiếu khớp 150/150 với bảng Tân Biên §8.1
    (5 cục x 30 ngày), kể cả các ca công thức Tam Hợp sai (Thổ ngày 9,
    Kim ngày 2/18, Mộc dư 2). Dùng làm fallback khi chưa có bảng chép.
    Thuật toán: bắt đầu ở Dần, cộng dồn cục cho tới khi >= ngày, rồi
    hiệu chỉnh bằng phần dư (dư chẵn tiến, dư lẻ lùi)."""
    cung_dan = 3  # Dần, đếm 1-based: Tý=1 ... Hợi=12
    cuc = cuc_num
    while cuc < day:
        cuc += cuc_num
        cung_dan += 1
    sai_lech = cuc - day
    if sai_lech % 2 == 1:
        sai_lech = -sai_lech
    idx = (cung_dan + sai_lech) % 12
    if idx == 0:
        idx = 12
    return CHI[idx - 1]


# --- Các hệ sao ------------------------------------------------------
def tu_vi_system(tu_vi):
    """Tử Vi hệ, Tân Biên §8.1: từ Tử Vi thuận đếm: bỏ 3 cung an Liêm
    (+4), bỏ 2 cung an Đồng (+3 nữa = +7), Vũ (+8), Dương (+9),
    bỏ 1 cung an Cơ (+11)."""
    t = CHI_IDX[tu_vi]
    return {
        "Tử Vi": tu_vi,
        "Liêm Trinh": CHI[(t + 4) % 12],
        "Thiên Đồng": CHI[(t + 7) % 12],
        "Vũ Khúc": CHI[(t + 8) % 12],
        "Thái Dương": CHI[(t + 9) % 12],
        "Thiên Cơ": CHI[(t + 11) % 12],
    }


def thien_phu_from_tu_vi(tu_vi):
    """Thiên Phủ đối xứng Tử Vi qua trục Dần-Thân (Tam Hợp pdf 042):
    Tử tại Tý -> Phủ tại Thìn; Tử tại Thìn -> Phủ tại Tý."""
    return CHI[(4 - CHI_IDX[tu_vi]) % 12]


def thien_phu_system(thien_phu):
    """Thiên Phủ hệ, Tân Biên §8.2: thuận đếm mỗi cung một sao:
    Âm (+1), Tham (+2), Cự (+3), Tướng (+4), Lương (+5), Sát (+6),
    bỏ 3 cung an Phá (+10)."""
    t = CHI_IDX[thien_phu]
    return {
        "Thiên Phủ": thien_phu,
        "Thái Âm": CHI[(t + 1) % 12],
        "Tham Lang": CHI[(t + 2) % 12],
        "Cự Môn": CHI[(t + 3) % 12],
        "Thiên Tướng": CHI[(t + 4) % 12],
        "Thiên Lương": CHI[(t + 5) % 12],
        "Thất Sát": CHI[(t + 6) % 12],
        "Phá Quân": CHI[(t + 10) % 12],
    }


TU_HOA = {
    # Theo Tân Biên §8.23 (bảng Tứ Hóa). LƯU Ý (22/10, từ repo lasotuvi +
    # lá app): 3 ô này từng ghi sai theo bảng phổ biến, đã sửa theo sách:
    # Mậu Khoa = Hữu Bật (không phải Thái Dương), Canh Khoa = Thái Âm
    # (không phải Thiên Phủ), Nhâm Khoa = Tả Phụ (không phải Thiên Phủ).
    # Lá lá mẫu (Nhâm) app ghi Khoa tại cung Tả Phụ, lá mẫu (Canh) app ghi
    # Khoa tại cung Thái Âm — đều khớp sách, xác nhận 2 sửa này.
    # RIÊNG Tân Quyền: sách Tân Biên §8.23 ghi Thiên Lương nhưng app lá mẫu
    # + repo + bảng phổ biến đều ghi Thái Dương — user CHỐT 22/10 giữ
    # Thái Dương theo app phổ biến (không theo sách ở ô này).
    "Giáp": ("Liêm Trinh", "Phá Quân", "Vũ Khúc", "Thái Dương"),
    "Ất": ("Thiên Cơ", "Thiên Lương", "Tử Vi", "Thái Âm"),
    "Bính": ("Thiên Đồng", "Thiên Cơ", "Văn Xương", "Liêm Trinh"),
    "Đinh": ("Thái Âm", "Thiên Đồng", "Thiên Cơ", "Cự Môn"),
    "Mậu": ("Tham Lang", "Thái Âm", "Hữu Bật", "Thiên Cơ"),
    "Kỷ": ("Vũ Khúc", "Tham Lang", "Thiên Lương", "Văn Khúc"),
    "Canh": ("Thái Dương", "Vũ Khúc", "Thái Âm", "Thiên Đồng"),
    "Tân": ("Cự Môn", "Thái Dương", "Văn Khúc", "Văn Xương"),
    "Nhâm": ("Thiên Lương", "Tử Vi", "Tả Phụ", "Vũ Khúc"),
    "Quý": ("Phá Quân", "Cự Môn", "Thái Âm", "Tham Lang"),
}  # thứ tự: Lộc, Quyền, Khoa, Kỵ

LOC_TON = {"Giáp": "Dần", "Ất": "Mão", "Bính": "Tỵ", "Đinh": "Ngọ",
           "Mậu": "Tỵ", "Kỷ": "Ngọ", "Canh": "Thân", "Tân": "Dậu",
           "Nhâm": "Hợi", "Quý": "Tý"}

TRIET = {"Giáp": ("Thân", "Dậu"), "Kỷ": ("Thân", "Dậu"),
         "Ất": ("Ngọ", "Mùi"), "Canh": ("Ngọ", "Mùi"),
         "Bính": ("Thìn", "Tỵ"), "Tân": ("Thìn", "Tỵ"),
         "Đinh": ("Dần", "Mão"), "Nhâm": ("Dần", "Mão"),
         "Mậu": ("Tý", "Sửu"), "Quý": ("Tý", "Sửu")}

TRUONG_SINH_START = {"Thủy": "Thân", "Mộc": "Hợi", "Kim": "Tỵ",
                      "Thổ": "Thân", "Hỏa": "Dần"}
TRUONG_SINH = ["Tràng Sinh", "Mộc Dục", "Quan Đới", "Lâm Quan", "Đế Vượng",
               "Suy", "Bệnh", "Tử", "Mộ", "Tuyệt", "Thai", "Dưỡng"]


def tuan_khong(year_stem, year_branch):
    """Tuần Không: tìm旬 chứa can chi năm; 2 chi không nằm trong旬
    là Tuần Không (Tam Hợp pdf 048-049)."""
    n = next(i for i in range(60)
             if CAN[i % 10] == year_stem and CHI[i % 12] == year_branch)
    tuan_start = n - (n % 10)  # can đầu旬 (Giáp ...)
    start_branch = tuan_start % 12
    covered = {(start_branch + i) % 12 for i in range(10)}
    return [CHI[b] for b in range(12) if b not in covered]


def build_chart(year_stem, year_branch, month, day, hour_branch,
                gender, tu_vi_override=None):
    menh, than = menh_than(month, hour_branch)
    menh_stem = palace_stem(menh, year_stem)
    cuc_table = cuc_from_table(menh, year_stem)
    cuc_napam = nap_am(menh_stem, menh)
    assert cuc_table == cuc_napam, f"Cục lệch: bảng {cuc_table} vs nạp âm {cuc_napam}"
    cuc = cuc_table
    cuc_num = CUC_NUM[cuc]

    # Âm dương: can năm Giáp/Bính/Mậu/Canh/Nhâm là dương, còn lại là âm
    am_duong = "Dương" if year_stem in ("Giáp", "Bính", "Mậu", "Canh", "Nhâm") else "Âm"
    # Đại hạn: Dương nam / Âm nữ thuận; Âm nam / Dương nữ nghịch
    thuan = (am_duong == "Dương" and gender == "nam") or \
            (am_duong == "Âm" and gender == "nữ")
    direction = 1 if thuan else -1
    menh_idx = CHI_IDX[menh]
    dai_van = {}
    for i in range(12):
        palace = CHI[(menh_idx + direction * i) % 12]
        dai_van[palace] = cuc_num + 10 * i

    # Tử Vi: ưu tiên bảng Tân Biên đã chép; fallback là công thức lasotuvi
    # (đã kiểm 150/150 với bảng). Công thức Tam Hợp cũ chỉ để tham khảo
    # vì đã biết sai ở Thổ ngày 9, Kim ngày 2/18, Mộc dư 2.
    tv_table = tu_vi_tan_bien_table(day, cuc)
    tv_formula = tu_vi_lasotuvi_formula(day, cuc_num)
    tu_vi = tu_vi_override or tv_table or tv_formula

    phu = thien_phu_from_tu_vi(tu_vi)
    stars = {}
    stars.update(tu_vi_system(tu_vi))
    stars.update(thien_phu_system(phu))

    loc, quyen, khoa, ky = TU_HOA[year_stem]
    tu_hoa = {"Hóa Lộc": loc, "Hóa Quyền": quyen, "Hóa Khoa": khoa, "Hóa Kỵ": ky}
    loc_ton = LOC_TON[year_stem]
    kinh = CHI[(CHI_IDX[loc_ton] + 1) % 12]
    da = CHI[(CHI_IDX[loc_ton] - 1) % 12]

    # Vòng Trường Sinh: khởi theo cục, thuận/nghịch theo âm dương + giới
    ts_start = CHI_IDX[TRUONG_SINH_START[cuc]]
    vong = {}
    for i, name in enumerate(TRUONG_SINH):
        vong[CHI[(ts_start + direction * i) % 12]] = name

    tuan = tuan_khong(year_stem, year_branch)
    triet = list(TRIET[year_stem])

    # Tên 12 cung từ Mệnh nghịch đếm
    cung_names = ["Mệnh", "Huynh Đệ", "Phu Thê", "Tử Nữ", "Tài Bạch",
                  "Tật Ách", "Thiên Di", "Nô Bộc", "Quan Lộc", "Điền Trạch",
                  "Phúc Đức", "Phụ Mẫu"]
    cung_of_branch = {}
    for i, name in enumerate(cung_names):
        cung_of_branch[CHI[(menh_idx - i) % 12]] = name
    lai_nhan, lai_nhan_branch = lai_nhan_cung(menh, year_stem)

    return {
        "menh": menh, "than": than, "menh_stem": menh_stem,
        "cuc": cuc, "cuc_num": cuc_num,
        "menh_nap_am": nap_am(menh_stem, menh),
        "nam_nap_am": nap_am(year_stem, year_branch),
        "menh_cuc_relation": menh_cuc_relation(
            nap_am(year_stem, year_branch), cuc),
        "lai_nhan": lai_nhan, "lai_nhan_branch": lai_nhan_branch,
        "am_duong": am_duong, "dai_van": dai_van,
        "tu_vi_table": tv_table, "tu_vi_formula": tv_formula,
        "tu_vi_used": tu_vi, "thien_phu": phu,
        "stars": stars, "tu_hoa": tu_hoa,
        "loc_ton": loc_ton, "kinh": kinh, "da": da,
        "vong": vong, "tuan": tuan, "triet": triet,
        "cung_of_branch": cung_of_branch,
        "chu_menh": CHU_MENH[year_branch],
        "chu_than": CHU_THAN[year_branch],
        "chu_than_tranh_cai": year_branch == "Hợi",
    }


def show(chart, title):
    print(f"===== {title} =====")
    print(f"Mệnh: {chart['menh_stem']}{chart['menh']} | Thân cư: {chart['than']} | "
          f"Cục: {chart['cuc']} {chart['cuc_num']} cục "
          f"(Mệnh nạp âm {chart['menh_nap_am']}, năm nạp âm {chart['nam_nap_am']}, "
          f"{chart['menh_cuc_relation']}) | "
          f"Lai nhân: {chart['lai_nhan']} ({chart['lai_nhan_branch']})")
    print(f"Tử Vi (bảng Tân Biên): {chart['tu_vi_table']} | "
          f"Tử Vi (công thức lasotuvi): {chart['tu_vi_formula']} | "
          f"Dùng: {chart['tu_vi_used']} | Thiên Phủ: {chart['thien_phu']}")
    print(f"Tứ Hóa: {chart['tu_hoa']} | Lộc Tồn: {chart['loc_ton']} | "
          f"Kình: {chart['kinh']} | Đà: {chart['da']} | "
          f"Tuần: {chart['tuan']} | Triệt: {chart['triet']}")
    tc = " (đang tranh cãi: Cơ theo bảng vs Tướng theo AItuvi/repo)" \
        if chart["chu_than_tranh_cai"] else ""
    print(f"Chủ mệnh: {chart['chu_menh']} | Chủ thân: {chart['chu_than']}{tc}")
    inv_stars = {}
    for s, b in chart["stars"].items():
        inv_stars.setdefault(b, []).append(s)
    for branch in CHI:
        cung = chart["cung_of_branch"].get(branch, "?")
        chinh = ", ".join(inv_stars.get(branch, ["(VCD)"]))
        extra = []
        if branch == chart["loc_ton"]:
            extra.append("Lộc Tồn")
        if branch == chart["kinh"]:
            extra.append("Kình Dương")
        if branch == chart["da"]:
            extra.append("Đà La")
        if branch in chart["tuan"]:
            extra.append("Tuần")
        if branch in chart["triet"]:
            extra.append("Triệt")
        print(f"  {cung} ({branch}): {chinh} | {chart['vong'][branch]} | "
              f"ĐV {chart['dai_van'][branch]} | {', '.join(extra)}")
    print()


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Lập lá số Tử Vi (mặc định: lá mẫu Quý Hợi 1983)")
    ap.add_argument("--solar", help="Ngày sinh dương lịch YYYY-MM-DD (đã xác nhận là dương lịch)")
    ap.add_argument("--time", default="00:00", help="Giờ sinh HH:MM")
    ap.add_argument("--gender", choices=["nam", "nữ"], default="nam")
    args = ap.parse_args()
    if args.solar:
        y, m, d = map(int, args.solar.split("-"))
        hh, mm = map(int, args.time.split(":"))
        ys, yb, lm, ld, day_gz = birth_lunar(y, m, d, hh)
        hb = hour_branch(hh, mm)
        print(f"Dương {args.solar} {args.time} -> âm {lm}/{ld} năm {ys}{yb}, "
              f"ngày {day_gz}, giờ {hb}")
        chart = build_chart(ys, yb, lm, ld, hb, args.gender)
        show(chart, f"LÁ SỐ (dương {args.solar} {args.time})")
        raise SystemExit(0)
    # Lá số mẫu: Quý Hợi 1983, tháng 8 âm lịch, ngày 10, giờ Tỵ, Âm nam
    # (ngày âm 10 = dương 16/9/1983; xem test_family_charts.py)
    book = build_chart("Quý", "Hợi", 8, 10, "Tỵ", "nam")
    show(book, "BẢN THEO SÁCH (Tử Vi từ bảng/công thức)")

    app = build_chart("Quý", "Hợi", 8, 16, "Tỵ", "nam", tu_vi_override="Mão")
    show(app, "BẢN GHIM TỬ VI TẠI MÃO (theo lá số mẫu)")

    # Đối chiếu bản ghim với lá số mẫu (chỉ các mục engine tính được)
    expected = {
        "Mệnh": ["Cự Môn"], "Huynh Đệ": ["Tử Vi", "Tham Lang"],
        "Phu Thê": ["Thái Âm", "Thiên Cơ"], "Tử Nữ": ["Thiên Phủ"],
        "Tài Bạch": ["Thái Dương"], "Tật Ách": ["Phá Quân", "Vũ Khúc"],
        "Thiên Di": ["Thiên Đồng"], "Nô Bộc": [], "Quan Lộc": [],
        "Điền Trạch": ["Liêm Trinh", "Thất Sát"], "Phúc Đức": ["Thiên Lương"],
        "Phụ Mẫu": ["Thiên Tướng"],
    }
    inv = {}
    for s, b in app["stars"].items():
        inv.setdefault(app["cung_of_branch"][b], []).append(s)
    print("===== ĐỐI CHIẾU BẢN GHIM vs LÁ SỐ MẪU (chính tinh) =====")
    ok = True
    for cung, exp in expected.items():
        got = sorted(inv.get(cung, []))
        match = sorted(exp) == got
        ok = ok and match
        print(f"  {'KHỚP' if match else 'LỆCH'} {cung}: mẫu {sorted(exp)} vs tính {got}")
    print(f"  Mệnh {app['menh']} (mẫu Thìn) | Thân {app['than']} (mẫu Dần) | "
          f"Cục {app['cuc']} (mẫu Thổ) | Tuần {app['tuan']} (mẫu Tý, Sửu) | "
          f"Triệt {app['triet']} (mẫu Tý, Sửu)")
    print(f"  Lộc Tồn {app['loc_ton']} (mẫu Tý) | Kình {app['kinh']} (mẫu Sửu) | "
          f"Đà {app['da']} (mẫu Hợi) | Tứ Hóa {app['tu_hoa']}")
    print("  => Bản ghim khớp 100% các mục kiểm tra được." if ok else
          "  => CÓ LỆCH, xem chi tiết trên.")
