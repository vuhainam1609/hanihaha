# -*- coding: utf-8 -*-
"""Port nhóm W3b (sát tinh / phụ tinh) từ repo lasotuvi sang pure Python.

KHÔNG import lap-la-so. Chỉ có một hàm công khai: stars_for(inp).

Quy ước chỉ số chi (khớp engine lõi): Tý=0, Sửu=1, Dần=2, Mão=3,
Thìn=4, Tỵ=5, Ngọ=6, Mùi=7, Thân=8, Dậu=9, Tuất=10, Hợi=11.

inp là dict với các key (theo brief giao việc):
  year_stem, year_branch, month, day, hour_branch, gender,
  menh_branch, than_branch, cuc, cuc_num, tu_vi_branch,
  thien_phu_branch, loc_ton_branch, kinh_branch, da_branch,
  vong, dai_van, cung_of_branch, tu_hoa, tuan, triet, direction, am_duong.
Trong các key đó, W3b chỉ dùng thật sự 3 key:
  year_branch (tên chi, vd "Hợi", hoặc chỉ số 0-11),
  month (tháng ÂM lịch, số 1-12),
  day (ngày ÂM lịch, số 1-30).
Các key còn lại được chấp nhận nhưng không dùng (các hệ W3b không
phụ thuộc can năm, giờ sinh, giới tính, Mệnh/Thân, Cục, Tử Vi...).
LƯU Ý: month/day PHẢI là âm lịch. Đưa dương lịch vào sẽ ra sai.

Trả về dict {tên chi: [tên sao]} — chỉ gồm các chi có sao, mỗi chi
liệt kê các sao theo đúng thứ tự hệ trong brief (Phượng Các, Giải
Thần, Hoa Cái, Thiên Hỷ, Thiên Đức, Nguyệt Đức, Kiếp Sát, Thiên
Diêu, Thiên Hình, Thiên Khốc, Thiên Hư, Thiên Không, Bát Tọa,
Tam Thai, Quả Tú). Sao nào chưa đủ bằng chứng thì KHÔNG có mặt
trong dict (xem RULES.md — nhóm W3b hiện không có sao nào như vậy;
2 trường hợp mẫu thiếu hẳn 1 sao được ghi rõ trong RULES.md).
Tên sao dùng đúng tên trong lá mẫu: "Thiên Diêu" (repo ghi
"Thiên riêu"), "Thiên Hỷ" (8/10 lá mẫu ghi biến thể "Thiên Hỉ").
"""

CHI = ("Tý", "Sửu", "Dần", "Mão", "Thìn", "Tỵ",
       "Ngọ", "Mùi", "Thân", "Dậu", "Tuất", "Hợi")


def stars_for(inp):
    # --- Chuẩn hoá đầu vào (tên chi hoặc chỉ số đều được) ---
    yb = inp["year_branch"]
    if isinstance(yb, int):
        chi_nam = yb % 12
    else:
        chi_nam = CHI.index(str(yb).strip())
    month = int(inp["month"])   # tháng âm lịch 1-12
    day = int(inp["day"])       # ngày âm lịch 1-30

    # --- Các vị trí trung gian (đều tính theo chi năm / tháng / ngày) ---
    # Long Trì: repo dichCung(5, chiNam-1) ở hệ 1-12  ->  (chi+4) ở hệ 0-11.
    long_tri = (chi_nam + 4) % 12
    # Phượng Các: đối xứng Long Trì qua trục Sửu-Mùi, repo
    # dichCung(2, 2-LongTrì)  ->  (2-LongTrì) ở hệ 0-11. Giải Thần
    # trong repo an CÙNG cung với Phượng Các (một lệnh nhapSao).
    phuong_cac = (2 - long_tri) % 12
    giai_than = phuong_cac
    # Thiên Mã theo tam hợp của chi năm:
    #   Dần-Ngọ-Tuất -> Thân; Hợi-Mão-Mùi -> Tỵ;
    #   Thân-Tý-Thìn -> Dần; Tỵ-Dậu-Sửu -> Hợi.
    if chi_nam in (2, 6, 10):
        thien_ma = 8    # Thân
    elif chi_nam in (11, 3, 7):
        thien_ma = 5    # Tỵ
    elif chi_nam in (8, 0, 4):
        thien_ma = 2    # Dần
    else:
        thien_ma = 11   # Hợi
    hoa_cai = (thien_ma + 2) % 12
    kiep_sat = (thien_ma + 3) % 12
    # Hồng Loan: repo dichCung(4, -chiNam+1) ở hệ 1-12
    #   -> (3-chi_nam) ở hệ 0-11; Thiên Hỷ đối cung Hồng Loan (+6).
    hong_loan = (3 - chi_nam) % 12
    thien_hy = (hong_loan + 6) % 12
    # Thiên Đức / Nguyệt Đức: vòng Thái Tuế (Thái Tuế = chi năm),
    # repo an Nguyệt Đức cùng Tử Phù (Thái Tuế+5), Thiên Đức cùng
    # Phúc Đức (Thái Tuế+9). KHÔNG phải theo tháng sinh (xem RULES.md).
    thien_duc = (chi_nam + 9) % 12
    nguyet_duc = (chi_nam + 5) % 12
    # Thiên Hình: repo dichCung(10, tháng-1) ở hệ 1-12
    #   -> (tháng+8) ở hệ 0-11; Thiên Diêu = Thiên Hình + 4.
    thien_hinh = (month + 8) % 12
    thien_dieu = (thien_hinh + 4) % 12
    # Thiên Khốc / Thiên Hư: khởi Ngọ, repo Khốc dichCung(7, -chiNam+1),
    # Hư dichCung(7, chiNam-1) ở hệ 1-12
    #   -> Khốc (6-chi_nam), Hư (6+chi_nam) ở hệ 0-11.
    thien_khoc = (6 - chi_nam) % 12
    thien_hu = (6 + chi_nam) % 12
    # Thiên Không: repo an CÙNG cung Thiếu Dương = Thái Tuế + 1.
    thien_khong = (chi_nam + 1) % 12
    # Tam Thai: repo dichCung(5, tháng+ngày-2) ở hệ 1-12
    #   -> (tháng+ngày+2) ở hệ 0-11; Bát Tọa đối xứng Tam Thai qua
    # trục Sửu-Mùi, repo dichCung(2, 2-TamThai) -> (2-TamThai).
    tam_thai = (month + day + 2) % 12
    bat_toa = (2 - tam_thai) % 12
    # Cô Thần theo chi năm (làm trung gian cho Quả Tú, Cô Thần tự
    # thân không thuộc nhóm W3b nên không đưa vào dict):
    #   Hợi-Tý-Sửu -> Dần; Dần-Mão-Thìn -> Tỵ;
    #   Tỵ-Ngọ-Mùi -> Thân; Thân-Dậu-Tuất -> Hợi.
    if chi_nam in (11, 0, 1):
        co_than = 2     # Dần
    elif chi_nam in (2, 3, 4):
        co_than = 5     # Tỵ
    elif chi_nam in (5, 6, 7):
        co_than = 8     # Thân
    else:
        co_than = 11    # Hợi
    qua_tu = (co_than - 4) % 12

    out = {}
    for branch, star in (
        (phuong_cac, "Phượng Các"),
        (giai_than, "Giải Thần"),
        (hoa_cai, "Hoa Cái"),
        (thien_hy, "Thiên Hỷ"),
        (thien_duc, "Thiên Đức"),
        (nguyet_duc, "Nguyệt Đức"),
        (kiep_sat, "Kiếp Sát"),
        (thien_dieu, "Thiên Diêu"),
        (thien_hinh, "Thiên Hình"),
        (thien_khoc, "Thiên Khốc"),
        (thien_hu, "Thiên Hư"),
        (thien_khong, "Thiên Không"),
        (bat_toa, "Bát Tọa"),
        (tam_thai, "Tam Thai"),
        (qua_tu, "Quả Tú"),
    ):
        out.setdefault(CHI[branch], []).append(star)
    return out
