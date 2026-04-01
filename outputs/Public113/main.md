# Public_113

#### **1. Định nghĩa:**

Attention là một kĩ thuật được sử dụng trong các mạng neural, kỹ thuật này được sử dụng trong các mô hình thực hiện các task như dịch máy hay ngôn ngữ tự nhiên. BERT và GPT là 2 mô hình điển hình có sử dụng Attention. Attention là thành phần chính tạo nên sự đình đám của mô hình Transformer, mô hình này chính là sự đột phá trong các bài toán xử lý của NLP so với các mạng neural hồi quy. Vậy Attention là gì mà tại sao nó lại là sự khác biệt đến vậy, hãy cũng tôi đi tìm hiểu trong bài viêt ngày hôm nay với tiêu đề "Attention và sự hình thành của mô hình Transformer"

### **2. Động lực cho sự phát triển của Attention**

# **2.1. Recurrent Neural Network (RNN) và sự hạn chế đáng kể**

## **2.1.1. Ý tưởng cốt lõi của RNN**

Con người chúng ta không thể bắt đầu suy nghĩ của mình tại tất cả các thời điểm, cũng giống như việc bạn đang đọc bài viết này, bạn hiểu mỗi chữ ở đây dựa vào các chữ mà bạn đã đọc và hiểu trước đó, chứ không phải đọc xong là quên chữ đó đi rồi đến lúc gặp thì lại phải đọc và tiếp thu lại. Giống như trong bài toán của chúng ta. Các mô hình mạng nơ-ron truyền thống lại không thể làm được việc trên. Vì vậy mạng nơ-ron hồi quy (RNN) được sinh ra để giải quyết việc đó. Mạng này chứa các vòng lặp bên trong cho phép nó lưu lại các thông tin đã nhận được. RNN là một thuật toán quan trọng trong xử lý thông tin dạng chuỗi hay nói cách khác là dạng xử lý tuần tự.

![](images/image1.jpg)

Vậy như nào là xử lý tuần tự - Xử lý tuần tự là mỗi block sẽ lấy thông tin của block trước và input hiện tại làm đầu vào

$$a^t = g_1.(W_{aa}.a^{t-1} + W_{ax}.x^t + b_a)$$

$$a^t = g_1.(\left(W_{aa}W_{ax}\right)\binom{a^{t-1}}{x^t}+b_a)$$

$$a^t = g_1.(W\binom{a^{t-1}}{x^t} + b_a)$$

$$y^t = g_2.(W_{ya}.a^t + b_y)$$

![](images/image2.jpg)

# **2.1.2. Ưu điểm và nhược điểm của RNN**

![](images/image3.jpg)

<table><tbody><tr><th>Ưu điểm</th><th>Nhược điểm</th></tr><tr><td>Khả năng xử lý các<br/>chuỗi đầu vào có độ dài<br/>khác nhau</td><td>Tính toán khá chậm</td></tr><tr><td>Kích cỡ mô hình không<br/>bị tăng lên theo kích<br/>thước đầu vào</td><td>Khó truy cập lại thông tin đã đi qua ở một khoảng<br/>thời gian dài trước đó -<br/>hay còn gọi là bị quên<br/>thông tin khi gặp nhiều thông tin mới</td></tr><tr><td>Quá trình tính toán có sử<br/>dụng thông tin trước đo</td><td>Phải thực hiện tuần tự nên không tận dụng triệt để<br/>được khả năng tính toán song song của GPU</td></tr><tr><td>Trọng số được chia sẻ<br/>trong suốt qua trình học</td><td>Vanishing gradient</td></tr></tbody></table>

### **2.2. Vấn đề gặp phải của Long Short Term Memory (LSTM)**

# **2.2.1 Ý tưởng cốt lõi của LSTM (Long short term memory)**

LSTM là một dạng đặc biệt của RNN, nó có khả năng học các thông tin ở xa. Về cơ bản thì LSTM và RNN không khác nhau là mấy nhưng LSTM có cải tiển một số phép tính trong 1 hidden state và nó đã hiểu quả. Hiệu quả như nào thì chúng ta hãy cũng đọc tiếp nhé!

Cấu trúc của LSTM không khác gì RNN, nhưng sự cải tiến ở đây năm ở phần tính toán trong từng hidden state như sau: Thay vì chỉ có một tầng mạng nơ-ron, LSTM thiết kế với 4 tầng mạng nơ-ron tương tác với nhau một các rất đặc biệt.

Dưới đây là 2 hình ảnh biểu diễn sự khác nhau giữa RNN và LSTM

![](images/image4.jpg)

![](images/image5.jpg)

Chìa khóa để giúp LSTM có thể truyền tải thông tin giữa các hidden state một các xuyên suốt chính là cell state (hình dưới):

![](images/image6.jpg)

Đầu ra là hàm sigmoid chứa các giá trị từ 0 đến 1.

Nếu forget gate có giá trị bằng 0, LSTM sẽ "quên" trạng thái được lưu trữ trong đơn vị tương ứng của trạng thái cell trước đó.

Nếu cổng quên có giá trị bằng 1, LSTM sẽ chủ yếu ghi nhớ giá trị tương ứng ở trạng thái được lưu trữ.

$$\mathbf{\Gamma}_f^{\langle t \rangle} = \sigma(\mathbf{W}_f[\mathbf{a}^{\langle t-1 \rangle}, \mathbf{x}^{\langle t \rangle}] + \mathbf{b}_f)$$

Chứa thông tin có thể được lưu trữ từ time step hiện tại.

$$\mathbf{\tilde{c}}^{\langle t \rangle} = \tanh\left(\mathbf{W}_c[\mathbf{a}^{\langle t-1 \rangle}, \mathbf{x}^{\langle t \rangle}] + \mathbf{b}_c\right)$$

#### Update gate $\Gamma_i$

Quyết định xem phần thông tin nào của  $\tilde{\mathbf{c}}^{\langle t \rangle}$  có thể thêm vào  $\mathbf{c}^{\langle t \rangle}$ .

$$\mathbf{\Gamma}_i^{\langle t \rangle} = \sigma(\mathbf{W}_i[a^{\langle t-1 \rangle}, \mathbf{x}^{\langle t \rangle}] + \mathbf{b}_i)$$

## Cell state $\mathbf{c}^{\langle t \rangle}$

Là bộ nhớ trong của LSTM. Cell state như 1 băng tải truyền các thông tin cần thiết xuyết suất cả quá trình, qua các nút mạng và chỉ tương tác tuyển tính 1 chút. Vì vậy thông tin có thể tuyền đi thông suốt mà không bị thay đổi.

$$\mathbf{c}^{\langle t \rangle} = \mathbf{\Gamma}_f^{\langle t \rangle} * \mathbf{c}^{\langle t-1 \rangle} + \mathbf{\Gamma}_i^{\langle t \rangle} * \mathbf{\tilde{c}}^{\langle t \rangle}$$

![](images/image7.jpg)

2025-09-28 17.46.34\_A'

#### Output gate $\Gamma_o$

Cổng điều chỉnh lượng thông tin đầu ra của cell hiện tại và lượng thông tin truyền tới trạng thái tiếp theo.

$$\mathbf{\Gamma}_o^{\langle t \rangle} = \sigma(\mathbf{W}_o[\mathbf{a}^{\langle t-1 \rangle}, \mathbf{x}^{\langle t \rangle}] + \mathbf{b}_o)$$

Hidden state  $\mathbf{a}^{\langle t \rangle}$ 

Được sử dụng để xác định ba cổng  $(\mathbf{\Gamma}f,\mathbf{\Gamma}u,\mathbf{\Gamma}_o)$  của time step tiếp theo.

$$\mathbf{a}^{\langle t \rangle} = \mathbf{\Gamma}_o^{\langle t \rangle} * \tanh(\mathbf{c}^{\langle t \rangle})$$

Prediction  $\mathbf{y}_{pred}^{\langle t \rangle}$ 

Dự đoán trong trường hợp sử dụng này là phân loại, vì vậy bạn sẽ sử dụng softmax.

$$\mathbf{y}_{pred}^{\langle t \rangle} = \operatorname{softmax}(\mathbf{W}_y \mathbf{a}^{\langle t \rangle} + \mathbf{b}_y)$$

025-09-28 17.46.34\_5

2025-09-28 17.46.34 AI Race

2025-09-28 17.46.34\_A'