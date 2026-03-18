| VIETTEL AI RACE                                                                                                                                  | Public 257      |
|--------------------------------------------------------------------------------------------------------------------------------------------------|-----------------|
| Quy định yêu cầu kỹ thuật đối với phần<br>mềm ký số, phần mềm kiểm tra chữ ký<br>số<br>và Cổng kết nối dịch vụ chứng thực<br>chữ ký số công cộng | Lần ban hành: 1 |

*Căn cứ Luật giao dịch điện tử ngày 22 tháng 06 năm 2023;*

*Căn cứ Nghị định số 23/2025/NĐ-CP ngày 21 tháng 02 năm 2025 của Chính phủ quy định về chữ ký điện tử và dịch vụ tin cậy;*

*Căn cứ Nghị định số 55/2025/NĐ-CP ngày 02 tháng 3 năm 2025 của Chính phủ quy định chức năng, nhiệm vụ và cơ cấu tổ chức của Bộ Khoa học và Công nghệ;*

*Theo đề nghị của Vụ trưởng Vụ Pháp chế và Giám đốc Trung tâm Chứng thực điện tử quốc gia;*

*Bộ trưởng Bộ Khoa học và Công nghệ ban hành Thông tư quy định yêu cầu kỹ thuật đối với phần mềm ký số, phần mềm kiểm tra chữ ký số và Cổng kết nối dịch vụ chứng thực chữ ký số công cộng.*

## **1. QUY ĐỊNH CHUNG**

## **1.1. Phạm vi điều chỉnh**

Thông tư này quy định yêu cầu kỹ thuật đối với phần mềm ký số, phần mềm kiểm tra chữ ký số và Cổng kết nối dịch vụ chứng thực chữ ký số công cộng.

## **1.2 . Đối tượng áp dụng**

Thông tư này áp dụng đối với tổ chức, cá nhân sử dụng phần mềm ký số, phần mềm kiểm tra chữ ký số; các tổ chức, cá nhân phát triển phần mềm ký số, phần mềm kiểm tra chữ ký số; các tổ chức cung cấp dịch vụ chứng thực chữ ký số; các tổ chức cung cấp dịch vụ chứng thực chữ ký điện tử chuyên dùng đảm bảo an toàn; các tổ chức cung cấp dịch vụ chứng thực chữ ký điện tử nước ngoài được công nhận tại Việt Nam; chủ quản các hệ thống thông tin phục vụ giao dịch điện tử có sử dụng chữ ký số và các tổ chức, cá nhân có liên quan khác.

### **1.3. Giải thích từ ngữ**

Trong Thông tư này, các từ ngữ dưới đây được hiểu như sau:

- "Cặp khóa bất đối xứng" là khóa công khai và khóa bí mật tương ứng.
- "Khóa bí mật" là thành phần của cặp khóa bất đối xứng được sử dụng để ký thông điệp dữ liệu.
- "Khóa công khai" là thành phần của cặp khóa bất đối xứng được sử dụng để xác thực chữ ký số trên thông điệp dữ liệu.
- "Chủ thể ký" là cá nhân hoặc tổ chức sở hữu chứng thư chữ ký số và sử dụng khóa bí mật tương ứng để thực hiện ký số trên thông điệp dữ liệu.
- "Chứng thư chữ ký số" là một dạng chứng thư điện tử do tổ chức cung cấp dịch vụ chứng thực chữ ký số cấp nhằm cung cấp thông tin về khóa công khai của một cá nhân, tổ chức từ đó xác nhận cá nhân, tổ chức là chủ thể ký thông qua việc sử dụng khóa bí mật tương ứng.
- "Phần mềm ký số" là chương trình độc lập hoặc một thành phần (module) phần mềm hoặc giải pháp có chức năng ký số vào thông điệp dữ liệu.
- "Phần mềm kiểm tra chữ ký số" là chương trình độc lập hoặc một thành phần (module) phần mềm hoặc giải pháp có chức năng kiểm tra tính hợp lệ của chữ ký số trên thông điệp dữ liệu đã ký.
- "Đường dẫn tin cậy của chứng thư chữ ký số" là thông tin đường dẫn trên chứng thư chữ ký số xác thực tổ chức cung cấp dịch vụ chứng thực chữ ký số đã cấp phát ra chứng thư chữ ký số đó.

# **2. Yêu cầu kỹ thuật đối với chức năng phần mềm ký số, phần mềm kiểm tra chữ ký số**

## **2.1 Yêu cầu chung**

Tuân thủ các yêu cầu và tiêu chuẩn kỹ thuật về chữ ký số trên thông điệp dữ liệu tại Phụ lục I ban hành kèm theo Thông tư này.

## **2.2 Yêu cầu về chức năng**

- Chức năng xác thực chủ thể ký và ký số:
  - + Kiểm tra được thông tin chủ thể ký trên chứng thư chữ ký số;

- + Cho phép chủ thể ký sử dụng khóa bí mật để thực hiện việc ký số vào thông điệp dữ liệu. Khoá bí mật lưu trong thiết bị được chủ thể ký sử dụng để ký số phải tuân thủ các yêu cầu và tiêu chuẩn kỹ thuật tại Phụ lục I ban hành kèm theo Thông tư này;
- + Cho phép chuyển đổi định dạng thông điệp dữ liệu thành các định dạng được nêu tại Phụ lục I ban hành kèm theo Thông tư này;
- + Gắn kèm chữ ký số và chứng thư chữ ký số vào thông điệp dữ liệu sau khi ký số;
- + Hỗ trợ cài đặt, tích hợp chứng thư chữ ký số của Tổ chức cung cấp dịch vụ chứng thực chữ ký số quốc gia và chứng thư chữ ký số thuộc Danh sách tin cậy chứng thư chữ ký điện tử nước ngoài được công nhận tại Việt Nam;
- + Đáp ứng các giao thức gửi nhận thông điệp dữ liệu của phần mềm ký số theo các yêu cầu và tiêu chuẩn tại Phụ lục I ban hành kèm theo Thông tư này.
  - Chức năng kiểm tra hiệu lực của chứng thư chữ ký số:
- + Thông tin trong chứng thư chữ ký số được định danh theo quy định pháp luật về định danh và xác thực điện tử;
- + Chứng thư chữ ký số của chủ thể ký phải được kiểm tra theo đường dẫn tin cậy của chứng thư chữ ký số đó và phải liên kết đến chứng thư chữ ký số gốc của Tổ chức cung cấp dịch vụ chứng thực chữ ký số quốc gia hoặc thuộc Danh sách tin cậy chứng thư chữ ký điện tử nước ngoài được công nhận tại Việt Nam;
- + Chứng thư chữ ký số phải có hiệu lực tại thời điểm ký số và đáp ứng các tiêu chí tại Phụ lục II ban hành kèm theo Thông tư này.
- Chức năng kết nối đến Cổng kết nối dịch vụ chứng thực chữ ký số công cộng: Hướng dẫn kết nối được quy định tại Chương III Thông tư này.
- Chức năng lưu trữ và hủy bỏ các thông tin kèm theo thông điệp dữ liệu ký số, bao gồm:
- + Chứng thư chữ ký số tương ứng với khóa bí mật mà chủ thể ký sử dụng để ký thông điệp dữ liệu tại thời điểm ký số;
- + Danh sách chứng thư chữ ký số thu hồi tại thời điểm ký trong chứng thư chữ ký số của chủ thể ký;
- + Quy chế chứng thực của tổ chức cung cấp dịch vụ chứng thực chữ ký số đã cấp chứng thư chữ ký số tương ứng với chữ ký số trên thông điệp dữ liệu;

![](_page_2_Picture_15.jpeg)

- + Kết quả kiểm tra trạng thái chứng thư chữ ký số tương ứng với chữ ký số trên thông điệp dữ liệu đã ký.
- Chức năng thay đổi (thêm, bớt) chứng thư chữ ký số của cơ quan, tổ chức tạo lập cấp, phát hành chứng thư chữ ký số:

Cho phép tích hợp và hiển thị đầy đủ các tổ chức cung cấp dịch vụ chứng thực chữ ký số và Danh sách tin cậy chứng thư chữ ký điện tử nước ngoài được công nhận tại Việt Nam.

- Chức năng thông báo bằng chữ hoặc ký hiệu cho chủ thể ký biết việc ký số vào thông điệp dữ liệu thành công hay không thành công, bao gồm việc:
  - + Hiển thị thông báo ký số thành công hoặc không thành công;
  - + Xem được thông điệp dữ liệu đã ký sau khi hoàn thành ký số;
  - + Tải được thông điệp dữ liệu đã ký về thiết bị.

### **2.3 Yêu cầu chung**

Tuân thủ các yêu cầu và tiêu chuẩn kỹ thuật về chữ ký số trên thông điệp dữ liệu tại Phụ lục I ban hành kèm theo Thông tư này.

### **2.4 Yêu cầu về chức năng**

- Chức năng kiểm tra tính hợp lệ của chữ ký số trên thông điệp dữ liệu:
- + Cho phép xác thực chữ ký số trên thông điệp dữ liệu theo nguyên tắc chữ ký số được tạo ra đúng với khóa bí mật tương ứng với khóa công khai trên chứng thư chữ ký số;
- + Cho phép kiểm tra chứng thư chữ ký số của chủ thể ký theo đường dẫn tin cậy của chứng thư chữ ký số đó và phải liên kết đến Tổ chức cung cấp dịch vụ chứng thực chữ ký số quốc gia hoặc thuộc Danh sách tin cậy chứng thư chữ ký điện tử nước ngoài được công nhận tại Việt Nam;
- + Bảo đảm chứng thư chữ ký số phải có hiệu lực tại thời điểm ký số và đáp ứng các tiêu chí tại Phụ lục II ban hành kèm theo Thông tư này;
- + Cho phép kiểm tra tính toàn vẹn của thông điệp dữ liệu ký số theo các bước sau:
- Giải mã chữ ký số trên thông điệp dữ liệu để có thông tin về mã băm của thông điệp dữ liệu;

![](_page_3_Picture_17.jpeg)

- Sử dụng thuật toán hàm băm an toàn đã tạo ra mã băm trên chữ ký số để thực hiện tạo mã băm cho thông điệp dữ liệu;
- So sánh sự trùng khớp của hai mã băm để kiểm tra tính toàn vẹn của thông điệp dữ liệu ký số.
- + Đảm bảo tính hợp lệ của chữ ký số trên thông điệp dữ liệu đã ký theo các tiêu chí tại Phụ lục II ban hành kèm theo Thông tư này;
- + Hỗ trợ cài đặt, tích hợp chứng thư chữ ký số của Tổ chức cung cấp dịch vụ chứng thực chữ ký số quốc gia và chứng thư chữ ký số thuộc danh sách tin cậy chứng thư chữ ký điện tử nước ngoài được công nhận tại Việt Nam;
- + Đáp ứng các giao thức gửi nhận thông điệp dữ liệu của phần mềm ký số theo tiêu chuẩn tại Phụ lục I ban hành kèm theo Thông tư này.
- Chức năng lưu trữ và hủy bỏ các thông tin kèm theo thông điệp dữ liệu ký số:
- + Chứng thư chữ ký số tương ứng với chữ ký số trên thông điệp dữ liệu đã ký;
- + Danh sách chứng thư chữ ký số thu hồi tại thời điểm ký được thể hiện trong chứng thư chữ ký số đính kèm thông điệp dữ liệu đã ký;
- + Quy chế chứng thực của các tổ chức cung cấp dịch vụ chứng thực chữ ký số cấp phát chứng thư chữ ký số tương ứng với các chữ ký số trên thông điệp dữ liệu đã ký;
- + Kết quả kiểm tra trạng thái chứng thư chữ ký số tương ứng với chữ ký số trên thông điệp dữ liệu đã ký.
- Chức năng thay đổi (thêm, bớt) chứng thư chữ ký số của cơ quan, tổ chức tạo lập, cấp, phát hành chứng thư chữ ký số.
- Chức năng thông báo bằng chữ hoặc ký hiệu việc kiểm tra tính hợp lệ của chữ ký số là hợp lệ hay không hợp lệ:
- + Hiển thị thông báo chữ ký số trên thông điệp dữ liệu đã ký hợp lệ hay không hợp lệ;
- + Hiển thị các thông tin về chữ ký số và chứng thư chữ ký số trên thông điệp dữ liệu đã ký, với tối thiểu các trường thông tin sau: thông tin về cơ quan, tổ chức tạo lập, cấp, phát hành chứng thư chữ ký số; thông tin về chủ thể ký; thông

![](_page_4_Picture_15.jpeg)

tin về thời điểm ký số hoặc dấu thời gian (nếu có); tính toàn vẹn của thông điệp dữ liệu đã ký; tính hợp lệ của chữ ký số tại thời điểm ký.

# **3. CỔNG KẾT NỐI DỊCH VỤ CHỨNG THỰC CHỮ KÝ SỐ CÔNG CỘNG**

## **3.1 Cổng kết nối dịch vụ chứng thực chữ ký số công cộng**

Cổng kết nối dịch vụ chứng thực chữ ký số công cộng là hệ thống thông tin phục vụ kết nối dịch vụ chứng thực chữ ký số công cộng với các hệ thống thông tin phục vụ giao dịch điện tử sử dụng chữ ký số để bảo đảm tính xác thực, tính toàn vẹn và tính chống chối bỏ của thông điệp dữ liệu.

## **3.2 Kết nối đến Cổng kết nối dịch vụ chứng thực chữ ký số công cộng**

- Các tổ chức cung cấp dịch vụ chứng thực chữ ký số công cộng kết nối đến Cổng kết nối dịch vụ chứng thực chữ ký số công cộng, cụ thể:
- + Thực hiện theo Hướng dẫn kết nối tại Phụ lục III ban hành kèm theo Thông tư này;
- + Cung cấp các đặc tả, thông số kỹ thuật và thông tin phục vụ kết nối cho Tổ chức cung cấp dịch vụ chứng thực điện tử quốc gia;
- + Cập nhật các thông số kỹ thuật hoặc thông tin phục vụ kết nối khi có thay đổi cho Tổ chức cung cấp dịch vụ chứng thực điện tử quốc gia.
- Các hệ thống thông tin phục vụ giao dịch điện tử sử dụng chữ ký số tích hợp với Cổng kết nối dịch vụ chứng thực chữ ký số công cộng để bảo đảm tính xác thực, tính toàn vẹn và tính chống chối bỏ của thông điệp dữ liệu, cụ thể:
- + Thực hiện theo Hướng dẫn kết nối tại Phụ lục III ban hành kèm theo Thông tư này;
- + Bảo đảm chức năng ký số của hệ thống thông tin phục vụ giao dịch điện tử sử dụng chữ ký số đáp ứng các quy định tại Điều 5 Thông tư này;
- + Tổ chức cung cấp dịch vụ chứng thực điện tử quốc gia cung cấp các đặc tả, thông số kỹ thuật và thông tin phục vụ việc kết nối đến Cổng kết nối dịch vụ chứng thực chữ ký số công cộng.
- Đầu mối hỗ trợ, hướng dẫn kết nối đến Cổng kết nối dịch vụ chứng thực chữ ký số công cộng: Trung tâm Chứng thực điện tử quốc gia, Bộ Khoa học và Công nghệ.

![](_page_5_Picture_15.jpeg)

# **4. ĐIỀU KHOẢN THI HÀNH**

### **4.1 Tổ chức thực hiện**

- Trung tâm Chứng thực điện tử quốc gia có trách nhiệm hướng dẫn thực hiện các nội dung của Thông tư này và công bố thông tin theo quy định tại điểm c khoản 2 Điều 9 Thông tư này.
- Tổ chức cung cấp dịch vụ chứng thực chữ ký số công cộng, tổ chức cung cấp dịch vụ chứng thực chữ ký điện tử chuyên dùng đảm bảo an toàn, Tổ chức cung cấp dịch vụ chứng thực chữ ký điện tử nước ngoài được công nhận tại Việt Nam có trách nhiệm công bố các đặc tả kỹ thuật (tài liệu và bộ công cụ), chứng thư chữ ký số liên quan đến tổ chức cung cấp dịch vụ chứng thực chữ ký số và các tiêu chuẩn chữ ký số trên trang tin điện tử của tổ chức cung cấp dịch vụ chứng thực chữ ký số đó.
- Tổ chức, cá nhân phát triển, sử dụng phần mềm ký số, phần mềm kiểm tra chữ ký số có trách nhiệm tuân thủ các quy định về yêu cầu kỹ thuật, hướng dẫn sử dụng đối với phần mềm ký số, phần mềm kiểm tra chữ ký số.

#### **4.2 Hiệu lực thi hành**

- Thông tư này có hiệu lực thi hành kể từ ngày tháng năm .
- Chánh Văn phòng, Giám đốc Trung tâm Chứng thực điện tử quốc gia, Thủ trưởng các cơ quan, đơn vị thuộc Bộ, Giám đốc Sở Khoa học và Công nghệ các tỉnh, thành phố trực thuộc Trung ương, tổ chức, cá nhân có liên quan chịu trách nhiệm thi hành Thông tư này.
- Trong quá trình thực hiện, nếu có khó khăn, vướng mắc, cơ quan, tổ chức, cá nhân phản ánh kịp thời về Bộ Khoa học và Công nghệ (Trung tâm Chứng thực điện tử quốc gia) để xem xét, giải quyết./.

### **Phụ lục I**

# **DANH MỤC TIÊU CHUẨN KỸ THUẬT VỀ CHỮ KÝ SỐ TRÊN THÔNG ĐIỆP DỮ LIỆU DÙNG CHO PHẦN MỀM KÝ SỐ VÀ PHẦN MỀM KIỂM TRA CHỮ KÝ SỐ**

*(Ban hành kèm theo Thông tư số /2025/TT-BKHCN ngày tháng năm 2025 của Bộ trưởng Bộ Khoa học và Công nghệ)*

| Số TT | Loại tiêu<br>chuẩn                                 | Ký hiệu<br>tiêu chuẩn        | Tên đầy đủ của tiêu<br>chuẩn                                                | Quy định áp<br>dụng                                |
|-------|----------------------------------------------------|------------------------------|-----------------------------------------------------------------------------|----------------------------------------------------|
|       |                                                    |                              | Tiêu chuẩn về định dạng thông điệp dữ liệu                                  |                                                    |
| 11    | Bộ ký tự và<br>mã hóa                              | ASCII                        | American Standard Code<br>for Information<br>Interchange                    | Khuyến nghị áp<br>dụng                             |
| 12    | Bộ ký tự và<br>mã hóa cho<br>tiếng Việt            | TCVN<br>6909:2001            | TCVN 6909:2001 " Công<br>nghệ thông tin-Bộ mã ký<br>tự tiếng Việt 16-bit"   | Bắt buộc áp<br>dụng                                |
| 13    | Trình diễn bộ<br>ký tự                             | UTF-8                        | 8-bit Universal<br>Character Set (UCS)/<br>Unicode Transformation<br>Format | Khuyến nghị áp<br>dụng                             |
| 14    | Ngôn ngữ<br>định dạng<br>thông điệp<br>dữ liệu     | XML v1.0<br>(5th<br>Edition) | Extensible Markup<br>Language version 1.0<br>(5th Edition)                  | Khuyến nghị áp<br>dụng một trong<br>hai tiêu chuẩn |
|       |                                                    | XML v1.1<br>(2nd<br>Edition) | Extensible Markup<br>Language version 1.1                                   |                                                    |
| 15    | Định nghĩa<br>các lược đồ<br>trong tài liệu<br>XML | XML<br>Schema<br>version 1.1 | XML Schema version 1.1                                                      | Khuyến nghị áp<br>dụng                             |
| 16    | Trao đổi dữ<br>liệu đặc tả<br>tài liệu XML         | XML v2.4.2                   | XML Metadata<br>Interchange version 2.4.2                                   | Khuyến nghị áp<br>dụng                             |

| 77   | Quản lý tài<br>liệu<br>-<br>Định<br>dạng tài liệu<br>di động                                                                           | ISO 32000-<br>1:2008 | Document management<br>-<br>Portable document<br>format                              | Khuyến nghị áp<br>dụng |
|------|----------------------------------------------------------------------------------------------------------------------------------------|----------------------|--------------------------------------------------------------------------------------|------------------------|
| 88   | Định dạng<br>trao đổi dữ<br>liệu theo ký<br>hiệu đối<br>tượng<br>Javascript                                                            | RFC7159              | The JavaScript Object<br>Notation (JSON) Data<br>Interchange Format                  | Khuyến nghị áp<br>dụng |
|      |                                                                                                                                        |                      | Tiêu chuẩn về ký số, kiểm tra chữ ký số                                              |                        |
| 21   | Tiêu chuẩn về ký số trên<br>thiết bị quản lý khóa bí mật, phần mềm<br>ký số, tạo chữ ký số, chứng thư số, phần mềm kiểm tra chữ ký số. |                      |                                                                                      |                        |
| 21.1 | Thuật toán<br>mã hóa                                                                                                                   | TCVN<br>7816:2007    | Công nghệ thông tin. Kỹ<br>thuật mật mã -<br>thuật toán<br>mã dữ liệu AES            | Khuyến nghị áp<br>dụng |
|      |                                                                                                                                        | NIST 800-<br>67      | Recommendation for the<br>Triple Data Encryption<br>Algorithm (TDEA) Block<br>Cipher | Khuyến nghị áp<br>dụng |
|      |                                                                                                                                        | PKCS#1               | RSA Cryptography<br>Standard<br>(Phiên bản 2.1<br>trở lên)                           | Khuyến nghị áp<br>dụng |
|      |                                                                                                                                        |                      | Áp dụng,<br>sử dụng lược<br>đồ RSAES-OAEP để mã<br>hoá                               |                        |
|      |                                                                                                                                        |                      | Độ dài khóa tối thiểu là<br>2048 bit                                                 |                        |
|      |                                                                                                                                        | ECC                  | Elliptic Curve<br>Crytography                                                        | Khuyến nghị áp<br>dụng |
| 21.2 | Thuật toán<br>chữ ký số                                                                                                                | TCVN<br>7635:2007    | Các kỹ thuật mật mã -<br>Chữ ký số                                                   |                        |

|      |                           | PKCS#1<br>ANSI<br>X9.62-2005 | RSA Cryptography<br>Standard<br>Public Key Cryptography<br>for the Financial<br>Services Industry: The<br>Elliptic Curve Digital<br>Signature Algorithm<br>(ECDSA) | -<br>Áp dụng một<br>trong ba tiêu<br>chuẩn.<br>-<br>Đối với tiêu<br>chuẩn<br>TCVN<br>7635:2007 và<br>PKCS#1:<br>+ Phiên bản 2.1<br>+ Áp dụng lược<br>đồ RSAES<br>OAEP để mã<br>hoá và RSASSA<br>PSS để ký.<br>+ Độ dài khóa<br>tối thiểu là<br>2048<br>bit<br>-<br>Đối với tiêu<br>chuẩn ECDSA:<br>độ<br>dài khóa tối<br>thiểu là 256 bit |  |
|------|---------------------------|------------------------------|--------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--|
| 21.3 | Hàm băm an<br>toàn        | FIPS PUB<br>180-4            | Secure Hash Algorithms                                                                                                                                             | Áp dụng một<br>trong các hàm                                                                                                                                                                                                                                                                                                              |  |
|      |                           | FIPS PUB<br>202              | SHA-3 Standard:<br>Permutation-Based Hash<br>and Extendable-Output<br>Functions                                                                                    | băm sau:<br>SHA-224,<br>SHA-256,<br>SHA-384,<br>SHA-512,<br>SHA-512/224,<br>SHA-512/256,<br>SHA3-224,<br>SHA3-256,<br>SHA3-384,<br>SHA3-512,<br>SHAKE128,<br>SHAKE256                                                                                                                                                                     |  |
| 21.4 | Cú pháp mã<br>hóa và cách | XML<br>Encryption            | XML Encryption Syntax<br>and Processing                                                                                                                            | Bắt buộc áp<br>dụng                                                                                                                                                                                                                                                                                                                       |  |

|      | xử lý thông<br>điệp dữ liệu                                                                          | Syntax and<br>Processing                     |                                                                                                             |                                                                 |  |
|------|------------------------------------------------------------------------------------------------------|----------------------------------------------|-------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------|--|
|      | định dạng<br>XML                                                                                     | XML<br>Signature<br>Syntax and<br>Processing | XML Signature Syntax<br>and Processing                                                                      | Bắt buộc áp<br>dụng                                             |  |
| 21.5 | Quản lý khóa<br>công khai<br>thông điệp<br>dữ liệu định<br>dạng XML                                  | XKMS v2.0                                    | XML Key Management<br>Specification version 2.0                                                             | Bắt buộc áp<br>dụng                                             |  |
| 21.6 | Cú pháp<br>thông điệp<br>mật mã cho<br>ký, mã hóa                                                    | PKCS#7<br>v1.5 (RFC<br>2315)                 | Cryptographic message<br>syntax for file-based<br>signing and encrypting<br>version 1.5                     | Bắt buộc áp<br>dụng                                             |  |
| 11.7 | Tiêu chuẩn<br>về chữ ký<br>điện tử nâng<br>cao dành cho<br>thông điệp<br>dữ liệu định<br>dạng<br>PDF | ETSI EN<br>319 142-1                         | Electronic Signatures<br>and Infrastructures (ESI)<br>-<br>PAdES digital<br>signatures                      | Áp dụng một<br>trong hai tiêu<br>chuẩn PAdES<br>hoặc CAdES      |  |
| 11.8 | Tiêu chuẩn<br>về chữ ký<br>điện tử nâng<br>cao dành cho<br>thông điệp<br>dữ liệu định<br>dạng XML    | ETSI TS<br>101 903                           | Electronic Signatures<br>and Infrastructures (ESI)<br>-<br>XML Advanced<br>Electronic Signatures<br>(XAdES) | Áp dụng một<br>trong hai tiêu<br>chuẩn XAdES<br>hoặc CAdES      |  |
| 11.9 | Tiêu chuẩn<br>về chữ ký<br>điện tử nâng<br>cao dành cho<br>thông điệp<br>dữ liệu định<br>dạng JSON   | RFC 7515                                     | JSON Web Signature<br>(JWS)                                                                                 | Bắt buộc áp<br>dụng cho thông<br>điệp dữ liệu định<br>dạng JSON |  |

| 11.10                                               | Tiêu chuẩn<br>về chữ ký<br>điện tử nâng<br>cao dành cho<br>cú pháp tin<br>nhắn mật mã                                                          | ETSI TS<br>101 733                                                                                                                                                                      | Electronic Signatures<br>and Infrastructures (ESI)<br>-<br>CMS Advanced<br>Electronic Signatures<br>(CAdES)                                                                                                               | Khuyến nghị áp<br>dụng                                                  |
|-----------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------------------------------------------------------|
| .2                                                  |                                                                                                                                                |                                                                                                                                                                                         | Tiêu chuẩn về hệ thống, thiết bị lưu trữ và sử dụng khóa bí mật                                                                                                                                                           |                                                                         |
| 22.1                                                | Yêu cầu an<br>toàn dành<br>cho mô đun<br>bảo mật<br>phần cứng                                                                                  | FIPS PUB<br>140-2                                                                                                                                                                       | Security Requirements<br>for Cryptographic<br>Modules                                                                                                                                                                     | -<br>Yêu cầu tối<br>thiểu mức 3<br>(level 3)                            |
| 22.2                                                | Yêu cầu an<br>toàn đối với<br>thẻ Token và<br>Smart card                                                                                       | FIPS PUB<br>140-2                                                                                                                                                                       | Security Requirements<br>for Cryptographic<br>Modules                                                                                                                                                                     | -<br>Yêu cầu tối<br>thiểu mức 2<br>(level 2)                            |
| .2.3                                                | Yêu cầu về<br>chính sách<br>và an toàn<br>cho các tổ<br>chức cung<br>cấp dịch vụ<br>tin cậy: Các<br>thành phần<br>dịch vụ vận<br>hành thiết bị | ETSI TS<br>119 431-1<br>ETSI TS                                                                                                                                                         | Electronic Signatures<br>and Infrastructures<br>(ESI); Policy and<br>security requirements for<br>trust service providers;<br>Part 1: TSP service<br>components operating a<br>remote QSCD/SCDev<br>Electronic Signatures | Áp dụng cả bộ<br>tiêu chuẩn 2<br>phần;<br>Phiên bản V1.1.1<br>(12/2018) |
| tạo chữ ký số<br>và hỗ trợ tạo<br>chữ ký số<br>AdES | 119 431-2                                                                                                                                      | and Infrastructures<br>(ESI); Policy and<br>security requirements for<br>trust service providers;<br>Part 2: TSP service<br>components supporting<br>AdES digital signature<br>creation |                                                                                                                                                                                                                           |                                                                         |
| .2.4                                                | Giao thức<br>tạo chữ ký số<br>từ xa                                                                                                            | ETSI TS<br>119 432                                                                                                                                                                      | Electronic Signatures<br>and Infrastructures<br>(ESI); Protocols for                                                                                                                                                      | Phiên bản V1.1.1<br>(03/2019)                                           |

|      |                                                                                                                                                                                               |                         | remote digital signature<br>creation                                                                                  |                                                        |
|------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-------------------------|-----------------------------------------------------------------------------------------------------------------------|--------------------------------------------------------|
| .2.5 | Hệ thống tin<br>cậy hỗ trợ ký<br>số từ xa -<br>Các yêu cầu<br>chung                                                                                                                           | EN<br>419241-<br>1:2018 | Trustworthy Systems<br>Supporting Server<br>Signing -<br>Part 1: General<br>system security<br>requirements           |                                                        |
| .2.6 | Hệ thống tin<br>cậy hỗ trợ ký<br>số từ xa –<br>Yêu cầu và<br>mục tiêu<br>(hồ<br>sơ<br>bảo vệ)<br>của thiết bị<br>tạo chữ ký số<br>dành cho ký<br>số từ xa                                     | EN<br>419241-<br>2:2019 | Trustworthy Systems<br>Supporting Server<br>Signing -<br>Part 2:<br>Protection Profile for<br>QSCD for Server Signing |                                                        |
| .2.7 | Yêu cầu và<br>mục tiêu<br>(hồ<br>sơ bảo vệ)<br>dành cho mô<br>đun bảo mật<br>phần cứng<br>của tổ chức<br>cung cấp dịch<br>vụ tin cậy –<br>mô đun mã<br>hóa dành cho<br>các dịch vụ<br>tin cậy | EN<br>419221-<br>5:2018 | Protection Profiles for<br>TSP Cryptographic<br>modules -<br>Part 5:<br>Cryptographic Module<br>for Trust Services    |                                                        |
| 33   | Tiêu chuẩn kiểm tra trạng thái chứng thư số                                                                                                                                                   |                         |                                                                                                                       |                                                        |
| 33.1 | Giao thức<br>truyền, nhận<br>chứng thư<br>chữ ký số<br>và<br>danh sách<br>chứng thư                                                                                                           | RFC 2585                | Internet X.509 Public<br>Key Infrastructure -<br>Operational Protocols:<br>FTP and HTTP                               | Áp dụng một<br>hoặc cả hai giao<br>thức FTP và<br>HTTP |

|      | chữ ký số<br>bị<br>thu hồi                                                     |          |                                                                                            |                                  |
|------|--------------------------------------------------------------------------------|----------|--------------------------------------------------------------------------------------------|----------------------------------|
| 33.2 | Giao thức<br>bảo mật tầng<br>giao vận                                          | RFC 8446 | The Transport Layer<br>Security (TLS) Protocol<br>Version 1.3                              | Bắt buộc áp<br>dụng<br>tối thiểu |
| 33.3 | Giao thức<br>cho kiểm tra<br>trạng thái<br>chứng thư<br>chữ ký sốtrực<br>tuyến | RFC 2560 | X.509 Internet Public<br>Key Infrastructure -<br>On<br>line Certificate status<br>protocol |                                  |

### **Phụ lục II**

# **DANH MỤC TIÊU CHÍ ĐÁNH GIÁ HIỆU LỰC CỦA CHỨNG THƯ CHỮ KÝ SỐ VÀ CHỮ KÝ SỐ HỢP LỆ TRONG PHẦN MỀM KÝ SỐ, PHẦN MỀM KIỂM TRA CHỮ KÝ SỐ**

*(Ban hành kèm theo Thông tư số /2025/TT-BKHCN ngày tháng năm 2025 của Bộ trưởng Bộ Khoa học và Công nghệ)*

| Số TT | Tiêu chí đánh giá                                                                                                                                                                                                                                                                                                                     | Hiệu lực/hợp lệ                                                                                                                                                                                                      | Quy định áp dụng |  |  |
|-------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|------------------|--|--|
| 1     | Tính hiệu lực của chứng thư chữ ký số                                                                                                                                                                                                                                                                                                 |                                                                                                                                                                                                                      |                  |  |  |
| 1.1   | Thời gian có hiệu lực của chứng<br>thư số                                                                                                                                                                                                                                                                                             | Thời gian trên chứng<br>thư chữ ký số<br>còn<br>hiệu lực tại thời<br>điểm ký số                                                                                                                                      | Bắt buộc áp dụng |  |  |
| 1.2   | Trạng thái chứng thư số qua danh<br>sách chứng thư chữ ký số<br>thu hồi<br>(CRL) được công bố tại thời điểm<br>ký số hoặc bằng phương pháp<br>kiểm tra trạng thái chứng thư chữ<br>ký số<br>trực tuyến (OCSP) ở chế độ<br>trực tuyến trong trường hợp tổ<br>chức cung cấp dịch vụ chứng thực<br>chữ ký số có cung cấp dịch vụ<br>OCSP | Trạng thái của<br>chứng thư chữ ký số<br>còn hoạt động tại<br>thời điểm ký số                                                                                                                                        | Bắt buộc áp dụng |  |  |
| 1.3   | Thuật toán mật mã trên chứng thư<br>chữ ký số                                                                                                                                                                                                                                                                                         | Các thuật toán mật<br>mã trên chứng thư<br>chữ ký số<br>tuân thủ<br>theo quy định về quy<br>chuẩn, tiêu chuẩn kỹ<br>thuật bắt buộc áp<br>dụng về chữ ký số và<br>dịch vụ chứng thực<br>chữ ký số đang có<br>hiệu lực | Bắt buộc áp dụng |  |  |
| 1.4   | Mục đích, phạm vi sử dụng của<br>chứng thư chữ ký số                                                                                                                                                                                                                                                                                  | Chứng thư chữ ký số<br>được sử dụng đúng<br>mục đích, phạm vi sử<br>dụng                                                                                                                                             | Bắt buộc áp dụng |  |  |

| 1.5 | Các tuyên bố khác của Tổ chức<br>cung cấp dịch vụ chứng thực chữ<br>ký số | Các tuyên bố khác<br>không nằm ngoài<br>phạm vi Quy chế<br>chứng thực của Tổ<br>chức cung cấp dịch<br>vụ chứng thực chữ<br>ký số | Khuyến nghị áp<br>dụng |  |  |
|-----|---------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------|------------------------|--|--|
| 2   | Tính hợp lệ của chữ ký số                                                 |                                                                                                                                  |                        |  |  |
| 2.1 | Thông tin về chủ thể ký                                                   | Kiểm tra, xác thực<br>được đúng thông tin<br>chủ thể<br>ký số                                                                    | Bắt buộc áp dụng       |  |  |
| 2.2 | Cách thức tạo chữ ký số                                                   | Chữ ký số được tạo<br>ra đúng bởi khóa bí<br>mật tương ứng với<br>khóa công khai trên<br>chứng thư chữ ký số                     | Bắt buộc áp dụng       |  |  |
| 2.3 | Chứng thư chữ ký số kèm theo<br>thông điệp dữ liệu                        | Chứng thư chữ ký số<br>có hiệu lực tại thời<br>điểm ký                                                                           | Bắt buộc áp dụng       |  |  |
| 2.4 | Tính toàn vẹn của thông điệp dữ<br>liệu                                   | Mã băm có được từ<br>việc băm thông điệp<br>dữ liệu và mã băm<br>có được khi giải mã<br>chữ ký số trùng nhau                     | Bắt buộc áp dụng       |  |  |

### **Phụ lục III**

# **HƯỚNG DẪN KẾT NỐI ĐẾN CỔNG KẾT NỐI DỊCH VỤ CHỨNG THỰC CHỮ KÝ SỐ CÔNG CỘNG**

*(Ban hành kèm theo Thông tư số /2025/TT-BKHCN ngày tháng năm 2025 của Bộ trưởng Bộ Khoa học và Công nghệ)*

# **1. Mô hình kết nối**

Mô hình kết nối với Cổng kết nối dịch vụ chứng thực chữ ký số công cộng (sau đây gọi là Cổng eSign) được mô tả tại sơ đồ như sau:

![](_page_16_Picture_6.jpeg)

### Chú thích:

- HTTT: Hệ thống thông tin phục vụ giao dịch điện tử sử dụng chữ ký số.
- CA: Tổ chức cung cấp dịch vụ chứng thực chữ ký số công cộng.

# **2. Các thông tin hướng dẫn kết nối**

- a) Giao thức sử dụng để kết nối là API, phương thức kết nối là POST.
- b) Đường dẫn kết nối các API: [https://esign.neac.gov.vn](https://esign.neac.gov.vn/)
- c) Thông tin Cổng eSign cung cấp cho các HTTT gồm: sp\_id và sp\_password hoặc token, trong đó:
  - sp\_id: Mã xác thực được cấp cho HTTT.
  - sp\_password: Mật khẩu kết nối được cấp cho HTTT tương ứng với sp\_id.
  - token: Thông tin xác thực được cấp cho HTTT.