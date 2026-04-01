# Public_189

## 1. CƠ SỞ LÝ THUYẾT

## 1.1 Tổng quan SQL Server

#### 1.1.1 SQL Server là gì?

SQL Server là gì? SQL Server hay Microsoft SQL Server là một hệ thống quản trị cơ sở dữ liệu quan hệ (Relational Database Management System – RDBMS) được phát triển bởi Microsoft vào năm 1988. Nó được sử dụng để tạo, duy trì, quản lý và triển khai hệ thống RDBMS.

Được thiết kế để quản lý và lưu trữ dữ liệu, SQL Server cho phép người dùng truy vấn, thao tác và quản lý dữ liệu một cách hiệu quả và an toàn. SQL Server là một trong những hệ quản trị cơ sở dữ liệu phổ biến nhất trên thế giới và được sử dụng rộng rãi trong các doanh nghiệp.

Phần mềm SQL Server được sử dụng khá rộng rãi vì nó được tối ưu để có thể chạy trên môi trường cơ sở dữ liệu rất lớn lên đến Tera – Byte cùng lúc phục vụ cho hàng ngàn user. Bên cạnh đó, ứng dụng này cung cấp đa dạng kiểu lập trình SQL từ ANSI SQL (SQL truyền thống) đến SQL và cả T-SQL (Transaction-SQL) được sử dụng cho cơ sở dữ liệu quan hệ nâng cao.

T-SQL là một ngôn ngữ mở rộng của SQL với các tính năng bổ sung như biến, điều kiện, vòng lặp và xử lý ngoại lệ, giúp người dùng viết các đoạn mã SQL manh mẽ và linh hoat hơn.

## 1.1.2 Cấu trúc của SQL Server

Sơ đồ dưới đây minh họa cấu trúc của SQL Server:

2025-09-28 21,40.54\_AI Race

![](images/image1.jpg)

SQL Server là một hệ quản trị cơ sở dữ liệu phức tạp với nhiều thành phần cấu thành giúp nó hoạt động hiệu quả và đáng tin cậy. Trong đó, SQL Server gồm ba thành phần quan là **Database Engine, External Protocols** và **SQLOS**.

## *1.1.2.1. Database Engine*

Database Engine là thành phần chính của MS SQL Server, chịu trách nhiệm quản lý và xử lý dữ liệu. Nó bao gồm các thành phần con quan trọng sau:

## *Storage Engine*

• File Storage: Quản lý các tệp dữ liệu và tệp nhật ký giao dịch. Dữ liệu được lưu trữ trong các tệp dữ liệu (.mdf và .ndf), trong khi các giao dịch được ghi lại trong tệp nhật ký giao dịch (.ldf).

• Buffer Manager: Quản lý bộ nhớ đệm (buffer pool), lưu trữ các trang dữ liệu được truy cập gần đây để tăng tốc độ truy vấn.

• Transaction Log: Ghi lại mọi thay đổi dữ liệu để đảm bảo tính toàn vẹn và khả năng phục hồi của cơ sở dữ liệu.

2

#### *Query Processor*

- Parser: Phân tích cú pháp các câu lệnh SQL và chuyển chúng thành các cây cú pháp (syntax tree) để xử lý tiếp theo.
- Optimizer: Tối ưu hóa các kế hoạch thực hiện truy vấn để đảm bảo hiệu suất cao nhất. Nó chọn lựa các kế hoạch truy vấn tối ưu dựa trên thống kê và chi phí ước tính.
- Executor: Thực hiện các kế hoạch truy vấn đã được tối ưu hóa, xử lý các câu lệnh SQL và trả về kết quả.

#### *Relational Engine*

- Metadata Manager: Quản lý thông tin về cấu trúc cơ sở dữ liệu như bảng, chỉ mục, ràng buộc và các đối tượng khác.
- Transaction Manager: Quản lý các giao dịch, đảm bảo tính nhất quán, cách ly và độ bền của các giao dịch thông qua các nguyên tắc ACID.
- Concurrency Control: Điều khiển đồng thời, sử dụng các kỹ thuật như khóa (locking) và phiên bản (versioning) để quản lý các truy cập đồng thời đến dữ liệu.

## *1.1.2.2. SQLOS (SQL Server Operating System)*

SQLOS là lớp trừu tượng phần cứng và hệ điều hành của SQL Server, cung cấp các dịch vụ cơ bản cho Database Engine. SQLOS chịu trách nhiệm quản lý tài nguyên hệ thống như bộ nhớ, CPU và I/O. Dưới đây là các thành phần chính của SQLOS:

## *Memory Management*

- Memory Allocation: Quản lý phân bổ và giải phóng bộ nhớ cho các hoạt động của SQL Server.
- Buffer Pool: Điều khiển bộ nhớ đệm, lưu trữ các trang dữ liệu được truy cập gần đây để giảm thiểu truy cập đĩa.

#### *Scheduler*

- Task Management: Quản lý các tác vụ và luồng, đảm bảo rằng các tác vụ được thực hiện hiệu quả và không có tác vụ nào bị bỏ lỡ.
- Worker Threads: Quản lý các luồng công việc (worker threads), thực hiện các yêu cầu truy vấn và các hoạt động khác của SQL Server.

#### *I/O Management*

• I/O Requests: Quản lý các yêu cầu I/O, bao gồm đọc và ghi dữ liệu từ đĩa.

- Async I/O: Hỗ trợ I/O không đồng bộ để cải thiện hiệu suất bằng cách cho phép các yêu cầu I/O được xử lý đồng thời. *Synchronization*
- Lock Manager: Quản lý các khóa để điều khiển truy cập đồng thời đến dữ liệu, đảm bảo tính nhất quán và tránh xung đột.
- Latches and Spinlocks: Sử dụng các cơ chế khóa nhẹ hơn như latches và spinlocks để bảo vệ các cấu trúc dữ liệu nội bộ của SQL Server.

#### *1.1.2.3. External Protocol*

External Protocol bao gồm các giao thức và công nghệ cho phép SQL Server tương tác với các hệ thống và ứng dụng bên ngoài. Các giao thức chính bao gồm:

- TDS (Tabular Data Stream): Giao thức chính được sử dụng để trao đổi dữ liệu giữa SQL Server và các ứng dụng khách như SQL Server Management Studio (SSMS), ứng dụng web và các ứng dụng tùy chỉnh. TDS xử lý việc truyền dữ liệu truy vấn, kết quả và các thông báo giữa máy chủ và khách.
- ODBC (Open Database Connectivity) và OLE DB: Các giao thức tiêu chuẩn cho phép các ứng dụng kết nối và tương tác với SQL Server. ODBC và OLE DB cung cấp các API để thực hiện các truy vấn, cập nhật và thao tác dữ liệu khác.
- JDBC (Java Database Connectivity): Giao thức tiêu chuẩn cho phép các ứng dụng Java kết nối và tương tác với SQL Server. JDBC cung cấp các API để thực hiện các truy vấn và thao tác dữ liệu từ các ứng dụng Java.
- HTTP/HTTPS: SQL Server hỗ trợ các giao thức HTTP/HTTPS để cung cấp các dịch vụ web, chẳng hạn như SQL Server Reporting Services (SSRS) và SQL Server Integration Services (SSIS). Điều này cho phép SQL Server cung cấp các dịch vụ dữ liệu qua web và tích hợp với các ứng dụng web.

## **1.2 SQL Server dùng để làm gì?**

SQL Server là một hệ quản trị cơ sở dữ liệu mạnh mẽ và linh hoạt do Microsoft phát triển, được sử dụng rộng rãi trong nhiều lĩnh vực khác nhau. Các chức năng chính của SQL Server bao gồm tạo và duy trì cơ sở dữ liệu, phân tích dữ liệu và tạo báo cáo. Dưới đây là các ứng dụng cụ thể của SQL Server:

## **Tạo và duy trì cơ sở dữ liệu**

SQL Server được sử dụng để tạo và duy trì các cơ sở dữ liệu quan hệ, cung cấp nền tảng vững chắc cho việc lưu trữ và quản lý dữ liệu. Các chức năng chính bao gồm:

- Quản lý dữ liệu: SQL Server cho phép người dùng tạo, sửa đổi và xóa các bảng dữ liệu, chỉ mục, và các mối quan hệ giữa các bảng. Hệ thống quản lý dữ liệu của SQL Server hỗ trợ các thao tác CRUD (Create, Read, Update, Delete), giúp quản lý dữ liệu một cách hiệu quả.
- Bảo mật dữ liệu: SQL Server cung cấp các tính năng bảo mật mạnh mẽ như mã hóa dữ liệu, kiểm soát truy cập dựa trên vai trò và xác thực người dùng. Các biện pháp bảo mật này đảm bảo rằng dữ liệu được bảo vệ khỏi các mối đe dọa và truy cập trái phép.
- Quản lý giao dịch: SQL Server hỗ trợ các tính năng quản lý giao dịch như Atomicity, Consistency, Isolation và Durability (ACID), đảm bảo rằng các thay đổi trong cơ sở dữ liệu được thực hiện một cách nhất quán và an toàn. Điều này rất quan trọng đối với các ứng dụng yêu cầu độ tin cậy cao như tài chính, ngân hàng và thương mại điện tử.
- Sao lưu và phục hồi: SQL Server cung cấp các tính năng sao lưu và phục hồi dữ liệu, cho phép người dùng tạo các bản sao lưu toàn bộ, gia tăng và khác biệt. Các tính năng này giúp bảo vệ dữ liệu khỏi mất mát do lỗi phần cứng, phần mềm hoặc lỗi con người và đảm bảo rằng dữ liệu có thể được phục hồi nhanh chóng trong trường hợp xảy ra sự cố.

## **Phân tích dữ liệu và tạo báo cáo**

SQL Server không chỉ là công cụ quản lý dữ liệu mà còn cung cấp các tính năng phân tích dữ liệu mạnh mẽ và tạo báo cáo chi tiết, giúp các tổ chức ra quyết định dựa trên dữ liệu một cách hiệu quả. Các chức năng chính bao gồm:

- Phân tích dữ liệu: SQL Server tích hợp sẵn các công cụ phân tích dữ liệu như SQL Server Analysis Services (SSAS), cho phép người dùng xây dựng các mô hình dữ liệu phức tạp và thực hiện các phân tích sâu. Các công cụ này hỗ trợ việc tạo ra các báo cáo phân tích, biểu đồ và bảng điều khiển (dashboards) giúp người dùng hiểu rõ hơn về dữ liệu và xu hướng.
- Tạo báo cáo: SQL Server Reporting Services (SSRS) là một công cụ mạnh mẽ cho phép người dùng tạo, quản lý và triển khai các báo cáo. SSRS hỗ trợ nhiều định dạng báo cáo khác nhau như PDF, Excel và HTML, giúp người dùng dễ dàng chia sẻ và trình bày thông tin. Các báo cáo có thể được tùy chỉnh để đáp ứng nhu cầu cụ thể của doanh nghiệp, từ báo cáo tài chính đến báo cáo hiệu suất kinh doanh.

• Khai thác dữ liệu: SQL Server hỗ trợ các tính năng khai thác dữ liệu (data mining) giúp phát hiện các mẫu và xu hướng ẩn trong dữ liệu lớn. Các công cụ khai thác dữ liệu này giúp doanh nghiệp đưa ra các dự đoán và quyết định dựa trên dữ liệu, cải thiện hiệu suất và tăng cường khả năng cạnh tranh.

• Tích hợp dữ liệu: SQL Server Integration Services (SSIS) là một công cụ mạnh mẽ cho phép người dùng tích hợp dữ liệu từ nhiều nguồn khác nhau vào một cơ sở dữ liệu duy nhất. SSIS hỗ trợ các hoạt động ETL (Extract, Transform, Load), giúp làm sạch, chuyển đổi và tải dữ liệu từ các hệ thống khác nhau vào SQL Server. Điều này giúp đảm bảo rằng dữ liệu luôn được cập nhật và nhất quán.

# **2. HƯỚNG DẪN CÀI ĐẶT SQL SERVER 2022**

**Bước 1:** Truy cập vào đường link: [https://www.microsoft.com/en-us/sql](https://www.microsoft.com/en-us/sql-server/sql-server-downloads?_ga=2.77687380.1361511729.1690361222-1340992660.1690361222)[server/sql-server-downloads](https://www.microsoft.com/en-us/sql-server/sql-server-downloads?_ga=2.77687380.1361511729.1690361222-1340992660.1690361222) 

![](images/image2.jpg)

**Bước 2:** Tìm đến **Express edition** of SQL Server 2022 và chọn **Download now**, chọn **Open file.**

![](images/image3.jpg)

**<u>Buốc 3:</u>** Chọn **Basic -> Accept ->** Chọn **Browser** lưu trữ **-> Install**.

![](images/image4.jpg)

![](images/image5.jpg)

21.40.54\_AI Race

![](images/image6.jpg)

Bước 4: Sau khi tải về thành công, ấn Install SSMS.

<table><tbody><tr><th>Express Edition

Installation has completed sumstance name
squexpress

squadministrators
Azureadi/nguyēn/ngocDiēmQuynh

Features installed
squengine

Version
16.0.1000.6, RTM

A computer restar</th><th></th></tr><tr><td>INSTANCE NAME
SQLEXPRESS

SQL ADMINISTRATORS
AzureAD\NguyēnNgocDiēmQuỳnh
FEATURES INSTALLED
SQLENGINE

VERSION
16.0.1000.6, RTM</td><td>ranast illi il</td></tr><tr><td>SQLEXPRESS

SQL ADMINISTRATORS

AzureAD\NguyễnNgọcDiễmQuỳnh

FEATURES INSTALLED

SQLENGINE

VERSION

16.0.1000.6, RTM</td><td>accessfully:</td></tr><tr><td>SQL ADMINISTRATORS

AzureAD\\NguyenNgocDiemQuynh

FEATURES INSTALLED

SQLENGINE

VERSION

16.0.1000.6, RTM</td><td>CONNECTION STRING</td></tr><tr><td>AzureAD\NguyễnNgọcDiễmQuỳnh

FEATURES INSTALLED

SQLENGINE

VERSION

16.0.1000.6, RTM</td><td>Server=localhost\SQLEXPRESS;Database=master;Trusted_Connection=True</td></tr><tr><td>FEATURES INSTALLED
SQLENGINE
VERSION
16.0.1000.6, RTM</td><td>SQL SERVER INSTALL LOG FOLDER</td></tr><tr><td>SQLENGINE

VERSION

16.0.1000.6, RTM</td><td>C:\Program Files\Microsoft SQL Server\160\Setup Bootstrap\Log\2023072</td></tr><tr><td>VERSION<br/>16.0.1000.6, RTM</td><td>INSTALLATION MEDIA FOLDER</td></tr><tr><td>16.0.1000.6, RTM</td><td>C:\SQL2022\Express_ENU</td></tr><tr><td>-8</td><td>INSTALLATION RESOURCES FOLDER</td></tr><tr><td>A computer restar</td><td>C:\Program Files\Microsoft SQL Server\160\SSEI\Resources</td></tr><tr><td>© Connect I</td><td>rt is required to complete your installation.</td></tr><tr><td></td><td>Now Customize Install SSMS Close</td></tr><tr><td></td><td>Install SSMS</td></tr></tbody></table>

Bước 5: Sau khi cửa sổ Download SSMS hiện ra, ấn vào link Download SSMS.

2025-09-28 21,40.54\_AI Race

![](images/image7.jpg)

Bước 6: Sau khi Download thành công, ấn Install.

2025-09-28 21,40.54\_AI Race

![](images/image8.jpg)

**RELEASE 19.1** 

# Microsoft SQL Server Management Studio with Azure Data Studio

Welcome. Click "Install" to begin.

Location:

21.40.54\_AI Race

C:\Program Files (x86)\Microsoft SQL Server Management Studio 19

Change

By clicking the "Install" button, I acknowledge that I accept the <u>Privacy Statement</u> and the License Terms for <u>SQL Server Management Studio</u> and <u>Azure Data Studio</u>

SQL Server Management Studio transmits information about your installation experience, as well as other usage and performance data, to Microsoft to help improve the product. To learn more about data processing and privacy controls, and to turn off the collection of this information after installation, see the <a href="documentation">documentation</a>

Install

Close

2025-09-28 21,40.54\_AI Race

![](images/image9.jpg)

<u>Bước 7:</u> Sau khi cài đặt, mở Microsoft SQL Server Management Studio 19, chọn Connect.

2025-09-28 21.40.54\_AIRace

![](images/image10.jpg)

![](images/image11.jpg)

- Để mở câu query mới, nhấn vào New Query trên thanh công cụ bên trên.
  - Để chạy câu lệnh, nhấn Ctrl + Enter hoặc nút Execute trên thanh công cụ bên trên.
  - Để xem bộ dữ liệu, nhấn mở mục Database ở thanh điều hướng bên trái màn hình.

Vậy là chúng ta đã hoàn tất việc cài đặt SQL Server 2022.

20/2.00

21.40.54\_AI Race

2025-09-28 21,40.54\_AI Race