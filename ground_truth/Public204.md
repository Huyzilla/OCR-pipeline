# Public_204

# Bản mạch in (PCB). 

PCB (viết tắt từ Printed Circuit Board) là một bản mạch có các đường nối dẫn điện liên kết các linh kiện với nhau theo nguyên lý. Mối hàn kim loại tạo mối liên kết điện giữa bề mặt PCB với các linh kiện gắn trên nó.
Trước khi mạch in PCB ra đời, mạch điện được đấu với nhau bằng dây điện nối điểm -điểm rất mất thời gian. Và đó cũng là nguyên nhân dẫn đến nhiều hư hỏng, ngắn mạch, đứt mạch.
Một tấm PCB được cấu thành từ nhiều lớp, mỗi lớp là một loại vật liệu khác nhau được kết dính bằng vật liệu kết dính và ép nhiệt để trở thành 1 bản mạch duy nhất.
|<image_1>|
**Vật liệu nền (Substrate)**  
Vật liệu nền, thường là sợi thủy tinh (FR4), ngoài ra còn có các vật liệu khác như nhựa Bakelit (FR1), eposi kết hợp sợi thủy tinh (CEM) ... Sợi thủy tinh có rất nhiều ưu điểm, nên hầu hết các thiết kế người ta sử dụng FR-4. Ngoài ra, đối với các loại PCB dẻo còn sử dụng loại nhựa chịu nhiệt cao để làm vật liệu nền (Kapton hoặc tương đương).
Có rất nhiều độ dày khác nhau cho PCB, chủ yếu và phổ biến là 1.6mm, ngoài ra còn có 0.16mm, 0.5mm, 0.8mm, 1.0mm, 1.2mm, 2.0mm ...
Các loại nền mạch rẻ tiền như Eposi, Phenol được sử dụng trong các sản phẩm điện tử cần giá thành thấp có độ bền kém hơn FR-4, có những đặc tính không dễ chịu như có mùi khét khi hàn, nếu đặt nhiệt độ quá cao hay hàn quá lâu bản mạch sẽ bị phân hủy, phát sinh khói.
**Đường đồng (Copper)**

|<image_2>|

Lớp tiếp theo là lớp đồng mỏng, được ép dính bằng keo kết dính và nhiệt trên vật liệu nền. Thông thường, đối với mạch 2 lớp, thì đồng được ép trên cả 2 mặt, đối với mạch 1 lớp, thì đồng chỉ được ép trên 1 mặt. Độ dày của lớp đồng khác nhau và được đo bằng trọng lượng, ounce/foot vuông. Đa số PCB có độ dày 1 ounce/foot vuông (độ dày của lớp đồng khoảng 35 micromet).

**Lớp phủ (Soldermask).**

Lớp phía trên lớp đồng là lớp phủ, hay còn gọi là mặt nạ mở phủ, phổ biến có màu xanh lá, ngoài ra có màu đỏ, đen, trắng, xanh dương. Nó được phủ lên lớp đồng để ngăn cách các đường đồng tiếp xúc ngẫu nhiên đối với kim loại, mối hàn, hoặc dây dẫn. Ngoài ra nó còn hữu ích để hàn chính xác, ngăn chặn lem hàn.
|<image_3>|
Trên hình, lớp phủ màu xanh lá được sử dụng phổ biến cho các loại PCB, phủ qua hết các đừờng mạch tuy nhiên vẫn chừa ra những chỗ màu trắng để hàn linh kiện.
**Lớp in linh kiện (Silkscreen)**

|<image_4>|

Lớp in linh kiện màu trắng là lớp trên cùng PCB, trên cả lớp phủ xanh. Ở lớp này có thể thêm những ký tự, số, ký hiệu của các linh kiện để dễ dàng nhận biết và lắp ráp linh kiện lên PCB. Thông thường lớp in linh kiện có màu trắng, tuy nhiên có những màu khác nữa như màu đen, mầu xám, nhưng tùy thuộc vào màu của lớp phủ để sử dụng màu của lớp in linh kiện sao cho nổi bật nhất. Ví dụ phủ đen thì in linh kiện trắng, còn phủ trắng thì in linh kiện đen.

# Tổ chức linh kiện trên bản mạch. 

Việc bố trí linh kiện trên bo mạch cho đúng và hợp lý phụ thuộc vào rất nhiều yếu tố. Tuy nhiên trong thiết kế mạch phải đảm bảo các nguyên tắc sau.

  * Có không gian đủ lớn cho các linh kiện công suất.

  * Hạn chế tối thiểu các đoạn dây nối chồng chéo.


# Dụng cụ, thiết bị cầm tay nghề điện tử. 

## Mỏ hàn. 

### Mỏ hàn nhiệt 

|<image_5>|

Phần chính của mỏ hàn thường là bộ phận gia nhiệt. Trên một ống sứ hình trụ rỗng, mặt ngoài tạo rãnh theo đường xoắn ốc, trên rãnh người ta đặt dây điện trở nhiệt, giữa ruột của ống sứ là mỏ hàn bằng đồng đỏ.
Đầu dây ra của điện trở nhiệt được bao phủ bởi các vòng (khoen) sứ nhỏ chịu nhiệt và cách điện tốt, xuyên qua cần hàn rồi đấu vào dây dẫn điện để dẫn điện vào mỏ hàn.
|<image_6>|
_Cấu tạo bên trong mỏ hàn thường_
Khi mỏ hàn được cấp nguồn sẽ xuất hiện dòng điện chạy qua cuộn dây điện trở nhiệt (1) cuốn trên ống sứ (3), làm cho cuộn dây (4) nóng dần lên sinh ra nhiệt. Nhiệt lượng này truyền qua ống sứ cách điện sang đầu mỏ hàn (5) (đầu mỏ hàn nằm trong ống sứ và cuộn dây). Đầu mỏ hàn được làm bằng lim loại nên hấp thụ nhiệt. Nhiệt lượng do đầu mỏ hàn toả ra nóng hơn nhiệt độ nóng chảy của thiếc nên khi ta đưa đầu mỏ hàn vào thiếc sẽ làm cho thiếc bị nóng chảy. Vậy mỏ hàn đã sinh nhiệt.

### Mỏ hàn xung 

Mỏ hàn xung thường được sử dụng ở mạng điện lưới 110V hay 220V, mỏ hàn xung được chế tạo gồm nhiều loại công suất khác nhau : 45W, 60W, 75W và 100W, 200W, tuỳ theo đối tượng hàn mà ta chọn loại mỏ hàn xung nào cho phù hợp.

|<image_7>|
_Hình dạng bên ngoài mỏ hàn xung_
Bộ phận tạo nhiệt cho mỏ hàn xung chính là phần dây dẫn làm mỏ hàn, dòng điện làm nóng mỏ hàn được lấy từ cuộn thứ cấp (cuộn thứ cấp có hai cuộn: cuộn chính cấp dòng cho mỏ hàn ; cuộn phụ cấp dòng cho đèn báo của biến áp hàn). Biến áp hàn có cuộn sơ cấp nối tiếp với nút ấn (công tắc nguồn) và dây dẫn điện cùng phích cắm để lấy điện xoay chiều vào.