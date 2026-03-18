![](_page_0_Picture_0.jpeg)

#### **1. Quy định chung**

## **1.1 Phạm vi điều chỉnh**

Thông tư này quy định các nội dung sau:

- 1. Yêu cầu kỹ thuật đối với phần mềm ký số, phần mềm kiểm tra chữ ký số theo quy định tại Điều 17, Nghị định số 23/2025/NĐ-CP ngày 21 tháng 02 năm 2025 của Chính phủ quy định về chữ ký điện tử và dịch vụ tin cậy.
- 2. Hướng dẫn kết nối đến Cổng kết nối dịch vụ chứng thực chữ ký số công cộng do Bộ Khoa học và Công nghệ xây dựng theo quy định tại Điều 44, Nghị định số 23/2025/NĐ-CP ngày 21 tháng 02 năm 2025 của Chính phủ quy định về chữ ký điện tử và dịch vụ tin cậy.

## **1.2 Đối tượng áp dụng**

Thông tư này áp dụng:

- 1. Tổ chức, cá nhân sử dụng phần mềm ký số, phần mềm kiểm tra chữ ký số; các tổ chức, cá nhân phát triển phần mềm ký số, phần mềm kiểm tra chữ ký số; các Tổ chức cung cấp dịch vụ chứng thực chữ ký số khi phát triển, sử dụng phần mềm ký số, phần mềm kiểm tra chữ ký số.
- 2. Các Tổ chức cung cấp dịch vụ chứng thực chữ ký số; các Tổ chức cung cấp dịch vụ chứng thực chữ ký điện tử nước ngoài được công nhận tại Việt Nam; chủ quản các hệ thống thông tin phục vụ giao dịch điện tử có sử dụng chữ ký số khi kết nối đến Cổng kết nối dịch vụ chứng thực chữ ký số công cộng.
- 3. Các tổ chức, cá nhân có liên quan khác.

#### **1.3 Giải thích từ ngữ**

Trong Thông tư này, các từ ngữ dưới đây được hiểu như sau:

- 1. "Cặp khóa không đối xứng" là khóa công khai và khóa bí mật tương ứng.
- 2. "Khóa bí mật" là thành phần của cặp khóa không đối xứng được sử dụng để ký thông điệp dữ liệu.
- 3. "Khóa công khai" là thành phần của cặp khóa không đối xứng được sử dụng để xác thực chữ ký số trên thông điệp dữ liệu.

![](_page_1_Picture_0.jpeg)

- 4. "Hàm băm" là một thuật toán chuyển đổi thông điệp dữ liệu đầu vào thành một chuỗi có độ dài cố định, gọi là mã băm. Hàm băm được sử dụng để kiểm tra tính toàn vẹn của thông điệp dữ liệu và tạo chữ ký số.
- 5. "Chủ thể ký" là cá nhân hoặc tổ chức sở hữu chứng thư chữ ký số và sử dụng khóa bí mật tương ứng để thực hiện ký số trên thông điệp dữ liệu.
- 6. "Chứng thư chữ ký số" là một dạng chứng thư chữ ký điện tử do Tổ chức cung cấp dịch vụ chứng thực chữ ký số cấp nhằm cung cấp thông tin về khóa công khai của một cá nhân, tổ chức từ đó xác nhận cá nhân, tổ chức là chủ thể ký thông qua việc sử dụng khóa bí mật tương ứng.
- 7. "Phần mềm ký số" là chương trình độc lập hoặc một thành phần (module) phần mềm hoặc giải pháp có chức năng ký số vào thông điệp dữ liệu.
- 8. "Phần mềm kiểm tra chữ ký số" là chương trình độc lập hoặc một thành phần (module) phần mềm hoặc giải pháp có chức năng kiểm tra tính hợp lệ của chữ ký số trên thông điệp dữ liệu đã ký. 10. "Đường dẫn tin cậy của chứng thư chữ ký số" là danh sách có thứ tự các chứng thư chữ ký số, bao gồm chứng thư chữ ký số của thuê bao, chứng thư chữ ký số của các Tổ chức cung cấp dịch vụ chứng thực chữ ký số và chứng thư chữ ký số gốc tin cậy nhằm xác minh nguồn gốc của chứng thư chữ ký số.

## **2. Yêu cầu kỹ thuật đối với chức năng phần mềm ký số, phần mềm kiểm tra chữ ký số**

### **2.1 Yêu cầu chung**

Tuân thủ các yêu cầu và tiêu chuẩn kỹ thuật về chữ ký số trên thông điệp dữ liệu dùng cho phần mềm ký số và phần mềm kiểm tra chữ ký số tại Phụ lục I ban hành kèm theo Thông tư này.

## **2.2 Yêu cầu về chức năng đối với phần mềm ký số**

## **Chức năng xác thực chủ thể ký và ký số**

a) Kiểm tra được thông tin chủ thể ký trên chứng thư chữ ký số và kiểm tra hiệu lực chứng thư chữ ký số theo quy định tại khoản 2 Điều này trước khi cho phép thực hiện ký số;

![](_page_2_Picture_0.jpeg)

- b) Cho phép chủ thể ký sử dụng khóa bí mật để thực hiện việc ký số vào thông điệp dữ liệu. Khoá bí mật lưu trong phương tiện lưu khóa bí mật được chủ thể ký sử dụng hoặc ủy quyền sử dụng để ký số phải tuân thủ các tiêu chuẩn bắt buộc áp dụng cho chữ ký số, chứng thư chữ ký số trên thông điệp dữ liệu dùng cho phần mềm ký số và phần mềm kiểm tra chữ ký số tại Phụ lục I ban hành kèm theo Thông tư này;
- c) Cho phép chuyển đổi định dạng thông điệp dữ liệu thành các định dạng theo tiêu chuẩn khuyến nghị áp dụng cho phần mềm ký số, phần mềm kiểm tra chữ ký số tại Phụ lục I ban hành kèm theo Thông tư này;
- d) Cho phép gắn kèm chữ ký số, chứng thư chữ ký số và thời điểm ký số vào thông điệp dữ liệu sau khi ký số;
- đ) Hỗ trợ cài đặt, tích hợp, cập nhật chứng thư chữ ký số của Trung tâm Chứng thực điện tử quốc gia, các Tổ chức cung cấp dịch vụ chứng thực chữ ký số công cộng và chứng thư chữ ký số thuộc Danh sách tin cậy chứng thư chữ ký điện tử nước ngoài được công nhận tại Việt Nam;
- e) Cho phép gắn dấu thời gian tương ứng với chữ ký số trên thông điệp dữ liệu trong trường hợp pháp luật quy định thông điệp dữ liệu cần có dấu thời gian;
- g) Đảm bảo tính toàn vẹn của thông điệp dữ liệu đã ký.

## **Chức năng kiểm tra hiệu lực của chứng thư chữ ký số**

- a) Xác thực được thông tin trong chứng thư chữ ký số theo quy định pháp luật về định danh và xác thực điện tử;
- b) Kiểm tra được chứng thư chữ ký số của chủ thể ký theo đường dẫn tin cậy của chứng thư chữ ký số đó hoặc theo Danh sách tin cậy chứng thư chữ ký điện tử nước ngoài được công nhận tại Việt Nam. Đường dẫn tin cậy phải có liên kết đến chứng thư chữ ký số gốc của Trung tâm Chứng thực điện tử quốc gia;
- c) Đáp ứng các yêu cầu về tính hiệu lực của chứng thư chữ ký số tại Phụ lục II ban hành kèm theo Thông tư này.

## **Chức năng kết nối đến Cổng kết nối dịch vụ chứng thực chữ ký số công cộng**

- a) Phát triển các thành phần, chương trình hoặc giải pháp phục vụ kết nối đến Cổng kết nối dịch vụ chứng thực chữ ký số công cộng;
- b) Tuân thủ Hướng dẫn kết nối đến Cổng kết nối dịch vụ chứng thực chữ ký số công cộng do Bộ Khoa học và Công nghệ xây dựng được quy định tại Điều 8 Thông tư này.

![](_page_3_Picture_0.jpeg)

## **QUY ĐỊNH YÊU CẦU KỸ THUẬT ĐỐI VỚI PHẦN MỀM KÝ SỐ, PHẦN MỀM KIỂM TRA CHỮ KÝ <sup>S</sup><sup>Ố</sup> VÀ CỔNG KẾT NỐI DỊCH V<sup>Ụ</sup> CHỨNG THỰC CH<sup>Ữ</sup> KÝ S<sup>Ố</sup> CÔNG CỘNG** <sup>L</sup>ần ban hành: 1

## **Chức năng lưu trữ và hủy bỏ các thông tin kèm theo thông điệp dữ liệu ký số, bao gồm:**

- a) Chứng thư chữ ký số tương ứng với khóa bí mật mà chủ thể ký sử dụng để ký thông điệp dữ liệu tại thời điểm ký số;
- b) Danh sách chứng thư chữ ký số thu hồi tại thời điểm ký trong chứng thư chữ ký số của chủ thể ký;
- c) Kết quả kiểm tra trạng thái chứng thư chữ ký số tương ứng với chữ ký số trên thông điệp dữ liệu đã ký.

## **Chức năng thay đổi (thêm, bớt) chứng thư chữ ký số của cơ quan, tổ chức tạo lập cấp, phát hành chứng thư chữ ký số:** Cho phép tích hợp và hiển thị đầy đủ các Tổ chức cung cấp dịch vụ chứng thực chữ ký số và Danh sách tin cậy chứng thư chữ ký điện tử nước ngoài được công nhận tại Việt Nam.

## **Chức năng thông báo bằng chữ hoặc ký hiệu cho chủ thể ký biết việc ký số vào thông điệp dữ liệu thành công hay không thành công, bao gồm việc:**

- a) Hiển thị thông báo về kết quả kiểm tra hiệu lực chứng thư chữ ký số;
- b) Hiển thị thông báo ký số thành công hoặc không thành công bằng tiếng Việt;
- c) Tải được thông điệp dữ liệu đã ký về thiết bị.

## **2.3 Yêu cầu về chức năng đối với phần mềm kiểm tra chữ ký số**

## **Chức năng kiểm tra tính hợp lệ của chữ ký số trên thông điệp dữ liệu:**

- a) Cho phép xác thực chữ ký số trên thông điệp dữ liệu theo nguyên tắc chữ ký số được tạo ra đúng với khóa bí mật tương ứng với khóa công khai trên chứng thư chữ ký số gắn kèm chữ ký số;
- b) Cho phép kiểm tra chứng thư chữ ký số của chủ thể ký theo đường dẫn tin cậy của chứng thư chữ ký số đó và phải liên kết đến Trung tâm Chứng thực điện tử quốc gia hoặc thuộc Danh sách tin cậy chứng thư chữ ký điện tử nước ngoài được công nhận tại Việt Nam;
- c) Bảo đảm chứng thư chữ ký số phải đáp ứng các yêu cầu về tính hiệu lực của chứng thư chữ ký số và tính hợp lệ của chữ ký số tại Phụ lục II ban hành kèm theo Thông tư này;
- d) Cho phép kiểm tra tính toàn vẹn của thông điệp dữ liệu ký số theo các bước sau: giải mã chữ ký số trên thông điệp dữ liệu bằng khóa công khai trên chứng thư chữ ký số để có thông tin về mã băm của thông điệp dữ liệu; sử dụng hàm băm đã tạo ra mã băm trên chữ ký số

![](_page_4_Picture_0.jpeg)

để thực hiện tạo mã băm cho thông điệp dữ liệu nhận được; so sánh sự trùng khớp của hai mã băm để kiểm tra tính toàn vẹn của thông điệp dữ liệu ký số;

- đ) Đảm bảo kiểm tra được tính hợp lệ của chữ ký số trên thông điệp dữ liệu đã ký theo các yêu cầu về tính hợp lệ của chữ ký số tại Phụ lục II ban hành kèm theo Thông tư này;
- e) Hỗ trợ cài đặt, tích hợp, cập nhật chứng thư chữ ký số của Trung tâm Chứng thực điện tử quốc gia, các Tổ chức cung cấp dịch vụ chứng thực chữ ký số công cộng và chứng thư chữ ký số thuộc Danh sách tin cậy chứng thư chữ ký điện tử nước ngoài được công nhận tại Việt Nam;
- g) Đảm bảo tính hợp lệ của dấu thời gian gắn kèm với chữ ký số trong trường hợp chữ ký số được gắn dấu thời gian;
- h) Đảm bảo tính toàn vẹn của thông điệp dữ liệu đã ký.

### **Chức năng lưu trữ và hủy bỏ các thông tin kèm theo thông điệp dữ liệu ký số:**

- a) Chứng thư chữ ký số tương ứng với chữ ký số trên thông điệp dữ liệu đã ký;
- b) Danh sách chứng thư chữ ký số thu hồi tại thời điểm ký được thể hiện trong chứng thư chữ ký số đính kèm thông điệp dữ liệu đã ký;
- c) Kết quả kiểm tra trạng thái chứng thư chữ ký số tương ứng với chữ ký số trên thông điệp dữ liệu đã ký.
  - **Chức năng thay đổi (thêm, bớt) chứng thư chữ ký số của cơ quan, tổ chức tạo lập, cấp, phát hành chứng thư chữ ký số.**

## **Chức năng thông báo bằng chữ hoặc ký hiệu việc kiểm tra tính hợp lệ của chữ ký số là hợp lệ hay không hợp lệ:**

- a) Hiển thị thông báo chữ ký số trên thông điệp dữ liệu đã ký hợp lệ hay không hợp lệ bằng tiếng Việt;
- b) Hiển thị các thông tin về chữ ký số và chứng thư chữ ký số trên thông điệp dữ liệu đã ký, với tối thiểu các trường thông tin sau: thông tin về cơ quan, tổ chức tạo lập, cấp, phát hành chứng thư chữ ký số; thông tin về chủ thể ký; thông tin về đơn vị quản lý chứng thư chữ ký số; thông tin về thời điểm ký số hoặc dấu thời gian (nếu có); tính toàn vẹn của thông điệp dữ liệu đã ký; tính hợp lệ của chữ ký số tại thời điểm ký; thời hạn có hiệu lực của chứng thư chữ ký số.

## **3. Cổng kết nói dịch vụ chứng thực chữ ký só công cộng**

![](_page_5_Picture_0.jpeg)

### **3.1 Cổng kết nối dịch vụ chứng thực chữ ký số công cộng**

- 1. Cổng kết nối dịch vụ chứng thực chữ ký số công cộng do Bộ Khoa học và Công nghệ xây dựng được quy định tại Nghị định số 42/2022/NĐ-CP.
- 2. Cổng kết nối dịch vụ chứng thực chữ ký số công cộng do Bộ Khoa học và Công nghệ xây dựng phục vụ kết nối dịch vụ chứng thực chữ ký số công cộng với các hệ thống thông tin phục vụ giao dịch điện tử sử dụng chữ ký số để bảo đảm tính xác thực, tính toàn vẹn và tính chống chối bỏ của thông điệp dữ liệu.
- **3.2 Kết nối đến Cổng kết nối dịch vụ chứng thực chữ ký số công cộng do Bộ Khoa học và Công nghệ xây dựng**
  - **Các Tổ chức cung cấp dịch vụ chứng thực chữ ký số công cộng kết nối đến Cổng kết nối dịch vụ chứng thực chữ ký số công cộng do Bộ Khoa học và Công nghệ xây dựng, cụ thể:**
- a) Thực hiện theo Hướng dẫn kết nối tại Phụ lục III ban hành kèm theo Thông tư này;
- b) Cung cấp các đặc tả, thông số kỹ thuật và thông tin phục vụ kết nối cho Trung tâm Chứng thực điện tử quốc gia;
- c) Cập nhật các thông số kỹ thuật hoặc thông tin phục vụ kết nối khi có thay đổi cho Trung tâm Chứng thực điện tử quốc gia.
  - **Các hệ thống thông tin phục vụ giao dịch điện tử sử dụng chữ ký số tích hợp với Cổng kết nối dịch vụ chứng thực chữ ký số công cộng do Bộ Khoa học và Công nghệ xây dựng để bảo đảm tính xác thực, tính toàn vẹn và tính chống chối bỏ của thông điệp dữ liệu, cụ thể:**
- a) Thực hiện theo Hướng dẫn kết nối tại Phụ lục III ban hành kèm theo Thông tư này;
- b) Bảo đảm chức năng ký số của hệ thống thông tin phục vụ giao dịch điện tử sử dụng chữ ký số đáp ứng các quy định tại Điều 5 Thông tư này;

![](_page_6_Picture_0.jpeg)

- **Trung tâm Chứng thực điện tử quốc gia cung cấp, cập nhật các đặc tả, thông số kỹ thuật và thông tin phục vụ việc kết nối đến Cổng kết nối dịch vụ chứng thực chữ ký số công cộng.**
- **Đầu mối hỗ trợ, hướng dẫn kết nối đến Cổng kết nối dịch vụ chứng thực chữ ký số công cộng do Bộ Khoa học và Công nghệ xây dựng: Trung tâm Chứng thực điện tử quốc gia, Bộ Khoa học và Công nghệ.**

## **4. Điều khoản thi hành**

## **4.1 Tổ chức thực hiện**

- Trung tâm Chứng thực điện tử quốc gia có trách nhiệm hướng dẫn thực hiện các nội dung của Thông tư này và công bố thông tin theo quy định tại khoản 3 Điều 8 Thông tư này.
- Tổ chức cung cấp dịch vụ chứng thực chữ ký số công cộng, Tổ chức cung cấp dịch vụ chứng thực chữ ký điện tử nước ngoài được công nhận tại Việt Nam có trách nhiệm công bố chứng thư chữ ký số liên quan đến Tổ chức cung cấp dịch vụ chứng thực chữ ký số và các tiêu chuẩn chữ ký số trên trang tin điện tử của Tổ chức cung cấp dịch vụ chứng thực chữ ký số đó.

#### **4.2 Hiệu lực thi hành**

- Thông tư này có hiệu lực thi hành kể từ ngày ký ban hành.
- Thông tư số 22/2020/TT-BTTTT ngày 07 tháng 9 năm 2020 của Bộ Thông tin và Truyền thông quy định về yêu cầu kỹ thuật đối với phần mềm ký số, phần mềm kiểm tra chữ ký số hết hiệu lực kể từ ngày Thông tư này có hiệu lực thi hành.
- Các hệ thống thông tin khi tiến hành phát triển, tích hợp phần mềm, ứng dụng sử dụng chữ ký số thực hiện theo các quy định tại Thông tư này.
- Chánh Văn phòng, Giám đốc Trung tâm Chứng thực điện tử quốc gia, Thủ trưởng các cơ quan, đơn vị thuộc Bộ, Giám đốc Sở Khoa học và Công nghệ các tỉnh, thành phố trực thuộc Trung ương, cơ quan quản lý nhà nước về giao dịch điện tử theo quy định của pháp luật, tổ chức, cá nhân có liên quan chịu trách nhiệm thi hành Thông tư này.
- Trong quá trình thực hiện, nếu có khó khăn, vướng mắc, cơ quan, tổ chức, cá nhân phản ánh kịp thời về Bộ Khoa học và Công nghệ (Trung tâm Chứng thực điện tử quốc gia) để xem xét, giải quyết.

![](_page_7_Picture_0.jpeg)

## **QUY ĐỊNH YÊU CẦU KỸ THUẬT ĐỐI VỚI PHẦN MỀM KÝ SỐ, PHẦN MỀM KIỂM TRA CHỮ KÝ <sup>S</sup><sup>Ố</sup> VÀ CỔNG KẾT NỐI DỊCH V<sup>Ụ</sup> CHỨNG THỰC CH<sup>Ữ</sup> KÝ S<sup>Ố</sup> CÔNG CỘNG** <sup>L</sup>ần ban hành: 1

## PHẦN 1: DANH MỤC TIỂU CHUẢN KỸ THUẬT VỀ CHỮ KÝ SÓ TRÊN THÔNG ĐIỆP DỮ LIỆU DUNG CHO PHẦN MỀM KÝ SÓ VÀ PHẦN MỀM KIỂM TRA CHỮ KÝ SỐ

| Số<br>TT | Loại tiêu chuẩn                                                                                                                                            | Ký hiệu tiêu chuẩn          | Tên đầy đủ<br>của tiêu chuẩn                                                                                                                      | Quy định áp dụng                                                                                                                                                                                                          |  |  |
|----------|------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|--|
| tra chữ  | 1. Tiêu chuẩn bắt buộc áp dụng cho chữ<br>ký số, chứng thư chữ<br>ký số<br>trên thông điệp dữ<br>liệu dùng cho phần mềm ký số<br>và phần mềm kiểm<br>ký số |                             |                                                                                                                                                   |                                                                                                                                                                                                                           |  |  |
| 1.1      | Mật mã đối xứng                                                                                                                                            | TCVN 7816:2007              | Công nghệ<br>thông tin -<br>Kỹ<br>thuật mật mã<br>thuật toản mã dũ liệu AES                                                                       | Áp dụng một trong hai tiêu chuẩn                                                                                                                                                                                          |  |  |
|          |                                                                                                                                                            | FIPS PUB 197                | Advanced Encryption Standard                                                                                                                      |                                                                                                                                                                                                                           |  |  |
| 1.2      | Mật mã phi đối<br>xứng và chữ<br>ký                                                                                                                        | PKCS<br>#1<br>(RFC<br>3447) | RSA Cryptography Standard                                                                                                                         | -<br>Áp dụng một trong hai tiêu chuẩn<br>-Đối với tiêu chuẩn RSA:                                                                                                                                                         |  |  |
|          | số                                                                                                                                                         | ANSI X9.62-2005             | Public<br>Key<br>Cryptography<br>for<br>the<br>Financial Services Industry: The Elliptic<br>Curve<br>Digital<br>Signature<br>Algorithm<br>(ECDSA) | + Tối thiểu phiên bản 2.1:<br>+ Áp dụng lược đồ<br>RSAES-OAEP để<br>mã<br>hoá và RSASSA-PSS để<br>ký.<br>+ Độ<br>dài khóa tối thiểu là 2048 bit<br>-<br>Đối với tiêu chuẩn ECDSA: độ<br>dài khóa<br>tối thiểu là 256 bit. |  |  |
| 1.3      | Yêu cầu cho hàm                                                                                                                                            | FIPS PUB 180-4              | Secure Hash Standard                                                                                                                              | Áp dụng một trong các hàm băm sau:                                                                                                                                                                                        |  |  |
|          | băm                                                                                                                                                        | FIPS PUB 202                | SHA-3<br>Standard:<br>Permutation-Based<br>Hash and Extendable-Output Functions                                                                   | SHA-256,<br>SHA-384,<br>SHA-512,<br>SHA<br>512/224,<br>SHA-512/256,<br>SHA3-224,<br>SHA3-256,<br>SHA3-384,<br>SHA3-512,<br>SHAKE128, SHAKE256                                                                             |  |  |
| 1.4      | Cú<br>pháp<br>thông<br>điệp mật mã                                                                                                                         | PKCS #7<br>(RFC 2630)       | Cryptographic Message Syntax Standard                                                                                                             | Phiên bản 1.5                                                                                                                                                                                                             |  |  |
| 1.5      | Chứ<br>ký số<br>cho                                                                                                                                        | ETSI EN 319 142-1           | Electronic Signatures and Infrastructures                                                                                                         | Áp dụng một trong hai bộ<br>tiêu chuẩn: ETSI                                                                                                                                                                              |  |  |

![](_page_8_Picture_0.jpeg)

|     | PDF                        |                      |                                                                                                                                                                                                                                  | EN 319 142-1 Phiên bản V1.2.1                                  |
|-----|----------------------------|----------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------|
|     |                            |                      | (ESI);<br>PAdES<br>digital<br>signatures;<br>Part<br>1:<br>Building blocks and PAdES baseline<br>signatures                                                                                                                      | ETSI EN 319 142-2 Phiên bản V1.1.1<br>Hoặc<br>ISO 14533-3:2017 |
|     |                            | ETSI EN 319 142-2    | Electronic Signatures and Infrastructures<br>(ESI); PAdES digital signatures; Part 2:<br>Additional PAdES signatures profiles                                                                                                    | ISO 32000-1:2008<br>ISO 32000-2:2020                           |
|     |                            | ISO 32000-<br>1:2008 | Document<br>management<br>-<br>Portable<br>document format -<br>Part 1: PDF 1.7                                                                                                                                                  |                                                                |
|     |                            | ISO 14533-<br>3:2017 | Processes, data elements and documents<br>in<br>commerce,<br>industry<br>and<br>administration —<br>Longterm signature<br>formats —<br>Part 3: Long-term signature<br>profiles for PDF Advanced Electronic<br>Signatures (PAdES) |                                                                |
|     |                            | ISO 32000-<br>2:2020 | Document<br>management<br>-<br>Portable<br>document format -<br>Part 2: PDF 2.0                                                                                                                                                  |                                                                |
| 1.6 | Chữ<br>ký số<br>cho<br>XML | ETSI EN 319 132-1    | Electronic Signatures and Infrastructures<br>(ESI); XAdES digital<br>signatures; Part 1:<br>Building blocks and XAdES baseline<br>signatures                                                                                     | Phiên bản V1.2.1                                               |
|     |                            | ETSI EN 319 132-2    | Electronic Signatures and Infrastructures<br>(ESI); XAdES digital signatures; Part 2:<br>Extended XAdES signatures                                                                                                               | Phiên bản V1.1.1                                               |
| 1.7 | Chữ<br>ký số<br>cho<br>CMS | ETSI EN 319 122-1    | lectronic Signatures and Infrastructures<br>(ESI); CAdES digital signatures; Part 1:                                                                                                                                             | Phiên bån V1.3.1                                               |

![](_page_9_Picture_0.jpeg)

|      |                                       |                                 | Building blocks and CAdES baseline<br>signatures                                                                                                                       |                                                                                         |
|------|---------------------------------------|---------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------|
|      |                                       | ETSI EN 319 122-2               | Electronic Signatures and Infrastructures<br>(ESI); CAdES digital signatures; Part 2:<br>Extended CAdES signatures                                                     | Phiên bản V1.1.1                                                                        |
|      |                                       | ETSI TS 119 122-3               | Electronic Signatures and Infrastructures<br>(ESI); CAdES digital signatures; Part 3:<br>Incorporation<br>of<br>Evidence<br>Record<br>Syntax (ERS) mechanisms in CAdES | Phiên bản V1.1.1                                                                        |
| 1.8  | Yêu cầu đối với<br>phần cứng HSM      | FIPS PUB 140-2                  | Security Requirements for Cryptographic<br>Modules                                                                                                                     | -<br>Áp dụng một trong ba tiêu chuẩn.<br>-<br>Đối với các tiêu chuẩn FIPS PUB 140-2/    |
|      |                                       | FIPS PUB 140-3                  | Security Requirements for Cryptographic<br>Modules                                                                                                                     | FIPS PUB<br>140-3: Yêu cầu tối<br>thiểu mức 3 (level 3)                                 |
|      |                                       | EN 419221-<br>5:2018            | Protection<br>Profiles<br>for<br>TSP<br>Cryptographic<br>modules<br>-<br>Part<br>5:<br>Cryptographic Module for Trust Services                                         |                                                                                         |
| 1.9  | Yêu cầu đối với<br>thẻ<br>Token<br>và | FIPS PUB 140-2                  | Security Requirements for Cryptographic<br>Modules                                                                                                                     | -<br>Áp dụng một trong hai tiêu chuân.<br>-<br>Yêu cầu tối thiều mức 2 (level 2)        |
|      | Smart card                            | FIPS PUB 140-3                  | Security Requirements for Cryptographic<br>Modules                                                                                                                     |                                                                                         |
| 1.10 | Yêu cầu đối với<br>thẻ<br>SIM         | FIPS PUB 140-2                  | Security Requirements for Cryptographic<br>Modules                                                                                                                     | -<br>Áp dụng một trong ba tiêu chuẩn.<br>-<br>Đối với các tiêu<br>chuẩn FIPS PUB 140-2/ |
|      |                                       | FIPS PUB 140-3                  | Security Requirements for Cryptographic<br>Modules                                                                                                                     | FIPS PUB 140-3: Yêu cầu tối thiểu mức 2<br>(level 2);                                   |
|      |                                       | TCVN<br>8709<br>(ISO/IEC 15408) | Công nghệ<br>thông tin –<br>Các kỹ<br>thuật an<br>toàn –<br>Các tiêu chí đánh giá an toàn công                                                                         | -<br>Đối với tiêu chuẩn TCVN 8709 (ISO/IEC<br>15408): Yêu cầu tối thiểu EAL mức 4       |

![](_page_10_Picture_0.jpeg)

|      |                                                                                                          |                      | nghệ<br>thông tin                                                                                                                                                                                       | (level 4)            |
|------|----------------------------------------------------------------------------------------------------------|----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------|
|      |                                                                                                          |                      | (Common<br>Criteria<br>for<br>Information                                                                                                                                                               |                      |
|      |                                                                                                          |                      | Technology Security Evaluation)                                                                                                                                                                         |                      |
| 1.11 | Yêu<br>cầu<br>chính<br>sách cho Tổ<br>chức<br>cung cấp dịch vụ<br>tạo chữ<br> ký số<br>của<br>khách hàng | ETSI TS 119 431-1    | Electronic Signatures and Infrastructures<br>(ESI); Policy and security requirements<br>for trust service providers; Part 1: TSP<br>service components operating a remote<br>QSCD/SCDev                 | Phiên bản V1.2.1     |
|      |                                                                                                          | ETSI TS 119 431-2    | Electronic Signatures and Infrastructures<br>(ESI); Policy and security requirements<br>for trust service providers; Part 2: TSP<br>service<br>components supporting AdES<br>digital signature creation | Phiên bản V1.2.1     |
| 1.12 | Giao thức tạo chữ<br>ký số                                                                               | ETSI TS 119 432      | Electronic Signatures and Infrastructures<br>(ESI);<br>Protocols<br>for<br>remote<br>digital<br>signature creation                                                                                      | Phiên bản V1.2.1     |
| 1.13 | Ứng dụng ký trên<br>máy chủ<br>ký số                                                                     | EN 419241-<br>1:2018 | Trustworthy Systems Supporting Server<br>Signing -<br>Part 1: General system security<br>requirements                                                                                                   |                      |
| 1.14 | Yêu cầu cho mô<br>đun ký số                                                                              | EN 419241-<br>2:2019 | Trustworthy Systems Supporting Server<br>Signing -<br>Part 2: Protection Profile for<br>QSCD for Server Signing                                                                                         |                      |
| 1.15 | Yêu cầu đối với<br>phần cứng HSM                                                                         | EN 419221-<br>5:2018 | Protection<br>Profiles<br>for<br>TSP<br>Cryptographic<br>modules<br>-<br>Part<br>5:<br>Cryptographic Module for Trust Services                                                                          |                      |
| 1.16 | Giao thức truyền, RFC 2585                                                                               |                      | Internet X.509 Public Key Infrastructure Áp dụng một hoặc cả                                                                                                                                            | hai giao thức FTP và |

![](_page_11_Picture_0.jpeg)

|      | nhận chứng thư<br>chữ<br>ký số<br>và danh<br>sách chứng thư<br>chữ<br>ký số<br>bị<br>thu<br>hồi      |                | -<br>Operational Protocols: FTP and HTTP                                                                 | HTTP                      |  |  |
|------|------------------------------------------------------------------------------------------------------|----------------|----------------------------------------------------------------------------------------------------------|---------------------------|--|--|
| 1.17 | Giao<br>thức<br>cho<br>kiểm<br>tra<br>trạng<br>thái<br>chứng<br>thu<br>chữ<br>ký số<br>trực<br>tuyến | RFC 6960       | X.509 Internet Public Key Infrastructure<br>Online Certificate Status Protocol -<br>OCSP                 |                           |  |  |
| 1.18 | Định dạng chứng<br>thư chữ<br>ký số<br>và<br>danh sách thu hồi<br>chứng thư chữ<br>ký<br>số          | RFC 5280       | Internet X.509 Public Key Infrastructure<br>Certificate and Certificate Revocation<br>List (CRL) Profile |                           |  |  |
|      |                                                                                                      |                | 2. Tiêu chuần bắt buộc áp dụng cho phần mềm ký số, phần mềm kiểm tra chữ<br>ký số                        |                           |  |  |
| 2.1  | Bộ<br>ký tự<br>và mã<br>hóa<br>cho<br>tiếng<br>Việt                                                  | TCVN 6909:2001 | TCVN 6909:2001 " Công nghệ<br>thông<br>tin-Bộ<br>mã ký tự<br>tiếng Việt 16-bit"                          | Bắt buộc áp dụng          |  |  |
| 2.2  | Giao thức đường<br>truyền                                                                            | RFC 9110       | HTTP Semantics                                                                                           | HTTP/1.1                  |  |  |
| 2.3  | Giao<br>thức<br>bảo<br>mật tầng giao vận                                                             | RFC 5246       | The Transport Layer Security (TLS)<br>Protocol Version 1.2                                               | Áp dụng tối thiểu TLS 1.2 |  |  |
|      | 3. Tiêu chuần khuyến nghị<br>áp dụng cho phần mềm ký số, phần mềm kiểm tra chứ<br>ký số              |                |                                                                                                          |                           |  |  |
| 3.1  | Bộ<br>ký tự<br>và mã<br>hóa                                                                          | ASCII          | American Standard Code for Information<br>Interchange                                                    |                           |  |  |

![](_page_12_Picture_0.jpeg)

| 3.2 | Trình diễn bộ<br>ký<br>tự                                                          | UTF-8                                            | 8-bit Universal Character Set (UCS)/<br>Unicode Transformation Format           |                            |
|-----|------------------------------------------------------------------------------------|--------------------------------------------------|---------------------------------------------------------------------------------|----------------------------|
| 3.3 | Ngôn<br>ngữ<br>định<br>dạng thông điệp<br>dữ<br>liệu                               | XML<br>v1.0<br>(5th<br>Edition)                  | Extensible Markup Language version 1.0<br>(5th Edition)                         | Áp dụng tối thiểu XML v1.0 |
|     |                                                                                    | XML<br>v1.1<br>(2nd<br>Edition)                  | Extensible Markup Language version 1.1                                          |                            |
| 3.4 | Định nghĩa các<br>lược đồ<br>trong tài<br>liệu XML                                 | XML<br>Schema<br>version 1.1                     | XML Schema version 1.1                                                          |                            |
| 3.5 | Trao đổi dũ liệu<br>đặc<br>tả<br>tài<br>liệu<br>XML                                | XML v2.4.2                                       | XML Metadata Interchange version 2.4.2                                          |                            |
| 3.6 | Định<br>dạng PDF                                                                   | ISO 32000-<br>1:2008                             | Document<br>management<br>-<br>Portable<br>document format -<br>Part 1: PDF 1.7 | Áp dụng tối thiểu PDF 1.7  |
|     |                                                                                    | ISO 32000-<br>2:2020                             | Document<br>management<br>-<br>Portable<br>document format -<br>Part 2: PDF 2.0 |                            |
| 3.7 | Định dạng JSON                                                                     | RFC 7159                                         | The JavaScript Object Notation (JSON)<br>Data Interchange Format                |                            |
| 3.8 | Cú pháp mã hóa<br>và<br>cách<br>xử<br>lý<br>thông điệp dữ<br>liệu<br>định dạng XML | XML<br>Encryption<br>Syntax<br>and<br>Processing | XML Encryption Syntax and Processing                                            |                            |
|     |                                                                                    | XML<br>Signature<br>Syntax<br>and<br>Processing  | XML Signature Syntax and Processing                                             |                            |
| 3.9 | Quản<br>lý                                                                         | khóa XKMS v2.0                                   | XML Key Management Specification                                                |                            |

![](_page_13_Picture_0.jpeg)

## **QUY ĐỊNH YÊU CẦU KỸ THUẬT ĐỐI VỚI PHẦN MỀM KÝ SỐ, PHẦN MỀM KIỂM TRA CHỮ KÝ <sup>S</sup><sup>Ố</sup> VÀ CỔNG KẾT NỐI DỊCH V<sup>Ụ</sup> CHỨNG THỰC CH<sup>Ữ</sup> KÝ S<sup>Ố</sup> CÔNG CỘNG** <sup>L</sup>ần ban hành: 1

|      | công khai thông<br>điệp dũ liệu định<br>dạng XML |          | version 2.0              |  |
|------|--------------------------------------------------|----------|--------------------------|--|
| 3.10 | Chũ ký số<br>cho<br>JSON                         | RFC 7515 | JSON Web Signature (JWS) |  |

## PHẦN 2: DANH MỤC YÊU CẦU ĐÁNH GIÁ TÍNH HIỆU LỰC CỦA CHỨNG THƯ CHỮ KÝ SỐ VÀ TÍNH HỢP LỆ CỦA CHỮ KÝ SỐ TRONG PHẦN MỀM KÝ SỐ, PHẦN MÈM KIỂM TRA CHỮ KÝ SỐ

| Số<br>TT | Yêu cầu đánh giá                                                                                                                                                                                                                                                                                                                                     | Hiệu lực/hợp lệ                                                                                                                                                                                                                                                      | Quy định áp dụng   |  |  |
|----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|--|--|
| 1        | Tính hiệu lực của chứng thư chữ<br>ký số                                                                                                                                                                                                                                                                                                             |                                                                                                                                                                                                                                                                      |                    |  |  |
| 1.1      | Thời gian có hiệu lực của chứng thư chữ<br>ký<br>số                                                                                                                                                                                                                                                                                                  | -<br>Thời điểm ký số<br>nằm trong thời<br>gian có hiệu lực của chứng thư chữ<br>ký số.                                                                                                                                                                               | Chức năng bắt buộc |  |  |
|          |                                                                                                                                                                                                                                                                                                                                                      | -<br>Thời gian có hiệu lực của chứng<br>thư chữ<br>ký số<br>tính từ<br>thời điểm<br>Valid from đến thời điểm Valid to.<br>-<br>Chứng thư chữ<br>ký số<br>không bị<br>tạm dừng  hoặc thu hổi tại thời<br>điểm ký số.                                                  |                    |  |  |
| 1.2      | -<br>Trạng thái chứng thư chũ ký số<br>qua danh<br>sách chứng thư chữ<br>ký số<br>thu hồi (CRL)<br>được công bố<br>tại thời điểm ký số;<br>-<br>Trạng thái chứng thư chữ<br>ký số<br>trực tuyến<br>(OCSP) ở<br>chế<br>độ<br>trực tuyến trong trường hợp<br>Tổ<br>chức cung cấp dịch vụ<br>chứng thực chữ<br>ký<br>số<br>có cung cấp dịch vụ<br>OCSP. | OCSP và CRL tuân theo tiêu chuẩn<br>nêu tại Phụ<br>lục I. Trường hợp sử<br>dụng OCSP, phần mềm phải được s<br>dụng ở<br>chế<br>độ<br>trực tuyến<br>Trường<br>hợp sử<br>dụng CRL, CRL phải là<br>CRL mới nhất tại thời điểm ký số<br>Trường hợp không thể<br>kiểm tra | Chức năng bắt buộc |  |  |

![](_page_14_Picture_0.jpeg)

|     |                                                                                    | trạng thái chứng thư chữ<br>ký số<br>thông qua OCSP/CRL, phần mềm<br>phải hiển<br>thị<br>cảnh báo tương ứng<br>cho chủ<br>thể<br>ký.                                                                                           |                    |  |
|-----|------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------------------|--|
| 1.3 | Thuật toán mật mã trên chứng thư chữ<br>ký số                                      | Các thuật toản mật mã trên chứng<br>thư chữ<br>ký số<br>tuân thủ<br>theo quy<br>định về<br>quy chuẩn, tiêu chuẩn kỹ<br>thuật bắt buộc áp dụng về<br>chữ<br>ký số<br>và dịch vụ<br>chứng thực chữ<br>ký số<br>đang có hiệu lực. | Chức năng bắt buộc |  |
| 1.4 | Phạm vi sử<br>dụng của chứng thư chữ<br>ký số                                      | Chúng thư chữ<br>ký số<br>được sử<br>dụng<br>đúng phạm vi trong các quy định về<br>chữ<br>ký điện tử<br>và dịch vụ<br>tin cậy.                                                                                                 | Chức năng bắt buộc |  |
| 1.5 | Mục đích sử<br>dụng của chứng thư chữ<br>ký số                                     | Mục đích sử<br>dụng chứng thư chữ<br>ký số<br>tại các trường thông tin Key<br>Usage, Extended Key Usage.                                                                                                                       | Chức năng tùy chọn |  |
| 1.6 | Các tuyên bố<br>khác của Tổ<br>chức cung cấp<br>dịch vụ<br>chứng thực chữ<br>ký số | Các tuyên bố<br>khác không nằm<br>ngoài phạm vi Quy chế<br>chứng thực<br>của Tổ<br>chức cung cấp dịch vụ<br>chứng thực chữ<br>ký số<br>tại mục<br>Issuer Statement.                                                            | Chức năng tùy chọn |  |
| 2   | Tính hợp lệ<br>của chữ<br>ký số                                                    |                                                                                                                                                                                                                                |                    |  |
| 2.1 | Thông tin về<br>chủ<br>thể<br>ký                                                   | Kiểm tra, xác thực được đúng<br>thông tin chủ<br>thể<br>ký số<br>trên thông<br>điệp dữ<br>liệu                                                                                                                                 | Chức năng bắt buộc |  |
| 2.2 | Cách thức tạo chữ<br>ký số                                                         | hữ<br>ký số<br>được tạo ra đúng bởi khóa Chức năng bắt buộc                                                                                                                                                                    |                    |  |

![](_page_15_Picture_0.jpeg)

**QUY ĐỊNH YÊU CẦU KỸ THUẬT ĐỐI VỚI PHẦN MỀM KÝ SỐ, PHẦN MỀM KIỂM TRA CHỮ KÝ <sup>S</sup><sup>Ố</sup> VÀ CỔNG KẾT NỐI DỊCH V<sup>Ụ</sup> CHỨNG THỰC CH<sup>Ữ</sup> KÝ S<sup>Ố</sup> CÔNG CỘNG** <sup>L</sup>ần ban hành: 1

|     |                                                          | bí<br>mật tương ứng với khóa công<br>khai trên chứng thư chữ<br>ký số<br>theo<br>các bước tại điểm d, khoản 1, Điều<br>6 Thông tư này. |                    |
|-----|----------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------|--------------------|
| 2.3 | Chứng thư chữ<br>ký số<br>kèm theo thông điệp dữ<br>liệu | Chứng thư chữ<br>ký số<br>có hiệu lực tại<br>thời điểm ký số.                                                                          | Chức năng bắt buộc |
| 2.4 | Tính toàn vẹn của thông điệp dữ<br>liệu                  | Mã băm có được từ<br>việc băm thông<br>điệp dữ<br>liệu và mã băm có được khi<br>giải mã chữ<br>ký số<br>trùng nhau                     | Chức năng bắt buộc |

PHẦN 3: HƯỚNG DẦN KẾT NỐI ĐẾN CÔNG KẾT NỐI DỊCH VỤ CHỨNG THỰC CHỮ KÝ SỐ CÔNG CỘNG DO BỘ KHOA HỌC VÀ CÔNG NGHỆ XÂY DỰNG

#### 1. Mô hình kết nối

Mô hình kết nối với Cổng kết nối dịch vụ chứng thực chữ ký số công cộng do Bộ Khoa học và Công nghệ xây dựng (sau đây gọi là Cồng eSign) được mô tả tại sơ đồ nhu sau:

![](_page_16_Picture_0.jpeg)

## **QUY ĐỊNH YÊU CẦU KỸ THUẬT ĐỐI VỚI PHẦN MỀM KÝ SỐ, PHẦN MỀM KIỂM TRA CHỮ KÝ <sup>S</sup><sup>Ố</sup> VÀ CỔNG KẾT NỐI DỊCH V<sup>Ụ</sup> CHỨNG THỰC CH<sup>Ữ</sup> KÝ S<sup>Ố</sup> CÔNG CỘNG** <sup>L</sup>ần ban hành: 1

![](_page_16_Picture_4.jpeg)

#### Chú thích:

- HTTT: Hệ thống thông tin phục vụ giao dịch điện tử sử dụng chữ ký số.
- CA: Tổ chức cung cấp dịch vụ chứng thực chữ ký số công cộng.
- 2. Các thông tin phục vụ kết nối
- a) Giao thức sử dụng để kết nối là API, phương thức kết nối là POST.
- b) Đường dẫn kết nối các API: [https://esign.neac.gov.vn](https://esign.neac.gov.vn/)
- c) Thông tin Cổng eSign cung cấp cho các HTTT gồm: sp\_id và sp\_password hoặc token, trong đó:
- sp\_id: Mã xác thực được cấp cho HTTT.
- sp\_password: Mật khẩu kết nối được cấp cho HTTT tương ứng với sp\_id.
- token: Thông tin xác thực được cấp cho HTTT.
- d) Giao thức bảo mật đường truyền khi kết nối tối thiểu là TLS 1.2.