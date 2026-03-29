# Public_180

# Khái niệm Performance Test là gì?

Performance Test là một quy trình hoặc phương pháp được sử dụng để đánh giá hiệu suất và khả năng chịu tải của một ứng dụng hoặc hệ thống. Mục đích của việc thực hiện Performance Test nhằm xác định các chỉ số hiệu suất như thời gian phản hồi, tải trọng tối đa mà hệ thống có thể chịu được.

|<image_1>|

Đồng thời, chương trình phát hiện và giải quyết các vấn đề hiệu suất ngẫu nhiên xuất hiện trong quá trình sử dụng ứng dụng hoặc hệ thống. Performance Test thường được thực hiện bằng cách tạo ra một phương án giả lập để mô phỏng các hoạt động thực tế của người dùng. Các chỉ số hiệu suất chính được đánh giá bao gồm:

  * Thời gian phản hồi: Thời gian mà hệ thống mất để phản hồi sau khi nhận một yêu cầu từ người dùng.

  * Tải trọng tối đa: Sức chứa tối đa của hệ thống, tức là số lượng yêu cầu mà hệ thống có thể xử lý trong một khoảng thời gian nhất định mà vẫn đáp ứng được yêu cầu hiệu suất mong muốn.

  * Băng thông: Khả năng truyền dữ liệu của hệ thống, đo bằng số lượng dữ liệu được truyền qua hệ thống trong một khoảng thời gian nhất định.

  * Sự ổn định: Khả năng của hệ thống chịu được tải trọng liên tục trong một thời gian dài mà không gây ra sự sụp đổ hay giảm hiệu suất.


Thông qua Performance Test, người ta có thể đánh giá và cải thiện hiệu suất của ứng dụng hoặc hệ thống. Từ đó đảm bảo rằng chương trình có thể hoạt động một cách ổn định và đáp ứng được nhu cầu của người dùng.

# Phân biệt các loại Performance Test

Trên thực tế có nhiều loại Performance Testing khác nhau trong quy trình kiểm thử phần mềm. Dưới đây là một số loại phổ biến:

## Load Testing

Load Testing kiểm tra hiệu suất của hệ thống khi chịu đựng tải trọng cao. Điều này đảm bảo rằng hệ thống có thể xử lý một lượng lớn yêu cầu từ người dùng trong khi duy trì hiệu suất mong muốn. Load Testing thường xác định ngưỡng tải trọng tối đa mà hệ thống có thể chịu được.

|<image_2>|

## Stress Testing

Stress Testing đo và đánh giá khả năng chịu đựng của hệ thống khi gặp tải trọng ngoại lệ, vượt quá giới hạn bình thường. Mục tiêu của hoạt động này chính là xác định điểm yếu và giới hạn của hệ thống.

## Soak Testing

Soak Testing là quá trình kiểm tra hiệu suất của hệ thống trong thời gian dài. Yếu tố này đánh giá sự ổn định và khả năng chịu được của hệ thống trong môi trường hoạt động liên tục.

## Spike Testing

Spike Testing đánh giá khả năng của hệ thống để xử lý một tải trọng cao đột ngột. Kiểm tra này đảm bảo rằng hệ thống không bị sụp đổ trong trường hợp có một số lượng lớn người dùng truy cập cùng một lúc.

## Endurance Testing

Endurance Testing kiểm tra khả năng hoạt động của hệ thống trong điều kiện chịu tải trọng và liên tục kéo dài thời gian. Mục tiêu của việc này nhằm xác định khả năng hệ thống duy trì hiệu suất mong muốn trong môi trường hoạt động thực tế.

|<image_3>|

## Scalability Testing

Scalability Testing đánh giá khả năng hệ thống mở rộng và tăng cường mức độ xử lý khi tải trọng tăng lên. Kiểm tra này giúp đảm bảo rằng hệ thống có thể mở rộng để đáp ứng nhu cầu người dùng tăng lên theo thời gian.

Mỗi loại Performance Testing phục vụ mục tiêu kiểm tra hiệu suất và khả năng chịu đựng của hệ thống trong các tình huống khác nhau. Việc sử dụng các loại kiểm tra phù hợp sẽ đảm bảo rằng hệ thống hoạt động ổn định. Từ đó đáp ứng hiệu suất mong muốn trong mọi tình huống.

# Những vấn đề về hiệu năng trên hệ thống

## Thời gian phản hồi

Đây là khoảng thời gian mà hệ thống cần để phản hồi sau khi nhận một yêu cầu từ người dùng. Thời gian phản hồi dài có thể làm giảm trải nghiệm người dùng và gây ra cảm giác không hài lòng. Nếu hệ thống không có đủ băng thông thì việc truyền dữ liệu có thể rơi vào tình trạng bị chậm hoặc bị chặn.

|<image_4>|

## Tải trọng và khả năng chịu đựng

Biểu thị khả năng hệ thống để xử lý số lượng yêu cầu từ người dùng mà không gây giảm hiệu suất hay sụp đổ. Nếu tải trọng vượt quá khả năng chịu đựng của hệ thống thì hiệu suất có thể giảm đi hoặc gặp sự cố.

## Hiệu suất hoạt động

Yếu tố này cho thấy tính hiệu quả của các chức năng và quá trình hoạt động trong hệ thống. Nếu một phần hoặc toàn bộ quá trình hoạt động chậm sẽ ảnh hưởng đến hiệu suất của hệ thống. Cách sử dụng và quản lý tài nguyên như bộ nhớ, bộ xử lý và dung lượng đĩa thường ảnh hưởng đến yếu tố này. Nếu tài nguyên không được quản lý tốt thì hệ thống có thể gặp sự cố hoặc hiệu suất giảm đi.

## Các vấn đề sản phẩm

Một số lỗi hoặc vấn đề trong mã nguồn, cấu trúc dữ liệu, cơ sở dữ liệu hoặc cấu hình có thể gây ra vấn đề về hiệu suất. Việc kiểm tra và giải quyết những vấn đề này vô cùng quan trọng. Từ đó mà người dùng có thể đảm bảo hệ thống hoạt động một cách mượt mà và hiệu quả hơn.

# Hướng dẫn cách kiểm thử hiệu năng cơ bản

Quy trình kiểm thử hiệu năng có tác dụng đảm bảo hệ thống hoạt động một cách ổn định. Từ đó đáp ứng được yêu cầu sử dụng hiệu năng của người dùng

|<image_5>|

## Xác định yêu cầu hiệu năng

Đầu tiên, bạn cần xác định các yêu cầu hiệu năng cụ thể cho hệ thống. Điều này bao gồm các hoạt động như: xác định thời gian phản hồi tối đa, tải trọng tối đa, số lượng người dùng đồng thời và các yêu cầu khác liên quan đến hiệu năng của hệ thống.

## Thiết kế kịch bản kiểm thử

Tạo ra các kịch bản kiểm thử phù hợp với yêu cầu hiệu năng đã xác định. Các kịch bản này nên phản ánh các hoạt động thực tế mà người dùng thực hiện trên hệ thống. Ví dụ: thêm sản phẩm vào giỏ hàng, gửi yêu cầu truy vấn cơ sở dữ liệu, đăng nhập vào hệ thống và tìm kiếm thông tin.

## Chuẩn bị môi trường kiểm thử

Chuẩn bị môi trường để thực hiện kiểm thử hiệu năng. Trong đó bao gồm những việc cài đặt và cấu hình các máy chủ, cơ sở dữ liệu và phần mềm kiểm thử hiệu năng.

## Thực hiện kiểm thử

Chạy các kịch bản kiểm thử trên môi trường đã chuẩn bị và thu thập dữ liệu hiệu năng. Đo và ghi lại các chỉ số hiệu năng như thời gian phản hồi, tải trọng và băng thông. Các công cụ kiểm thử hiệu năng như Apache jmeter hoặc Loadrunner có thể được sử dụng trong quy trình này.

|<image_6>|

## Phân tích kết quả

Phân tích dữ liệu hiệu năng thu thập được từ quá trình kiểm thử. Đánh giá hiệu suất thực tế của hệ thống, xác định kỹ thuật và vấn đề hiệu suất tiềm tàng.

## Tối ưu hóa hiệu năng

Dựa trên kết quả phân tích, thực hiện các biện pháp cải thiện hiệu suất cần thiết. Hoạt động này bao gồm việc tinh chỉnh cấu hình hệ thống, tối ưu hóa mã nguồn và cải thiện quy trình xử lý.

## Lặp lại kiểm thử

Chạy lại quy trình kiểm thử sau khi đã thực hiện các biện pháp tối ưu hóa. Tiếp tục thu thập dữ liệu và so sánh với kết quả trước đó để xác minh sự cải thiện trong hiệu suất.

## Báo cáo kết quả

Tạo báo cáo chi tiết về quá trình kiểm thử và kết quả hiệu năng. Báo cáo này nên gồm thông tin về các vấn đề phát hiện được, giải pháp tối ưu và những khuyến nghị để cải thiện hiệu suất của hệ thống.

# Giới thiệu các công cụ Performance Test

## Apache jmeter

Là một công cụ mã nguồn mở và miễn phí, Jmeter được sử dụng rộng rãi để thực hiện kiểm thử hiệu năng. Hệ thống hỗ trợ tạo kịch bản kiểm thử, quản lý, thực hiện quá trình thu thập dữ liệu và phân tích kết quả.

|<image_7>|

## Loadrunner

Bộ công cụ có trả phí do hãng Micro Focus phát triển, Loadrunner cung cấp khả năng kiểm tra hiệu năng, tải trọng và tư duy về quy mô. Phiên bản này hỗ trợ nhiều loại ứng dụng và có giao diện đơn giản giúp người dùng dễ sử dụng.

## Gatling

Đây là một công cụ kiểm thử hiệu năng mã nguồn mở và miễn phí. Gatling sử dụng Scala để tạo ra kịch bản kiểm thử và có khả năng xử lý tải trọng lớn. Chương trình cung cấp tính năng thu thập dữ liệu và phân tích kết quả hiệu năng.

## Webload

Webload là một công cụ kiểm thử hiệu năng có trả phí do hãng Radview Software phát triển. Phần mềm cung cấp khả năng thực hiện kiểm thử hiệu năng trên các ứng dụng web, di động và thiết bị iot. Webload hỗ trợ kiểm thử với tải lớn và cung cấp các tính năng phân tích hiệu năng.

|<image_8>|

## Apache Bench

Apache Bench là một công cụ kiểm thử hiệu năng miễn phí được cung cấp kèm theo bộ phần mềm máy chủ web Apache. Chương trình cung cấp khả năng đánh giá hiệu suất của máy chủ bằng cách gửi yêu cầu HTTP không đồng thời.

## Siege

Siege là một công cụ kiểm thử hiệu năng miễn phí và mã nguồn mở. Hệ thống có thể đánh giá hiệu suất của máy chủ dựa trên tải trọng và số lượng yêu cầu đồng thời.

Những công cụ này có thể hỗ trợ trong việc tạo và thực hiện kịch bản kiểm thử, thu thập dữ liệu hiệu năng và phân tích kết quả. Tuy nhiên, việc lựa chọn công cụ phụ thuộc vào yêu cầu cụ thể của dự án và tiêu chuẩn của nhóm kiểm thử.