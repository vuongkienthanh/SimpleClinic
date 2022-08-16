# Phần mềm phòng khám tại nhà
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
- Dùng database SQLite gọn nhẹ
- Tương thích với Windows, Macos, Linux
- Chỉ dùng được trên 1 máy, không có chức năng server

## Download demo
https://github.com/vuongkienthanh/pmpktn2/releases/download/V2.1/demo.exe

## Hướng dẫn cài đặt / yêu cầu chức năng
Làm theo hướng dẫn phía dưới hoặc liên hệ hỗ trợ qua Email: thanhstardust@outlook.com

## Cài đặt:
<details> <summary>Windows</summary>

### Install `python`
Download **python3.10** at https://www.python.org/downloads/ and install it

### Install `poetry`
Open power shell
```powershell
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
```
Check installed version
```sh
poetry --version # poetry 1.1.13
```

### Download this repo
Initialize the poetry env
```sh
poetry env use python3.10
poetry install --no-dev
```
</details>

<details> <summary>Mac OS</summary>

### Install `python`
Download **python3.10** at https://www.python.org/downloads/ and install it

### Install `poetry`
```sh
curl -sSL https://install.python-poetry.org | python3 -
```
Check installed version
```sh
poetry --version # poetry 1.1.13
```

### Download this repo
Initialize the poetry env
```sh
poetry env use python3.10
poetry install --no-dev
```
</details>

<details> <summary>Linux (Ubuntu, Debian based)</summary>

### Download source code and build `python`
As of writing, there is no available python3.10 executable.  
You have to compile it yourself.  
Download **python3.10** source code at https://www.python.org/downloads/

Install dependencies
```sh
sudo apt install -y build-essential gdb lcov pkg-config \
      libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev \
      libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev \
      lzma lzma-dev tk-dev uuid-dev zlib1g-dev python3-venv\
      libgtk-3-0 libgtk-3-bin libgtk-3-common libgtk-3-dev \
      libgstreamer1.0-dev libgstreamer-plugins-base1.0-0 \
      libgstreamer-plugins-base1.0-dev freeglut3 freeglut3-dev \
      python3-dev libsdl-dev libtiff-dev libpng-dev \
      liblzma-dev libjpeg-dev libwebkit2gtk-4.0-dev libsdl2-dev
```

Extract `python` source code and install in `/opt/python310`
```sh
sudo mkdir /opt/python310
./configure --enable-loadable-sqlite-extensions --enable-optimizations --enable-shared --prefix=/opt/python310 LDFLAGS="-Wl,-rpath=/opt/python310/lib"
make
sudo make altinstall
echo "export PATH=/opt/python310/bin:\$PATH" | tee -a ~/.profile
echo "export PATH=/opt/python310/bin:\$PATH" | tee -a ~/.bashrc
```

### Install `poetry`
```sh
curl -sSL https://install.python-poetry.org | python3 -
```
Check installed version
```sh
poetry --version # poetry 1.1.13
```

### Download this repo
Initialize the poetry env
```sh
poetry env use python3.10
poetry install --no-dev
```
</details>

---

## Hướng dẫn sử dụng
 
Run app
```sh
poetry run python -OO main.py
```

Shortcuts to run app for each platform are available at `shortcuts` folder.

Config and database are located at:
- Windows: `%USERPROFILE%\.pmpktn\`
- MacOS/Linux: `$HOME/.pmpktn/`

---

## Default configuration

```sh
{
  // Tên phòng khám, được in trong toa
  "clinic_name": "Phòng khám chuyên khoa nhi - Bs xxxx yyyyy zzzz",
  // Tên bác sĩ, được in trong toa
  "doctor_name": "Bs xxxx yyyyy zzzz aaa",
  // Địa chỉ, được in trong toa
  "clinic_address": "Qui laboriosam corporis non quasi maiores velit culpa",
  // Số điện thoại, được in trong toa
  "clinic_phone_number": "0909.222.111",
  // Tiền công khám bệnh
  "initial_price": 50000,
  // Số ngày toa về mặc định cho toa thuốc
  "default_days_for_prescription": 2,
  // Lượng thuốc tối thiểu để báo động trong danh sách thuốc
  "minimum_drug_quantity_alert": 20,
  // Đơn vị thuốc bán một đơn vị
  "single_sale_units": [
    "chai",
    "lọ",
    "týp"
  ],
  // Lời dặn dò mở rộng khi in toa
  "follow_choices": {
    "Dấu hiệu chung": "Khám lại khi trẻ có những dấu hiệu sau: co giật, ngủ li bì hay vật vã, bứt rứt, thở mệt, nôn ói nhiều, sốt cao liên tục, tiêu máu",
    "Dấu hiệu nặng TCM": "Sốt cao ≥39 độ C hay sốt liên tục trên 2 ngày - Giật mình, chới với, hốt hoảng bất thường - Ngủ gà, li bì hay bứt rứt - Run giật tay chân bất thường - Yếu tay chân, ngồi không vững, đi đứng loạng choạng - Thở bất thường: không đều, thở nhanh - Nuốt sặc, thay đổi giọng nói",
    "Dấu hiệu nặng SXH": "Lừ đừ, bứt rứt - Lạnh tay chân khi trẻ đã hết sốt (thường vào ngày thứ 4, thứ 5 của bệnh) - Đau bụng - Ói nhiều - Chảy máu bất thường: Chảy máu răng, máu mũi, đi cầu phân đen, ói ra máu"
  },
  // Hiển thị giá tiền trên toa thuốc
  "print_price": true,
  // Số lượng thuốc tối đa trong một tờ giấy toa thuốc
  "number_of_drugs_ine_one_page": 8,
  // Số lượt khám gần nhất được hiển thị; -1 là hiển thị hết
  "display_recent_visit_count": -1,
  // Tùy vào hệ điều hành, máy in, toa thuốc bị thu nhỏ hay phóng toa
  // Phải chỉnh lại qua print_scale, preview_scale
  "print_scale": 1,
  "preview_scale": 1,
  // Phóng to khi mở app
  "maximize_at_start": false,
  // Khi font chữ hệ thống được phóng to trong Accessibility > Text Size
  // Phải chỉnh lại độ dài các thanh header của app
  "listctrl_header_scale": 1,
  // Tùy chỉnh màu sắc
  "background_color":{
    "mainview": [ 206, 219, 186 ], // Nền chính của app
    "patient_list": [ 255, 255, 255 ], // Danh sách bệnh nhân
    "visit_list": [ 255, 255, 255 ], // Danh sách các lượt khám
    "name": [ 200, 200, 200 ], // Tên
    "gender": [ 200, 200, 200 ], // Giới tính
    "birthdate": [ 200, 200, 200 ], // Ngày sinh
    "age": [ 200, 200, 200 ], // Tuổi
    "address": [ 200, 200, 200 ], // Địa chỉ
    "phone": [ 200, 200, 200 ], // Điện thoại
    "diagnosis": [ 255, 255, 255 ], // Chẩn đoán
    "price": [ 255, 255, 255 ], // Giá tiền
    "drug_list": [ 255, 255, 255 ], // Danh sách thuốc
    "procedure_list": [ 255, 255, 255 ], // Danh sách thủ thuật
    "past_history": [ 255, 255, 255 ], // Tiền căn
    "visit_note": [ 255, 255, 255 ], // Bệnh sử
    "weight": [ 255, 255, 255 ], // Cân năng
    "days": [ 255, 255, 255 ], // Số ngày cho toa về
    "drug_picker": [ 255, 255, 255 ], // Danh mục chọn thuốc
    "drug_times": [ 255, 255, 255 ], // Số lần dùng của thuốc
    "drug_dose": [ 255, 255, 255 ], // Liều thuốc
    "drug_quantity": [ 255, 255, 255 ], // Số lượng thuốc
    "drug_note": [ 255, 255, 255 ], // Cách dùng thuốc
    "recheck": [ 255, 255, 255 ], // Số ngày tái khám
    "follow": [ 255, 255, 255 ], // Lời dặn dò
    "procedure_picker": [ 255, 255, 255 ] // Danh mục chọn thủ thuật
  }
}
```
