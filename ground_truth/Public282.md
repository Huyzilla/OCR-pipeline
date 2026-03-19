# Public_282

# Giới thiệu

## Mục đích

  * Giới thiệu về dự án: Mục đích và ý nghĩa của dự án

  * Lập kế hoạch cho toàn bộ dự án

  * Ước lượng thời gian của dự án


Mô tả về dự án: Bối cảnh phát triển của dự án, các yêu cầu về môi trường vận hành và các ràng buộc dự án

  * Phân tích các yêu cầu nghiệp vụ của hệ thống thông tin quản lý và phân bố giảng đường

  * Tài liệu được xây dựng dựa trên quá trình khảo sát, phỏng vấn các đối tượng có liên quan và nghiên cứu các tài liệu có liên quan tới nghiệp vụ của hệ thống

  * \- Các chức năng của hệ thống được sửa đổi và bổ sung so với phiên bản trước


## Các tiêu chuẩn

Tài liệu được viết theo font chữ Time New Roman, cỡ chữ 13, khổ giấy A4

## Đối tượng độc giả

Các đối tượng tham gia vào dự án, có thể đọc và sử dụng tài liệu này như: Ngườiquản lý dự án, lập trình viên, tester,...

## Phạm vi dự án

  * Phần mềm thuộc quyền quản lý của khoa Công nghệ thông tin trường Đại học Sư phạm Hà Nội

  * Quản lý trang thiết bị

  * Quản lý giảng đường

  * Quản lý quá trình mượn và trả trang thiết bị phục vụ cho việc giảng dạy và các côngviệc khác

  * Quản lý các sự cố và tình huống rủi ro xảy ra trong giảng đường


## Tài liệu tham khảo 
<table>
<colgroup>
<col/>
<col/>
<col/>
<col/>
</colgroup>
<thead>
<tr>
<th></th>
<th><strong>Tiêu đề</strong></th>
<th><strong>Tác giả</strong></th>
<th><strong>Số phiên bản</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td>Hướng dẫn thiết kế giao diện</td>
<td>Principles of User Interface Design</td>
<td>Ben Shneiderman</td>
<td>2nd Edition</td>
</tr>
<tr>
<td>Hợp đồng</td>
<td>Software Development Contract Template</td>
<td colspan="2">N/a</td>
</tr>
<tr>
<td>Các tiêu chuẩn về phát triển phần mềm</td>
<td>IEEE Standard for Software and System Test Documentation</td>
<td>IEEE Standards Association</td>
<td>IEEE Std 829-2008</td>
</tr>
<tr>
<td>Tài liệu yêu cầu</td>
<td>Software Requirements Specification (SRS)</td>
<td>Karl Wiegers và Joy Beatty</td>
<td>3rd Edition</td>
</tr>
<tr>
<td>Tài liệu đặc tả use case</td>
<td>Writing Effective Use Cases</td>
<td>Alistair Cockburn</td>
<td>1st Edition</td>
</tr>
</tbody>
</table> 

# Mô tả chung

## Tổng quan về sản phẩm

Hiện nay, sự tiến bộ trong công nghệ và phương tiện truyền thông đã tác động lớnđến hệ thống thông tin quản lý và phân bố giảng đường của các trường đại học. Công nghệthông tin và Internet đã mở ra cơ hội cho việc tạo ra môi trường học tập trực tuyến và cảithiện quản lý học phần, khóa học và thông tin sinh viên.Sự phổ biến của học tập từ xa và học trực tuyến đã thúc đẩy các trường đại học phải xâydựng hệ thống thông tin quản lý và phân bố giảng đường linh hoạt, cho phép sinh viên vàgiảng viên tương tác và tiếp cận nội dung giảng dạy từ xa.Sự tăng số lượng sinh viên và khó khăn trong việc quản lý thông tin đã thúc đẩy các trường đại học phải xây dựng các hệ thống thông tin quản lý và phân bố giảng đường. Điều này giúp tăng cường khả năng quản lý thông tin học phần, khóa học, sinh viên và giảng viênmột cách hiệu quả.Việc quản lý giảng đường, phân bổ giảng đường theo lịch học là một việc làm khá vất vảđối với nhà trường. Ngoài thời gian được bố trí theo thời khóa biểu, các giảng đường cũngcó thể được sinh viên, giáo viên đăng ký sử dụng cho các công việc đột xuất. Người quản lýcũng cần kiểm soát được các thiết bị, đồ dùng của từng giảng đường.

## Các chức năng chính của sản phẩm (Product Functions)

Các chức năng chính của hệ thống thông tin quản lý và phân bố giảng đường:

  * Lịch sử dụng giảng đường: Hệ thống cho phép Phòng đào tạo nhập thông tin về thời khóa biểu và thay đổi lịch sử dụng giảng đường. Giảng viên và sinh viên có thể truy cập vào hệ thống để xem lịch trình sử dụng giảng đường của mình.

  * Quản lý mượn giảng đường: Hệ thống cung cấp cơ chế đặt lịch và đăng ký mượn giảng đường cho các công việc đột xuất. Giáo viên hoặc sinh viên có thể yêu cầu mượn giảng đường trong trường hợp cần sử dụng ngoài lịch trình đã thiết lập. Quá trình đăng ký và xác nhận mượn giảng đường được thực hiện thông qua hệ thống.

  * Quản lý trang thiết bị của giảng đường: Hệ thống cho phép quản lý thông tin về trang thiết bị có sẵn trong từng giảng đường. Các thông tin này bao gồm danh sách trang thiết bị, tình trạng, ngày mua và thông tin bảo trì. Người dùng có thể tra cứu thông tin trang thiết bị và kiểm tra tình trạng sẵn có trước khi sử dụng giảng đường.

  * Báo cáo sự cố và thống kê tình trạng giảng đường: Hệ thống cung cấp chức năng cho phép người dùng báo cáo các sự cố mất, hỏng liên quan đến giảng đường; thống kê và báo cáo về tình hình sử dụng giảng đường và trang thiết bị. Người dùng có thể ghi lại thông tin chi tiết về sự cố và gửi báo cáo từ hệ thống. Quản lý có thể xem và xử lý những sự cố này để đảm bảo giảng đường hoạt động trơn tru.


## Phân loại người dùng 

Người dùng hệ thống được chia làm 4 loại:

  * Quản lý hệ thống: Bao gồm các quản lý hệ thống, nhân viên phòng đào tạo hoặc nhân viên quản lý tài sản. Họ có quyền truy cập và quản lý toàn bộ hệ thống, bao gồm thiết lập lịch trình sử dụng giảng đường, quản lý trang thiết bị, xử lý báo cáo sự cố và tạo báo cáo thống kê.

  * Giảng viên: Sử dụng hệ thống để xem lịch trình sử dụng giảng đường của mình, đặt lịch và xác nhận mượn giảng đường cho các công việc đột xuất, và báo cáo sự cố liên quan đến giảng đường.

  * Sinh viên: Sử dụng hệ thống để xem lịch trình sử dụng giảng đường, đặt lịch và xác nhận mượn giảng đường cho các công việc đột xuất. Họ cũng có thể báo cáo sự cố liên quan đến giảng đường.

  * Quản lý sự kiện: Nhóm này bao gồm các nhân viên quản lý sự kiện, tổ chức hội thảo hoặc các hoạt động ngoại khóa. Họ sử dụng hệ thống để đặt lịch và quản lý sự kiện diễn ra trong giảng đường.


## Môi trường hoạt động 

Hệ thống hoạt động trên nền tảng các Web hoặc ứng dụng trên máy tính cá nhân.

## Các ràng buộc thiết kế và cài đặt 

  * Hệ thống sử dụng các công cụ công nghệ:


  * Ngôn ngữ lập trình backend: Java

  * Framework: Spring để giảm thời gian phát triển và tăng tính bảo mật.

  * Cơ sở dữ liệu: Sử dụng hệ quản trị cơ sở dữ liệu PostgreSQL để lưu trữ dữ liệu liên quan đến lịch trình, trang thiết bị, sự cố và người dùng.

  * UI/UX: Sử dụng React kết hợp cùng Ant design


  * Hệ thống chạy trên môi trường website.


## Tài liệu người dùng (User Documentation)

### Hướng dẫn sử dụng:

Tài liệu hướng dẫn sử dụng cung cấp hướng dẫn chi tiết về cách sử dụng các tính năng và chức năng của hệ thống. Nó có thể bao gồm hướng dẫn đăng nhập, đặt lịch sử dụng giảng đường, quản lý thông tin giảng đường, tạo báo cáo, vv.

### Tài liệu hỗ trợ kỹ thuật:

Tài liệu hỗ trợ kỹ thuật cung cấp thông tin về cách cài đặt, cấu hình, và bảo trì hệ thống. Nó có thể bao gồm hướng dẫn về cách triển khai hệ thống, cách sao lưu và khôi phục dữ liệu, và các vấn đề kỹ thuật phổ biến khác.

### Tài liệu API:

Nếu hệ thống cung cấp API cho việc tích hợp với các ứng dụng hoặc dịch vụ khác, tài liệu API sẽ cung cấp thông tin về cách sử dụng API, các yêu cầu và phản hồi được hỗ trợ, và các ví dụ về cách tích hợp.

### Tài liệu quản trị hệ thống:

Tài liệu quản trị hệ thống cung cấp thông tin về cách quản lý người dùng, quyền truy cập, và cấu hình hệ thống. Nó có thể bao gồm hướng dẫn về cách tạo và quản lý tài khoản người dùng, quản lý nhóm người dùng, và cấu hình cài đặt hệ thống.

### Hỗ trợ trực tuyến:

Cung cấp một kênh để người dùng có thể tìm kiếm trợ giúp hoặc yêu cầu hỗ trợ trực tuyến từ nhóm hỗ trợ kỹ thuật. Điều này có thể bao gồm diễn đàn hỗ trợ trực tuyến, trang web hỗ trợ, hoặc hệ thống ticket hỗ trợ.

### Tài liệu đào tạo:

Tài liệu đào tạo cung cấp tài liệu hoặc tài nguyên giáo trình để đào tạo người dùng về cách sử dụng hệ thống một cách hiệu quả. Điều này có thể bao gồm tài liệu học trực tuyến, video hướng dẫn, hoặc các tài liệu đào tạo in ấn.

## Các mặc định và phụ thuộc khác (Assumptions and Dependencies)

  * Danh sách sinh viên đang học tại trường và được cập nhật theo mỗi kỳ học từ phòng Quản lý sinh viên


  * Danh sách cán bộ, giảng viên đang làm việc tại trường

  * Hệ thống phải tuân thủ các quy định về bảo vệ dữ liệu cá nhân và quyền riêng tư theo các


quy định pháp luật hiện hành.

# Yêu cầu về giao tiếp

## Giao tiếp với người dùng (User Interfaces)

Mô tả các đặc tính của mỗi giao diện sử dụng trong hệ thống quản lý và phân bổ giảng

đường bao gồm:

### Hình ảnh màn hình:

  * Cung cấp các hình ảnh minh họa chi tiết về các giao diện người dùng, bao gồm các trang, các màn hình và các thành phần giao diện khác nhau.

  * Đảm bảo rằng hình ảnh màn hình được hiển thị rõ ràng và có thể giải thích được các chức năng và tính năng của hệ thống.


### Chuẩn thiết kế giao diện:

  * Áp dụng các chuẩn thiết kế giao diện như Material Design, Bootstrap, hoặc các chuẩn thiết kế nội bộ của tổ chức để đảm bảo tính nhất quán và trải nghiệm người dùng tốt.

  * Đảm bảo rằng giao diện sử dụng các yếu tố thiết kế như màu sắc, font chữ, kích thước và bố trí phù hợp để tạo ra giao diện hấp dẫn và dễ sử dụng.


### Hướng dẫn thiết kế sản phẩm:

  * Cung cấp hướng dẫn chi tiết về cách sử dụng giao diện người dùng, bao gồm các hướng dẫn sử dụng các tính năng, thực hiện các thao tác và truy cập vào các chức năng khác nhau của hệ thống.

  * Đảm bảo rằng hướng dẫn thiết kế sản phẩm là dễ hiểu và dễ truy cập để người dùng có thể tận dụng tối đa các tính năng của hệ thống.


### Tiêu chuẩn về giao diện:

  * Tuân thủ các tiêu chuẩn về giao diện của hệ thống như độ phản hồi, tương thích với các thiết bị di động, trình duyệt web, và các chuẩn định dạng dữ liệu như JSON hoặc XML

  * Đảm bảo rằng giao diện người dùng đáp ứng đúng các tiêu chuẩn và chuẩn mực về giao diện để tối ưu hóa trải nghiệm người dùng.


### Vào ra dữ liệu:

  * Cung cấp các giao diện dễ sử dụng để nhập liệu từ người dùng, bao gồm các biểu mẫu, trường dữ liệu, và các điều khiển nhập liệu khác nhau.

  * Đảm bảo rằng các giao diện nhập liệu hỗ trợ kiểm tra lỗi và cung cấp thông báo rõ ràng khi người dùng nhập liệu không hợp lệ.


### Thông báo lỗi:

  * Hiển thị thông báo lỗi một cách rõ ràng và dễ hiểu khi xảy ra lỗi trong quá trình sử dụng hệ thống.

  * Cung cấp các thông báo lỗi đầy đủ thông tin và hướng dẫn để người dùng có thể sửa lỗi hoặc liên hệ với hỗ trợ kỹ thuật nếu cần


## Giao tiếp với phần cứng (Hardware Interfaces)

Mô tả các đặc điểm logic và vật lý của giao diện giao tiếp giữa phần mềm và các thiết bị phần cứng của hệ thống quản lý và phân bổ giảng đường bao gồm:

### Kiểu thiết bị:

  * Máy tính cá nhân và thiết bị di động: Hệ thống quản lý và phân bổ giảng đường thường tương tác với máy tính cá nhân, laptop, tablet và điện thoại di động thông qua giao diện người dùng web hoặc ứng dụng di động.

  * Máy chủ: Hệ thống cũng có thể tương tác với các máy chủ để lưu trữ dữ liệu, xử lý yêu cầu và cung cấp dịch vụ.


### Loại tương tác dữ liệu và điều khiển:

  * Người dùng nhập liệu: Người dùng có thể tương tác với hệ thống bằng cách sử dụng chuột và bàn phím để nhập liệu thông qua các biểu mẫu trên giao diệnngười dùng, chẳng hạn như điền thông tin đặt lịch sử dụng giảng đường.

  * Truy vấn và cập nhật dữ liệu: Hệ thống cũng có thể tương tác với cơ sở dữ liệu để truy vấn và cập nhật thông tin về giảng đường, lịch sử đặt lịch, người dùng, vv.

  * Giao diện với thiết bị ngoại vi: Hệ thống có thể giao tiếp với các thiết bị ngoại vi khác như máy in, máy quét mã vạch hoặc thiết bị đo lường thông qua các giao diện tương thích.


### Giao thức truyền thông:

  * HTTP/HTTPS: Giao thức HTTP/HTTPS thường được sử dụng cho việc truyền tải dữ liệu giữa máy tính cá nhân và máy chủ thông qua giao diện người dùng web.

  * SQL: Giao thức SQL thường được sử dụng cho việc truy vấn và cập nhật cơ sở dữ liệu.

  * APIs: Giao thức RESTful hoặc SOAP thường được sử dụng cho việc tương tác giữa hệ thống và các ứng dụng hoặc dịch vụ bên ngoài.


### Đặc điểm vật lý:

  * Kết nối mạng: Hệ thống cần kết nối mạng Internet LAN hoặc WLAN để tương tác với người dùng và dịch vụ trên mạng.

  * Thiết bị lưu trữ: Các dữ liệu cần được lưu trữ trên máy chủ hoặc hệ thống lưu trữ đám mây.

  * Thiết bị người dùng: Người dùng cần sử dụng các thiết bị như máy tính, điện thoại di động hoặc máy tính bảng để truy cập và tương tác với hệ thống