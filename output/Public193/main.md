# Public_193

# TỔNG QUAN VỀ VỊ TRÍ DEVOPS

## Devops là gì?

**DevOps** là một sự kết hợp của các nguyên lý, thực hành, quy trình và các tool giúp tự động hóa quá trình lập trình và chuyển giao phần mềm. Với DevOps, các công ty có thể “release” các tính năng nhỏ rất nhanh và kết hợp các phản hồi mà họ nhận được một cách nhanh chóng. DevOps là kết hợp của các cụm từ tiếng Anh software development và information technology operations.

  * Giai đoạn phát triển (development) bao gồm phần việc của UI designer, developer, [QA/QC](https://topdev.vn/blog/qa-la-gi-qc-la-gi/)…

  * Giai đoạn vận hành (operations) có sự tham gia của system engineer, system administrator, operation executive, release engineer, DBA, network engineer,…


Hai giai đoạn này tương đối tách rời nhau. Đặc biệt là ở những công ty có quy mô từ trung bình trở lên. Chính vì thế, khái niêm **devops** ra đời nhằm tối ưu hóa chu trình phát triển phần mềm. Giúp sản phẩm phần mềm được release nhanh và thường xuyên hơn.

|<image_1>|

## Devops Engineer là vị trí gì?

Các công việc chính của **DevOps Engineer** gần giống với công việc của Sysadmin, bao gồm: deploy, optimizing, monitoring, analysis… Điểm khác biệt là:

  * DevOps Engineer đòi hỏi nhiều kĩ năng mềm hơn như phải có coding skill, scripting để automation hệ thống.

  * DevOps Engineer cần tìm hiểu về tech stack mà sản phẩm công ty đang sử dụng. Ngoài ra họ cũng có thể cùng review bug hay viết những unit test thông thường.


**DevOps Engineer** nay thường phải tham gia ngay vào giai đoạn phát triển nhằm:

  * Chuẩn hóa môi trường làm việc từ local cho đến production.

  * Hiểu sản phẩm hơn, để tối ưu hóa sản phẩm tốt hơn.

  * Nắm được cơ bản logic code, nắm được tiến trình của code chạy như thế nào.v.v…


## Công việc của Devops Engineer

DevOps là một thành phần cực kỳ quan trọng trong [quy trình phát triển phần mềm](https://topdev.vn/blog/quy-trinh-phat-trien-phan-mem/) cùng với phương pháp [Agile](https://topdev.vn/blog/agile-la-gi-scrum-la-gi/). Nó giúp hoàn thiện việc chuyển đổi quy trình phát triển và vận hành phần mềm từ mô hình thác nước (waterfall) sang mô hình phát triển/phát hành liên tục (CI/CD).

Tất cả đều phục vụ cho mục đích cuối cùng là cải thiện khả năng triển khai phần mềm một cách nhanh chóng. Từ đó, tăng khả năng cạnh tranh của sản phẩm/doanh nghiệp.

Một khi đã hiểu được những giá trị thực sự của DevOps và thực hiện những thay đổi nhỏ, vững vàng thì team bạn có thể bắt đầu cuộc hành trình với DevOps được rồi:

  * CI (Continuous Integration): Một hình thức trong việc phát triển phần mềm, các developer thường gộp hoặc chuyển các thay đổi trong code về một repo master, và các build và test sau đó sẽ tự động chạy. Mục tiêu của CI đó là tìm bug nhanh hơn từ sớm, cải thiện chất lượng phần mềm, và giản thiểu thời gian để xác thực và ra mắt các update mới.

  * CD (Continuous Deployment) : Mọi thay đổi được duyệt qua test sẽ tự động được triển khai trên production. Nghĩa là bạn pull bản build mới nhất ngay hoặc tìm repo mới nhất đã được test và tiến hành deploy trên production. CD là một cách tuyệt vời để tăng tốc quá trình deploy sản phẩm liên tục để đáp ứng các yêu cầu liên tục của khách hàng.

  * Xây dựng kiến trúc (Infrastructure as code) hệ thống như là code: Định nghĩa này hơi khó hiểu, có thể hiểu như là một phương pháp để đảm bảo rằng bạn có thể maintain chất lượng version control trong khi sử dụng CI. Infrastructure cần được cấu hình tự động hoàn toàn để các server được chuẩn hóa các bản patch và version mới nhất.

  * Communication và Collaboration: Collaboration và communication là các nhân tố bí ẩn giúp doanh nghiệp phát triển và đánh giá DevOps. Nó đẩy nhanh quá trình phát triển, vận hành và cả các team khác như marketing, sales, cho phép các bộ phận của tổ chức tiến gần hơn với việc đạt được mục tiêu.


|<image_2>|

## Tại sao Doanh nghiệp cần Devops

  * **Tốc độ** : DevOps giúp các developers và team operations đạt được mục tiêu ở một tốc độ khác giúp cải tiến sản phẩm nhanh chóng phục vụ người dùng, thích nghi với thị trường tốt hơn và điểu chỉnh hiểu quả kinh doanh hiệu quả hơn.

  * **Chuyển giao nhanh chóng** : Tăng tốc độ release thường xuyên để chúng ta cải thiện sản phẩm nhanh hơn và cho ra mắt các feature nhanh hơn cũng như fix bug, giúp phản hồi cho khách hàng nhanh chóng và xây dựng nên lợi thế cạnh tranh tốt hơn.

  * **Độ tin cậy** : DevOps đảm bảo chất lượng bằng cách áp dụng CI /CD, Monitoring và logging process. Bằng cách update mà team infrastructure cấp quyền cho team development để chuyển giao nhanh hơn mà vẫn duy trì được trải nghiệm người dùng tốt.

  * **Mở rộng** : Team vận hành, quản lý infra và các quy trình. Lên kế hoạch về quy mô và nâng cấp môi trường giúp quản trị các hệ thống phức tạp hoặc hay thay đổi hiệu quả cũng như giảm thiểu rủi ro.

  * **Bảo mật** : DevOps giúp di chuyển mà không chịu tổn thất về bảo mật bằng các chính sách, kiểm soát và phương pháp quản lý configuration. Thậm chí các team có thể kêu gọi bạn theo các tiêu chuẩn từ sớm bằng cách cung cấp các setup các tool theo dõi.


# Lộ trình phát triển nghề Devops

## Devops cần học gì?

Để làm được devops bạn phải biết khá nhiều thứ về system cũng như coding và nhiều kỹ năng sau đây:

  * Biết và sử dụng thành thạo linux, window, macOS. Biết dùng thành thạo lệnh Terminal trong linux, CMD và powercell trong window và lệnh trong Linux hoặc Macos. Có kiến thức cơ bản về: Process Management, Threads and Concurrency, Sockets, I/O Management, Virtualization, Memory storage and File systems.

  * Nên có kiến thức cơ bản về: DNS, HTTP, HTTPS, FTP, SSL. Hoặc tìm hiểu thêm về các lỗ hổng bảo mật thường gặp.

  * Biết cài đặt và sử dụng vài Web Server phổ biến như: Apache và Nginx. Tìm hiểu một số khái niệm và chức năng thường được sử dụng: Caching Server, Load balancer, Reverse Proxy, and Firewall. Có thể bắt đầu với một vài practice với Docker đơn giản như:

* Setup thử một vài cache server

* Giả lập có nhiều servers dưới local bằng cách dùng các Docker container. Sử dụng chức năng Load balancer của Web server để cân bằng tải cho server.

  * Biết và sử dụng một số dịnh vụ cloud như AWS của amazon, google cloud, và azure của microsoft.

  * Biết code một số ngôn ngữ hệ thống như bashscript, java, javascipt , python, Php…

  * Biết dùng 1 số tool để truyển khai CI&CD như jenkins, jira , git (Gitlab, Bitbucket…)… Một DevOps Engineer nên biết Infrastructure as code):

* Containers: Docker, Kubernetes

* Các công cụ quản lý cấu hình: Ansible, Pupet, Chef,..

  * Biết sử dụng các tool monitoring server như: Nagios, Zabbix, Icing, Datadog…


## Devops Roadmap

|<image_3>|