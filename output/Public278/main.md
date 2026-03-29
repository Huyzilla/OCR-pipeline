# Public_278

# Tổng quan

## Mục đích

Tài liệu trình bày tổng quan giải pháp và quy trình nghiệp vụ đáp ứng cho bài toán tích hợp đối tác kinh doanh tại Tổng công ty cổ phần Bưu chính Viettel.

Thiết kế, mô tả các quy trình nghiệp vụ của Hệ thống đảm bảo cung cấp giải pháp hoàn chỉnh, xuyên suốt quá trình khai báo và phê duyệt mã KH chi COD

## Phạm vi
<table>
<colgroup>
<col/>
<col/>
<col/>
</colgroup>
<thead>
<tr>
<th><em><strong>STT</strong></em></th>
<th><em><strong>Nghiệp vụ</strong></em></th>
<th><em><strong>Phạm vi áp dụng</strong></em></th>
</tr>
</thead>
<tbody>
<tr>
<td><ol>
<li></li>
</ol></td>
<td><em>Khai báo cấu hình</em></td>
<td><p><em>- Khai báo cấu hình sản lượng doanh thu theo địa bàn</em></p>
<p><em>- Khai báo mã KH cấu hình chi COD</em></p></td>
</tr>
<tr>
<td><ol>
<li></li>
</ol></td>
<td><em>Phê duyệt mã KH</em></td>
<td><p><em>Thực hiện phê duyệt mã KH đã khai báo theo sản lượng/doanh
thu cam kết</em></p>
<ul>
<li><p><em>Hệ thống tự động phê duyệt nếu đạt sản lượng hoặc doanh thu
theo địa bàn</em></p></li>
<li><p><em>Hệ thống thự hiện trình ký phê duyệt Voffice với các trường
hợp không đạt doanh thu sản lượng theo địa bàn</em></p></li>
</ul></td>
</tr>
<tr>
<td><ol>
<li></li>
</ol></td>
<td><em>Báo cáo sản lượng doanh thu theo mã KH</em></td>
<td><p><em>Báo cáo cấu hình chi của mã KH</em></p>
<p><em>Báo cáo sản lượng/doanh thu</em></p></td>
</tr>
</tbody>
</table> 

#  Quy trình tổng quan

|<image_5>|

**Mô tả quy trình:**
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
<th>Bước</th>
<th><strong>Nội dung</strong></th>
<th><strong>Đối tượng thực hiện</strong></th>
<th><strong>Hệ thống thực hiện</strong></th>
<th><blockquote>
<p><strong>Mô tả</strong></p>
</blockquote></th>
</tr>
</thead>
<tbody>
<tr>
<td>1</td>
<td>Chức năng khai báo mã KH cusID</td>
<td>User được phân quyền</td>
<td>FICO</td>
<td><p>User được phân quyền truy cập vào chức năng khai báo mã KH cusID
trên hệ thống FICO.</p>
<p>Chuyển bước 2.</p></td>
</tr>
<tr>
<td>2</td>
<td>Chọn mã KH hoặc Import file</td>
<td>User được phân quyền</td>
<td>FICO</td>
<td><p>Người dùng nhập mã KH hoặc import danh sách KH cần khai báo chi
COD hàng ngày.</p>
<p>Hệ thống kiếm tra:</p>
<ul>
<li><p>Nếu KH đang có kỳ thanh toán COD hàng ngày Thông báo lỗi</p></li>
<li><p>Nếu KH đang không có kỳ thanh toán COD hàng ngày chuyển bước
3.</p></li>
</ul></td>
</tr>
<tr>
<td>3</td>
<td>Hiển thị thông tin thanh toán của KH</td>
<td>Hệ thống</td>
<td>FICO</td>
<td><p>Hiển thị thông tin thanh toán hiện tại của cus tìm kiếm.</p>
<p>Chuyển bước 4.</p></td>
</tr>
<tr>
<td>4</td>
<td>Chọn Thanh toán COD hàng ngày</td>
<td>User được phân quyền</td>
<td>FICO</td>
<td><p>Chọn loại kỳ thanh toán Hàng ngày cho các mã KH khai báo.</p>
<p>Chuyển bước 5.</p></td>
</tr>
<tr>
<td>5</td>
<td>Xác nhận đẩy yêu cầu xác thực OTP trên app KH</td>
<td>User được phân quyền</td>
<td>FICO</td>
<td><p>Người dùng xác nhận khai báo các mã KH về hình thức thanh toán
COD hàng ngày. Hệ thống tự động đẩy yêu cầu xác thực OTP lên app KH.</p>
<p>Chuyển bước 6.</p></td>
</tr>
<tr>
<td>6</td>
<td>Hiển thị yêu cầu xác thực lên app KH</td>
<td>Hệ thống</td>
<td>App KH</td>
<td><p>KH thực hiện xác thực OTP trên App KH.</p>
<ul>
<li><p>Xác thực thành công chuyển bước 7</p></li>
<li><p>Không xác thực Chuyển bước 9</p></li>
</ul></td>
</tr>
<tr>
<td>7</td>
<td>Lưu thông tin kỳ thanh toán cusID</td>
<td>Hệ thống</td>
<td>FICO</td>
<td><p>KH xác thực thành công hệ thống tự động cập nhật thông tin thanh
toán mới của KH.</p>
<ul>
<li><p>Hiển thị Ngày thanh toán mới và lịch sử cập nhật trên app
KH</p></li>
<li><p>Cập nhật thông tin kỳ thanh toán trên hệ thống FICO, HR Chuyển
bước 8.</p></li>
</ul></td>
</tr>
<tr>
<td>8</td>
<td>Đồng bộ kỳ thanh toán sang mã EVTP</td>
<td>Hệ thống</td>
<td>FICO</td>
<td><p>Đồng bộ kỳ thanh toán từ mã Cus sang toàn bộ mã EVTP thuộc
cus.</p>
<p>Chuyển bước 10.</p></td>
</tr>
<tr>
<td>9</td>
<td>Tự động hủy yêu cầu sau 72h</td>
<td>Hệ thống</td>
<td>FICO</td>
<td><p>Với yêu cầu xác thực quá 72h không có phản hồi từ KH hệ thống tự
động cập nhật về trạng thái Xác thực thất bại.</p>
<ul>
<li><p>Khi KH click vào yêu cầu trên app hệ thống thông báo Yêu cầu
không tồn tại hoặc đã quá hạn xử lý</p></li>
<li><p>Hệ thống cập nhật trạng thái Xác thực thất bại.</p></li>
</ul>
<p>Chuyển bước 10.</p></td>
</tr>
<tr>
<td>10</td>
<td>Cập nhật trạng thái xác thực</td>
<td>Hệ thống</td>
<td>FICO</td>
<td><p>Hệ thống cập nhật chính xác trạng thái xác thực.</p>
<p>Kết thúc luồng.</p></td>
</tr>
</tbody>
</table> 

# Chi tiết chức năng Quản lý CusID và khai báo KH thanh toán hàng ngày trên FICO

## SCR1: Màn hình Quản lý khách hàng CusID

### Màn hình

|<image_6>|Phân quyền: User được phân quyền theo quy định của TTDVCP

### Mô tả màn hình
<table>
<colgroup>
<col/>
<col/>
<col/>
<col/>
<col/>
<col/>
</colgroup>
<thead>
<tr>
<th><strong>No</strong></th>
<th><strong>Field Name</strong></th>
<th><strong>Control Type</strong></th>
<th><p><strong>Mandatory</strong></p>
<p><strong>(Yes/No)</strong></p></th>
<th><strong>Editable/ Read-only</strong></th>
<th><strong>Description/Note</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="6"><strong>Chức năng tra cứu</strong></td>
</tr>
<tr>
<td><strong>1</strong></td>
<td>Khách hàng cus</td>
<td>Textbox</td>
<td>No</td>
<td>Editable</td>
<td><h6>Cho phép user nhập thông tin KH để tìm kiếm.</h6>
<p>Cho phép nhập các giá trị sau:</p>
<ul>
<li><p>Mã CusID</p></li>
<li><p>Số điện thoại (sđt đăng nhập hệ thống app/web)</p></li>
<li><p>Email (Email đăng nhập hệ thống app/web)</p></li>
</ul>
<p>Hệ thống tìm kiếm mã cus theo điều kiện nhập.</p></td>
</tr>
<tr>
<td><strong>2</strong></td>
<td>Khách hàng EVTP</td>
<td>Textbox</td>
<td>No</td>
<td>Editable</td>
<td><h6>Cho phép KH nhập mã EVTP để tìm kiếm mã KH
CusID</h6></td>
</tr>
<tr>
<td><strong>3</strong></td>
<td>Tìm kiếm</td>
<td>Button</td>
<td>Yes</td>
<td>Editable</td>
<td><h6>Click
button thực hiện tra cứu.</h6>
<h6>Hiển thị toàn bộ dữ liệu theo điều kiện tìm
kiếm</h6></td>
</tr>
<tr>
<td colspan="6"><strong>Chi tiết thông tin KH</strong></td>
</tr>
<tr>
<td><strong>4</strong></td>
<td>STT</td>
<td>Text</td>
<td>No</td>
<td>Read-only</td>
<td>Hiển thị số thứ tự</td>
</tr>
<tr>
<td><strong>5</strong></td>
<td>Mã cusid</td>
<td>Text</td>
<td>No</td>
<td>Editable</td>
<td>Hiển thị mã Cusid</td>
</tr>
<tr>
<td><strong>6</strong></td>
<td>Số điện thoại</td>
<td>Text</td>
<td>No</td>
<td>Read-only</td>
<td>Hiển thị số điện thoại KH</td>
</tr>
<tr>
<td><strong>7</strong></td>
<td>Tên KH</td>
<td>Text</td>
<td>No</td>
<td>Read-only</td>
<td>Hiển thị Tên KH</td>
</tr>
<tr>
<td><strong>8</strong></td>
<td>Loại kỳ thanh toán</td>
<td>Text</td>
<td>No</td>
<td>Read-only</td>
<td>Hiển thị loại kỳ thanh toán theo HDDT</td>
</tr>
<tr>
<td><strong>9</strong></td>
<td>Email</td>
<td>Text</td>
<td>No</td>
<td>Read-only</td>
<td>Hiển thị email KH</td>
</tr>
<tr>
<td><strong>10</strong></td>
<td>Hình thức thanh toán</td>
<td>Text</td>
<td>No</td>
<td>Read-only</td>
<td>Hiện thị hình thức thanh toán của KH</td>
</tr>
<tr>
<td><strong>11</strong></td>
<td>Ngân hàng</td>
<td>Text</td>
<td>No</td>
<td>Read-only</td>
<td>Hiển thị ngân hàng nhận COD theo HDDT</td>
</tr>
<tr>
<td><strong>12</strong></td>
<td>Chi nhánh</td>
<td>Text</td>
<td>No</td>
<td>Read-only</td>
<td><p>Hiển thị chi nhánh của ngân hàng</p>
<p>Không có để trống</p></td>
</tr>
<tr>
<td><strong>13</strong></td>
<td>Số tài khoản</td>
<td>Text</td>
<td>No</td>
<td>Read-only</td>
<td>Hiển thị số tài khoản theo HDDT</td>
</tr>
<tr>
<td><strong>14</strong></td>
<td>Người thụ hưởng</td>
<td>Text</td>
<td>No</td>
<td>Read-only</td>
<td>Hiển thị tên người thụ hưởng theo HDDT</td>
</tr>
<tr>
<td><strong>15</strong></td>
<td>Thao tác</td>
<td>Button</td>
<td>Yes</td>
<td>Editable</td>
<td><p>Cho phép thao tác sửa và xóa cấu hình theo từng địa bàn.</p>
<p>- Click Button Xem cho phép xem chi tiết danh sách KH EVTP của mã
cus</p>
<p>- Click Xem lịch sử Hiển thị lịch sử cập nhật của cusid.</p>
<p>Hiển thị tooltip khi Hower chuột “Xem” và “Lịch sử cập nhật”</p></td>
</tr>
<tr>
<td colspan="6"><p><strong>Chi tiết thông tin KH EVTP</strong></p>
<p><strong>Hiển thị danh sách mã KH EVTP thuộc mã
CusID</strong></p></td>
</tr>
<tr>
<td><strong>1</strong></td>
<td>STT</td>
<td>Text</td>
<td>No</td>
<td>Read-only</td>
<td>Hiển thị số thứ tự</td>
</tr>
<tr>
<td><strong>2</strong></td>
<td>Chi nhánh</td>
<td>Text</td>
<td>No</td>
<td>Read-only</td>
<td>Hiển thị tên chi nhánh</td>
</tr>
<tr>
<td><strong>3</strong></td>
<td>Bưu cục</td>
<td>Text</td>
<td>No</td>
<td>Read-only</td>
<td>Hiển thị tên bưu cục</td>
</tr>
<tr>
<td><strong>4</strong></td>
<td>Mã KH EVTP</td>
<td>Text</td>
<td>No</td>
<td>Read-only</td>
<td>Hiển thị mã KH EVTP</td>
</tr>
<tr>
<td><strong>5</strong></td>
<td>Tên KH</td>
<td>Text</td>
<td>No</td>
<td>Read-only</td>
<td>Hiển thị tên KH EVTP</td>
</tr>
<tr>
<td><strong>6</strong></td>
<td>Hình thức cấn trừ</td>
<td>Text</td>
<td>No</td>
<td>Read-only</td>
<td><p>Hiển thị hình thức cấn trừ của mã EVTP</p>
<p>Không có để trống.</p></td>
</tr>
<tr>
<td><strong>7</strong></td>
<td>Kỳ cấn trừ</td>
<td>Text</td>
<td>No</td>
<td>Read-only</td>
<td><p>Hiển thị kỳ cấn trừ.</p>
<p>Không có để trống.</p></td>
</tr>
<tr>
<td><strong>8</strong></td>
<td>Ngày lấy cấn trừ</td>
<td>Text</td>
<td>No</td>
<td>Read-only</td>
<td><p>Hiển thị ngày lấy cấn trừ</p>
<p>Không có để trống.</p></td>
</tr>
<tr>
<td><strong>9</strong></td>
<td>Kết xuất excel</td>
<td>Button</td>
<td>Yes</td>
<td>Editable</td>
<td><p>Khi click thì thực hiện kết xuất danh sách excel trên grid.</p>
<blockquote>
<p><strong><u>Quy Tắc Kết Xuất:</u></strong></p>
</blockquote>
<ul>
<li><p>Nếu kết quả tìm kiếm không có dữ liệu thì hệ thống hiển thị thông
báo “Không tồn tại kết quả”.</p></li>
<li><p>Nếu kết quả tìm kiếm có dữ liệu thì hệ thống thực hiện kết xuất
toán bộ dữ liệu trên grid.</p></li>
</ul>
<p>Tên file: Danh sách KH EVTP mã cusID {Mã cusid}</p></td>
</tr>
</tbody>
</table> 

## SCR2: Màn hình Khai báo mã khách hàng

### Màn hình

|<image_7>|

### Mô tả Màn hình
<table style="width:100%;">
<colgroup>
<col/>
<col/>
<col/>
<col/>
<col/>
<col/>
</colgroup>
<thead>
<tr>
<th><blockquote>
<p><strong>No</strong></p>
</blockquote></th>
<th><strong>Field Name</strong></th>
<th><strong>Control Type</strong></th>
<th><p><strong>Mandatory</strong></p>
<p><strong>(Yes/No)</strong></p></th>
<th><strong>Editable/ Read-only</strong></th>
<th><strong>Description/Note</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td colspan="6"><strong>Chức năng tra cứu</strong></td>
</tr>
<tr>
<td><strong>1</strong></td>
<td>Khách hàng cus</td>
<td>Textbox</td>
<td>No</td>
<td>Editable</td>
<td><h6>Cho phép user nhập thông tin KH để tìm kiếm.</h6>
<p>Cho phép nhập các giá trị sau:</p>
<ul>
<li><p>Mã CusID</p></li>
<li><p>Số điện thoại (sđt đăng nhập hệ thống app/web)</p></li>
<li><p>Email (Email đăng nhập hệ thống app/web)</p></li>
</ul>
<p>Hệ thống tìm kiếm mã cus theo điều kiện nhập.</p></td>
</tr>
<tr>
<td><strong>2</strong></td>
<td>Khách hàng EVTP</td>
<td>Textbox</td>
<td>No</td>
<td>Editable</td>
<td>Cho phép KH nhập mã EVTP để tìm kiếm mã KH CusID</td>
</tr>
<tr>
<td><strong>3</strong></td>
<td>Tìm kiếm</td>
<td>Button</td>
<td>Yes</td>
<td>Editable</td>
<td><h6>Click
button thực hiện tra cứu.</h6>
<p>Hiển thị toàn bộ dữ liệu theo điều kiện tìm kiếm</p></td>
</tr>
<tr>
<td><strong>4</strong></td>
<td>Kết xuất excel</td>
<td>Button</td>
<td>Yes</td>
<td>Editable</td>
<td><p>Khi click thì thực hiện kết xuất danh sách excel trên grid.</p>
<blockquote>
<p><strong><u>Quy Tắc Kết Xuất:</u></strong></p>
</blockquote>
<ul>
<li><p>Nếu kết quả tìm kiếm không có dữ liệu thì hệ thống hiển thị thông
báo “Không tồn tại kết quả”.</p></li>
<li><p>Nếu kết quả tìm kiếm có dữ liệu thì hệ thống thực hiện kết xuất
toán bộ dữ liệu trên grid.</p></li>
</ul>
<ul>
<li><p>Tên file: Danh sách KH khai báo thanh toán hàng ngày</p></li>
</ul></td>
</tr>
<tr>
<td><strong>5</strong></td>
<td>Khai báo mã KH</td>
<td>Button</td>
<td>Yes</td>
<td>Editable</td>
<td>Hiển thị button Khai báo mã KH. Click button hiển thị popup Khai báo
mã KH chi tiết tại màn hình SCR 3. Màn hình Khai báo thông tin mã
KH</td>
</tr>
<tr>
<td colspan="6"><strong>Chi tiết thông tin cấu hình</strong></td>
</tr>
<tr>
<td><strong>6</strong></td>
<td>STT</td>
<td>Text</td>
<td>No</td>
<td>Read-only</td>
<td>Hiển thị số thứ tự</td>
</tr>
<tr>
<td><strong>7</strong></td>
<td>STT</td>
<td>Text</td>
<td>No</td>
<td>Read-only</td>
<td>Hiển thị số thứ tự</td>
</tr>
<tr>
<td><strong>8</strong></td>
<td>Mã cusid</td>
<td>Text</td>
<td>No</td>
<td>Editable</td>
<td>Hiển thị mã Cusid</td>
</tr>
<tr>
<td><strong>9</strong></td>
<td>Số điện thoại</td>
<td>Text</td>
<td>No</td>
<td>Read-only</td>
<td>Hiển thị số điện thoại KH</td>
</tr>
<tr>
<td><strong>10</strong></td>
<td>Tên KH</td>
<td>Text</td>
<td>No</td>
<td>Read-only</td>
<td>Hiển thị Tên KH</td>
</tr>
<tr>
<td><strong>11</strong></td>
<td>Loại kỳ thanh toán</td>
<td>Text</td>
<td>No</td>
<td>Read-only</td>
<td>Hiển thị loại kỳ thanh toán theo HDDT</td>
</tr>
<tr>
<td><strong>12</strong></td>
<td>Email</td>
<td>Text</td>
<td>No</td>
<td>Read-only</td>
<td>Hiển thị email KH</td>
</tr>
<tr>
<td><strong>13</strong></td>
<td>Hình thức thanh toán</td>
<td>Text</td>
<td>No</td>
<td>Read-only</td>
<td>Hiện thị hình thức thanh toán của KH</td>
</tr>
<tr>
<td><strong>14</strong></td>
<td>Trạng thái</td>
<td>Text</td>
<td>No</td>
<td>Read-only</td>
<td><p>Hiển thị trạng thái tương ứng của yêu cầu:</p>
<ul>
<li><p>Chờ xác thực – Đã gửi yêu cầu xác thực nhưng KH chưa xác
thực</p></li>
<li><p>Đã xác thực – KH đã xác thực OTP thành công</p></li>
<li><p>Xác thực thất bại – KH từ chối xác thực hoặc xác thực tự động hủy
sau 72h</p></li>
<li><p>Không hoạt động – khi có cập nhật kỳ thanh toán mới (KH ký PL HĐ
có thay đổi kỳ thanh toán hoặc thay đổi kỳ thanh toán)</p></li>
</ul></td>
</tr>
<tr>
<td><strong>15</strong></td>
<td>Người khai báo</td>
<td>Datetime</td>
<td>No</td>
<td>Read-only</td>
<td>Hiển thị tên người thực hiện khai báo</td>
</tr>
<tr>
<td><strong>16</strong></td>
<td>Thời gian khai báo</td>
<td>Datetime</td>
<td>No</td>
<td>Read-only</td>
<td>Hiển thị thời gian thực hiện khai báo</td>
</tr>
<tr>
<td><strong>17</strong></td>
<td>Thời gian cập nhật</td>
<td>Datetime</td>
<td>No</td>
<td>Read-only</td>
<td>Hiển thị thời gian cập nhật (thời gian xác thực, hủy)</td>
</tr>
<tr>
<td><strong>18</strong></td>
<td>Thao tác</td>
<td>Button</td>
<td>Yes</td>
<td>Editable</td>
<td><p>Cho phép thao tác gửi lại yêu cầu xác thực và xóa cấu hình.</p>
<p>- Click Button Gửi yêu cầu xác thực chỉ hiển thị với trạng thái Xác
thực thất bại và Không hoạt động.</p>
<p>- Click Xóa Chỉ hiển thị với trạng thái Chờ xác thực và Xác thực thất
bại Hiển thị thông báo Xác nhận xóa khai báo cấu hình.</p>
<p>Hiển thị tooltip khi Hower chuột “Gửi yêu cầu xác thực” và
“Xóa”</p></td>
</tr>
</tbody>
</table> 

### SCR3. Màn hình Khai báo thông tin mã KH

|<image_8>|
<table>
<colgroup>
<col/>
<col/>
<col/>
<col/>
<col/>
<col/>
</colgroup>
<thead>
<tr>
<th><blockquote>
<p><strong>No</strong></p>
</blockquote></th>
<th><strong>Field Name</strong></th>
<th><strong>Control Type</strong></th>
<th><p><strong>Mandatory</strong></p>
<p><strong>(Yes/No)</strong></p></th>
<th><strong>Editable/ Read-only</strong></th>
<th><strong>Description/Note</strong></th>
</tr>
</thead>
<tbody>
<tr>
<td><strong>1</strong></td>
<td>Import file</td>
<td>Button</td>
<td>Yes</td>
<td>Editable</td>
<td><p>Cho phép user import file KH theo template.</p>
<p>Nguyên tắc import:</p>
<ul>
<li><p>Nếu KH đang có khai báo kỳ thanh toán COD hàng ngày không cho
phép import</p></li>
<li><p>Nếu KH đang không phải kỳ thanh toán hàng ngày cho phép
import</p></li>
<li><p>Dữ liệu import lên phải là mã cusid</p></li>
</ul></td>
</tr>
<tr>
<td><strong>2</strong></td>
<td>Tải xuống file biểu mẫu</td>
<td>Button</td>
<td>No</td>
<td>Editable</td>
<td><p>Cho phép user tải xuống file biểu mẫu</p>
<p>Template file:</p></td>
</tr>
<tr>
<td><strong>3</strong></td>
<td>STT</td>
<td>Button</td>
<td>Yes</td>
<td>Editable</td>
<td>Hiển thị STT</td>
</tr>
<tr>
<td><strong>4</strong></td>
<td>Mã CusID</td>
<td>Texbox</td>
<td>Yes</td>
<td>Editable</td>
<td><h6>Cho phép user nhập thông tin KH để tìm kiếm.</h6>
<p>Cho phép nhập các giá trị sau:</p>
<ul>
<li><p>Mã CusID</p></li>
<li><p>Số điện thoại (sđt đăng nhập hệ thống app/web)</p></li>
<li><p>Email (Email đăng nhập hệ thống app/web)</p></li>
</ul>
<p>Click enter hoặc click chuột Hệ thống tìm kiếm mã cus theo điều kiện
nhập.</p>
<p>Kiểm tra mã cus nhập vào hệ thống:</p>
<ul>
<li><p>Nếu KH đang có khai báo kỳ thanh toán COD hàng ngày Thông báo lỗi
“KH đang có kỳ thanh toán hàng ngày”</p></li>
<li><p>Nếu KH đang không phải kỳ thanh toán hàng ngày Hiển thị thông tin
KH tìm kiếm</p></li>
<li><p>Mã KH nhập bị trùng với mã KH đã nhập báo lỗi “Mã KH đã được
nhập”</p></li>
</ul></td>
</tr>
<tr>
<td><strong>5</strong></td>
<td>Tên KH</td>
<td>Text</td>
<td>N/A</td>
<td>Readonly</td>
<td><p>Hiển thị tên KH theo cus đã tìm kiếm</p>
<p>Không có để trống</p></td>
</tr>
<tr>
<td><strong>6</strong></td>
<td>Số điện thoại</td>
<td>Text</td>
<td>N/A</td>
<td>Readonly</td>
<td><p>Hiển thị SĐT KH theo cus đã tìm kiếm</p>
<p>Không có để trống</p></td>
</tr>
<tr>
<td><strong>7</strong></td>
<td>Email</td>
<td>Text</td>
<td>N/A</td>
<td>Readonly</td>
<td><p>Hiển thị Email KH theo cus đã tìm kiếm</p>
<p>Không có để trống</p></td>
</tr>
<tr>
<td><strong>8</strong></td>
<td>Loại kỳ thanh toán</td>
<td>Text</td>
<td>N/A</td>
<td>Readonly</td>
<td><p>Hiển thị loại kỳ thanh toán đang áp dụng theo cus đã tìm kiếm</p>
<p>Không có để trống</p></td>
</tr>
<tr>
<td><strong>9</strong></td>
<td>Loại kỳ thanh toán khai báo</td>
<td>Dropdownlist</td>
<td>Yes</td>
<td>Editable</td>
<td><p>Cho phép chọn loại kỳ thanh toán</p>
<p>Mặc định chọn: Hàng ngày</p></td>
</tr>
<tr>
<td><strong>10</strong></td>
<td>Thao tác</td>
<td>Button</td>
<td>Yes</td>
<td>Editable</td>
<td><p>Cho phép thao tác xóa mã KH đã nhập.</p>
<p>- Click Xóa Hiển thị thông báo Xác nhận xóa mã KH.</p>
<p>Hiển thị tooltip khi Hower chuột “Xóa”</p></td>
</tr>
<tr>
<td><strong>11</strong></td>
<td>Xác nhận</td>
<td>Button</td>
<td>Yes</td>
<td>Editable</td>
<td>Click Cập nhật để gửi yêu cầu xác thực đẩy yêu cầu xác thực sang hệ
thống App KH</td>
</tr>
<tr>
<td><strong>12</strong></td>
<td>Đóng</td>
<td>Button</td>
<td>Yes</td>
<td>Editable</td>
<td>Click “Đóng” để tắt nội dung thay đổi</td>
</tr>
<tr>
<td><strong>13</strong></td>
<td>Thêm dòng</td>
<td>Button</td>
<td>Yes</td>
<td>Editable</td>
<td>Cho phép user thêm dòng để nhập mã KH khai báo</td>
</tr>
</tbody>
</table> 

## Yêu cầu nghiệp vụ chi tiết

KH được xác thực thanh công sẽ có Kỳ thanh toán hàng ngày hệ thống tự động cập nhật toàn bộ mã KH EVTP của mã CusID về kỳ thanh toán của cus

Kỳ thanh toán sẽ thay đổi nếu KH thực hiện Ký PL thay đổi hình thức thanh toán hoặc thực hiện yêu cầu xác thực lại Kỳ thanh toán Kỳ thanh toán đã được khai báo sẽ được cập nhật về trạng thái Không hoạt động.

Ảnh hưởng:

\- Màn hình quản lý KH chi nhánh trên HR thêm type "Thanh toán COD hàng ngày"

\- Màn hình quản lý KH FICO thêm type "Thanh toán COD hàng ngày"

\- Chức năng chi: hệ thống gom chi tự động theo đúng hình thức thanh toán của KH

# Chi tiết chức năng Xác thực OTP trên app KH

## SCR1: Màn hình yêu cầu xác thực

### Màn hình
<table>
<colgroup>
<col/>
<col/>
<col/>
<col/>
</colgroup>
<thead>
<tr>
<th>|<image_1>|</th>
<th>|<image_2>|</th>
<th>|<image_3>|</th>
<th>|<image_4>|</th>
</tr>
</thead>
<tbody>
<tr>
<td>MH01</td>
<td>MH02</td>
<td>MH03</td>
<td>MH04</td>
</tr>
</tbody>
</table> 

### Mô tả màn hình

  * Hiển thị thông báo “Khách hàng có 1 yêu cầu xác thực thay đổi ngày thanh toán COD. Xác thực ngay.” click thông báo hiển thị màn hình MH02: Xác nhận cập nhật ngày thanh toán click Xác nhận hiển thị màn hình MH03: nhập mã xác thực OTP Xác thực thành công hiển thị màn hình MH04: thông báo cập nhật thành công,

  * MH01: Chi tiết tài khoản Hiển thị cảnh báo “Khách hàng có 1 yêu cầu xác thực thay đổi ngày thanh toán COD. Xác thực ngay.” Click Xác thực ngay Chuyển sang màn MH02.

  * MH02: Xác nhận cập nhật ngày thanh toán.


  * Hiển thị thông tin cập nhật

  * Click Xác nhận chuyển màn hình MH03

  * Click Bỏ qua để từ chối cập nhật Cập nhật trạng thái “Xác nhận thất bại” với lý do “KH từ chối xác nhận.”


  * MH03: Xác thực OTP


  * KH nhập mã xác thực qua tin nhắn gửi về.

  * Xác thực thành công chuyển màn hình MH04

  * Xác thực không thành công quay về màn hình MH01.


MH04: Thông báo thành công Hiển thị thông báo “Cập nhật thông tin thanh toán thành công” nếu KH xác thực OTP thành công