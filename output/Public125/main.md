# Public_125

Loài kiến là loài sâu bọ có tính chất xã hội, chúng sống thành từng đàn, bởi vậy có sự tác động lẫn nhau, chúng thạo tìm kiếm thức ăn và hoàn thành những nhiệm vụ từ kiến chỉ huy. Một điều thú vị trong tìm kiếm thức ăn của vài con kiến đặc biệt là khả năng của chúng để tìm kiếm đường đi ngắn nhất giữa tổ kiến và nguồn thức ăn. Trên thực tế, điều dễ nhận thấy có trong suy nghĩ nhưng nhiều con kiến hầu hết không nhận ra vì chúng không dùng thị giác để tìm kiếm những đầu mối thức ăn.

Tất cả mọi con kiến hầu như là mù, chúng chỉ có thể tương tác với nhau và với môi trường bằng cách sử dụng pheromone: đi đến đâu chúng xịt pheromone ra đến đấy. Mỗi một con kiến tại mỗi vị trí quyết định hướng đi tiếp theo dựa vào nồng độ pheromone của các hướng. Tại vị trí mà nồng độ pheromone xung quanh đều bằng nhau hoặc không có pheromone thì chúng sẽ quyết định hướng đi một cách ngẫu nhiên. Cứ như vậy thì các con kiến cứ đi theo bước chân của nhau và tạo thành một đường đi (path). Ta xét trường hợp tổ kiến ở vị trí 1 và nguồn thức ăn ở vị trí 2 như hình vẽ

![A diagram of a diamond AI-generated content may be incorrect.](images/image1.png)

Giả sử tại thời điểm ban đầu có 2 con kiến ra đi tìm thức ăn. Vì ban đầu chưa có pheromone nên chúng chọn 2 hướng đi khác nhau một cách ngẫu nhiên. Một hướng có đường đi đến nguồn thức ăn dài hơn hướng kia. Trong giai đoạn đầu các con kiến đi sau sẽ cảm nhận thấy nồng độ pheromone của cả 2 hướng là như nhau nên cũng chọn đi theo một trong 2 hướng một cách ngẫu nhiên. Tuy nhiên đường đi ngắn hơn làm cho khoảng thời gian di chuyển từ tổ đến nguồn thức ăn rồi quay trở lại của mỗi con kiến theo con đường đó cũng ngắn hơn và do đó mật độ di chuyển qua lại của đàn kiến tại mỗi vị trí của con đường ngắn sẽ cao hơn con đường dài. Do mật độ qua lại lớn hơn dẫn đến kết quả là nồng độ pheromone trên con đường ngắn càng ngày càng cao hơn con đường dài. Kết quả cuối cùng là đàn kiến ngày càng từ bỏ con đường dài và đi theo con dường ngắn. Đến một lúc nào đó sẽ không còn con kiến nào đi theo con đường dài nữa mà tất cả đều đi theo con đường ngắn.

![A group of hexagons with dots AI-generated content may be incorrect.](images/image2.png)

Thuật toán dựa trên hoạt động của đàn kiến có một số biến thể. Dạng đơn giản nhất gọi là AS (Ant System). Thuật toán này chỉ dùng để giải quyết bài toán tìm đường. Ở mức cao hơn là thuật toán ACO (Ant Colony Optimization).

# Từ những con kiến trong tự nhiên tới thuật toán ACO.

Thuật toán ACO lấy ý tưởng từ việc kiếm thức ăn của đàn kiến ngoài thực tế để giải quyết các bài toán tối ưu tổ hợp. Chúng dựa trên cơ sở một đàn kiến nhân tạo, chúng được tính toán tìm kiếm thức ăn nhờ mùi lạ nhân tạo.

Cấu trúc cơ bản của thuật toán ACO: trong mỗi thuật toán, tất cả kiến đi xây dựng cách giải quyết bài toán bằng cách xây dựng một đồ thị. Mỗi cạnh của đồ thị miêu tả các bước kiến có thể đi được kết hợp từ hai loại thông tin hướng dẫn kiến di chuyển:

Thông tin kinh nghiệm (heuristic information): giới hạn kinh nghiệm ưu tiên di chuyển từ nút r tới s…của cạnh ars. Nó được đánh dấu bởi rs. Thông tin này không được thay đổi bởi kiến trong suốt quá trình chạy thuật toán.

Thông tin mùi lạ nhân tạo (artificial pheromone trail information), nó giới hạn “nghiên cứu sự thèm muốn” của chuyển động là kiến nhân tạo và bắt chước mùi lạ thực tế của đàn kiến tự nhiên. Thông tin này bị thay đổi trong suốt quá trình thuật toán chạy phụ thuộc vào cách giải quyết được tìm thấy bởi những con kiến. Nó được đánh dấu bởi rs.

Giới thiệu các bước ảnh hưởng từ những con kiến thật vào ACO. Có hai vấn đề cần chú ý:

  * Chúng trừu tượng hoá vài mô hình thức ăn của kiến ngoài thực tế để tìm ra đường đi tìm kiếm thức ăn ngắn nhất.

  * Chúng bao gồm vài đặc điểm không giống với tự nhiên nhưng lại cho phép thuật toán phát triển chứa đựng cách giải quyết tốt tới bài toán bị cản (ví dụ: sử dụng thông tin kinh nghiệm để hướng dẫn chuyển động của kiến).


Cách thức hoạt động cơ bản của một thuật toán ACO như sau: m kiến nhân tạo di chuyến, đồng thời và không đồng bộ, qua các trạng thái liền kề của bài toán. Sự di chuyển này theo một tập quy tắc làm cơ sở từ những vùng thông tin có sẵn ở các thành phần (các nút). Vùng thông tin này bao gồm thông tin kinh nghiệm và thông tin mùi lạ để hướng dẫn tìm kiếm. Qua sự di chuyển trên đồ thị kiến xây dựng được cách giải quyết. Những con kiến sẽ giải phóng mùi lạ ở mỗi lần chúng đi qua một cạnh (kết nối) trong khi xây dựng cách giải quyết (cập nhật từng bước mùi lạ trực tuyến). Mỗi lần những con kiến sinh ra cách giải quyết, nó được đánh giá và nó có thể tạo luồng mùi lạ là hoạt động của chất lượng của cách giải quyết của kiến (cập nhật lại mùi lạ trực tuyến). Thông tin này sẽ hướng dẫn tìm kiếm cho những con kiến đi sau.

Hơn thế nữa, cách thức sinh hoạt động của thuật toán ACO bao gồm thêm hai thủ tục, sự bay hơi mùi lạ ( _pheromone trail evaporation_ ) và hoạt động lạ ( _daemon actions_ ). Sự bay hơi của mùi lạ được khởi sự từ môi trường và nó được sử dụng như là một kĩ thuật để tránh tìm kiếm bị dừng lại và cho phép kiến khảo sát vùng không gian mới. Daemon actions là những hoạt động tối ưu như một bản sao tự nhiên để thực hiện những nhiệm vụ từ một mục tiêu xa tới vùng của kiến.

# Giới thiệu về thuật toán 

Các thuật toán kiến là các thuật toán dựa vào sự quan sát các bầy kiến thực. Kiến là loại cá thể sống bầy đàn. Chúng giao tiếp với nhau thông qua mùi mà chúng để lại trên hành trình mà chúng đi qua. Mỗi kiến khi đi qua một đoạn đường sẽ để lại trên đoạn đó một chất mà chúng ta gọi là mùi. Số lượng mùi sẽ tăng lên khi có nhiều kiến cùng đi qua. Các con kiến khác sẽ tìm đường dựa vào mật độ mùi trên đường, mật độ mùi càng lớn thì chúng càng có xu hướng chọn. Dựa vào hành vi tìm kiếm này mà đàn kíên tìm được đường đi ngắn nhất từ tổ đến nguồn thức ăn và sau đó quay trở tổ của mình.

Sau đây là ví dụ về luồng đi của đàn kiến thực tế.

![A diagram of a obstacle course AI-generated content may be incorrect.](images/image3.png)

**Hình 1**

  1. Kiến đi theo đường thẳng giữa A và E

  2. Khi có chướng ngại vật kiến sẽ chọn hướng đi, có hai hướng với khả năng kiến sẽ chọn là như nhau.

  3. Trên đường ngắn hơn thì nhiều mùi (pheromone) hơn


![A diagram of a hexagon with numbers and arrows AI-generated content may be incorrect.](images/image4.png)

**Hình 2**

Xem hình 2a là giải thích rõ tình huống trong hình 1b.

Giả sử khoảng cách DH=BH=DB qua C và =1, C là điểm nằm giữa B và D (hình 2a). Bây giờ chúng ta xem xét điều gì xảy ra tại những khoảng thời gian rời rạc: t=0, 1, 2… Giả định rằng 30 con kiến mới đi từ A đến B, 30 con từ E đến D, mỗi kiến di chuyển với tốc độ một đơn vị thời gian và khi di chuyển kiến để tại thời điểm t một vệt pheromone với nồng độ là 1\. Để đơn giản chúng ta xét lượng pheromone bay hơi hoàn toàn và liên tục trong khoảng thời gian (t+1, t+2).

Tại thời điểm t=0, thì không có vệt mùi nào trên cạnh và có 30 kiến ở B, 30 ở D. Việc lựa chọn đường đi của chúng ta ngẫu nhiên do đó, trung bình từ mỗi nút có 15 con kiến sẽ đi đến H và 15 con sẽ đi đến C (hình 2b)

Tại thời điểm t=1, 30 con kiến mới đi từ A đến B, lúc này nó sẽ chọn hướng đến C hoặc hướng đến H. Tại hướng đến H có vệt mùi 15 do 15 con kiến đi từ B đến H, tại hướng đến C có vệt mùi 30 do 15 kiến đi từ B đến D và 15 con đi từ D đến B thông qua C (hình 2c). Do đó khả năng kiến hướng đến chọn đường đến C, do đó số kiến mong muốn đi đến C sẽ gấp đôi số kiến đi đến H (20 con đến C và 10 con đến H). Tương tự như vậy cho 30 con kiến mới đi từ D đến B.

Quá trình sẽ liên tục cho đến khi tất cả kiến sẽ chọn đường đi ngắn nhất.

Trên đây chúng ta mô tả hành vi tìm kiếm của bầy kiến thực.Sau đây , chúng ta sẽ tìm hiểu sâu hơn về các thuật toán kiến.

Thuật toán tối ưu bầy kiến (ACO) nghiên cứu các hệ thống nhân tạo dựa vào hành vi tìm kiếm của bầy kiến thực và được sử dụng để giải quyết các vấn đề về tối ưu rời rạc.Thuật toán bầy kiến siêu tìm kiếm(ACO meta_heuristic) lần đầu tiên được Dorigo, Di Caro và Gambardella đề xuất vào năm 1999.

Metaheuristic là một tập các khái niệm về thuật toán được sử dụng để xác định các phương thức tìm kiếm thích hợp cho một tập các vấn đề khác nhau. Hay nói cách khác, một siêu tìm kiếm ( meta-heuristic) có thể coi là một phương thức tìm kiếm đa năng.

ACO là một meta-heuristic, trong đó một tập các con kiến nhân tạo phối hợp tìm kiếm các giải pháp tốt cho các vấn đề về tối ưu rời rạc. Sự phối hợp là yếu tố cối lõi của các thuật toán ACO. Các con kiến nhân tạo liên lạc với nhau thông qua trung gian mà ta thường gọi là mùi.

Các thuật toán ACO được sử dụng để giải quyết các vấn đề về tối ưu tổ hợp tĩnh và động. Các vấn đề tĩnh là các vấn đề mà ở đó các đặc tính của vấn đề là không thay đổi trong suốt quá trình giải quyết vấn đề. Còn các vấn đề động thì ngược lại là một hàm các tham số mà giá trị của nó là động hay thay đổi trong quá trình giải quyết vấn đề, ví dụ bài toán người đưa thư là một vấn đề dynamic problem

Hệ thống ACO lần đầu tiên được Marco Dorigo giới thiệu trong luận văn của mình vào năm 1992, và được gọi là Hệ thống kiến (Ant System, hay AS). AS là kết quả của việc nghiên cứu trên hướng tiếp cận trí tuệ máy tính nhằm tối ưu tổ hợp mà Dorigo được hướng dẫn ở Politecnico di milano với sự hợp tác của Alberto Colorni và Vittorio Maniezzo. AS ban đầu được áp dụng cho bài toán người du lịch (TSP) và QAP

Cũng vào năm 1992, tại hội nghị sự sống nhân tạo lần đầu tiên ở châu Âu, Dorigo và các cộng sự đã công bố bài: sự tối ưu được phân bố bởi đàn kiến.

Tiếp theo tại hội nghị quốc tế thứ hai về giải quyết các vấn đề song song trong tự nhiên ở Hà Lan (1992), ông và các cộng sự đã công bố bài: nghiên cứu về các đặc tính của một giải thuật kiến.

Kể từ năm 1995 Dorigo, Gambardella và Stützle đã phát triển các sơ đồ AS khác nhau. Dorigo và Gambardella đã đề xuất Hệ thống bầy kiến (Ant Colony System, hay ACS) trong khi Stützle and Hoos đề xuất MAX-MIN Ant System (MMAS). Tất cả đều áp dụng cho bài toán người du lịch đối xứng hay không đối xứng và cho kết quả mỹ mãn. Dorigo, Gambardella and Stützle cũng đề xuất những phiên bản lai của ACO với tìm kiếm địa phưong.

Vào năm 1995, L.M. Gambardella và M. Dorigo đã đề xuất hệ thống Ant-Q, là một cách tiếp cận học tăng cường cho cho bài toán TSP.Và nó được áp dụng trong Học Máy.

Tiếp đó, vào năm 1996, trong bài báo công nghệ của mình tại Bruxelles M. Dorigo và L.M. Gambardella đã công bố hệ thống Ant Conoly System. Đây là hệ thống đề cập đến cách học phối hợp áp dụng cho bài toán TSP.

Cũng trong năm 1996 này, T. Stützle và H. H. Hoos đã đề xuất hệt thống Max-Min Ant System **.** Đây là một hệ thống cải tiến hệ thống AntSystem ban đầu và được đánh giá là hệ thống tính toán trong tương lai.

Sau đó, vào năm 1997, G. Di Caro và M. Dorigo đã đề xuất hệ thống AntNet. Đây là cách tiếp cận về định hướng sự thích nghi. Và phiên bản cuối cùng của hệ thống AntNet về điều khiển mạng truyền thông đã được công bố vào năm 1998.

Cũng trong năm 1997, hệ thống Rank-based Ant System, một hệ thống cải tiến hệ thống kiến ban đầu về nghiên cứu hệ thống tính toán đã được đề xuất bởi B. Bullnheimer, R. F. Hartl và C. Strauss. Phiên bản cuối cùng của hệ thống này được công bố vào năm 1999.

Vào năm 2001, C. Blum, A. Roli, và M. Dorigo đã cho công bố về hệ thống kiến mới là Hyper Cube – ACO. Phiên bản mở rộng tiếp đó đã được công bố vào năm 2004.

Hầu hết các nghiên cứu gần đây về ACO tập trung vào việc phát triển các thuật toán biến thể để làm tăng hiệu năng tính toán của thuật toán Ant System ban đầu.

Trên đây là sơ lược chung về các thuật toán kiến, mục tiếp theo sẽ mô tả về sơ đồ chung của thuật toán kiến.

# Sơ đồ chung thuật toán đàn kiến

**Procedure** ACO

**Initial();**

**While** (!ĐK dừng) do

ConstructSolutions();

LocalSearch(); **/*** Tuỳ ý, có thể có hoặc không

UpdateTrails();

**End** ;

**End** ;

trong đó:

ĐK dừng (tức là điều kiện dừng) là điều kiện đạt được khi thuật toán ở trạng thái kết thúc. Với bài toán người đưa thư thì ĐK dừng là điều kiện đạt được khi số vòng lặp của thuật toán = số vòng lặp lớn nhất do người dùng tự định nghĩa hoặc là tất cả đàn kiến đều đi theo một đường (tức là đường đi ngắn nhất).

ConstrucSolutions() là hàm xây dựng một giải pháp có thể theo phương pháp siêu tìm kiếm(meta-heuristic), với bài toán người đưa thư thì đó là hàm xây dựng chu trình cho mỗi kiến .

UpdateTrails() là hàm cập nhật mùi cho hành trình mà kiến đã đi qua.

LocalSearch() là hàm tìm kiếm địa phương, giúp tìm ra tối ưu cục bộ.

![A diagram of a flowchart AI-generated content may be incorrect.](images/image5.png)

**Hình 3**. Sơ đồ chung của thuật toán bầy kiến

# Các bước giải quyết bài toán đàn kiến

Từ thuật toán trên ta có thể rút ra các bước giải quyết một bài toán ứng dụng với thuật toán đàn kiến:

Bước 1: Thể hiện bài toán trong khung của tập các thành phần và sự chuyển đổi hoặc bởi một đồ thị được đánh dấu bởi kiến đề xây dựng cách giải quyết.

Bước 2: Định nghĩa thích hợp cho mùi lạ rs là một xu hướng quyết định. Đó là một bước chủ yếu trong việc hình thanhg thuật toán ACO và xác định rõ mùi lạ không là một nhiệm vụ tầm thường và nó tính toán yêu cầu bên trong của bài toán sau đáp án.

Bước 3: Định nghĩa thích hợp kinh nghiệm cho mỗi quyết định để một con kiến có thể xây dựng cách giải quyết, ví dụ: định nghĩa thông tin kinh nghiệm rs kết hợp mỗi thành phần hoặc trạng thái chuyển đổi. Thông tin kinh nghiệm chủ yếu cho việc tìm kiếm tốt nếu thuật toán tìm kiếm vùng không có sẵn hoặc không thể ứng dụng.

Bước 4: Nếu thực hiện được, tạo ra một vùng thuật toán tìm kiếm hiệu quả cho bài toán sau đáp án bởi vì kết quả của nhiều ứng dụng ACO cho bài toán tổ hợp tối ưu NP-hard thể hiện qua sự tìm kiếm tốt nhất đạt được khi ACO có vùng lạc quan.

Bước 5: Lựa chọn một thuật toán ACO và ứng dụng nó vào những bài toán cần giải quyết.

Bước 6: Các tham số phù hợp của thuật toán ACO. Một điểm bắt đầu tốt cho tham số phù hợp là sử dụng cài đặt tham số để tìm kiếm tốt khi ứng dụng thuật toán ACO vào bài toán đơn giản hoặc các bài toán khác nhau. Một vấn đề khác chi phối thời gian trong nhiệm phù hợp là để sử dụng thủ tục động cho tham số phù hợp.

Nó nên xoá các bước tiếp có thể chỉ đưa ra một hướng dẫn sử dụng thuật toán ACO. Thêm nữa, việc sử dụng là sự kết hợp các quá trình ở đó với vài bài toán sâu hơn và hoạt động của thuật toán, vài lựa chọn ban đầu cần phải sửa lại. Cuối cùng, chúng ta muốn trên thực tế, điều quan trọng nhất của các bước là đầu tiên phải khớp bởi vì lựa chọn tồi ở trạng thái này tính không thể tính với một tham số gốc phù hợp tốt.

# Các sơ đồ thuật toán khác phát triển trên mô hình ACO

Nhiều thuật toán đã được đưa ra dựa trên mô hình thuật toán **metaheuristic ACO**. Trong các mô hình đưa ra để giải quyết các bài toán tổ hợp tối ưu **NP-khó** sau đây xin trình bày chi tiết về 5 mô hình. Các mô hình này là phát triển dựa trên mô hình thuật toán ACO cụ thể trình bày ở phần trên. Theo các nghiên cứu cho thấy khi sử dụng thuật toán bầy kiến nói chung các thông tin pheromone và heuristic có thể áp dụng cho các nút hoặc cạnh nối. Trong các thuật toán đưa ra sau đây thì thông tin pheromone và heuristic chỉ gắn với các cạnh mà thôi.

## Thuật toán Ant System (AS)

Được phát triển bởi Dorigo, Maniezzo và Colorni năm 1991, là thuật toán ACO đầu tiên. Ban đầu có 3 biến thể khác nhau là: AS-Density, AS-Quantity và AS-Cycle khác nhau bởi cách thức cập nhật thông tin Pheromone.

Trong đó:

  * AS-Density: Thì đàn kiến sẽ đặt thêm pheromone trong quá trình xây dựng lời giải (online step-by-step pheromone update), lượng pheromone để cập nhật là một hằng số.

  * AS-Quantity: Thì đàn kiến sẽ đặt thêm pheromone trong quá trình xây dựng lời giải (online step-by-step pheromone update), lượng pheromone để cập nhật là phụ thuộc vào độ mong muốn (thông tin heuristic) với đoạn đường đi qua ηij.

  * AS-Cycle: Thông tin pheromone sẽ được cập nhật khi lời giải đã hoàn thành (online delayed pheromone update). Đây là mô hình cho kết quả tốt nhất và được coi như là thuật toán AS.


❖ _**Quy tắc di chuyển của kiến**_

Trong thuật toán AS, kiến xây dựng một đường đi bắt đầu tại một đỉnh được chọn ngẫu nhiên.

Tại đỉnh i, một con kiến k sẽ chọn đỉnh j chưa được đi qua trong tập láng giềng của i theo công thức sau:

![A mathematical equation with a square root AI-generated content may be incorrect.](images/image6.png)

Trong đó:

![A white background with black text AI-generated content may be incorrect.](images/image7.png)

Sự lựa chọn của con khi quyết định đi từ đỉnh i qua đỉnh j và được tính theo công thức:

![A white background with black text AI-generated content may be incorrect.](images/image8.png)

❖ _**Quy tắc cập nhật thông tin mùi**_

Trong quá trình di chuyển tìm đường đi của đàn kiến, chúng thực hiện cập nhật thông tin mùi trên những đoạn đường mà chúng đã đi qua. Gắn với mỗi cạnh (i,j) nồng độ vết mùi ij và thông số heuristic ij trên cạnh đó.

Ban đầu nồng độ mùi trên mỗi cạnh (i,j) được khởi tạo một hằng số c, hoặc được xác định theo công thức:

![A math equations on a white background AI-generated content may be incorrect.](images/image9.png)

Việc cập nhập pherpmone được tiến hành như sau:

  * Đầu tiên tất cả pheromone trên các cung sẽ được giảm đi bởi một lượng:


![](images/image10.png)

Với _p_ trong khoảng (0,1) là tốc độ bay hơi của pheromone.

  * Tiếp theo mỗi con kiến trong đàn sẽ đặt thêm một lượng thông tin pheromone trên những cung mà chúng đã đi qua trong hành trình của chúng.


![A group of black letters AI-generated content may be incorrect.](images/image11.png)

Trong đó: deta ij là lượng pheromone mà con kiến k đặt lên cạnh mà nó đã đi qua và được tính như sau:

![A close up of black text AI-generated content may be incorrect.](images/image12.png)

Với: Ck là độ dài đường đi của con kiến thứ k sau khi hoàn thành đường đi, tức là bằng tổng các cung thuộc đường đi mà kiến đã đi qua.

## Thuật toán Ant Colony System (ACS)

Phát triển từ thuật toán AS

_**❖ Quy tắc di chuyển của kiến**_

Trong thuật toán ACS, con kiến k đang ở đỉnh i, việc kiến chọn đỉnh j để di chuyển đến được xác định bằng quy luật như sau:

  * Cho qo là một hằng số cho trước (0<q0<1)

  * Chọn ngẫu nhiên một giá trị q trong khoảng [0,1]

  * Nếu q<q0 kiến k chọn điểm j di chuyển tiếp theo dựa trên giá trị lớn nhất của thông tin mùi và thông tin heuristic có trên cạnh tương ứng với công thức:


![](images/image13.png)

  * Nếu q>q0 kiến k sẽ chọn đỉnh j chưa được đi qua trong tập láng giềng của I theo một quy luật phân bổ xác xuất được xác định theo công thức sau:


![A black math equation AI-generated content may be incorrect.](images/image14.png)

_**❖ Quy tắc cập nhật thông tin mùi**_

Cập nhật thông tin mùi toàn cục:

Một con kiến có đường đi tốt nhất sau mỗi lần lặp thì được phép cập nhật thông tin pheromone. Việc cập nhật được thực hiện theo công thức sau:

![](images/image15.png)

Cập nhật thông tin mùi cục bộ:

Công thức sau:

![A black text on a white background AI-generated content may be incorrect.](images/image16.png)

Với _p_ : là tham số bay hơi năm trong khoảng (0,1)

0 =1/(nCnm)

n: là số dỉnh hay là số thành phố

Cnm: chiều dài hành trình cho bởi phương pháp tìm kiếm gần nhát

## Thuật toán Max–Min Ant System (MMAS)

Được phát triển bởi Stutzle và Hooss vào năm 1996, được mở rộng lên từ hệ thống AS. Luật di chuyển của kiến được thực hiện tương tự như trong thuật toán ACS

_**❖ Quy tắc cập nhật thông tin mùi**_

Thuật toán MMAS thực hiện việc cập nhật thông tin mùi khi toàn bộ kiến trong đàn hoàn thành lời giải và lượng thông tin mùi chỉ cập nhật trên các cạnh thuộc lời giải tối ưu nhất. Ban đầu cũng thực hiện bay hơi thông tin mùi trên các cạnh thuộc lơi giải tối ưu với một lượng được xác định tại công thức (2.4).

Lượng pheromone trên một cạnh được xác định như sau:

![A group of black letters AI-generated content may be incorrect.](images/image17.png)

Cbest là độ dài đường đi ngắn nhất của con kiến thứ k sau khi cả đàn hoàn thành đường đi.

_**❖ Khởi tạo và khởi tạo lại thông tin mùi**_

Thuật toán MMAS đã thêm vào giá trị cận trên và giá trị cận dưới cho thông tin pheromone gọi là _τ_ min và _τ_ max

Sau mỗi lần cập nhật giá trị thông tin mùi _τ_ ij nếu _τ_ ij < _τ_ min thì sẽ gán _τ_ ij = _τ_ min và nếu _τ_ ij > _τ_ max thì gán _τ_ ij = _τ_ max

Giá trị cận trên _τ_ max thường được thiết lập với công thức sau:

_τ max_ = $1ρCbestfrac{1}{rho C_{best}}$

Giá trị cận dưới _τ_ min được xác định bằng công thức:

_τ_ min = _τ_ max /2n.

## Thuật toán Rank-Based Ant System (RBAS)

Đây cũng là một thuật toán được mở rộng phát triển từ hệ thống AS đưa ra bởi Bullnheimer, Hartl và Strauss vào năm 1997. Thuật toán này đưa vào ý tưởng xếp hạng cho các lời giải khi thực hiện cập nhật pheromone. Cụ thể như sau:

  * Đầu tiên, m con kiến được xếp hạng theo thứ tự giảm dần dựa theo chất lượng lời giải mà nó thu được. Ví dụ: (S1, S2, … Sm-1, Sm) trong đó S1 là phương án tốt nhất.

  * Pheromone chỉ được đặt thêm trên các cung của б -1 con kiến có lời giải tốt nhất. Lượng pheromone cũng phụ thuộc trực tiếp vào thứ hạng sắp xếp của con kiến.

  * Các đoạn đường đi của lời giải tốt nhất được nhận thêm một lượng pheromone phụ thuộc vào chất lượng lời giải.


Các công thức như sau:

![](images/image18.wmf)

Trong đó ![](images/image19.wmf)

Và

![](images/image20.wmf)

Tóm tắt thủ tục cập nhật pheromone của thuật toán này:

1 **Procedure** daemon_actions

2 **for each** ![](images/image21.wmf) **do** local_search (![](images/image21.wmf)) {optional}

3 rank ![](images/image22.wmf) in decreasing order of solution

quality into ![](images/image23.wmf)

4 **if** (best (![](images/image24.wmf),![](images/image25.wmf)))

5 ![](images/image25.wmf) = ![](images/image24.wmf)

6 **end if**

7 **for** ![](images/image26.wmf) to ![](images/image27.wmf) **do**

8 **for** each edge ![](images/image28.wmf)![](images/image29.wmf) ![](images/image30.wmf) **do**

9 ![](images/image31.wmf)

10 **end for**

11 **end for**

12 **for** each edge ![](images/image32.wmf) ![](images/image33.wmf) ![](images/image25.wmf) **do**

13 ![](images/image34.wmf)

14 **end for**

15 **end Procedure**

## Thuật toán Best-Worst Ant System(BWAS)

Thuật toán được đưa ra bởi Cordon vào năm 1999. Thuật toán này bao gồm một thuật toán mở rộng khác của AS là MMAS (về luật di chuyển và việc bay hơi của pheromone). Bên cạnh đó trong thuật toán này còn quan tâm tới của việc tối ưu cục bộ một cách hệ thống để nâng cao chất lượng lời giải của con kiến. Trong thuật toán BWAS có 3 **daemon action** thêm vào gồm có:

  * Đầu tiên, áp dụng luật có tên _best-worst pheromone update_ để tăng cường pheromone trên các đoạn đường đi qua bởi lời giải tốt nhất toàn cục (global best solution). Thêm vào đó luật này sẽ phạt những cạnh của lời giải tồi nhất trong lần lặp Scurrent-worst.

  * Áp dụng _Pheromone trail mutation_ để đi theo các hướng khác nhau trong quá trình tìm kiếm.

  * BWAS có cơ chế khởi tạo lại thông tin pheromone khi thuật toán bị đình trệ, bằng cách thiết lập pheromone trail cho tất cả các thành phần bằng ![](images/image35.png).


Mô hình thủ tục **Daemon action** của thuật toán BWAS như sau:

1 **Procedure** daemon_actions

2 **for each** ![](images/image21.wmf) **do** local_search (![](images/image21.wmf))

3 ![](images/image36.wmf)best_solution (![](images/image21.wmf))

4 **if** (best (![](images/image37.wmf),![](images/image25.wmf)))

5 ![](images/image25.wmf) =![](images/image37.wmf)

6 **end if**

7 **for** each edge ![](images/image38.wmf)![](images/image29.wmf) ![](images/image25.wmf) **do**

8 ![](images/image39.wmf)

9 ![](images/image40.wmf)

10 **end for**

11 ![](images/image41.wmf)

12 ![](images/image42.wmf)

13 **for** each edge ![](images/image43.wmf) ![](images/image44.wmf)and ![](images/image45.wmf) ![](images/image46.wmf) **do**

14 ![](images/image47.wmf)

15 **end for**

16 ![](images/image48.wmf)

17 **for** each nút / component ![](images/image49.wmf) **do**

18 z = generate_random_value_in_[0,1]

19 **if** (![](images/image50.wmf))

20 s = generate_random_value_in_[1,…, 1]

21 a = generate_random_value_in_[0,1]

22 if ![](images/image51.wmf)

23 else ![](images/image52.wmf)

24 **end if**

25 **end for**

26 **if** (stagnation_condition)

27 **for** each ![](images/image53.wmf) **do** ![](images/image54.wmf)

28 **end if**

29 **end Procedure**

Mục này chỉ đưa ra 5 mô hình thuật toán ACO phát triển từ hệ thống Ant System. Nhưng đó chỉ là một số các dạng tiêu biểu của thuật toán ACO, còn tồn tại rất nhiều các biến thể khác. Và trong đồ án sẽ áp dụng thuật toán theo mô hình hệ thống MMAS để giải bài toán CPMP. Mô hình thuật toán MMAS là một trong các thuật toán hiệu quả nhất của các thuật toán bầy kiến.

# Thuật toán đàn kiến song song

Từ sơ đồ giải thuật ta nhận thấy các cá thể kiến trong giải thuật là rất độc lập với nhau và vì vậy ý tưởng song song đơn giản và hiệu quả nhất là phân chia kiến ra các bộ xử lý khác nhau , các bộ xử lý mạnh có thể nhận nhiều kiến, các bộ xử lý yếu hơn sẽ nhận ít kiến hơn. Việc phân chia như vậy sẽ làm tăng hiệu suất của giải thuật,tuy nhiên khi tới bước cập nhập ma trận mùi các bộ xử lý cần phải trao đổi dữ liệu với nhau, tùy vào thông tin được trao đổi và mô hình các bộ xử lý mà ta có các kiểu thuật toán song song khác nhau và các tham số khác nhau cho giải thuật.

**All-to-all topology** :Các cụm kiến gửi thông tin tới tất cả các cụm kiến khác

**(Directed or undirected) ring topology** : trong mô hình directed ring colony cụm kiến (z +1 mod _**p )**_ \+ 1 là hàng xóm của cụm _**i**_ cho tất cả các cụm kiến và trong mô hình undirected ring colony cụm kiến _**(i**_ \- 1 mod _**p )**_ \+ 1 là hàng xóm của cụm kiến

_**i**_ cho tất cả các cụm kiến.

**Hypercube topology** : Mô hình này yêu cầu có _**p**_ = _**2^k**_ cụm kiến và mỗi cụm kiến I là hàng xóm với cụm kiến j nếu và chỉ nếu kiểu biểu diễn nhị phân của i và j chỉ khác nhau 1 bit. Vì vậy mỗi cụm kiến chỉ có k hàng xóm.

**Random topology** :Trong mô hình này các hàng xóm của mỗi cụm kiến được đinh nghĩa một cách ngẫu nhiên trong mỗi bước trao đổi thông tin .Có nhiều phương thức xác định hàng xóm ngẫu nhiên trong trường hợp này

Cũng có thể phân biệt các giải thuật với nhau bằng loại thông tin gửi nhận qua mỗi bước lặp.

**Lời giải** : Trong chiến thuật này các lời giải tố đã tìm ra sẽ được gửi đi tới các cụm kiến khác .có nhiều kiểu lời giải có thể được gửi đi

**Kiến** : Lời giải của một con kiến từ lần lặp này được gửi tới cụm kiến khác, thông thường đây là lời giải của con kiến tốt nhất

**Lời giải toàn cục tốt nhất**. Lời giải tốt nhất của các cụm kiến được gửi đi cho tất cả các cụm kiến

**Lời giải của hàng xóm tốt nhất** . Lời giải tốt nhất của các cụm kiến được gửi tới các hàng xóm

**Lời giải cục bộ tốt nhất**. Lời giải cục bộ tốt nhất được gửi đi tới các hàng xóm

**Vector mùi** . Thay vì gửi lời giải thì vector mùi sẽ được gửi sau mỗi buớc lặp.