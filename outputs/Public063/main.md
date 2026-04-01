# Public_063

## **1. Kiểm thử bằng bảng quyết định**

Kỹ thuật kiểm thử lớp tương đương và kiểm thử giá trị biên thích hợp cho các hàm có các biến đầu vào không có quan hệ ràng buộc với nhau. Kỹ thuật kiểm thử dựa trên bảng quyết định sẽ phù hợp cho các hàm có các hành vi khác nhau dựa trên tính chất của bộ giá trị của đầu vào. Nói cách khác, kỹ thuật này phù hợp với các hàm/chương trình có các biến đầu vào phụ thuộc lẫn nhau.

Kiểm thử dựa trên bảng quyết định là phương pháp chính xác nhất trong các kỹ thuật kiểm thử chức năng. Bảng quyết định là phương pháp hiệu quả để mô tả các sự kiện, hành vi sẽ xảy ra khi một số điều kiện thỏa mãn.

## **1.1 Bảng quyết định**

Cấu trúc của một bảng quyết định chia thành bốn phần chính như trong Bảng 5.9, bao gồm:

- Các biểu thức điều kiện *C*1*, C*2*, C*3;
- Giá trị điều kiện T, F, –;
- Các hành động *A*1*, A*2*, A*3*, A*4; và
- Giá trị hành động, có (xảy ra) hay không. Chúng ta ký hiệu X để chỉ hành động là có xảy ra ứng với các điều kiện tương ứng của cột.

Khi lập bảng quyết định, chúng ta thường tìm các điều kiện có thể xảy ra để xét các tổ hợp của chúng mà từ đó chúng ta sẽ xác định được các ca kiểm thử tương ứng cho các điều kiện được thỏa mãn. Các hành động xảy ra chính là kết quả mong đợi của ca kiểm thử đó.

Bảng quyết định với các giá trị điều kiện chỉ là T, F, và – được gọi là *bảng quyết định lôgic*. Chúng ta có thể mở rộng các giá trị này bằng các tập giá trị khác, ví dụ 1, 2, 3, 4, khi đó chúng ta có *bảng quyết định tổng quát*.

Bảng 5.10 là một ví dụ đơn giản về một bảng quyết định để khắc phục sự cố máy in. Khi máy in có sự cố, chúng ta sẽ xem xét tình trạng dựa trên các điều kiện trong bảng là đúng (T) hay sai (F), từ đó xác định được cột duy nhất có các điều kiện thỏa mãn, và thực hiện các hành động khắc phục sự cố tương ứng.

**Bảng 5.9: Ví dụ về một bảng quyết định**

<table><tbody><tr><th></th><th></th><th></th><th></th><th>Quy</th><th></th></tr><tr><td></td><td></td><td>1</td><td>2</td><td>3</td><td>4</td><td>5</td><td>6</td></tr><tr><td>Điều kiện</td><td><math>C_1</math></td><td>T</td><td>T</td><td>T</td><td>F</td><td>F</td><td>F</td></tr><tr><td></td><td><math>C_2</math></td><td>T</td><td>T</td><td>F</td><td>T</td><td>F</td><td>F</td></tr><tr><td></td><td><math>C_3</math></td><td>T</td><td>F</td><td>-</td><td>-</td><td>T</td><td>F</td></tr><tr><td>Hành động</td><td><math>A_1</math></td><td>X</td><td>X</td><td></td><td>X</td><td></td><td></td></tr><tr><td></td><td><math>A_2</math></td><td>X</td><td></td><td></td><td></td><td>X</td><td></td></tr><tr><td></td><td><math>A_3</math></td><td></td><td>X</td><td></td><td>X</td><td>X</td><td></td></tr><tr><td></td><td><math>A_4</math></td><td></td><td></td><td>X</td><td></td><td></td><td>X</td></tr></tbody></table>

Chú ý là ở đây thứ tự các điều kiện và thứ tự thực hiện hành động không quan trọng, nên chúng ta có thể đổi vị trí các hàng. Với các hành động cũng vậy, tuy nhiên tùy trường hợp chúng ta có thể làm mịn hơn bằng việc đánh số thứ tự hành động xảy ra thay cho dấu X để chỉ ra hành động nào cần làm trước. Với bảng quyết định tổng quát, các giá trị của điều kiện không chỉ nhận giá trị đúng (T) hoặc sai (F), khi đó ta cần tăng số cột để bao hết các tổ hợp có thể của các điều kiện.

**Bảng 5.10: Bảng quyết định để khắc phục sự cố máy in**

<table><tbody><tr><th></th><th></th><th>1</th><th>2</th><th>3</th><th>4</th><th>5</th><th>6</th><th>7</th><th>8</th></tr><tr><td>Điều kiện</td><td>Máy in không in</td><td>T</td><td>T</td><td>T</td><td>T</td><td>F</td><td>F</td><td>F</td><td>F</td></tr><tr><td></td><td>Đèn đỏ nhấp nháy</td><td>T</td><td>T</td><td>F</td><td>F</td><td>T</td><td>T</td><td>F</td><td>F</td></tr><tr><td></td><td>Không nhận ra máy in</td><td>T</td><td>F</td><td>T</td><td>F</td><td>T</td><td>F</td><td>T</td><td>F</td></tr><tr><td>Hành động</td><td>Kiểm tra dây nguồn</td><td></td><td></td><td>X</td><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td>Kiểm tra cáp máy in</td><td>X</td><td></td><td>X</td><td></td><td></td><td></td><td></td><td></td></tr><tr><td></td><td>Kiểm tra phần mềm in</td><td>X</td><td></td><td>X</td><td></td><td>X</td><td></td><td>X</td><td></td></tr><tr><td></td><td>Kiểm tra mực in</td><td>X</td><td>X</td><td></td><td></td><td>X</td><td>X</td><td></td><td></td></tr><tr><td></td><td>Kiểm tra kẹt giấy</td><td></td><td>X</td><td></td><td>X</td><td></td><td></td><td></td><td></td></tr></tbody></table>

**Kỹ thuật thực hiện:** Để xác định các ca kiểm thử dựa trên bảng quyết định, ta dịch các điều kiện thành các đầu vào và các hành động thành các đầu ra. Đôi khi các điều kiện sẽ xác định các lớp tương đương của đầu vào và các hành động tương ứng với các mô-đun xử lý chức năng đang kiểm thử. Do đó mỗi cột tương ứng với một ca kiểm thử. Vì tất cả các cột bao phủ toàn bộ các tổ hợp đầu vào nên chúng ta có một bộ kiểm thử đầy đủ.

Trên thực tế không phải tổ hợp đầu vào nào cũng là hợp lệ, do đó khi sử dụng bảng quyết định người ta thường bổ sung thêm một giá trị đặc biệt "–" để đánh dấu các điều kiện không thể cùng xảy ra này. Các giá trị – (không quan tâm) có thể hiểu là luôn sai, không hợp lệ. Nếu các điều kiện chỉ là T và F ta có 2*<sup>n</sup>* cột qui tắc. Mỗi giá trị "–" sẽ đại diện cho hai cột. Để dễ kiểm tra không sót cột nào ta có thể thêm hàng đếm "Số luật" như trong Bảng 5.11 và khi tổng hàng này bằng 2*<sup>n</sup>* ta biết số cột qui tắc đã đủ.

**Bảng 5.11: Bảng quyết định cho hàm Triangle**

<table><tbody><tr><th></th><th colspan="6"></th><th></th></tr><tr><td>Điều kiện</td><td>1</td><td>2</td><td>3</td><td>4</td><td>5</td><td>6</td><td>7</td><td>8</td><td>9</td><td>10</td><td>11</td></tr><tr><td>c1: a<b+c?< td=""><td>F</td><td>T</td><td>T</td><td>T</td><td>T</td><td>T</td><td>T</td><td>T</td><td>T</td><td>T</td><td>T</td></b+c?<></td></tr><tr><td>c2: b<a+c?< td=""><td>-</td><td>F</td><td>T</td><td>T</td><td>T</td><td>T</td><td>T</td><td>T</td><td>T</td><td>T</td><td>T</td></a+c?<></td></tr><tr><td>c3: c<a+b?< td=""><td>-</td><td>-</td><td>F</td><td>T</td><td>T</td><td>T</td><td>T</td><td>T</td><td>T</td><td>T</td><td>T</td></a+b?<></td></tr><tr><td>c4: a = b?</td><td>-</td><td>-</td><td>-</td><td>T</td><td>T</td><td>T</td><td>T</td><td>F</td><td>F</td><td>F</td><td>F</td></tr><tr><td>c5: a = c?</td><td>-</td><td>-</td><td>-</td><td>T</td><td>T</td><td>F</td><td>F</td><td>T</td><td>T</td><td>F</td><td>F</td></tr><tr><td>c6: b = c?</td><td>-</td><td>-</td><td>-</td><td>T</td><td>F</td><td>T</td><td>F</td><td>T</td><td>F</td><td>T</td><td>F</td></tr><tr><td>Số luật</td><td>32</td><td>16</td><td>8</td><td>1</td><td>1</td><td>1</td><td>1</td><td>1</td><td>1</td><td>1</td><td>1</td></tr><tr><td>a1: Không là tam giác</td><td>X</td><td>X</td><td>X</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>a2: Tam giác lệch</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td></td><td>X</td></tr><tr><td>a3: Tam giác cân</td><td></td><td></td><td></td><td></td><td></td><td></td><td>X</td><td></td><td>X</td><td>X</td><td></td></tr><tr><td>a4: Tam giác đều</td><td></td><td></td><td></td><td>X</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr><tr><td>a5: Không hợp lệ</td><td></td><td></td><td></td><td></td><td>X</td><td>X</td><td></td><td>X</td><td></td><td></td><td></td></tr></tbody></table>

## **1.2 Ví dụ minh họa**

**Kiểm thử bằng bảng quyết định cho hàm Triangle:** Sử dụng bảng quyết định được mô tả ở Bảng 5.11, ta có 11 ca kiểm thử nhằm kiểm tra tính đúng đắn của hàm Triangle. Cụ thể, có ba (3) trường hợp không hợp lệ, ba (3) trường hợp không phải là tam giác, một (1) trường hợp tam giác đều, một (1) trường hợp tam giác thường và ba (3) trường hợp tam giác cân. Bảng 5.12 là kết

quả chi tiết về các ca kiểm thử này. Nếu ta thêm điều kiện kiểm tra bất đẳng thức tam giác ta sẽ có thêm ba (3) ca kiểm thử nữa (trường hợp một cạnh có độ dài bằng tổng hai cạnh còn lại).

**Bảng 5.12: Ca kiểm thử bằng bảng quyết định cho hàm Triangle**

<table><tbody><tr><th>TT</th><th>a</th><th>b</th><th>c</th><th>Kết quả mong đợi</th></tr><tr><td>1</td><td>4</td><td>1</td><td>2</td><td>Không phải tam giác</td></tr><tr><td>2</td><td>1</td><td>4</td><td>2</td><td>Không phải tam giác</td></tr><tr><td>3</td><td>1</td><td>2</td><td>4</td><td>Không phải tam giác</td></tr><tr><td>4</td><td>5</td><td>5</td><td>5</td><td>Tam giác đều</td></tr><tr><td>5</td><td>?</td><td>?</td><td>?</td><td>Không khả thi</td></tr><tr><td>6</td><td>?</td><td>?</td><td>?</td><td>Không khả thi</td></tr><tr><td>7</td><td>2</td><td>2</td><td>3</td><td>Tam giác cân</td></tr><tr><td>8</td><td>?</td><td>?</td><td>?</td><td>Không khả thi</td></tr><tr><td>9</td><td>2</td><td>3</td><td>2</td><td>Tam giác cân</td></tr><tr><td>10</td><td>3</td><td>2</td><td>2</td><td>Tam giác cân</td></tr><tr><td>11</td><td>3</td><td>4</td><td>5</td><td>Tam giác thường</td></tr></tbody></table>

**Kiểm thử bằng bảng quyết định cho hàm NextDate:** Có nhiều cách xác định các điều kiện. Ví dụ chúng ta sẽ đặc tả ngày và tháng trong năm và quy đổi về dạng của một năm nhuận hay một năm thông thường giống như trong lần thử đầu tiên, do đó năm 1900 sẽ không có gì đặc biệt. Các miền tương đương bây giờ như sau:

- M1 = { tháng *|* tháng có 30 ngày }
- M2 = { tháng *|* tháng có 31 ngày, trừ tháng 12 }
- M3 = { tháng *|* tháng 12 }
- M4 = { tháng *|* tháng 2 }

Ngày

- D1 = {ngày *|* 1 *≤* ngày *≤* 27 }
- D2 = {ngày *|* ngày = 28 }
- D3 = {ngày *|* ngày = 29 }
  - D4 = {ngày *|* ngày = 30 }
  - D5 = {ngày *|* ngày = 31 }

Năm

- Y1 = {năm *|* năm nhuận }
- Y2 = {năm *|* năm thông thường }

Trong khi tích Đề-các sẽ tạo ra 40 bộ giá trị nếu áp dụng kiểm thử lớp tương đương mạnh, bảng quyết định được lập như Bảng 5.13 chỉ cần 22 bộ giá trị ứng với 22 ca kiểm thử. Có 22 quy tắc, so với 36 trong thử lần hai. Chúng ta có một bảng quyết định với 22 quy tắc. Năm quy tắc đầu tiên cho tháng có 30 ngày. Hai bộ tiếp theo (6-10 và 11-15) cho tháng có 31 ngày, với các tháng khác Tháng Mười Hai và với Tháng Mười Hai.