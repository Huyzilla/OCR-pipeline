# Public_254
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
<th>Public 254</th>
</tr>
<tr>
<th><strong>Giấu tin trong ảnh</strong></th>
<th>Lần ban hành: 1</th>
</tr>
</thead>
<tbody>
</tbody>
</table> 

# Giới thiệu về giấu tin trong ảnh

## 1 Khái niệm về giấu tin trong ảnh

Giấu tin trong ảnh là kỹ thuật giấu tin mà trong đó thông tin sẽ được giấu trong dữ liệu ảnh. Các kỹ thuật giấu tin trong ảnh được thực hiện sao cho chất lượng ảnh ít bị thay đổi nhất để bằng mắt thường con người không thể phát hiện ra sự thay đổi đó. Cụ thể, các thuật toán giấu tin sẽ tìm cách khai thác và lợi dụng sự hạn chế về cảm nhận hình ảnh của con người để giấu thông tin. Tùy theo từng ứng dụng mà các kỹ thuật giấu tin có những tính chất và yêu cầu khác nhau. Nhưng tựu chung lại, các kỹ thuật giấu tin trong ảnh không chỉ phải đảm bảo tất cả các tính chất của kỹ thuật giấu tin yêu cầu mà còn phải đảm bảo một số tính chất riêng đối với môi trường ảnh. Ngày nay, kỹ thuật giấu tin trong ảnh thường được sử dụng để truyền thông tin mật giữa người dùng mà người khác không thể biết được. Chính từ những lợi ích mà các kỹ thuật giấu tin trong ảnh mang lại nên hiện nay lĩnh vực giấu tin trong ảnh đang được phát triển nhanh chóng và mạnh mẽ. Ví dụ như đối với các nước phát triển, chữ kí tay đã được số hóa và lưu trữ sử dụng như là hồ sơ cá nhân của các dịch vụ ngân hàng và tài chính, nó được dùng để xác thực trong các thẻ tín dụng của người tiêu dùng. Ngoài ra phần mềm Microsoft Word cũng cho phép người dùng lưu trữ chữ kí trong ảnh nhị phân rồi gắn vào vị trí nào đó trong file văn bản để đảm bảo tính toàn vẹn của thông tin.

##  1.2 Một số định dạng ảnh và công cụ xử lý ảnh

  1. Một số định dạng ảnh


Hiện nay có nhiều loại định dạng ảnh khác nhau có thể được lựa chọn để giấu tin. Mỗi định dạng ảnh sẽ có tiêu chuẩn và tính chất khác nhau. Do đó, để tối ưu hóa quá trình giấu tin thì trước khi tiến hành giấu tin người giấu tin cần phải xem xét và đánh giá các định dạng, tiêu chuẩn ảnh. Tiếp theo, giáo trình sẽ cung cấp một số mô tả về một số định dạng ảnh đang được sử dụng phổ biến hiện nay.
\- **Định dạng ảnh BMP** : BMP được biết đến với tên tiếng Anh khác là Windows bitmap, là một định dạng ảnh phổ biến. Định dạng ảnh BMP được sử dụng để lưu trữ hình ảnh kỹ thuật số bitmap, độc lập với thiết bị hiển thị và có khả năng lưu trữ hình ảnh kỹ thuật số hai chiều cả đơn màu, đa màu, ở các độ sâu màu khác nhau tùy vào dữ liệu nén, các kênh alpha và các cấu hình màu. Một tập tin Bitmap bao gồm các cấu trúc theo thứ tự như biểu trên bảng sau.
<table>
<colgroup>
<col/>
<col/>
<col/>
</colgroup>
<tbody>
<tr>
<td><strong>Tên cấu trúc</strong></td>
<td><strong>Kích thước</strong></td>
<td><strong>Mục đích</strong></td>
</tr>
<tr>
<td>Tiêu đề tệp Bitmap</td>
<td>14 byte</td>
<td>Lưu trữ thông tin tổng quát về tệp hình ảnh bitmap</td>
</tr>
<tr>
<td>Mặt nạ thêm bit</td>
<td>12 hoặc 16 byte</td>
<td>Xác định định dạng điểm ảnh.</td>
</tr>
<tr>
<td>Tiêu đề DIB</td>
<td rowspan="6">Tùy theo các phiên bản</td>
<td>Lưu trữ thông tin chi tiết về ảnh bitmap và xác định định dạng điểm
ảnh</td>
</tr>
<tr>
<td>Bảng màu</td>
<td>Xác định màu sắc được sử dụng bởi dữ liệu hình ảnh bitmap</td>
</tr>
<tr>
<td>Gap1</td>
<td>Cân chỉnh cấu trúc</td>
</tr>
<tr>
<td>Mảng điểm ảnh</td>
<td>Xác định giá trị các điểm ảnh</td>
</tr>
<tr>
<td>Gap2</td>
<td>Cân chỉnh cấu trúc</td>
</tr>
<tr>
<td>Màu ICC</td>
<td>Xác định cấu hình màu để quản lý màu sắc</td>
</tr>
</tbody>
</table> 

Từ bảng trên có thể thấy được định dạng BMP có cấu trúc tương đối đơn giản. Ngoài ra, khi ảnh BMP không nén thì các ảnh này chỉ là một ma trận các điểm ảnh. Trong đó, mỗi một phần tử của ma trận biểu diễn một điểm ảnh, bao gồm các thành phần đỏ (kí hiệu R), xanh lục (kí hiệu G), xanh lam (kí hiệu B), alpha (kí hiệu A), các thành phần bổ sung (kí hiệu X). Ngày này các kỹ thuật giấu tin trong ảnh sử dụng ảnh theo chuẩn BMP không được sử dụng phổ biến. Bởi vì các ảnh này có cấu trúc đơn giản, do đó giấu được ít thông tin cũng như thông tin sau khi giấu dễ bị phát hiện.
\- **Định dạng ảnh PNG** : PNG (Portable Network Graphics) là một dạng ảnh sử dụng phương pháp nén dữ liệu không làm mất đi dữ liệu gốc. PNG hỗ trợ các ảnh dựa trên bảng màu (với bảng màu RGB 24 bit hoặc RGBA 32 bit), ảnh xám (có hoặc không có kênh alpha) và ảnh RGB/RGBA không có bảng màu đầy đủ. Các giá trị trong phần tiêu đề của định dạng ảnh PNG được liệt kê trong bảng sau.
<table>
<colgroup>
<col/>
<col/>
</colgroup>
<tbody>
<tr>
<td><strong>Giá trị</strong></td>
<td><strong>Mục đích</strong></td>
</tr>
<tr>
<td>89</td>
<td>Có các bit cao thiết lập để phát hiện các hệ thống truyền dẫn không
hỗ trợ dữ liệu 8 bit, giảm nguy cơ mà một tập tin văn bản bị hiểu nhầm
là một tập PNG, hoặc ngược lại.</td>
</tr>
<tr>
<td>50 4E 47</td>
<td>Là chữ cái PNG trong bảng mã ASCII, cho phép xác định định dạng
PNG</td>
</tr>
<tr>
<td>0D 0A</td>
<td>Là một kiểu kết thúc của DOS giúp phát hiện dòng kết thúc chuyển đổi
dữ liệu</td>
</tr>
<tr>
<td>1A</td>
<td>Một byte thông báo dừng hiển thị của tập tin</td>
</tr>
</tbody>
</table> 

Ngoài các thành phần tiêu đề tập tin PNG được mô tả trong bảng trên thì chuẩn PNG còn có các đoạn mã lưu trữ dữ liệu (chunk). Đoạn mã lưu trữ dữ liệu này là một đoạn thông tin được sử dụng trong nhiều định dạng đa phương tiện. Mỗi một đoạn mã lưu trữ dữ liệu truyền tải thông tin nhất định về hình ảnh. Có hai loại đoạn mã lưu trữ dữ liệu: một là đoạn mã chính, hai là đoạn mã phụ trợ. Một bộ giải mã có khả năng đọc các đoạn mã lưu trữ dữ liệu quan trọng và hiển thị tệp PNG. Các đoạn mã lưu trữ dữ liệu phụ trợ là các thuộc tính hình ảnh khác có thể được lưu trữ trong các tệp PNG bao gồm các giá trị gamma, màu nền... Các đoạn mã lưu trữ dữ liệu quan trọng bao gồm IHDR, PLTE, IDAT, IEND. Giá trị của các IHDR, PLTE, IDAT, IEND được mô tả trong tài liệu.
\- **Định dạng ảnh JPEG** : JPEG (Joint Photographic Experts Group) một nhóm các nhà nghiên cứu đã phát minh ra định dạng này để hiển thị các hình ảnh đầy đủ màu hơn mà kích thước file lại nhỏ hơn. Chuẩn JPEG có thể hiển thị các hình ảnh với các màu chính xác lên đến 16 triệu màu. Cấu trúc ảnh JPEG bao gồm nhiều phân đoạn (segment), ở mỗi đoạn là 1 cờ (marker), mỗi cờ bắt đầu bằng byte 0xFF và theo sau đó là 1 byte chỉ ra mã của loại cờ. Một số cờ chỉ gồm 2 byte; sau 2 byte cờ là 2 byte chỉ ra độ dài của đoạn không tính 2 byte của cờ. Với những đoạn chứa dữ liệu nén (entropy-coded data), 2 byte xác định độ dài của đoạn không tính độ dài của dữ liệu nén. Ảnh JPEG không yêu cầu các đoạn phải nằm theo đúng thứ tự nhưng đoạn đầu tiên của ảnh phải là đoạn SOI; đoạn cuối cùng là đoạn EOI. Một số thuộc tính của những cờ thường gặp trong ảnh JPEG được mô tả trong bảng sau.
<table>
<colgroup>
<col/>
<col/>
<col/>
</colgroup>
<tbody>
<tr>
<td><strong>Tên rút gọn</strong></td>
<td><strong>Giá trị cờ</strong></td>
<td><strong>Mô tả tóm tắt</strong></td>
</tr>
<tr>
<td>SOI</td>
<td>0xFF, 0xD8</td>
<td>Đánh dấu bắt đầu ảnh JPEG</td>
</tr>
<tr>
<td>SOFn</td>
<td>0xFF, 0xC4</td>
<td>Bắt đầu của khung, mô tả các thông số của ảnh: chiều cao, chiều
rộng, số lượng thành phần màu, tỉ lệ số lượng thành phần màu.</td>
</tr>
<tr>
<td>DHT</td>
<td>0xFF, 0xC4</td>
<td>Xác định bảng Huffman. Trong ảnh JPEG có thể xuất hiện nhiều đoạn
DHT</td>
</tr>
<tr>
<td>DQT</td>
<td>0xFF, 0xDB</td>
<td>Xác định bảng lượng tử hóa. Trong ảnh JPEG có thể xuất hiện nhiều
đoạn DQT</td>
</tr>
<tr>
<td>SOS</td>
<td>0xFF, 0xDA</td>
<td>Đánh dấu bắt đầu quét ảnh từ trên xuống dưới.</td>
</tr>
<tr>
<td>APPn</td>
<td>0xFF, 0xEn</td>
<td>Dành riêng cho đoạn ứng dụng, đánh dấu bắt đầu của đoạn dữ liệu ứng
dụng.</td>
</tr>
<tr>
<td>COM</td>
<td>0xFF, 0xEE</td>
<td>Cờ bắt đầu chứa lời bình (chú thích).</td>
</tr>
<tr>
<td>EOI</td>
<td>0xFF, 0xD9</td>
<td>Đánh dấu kết thúc ảnh</td>
</tr>
</tbody>
</table> 

Từ bảng trên có thể thấy được ảnh JPEG có cấu trúc phức tạp bao gồm nhiều thành phần khác nhau. Dựa trên đặc điểm của các thành phần này, các phương pháp giấu tin trong ảnh sẽ khai thác để thực hiện giấu tin.

  2. Một số công cụ xử lý ảnh phổ biến


Các công cụ xử lý ảnh hiện nay đóng vai trò quan trọng trong việc triển khai các phương pháp giấu tin trong ảnh và xử lý ảnh chuyên sâu. Sau đây là một số công cụ thường để xử lý ảnh phổ biến: Corel PaintShop Pro, GIMP, Adobe Photoshop Elements, Paint.NET, Photo Pos Pro, Zoner Photo Studio, PhotoScape, Xara Photo & Graphic Designer.