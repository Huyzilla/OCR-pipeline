# Page 0

## [0] Picture

<!-- EMPTY_BLOCK -->

## [1] SectionHeader

<!-- EMPTY_BLOCK -->

## [2] SectionHeader

QUY ĐỊNH YÊU CẦU KỸ THUẬT ĐỐI VỚI PHẦN MỀM KÝ SỐ, PHẦN MỀM KIỂM TRA CHỮ KÝ
SỐ VÀ CỔNG KẾT NỐI DỊCH VỤ CHỨNG THỰC CHỮ KÝ SỐ CÔNG CỘNG Lần ban hành: 1

## [3] Text

<!-- EMPTY_BLOCK -->

## [4] SectionHeader

1.1 Phạm vi điều chỉnh
Thông tư này quy định các nội dung sau:

## [5] SectionHeader

1. Yêu cầu kỹ thuật đối với phần mềm ký số, phần mềm kiểm tra chữ ký số theo quy định tại Điều 17, Nghị định số 23/2025/NĐ-CP ngày
21 tháng 02 năm 2025 của Chính phủ quy định về chữ ký điện tử và dịch vụ tin cậy.

## [6] Text

2. Hướng dẫn kết nối đến Cổng kết nối dịch vụ chứng thực chữ ký số công cộng do Bộ Khoa học và Công nghệ xây dựng theo quy định tại

## [7] ListItem

Điều 44, Nghị định số 23/2025/NĐ-CP ngày 21 tháng 02 năm 2025 của Chính phủ quy định về chữ ký điện tử và dịch vụ tin cậy.
1.2 Đối tượng áp dụng

## [8] ListItem

Thông tư này áp dụng:
1. Tổ chức, cá nhân sử dụng phần mềm ký số, phần mềm kiểm tra chữ ký số; các tổ chức, cá nhân phát triển phần mềm ký số, phần mềm
kiểm tra chữ ký số; các Tổ chức cung cấp dịch vụ chứng thực chữ ký số khi phát triển, sử dụng phần mềm ký số, phần mềm kiểm tra chữ

## [9] SectionHeader

ký số.
2. Các Tổ chức cung cấp dịch vụ chứng thực chữ ký số; các Tổ chức cung cấp dịch vụ chứng thực chữ ký điện tử nước ngoài được công

## [10] Text

nhận tại Việt Nam; chủ quản các hệ thống thông tin phục vụ giao dịch điện tử có sử dụng chữ ký số khi kết nối đến Cổng kết nối dịch vụ

## [11] ListItem

chứng thực chữ ký số công cộng.
3. Các tổ chức, cá nhân có liên quan khác.
1.3 Giải thích từ ngữ
Trong Thông tư này, các từ ngữ dưới đây được hiểu như sau:

## [12] ListItem

1. “Cặp khóa không đối xứng” là khóa công khai và khóa bí mật tương ứng.
2. “Khóa bí mật” là thành phần của cặp khóa không đối xứng được sử dụng để ký thông điệp dữ liệu.
3. “Khóa công khai” là thành phần của cặp khóa không đối xứng được sử dụng để xác thực chữ ký số trên thông điệp dữ liệu.

## [13] ListItem

<!-- EMPTY_BLOCK -->

## [14] SectionHeader

<!-- EMPTY_BLOCK -->

## [15] Text

<!-- EMPTY_BLOCK -->

## [16] ListItem

<!-- EMPTY_BLOCK -->

## [17] ListItem

<!-- EMPTY_BLOCK -->

## [18] ListItem

<!-- EMPTY_BLOCK -->

## [19] PageFooter

<!-- EMPTY_BLOCK -->

---

# Page 1

## [0] Picture

<!-- EMPTY_BLOCK -->

## [1] SectionHeader

<!-- EMPTY_BLOCK -->

## [2] SectionHeader

QUY ĐỊNH YÊU CẦU KỸ THUẬT ĐỐI VỚI PHẦN MỀM KÝ SỐ, PHẦN MỀM KIỂM TRA CHỮ KÝ
SỐ VÀ CỔNG KẾT NỐI DỊCH VỤ CHỨNG THỰC CHỮ KÝ SỐ CÔNG CỘNG Lần ban hành: 1
4. “Hàm băm” là một thuật toán chuyển đổi thông điệp dữ liệu đầu vào thành một chuỗi có độ dài cố định, gọi là mã băm. Hàm băm được

## [3] Text

<!-- EMPTY_BLOCK -->

## [4] ListItem

5. “Chủ thể ký” là cá nhân hoặc tổ chức sở hữu chứng thư chữ ký số và sử dụng khóa bí mật tương ứng để thực hiện ký số trên thông điệp
dữ liệu.

## [5] ListItem

6. “Chứng thư chữ ký số” là một dạng chứng thư chữ ký điện tử do Tổ chức cung cấp dịch vụ chứng thực chữ ký số cấp nhằm cung cấp
thông tin về khóa công khai của một cá nhân, tổ chức từ đó xác nhận cá nhân, tổ chức là chủ thể ký thông qua việc sử dụng khóa bí mật
tương ứng.

## [6] ListItem

7. “Phần mềm ký số” là chương trình độc lập hoặc một thành phần (module) phần mềm hoặc giải pháp có chức năng ký số vào thông điệp
dữ liệu.
8. “Phần mềm kiểm tra chữ ký số” là chương trình độc lập hoặc một thành phần (module) phần mềm hoặc giải pháp có chức năng kiểm tra
tính hợp lệ của chữ ký số trên thông điệp dữ liệu đã ký. 10. “Đường dẫn tin cậy của chứng thư chữ ký số” là danh sách có thứ tự các chứng

## [7] ListItem

thư chữ ký số, bao gồm chứng thư chữ ký số của thuê bao, chứng thư chữ ký số của các Tổ chức cung cấp dịch vụ chứng thực chữ ký số và
chứng thư chữ ký số gốc tin cậy nhằm xác minh nguồn gốc của chứng thư chữ ký số.

## [8] ListItem

2. Yêu cầu kỹ thuật đối với chức năng phần mềm ký số, phần mềm kiểm tra chữ ký số
2.1 Yêu cầu chung
Tuân thủ các yêu cầu và tiêu chuẩn kỹ thuật về chữ ký số trên thông điệp dữ liệu dùng cho phần mềm ký số và phần mềm kiểm tra chữ ký
số tại Phụ lục I ban hành kèm theo Thông tư này.

## [9] SectionHeader

Chức năng xác thực chủ thể ký và ký số
a) Kiểm tra được thông tin chủ thể ký trên chứng thư chữ ký số và kiểm tra hiệu lực chứng thư chữ ký số theo quy định tại khoản 2 Điều

## [10] SectionHeader

này trước khi cho phép thực hiện ký số;

## [11] Text

2

## [12] SectionHeader

<!-- EMPTY_BLOCK -->

## [13] SectionHeader

<!-- EMPTY_BLOCK -->

## [14] Text

<!-- EMPTY_BLOCK -->

## [15] PageFooter

<!-- EMPTY_BLOCK -->

---

# Page 2

## [0] Picture

<!-- EMPTY_BLOCK -->

## [1] SectionHeader

<!-- EMPTY_BLOCK -->

## [2] SectionHeader

QUY ĐỊNH YÊU CẦU KỸ THUẬT ĐỐI VỚI PHẦN MỀM KÝ SỐ, PHẦN MỀM KIỂM TRA CHỮ KÝ
SỐ VÀ CỔNG KẾT NỐI DỊCH VỤ CHỨNG THỰC CHỮ KÝ SỐ CÔNG CỘNG Lần ban hành: 1
b) Cho phép chủ thể ký sử dụng khóa bí mật để thực hiện việc ký số vào thông điệp dữ liệu. Khoá bí mật lưu trong phương tiện lưu khóa bí

## [3] Text

<!-- EMPTY_BLOCK -->

## [4] ListItem

ký số trên thông điệp dữ liệu dùng cho phần mềm ký số và phần mềm kiểm tra chữ ký số tại Phụ lục I ban hành kèm theo Thông tư này;
c) Cho phép chuyển đổi định dạng thông điệp dữ liệu thành các định dạng theo tiêu chuẩn khuyến nghị áp dụng cho phần mềm ký số, phần
mềm kiểm tra chữ ký số tại Phụ lục I ban hành kèm theo Thông tư này;
d) Cho phép gắn kèm chữ ký số, chứng thư chữ ký số và thời điểm ký số vào thông điệp dữ liệu sau khi ký số;

## [5] ListItem

đ) Hỗ trợ cài đặt, tích hợp, cập nhật chứng thư chữ ký số của Trung tâm Chứng thực điện tử quốc gia, các Tổ chức cung cấp dịch vụ chứng
thực chữ ký số công cộng và chứng thư chữ ký số thuộc Danh sách tin cậy chứng thư chữ ký điện tử nước ngoài được công nhận tại Việt

## [6] ListItem

Nam;
e) Cho phép gắn dấu thời gian tương ứng với chữ ký số trên thông điệp dữ liệu trong trường hợp pháp luật quy định thông điệp dữ liệu cần

## [7] ListItem

có dấu thời gian;
g) Đảm bảo tính toàn vẹn của thông điệp dữ liệu đã ký.
Chức năng kiểm tra hiệu lực của chứng thư chữ ký số

## [8] ListItem

a) Xác thực được thông tin trong chứng thư chữ ký số theo quy định pháp luật về định danh và xác thực điện tử;
b) Kiểm tra được chứng thư chữ ký số của chủ thể ký theo đường dẫn tin cậy của chứng thư chữ ký số đó hoặc theo Danh sách tin cậy
chứng thư chữ ký điện tử nước ngoài được công nhận tại Việt Nam. Đường dẫn tin cậy phải có liên kết đến chứng thư chữ ký số gốc của

## [9] ListItem

Trung tâm Chứng thực điện tử quốc gia;

## [10] SectionHeader

Chức năng kết nối đến Cổng kết nối dịch vụ chứng thực chữ ký số công cộng

## [11] ListItem

a) Phát triển các thành phần, chương trình hoặc giải pháp phục vụ kết nối đến Cổng kết nối dịch vụ chứng thực chữ ký số công cộng;

## [12] ListItem

b) Tuân thủ Hướng dẫn kết nối đến Cổng kết nối dịch vụ chứng thực chữ ký số công cộng do Bộ Khoa học và Công nghệ xây dựng được
quy định tại Điều 8 Thông tư này.
3

## [13] ListItem

<!-- EMPTY_BLOCK -->

## [14] SectionHeader

<!-- EMPTY_BLOCK -->

## [15] ListItem

<!-- EMPTY_BLOCK -->

## [16] ListItem

<!-- EMPTY_BLOCK -->

## [17] PageFooter

<!-- EMPTY_BLOCK -->

---
