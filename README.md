# Phần mềm phòng khám Simple Clinic
- Tác giả: BS Vương Kiến Thanh  
- Email: thanhstardust@outlook.com

Phần mềm by doctor for doctor, thích hợp cho mô hình phòng khám nhỏ.

## Chức năng:
- Quản lý bệnh nhân và các lượt khám
- Xem được các lượt khám cũ
- Quản lý kho thuốc
- Quản lý thủ thuật đơn giản
- In toa thuốc (có hoặc không kèm giá tiền)
- Toa mẫu
- Dùng lại toa cũ
- Copy thông tin lượt khám dạng text (dùng để đưa qua tin nhắn)
- Báo cáo doanh thu theo ngày, tháng
- Báo cáo chi tiết thuốc dùng trong tháng
- Dùng database SQLite gọn nhẹ
- Tùy chọn màu màn hình chính
- Tương thích với Windows, Macos, Linux
- Chỉ dùng được trên 1 máy, không có chức năng server

## Download demo
https://github.com/vuongkienthanh/simpleclinic/releases/latest

## Hướng dẫn cài đặt / yêu cầu chức năng

- Download Python 3.10
- Download python-poetry
- Download repo này

```sh
poetry env use python3.10
poetry install
```

---

## Hướng dẫn sử dụng
 
Run app
```sh
poetry run python -OO main.py
```

Shortcuts to run app for each platform are available at `shortcuts` folder.

Config and database are located at:
- Windows: `%USERPROFILE%\.simpleclinic\`
- MacOS/Linux: `$HOME/.simpleclinic/`
