# Public_174

ETL (Extract, Transform, Load) đóng vai trò quan trọng trong quản lý dữ liệu và xử lý thông tin. Để hiểu rõ hơn về ETL là gì và vai trò của nó, chúng ta cần xem xét quy trình và các bước cơ bản trong quá trình này. Từ việc trích xuất dữ liệu từ nguồn, biến đổi chúng để phù hợp với mục đích cụ thể, cho đến việc tải dữ liệu đã chuẩn hóa vào hệ thống lưu trữ, ETL đóng vai trò quan trọng trong việc chuẩn bị dữ liệu cho các hoạt động phân tích và ứng dụng trong môi trường kinh doanh hiện đại. Hãy cùng đi sâu vào quy trình ETL là gì để hiểu rõ hơn về tính chất và cách thức hoạt động của nó nhé!

# ETL là gì?

Trích xuất, chuyển đổi và tải (ETL) đại diện cho việc tập hợp dữ liệu từ nhiều nguồn khác nhau và hợp nhất chúng vào một kho lưu trữ trung tâm lớn, thường gọi là kho dữ liệu. ETL sử dụng các nguyên tắc kinh doanh để xử lý và sắp xếp dữ liệu gốc, sau đó chuẩn bị thông tin để sử dụng trong quá trình lưu trữ, phân tích và các ứng dụng học máy (ML). Qua việc phân tích dữ liệu, người dùng có thể giải quyết các nhu cầu cụ thể về thông tin kinh doanh, bao gồm việc dự đoán kết quả từ các quyết định kinh doanh, tạo ra báo cáo và bảng thông tin, cải thiện khả năng vận hành hiệu quả và nhiều mục đích khác.

|<image_1>|

# Tại sao ETL lại quan trọng?

Ngày nay, các tổ chức sở hữu cả dữ liệu có cấu trúc và dữ liệu phi cấu trúc từ nhiều nguồn khác nhau, bao gồm:

Dữ liệu về khách hàng từ hệ thống quản lý quan hệ khách hàng (CRM) và giao dịch thanh toán trực tuyến.

Dữ liệu liên quan đến hàng tồn kho và các hoạt động từ hệ thống của các nhà cung cấp.

Dữ liệu từ các cảm biến trên các thiết bị Internet của mọi vật IoT.

Dữ liệu tiếp thị từ các phương tiện truyền thông xã hội và phản hồi từ khách hàng.

Dữ liệu về nhân viên từ hệ thống quản lý nhân sự nội bộ.

|<image_2>|

Bằng việc thực hiện quy trình trích xuất, chuyển đổi và tải (ETL), các tập dữ liệu thô riêng lẻ có thể được chuẩn bị theo một định dạng và cấu trúc dễ tiêu thụ hơn cho mục đích phân tích, tạo ra thông tin sâu hơn và có giá trị hơn. Ví dụ, các doanh nghiệp bán lẻ trực tuyến có thể phân tích dữ liệu từ các điểm bán hàng để dự báo nhu cầu và quản lý hàng tồn kho. Các nhóm tiếp thị có thể tích hợp dữ liệu từ CRM với phản hồi từ khách hàng trên mạng xã hội để nghiên cứu hành vi của người tiêu dùng.

# ETL mang lại lợi ích cho việc thu thập thông tin kinh doanh như thế nào?

Lợi ích của ETL là gì trong việc cải thiện việc thu thập và phân tích thông tin kinh doanh:

## 3.1. Lịch sử và bối cảnh

ETL đóng vai trò quan trọng trong việc cung cấp cái nhìn sâu rộng về lịch sử dữ liệu của tổ chức. Điều này cho phép doanh nghiệp kết hợp dữ liệu cũ với thông tin mới từ các nền tảng và ứng dụng hiện đại. Bằng việc xem xét dữ liệu cũ đồng thời với dữ liệu mới, ETL mở ra cái nhìn dài hạn về thông tin.

## 3.2. Hợp nhất dữ liệu

ETL cung cấp một chế độ xem hợp nhất về dữ liệu để phân tích và tạo báo cáo chi tiết. Quản lý nhiều tập dữ liệu yêu cầu thời gian và sự phối hợp, có thể dẫn đến việc xử lý không hiệu quả và chậm trễ. ETL kết hợp các cơ sở dữ liệu và các dạng dữ liệu khác nhau thành một chế độ xem thống nhất và duy nhất. Quá trình tích hợp dữ liệu cải thiện chất lượng dữ liệu và giảm thời gian cần thiết cho việc di chuyển, phân loại hoặc chuẩn hóa dữ liệu. Điều này giúp dễ dàng hơn trong việc phân tích, hình dung và hiểu các tập dữ liệu lớn.

|<image_3>|

## 3.3. Phân tích dữ liệu chính xác

ETL cung cấp khả năng phân tích dữ liệu chính xác hơn để đáp ứng các tiêu chuẩn về tuân thủ và quy định. Bằng cách tích hợp công cụ ETL với các công cụ kiểm soát chất lượng dữ liệu, bạn có thể tạo hồ sơ, kiểm tra và làm sạch dữ liệu, đảm bảo rằng dữ liệu được xác thực và tin cậy.

## 3.4. Tự động hóa tác vụ

ETL tự động hóa các tác vụ xử lý dữ liệu lặp đi lặp lại để tăng hiệu suất trong phân tích. Công cụ ETL tự động hóa việc di chuyển dữ liệu và bạn có thể lập lịch để tích hợp thay đổi dữ liệu theo định kỳ hoặc thậm chí trong quá trình chạy. Điều này giúp nhân viên dữ liệu dành nhiều thời gian hơn cho sáng tạo và ít thời gian hơn trong việc quản lý các công việc tẻ nhạt như di chuyển và chuẩn hóa dữ liệu.

|<image_4>|

# ETL đã phát triển như thế nào?

ETL (Extraction, Transformation, Loading) xuất phát từ sự xuất hiện của cơ sở dữ liệu quan hệ, nơi dữ liệu được tổ chức và lưu trữ dưới dạng các bảng để dễ dàng phân tích. Ban đầu, các công cụ ETL đã được phát triển để chuyển đổi dữ liệu từ định dạng giao dịch sang định dạng quan hệ để phục vụ mục đích phân tích.

## 4.1. ETL truyền thống

Trước đây, dữ liệu nguyên thủy thường được lưu trữ trong cơ sở dữ liệu giao dịch, hỗ trợ nhiều yêu cầu về đọc và ghi dữ liệu nhưng không phù hợp cho mục đích phân tích. Có thể coi nó như việc lưu trữ dữ liệu trong một bảng tính. Ví dụ, trong hệ thống thương mại điện tử, cơ sở dữ liệu giao dịch lưu trữ thông tin về các mặt hàng đã mua, chi tiết về khách hàng và đơn hàng trong một giao dịch. Trong một năm, nó ghi chép một danh sách dài các giao dịch với các mục nhập lặp lại cho cùng một khách hàng đã mua nhiều mặt hàng khác nhau trong năm đó. Với sự trùng lặp dữ liệu này, việc phân tích các mặt hàng phổ biến nhất hoặc xu hướng mua hàng trong năm trở nên phức tạp.

|<image_5>|

Để giải quyết vấn đề này, các công cụ ETL đã tự động chuyển đổi dữ liệu giao dịch sang dạng dữ liệu quan hệ, trong đó các bảng được liên kết với nhau. Nhà phân tích có thể sử dụng các truy vấn để xác định mối quan hệ giữa các bảng, cũng như phân tích các mẫu và xu hướng.

## 4.2. ETL hiện đại

Khi công nghệ ETL phát triển, cả loại dữ liệu và nguồn dữ liệu đều tăng về quy mô. Công nghệ đám mây đã xuất hiện để tạo ra các hệ thống lưu trữ rộng lớn, hay còn gọi là các Data Warehouse. Những Data Warehouse như vậy có khả năng tiếp nhận dữ liệu từ nhiều nguồn và sử dụng các tài nguyên phần cứng có khả năng mở rộng theo thời gian. Các công cụ ETL cũng đã trở nên tinh vi hơn và có khả năng làm việc với các Data Warehouse hiện đại. Chúng có thể chuyển đổi dữ liệu từ các định dạng dữ liệu cổ điển sang các định dạng dữ liệu hiện đại. Dưới đây là một số ví dụ về các hệ thống lưu trữ dữ liệu hiện đại.

### 4.2.1. Kho dữ liệu (Data Warehouse)

Kho dữ liệu là một trung tâm lưu trữ dữ liệu có khả năng chứa nhiều cơ sở dữ liệu khác nhau. Trong mỗi cơ sở dữ liệu, dữ liệu được tổ chức thành các bảng và cột mô tả các loại dữ liệu trong bảng đó. Phần mềm của kho dữ liệu hoạt động trên nhiều loại phần cứng lưu trữ như ổ cứngthể rắn (SSD), ổ cứng và lưu trữ đám mây khác, nhằm tối ưu hóa việc xử lý dữ liệu.

|<image_6>|

### 4.2.2. Hồ dữ liệu (Data Lake)

Data Lake cho phép bạn lưu trữ toàn bộ dữ liệu, bao gồm cả dữ liệu có cấu trúc và không có cấu trúc, ở bất kỳ quy mô nào tại một nơi tập trung. Bạn có thể lưu trữ dữ liệu nguyên gốc mà không cần phải cấu trúc hóa trước dựa trên các câu hỏi có thể xuất hiện trong tương lai. Hồ dữ liệu cho phép sử dụng nhiều phương pháp phân tích khác nhau trên dữ liệu của bạn, từ truy vấn SQL, phân tích dữ liệu lớn, tìm kiếm toàn văn bản, phân tích thời gian thực đến học máy (ML), giúp hướng dẫn quyết định một cách hiệu quả hơn.

|<image_7>|

# ETL hoạt động như thế nào?

Quá trình ETL (Trích xuất, Chuyển đổi, Tải) là quá trình chuyển dữ liệu từ hệ thống nguồn đến hệ thống đích theo các chu kỳ thời gian cố định. Quá trình ETL là gì và bao gồm bao nhiêu giai đoạn cụ thể có thể tóm gọn như sau:

Trích xuất dữ liệu từ cơ sở dữ liệu nguồn.

Chuyển đổi dữ liệu để phù hợp với yêu cầu phân tích.

Tải dữ liệu vào cơ sở dữ liệu đích

# Trích xuất dữ liệu là gì?

Trong quá trình trích xuất dữ liệu, các công cụ ETL (Trích xuất, Chuyển đổi, Tải) thu thập hoặc sao chép dữ liệu thô từ nhiều nguồn và lưu trữ chúng tạm thời trong một khu vực lưu trữ trung gian, thường được gọi là vùng đệm. Vùng đệm hoạt động như một bước trung gian để tạm thời lưu giữ dữ liệu đã được trích xuất. Thông thường, vùng đệm chứa dữ liệu tạm thời và sẽ bị xóa sau khi quá trình trích xuất dữ liệu hoàn tất. Tuy nhiên, nó cũng có thể được sử dụng như một nguồn dữ liệu dự phòng để khắc phục sự cố khi cần thiết.

|<image_8>|

Việc dữ liệu được chuyển từ nguồn đến kho lưu trữ đích phụ thuộc vào cơ chế thu thập và theo dõi sự thay đổi của dữ liệu. Quá trình trích xuất dữ liệu thường được thực hiện theo một trong ba cách sau đây.

**Thông báo cập nhật**

Trong quá trình thông báo cập nhật, hệ thống nguồn thông tin về việc thay đổi bản ghi dữ liệu. Sau đó, bạn có thể thực hiện quá trình trích xuất dữ liệu chỉ từ những thay đổi đó. Đa số cơ sở dữ liệu và ứng dụng web đều cung cấp các cơ chế cập nhật để hỗ trợ tích hợp dữ liệu theo phương pháp này.

**Trích xuất tăng dần**

Một số nguồn dữ liệu không thể gửi thông báo cập nhật, nhưng có khả năng xác định và trích xuất dữ liệu đã được sửa đổi trong một khoảng thời gian cụ thể. Trong tình huống này, hệ thống sẽ kiểm tra các thay đổi theo chu kỳ nhất định, ví dụ như hàng tuần, hàng tháng hoặc khi một chiến dịch kết thúc. Điều này giúp bạn chỉ trích xuất dữ liệu đã có sự thay đổi.

|<image_9>|

**Trích xuất hoàn toàn**

Một số hệ thống không thể xác định sự thay đổi trong dữ liệu hoặc cung cấp thông báo, do đó, việc tải lại toàn bộ dữ liệu là phương pháp duy nhất. Cách tiếp cận này đòi hỏi bạn duy trì một bản sao của lần trích xuất gần nhất để kiểm tra bản ghi nào là mới nhất. Tuy nhiên, do phương pháp này yêu cầu truyền toàn bộ dữ liệu, chúng tôi khuyên bạn chỉ nên áp dụng cho các bảng dữ liệu nhỏ.

# Chuyển đổi dữ liệu là gì?

Trong quá trình chuyển đổi dữ liệu, các công cụ ETL (Trích xuất, Chuyển đổi, Tải) sẽ thực hiện việc chuyển đổi và hợp nhất dữ liệu thô từ vùng đệm để chuẩn bị cho kho dữ liệu đích. Quá trình chuyển đổi dữ liệu có thể bao gồm các loại thay đổi dữ liệu sau đây.

## 7.1. Chuyển đổi dữ liệu cơ bản

Các chuyển đổi cơ bản trong quá trình chuyển đổi dữ liệu:

**Làm sạch dữ liệu** : Làm sạch dữ liệu là quá trình loại bỏ các lỗi và biến đổi dữ liệu nguồn để phù hợp với định dạng dữ liệu đích.

**Ví dụ** : Chuyển đổi trường dữ liệu trống thành giá trị số 0, ánh xạ các dữ liệu "Parent" thành "P" hoặc "Child" thành "C."

|<image_10>|

**Chống trùng lặp dữ liệu** : Quá trình này tập trung vào xác định và loại bỏ các bản ghi trùng lặp trong dữ liệu.

**Sửa đổi định dạng dữ liệu** : Chỉnh sửa định dạng dữ liệu là việc biến đổi dữ liệu sang một định dạng thống nhất, bao gồm đổi đơn vị đo lường, định dạng ngày/tháng/năm theo chuẩn.

**Ví dụ** : Một công ty thực phẩm có thể sử dụng các đơn vị khác nhau trong cơ sở dữ liệu, như kilogram và cân Anh. Quá trình ETL sẽ chuyển đổi tất cả các đơn vị sang cân Anh để có định dạng thống nhất.

## 7.2. Chuyển đổi dữ liệu nâng cao

Chuyển đổi nâng cao áp dụng quy tắc kinh doanh để tối ưu hóa dữ liệu cho việc phân tích thuận lợi hơn. Dưới đây là các ví dụ về các loại chuyển đổi này:

**Dẫn xuất** : Dẫn xuất là việc áp dụng các quy tắc kinh doanh vào dữ liệu để tạo ra các giá trị mới dựa trên thông tin hiện có. Ví dụ: Chuyển đổi doanh thu thành lợi nhuận bằng cách trừ đi chi phí hoặc tính tổng chi phí mua hàng bằng cách nhân giá của mỗi mặt hàng với số lượng đã đặt.

**Gộp ghép** : Trong quá trình chuẩn bị dữ liệu, gộp ghép là việc kết nối dữ liệu tương tự từ các nguồn dữ liệu khác nhau. Ví dụ: Tính tổng chi phí mua một mặt hàng bằng cách cộng giá trị mua hàng từ các nhà cung cấp khác nhau và chỉ lưu tổng kết quả trong hệ thống đích.

|<image_11>|

**Chia tách** : Chia tách dữ liệu cho phép bạn phân chia một cột hoặc thuộc tính dữ liệu thành nhiều cột trong hệ thống đích. Ví dụ: Nếu tên khách hàng trong nguồn dữ liệu được ghi là "Jane John Doe", bạn có thể chia thành các cột riêng biệt cho họ, tên đệm và tên.

**Tổng hợp** : Tổng hợp cải thiện chất lượng dữ liệu bằng việc tổng hợp nhiều giá trị dữ liệu thành một tập dữ liệu nhỏ hơn. Ví dụ: Tính tổng hóa đơn đặt hàng từ khách hàng để xây dựng chỉ số giá trị lâu dài của khách hàng (CLV) bằng cách cộng gộp giá trị trong một khoảng thời gian nhất định.

|<image_12>|

**Mã hóa** : Mã hóa dữ liệu nhạy cảm nhằm bảo vệ tính riêng tư hoặc tuân thủ luật dữ liệu trước khi dữ liệu được truyền đến cơ sở dữ liệu đích.

# Tải dữ liệu là gì?

Trong quá trình tải dữ liệu, công cụ ETL (Extract, Transform, Load) di chuyển dữ liệu đã trải qua quá trình chuyển đổi từ khu vực lưu đệm vào kho dữ liệu đích. Đối với hầu hết các tổ chức sử dụng ETL, quá trình này được tự động hóa, có định rõ, liên tục và theo lịch trình hàng loạt. Dưới đây là hai phương pháp tải dữ liệu.

**Tải hoàn toàn** : Trong quá trình tải hoàn toàn, toàn bộ dữ liệu từ nguồn được chuyển đổi và đưa vào kho dữ liệu. Quá trình này thường diễn ra khi bạn tải dữ liệu từ hệ thống nguồn vào kho dữ liệu lần đầu tiên.

**Tải tăng dần** : Trong phương pháp tải tăng dần, công cụ ETL tải delta (hoặc sự chênh lệch) giữa hệ thống đích và nguồn theo các khoảng thời gian đều đặn. Công cụ này ghi nhớ ngày trích xuất cuối cùng để chỉ tải các bản ghi được thêm vào sau ngày này. Có hai cách để thực hiện tải tăng dần.

|<image_13>|

**Tải tăng dần theo luồng** : Trong trường hợp có khối lượng dữ liệu nhỏ, bạn có thể truyền các thay đổi liên tục qua đường ống dữ liệu tới kho dữ liệu đích. Đối với tốc độ dữ liệu lớn như hàng triệu sự kiện mỗi giây, bạn có thể áp dụng xử lý luồng sự kiện để theo dõi và xử lý dữ liệu đồng thời, cho quyết định nhanh hơn.

**Tải gia tăng theo hàng loạt** : Nếu bạn xử lý khối lượng dữ liệu lớn, bạn có thể thu thập các thay đổi dữ liệu và tải chúng theo từng loạt theo lịch trình định kỳ. Trong khoảng thời gian định kỳ này, không có hành động nào xảy ra với hệ thống nguồn hoặc hệ thống đích khi dữ liệu được đồng bộ hóa.

# ELT là gì?

ELT là viết tắt của "Extract, Load, Transform", một phương pháp mở rộng đảo ngược thứ tự của quá trình "Extract, Transform, Load" (ETL). Trong ELT, dữ liệu có thể được tải trực tiếp vào hệ thống đích trước khi trải qua quá trình xử lý. Không cần phải sử dụng khu vực lưu đệm trung gian, bởi vì kho dữ liệu đích có khả năng xử lý dữ liệu bên trong nó. Sự phổ biến của việc sử dụng cơ sở hạ tầng đám mây đã làm cho ELT trở nên phổ biến hơn, cung cấp sức mạnh xử lý cần thiết cho cơ sở dữ liệu đích.

|<image_14>|

**So sánh ETL và ELT**

ELT thích hợp với việc xử lý các tập dữ liệu không có cấu trúc, có khối lượng lớn và yêu cầu tải dữ liệu thường xuyên. Đây cũng là công cụ lý tưởng cho dữ liệu lớn, vì quá trình lập kế hoạch phân tích có thể được thực hiện sau khi dữ liệu được trích xuất và lưu trữ. Ngược lại, ETL để lại phần lớn công việc chuyển đổi dữ liệu cho giai đoạn phân tích và tập trung vào việc tải dữ liệu thô được xử lý tối thiểu vào kho dữ liệu.

|<image_15>|

Quy trình ETL đòi hỏi sự xác định nhiều hơn từ ban đầu. Cần phải tiến hành phân tích sâu hơn từ đầu để xác định loại, cấu trúc và mối quan hệ của dữ liệu đích. Các nhà khoa học dữ liệu thường sử dụng ETL để tải cơ sở dữ liệu cũ vào kho dữ liệu, và hiện nay, ELT đã trở thành tiêu chuẩn chung.

# Ảo hóa dữ liệu là gì?

Ảo hóa dữ liệu sử dụng lớp trừu tượng hóa phần mềm để tạo ra chế độ xem dữ liệu tích hợp mà không cần phải trích xuất, chuyển đổi hoặc tải dữ liệu một cách vật lý. Các tổ chức sử dụng tính năng này như một kho lưu trữ dữ liệu ảo hợp nhất mà không cần chi phí và sự phức tạp trong việc xây dựng và quản lý các nền tảng nguồn và đích riêng biệt. Mặc dù ảo hóa dữ liệu có thể được kết hợp với quá trình trích xuất, chuyển đổi và tải (ETL), nhưng nó ngày càng được coi là một giải pháp thay thế cho ETL và các phương pháp tích hợp dữ liệu vật lý khác. Ví dụ, bạn có thể sử dụng AWS Glue Elastic Views để nhanh chóng tạo ra một bảng ảo, hay còn gọi là một chế độ xem cụ thể hóa, từ nhiều kho dữ liệu nguồn khác nhau.

|<image_16>|

# AWS Glue là gì?

AWS Glue là một dịch vụ tích hợp dữ liệu không cần máy chủ, giúp người dùng dễ dàng khám phá, chuẩn bị, di chuyển và tích hợp dữ liệu từ nhiều nguồn khác nhau để sử dụng cho hoạt động phân tích, máy học và phát triển ứng dụng.

Tính năng của AWS Glue:

Khả năng khám phá và kết nối với hơn 80 kho lưu trữ dữ liệu đa dạng.

Quản lý dữ liệu một cách tập trung trong một danh mục dữ liệu.

AWS Glue Studio, dành cho kỹ sư dữ liệu, nhà phát triển ETL, nhà phân tích dữ liệu và người dùng doanh nghiệp, để tạo, chạy và theo dõi quy trình ETL nhằm tải dữ liệu vào hồ dữ liệu.

Cung cấp giao diện ETL trực quan, Sổ tay và trình soạn mã cho người dùng với các công cụ phù hợp với bộ kỹ năng của họ.

Phiên tương tác cho phép kỹ sư dữ liệu khám phá, tác giả và kiểm thử tác vụ thông qua IDE hoặc sổ tay mà họ ưa thích.

AWS Glue là dịch vụ không cần máy chủ và tự động điều chỉnh quy mô theo nhu cầu, giúp người dùng tập trung vào việc thu thập thông tin từ dữ liệu ở quy mô petabyte mà không cần lo lắng về quản lý cơ sở hạ tầng

|<image_17>|

Để bắt đầu sử dụng AWS Glue, bạn có thể tạo tài khoản AWS.

# Tạm kết

Tóm lại, việc quản lý dữ liệu ngày nay đang trở nên quan trọng hơn bao giờ hết, và các công cụ như ETL, ELT, ảo hóa dữ liệu cùng với các dịch vụ như AWS Glue đang chơi vai trò quan trọng trong việc thu thập, xử lý và tận dụng thông tin từ nhiều nguồn khác nhau. Chúng mở ra cánh cửa cho sự linh hoạt và tiện ích, giúp tạo ra một môi trường quản lý dữ liệu hiệu quả và linh hoạt. Nhờ vào sự phát triển này, người dùng có khả năng tận dụng dữ liệu một cách nhanh chóng và thông minh hơn, từ đó đưa ra quyết định thông minh và tạo ra sáng kiến đổi mới trong môi trường kinh doanh ngày nay.