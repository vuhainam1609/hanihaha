# -*- coding: utf-8 -*-
"""W1 — vòng Lộc Tồn, vòng Thái Tuế, Địa Không / Địa Kiếp.

Pure Python, KHÔNG import lap-la-so.py. Input là dict theo đúng spec
của brief W1; chỉ dùng các key: year_branch, hour_branch,
loc_ton_branch, direction. Các key còn lại của inp được nhận nhưng
không dùng (ghi rõ để caller khỏi nhầm là thiếu input).

Quy luật (đã kiểm chứng trên 10 lá mẫu, xem RULES.md):
- Vòng Lộc Tồn: Bác Sĩ ở cùng cung Lộc Tồn, rồi đi theo chiều
  `direction` (+1 thuận / -1 nghịch, tức Dương nam & Âm nữ thuận,
  còn lại nghịch — đúng quy tắc repo dùng cho vòng này):
  Lực Sĩ, Thanh Long, Tiểu Hao, Tướng Quân, Tấu Thư, Phi Liêm,
  Hỷ Thần, Bệnh Phù, Đại Hao, Phục Binh, Quan Phủ.
- Vòng Thái Tuế: luôn đi THUẬN từ chi năm, bất kể giới tính:
  Thái Tuế, Thiếu Dương, Tang Môn, Thiếu Âm, Quan Phù, Tử Phù,
  Tuế Phá, Long Đức, Bạch Hổ, Phúc Đức, Điếu Khách, Trực Phù.
- Địa Kiếp: khởi giờ Tý ở Hợi, đếm THUẬN đến giờ sinh.
  Địa Không: khởi giờ Tý ở Hợi, đếm NGHỊCH đến giờ sinh.
  (Với giờ Tý và giờ Ngọ, hai sao trùng cung — xem RULES.md về
  trường hợp nguyen, mẫu chỉ ghi Địa Không; ở đây vẫn trả cả hai
  theo đúng công thức repo vì chỉ có 1 bằng chứng, chưa đủ để
  kết luận app bỏ Kiếp khi trùng cung.)

KHÔNG trả về: Lộc Tồn, Kình Dương, Đà La — ba sao này thuộc
engine lõi (lap-la-so.py) và chỉ được XÁC NHẬN khớp mẫu trong
RULES.md, không code lại ở đây.

Tên sao trả về dùng dạng CHUẨN: "Bác Sĩ", "Lực Sĩ", "Điếu Khách".
Biến thể trong mẫu (Bác Sỹ, Lực Sỹ, Điều Khách, Bach Hổ) được
ghi trong RULES.md, không trả về.
QUAN PHỦ vs QUAN PHÙ LÀ 2 SAO RIÊNG (quyết 25/10, user xác nhận
thủ công lá TVN Nhâm 1992): vòng Lộc Tồn kết bằng "Quan Phủ",
vòng Thái Tuế có "Quan Phù" (Tân Biên §8.3/§8.4, §3.60/§3.73;
pattern đa số mẫu: Lộc = Phủ, Thái = Phù, khớp TVN lá Quý/Hợi).
Nếu hai vòng trùng cung (vd lá mẫu, lá test Nhâm 1992), cả hai
tên đều ghi tại cung đó — KHÔNG gộp, KHÔNG dedup chéo tên.
"""

CHI = ["Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
       "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi"]
_CHI_IDX = {c: i for i, c in enumerate(CHI)}

# Bác Sĩ ở bước 0 (cùng cung Lộc Tồn), các sao sau cách 1..11 cung.
LOC_RING = ["Bác Sĩ", "Lực Sĩ", "Thanh Long", "Tiểu Hao",
            "Tướng Quân", "Tấu Thư", "Phi Liêm", "Hỷ Thần",
            "Bệnh Phù", "Đại Hao", "Phục Binh", "Quan Phủ"]

# Thái Tuế ở bước 0 (cùng chi năm), các sao sau cách 1..11 cung thuận.
# Bước 4 là "Quan Phù" — KHÁC sao "Quan Phủ" cuối vòng Lộc Tồn.
THAI_RING = ["Thái Tuế", "Thiếu Dương", "Tang Môn", "Thiếu Âm",
             "Quan Phù", "Tử Phù", "Tuế Phá", "Long Đức",
             "Bạch Hổ", "Phúc Đức", "Điếu Khách", "Trực Phù"]


def _idx(branch):
    try:
        return _CHI_IDX[branch]
    except KeyError:
        raise ValueError("chi không hợp lệ: %r" % (branch,))


def _put(out, branch, star):
    stars = out.setdefault(branch, [])
    if star not in stars:
        stars.append(star)


def stars_for(inp):
    """Trả về dict {tên chi: [tên sao]} cho các hệ W1.

    inp cần có: year_branch, hour_branch, loc_ton_branch, direction
    (+1 thuận / -1 nghịch). Các key khác trong spec W1 được chấp
    nhận nhưng không ảnh hưởng các hệ này.
    """
    direction = inp.get("direction")
    if direction is None:
        # Fallback khi caller không đưa direction: suy từ âm/dương
        # can năm + giới tính (quy tắc của engine lõi).
        am_duong = inp.get("am_duong")
        gender = inp.get("gender")
        thuan = (am_duong == "Dương" and gender == "nam") or \
            (am_duong == "Âm" and gender == "nữ")
        direction = 1 if thuan else -1
    if direction not in (1, -1):
        raise ValueError("direction phải là +1 hoặc -1, nhận: %r"
                         % (direction,))

    out = {}

    # 1. Vòng Lộc Tồn — theo chiều direction.
    loc = _idx(inp["loc_ton_branch"])
    for step, star in enumerate(LOC_RING):
        _put(out, CHI[(loc + direction * step) % 12], star)

    # 2. Vòng Thái Tuế — luôn thuận từ chi năm.
    thai = _idx(inp["year_branch"])
    for step, star in enumerate(THAI_RING):
        _put(out, CHI[(thai + step) % 12], star)

    # 3. Địa Không / Địa Kiếp — khởi Hợi (chỉ số 11).
    hour = _idx(inp["hour_branch"])
    _put(out, CHI[(11 + hour) % 12], "Địa Kiếp")   # thuận
    _put(out, CHI[(11 - hour) % 12], "Địa Không")  # nghịch

    return out
