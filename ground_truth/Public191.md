# Public_191

# CƠ SỞ LÝ THUYẾT

## Hệ điều hành Ubuntu

### Tổng quan về hệ điều hành Ubuntu

Ubuntu là một hệ điều hành máy tính mã nguồn mở dựa trên nền tảng [Linux](https://topdev.vn/blog/linux-la-gi/). Được phát triển và duy trì bởi Canonical Ltd. và cộng đồng người dùng toàn cầu, Ubuntu được thiết kế để cung cấp một trải nghiệm máy tính dễ sử dụng, ổn định và an toàn cho mọi người, từ người dùng cá nhân đến doanh nghiệp và tổ chức.

Ubuntu đi kèm với các tính năng như giao diện người dùng đồ họa (GUI) thân thiện, hỗ trợ cho nhiều loại phần cứng và phần mềm, cũng như khả năng tùy chỉnh linh hoạt để phù hợp với nhu cầu cụ thể của người dùng. Đặc biệt, Ubuntu được cung cấp hoàn toàn miễn phí và đồng thời được hỗ trợ bởi một cộng đồng lớn các nhà phát triển và người dùng trên toàn thế giới.

### Các phiên bản khác của Ubuntu

  * **Ubuntu LTS (Long Term Support)** là phiên bản Ubuntu được hỗ trợ dài hạn. Cụ thể, các phiên bản LTS của Ubuntu nhận được bảo trì và cập nhật bảo mật trong khoảng thời gian kéo dài hàng năm (ví dụ: 5 năm cho phiên bản LTS phổ biến nhất). Điều này làm cho Ubuntu LTS trở thành lựa chọn ổn định và lâu dài cho các doanh nghiệp và người dùng muốn tránh việc nâng cấp thường xuyên.

  * **Ubuntu Server** là một phiên bản Ubuntu được tối ưu hóa để sử dụng làm hệ điều hành cho các máy chủ. Nó cung cấp các tính năng và công cụ cần thiết để triển khai, quản lý và vận hành các dịch vụ và ứng dụng máy chủ, bao gồm các dịch vụ như web server, email server, database server và nhiều hơn nữa.

  * **Ubuntu MATE** là một biến thể của Ubuntu được thiết kế với một giao diện người dùng truyền thống và dễ sử dụng. Giao diện của Ubuntu MATE nhắm đến sự đơn giản và sự dễ dàng sử dụng cho người dùng, đồng thời vẫn cung cấp đầy đủ các tính năng và công cụ của hệ điều hành Ubuntu.

  * **Ubuntu Kylin** là một phiên bản Ubuntu được tối ưu hóa cho người dùng ở Trung Quốc. Nó được phát triển bởi một tổ chức Trung Quốc với mục tiêu làm cho Ubuntu trở nên thân thiện và dễ sử dụng hơn đối với người dùng Trung Quốc thông qua việc cung cấp các tính năng và ứng dụng phù hợp với nhu cầu và thói quen của địa phương.


### Những điểm nổi bật của hệ điều hành Ubuntu

|<image_1>|

Hệ điều hành Ubuntu có nhiều điểm nổi bật mà người dùng thường đánh giá cao:

  * **Miễn phí và mã nguồn mở:** Ubuntu là hệ điều hành hoàn toàn miễn phí. Bạn có thể tải xuống, cài đặt và sử dụng mà không phải trả bất kỳ khoản phí nào.

  * **Dễ sử dụng:** Giao diện đồ họa trực quan, các ứng dụng được cài đặt sẵn và cộng đồng hỗ trợ nhiệt tình giúp cho việc sử dụng Ubuntu trở nên dễ dàng hơn bao giờ hết.

  * **Ổn định và bảo mật:** Ubuntu được coi là một trong những phiên bản Linux ổn định nhất, với việc cập nhật bảo mật thường xuyên để bảo vệ người dùng khỏi các lỗ hổng tiềm ẩn.

  * **Tính tùy chỉnh:** Ubuntu có thể tùy chỉnh cao. Người dùng có thể thay đổi giao diện, cài đặt thêm phần mềm và cấu hình hệ điều hành theo nhu cầu của mình.

  * **Kho phần mềm phong phú:** Bạn có thể tìm thấy hầu hết các ứng dụng phổ biến cho Ubuntu, bao gồm trình duyệt web, trình soạn thảo văn bản, bảng tính, trình phát đa phương tiện và nhiều loại ứng dụng khác.

  * **Đa dạng phiên bản:** Ubuntu cung cấp nhiều biến thể như Ubuntu Desktop, Ubuntu Server, Ubuntu MATE, Ubuntu Kylin, v.v., phù hợp với nhu cầu sử dụng khác nhau của người dùng.

  * **Cộng đồng lớn mạnh:** Ubuntu có một cộng đồng người dùng và nhà phát triển rộng lớn trên toàn thế giới, với sự hỗ trợ, chia sẻ kiến thức và giải đáp thắc mắc qua các diễn đàn, blog và trang web.


### So sánh hệ điều hành Ubuntu với Windows

Dưới đây là một bảng so sánh giữa Ubuntu và Windows dựa trên một số tiêu chí phổ biến:

|<image_2>|

## Quy trình cài đặt Driver Nvidia sử dụng Repository chuẩn của Ubuntu

Phương pháp đầu tiên là dễ thực hiện nhất và trong hầu hết các trường hợp, đây là cách được khuyến nghị.

### Phương pháp cài đặt qua dòng lệnh

**_Bước 1:_** Đầu tiên, hãy xác định model card đồ họa Nvidia của bạn và driver được khuyến nghị. Để thực hiện, hãy chạy lệnh sau. Lưu ý rằng kết quả đầu ra và driver được khuyến nghị có thể khác nhau:|<image_3>|

Từ kết quả trên, chúng ta có thể kết luận rằng hệ thống hiện tại đã cài đặt card đồ họa **NVIDIA GeForce RTX 3080** và driver được khuyến nghị để cài đặt là **nvidia-driver-470**.

**_Bước 2:_** Cài đặt driver  
Nếu bạn đồng ý với đề xuất, hãy sử dụng lệnh ubuntu-drivers một lần nữa để tự động cài đặt tất cả các driver được khuyến nghị:

|<image_4>|

Ngoài ra, bạn có thể cài đặt driver mong muốn một cách chọn lọc sử dụng lệnh apt. Ví dụ:
|<image_5>|
**_Bước 3:_** Sau khi cài đặt hoàn tất, hãy khởi động lại hệ thống của bạn:
|<image_6>|

### Phương pháp cài đặt tự động reposity PPA để cài đặt driver Nvidia Beta

**_Bước 1:_** Việc sử dụng repository PPA graphics-drivers cho phép chúng ta cài đặt các driver Nvidia beta tiên tiến nhất, mặc dù có thể đi kèm với rủi ro hệ thống không ổn định. Để tiến hành, trước tiên hãy thêm repository ppa:graphics-drivers/ppa vào hệ thống của bạn:

|<image_7>|

**_Bước 2:_** Tiếp theo, hãy xác định model card đồ họa của bạn và driver được khuyến nghị:

|<image_8>|

**_Bước 3:_** Cài đặt Driver Nvidia:  
Tương tự như ví dụ với repository chuẩn của Ubuntu ở trên, bạn có thể tự động cài đặt tất cả các driver được khuyến nghị:

|<image_9>|

Hoặc, cài đặt một cách chọn lọc sử dụng lệnh apt. Ví dụ:

|<image_10>|

**_Bước 4:_** Sau khi cài đặt xong, khởi động lại máy tính của bạn:

|<image_11>|

### Phương pháp cài đặt thủ công sử dụng driver chính thức từ Nvidia.com theo hướng dẫn các bước 

**_Bước 1:_** Xác định card VGA của NVIDIA

Các lệnh dưới đây sẽ giúp bạn xác định model card Nvidia:

|<image_12>|

hoặc

|<image_13>|

hoặc

|<image_14>|

**_Bước 2:_** Tải Driver chính thức của Nvidia

Sử dụng trình duyệt web của bạn, hãy truy cập trang web chính thức của Nvidia và tải xuống driver phù hợp cho card đồ họa Nvidia của bạn. Ngoài ra, nếu bạn đã nắm rõ quy trình, bạn có thể tải driver trực tiếp từ danh sách driver Nvidia Linux. Khi hoàn tất, bạn sẽ có một file tương tự như file được hiển thị dưới đây:

|<image_15>|

**_Bước 3:_** Cài đặt các gói cần thiết

Các gói phụ thuộc sau đây cần được cài đặt để biên dịch và cài đặt driver Nvidia:

|<image_16>|

### Vô hiệu hóa driver Nouveau của Nvidia 

**_Bước 1:_** Bước tiếp theo là vô hiệu hóa driver Nouveau mặc định. Hãy làm theo hướng dẫn để vô hiệu hóa driver Nouveau mặc định.

|<image_17>|

Hãy chắc chắn rằng bạn đã khởi động lại hệ thống trước khi tiến hành bước tiếp theo.

**_Bước 2:_** Dừng Trình Quản Lý Desktop

Để cài đặt driver Nvidia mới, chúng ta cần dừng server hiển thị hiện tại. Cách đơn giản nhất là chuyển sang runlevel 3 sử dụng lệnh telinit. Sau khi thực thi lệnh dưới đây, server hiển thị sẽ dừng lại, vì vậy hãy chắc chắn lưu lại tất cả công việc hiện tại (nếu có) trước khi tiến hành:

|<image_18>|

Nhấn **CTRL+ALT+F1** và đăng nhập với tên người dùng cùng mật khẩu của bạn để mở phiên TTY1 mới hoặc đăng nhập qua SSH.

**_Bước 3:_** Cài đặt Driver Nvidia

Để bắt đầu cài đặt driver Nvidia, thực hiện lệnh dưới đây và làm theo hướng dẫn:

|<image_19>|

**_Bước 4:_** Driver Nvidia đã được cài đặt. Khởi động lại hệ thống của bạn:

|<image_20>|

**_Bước 5:_** Cấu hình cài đặt NVIDIA X Server. Sau khi khởi động lại, bạn sẽ có thể mở ứng dụng **NVIDIA X Server Settings** từ menu **Activities**.

Sau khi cài driver NVIDIA, bạn có thể nâng cấp trải nghiệm với một [**VPS server**](https://dataonline.vn/cloud-vps-gia-re/) mạnh mẽ