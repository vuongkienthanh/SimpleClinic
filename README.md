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
https://github.com/vuongkienthanh/pmpktn2/releases/download/V2.0/demo.exe

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
      libbz2-dev libffi-dev libgdbm-dev libgdbm-compat-dev liblzma-dev \
      libncurses5-dev libreadline6-dev libsqlite3-dev libssl-dev \
      lzma lzma-dev tk-dev uuid-dev zlib1g-dev python3-venv\
      libgtk-3-0 libgtk-3-bin libgtk-3-common libgtk-3-dev \
      libgstreamer1.0-dev libgstreamer-plugins-base1.0-0 \
      libgstreamer-plugins-base1.0-dev freeglut3 freeglut3-dev \
      python3-dev libsdl-dev libtiff-dev libpng-dev \
      libjpeg-dev python-is-python3
```

Extract `python` source code and install in `/opt/python310`
```sh
./configure \
  --enable-loadable-sqlite-extensions \
  --enable-optimizations \
  --enable-shared \ 
  --prefix=/opt/python310 \
  LDFLAGS="-Wl,-rpath=/opt/python310/lib"
make
sudo make altinstall
echo "export PATH=/opt/python310/bin:\$PATH" | tee -a ~/.profile
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

Run app
```sh
poetry run python -OO main.py
```

Shortcuts to run app for each platform are available at `shortcuts` folder.
