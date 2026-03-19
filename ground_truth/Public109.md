# Public_109

### Tầm quan trọng của việc khai thác thông tin tuần tự trong dữ liệu người dùng

Hệ gợi ý tuần tự là một trong những hướng nghiên cứu quan trọng trong lĩnh vực hệ gợi ý, tập trung vào việc khai thác thông tin từ chuỗi hành vi của người dùng để dự đoán hành động tiếp theo. Khác với các hệ gợi ý truyền thống chỉ dựa trên thông tin tĩnh, như lịch sử tương tác tổng quát hoặc các thuộc tính người dùng, hệ gợi ý tuần tự tận dụng các thay đổi động trong sở thích và hành vi người dùng theo thời gian.

Nhờ sự phát triển của học sâu, các phương pháp hiện đại như GRU4Rec, SASRec và BERT4Rec đã cải thiện đáng kể khả năng khai thác thông tin tuần tự:

  * **GRU4Rec** : Giúp mã hóa chuỗi sự kiện tuần tự, nhưng còn hạn chế trong việc xử lý chuỗi dài.

  * **SASRec** : Loại bỏ hạn chế của RNN bằng cách sử dụng self-attention để nắm bắt các mối quan hệ giữa các sự kiện mà không bị giới hạn bởi khoảng cách.

  * **BERT4Rec** : Mở rộng SASRec với khả năng khai thác ngữ cảnh hai chiều, tối ưu hóa thông tin từ cả phía trước và phía sau trong chuỗi.


Việc áp dụng các phương pháp này đã mở ra khả năng gợi ý chính xác và hiệu quả hơn, đặc biệt trong các môi trường thực tế như thương mại điện tử, nơi hành vi người dùng thay đổi nhanh chóng và có tính cá nhân hóa cao.

### Cấu trúc GRU

Để xử lý vấn đề gradient biến mất hoặc bùng nổ khi chuỗi trở nên quá dài, các biến thể như GRU (Gated Recurrent Unit) và LSTM (Long Short-Term Memory) đã được giới thiệu. Chúng sử dụng các cổng kiểm soát (gates) để điều chỉnh dòng thông tin trong quá trình lan truyền ngược.

GRU sử dụng hai cổng chính, gồm **cổng cập nhật** (zt​) và **cổng xoá bỏ** (rt​), để kiểm soát dòng thông tin trong quá trình cập nhật trạng thái ẩn. Công thức cập nhật trạng thái trong GRU được định nghĩa như sau:

  * Cổng cập nhật:

$$
zt=σ(Wz•[ht−1,xt]+bz)z_{t} = sigmaleft( W_{z} bullet leftlbrack h_{t - 1},x_{t} rightrbrack + b_{z} right)
$$


Cổng này xác định tỷ lệ thông tin từ trạng thái cũ ht−1​ cần giữ lại để sử dụng trong trạng thái hiện tại.

  * Cổng xóa bỏ:

$$
rt=σ(Wr•[ht−1,xt]+br)r_{t} = sigmaleft( W_{r} bullet leftlbrack h_{t - 1},x_{t} rightrbrack + b_{r} right)
$$


Cổng xoá bỏ kiểm soát mức độ ảnh hưởng của trạng thái trước đó ht−1​ khi tạo trạng thái mới.

  * Trạng thái ứng viên:

$$
h̃t=tanh(Wh•[rt⨀ht−1,xt]+bh){widetilde{h}}_{t} = tanhleft( W_{h} bullet leftlbrack {r_{t} bigodot h}_{t - 1},x_{t} rightrbrack + b_{h} right)
$$


Trạng thái ứng viên $h̃t{widetilde{h}}_{t}$​ là biểu diễn trung gian, chịu tác động bởi cổng xoá bỏ $rtr_{t}$​ và thông tin đầu vào $xtx_{t}$​.

  * Trạng thái ẩn cuối cùng:

$$
ht=zt⨀ht−1+(1−zt)⨀h̃th_{t} = {z_{t} bigodot h}_{t - 1} + left( 1 - z_{t} right) bigodot {widetilde{h}}_{t}
$$


Trạng thái cuối cùng $hth_{t}$​ là sự kết hợp giữa trạng thái trước đó $ht−1h_{t - 1}$​ (được điều chỉnh bởi $ztz_{t}$) và trạng thái ứng viên $h̃t{widetilde{h}}_{t}$.

![Diagram of the gated recurrent unit RNN (GRU RNN) unit. Diagram of the... | Download Scientific Diagram](images/image1.jpeg)

  * Ở đây:

* $xtx_{t}$ là đầu vào tại thời điểm 𝑡 (ví dụ: embedding của sản phẩm).

* $ht−1h_{t - 1}$ là trạng thái ẩn tại thời điểm trước đó.

* $σsigma$ là hàm sigmoid, còn tanh làm hàm kích hoạt phi tuyến.

* $Wz,Wr,WhW_{z},W_{r},W_{h}$là các trọng số cần học.

* $bz,br,bhb_{z},b_{r},b_{h}$ là bias.

  * Dự đoán đầu ra: Dựa trên trạng thái ẩn $hth_{t}$​, GRU dự đoán phần tử tiếp theo trong chuỗi thông qua một lớp softmax:


$$
yt=softmax(Wy•ht+by)y_{t} = softmax(W_{y} bullet h_{t} + b_{y})
$$

Hàm mất mát thường được sử dụng là cross-entropy giữa phân phối dự đoán yt​ và nhãn thực yt∗​.

### GRU4Rec

Cấu trúc mạng sử dụng trong GRU4Rec được tổ chức theo các tầng sau:

  * Tầng đầu vào (Input Layer): Nhận chuỗi nhấp chuột của người dùng.

  * Tầng nhúng (Embedding Layer): Biểu diễn sản phẩm dưới dạng vector nhúng và có thể áp dụng dropout để giảm overfitting.

  * Tầng hồi tiếp (Recurrent Layer - GRU): Mô hình hóa thông tin tuần tự dựa trên GRU.

  * Tầng fully connected: Hợp nhất thông tin từ trạng thái ẩn của GRU.

  * Tầng đầu ra (Output Layer): Có thể sử dụng hàm softmax hoặc linear để dự đoán sản phẩm tiếp theo.


![A diagram of a process AI-generated content may be incorrect.](images/image2.png)

_Kiến trúc tổng quát của mạng sử dụng trong GRU4Rec, bao gồm các tầng xử lý từ đầu vào đến đầu ra_