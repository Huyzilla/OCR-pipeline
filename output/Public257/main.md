# Public_257
<table>
<colgroup>
<col/>
<col/>
<col/>
</colgroup>
<thead>
<tr>
<th rowspan="2">|<image_1>|</th>
<th><strong>VIETTEL AI RACE</strong></th>
<th>Public 257</th>
</tr>
<tr>
<th><strong>Quy định yêu cầu kỹ thuật đối với phần mềm ký số, phần mềm
kiểm tra chữ ký số và Cổng kết nối dịch vụ chứng thực chữ ký số công
cộng</strong></th>
<th>Lần ban hành: 1</th>
</tr>
</thead>
<tbody>
</tbody>
</table> 

_Căn cứ Luật giao dịch điện tử ngày 22 tháng 06 năm 2023;_

_Căn cứ Nghị định số 23/2025/NĐ-CP ngày 21 tháng 02 năm 2025 của Chính phủ quy định về chữ ký điện tử và dịch vụ tin cậy;_

_Căn cứ Nghị định số 55/2025/NĐ-CP ngày 02 tháng 3 năm 2025 của Chính phủ quy định chức năng, nhiệm vụ và cơ cấu tổ chức của Bộ Khoa học và Công nghệ;_

_Theo đề nghị của Vụ trưởng Vụ Pháp chế và Giám đốc Trung tâm Chứng thực điện tử quốc gia;_

_Bộ trưởng Bộ Khoa học và Công nghệ ban hành Thông tư quy định yêu cầu kỹ thuật đối với phần mềm ký số, phần mềm kiểm tra chữ ký số và Cổng kết nối dịch vụ chứng thực chữ ký số công cộng._

# 1\. QUY ĐỊNH CHUNG

## 1.1. Phạm vi điều chỉnh

Thông tư này quy định yêu cầu kỹ thuật đối với phần mềm ký số, phần mềm kiểm tra chữ ký số và Cổng kết nối dịch vụ chứng thực chữ ký số công cộng.

## 1.2 . Đối tượng áp dụng

Thông tư này áp dụng đối với tổ chức, cá nhân sử dụng phần mềm ký số, phần mềm kiểm tra chữ ký số; các tổ chức, cá nhân phát triển phần mềm ký số, phần mềm kiểm tra chữ ký số; các tổ chức cung cấp dịch vụ chứng thực chữ ký số; các tổ chức cung cấp dịch vụ chứng thực chữ ký điện tử chuyên dùng đảm bảo an toàn; các tổ chức cung cấp dịch vụ chứng thực chữ ký điện tử nước ngoài được công nhận tại Việt Nam; chủ quản các hệ thống thông tin phục vụ giao dịch điện tử có sử dụng chữ ký số và các tổ chức, cá nhân có liên quan khác.

## 1.3. Giải thích từ ngữ

Trong Thông tư này, các từ ngữ dưới đây được hiểu như sau:

\- “Cặp khóa bất đối xứng” là khóa công khai và khóa bí mật tương ứng.

\- “Khóa bí mật” là thành phần của cặp khóa bất đối xứng được sử dụng để ký thông điệp dữ liệu.

\- “Khóa công khai” là thành phần của cặp khóa bất đối xứng được sử dụng để xác thực chữ ký số trên thông điệp dữ liệu.

\- “Chủ thể ký” là cá nhân hoặc tổ chức sở hữu chứng thư chữ ký số và sử dụng khóa bí mật tương ứng để thực hiện ký số trên thông điệp dữ liệu.

\- “Chứng thư chữ ký số” là một dạng chứng thư điện tử do tổ chức cung cấp dịch vụ chứng thực chữ ký số cấp nhằm cung cấp thông tin về khóa công khai của một cá nhân, tổ chức từ đó xác nhận cá nhân, tổ chức là chủ thể ký thông qua việc sử dụng khóa bí mật tương ứng.

\- “Phần mềm ký số” là chương trình độc lập hoặc một thành phần (module) phần mềm hoặc giải pháp có chức năng ký số vào thông điệp dữ liệu.

\- "Phần mềm kiểm tra chữ ký số" là chương trình độc lập hoặc một thành phần (module) phần mềm hoặc giải pháp có chức năng kiểm tra tính hợp lệ của chữ ký số trên thông điệp dữ liệu đã ký.

\- "Đường dẫn tin cậy của chứng thư chữ ký số" là thông tin đường dẫn trên chứng thư chữ ký số xác thực tổ chức cung cấp dịch vụ chứng thực chữ ký số đã cấp phát ra chứng thư chữ ký số đó.

# 2\. Yêu cầu kỹ thuật đối với chức năng phần mềm ký số, phần mềm kiểm tra chữ ký số

## 2.1 Yêu cầu chung

Tuân thủ các yêu cầu và tiêu chuẩn kỹ thuật về chữ ký số trên thông điệp dữ liệu tại Phụ lục I ban hành kèm theo Thông tư này.

## 2.2 Yêu cầu về chức năng

\- Chức năng xác thực chủ thể ký và ký số:

\+ Kiểm tra được thông tin chủ thể ký trên chứng thư chữ ký số;

\+ Cho phép chủ thể ký sử dụng khóa bí mật để thực hiện việc ký số vào thông điệp dữ liệu. Khoá bí mật lưu trong thiết bị được chủ thể ký sử dụng để ký số phải tuân thủ các yêu cầu và tiêu chuẩn kỹ thuật tại Phụ lục I ban hành kèm theo Thông tư này;

\+ Cho phép chuyển đổi định dạng thông điệp dữ liệu thành các định dạng được nêu tại Phụ lục I ban hành kèm theo Thông tư này;

\+ Gắn kèm chữ ký số và chứng thư chữ ký số vào thông điệp dữ liệu sau khi ký số;

\+ Hỗ trợ cài đặt, tích hợp chứng thư chữ ký số của Tổ chức cung cấp dịch vụ chứng thực chữ ký số quốc gia và chứng thư chữ ký số thuộc Danh sách tin cậy chứng thư chữ ký điện tử nước ngoài được công nhận tại Việt Nam;

\+ Đáp ứng các giao thức gửi nhận thông điệp dữ liệu của phần mềm ký số theo các yêu cầu và tiêu chuẩn tại Phụ lục I ban hành kèm theo Thông tư này.

\- Chức năng kiểm tra hiệu lực của chứng thư chữ ký số:

\+ Thông tin trong chứng thư chữ ký số được định danh theo quy định pháp luật về định danh và xác thực điện tử;

\+ Chứng thư chữ ký số của chủ thể ký phải được kiểm tra theo đường dẫn tin cậy của chứng thư chữ ký số đó và phải liên kết đến chứng thư chữ ký số gốc của Tổ chức cung cấp dịch vụ chứng thực chữ ký số quốc gia hoặc thuộc Danh sách tin cậy chứng thư chữ ký điện tử nước ngoài được công nhận tại Việt Nam;

\+ Chứng thư chữ ký số phải có hiệu lực tại thời điểm ký số và đáp ứng các tiêu chí tại Phụ lục II ban hành kèm theo Thông tư này.

\- Chức năng kết nối đến Cổng kết nối dịch vụ chứng thực chữ ký số công cộng: Hướng dẫn kết nối được quy định tại Chương III Thông tư này.

\- Chức năng lưu trữ và hủy bỏ các thông tin kèm theo thông điệp dữ liệu ký số, bao gồm:

\+ Chứng thư chữ ký số tương ứng với khóa bí mật mà chủ thể ký sử dụng để ký thông điệp dữ liệu tại thời điểm ký số;

\+ Danh sách chứng thư chữ ký số thu hồi tại thời điểm ký trong chứng thư chữ ký số của chủ thể ký;

\+ Quy chế chứng thực của tổ chức cung cấp dịch vụ chứng thực chữ ký số đã cấp chứng thư chữ ký số tương ứng với chữ ký số trên thông điệp dữ liệu;

\+ Kết quả kiểm tra trạng thái chứng thư chữ ký số tương ứng với chữ ký số trên thông điệp dữ liệu đã ký.

\- Chức năng thay đổi (thêm, bớt) chứng thư chữ ký số của cơ quan, tổ chức tạo lập cấp, phát hành chứng thư chữ ký số:

Cho phép tích hợp và hiển thị đầy đủ các tổ chức cung cấp dịch vụ chứng thực chữ ký số và Danh sách tin cậy chứng thư chữ ký điện tử nước ngoài được công nhận tại Việt Nam.

\- Chức năng thông báo bằng chữ hoặc ký hiệu cho chủ thể ký biết việc ký số vào thông điệp dữ liệu thành công hay không thành công, bao gồm việc:

\+ Hiển thị thông báo ký số thành công hoặc không thành công;

\+ Xem được thông điệp dữ liệu đã ký sau khi hoàn thành ký số;

\+ Tải được thông điệp dữ liệu đã ký về thiết bị.

## 2.3 Yêu cầu chung

Tuân thủ các yêu cầu và tiêu chuẩn kỹ thuật về chữ ký số trên thông điệp dữ liệu tại Phụ lục I ban hành kèm theo Thông tư này.

## 2.4 Yêu cầu về chức năng

\- Chức năng kiểm tra tính hợp lệ của chữ ký số trên thông điệp dữ liệu:

\+ Cho phép xác thực chữ ký số trên thông điệp dữ liệu theo nguyên tắc chữ ký số được tạo ra đúng với khóa bí mật tương ứng với khóa công khai trên chứng thư chữ ký số;

\+ Cho phép kiểm tra chứng thư chữ ký số của chủ thể ký theo đường dẫn tin cậy của chứng thư chữ ký số đó và phải liên kết đến Tổ chức cung cấp dịch vụ chứng thực chữ ký số quốc gia hoặc thuộc Danh sách tin cậy chứng thư chữ ký điện tử nước ngoài được công nhận tại Việt Nam;

\+ Bảo đảm chứng thư chữ ký số phải có hiệu lực tại thời điểm ký số và đáp ứng các tiêu chí tại Phụ lục II ban hành kèm theo Thông tư này;

\+ Cho phép kiểm tra tính toàn vẹn của thông điệp dữ liệu ký số theo các bước sau:

\- Giải mã chữ ký số trên thông điệp dữ liệu để có thông tin về mã băm của thông điệp dữ liệu;

\- Sử dụng thuật toán hàm băm an toàn đã tạo ra mã băm trên chữ ký số để thực hiện tạo mã băm cho thông điệp dữ liệu;

\- So sánh sự trùng khớp của hai mã băm để kiểm tra tính toàn vẹn của thông điệp dữ liệu ký số.

\+ Đảm bảo tính hợp lệ của chữ ký số trên thông điệp dữ liệu đã ký theo các tiêu chí tại Phụ lục II ban hành kèm theo Thông tư này;

\+ Hỗ trợ cài đặt, tích hợp chứng thư chữ ký số của Tổ chức cung cấp dịch vụ chứng thực chữ ký số quốc gia và chứng thư chữ ký số thuộc danh sách tin cậy chứng thư chữ ký điện tử nước ngoài được công nhận tại Việt Nam;

\+ Đáp ứng các giao thức gửi nhận thông điệp dữ liệu của phần mềm ký số theo tiêu chuẩn tại Phụ lục I ban hành kèm theo Thông tư này.

\- Chức năng lưu trữ và hủy bỏ các thông tin kèm theo thông điệp dữ liệu ký số:

\+ Chứng thư chữ ký số tương ứng với chữ ký số trên thông điệp dữ liệu đã ký;

\+ Danh sách chứng thư chữ ký số thu hồi tại thời điểm ký được thể hiện trong chứng thư chữ ký số đính kèm thông điệp dữ liệu đã ký;

\+ Quy chế chứng thực của các tổ chức cung cấp dịch vụ chứng thực chữ ký số cấp phát chứng thư chữ ký số tương ứng với các chữ ký số trên thông điệp dữ liệu đã ký;

\+ Kết quả kiểm tra trạng thái chứng thư chữ ký số tương ứng với chữ ký số trên thông điệp dữ liệu đã ký.

\- Chức năng thay đổi (thêm, bớt) chứng thư chữ ký số của cơ quan, tổ chức tạo lập, cấp, phát hành chứng thư chữ ký số.

\- Chức năng thông báo bằng chữ hoặc ký hiệu việc kiểm tra tính hợp lệ của chữ ký số là hợp lệ hay không hợp lệ:

\+ Hiển thị thông báo chữ ký số trên thông điệp dữ liệu đã ký hợp lệ hay không hợp lệ;

\+ Hiển thị các thông tin về chữ ký số và chứng thư chữ ký số trên thông điệp dữ liệu đã ký, với tối thiểu các trường thông tin sau: thông tin về cơ quan, tổ chức tạo lập, cấp, phát hành chứng thư chữ ký số; thông tin về chủ thể ký; thông tin về thời điểm ký số hoặc dấu thời gian (nếu có); tính toàn vẹn của thông điệp dữ liệu đã ký; tính hợp lệ của chữ ký số tại thời điểm ký.

# 3\. CỔNG KẾT NỐI DỊCH VỤ CHỨNG THỰC CHỮ KÝ SỐ CÔNG CỘNG

## 3.1 Cổng kết nối dịch vụ chứng thực chữ ký số công cộng

Cổng kết nối dịch vụ chứng thực chữ ký số công cộng là hệ thống thông tin phục vụ kết nối dịch vụ chứng thực chữ ký số công cộng với các hệ thống thông tin phục vụ giao dịch điện tử sử dụng chữ ký số để bảo đảm tính xác thực, tính toàn vẹn và tính chống chối bỏ của thông điệp dữ liệu.

## 3.2 Kết nối đến Cổng kết nối dịch vụ chứng thực chữ ký số công cộng

\- Các tổ chức cung cấp dịch vụ chứng thực chữ ký số công cộng kết nối đến Cổng kết nối dịch vụ chứng thực chữ ký số công cộng, cụ thể:

\+ Thực hiện theo Hướng dẫn kết nối tại Phụ lục III ban hành kèm theo Thông tư này;

\+ Cung cấp các đặc tả, thông số kỹ thuật và thông tin phục vụ kết nối cho Tổ chức cung cấp dịch vụ chứng thực điện tử quốc gia;

\+ Cập nhật các thông số kỹ thuật hoặc thông tin phục vụ kết nối khi có thay đổi cho Tổ chức cung cấp dịch vụ chứng thực điện tử quốc gia.

\- Các hệ thống thông tin phục vụ giao dịch điện tử sử dụng chữ ký số tích hợp với Cổng kết nối dịch vụ chứng thực chữ ký số công cộng để bảo đảm tính xác thực, tính toàn vẹn và tính chống chối bỏ của thông điệp dữ liệu, cụ thể:

\+ Thực hiện theo Hướng dẫn kết nối tại Phụ lục III ban hành kèm theo Thông tư này;

\+ Bảo đảm chức năng ký số của hệ thống thông tin phục vụ giao dịch điện tử sử dụng chữ ký số đáp ứng các quy định tại Điều 5 Thông tư này;

\+ Tổ chức cung cấp dịch vụ chứng thực điện tử quốc gia cung cấp các đặc tả, thông số kỹ thuật và thông tin phục vụ việc kết nối đến Cổng kết nối dịch vụ chứng thực chữ ký số công cộng.

\- Đầu mối hỗ trợ, hướng dẫn kết nối đến Cổng kết nối dịch vụ chứng thực chữ ký số công cộng: Trung tâm Chứng thực điện tử quốc gia, Bộ Khoa học và Công nghệ.

# 4\. ĐIỀU KHOẢN THI HÀNH

## 4.1 Tổ chức thực hiện

\- Trung tâm Chứng thực điện tử quốc gia có trách nhiệm hướng dẫn thực hiện các nội dung của Thông tư này và công bố thông tin theo quy định tại điểm c khoản 2 Điều 9 Thông tư này.

\- Tổ chức cung cấp dịch vụ chứng thực chữ ký số công cộng, tổ chức cung cấp dịch vụ chứng thực chữ ký điện tử chuyên dùng đảm bảo an toàn, Tổ chức cung cấp dịch vụ chứng thực chữ ký điện tử nước ngoài được công nhận tại Việt Nam có trách nhiệm công bố các đặc tả kỹ thuật (tài liệu và bộ công cụ), chứng thư chữ ký số liên quan đến tổ chức cung cấp dịch vụ chứng thực chữ ký số và các tiêu chuẩn chữ ký số trên trang tin điện tử của tổ chức cung cấp dịch vụ chứng thực chữ ký số đó.

\- Tổ chức, cá nhân phát triển, sử dụng phần mềm ký số, phần mềm kiểm tra chữ ký số có trách nhiệm tuân thủ các quy định về yêu cầu kỹ thuật, hướng dẫn sử dụng đối với phần mềm ký số, phần mềm kiểm tra chữ ký số.

## 4.2 Hiệu lực thi hành

\- Thông tư này có hiệu lực thi hành kể từ ngày tháng năm .

\- Chánh Văn phòng, Giám đốc Trung tâm Chứng thực điện tử quốc gia, Thủ trưởng các cơ quan, đơn vị thuộc Bộ, Giám đốc Sở Khoa học và Công nghệ các tỉnh, thành phố trực thuộc Trung ương, tổ chức, cá nhân có liên quan chịu trách nhiệm thi hành Thông tư này.

\- Trong quá trình thực hiện, nếu có khó khăn, vướng mắc, cơ quan, tổ chức, cá nhân phản ánh kịp thời về Bộ Khoa học và Công nghệ (Trung tâm Chứng thực điện tử quốc gia) để xem xét, giải quyết./.
<table>
<colgroup>
<col/>
<col/>
</colgroup>
<tbody>
</tbody>
</table> 

**Phụ lục I**

**DANH MỤC TIÊU CHUẨN KỸ THUẬT VỀ CHỮ KÝ SỐ  
TRÊN THÔNG ĐIỆP DỮ LIỆU DÙNG CHO PHẦN MỀM KÝ SỐ VÀ PHẦN MỀM KIỂM TRA CHỮ KÝ SỐ**

_(Ban hành kèm theo Thông tư số /2025/TT-BKHCN ngày tháng năm 2025 của Bộ trưởng Bộ Khoa học và Công nghệ)_
<table>
<colgroup>
<col/>
<col/>
<col/>
<col/>
<col/>
</colgroup>
<thead>
<tr>
<th><em><strong>Số TT</strong></em></th>
<th><em><strong>Loại tiêu chuẩn</strong></em></th>
<th><em><strong>Ký hiệu tiêu chuẩn</strong></em></th>
<th><em><strong>Tên đầy đủ của tiêu chuẩn</strong></em></th>
<th><em><strong>Quy định áp dụng</strong></em></th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="5"><em><strong>Tiêu chuẩn về định dạng thông điệp dữ
liệu</strong></em></td>
</tr>
<tr>
<td><em>11</em></td>
<td><em>Bộ ký tự và mã hóa</em></td>
<td><em>ASCII</em></td>
<td><em>American Standard Code for Information Interchange</em></td>
<td><em>Khuyến nghị áp dụng</em></td>
</tr>
<tr>
<td><em>12</em></td>
<td><em>Bộ ký tự và mã hóa cho tiếng Việt</em></td>
<td><p><em>TCVN</em></p>
<p><em>6909:2001</em></p></td>
<td><em>TCVN 6909:2001 “ Công nghệ thông tin-Bộ mã ký tự tiếng Việt
16-bit”</em></td>
<td><em>Bắt buộc áp dụng</em></td>
</tr>
<tr>
<td><em>13</em></td>
<td><em>Trình diễn bộ ký tự</em></td>
<td><em>UTF-8</em></td>
<td><em>8-bit Universal Character Set (UCS)/ Unicode Transformation
Format</em></td>
<td><em>Khuyến nghị áp dụng</em></td>
</tr>
<tr>
<td rowspan="2"><em>14</em></td>
<td rowspan="2"><em>Ngôn ngữ định dạng thông điệp dữ liệu</em></td>
<td><p><em>XML v1.0</em></p>
<p><em>(5th Edition)</em></p></td>
<td><em>Extensible Markup Language version 1.0 (5th Edition)</em></td>
<td rowspan="2"><em>Khuyến nghị áp dụng một trong hai tiêu
chuẩn</em></td>
</tr>
<tr>
<td><em>XML v1.1 (2nd Edition)</em></td>
<td><em>Extensible Markup Language version 1.1</em></td>
</tr>
<tr>
<td><em>15</em></td>
<td><em>Định nghĩa các lược đồ trong tài liệu XML</em></td>
<td><em>XML Schema version 1.1</em></td>
<td><em>XML Schema version 1.1</em></td>
<td><em>Khuyến nghị áp dụng</em></td>
</tr>
<tr>
<td><em>16</em></td>
<td><em>Trao đổi dữ liệu đặc tả tài liệu XML</em></td>
<td><em>XML v2.4.2</em></td>
<td><em>XML Metadata Interchange version 2.4.2</em></td>
<td><em>Khuyến nghị áp dụng</em></td>
</tr>
<tr>
<td><em>77</em></td>
<td><em>Quản lý tài liệu - Định dạng tài liệu di động</em></td>
<td><em>ISO 32000-1:2008</em></td>
<td><em>Document management - Portable document format</em></td>
<td><em>Khuyến nghị áp dụng</em></td>
</tr>
<tr>
<td><em>88</em></td>
<td><em>Định dạng trao đổi dữ liệu theo ký hiệu đối tượng
Javascript</em></td>
<td><em>RFC7159</em></td>
<td><em>The JavaScript Object Notation (JSON) Data Interchange
Format</em></td>
<td><em>Khuyến nghị áp dụng</em></td>
</tr>
<tr>
<td colspan="5"><em><strong>Tiêu chuẩn về ký số, kiểm tra chữ ký
số</strong></em></td>
</tr>
<tr>
<td><em><strong>21</strong></em></td>
<td colspan="4"><em><strong>Tiêu chuẩn về ký số trên thiết bị quản lý
khóa bí mật, phần mềm ký số, tạo chữ ký số, chứng thư số, phần mềm kiểm
tra chữ ký số.</strong></em></td>
</tr>
<tr>
<td rowspan="4"><em>21.1</em></td>
<td rowspan="4"><em>Thuật toán mã hóa</em></td>
<td><em>TCVN 7816:2007</em></td>
<td><em>Công nghệ thông tin. Kỹ thuật mật mã - thuật toán mã dữ liệu
AES</em></td>
<td><em>Khuyến nghị áp dụng</em></td>
</tr>
<tr>
<td><em>NIST 800-67</em></td>
<td><em>Recommendation for the Triple Data Encryption Algorithm (TDEA)
Block Cipher</em></td>
<td><em>Khuyến nghị áp dụng</em></td>
</tr>
<tr>
<td><em>PKCS#1</em></td>
<td><p><em>RSA Cryptography Standard (Phiên bản 2.1 trở lên)</em></p>
<p><em>Áp dụng, sử dụng lược đồ RSAES-OAEP để mã hoá</em></p>
<p><em>Độ dài khóa tối thiểu là 2048 bit</em></p></td>
<td><em>Khuyến nghị áp dụng</em></td>
</tr>
<tr>
<td><em>ECC</em></td>
<td><em>Elliptic Curve Crytography</em></td>
<td><em>Khuyến nghị áp dụng</em></td>
</tr>
<tr>
<td rowspan="3"><em>21.2</em></td>
<td rowspan="3"><em>Thuật toán chữ ký số</em></td>
<td><em>TCVN 7635:2007</em></td>
<td><em>Các kỹ thuật mật mã - Chữ ký số</em></td>
<td rowspan="3"><p><em>- Áp dụng một trong ba tiêu chuẩn.</em></p>
<p><em>- Đối với tiêu chuẩn TCVN 7635:2007 và PKCS#1:</em></p>
<p><em>+ Phiên bản 2.1</em></p>
<p><em>+ Áp dụng lược đồ RSAES-OAEP để mã hoá và RSASSA-PSS để
ký.</em></p>
<p><em>+ Độ dài khóa tối thiểu là 2048 bit</em></p>
<p><em>- Đối với tiêu chuẩn ECDSA: độ dài khóa tối thiểu là 256
bit</em></p></td>
</tr>
<tr>
<td><em>PKCS#1</em></td>
<td><em>RSA Cryptography Standard</em></td>
</tr>
<tr>
<td><em>ANSI X9.62-2005</em></td>
<td><em>Public Key Cryptography for the Financial Services Industry: The
Elliptic Curve Digital Signature Algorithm (ECDSA)</em></td>
</tr>
<tr>
<td rowspan="2"><em>21.3</em></td>
<td rowspan="2"><em>Hàm băm an toàn</em></td>
<td><em>FIPS PUB 180-4</em></td>
<td><em>Secure Hash Algorithms</em></td>
<td rowspan="2"><em>Áp dụng một trong các hàm băm sau:<br/>
SHA-224,<br/>
SHA-256,<br/>
SHA-384,<br/>
SHA-512,<br/>
SHA-512/224,<br/>
SHA-512/256,<br/>
SHA3-224,<br/>
SHA3-256,<br/>
SHA3-384,<br/>
SHA3-512, SHAKE128, SHAKE256</em></td>
</tr>
<tr>
<td><em>FIPS PUB 202</em></td>
<td><em>SHA-3 Standard: Permutation-Based Hash and Extendable-Output
Functions</em></td>
</tr>
<tr>
<td rowspan="2"><em>21.4</em></td>
<td rowspan="2"><em>Cú pháp mã hóa và cách xử lý thông điệp dữ liệu định
dạng XML</em></td>
<td><em>XML Encryption Syntax and Processing</em></td>
<td><em>XML Encryption Syntax and Processing</em></td>
<td><em>Bắt buộc áp dụng</em></td>
</tr>
<tr>
<td><em>XML Signature Syntax and Processing</em></td>
<td><em>XML Signature Syntax and Processing</em></td>
<td><em>Bắt buộc áp dụng</em></td>
</tr>
<tr>
<td><em>21.5</em></td>
<td><em>Quản lý khóa công khai thông điệp dữ liệu định dạng
XML</em></td>
<td><em>XKMS v2.0</em></td>
<td><em>XML Key Management Specification version 2.0</em></td>
<td><em>Bắt buộc áp dụng</em></td>
</tr>
<tr>
<td><em>21.6</em></td>
<td><em>Cú pháp thông điệp mật mã cho ký, mã hóa</em></td>
<td><em>PKCS#7 v1.5 (RFC 2315)</em></td>
<td><em>Cryptographic message syntax for file-based signing and
encrypting version 1.5</em></td>
<td><em>Bắt buộc áp dụng</em></td>
</tr>
<tr>
<td><em>11.7</em></td>
<td><em>Tiêu chuẩn về chữ ký điện tử nâng cao dành cho thông điệp dữ
liệu định dạng PDF</em></td>
<td><em>ETSI EN 319 142-1</em></td>
<td><em>Electronic Signatures and Infrastructures (ESI) - PAdES digital
signatures</em></td>
<td><em>Áp dụng một trong hai tiêu chuẩn PAdES hoặc CAdES</em></td>
</tr>
<tr>
<td><em>11.8</em></td>
<td><em>Tiêu chuẩn về chữ ký điện tử nâng cao dành cho thông điệp dữ
liệu định dạng XML</em></td>
<td><em>ETSI TS 101 903</em></td>
<td><em>Electronic Signatures and Infrastructures (ESI) - XML Advanced
Electronic Signatures (XAdES)</em></td>
<td><em>Áp dụng một trong hai tiêu chuẩn XAdES hoặc CAdES</em></td>
</tr>
<tr>
<td><em>11.9</em></td>
<td><em>Tiêu chuẩn về chữ ký điện tử nâng cao dành cho thông điệp dữ
liệu định dạng JSON</em></td>
<td><em>RFC 7515</em></td>
<td><em>JSON Web Signature (JWS)</em></td>
<td><em>Bắt buộc áp dụng cho thông điệp dữ liệu định dạng JSON</em></td>
</tr>
<tr>
<td><em>11.10</em></td>
<td><em>Tiêu chuẩn về chữ ký điện tử nâng cao dành cho cú pháp tin nhắn
mật mã</em></td>
<td><em> ETSI TS 101 733</em></td>
<td><em>Electronic Signatures and Infrastructures (ESI) - CMS Advanced
Electronic Signatures (CAdES)</em></td>
<td><em>Khuyến nghị áp dụng</em></td>
</tr>
<tr>
<td><em><strong>.2</strong></em></td>
<td colspan="4"><em><strong>Tiêu chuẩn về hệ thống, thiết bị lưu trữ và
sử dụng khóa bí mật</strong></em></td>
</tr>
<tr>
<td><em>22.1</em></td>
<td><em>Yêu cầu an toàn dành cho mô đun bảo mật phần cứng</em></td>
<td><em>FIPS PUB 140-2</em></td>
<td><em>Security Requirements for Cryptographic Modules</em></td>
<td><em>- Yêu cầu tối thiểu mức 3 (level 3)</em></td>
</tr>
<tr>
<td><em>22.2</em></td>
<td><em>Yêu cầu an toàn đối với thẻ Token và Smart card</em></td>
<td><em>FIPS PUB 140-2</em></td>
<td><em>Security Requirements for Cryptographic Modules</em></td>
<td><em>- Yêu cầu tối thiểu mức 2 (level 2)</em></td>
</tr>
<tr>
<td rowspan="2"><em>.2.3</em></td>
<td rowspan="2"><em>Yêu cầu về chính sách và an toàn cho các tổ chức
cung cấp dịch vụ tin cậy: Các thành phần dịch vụ vận hành thiết bị tạo
chữ ký số và hỗ trợ tạo chữ ký số AdES</em></td>
<td><em>ETSI TS 119 431-1</em></td>
<td><em>Electronic Signatures and Infrastructures (ESI); Policy and
security requirements for trust service providers; Part 1: TSP service
components operating a remote QSCD/SCDev</em></td>
<td rowspan="2"><p><em>Áp dụng cả bộ tiêu chuẩn 2 phần;</em></p>
<p><em>Phiên bản V1.1.1 (12/2018)</em></p></td>
</tr>
<tr>
<td><em>ETSI TS 119 431-2</em></td>
<td><em>Electronic Signatures and Infrastructures (ESI); Policy and
security requirements for trust service providers; Part 2: TSP service
components supporting AdES digital signature creation</em></td>
</tr>
<tr>
<td><em>.2.4</em></td>
<td><em>Giao thức tạo chữ ký số từ xa</em></td>
<td><em>ETSI TS 119 432</em></td>
<td><em>Electronic Signatures and Infrastructures (ESI); Protocols for
remote digital signature creation</em></td>
<td><em>Phiên bản V1.1.1 (03/2019)</em></td>
</tr>
<tr>
<td><em>.2.5</em></td>
<td><em>Hệ thống tin cậy hỗ trợ ký số từ xa - Các yêu cầu
chung</em></td>
<td><em>EN 419241-1:2018</em></td>
<td><em>Trustworthy Systems Supporting Server Signing - Part 1: General
system security requirements</em></td>
<td></td>
</tr>
<tr>
<td><em>.2.6</em></td>
<td><em>Hệ thống tin cậy hỗ trợ ký số từ xa – Yêu cầu và mục tiêu (hồ sơ
bảo vệ) của thiết bị tạo chữ ký số dành cho ký số từ xa</em></td>
<td><em>EN 419241-2:2019</em></td>
<td><em>Trustworthy Systems Supporting Server Signing - Part 2:
Protection Profile for QSCD for Server Signing</em></td>
<td></td>
</tr>
<tr>
<td><em>.2.7</em></td>
<td><em>Yêu cầu và mục tiêu (hồ sơ bảo vệ) dành cho mô đun bảo mật phần
cứng của tổ chức cung cấp dịch vụ tin cậy – mô đun mã hóa dành cho các
dịch vụ tin cậy</em></td>
<td><em>EN 419221-5:2018</em></td>
<td><em>Protection Profiles for TSP Cryptographic modules - Part 5:
Cryptographic Module for Trust Services</em></td>
<td></td>
</tr>
<tr>
<td><em><strong>33</strong></em></td>
<td colspan="4"><em><strong>Tiêu chuẩn kiểm tra trạng thái chứng thư
số</strong></em></td>
</tr>
<tr>
<td><em>33.1</em></td>
<td><em>Giao thức truyền, nhận chứng thư chữ ký số và danh sách chứng
thư chữ ký số bị thu hồi</em></td>
<td><em>RFC 2585</em></td>
<td><em>Internet X.509 Public Key Infrastructure - Operational
Protocols: FTP and HTTP</em></td>
<td><em>Áp dụng một hoặc cả hai giao thức FTP và HTTP</em></td>
</tr>
<tr>
<td><em>33.2</em></td>
<td><em>Giao thức bảo mật tầng giao vận</em></td>
<td><em>RFC 8446</em></td>
<td><em>The Transport Layer Security (TLS) Protocol Version
1.3</em></td>
<td><em>Bắt buộc áp dụng <del>tối thiểu</del></em></td>
</tr>
<tr>
<td><em>33.3</em></td>
<td><em>Giao thức cho kiểm tra trạng thái chứng thư chữ ký sốtrực
tuyến</em></td>
<td><em>RFC 2560</em></td>
<td><em>X.509 Internet Public Key Infrastructure - On-line Certificate
status protocol</em></td>
<td></td>
</tr>
</tbody>
</table> 

**  
Phụ lục II**

**DANH MỤC TIÊU CHÍ ĐÁNH GIÁ HIỆU LỰC CỦA CHỨNG THƯ CHỮ KÝ SỐ VÀ CHỮ KÝ SỐ HỢP LỆ TRONG PHẦN MỀM KÝ SỐ, PHẦN MỀM KIỂM TRA CHỮ KÝ SỐ**

_(Ban hành kèm theo Thông tư số /2025/TT-BKHCN ngày tháng năm 2025 của Bộ trưởng Bộ Khoa học và Công nghệ)_
<table>
<colgroup>
<col/>
<col/>
<col/>
<col/>
</colgroup>
<thead>
<tr>
<th><em><strong>Số TT</strong></em></th>
<th><em><strong>Tiêu chí đánh giá</strong></em></th>
<th><em><strong>Hiệu lực/hợp lệ</strong></em></th>
<th><em><strong>Quy định áp dụng</strong></em></th>
</tr>
</thead>
<tbody>
<tr>
<td><em><strong>1</strong></em></td>
<td colspan="3"><em><strong>Tính hiệu lực của chứng thư chữ ký
số</strong></em></td>
</tr>
<tr>
<td><em>1.1</em></td>
<td><em>Thời gian có hiệu lực của chứng thư số</em></td>
<td><em>Thời gian trên chứng thư chữ ký số còn hiệu lực tại thời điểm ký
số</em></td>
<td><em>Bắt buộc áp dụng</em></td>
</tr>
<tr>
<td><em>1.2</em></td>
<td><em>Trạng thái chứng thư số qua danh sách chứng thư chữ ký số thu
hồi (CRL) được công bố tại thời điểm ký số hoặc bằng phương pháp kiểm
tra trạng thái chứng thư chữ ký số trực tuyến (OCSP) ở chế độ trực tuyến
trong trường hợp tổ chức cung cấp dịch vụ chứng thực chữ ký số có cung
cấp dịch vụ OCSP</em></td>
<td><em>Trạng thái của chứng thư chữ ký số còn hoạt động tại thời điểm
ký số</em></td>
<td><em>Bắt buộc áp dụng</em></td>
</tr>
<tr>
<td><em>1.3</em></td>
<td><em>Thuật toán mật mã trên chứng thư chữ ký số</em></td>
<td><em>Các thuật toán mật mã trên chứng thư chữ ký số tuân thủ theo quy
định về quy chuẩn, tiêu chuẩn kỹ thuật bắt buộc áp dụng về chữ ký số và
dịch vụ chứng thực chữ ký số đang có hiệu lực</em></td>
<td><em>Bắt buộc áp dụng</em></td>
</tr>
<tr>
<td><em>1.4</em></td>
<td><em>Mục đích, phạm vi sử dụng của chứng thư chữ ký số</em></td>
<td><em>Chứng thư chữ ký số được sử dụng đúng mục đích, phạm vi sử
dụng</em></td>
<td><em>Bắt buộc áp dụng</em></td>
</tr>
<tr>
<td><em>1.5</em></td>
<td><em>Các tuyên bố khác của Tổ chức cung cấp dịch vụ chứng thực chữ ký
số</em></td>
<td><em>Các tuyên bố khác không nằm ngoài phạm vi Quy chế chứng thực của
Tổ chức cung cấp dịch vụ chứng thực chữ ký số</em></td>
<td><em>Khuyến nghị áp dụng</em></td>
</tr>
<tr>
<td><em><strong>2</strong></em></td>
<td colspan="3"><em><strong>Tính hợp lệ của chữ ký số</strong></em></td>
</tr>
<tr>
<td><em>2.1</em></td>
<td><em>Thông tin về chủ thể ký</em></td>
<td><em>Kiểm tra, xác thực được đúng thông tin chủ thể ký số</em></td>
<td><em>Bắt buộc áp dụng</em></td>
</tr>
<tr>
<td><em>2.2</em></td>
<td><em>Cách thức tạo chữ ký số</em></td>
<td><em>Chữ ký số được tạo ra đúng bởi khóa bí mật tương ứng với khóa
công khai trên chứng thư chữ ký số</em></td>
<td><em>Bắt buộc áp dụng</em></td>
</tr>
<tr>
<td><em>2.3</em></td>
<td><em>Chứng thư chữ ký số kèm theo thông điệp dữ liệu</em></td>
<td><em>Chứng thư chữ ký số có hiệu lực tại thời điểm ký</em></td>
<td><em>Bắt buộc áp dụng</em></td>
</tr>
<tr>
<td><em>2.4</em></td>
<td><em>Tính toàn vẹn của thông điệp dữ liệu</em></td>
<td><em>Mã băm có được từ việc băm thông điệp dữ liệu và mã băm có được
khi giải mã chữ ký số trùng nhau</em></td>
<td><em>Bắt buộc áp dụng</em></td>
</tr>
</tbody>
</table> 

**Phụ lục III**

**HƯỚNG DẪN KẾT NỐI ĐẾN CỔNG KẾT NỐI DỊCH VỤ CHỨNG THỰC CHỮ KÝ SỐ CÔNG CỘNG**

_(Ban hành kèm theo Thông tư số /2025/TT-BKHCN ngày tháng năm 2025 của Bộ trưởng Bộ Khoa học và Công nghệ)_

**1\. Mô hình kết nối**

Mô hình kết nối với Cổng kết nối dịch vụ chứng thực chữ ký số công cộng (sau đây gọi là Cổng eSign) được mô tả tại sơ đồ như sau:

|<image_2>| _  
_ Chú thích:

\- HTTT: Hệ thống thông tin phục vụ giao dịch điện tử sử dụng chữ ký số.
\- CA: Tổ chức cung cấp dịch vụ chứng thực chữ ký số công cộng.

**2\. Các thông tin hướng dẫn kết nối**

a) Giao thức sử dụng để kết nối là API, phương thức kết nối là POST.

b) Đường dẫn kết nối các API: <https://esign.neac.gov.vn>

c) Thông tin Cổng eSign cung cấp cho các HTTT gồm: sp_id và sp_password hoặc token, trong đó:

\- sp_id: Mã xác thực được cấp cho HTTT.

\- sp_password: Mật khẩu kết nối được cấp cho HTTT tương ứng với sp_id.

\- token: Thông tin xác thực được cấp cho HTTT.